# Recherche : Character Card V3 (CCC) vs VictorUCF

> Source : [moeru-ai/airi](https://github.com/moeru-ai/airi) — 19K+ stars
> Date : 2026-02-28
> Contexte : AIRI utilise le format Character Card V3 pour ses personnages IA. Ce document compare ce standard avec VictorUCF et identifie les opportunites d'evolution.

---

## 1. Qu'est-ce que CCC V3 ?

**Character Card Spec V3** est un standard open-source pour definir des personnages IA. Utilise par SillyTavern, AgnAI, RisuAI, et maintenant AIRI (19K stars).

Spec officielle : https://github.com/kwaroran/character-card-spec-v3

### Structure CCC V3

```
CharacterCardV3
  spec: 'chara_card_v3'
  spec_version: '3.0'
  data:
    ├── DataV1 (obligatoire)
    │   ├── name              — Nom du personnage
    │   ├── description       — Description courte
    │   ├── personality       — Texte libre personnalite
    │   ├── scenario          — Contexte de la conversation
    │   ├── first_mes         — Premier message de salutation
    │   ├── mes_example       — Exemples de conversation (format {{user}}/{{char}})
    │   └── character_book    — Knowledge base (entries avec keywords + position + priorite)
    │
    ├── DataV2 (recommande)
    │   ├── character_version — Versioning semantique
    │   ├── creator           — Auteur
    │   ├── creator_notes     — Notes pour l'utilisateur
    │   ├── system_prompt     — Prompt systeme complet
    │   ├── post_history_instructions — Instructions apres l'historique
    │   ├── alternate_greetings[]     — Salutations variees
    │   ├── group_only_greetings[]    — Salutations pour chats de groupe
    │   └── tags[]            — Categories
    │
    └── DataV3 (optionnel)
        ├── nickname          — Surnom
        ├── creation_date     — Timestamp creation
        ├── modification_date — Timestamp modification
        ├── source[]          — Origines du personnage
        ├── creator_notes_multilingual — Notes multilingues
        ├── assets[]          — Images, avatars, videos
        └── extensions{}      — Extensible a l'infini (key-value libre)
```

### Character Book (Knowledge Base)

```typescript
character_book: {
  entries: [{
    keys: string[],           // Mots-cles declencheurs
    secondary_keys: string[], // Conditions additionnelles
    content: string,          // Contenu a injecter
    selective: boolean,       // Si true, keys ET secondary_keys requis
    position: 'before_char' | 'after_char',
    insertion_order: number,  // Ordre dans le prompt
    priority: number,         // 0-100, plus haut = plus important
    enabled: boolean
  }]
}
```

---

## 2. Comparaison VictorUCF vs CCC V3

### Ce que VictorUCF fait MIEUX

| Feature | VictorUCF | CCC V3 | Verdict |
|---------|----------|--------|---------|
| **Vecteurs OCEAN** | 5 dimensions quantifiees (0.0-1.0) avec labels et details | Rien (texte libre dans `personality`) | **VictorUCF gagne** — fondation psychologique mesurable |
| **Systeme de moods** | 13 etats + triggers dynamiques | Rien | **VictorUCF gagne** — comportement adaptatif |
| **Config vocale TTS** | tone, rhythm, signature_laugh, forbidden_words | Rien | **VictorUCF gagne** — pret pour la synthese vocale |
| **Parametres LLM** | temperature, top_p, penalties, max_tokens | Rien | **VictorUCF gagne** — personnage = config complete |
| **KB modulaire** | 7 fichiers markdown, injection selective lisible | JSON entries avec keywords | **VictorUCF gagne** — plus intuitif, editable dans n'importe quel editeur |
| **Brand safety** | 3 niveaux structures, protocole crise, numeros urgence | Rien de structure | **VictorUCF gagne** — pret production |
| **Lisibilite** | Markdown + JSON separes | Tout dans un JSON monolithique | **VictorUCF gagne** — versionnable, maintenable |
| **Budget tokens** | ~3000 tokens (selectif) a ~6000 (full) | Pas d'optimisation | **VictorUCF gagne** |

### Ce que CCC V3 fait MIEUX

| Feature | CCC V3 | VictorUCF | Verdict |
|---------|--------|----------|---------|
| **Standard ecosysteme** | Compatible SillyTavern, AgnAI, RisuAI, AIRI | Format proprietaire | **CCC V3 gagne** — interoperabilite |
| **Versioning** | `character_version` natif | Absent | **CCC V3 gagne** |
| **Assets** | `assets[]` (images, avatar, video) | Rien | **CCC V3 gagne** |
| **Salutations multiples** | `first_mes` + `alternate_greetings[]` | Absent | **CCC V3 gagne** |
| **Multilingue** | `creator_notes_multilingual` | FR uniquement | **CCC V3 gagne** |
| **Exemples conversation** | `mes_example` avec format {{user}}/{{char}} | Absent | **CCC V3 gagne** |
| **Post-history instructions** | `post_history_instructions` separe | Integre dans system-prompt | **CCC V3 gagne** — plus flexible |
| **Extensibilite** | `extensions{}` open-ended | Structure fixe | **CCC V3 gagne** — evolutif sans casser le format |
| **Export PNG** | Card embeddable dans une image PNG (metadata) | Impossible | **CCC V3 gagne** — partage facile |

---

## 3. Ce que VictorUCF devrait emprunter a CCC V3

### Priorite haute

1. **Versioning** — Ajouter `"version": "1.0.0"` dans character.json
2. **Salutations multiples** — Ajouter `"greetings"` dans character.json (Marcus a plusieurs facons d'ouvrir)
3. **Exemples de conversation** — Ajouter des paires {{user}}/{{char}} pour calibrer le ton
4. **Assets** — Associer avatar, photo de reference
5. **Export CCC V3** — Script de conversion VictorUCF → CCC V3 JSON pour compatibilite ecosysteme

### Priorite moyenne

6. **Post-history instructions** — Separer du system-prompt pour flexibilite
7. **Tags/categories** — Pour indexation et decouverte
8. **Multilingue** — Preparer les traductions (EN au minimum)

### Priorite basse

9. **Export PNG** — Card dans une image (gadget mais cool pour le partage)
10. **Nickname** — Surnom (trivial mais utile)

---

## 4. Ce que CCC V3 devrait emprunter a VictorUCF

> Ces elements n'existent nulle part dans CCC V3 ni dans AIRI. VictorUCF est en avance.

1. **Vecteurs OCEAN** — Personnalite quantifiable, pas un texte vague
2. **Mood triggers** — Comportement dynamique sans re-prompt complet
3. **Config TTS native** — Ton, rythme, mots interdits, registre vocal
4. **Parametres LLM embarques** — Le personnage porte sa propre config API
5. **Brand safety structure** — 3 niveaux, protocole crise, override d'urgence
6. **KB injection selective** — Socle permanent + injection conditionnelle

---

## 5. Strategie : VictorUCF + CCC V3 = hybride optimal

### Architecture cible

```
VictorUCF/
├── character.json           ← Source de verite (format VictorUCF)
├── system-prompt.md         ← Prompt systeme
├── kb/                      ← Knowledge base modulaire
│   └── *.md
├── ARCHITECTURE.md          ← Documentation
│
├── exports/                 ← NOUVEAU : exports multi-format
│   ├── marcus-ccc-v3.json   ← Export CCC V3 complet (compatible AIRI, SillyTavern)
│   ├── marcus-ccc-v3.png    ← Export PNG avec metadata embarquee
│   └── convert.ts           ← Script de conversion VictorUCF → CCC V3
│
└── greetings.md             ← NOUVEAU : salutations variees
```

### Mapping VictorUCF → CCC V3

```
character.json:character.name       → data.name
character.json:character.context    → data.scenario
system-prompt.md (complet)          → data.system_prompt
character.json:ocean                → data.extensions.ocean
character.json:mood                 → data.extensions.mood_system
character.json:voice                → data.extensions.tts_config
character.json:transpiler_hints     → data.extensions.llm_params
kb/*.md                             → data.character_book.entries[]
                                      (avec keys, position, priority)
greetings.md                        → data.first_mes + data.alternate_greetings[]
brand-safety                        → data.extensions.brand_safety
```

### Ce qu'on gagne

- **Compatibilite** : Marcus chargeable dans AIRI, SillyTavern, AgnAI en un clic
- **Profondeur** : Les extensions CCC V3 portent OCEAN, moods, TTS, LLM params — notre avantage
- **Double format** : VictorUCF (source de verite editable) + CCC V3 (export distributable)
- **Ecosysteme** : 19K+ utilisateurs AIRI peuvent utiliser Marcus

---

## 6. AIRI — Points d'interet supplementaires

### Architecture cognitive 4 couches (Minecraft bot)

```
Couche A : Perception   — Events bruts → signaux normalises
Couche B : Reflexe      — FSM reactions immediates (survie, faim)
Couche C : Conscient    — LLM planning + reasoning
Couche D : Action       — Execution des taches
```

**Pertinence UCF** : Ce pattern est reutilisable pour un middleware de personnalite IA generique. La couche B (reflexe) correspond aux mood triggers VictorUCF. La couche C utilise le system prompt + KB.

### Multi-provider xsAI

AIRI utilise xsAI, une abstraction au-dessus de 25+ providers LLM :
- OpenAI, Claude, DeepSeek, Gemini, Mistral, Groq, xAI, Ollama, vLLM...
- Meme abstraction pour TTS : ElevenLabs, OpenAI, Microsoft, Kokoro (local)...

**Pertinence UCF** : Le middleware UCF pourrait adopter xsAI comme couche d'abstraction LLM au lieu de gerer chaque provider manuellement.

### Systeme d'emotions AIRI

```
Emotions AIRI : happy, sad, angry, think, surprised, awkward, question, curious, neutral
→ Mappees vers des expressions VRM (3D) et Live2D (2D)
```

**Pertinence VictorUCF** : Les 13 moods de Marcus pourraient etre mappes vers ces 9 emotions pour un rendu visuel. Exemple :
- `cynique-bienveillant` → neutral + think
- `allume-vivant` → happy + curious
- `silence-respectueux` → sad
- `chasseur-patient` → think
- `urgence-humaine` → neutral (sort du personnage)

---

## 7. Conclusion

**VictorUCF n'est pas inferieur a CCC V3 — il est different.**

- CCC V3 = **conteneur generique standardise** (comme un format de fichier)
- VictorUCF = **systeme de personnalite avance** (comme un moteur)

La strategie optimale : **VictorUCF reste la source de verite** pour la profondeur du personnage, et **CCC V3 devient le format d'export** pour la distribution et la compatibilite.

Les innovations de VictorUCF (OCEAN, moods, TTS, LLM params, brand safety) sont exactement ce qui manque a CCC V3. Elles pourraient devenir des **extensions standard** si on propose le format a la communaute.

### Actions concretes

1. Ajouter versioning + greetings + exemples conversation a VictorUCF
2. Creer le script de conversion `convert.ts` (VictorUCF → CCC V3)
3. Tester l'import de Marcus dans AIRI (via le CCC V3 exporte)
4. Proposer les extensions OCEAN/mood/TTS a la spec CCC V3 upstream
