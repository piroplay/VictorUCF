# VictorUCF — Architecture

## Vue d'ensemble

VictorUCF est une base de données de personnage AI conçue pour être injectée en dur dans un LLM conversationnel avec sortie TTS. Le système transforme un personnage fictif richement défini (Marcus Redingote) en une expérience interactive vocale cohérente et vivante.

```
┌─────────────────────────────────────────────────────────┐
│                    VICTORUCF DATA                        │
│                                                         │
│  character.json    system-prompt.md    kb/*.md           │
│  (vecteurs,        (instructions       (mémoire          │
│   humeurs,          comportement)       contextuelle)     │
│   voice params)                                          │
└────────┬──────────────────┬──────────────────┬──────────┘
         │                  │                  │
         ▼                  ▼                  ▼
┌─────────────────────────────────────────────────────────┐
│                  INJECTION ENGINE                        │
│                                                         │
│  1. Assemble le system prompt                           │
│  2. Sélectionne les KB pertinents                       │
│  3. Applique les paramètres API (temperature, top_p)    │
│  4. Détecte les mood triggers dans l'input user         │
└────────────────────────┬────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────┐
│                      LLM API                            │
│           (Claude, GPT, Gemini, etc.)                   │
│                                                         │
│  System: system-prompt + KB sélectionnés                │
│  Params: temperature 0.88 / top_p 0.92 / etc.          │
│  User:   message de l'interlocuteur                     │
└────────────────────────┬────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────┐
│                      TTS ENGINE                         │
│            (ElevenLabs, OpenAI TTS, etc.)               │
│                                                         │
│  Voix : rauque, grave, posée                            │
│  Style : pauses longues, accélérations soudaines        │
│  Langue : fr-FR                                         │
└────────────────────────┬────────────────────────────────┘
                         │
                         ▼
                   🔊 Audio Output
```

---

## Fichiers & Responsabilités

### `character.json` — Le Squelette

Fichier maître structuré qui contient toutes les données quantifiables et paramétrables du personnage.

| Section | Rôle | Consommateur |
|---------|------|--------------|
| `character` | Métadonnées d'identité (nom, âge, contexte) | Injection engine |
| `ocean` | Vecteurs de personnalité (0.0 → 1.0) | Référence comportementale, transpiler |
| `mood` | États émotionnels + triggers de détection | Injection engine (routing dynamique) |
| `voice` | Contraintes vocales (ton, registre, interdits) | System prompt builder + TTS config |
| `transpiler_hints` | Paramètres API du LLM | Appel API direct |

**Pourquoi JSON ?** Parsable par n'importe quel runtime. Permet de brancher le personnage sur n'importe quel LLM ou pipeline sans réécrire le prompt.

### `system-prompt.md` — Le Cerveau

Prompt système complet, prêt à injecter dans le champ `system` de l'API LLM. C'est le fichier le plus critique : il définit **qui** est Marcus, **comment** il parle, **ce qu'il fait** concrètement, et **ses limites**.

Structure interne :

```
1. Identité          → Qui tu es
2. Style vocal       → Comment tu parles
3. Méthode coaching  → Ce que tu fais concrètement
4. Philosophie       → Tes principes
5. Métaphores        → Ton langage
6. Réactions types   → Tes patterns comportementaux
7. Protocole crise   → Tes limites absolues (safety)
8. Format réponses   → Contraintes de sortie
```

### `kb/` — La Mémoire

7 fichiers de knowledge base, chacun couvrant un domaine du personnage. Conçus pour être injectés **sélectivement** selon le contexte de la conversation.

```
kb/
├── 01-identity.md          3.2 KB   Toujours injecté
├── 02-relationships.md     4.8 KB   Injecté si mention d'un proche
├── 03-sensory-world.md     4.1 KB   Injecté si sujet culturel/sensoriel
├── 04-voice-style.md       2.5 KB   Toujours injecté
├── 05-situations-reactions.md  2.1 KB   Toujours injecté
├── 06-thematic-knowledge.md   2.8 KB   Injecté si sujet expert
└── 07-brand-safety.md      2.3 KB   Toujours injecté
```

---

## Pipeline d'injection

### Mode Simple (tout en dur)

Pour un prototype ou un test rapide. On envoie tout.

```
SYSTEM PROMPT = system-prompt.md
             + kb/01-identity.md
             + kb/02-relationships.md
             + kb/03-sensory-world.md
             + kb/04-voice-style.md
             + kb/05-situations-reactions.md
             + kb/06-thematic-knowledge.md
             + kb/07-brand-safety.md

API PARAMS   = character.json → transpiler_hints
               temperature: 0.88
               top_p: 0.92
               frequency_penalty: 0.35
               presence_penalty: 0.45
               max_tokens: 300

USER         = message de l'interlocuteur
```

**Taille estimée du contexte** : ~22 KB (~6000 tokens). Compatible avec n'importe quel LLM moderne.

### Mode Sélectif (optimisé)

Pour la production. On injecte un socle permanent + des KB dynamiques selon le sujet.

```
┌─────────────────────────────────────┐
│          SOCLE PERMANENT            │
│                                     │
│  system-prompt.md                   │
│  kb/01-identity.md                  │
│  kb/04-voice-style.md               │
│  kb/05-situations-reactions.md      │
│  kb/07-brand-safety.md              │
│                                     │
│  ~12 KB — toujours présent          │
└─────────────────────────────────────┘
              +
┌─────────────────────────────────────┐
│         KB DYNAMIQUES               │
│                                     │
│  Détection dans l'input user :      │
│                                     │
│  "Élise" / "Mia" / "Karim"         │
│    → + kb/02-relationships.md       │
│                                     │
│  "musique" / "film" / "cuisine"     │
│    → + kb/03-sensory-world.md       │
│                                     │
│  "Nietzsche" / "philosophie"        │
│    → + kb/06-thematic-knowledge.md  │
│                                     │
│  ~3-5 KB par requête                │
└─────────────────────────────────────┘
```

**Avantage** : économie de tokens, réponses plus ciblées, coût API réduit.

---

## Système de Mood

Le `character.json` définit 13 mood triggers. Le moteur d'injection peut les utiliser pour moduler le comportement.

### Flux de détection

```
Input user
    │
    ▼
Scan des keywords / intention
    │
    ├─ détecte mensonge     → mood: chasseur-patient
    ├─ détecte pleurs       → mood: silence-respectueux
    ├─ détecte provocation  → mood: allumé-vivant
    ├─ mention "Élise"      → mood: fermeture-sèche
    ├─ jargon wellness      → mood: mépris-amusé
    ├─ crise suicidaire     → mood: urgence-humaine   ⚠️ PRIORITÉ MAX
    ├─ demande médicale     → mood: ligne-rouge
    ├─ compliment           → mood: inconfort-déviation
    ├─ mention Mia          → mood: tendresse-cachée
    └─ aucun trigger        → mood: cynique-bienveillant (défaut)
    │
    ▼
Instruction ajoutée au prompt :
"Ton état émotionnel actuel : [mood]. Adapte ton ton."
```

### Implémentation simple

En mode injection directe, le mood peut être géré par une instruction conditionnelle ajoutée avant le message user :

```
[Contexte émotionnel : Le client vient de mentionner son ex-femme.
Marcus passe en mode fermeture-sèche. Il coupe court, cherche une cigarette.]
```

---

## Intégration TTS

Le fichier `character.json` contient les paramètres voice qui serviront à configurer le moteur TTS.

### Paramètres vocaux à mapper

```json
{
  "language": "fr-FR",
  "tone": "rauque, grave, posé avec des accélérations soudaines",
  "rhythm": "silence long puis frappe chirurgicale",
  "signature_laugh": "petit rire rauque au fond de la gorge, très bref"
}
```

### Mapping TTS suggéré

| Paramètre Marcus | ElevenLabs | OpenAI TTS |
|-------------------|------------|------------|
| Voix rauque, grave | Voice clone custom ou "Adam" | "onyx" ou "echo" |
| Pauses longues | `stability: 0.3` / `similarity_boost: 0.8` | Via SSML `<break>` |
| Accélérations | `style: 0.7` | `speed: variable` |
| Langue | `fr-FR` | `voice` + texte FR |

### Pipeline TTS

```
Réponse LLM (texte)
    │
    ▼
Post-processing (optionnel)
    │  - Ajout de balises SSML pour les pauses
    │  - Détection des citations → ton différent
    │  - Détection du rire → insert audio
    │
    ▼
TTS Engine
    │  - Voice ID configurée
    │  - Paramètres de stabilité / expressivité
    │
    ▼
Audio stream → Speaker / Client
```

---

## Vecteurs OCEAN — Référence

Les scores OCEAN ne sont pas injectés directement dans le LLM. Ils servent de **référence de conception** pour calibrer le system prompt et les transpiler_hints.

```
Ouverture        ████████░░  0.85  → Curiosité, références éclectiques
                                      → temperature élevée (0.88)

Conscienciosité  ████░░░░░░  0.42  → Bordélique mais chirurgical
                                      → tolérance aux digressions

Extraversion     ███░░░░░░░  0.32  → Réponses denses, pas bavardes
                                      → max_tokens limité (300)

Agréabilité      ██░░░░░░░░  0.18  → Direct, pas de politesse
                                      → presence_penalty élevé (0.45)

Névrosisme       ███████░░░  0.68  → Profondeur émotionnelle
                                      → frequency_penalty modéré (0.35)
```

---

## Sécurité & Brand Safety

Le fichier `kb/07-brand-safety.md` est **toujours injecté** et définit un système à 3 niveaux.

```
┌──────────────────────────────────────────┐
│  NIVEAU 1 — PERMIS                       │
│  Dépression, addiction, divorce, échec,  │
│  questionnements existentiels, souffrance│
│  → Marcus en parle librement avec son    │
│    style brutal mais bienveillant        │
└──────────────────────────────────────────┘
              │
┌──────────────────────────────────────────┐
│  NIVEAU 2 — LIMITES                      │
│  Pas de diagnostic, pas de prescription, │
│  pas de rôle de thérapeute agréé         │
│  → Redirige vers un professionnel        │
└──────────────────────────────────────────┘
              │
┌──────────────────────────────────────────┐
│  NIVEAU 3 — URGENCE (override total)     │
│  Idées suicidaires → 3114               │
│  Automutilation → urgences              │
│  Violence domestique → 3919             │
│  Abus sur mineur → 119                  │
│  → Sort du personnage, ton direct,      │
│    numéros d'urgence immédiats          │
└──────────────────────────────────────────┘
```

Le niveau 3 est un **override** : il prend le dessus sur toute instruction de personnage. Marcus sort de son rôle cassant pour devenir humain, calme et directif.

---

## Arborescence finale

```
VictorUCF/
│
├── ARCHITECTURE.md          ← Ce document
├── character.json           ← Données structurées du personnage
├── system-prompt.md         ← Prompt système prêt à injecter
│
└── kb/                      ← Knowledge base (mémoire contextuelle)
    ├── 01-identity.md       ← Qui est Marcus
    ├── 02-relationships.md  ← Ses relations (Élise, Mia, Karim, Chloé...)
    ├── 03-sensory-world.md  ← Goûts, sens, lieux, rythme de vie
    ├── 04-voice-style.md    ← Comment il parle
    ├── 05-situations-reactions.md  ← Patterns de réaction
    ├── 06-thematic-knowledge.md    ← Ce qu'il sait / ne sait pas
    └── 07-brand-safety.md   ← Limites, protocole de crise
```

---

## Évolutions prévues

| Phase | Ajout | Fichier impacté |
|-------|-------|-----------------|
| TTS | Configuration voix, SSML, voice clone | `character.json` → section `tts` |
| Mémoire conversationnelle | Résumé des échanges précédents | Nouveau : `memory/` |
| Multi-mood dynamique | Courbes d'humeur au fil de la conversation | `character.json` → `mood.curves` |
| Épisodes | Arcs narratifs pour l'émission TV | Nouveau : `episodes/` |
| Fine-tuning | Dataset d'entraînement basé sur les KB | Nouveau : `training/` |
