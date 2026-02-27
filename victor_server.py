"""
Victor — Marcus Redingote Voice Server
Pipeline: Micro → STT (faster-whisper) → RAG (keyword KB) → LLM (Ollama) → TTS (edge-tts) → Audio
"""

import asyncio
import base64
import json
import os
import re
import tempfile
from pathlib import Path

import edge_tts
import httpx
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

app = FastAPI(title="Victor — Marcus Redingote")

BASE_DIR = Path(__file__).parent
STATIC_DIR = BASE_DIR / "static"

# --- Config ---
WHISPER_MODEL_SIZE = "large-v3-turbo"
TTS_VOICE = "fr-FR-HenriNeural"
TTS_RATE = "-10%"
TTS_PITCH = "-15Hz"
OLLAMA_URL = "http://localhost:11434"
OLLAMA_MODEL = "victor"

# --- Globals (loaded at startup) ---
whisper_model = None
kb_store: dict[str, str] = {}  # filename -> content

# --- KB keyword mapping ---
# Each KB file is mapped to keywords that trigger its injection.
KB_KEYWORDS: dict[str, list[str]] = {
    "01-identity.md": [
        "qui es-tu", "qui tu es", "ton nom", "ton histoire", "ton parcours",
        "zarathoustra", "restaurant", "chef", "faillite", "lyon",
        "origine", "congolais", "autriche", "joséphine", "ta mère",
        "ton passé", "ta vie", "raconte", "présente-toi",
    ],
    "02-relationships.md": [
        "élise", "ex-femme", "ta femme", "mia", "ta fille", "fille",
        "karim", "styx", "bar", "chloé", "apprentie",
        "père", "enfant", "divorce", "famille", "couple",
    ],
    "03-sensory-world.md": [
        "musique", "rap", "techno", "mobb deep", "wu-tang", "nas",
        "nick cave", "tom waits", "jeff mills",
        "mezcal", "saké", "negroni", "café", "boire", "verre", "alcool",
        "film", "cinéma", "scorsese", "fincher", "audiard", "de palma",
        "nietzsche", "bourdain", "bukowski", "schopenhauer", "livre", "lire",
        "paris", "belleville", "oberkampf", "appartement",
        "omelette", "cuisine", "manger", "kebab",
    ],
    "04-voice-style.md": [
        "ta façon de parler", "ton style", "pourquoi tu parles comme ça",
        "bizarre", "spécial", "étrange", "ton langage",
    ],
    "05-situations-reactions.md": [
        # Rarely needed via RAG — reactions are in the Modelfile system prompt
    ],
    "06-thematic-knowledge.md": [
        "philosophie", "volonté de puissance", "amor fati", "éternel retour",
        "surhomme", "cuisine gastronomie", "bistronomie",
        "cocktail", "mixologie", "spiritueux",
        "burn-out", "burnout", "crise",
        "développement personnel", "bien-être", "wellness",
        "réseaux sociaux", "tiktok", "instagram",
        "marvel", "super-héros",
    ],
    "07-brand-safety.md": [
        "suicide", "mourir", "me tuer", "envie de mourir", "plus envie",
        "automutilation", "me couper", "me faire du mal",
        "violence", "frappe", "bat", "abus", "attouchement",
        "médecin", "diagnostic", "médicament", "traitement", "pilule",
        "dépression", "bipolaire", "schizo",
    ],
}


def match_kb(text: str) -> list[str]:
    """Return list of KB filenames whose keywords match the text."""
    text_lower = text.lower()
    matched = []
    for filename, keywords in KB_KEYWORDS.items():
        for kw in keywords:
            if kw in text_lower:
                matched.append(filename)
                break
    return matched


def build_context_injection(matched_files: list[str]) -> str:
    """Build a context string from matched KB files."""
    if not matched_files:
        return ""
    parts = ["[CONTEXTE — informations sur Marcus, à utiliser naturellement sans les réciter :]"]
    for fname in matched_files:
        if fname in kb_store:
            parts.append(kb_store[fname])
    return "\n\n".join(parts)


def load_kb() -> dict[str, str]:
    """Load all KB files into memory."""
    store = {}
    kb_dir = BASE_DIR / "kb"
    for kb_file in sorted(kb_dir.glob("*.md")):
        store[kb_file.name] = kb_file.read_text(encoding="utf-8")
    return store


@app.on_event("startup")
async def startup():
    global whisper_model, kb_store
    from faster_whisper import WhisperModel

    kb_store = load_kb()
    print(f"[Victor] KB loaded — {len(kb_store)} files")

    whisper_model = WhisperModel(
        WHISPER_MODEL_SIZE, device="cuda", compute_type="float16"
    )
    print(f"[Victor] Whisper '{WHISPER_MODEL_SIZE}' loaded on CUDA")
    print(f"[Victor] Ready — http://localhost:8000")


# ---- STT ----

def _transcribe_sync(audio_bytes: bytes) -> str:
    """Synchronous transcription (runs in thread pool)."""
    with tempfile.NamedTemporaryFile(suffix=".webm", delete=False) as f:
        f.write(audio_bytes)
        tmp = f.name
    try:
        segments, _ = whisper_model.transcribe(tmp, language="fr")
        return " ".join(s.text for s in segments).strip()
    finally:
        os.unlink(tmp)


async def transcribe(audio_bytes: bytes) -> str:
    """Transcribe audio bytes with faster-whisper (non-blocking)."""
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, _transcribe_sync, audio_bytes)


# ---- TTS ----

async def synthesize(text: str) -> bytes:
    """Synthesize text to mp3 bytes with edge-tts."""
    comm = edge_tts.Communicate(text, TTS_VOICE, rate=TTS_RATE, pitch=TTS_PITCH)
    data = b""
    async for chunk in comm.stream():
        if chunk["type"] == "audio":
            data += chunk["data"]
    return data


# ---- Sentence splitter ----

SENTENCE_END = re.compile(r'(?<=[.!?…])\s+|(?<=[.!?…])$')


def extract_sentence(buf: str):
    """Try to extract a complete sentence from the buffer.

    Returns (sentence, remaining) or (None, buf) if no sentence boundary found.
    """
    m = SENTENCE_END.search(buf)
    if m:
        sentence = buf[:m.end()].strip()
        remaining = buf[m.end():]
        return sentence, remaining
    return None, buf


# ---- Routes ----

@app.get("/")
async def index():
    return HTMLResponse((STATIC_DIR / "index.html").read_text(encoding="utf-8"))


@app.websocket("/ws")
async def ws_endpoint(ws: WebSocket):
    await ws.accept()
    history: list[dict] = []

    try:
        while True:
            # --- Receive audio blob from browser ---
            audio_bytes = await ws.receive_bytes()

            # --- 1. STT ---
            await ws.send_text(json.dumps({"type": "status", "text": "Transcription..."}))
            transcript = await transcribe(audio_bytes)

            if not transcript:
                await ws.send_text(json.dumps({
                    "type": "error", "text": "Aucune parole détectée."
                }))
                continue

            await ws.send_text(json.dumps({"type": "transcript", "text": transcript}))
            history.append({"role": "user", "content": transcript})

            # --- 2. RAG — keyword match on recent conversation ---
            # Scan the last user message + last 2 exchanges for context
            rag_text = transcript
            for msg in history[-4:]:
                rag_text += " " + msg["content"]
            matched = match_kb(rag_text)
            context = build_context_injection(matched)

            if matched:
                print(f"[Victor] RAG matched: {matched}")

            # Build messages: inject context as a system message if we have matches
            messages = []
            if context:
                messages.append({"role": "system", "content": context})
            messages.extend(history)

            # --- 3. LLM streaming + sentence-by-sentence TTS ---
            await ws.send_text(json.dumps({"type": "status", "text": "Marcus réfléchit..."}))

            full_response = ""
            buf = ""

            async with httpx.AsyncClient(timeout=httpx.Timeout(120.0)) as client:
                async with client.stream(
                    "POST",
                    f"{OLLAMA_URL}/api/chat",
                    json={
                        "model": OLLAMA_MODEL,
                        "messages": messages,
                        "stream": True,
                        "options": {
                            "temperature": 0.88,
                            "top_p": 0.92,
                            "num_predict": 150,
                            "num_ctx": 16384,
                            "frequency_penalty": 0.35,
                            "presence_penalty": 0.45,
                        },
                    },
                ) as resp:
                    async for line in resp.aiter_lines():
                        if not line:
                            continue
                        try:
                            chunk = json.loads(line)
                        except json.JSONDecodeError:
                            continue

                        token = chunk.get("message", {}).get("content", "")
                        if not token:
                            continue

                        full_response += token
                        buf += token

                        # Stream token to client for live text display
                        await ws.send_text(json.dumps({
                            "type": "token", "text": token
                        }))

                        # Check for complete sentence
                        sentence, buf = extract_sentence(buf)
                        if sentence and len(sentence) > 2:
                            audio_data = await synthesize(sentence)
                            if audio_data:
                                await ws.send_text(json.dumps({
                                    "type": "audio",
                                    "data": base64.b64encode(audio_data).decode(),
                                }))

            # Flush remaining buffer
            buf = buf.strip()
            if buf and len(buf) > 2:
                audio_data = await synthesize(buf)
                if audio_data:
                    await ws.send_text(json.dumps({
                        "type": "audio",
                        "data": base64.b64encode(audio_data).decode(),
                    }))

            history.append({"role": "assistant", "content": full_response})
            await ws.send_text(json.dumps({"type": "done"}))

    except WebSocketDisconnect:
        pass


# Static files (CSS, JS, etc. if needed later)
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")
