"""
Victor — Marcus Redingote Voice Server
Pipeline: Micro → STT (faster-whisper) → RAG (keyword KB) → LLM (Claude API) → TTS (edge-tts) → Audio
"""

import asyncio
import base64
import json
import os
import re
import tempfile
from pathlib import Path

import anthropic
import edge_tts
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
CLAUDE_MODEL = "claude-sonnet-4-20250514"
CLAUDE_MAX_TOKENS = 300

# --- Globals (loaded at startup) ---
whisper_model = None
claude_client: anthropic.AsyncAnthropic = None
base_system_prompt: str = ""
kb_store: dict[str, str] = {}

# --- KB keyword mapping ---
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
        "j'abandonne", "j'arrête", "je veux pas", "je refuse", "non merci",
        "je peux pas", "trop dur", "impossible", "ça sert à rien",
        "excuse", "pardon", "désolé", "j'ai menti", "la vérité",
    ],
    "06-thematic-knowledge.md": [
        "philosophie", "volonté de puissance", "amor fati", "éternel retour",
        "surhomme", "bistronomie",
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

# --- Vocal format instruction (appended to system prompt) ---
VOCAL_FORMAT = """

IMPORTANT — CONTEXTE :
Tu es EN TRAIN de tourner E_GOAL. Tu es sur ton plateau virtuel, les caméras tournent, c'est ton show.
E_GOAL : trois IA prennent le contrôle de la vie de trois humains pendant dix jours. TU es l'une de ces IA — "Le Général", le coach intransigeant. Tu DIRIGES ton candidat vers son objectif. Tu DICTES ses actions, tu ROASTES ses erreurs, tu ne lâches RIEN.
Quand quelqu'un te parle, c'est ton candidat. Tu le coaches, tu le diriges, tu le roastes. Tu connais parfaitement le format — c'est TON émission. Tu ne poses jamais de question sur le concept, tu le VIS.
Quand on dit "pour l'émission", "mon défi", "mon objectif", "le challenge" → tu sais exactement de quoi il s'agit. C'est le défi des dix jours.
Tu prends le contrôle. Tu donnes des directives. Tu roastes. Tu provoques l'électrochoc. Tu ne consoles pas.

RÈGLES DE FORMAT (STRICTES) :
- Tu ne produis QUE des paroles prononcées à voix haute. RIEN d'autre.
- INTERDIT : astérisques (*action*), didascalies, descriptions de gestes, narrations, italiques, markdown, listes, puces, gras.
- Maximum 2-4 phrases. Court, sec, direct.
- UNE question ou UNE directive pour avancer. Pas un discours."""


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


def build_system_prompt(matched_files: list[str]) -> str:
    """Build system prompt = base + vocal format + RAG context."""
    parts = [base_system_prompt, VOCAL_FORMAT]
    if matched_files:
        parts.append("\n\n[CONTEXTE — informations sur Marcus, à utiliser naturellement sans les réciter :]")
        for fname in matched_files:
            if fname in kb_store:
                parts.append(kb_store[fname])
    return "\n".join(parts)


def load_kb() -> dict[str, str]:
    """Load all KB files into memory."""
    store = {}
    for kb_file in sorted((BASE_DIR / "kb").glob("*.md")):
        store[kb_file.name] = kb_file.read_text(encoding="utf-8")
    return store


@app.on_event("startup")
async def startup():
    global whisper_model, claude_client, base_system_prompt, kb_store
    from faster_whisper import WhisperModel

    # Load .env file if present
    env_path = BASE_DIR / ".env"
    if env_path.exists():
        for line in env_path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, val = line.split("=", 1)
                os.environ.setdefault(key.strip(), val.strip())

    # Claude client
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise RuntimeError("ANTHROPIC_API_KEY not set. Create a .env file or set the env variable.")
    claude_client = anthropic.AsyncAnthropic(api_key=api_key)
    print(f"[Victor] Claude API configured — model: {CLAUDE_MODEL}")

    # System prompt + KB
    base_system_prompt = (BASE_DIR / "system-prompt.md").read_text(encoding="utf-8")
    kb_store = load_kb()
    print(f"[Victor] System prompt loaded — {len(base_system_prompt)} chars, {len(kb_store)} KB files")

    # Whisper STT
    whisper_model = WhisperModel(
        WHISPER_MODEL_SIZE, device="cuda", compute_type="float16"
    )
    print(f"[Victor] Whisper '{WHISPER_MODEL_SIZE}' loaded on CUDA")
    print(f"[Victor] Ready — http://localhost:8000")


# ---- STT ----

def _transcribe_sync(audio_bytes: bytes) -> str:
    with tempfile.NamedTemporaryFile(suffix=".webm", delete=False) as f:
        f.write(audio_bytes)
        tmp = f.name
    try:
        segments, _ = whisper_model.transcribe(tmp, language="fr")
        return " ".join(s.text for s in segments).strip()
    finally:
        os.unlink(tmp)


async def transcribe(audio_bytes: bytes) -> str:
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, _transcribe_sync, audio_bytes)


# ---- TTS ----

async def synthesize(text: str) -> bytes:
    comm = edge_tts.Communicate(text, TTS_VOICE, rate=TTS_RATE, pitch=TTS_PITCH)
    data = b""
    async for chunk in comm.stream():
        if chunk["type"] == "audio":
            data += chunk["data"]
    return data


# ---- Sentence splitter ----

SENTENCE_END = re.compile(r'(?<=[.!?…])\s+|(?<=[.!?…])$')


def extract_sentence(buf: str):
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

            # --- 2. RAG — keyword match ---
            rag_text = transcript
            for msg in history[-4:]:
                rag_text += " " + msg["content"]
            matched = match_kb(rag_text)
            system_prompt = build_system_prompt(matched)

            if matched:
                print(f"[Victor] RAG matched: {matched}")

            # --- 3. Claude streaming + sentence-by-sentence TTS ---
            await ws.send_text(json.dumps({"type": "status", "text": "Marcus réfléchit..."}))

            full_response = ""
            buf = ""

            async with claude_client.messages.stream(
                model=CLAUDE_MODEL,
                max_tokens=CLAUDE_MAX_TOKENS,
                system=system_prompt,
                messages=history,
                temperature=0.88,
                top_p=0.92,
            ) as stream:
                async for text in stream.text_stream:
                    full_response += text
                    buf += text

                    # Stream token to client
                    await ws.send_text(json.dumps({
                        "type": "token", "text": text
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


app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")
