#!/usr/bin/env python3
"""
victor-chat.py — Simulateur de conversation avec Marcus Redingote
Test A/B/C pour optimiser la coherence du personnage.

Configs:
  A = VictorUCF actuel (system-prompt-v2 + character.json)
  B = A + exemples de conversation (few-shot calibration)
  C = B + post-history instructions (anti-drift CCC v3)

Usage:
  python3 victor-chat.py                          # Mode interactif, config C (default)
  python3 victor-chat.py --config a               # Mode interactif, config A
  python3 victor-chat.py --config c --scenario scenarios/mission-refus.txt --mission missions/5000-euros.md --fiche fiches/sophie-patronne.md
  python3 victor-chat.py --config c --assemble    # Genere le prompt sans lancer le chat
"""

import subprocess
import json
import sys
import re
import argparse
from datetime import datetime
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
V2 = REPO / "v2"
KB = REPO / "kb"
TEST = REPO / "test"


def read_file(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def load_character_json():
    with open(REPO / "character.json", "r", encoding="utf-8") as f:
        return json.load(f)


def build_system_prompt(config: str, mission_path: str = None, fiche_path: str = None) -> str:
    """Assemble le system prompt selon la config, avec mission et fiche optionnelles."""

    # --- Base : system-prompt-v2 ---
    system = read_file(V2 / "system-prompt-v2.md")

    # --- Character.json : OCEAN + moods + voice ---
    char = load_character_json()

    system += "\n\n---\n\n# Donnees structurees du personnage\n"

    system += "\n## Vecteurs OCEAN\n"
    for trait, data in char["ocean"].items():
        system += f"- {trait} ({data['score']}) : {data['label']}\n"

    system += "\n## Moods et triggers\n"
    system += f"- Mood par defaut : {char['mood']['default']}\n"
    for t in char["mood"]["triggers"]:
        system += f"- {t['trigger']} -> {t['mood']}\n"

    system += "\n## Mots et elements interdits\n"
    system += f"- Mots : {', '.join(char['voice']['forbidden_words'])}\n"
    system += f"- Elements : {', '.join(char['voice']['forbidden_elements'])}\n"

    # --- Mission (si fournie) ---
    if mission_path:
        mission_content = read_file(mission_path)
        system += "\n\n---\n\n# MISSION EN COURS\n\n"
        system += "Tu as assigne cette mission au candidat. C'est le cadre de l'echange.\n"
        system += "Toutes tes interventions doivent etre en rapport avec cette mission.\n\n"
        system += mission_content

    # --- Fiche candidat (si fournie) ---
    if fiche_path:
        fiche_content = read_file(fiche_path)
        system += "\n\n---\n\n# FICHE CANDIDAT (confidentielle)\n\n"
        system += "Tu connais ce candidat. Utilise ces infos pour calibrer tes interventions.\n"
        system += "ATTENTION : ne revele JAMAIS la ligne rouge directement.\n"
        system += "Le point sensible, tu peux l'approcher progressivement.\n\n"
        system += fiche_content

    # --- Config B et C : exemples few-shot ---
    if config in ("b", "c"):
        system += "\n\n---\n\n# Exemples de conversation (calibration du ton)\n"
        system += "\nCes exemples montrent EXACTEMENT comment tu dois repondre.\n"
        system += "Imite ce rythme, cette longueur, ce style.\n\n"

        examples = read_file(V2 / "conversation-examples.md")
        system += examples

    return system


def build_post_history(config: str) -> str:
    """Post-history instructions pour config C."""
    if config != "c":
        return ""

    return read_file(V2 / "post-history-instructions.md")


def assemble_user_turn(history: list, user_msg: str, post_history: str) -> str:
    """Construit le message utilisateur avec historique et post-history."""
    prompt = ""

    if history:
        prompt += "[Conversation precedente]\n\n"
        for msg in history:
            if msg["role"] == "user":
                prompt += f"Interlocuteur : {msg['content']}\n\n"
            else:
                prompt += f"Marcus : {msg['content']}\n\n"

    prompt += f"Interlocuteur : {user_msg}\n\n"

    if post_history:
        prompt += f"\n[RAPPEL AVANT DE REPONDRE]\n{post_history}\n\n"

    prompt += "Marcus :"

    return prompt


def call_claude(system_prompt: str, user_prompt: str) -> str:
    """Appelle claude -p avec system prompt et user prompt."""
    try:
        # Unset CLAUDECODE pour eviter le blocage nested session
        env = {k: v for k, v in __import__("os").environ.items() if k != "CLAUDECODE"}
        result = subprocess.run(
            ["claude", "-p", "--system-prompt", system_prompt, user_prompt],
            capture_output=True,
            text=True,
            timeout=120,
            env=env,
        )
        response = result.stdout.strip()
        if not response and result.stderr:
            return f"[ERREUR] {result.stderr.strip()}"
        # Strip thinking tags qui leakent parfois dans la sortie
        response = re.sub(r"<thinking>.*?</thinking>", "", response, flags=re.DOTALL).strip()
        return response
    except subprocess.TimeoutExpired:
        return "[ERREUR] Timeout (120s)"
    except Exception as e:
        return f"[ERREUR] {e}"


def save_assembled(config: str, system_prompt: str, post_history: str,
                    mission_path: str = None, fiche_path: str = None):
    """Sauvegarde le prompt assemble pour inspection."""
    out_dir = TEST / "configs"
    out_dir.mkdir(parents=True, exist_ok=True)

    out_file = out_dir / f"assembled-{config}.md"

    content = f"# Prompt assemble — Config {config.upper()}\n"
    content += f"> Genere le {datetime.now().strftime('%Y-%m-%d %H:%M')}\n"
    content += f"> Taille system prompt : {len(system_prompt)} chars (~{len(system_prompt)//4} tokens)\n"
    content += f"> Post-history : {'oui' if post_history else 'non'}\n"
    if mission_path:
        content += f"> Mission : {mission_path}\n"
    if fiche_path:
        content += f"> Fiche candidat : {fiche_path}\n"
    content += "\n"
    content += "---\n\n"
    content += "## SYSTEM PROMPT\n\n"
    content += system_prompt
    content += "\n\n---\n\n"

    if post_history:
        content += "## POST-HISTORY INSTRUCTIONS\n\n"
        content += post_history
        content += "\n\n---\n\n"

    with open(out_file, "w", encoding="utf-8") as f:
        f.write(content)

    return out_file


def save_log(config: str, history: list):
    """Sauvegarde le log de conversation."""
    if not history:
        return None

    log_dir = TEST / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = log_dir / f"chat_{config}_{ts}.md"

    content = f"# Conversation Marcus — Config {config.upper()}\n"
    content += f"> {datetime.now().strftime('%Y-%m-%d %H:%M')}\n"
    content += f"> Tours : {len(history) // 2}\n\n---\n\n"

    for msg in history:
        if msg["role"] == "user":
            content += f"**Interlocuteur** : {msg['content']}\n\n"
        else:
            content += f"**Marcus** : {msg['content']}\n\n"
            content += "---\n\n"

    with open(log_file, "w", encoding="utf-8") as f:
        f.write(content)

    return log_file


def load_scenario(path: str) -> list:
    """Charge un scenario (un message par ligne, lignes vides ignorees)."""
    with open(path, "r", encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip() and not line.startswith("#")]


def print_header(config: str, system_len: int, post_history: bool,
                  mission_path: str = None, fiche_path: str = None):
    label = {
        "a": "VictorUCF base",
        "b": "+ few-shot examples",
        "c": "+ CCC v3 hybrid (post-history + realisme)",
    }
    print(f"\n--- Marcus Redingote — Config {config.upper()} ({label[config]}) ---")
    print(f"    System prompt : {system_len} chars (~{system_len//4} tokens)")
    print(f"    Post-history  : {'oui' if post_history else 'non'}")
    if mission_path:
        print(f"    Mission       : {Path(mission_path).name}")
    if fiche_path:
        print(f"    Fiche candidat: {Path(fiche_path).name}")
    print(f"    Commandes     : quit, save, /config")
    print()


def main():
    parser = argparse.ArgumentParser(description="Victor UCF — Chat Simulator")
    parser.add_argument(
        "--config",
        choices=["a", "b", "c"],
        default="c",
        help="Config: a=base, b=+examples, c=+post-history+realisme (default: c)",
    )
    parser.add_argument("--scenario", help="Fichier scenario (un message par ligne)")
    parser.add_argument("--mission", help="Fichier mission (.md) a injecter dans le system prompt")
    parser.add_argument("--fiche", help="Fichier fiche candidat (.md) a injecter dans le system prompt")
    parser.add_argument(
        "--assemble",
        action="store_true",
        help="Genere les prompts assembles sans lancer le chat",
    )
    args = parser.parse_args()

    # Build prompts
    system = build_system_prompt(args.config, args.mission, args.fiche)
    post_history = build_post_history(args.config)

    # Save assembled prompts for inspection
    assembled_file = save_assembled(args.config, system, post_history, args.mission, args.fiche)
    print(f"\nPrompt assemble sauvegarde : {assembled_file}")

    if args.assemble:
        # Generate all 3 configs for comparison
        for cfg in ["a", "b", "c"]:
            s = build_system_prompt(cfg)
            ph = build_post_history(cfg)
            f = save_assembled(cfg, s, ph)
            print(f"  Config {cfg.upper()} : {f} ({len(s)} chars)")
        print("\nOuvre ces fichiers pour comparer les 3 configs.")
        return

    print_header(args.config, len(system), bool(post_history), args.mission, args.fiche)

    history = []

    # Scenario mode
    if args.scenario:
        messages = load_scenario(args.scenario)
        print(f"Scenario : {args.scenario} ({len(messages)} messages)\n")

        for i, msg in enumerate(messages):
            print(f"Interlocuteur [{i+1}/{len(messages)}] : {msg}")
            user_prompt = assemble_user_turn(history, msg, post_history)
            response = call_claude(system, user_prompt)
            print(f"Marcus : {response}\n---\n")

            history.append({"role": "user", "content": msg})
            history.append({"role": "assistant", "content": response})

        log_file = save_log(args.config, history)
        print(f"\nLog sauvegarde : {log_file}")
        return

    # Interactive mode
    while True:
        try:
            user_input = input("Toi > ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break

        if not user_input:
            continue
        if user_input.lower() == "quit":
            break
        if user_input.lower() == "save":
            log_file = save_log(args.config, history)
            if log_file:
                print(f"Log sauvegarde : {log_file}")
            continue
        if user_input == "/config":
            print(f"Config actuelle : {args.config.upper()}")
            print(f"System prompt : {len(system)} chars")
            print(f"Post-history : {'oui' if post_history else 'non'}")
            print(f"Historique : {len(history)//2} tours")
            continue

        user_prompt = assemble_user_turn(history, user_input, post_history)
        response = call_claude(system, user_prompt)
        print(f"\nMarcus > {response}\n")

        history.append({"role": "user", "content": user_input})
        history.append({"role": "assistant", "content": response})

    # Auto-save
    if history:
        log_file = save_log(args.config, history)
        print(f"Log sauvegarde : {log_file}")


if __name__ == "__main__":
    main()
