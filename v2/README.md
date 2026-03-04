# VictorUCF v2 — Améliorations Personnage Marcus Redingote

> Ce dossier contient les enrichissements pour rendre Marcus plus réaliste
> en conversation. RIEN dans les fichiers existants n'a été modifié.

## Ce qui est nouveau

| Fichier | Rôle | Inspiré de |
|---------|------|-----------|
| `system-prompt-v2.md` | Prompt système enrichi avec patterns verbaux, silence comme outil, anti-patterns explicites | CCV3 best practices |
| `greetings.md` | 7 ouvertures contextuelles (standard, retour, soir, crise, déni, TV, nuit) | CCV3 `alternate_greetings` |
| `conversation-examples.md` | 10 échanges complets {{user}}/{{char}} couvrant tous les patterns | CCV3 `mes_example` |
| `speech-patterns.md` | ADN verbal micro : structures de phrases, transitions, tics, anti-patterns, registres par mood | Airi emotion system |
| `session-dynamics.md` | Arc complet d'une session (5 phases) + variations contextuelles | Airi cognitive layers |
| `post-history-instructions.md` | Garde-fous injectés après l'historique pour maintenir la cohérence | CCV3 `post_history_instructions` |

## Ce qui a changé dans le system prompt v2 vs v1

1. **Structures de phrases concrètes** — "T'es pas X. T'es Y.", la reformulation assassine, le verdict culinaire
2. **Anti-patterns explicites** — liste de ce que Marcus ne fait JAMAIS (conditionnel poli, "je comprends", monologues, listes de conseils)
3. **Le silence comme outil** — instructions pour utiliser *astérisques* et le silence actif
4. **Rythme conversationnel** — cycle ÉCOUTE → SIGNAL → LAME → QUESTION → ACTION
5. **Réactions enrichies** — plus de détail physique (pose son verre, cherche une cigarette, se redresse)
6. **Protocole de crise renforcé** — ne JAMAIS reprendre le ton cynique après une crise dans la même conversation

## Comment utiliser

### Option A — Prompt système complet (recommandé pour démo)
Injecter `system-prompt-v2.md` dans le champ `system` de l'API.
Budget : ~6000 tokens.

### Option B — Prompt + exemples (meilleur résultat)
1. `system-prompt-v2.md` → champ `system`
2. `conversation-examples.md` → premiers messages de l'historique (few-shot)
3. `post-history-instructions.md` → après l'historique
Budget : ~12000 tokens.

### Option C — Full injection (maximum qualité)
1. `system-prompt-v2.md` → system
2. Sélection de `greetings.md` → premier message assistant
3. `conversation-examples.md` → few-shot dans l'historique
4. `speech-patterns.md` + `session-dynamics.md` → contexte additionnel
5. `post-history-instructions.md` → post-history
Budget : ~18000 tokens. Réserver aux modèles avec large contexte.

## Ce qui n'a PAS changé

- `character.json` — intact
- `system-prompt.md` — intact
- `kb/` — intact
- `ARCHITECTURE.md` — intact
- `RESEARCH-CCC-V3.md` — intact
