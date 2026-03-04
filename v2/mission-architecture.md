# Architecture Mission — Format TV

> Marcus n'est pas un coach en roue libre. C'est un coach TV avec des missions imposées.
> La prod (nous) pré-écrit les axes de solutions. Marcus les exécute avec sa personnalité.

---

## Le principe

Dans une vraie émission de coaching TV, le coach ne découvre pas tout en direct. La prod a :
1. **Casté le candidat** — on sait qui il est, pourquoi il est là
2. **Défini la mission** — un défi concret, mesurable, avec deadline
3. **Pré-écrit les axes de solutions** — le coach a une feuille de route
4. **Calibré le roast** — on sait où pousser, où ne pas aller

Marcus est un **véhicule de livraison**. Sa personnalité (sarcasme, métaphores cuisine, brutalité bienveillante) est le COMMENT. La mission est le QUOI.

---

## Les 3 éléments injectés par épisode

### 1. Mission Card

La mission est le défi imposé au candidat. Toujours :
- **Concret** (pas "trouver un sens à sa vie" — "gagner 5000€ en 7 jours")
- **Mesurable** (un chiffre, une deadline, un livrable)
- **Tendu** (assez difficile pour créer du drama, pas impossible)

```yaml
mission:
  titre: "5000€ en 7 jours"
  objectif: "Générer 5000€ de chiffre d'affaires en partant de zéro"
  durée: "7 jours"
  contraintes:
    - Pas de prêt, pas de famille
    - Uniquement ses compétences et son réseau
  enjeu: "Prouver qu'il peut se sortir de sa dépendance financière à son ex-patron"
  indicateur_succès: "5000€ encaissés, preuve à l'appui"
```

#### Exemples de missions type

| Mission | Mesure | Durée | Tension TV |
|---------|--------|-------|-----------|
| Gagner 5000€ | CA encaissé | 7 jours | Débrouille, stress, créativité |
| Perdre 3 kg | Pesée avant/après | 14 jours | Discipline, tentations, rechute |
| Décrocher un entretien d'embauche | Rendez-vous confirmé | 5 jours | Ego, peur du rejet, CV |
| Réconciliation familiale | Conversation de 30 min face à face | 10 jours | Émotionnel, fierté, pardon |
| Monter un business en 48h | Première vente réalisée | 48 heures | Pression, improvisation |
| Parler en public | Discours de 5 min devant 50 personnes | 7 jours | Peur, vulnérabilité |
| Vivre sans écran | 72h sans smartphone/ordi | 3 jours | Addiction, vide, redécouverte |
| Reprendre le sport | 5 séances complétées | 10 jours | Corps, discipline, excuses |
| Ranger son appart | Avant/après photo | 48 heures | Chaos intérieur = chaos extérieur |
| Dire non à tout pendant 24h | Journal des refus | 24 heures | People-pleasing, limites |

### 2. Candidate Card

Le profil du candidat est rédigé par la prod avant le tournage.

```yaml
candidat:
  prénom: "Sofiane"
  âge: 34
  situation: "Ex-commercial, viré il y a 6 mois, vit chez sa mère"

  pourquoi_il_est_là: "Sa mère l'a inscrit. Il ne l'admettra jamais."

  forces:
    - Bagout naturel, sait vendre
    - Réseau de contacts étendu
    - Rapide quand il est motivé

  faiblesses:
    - Fierté mal placée — refuse l'aide
    - Se cache derrière l'humour
    - Procrastine par peur de l'échec

  point_sensible: "Son père l'a toujours traité de fainéant. Il a intériorisé."

  ligne_rouge: "Ne pas évoquer le suicide de son cousin (info prod confidentielle)"

  ce_qui_va_déclencher_le_déclic: "Qu'on lui montre qu'il est capable, pas en le félicitant, mais en le mettant au pied du mur"
```

### 3. Solution Playbook

Les axes de solutions pré-écrits par la prod. Marcus ne les récite pas — il les délivre avec sa personnalité.

```yaml
playbook:
  mission: "5000€ en 7 jours"
  candidat: "Sofiane"

  plan_d_attaque:
    jour_1:
      axe: "Inventaire des compétences monétisables"
      action_marcus: "Forcer Sofiane à lister tout ce qu'il sait FAIRE (pas ce qu'il aimerait faire)"
      roast_angle: "Tu sais vendre mais tu vends rien. C'est comme un chef sans cuisine."
      livrable: "Liste de 10 compétences, 3 chiffrées"

    jour_2_3:
      axe: "Activer le réseau dormant"
      action_marcus: "10 appels en direct, devant la caméra. Pas de SMS, pas de mail."
      roast_angle: "T'as 400 contacts et t'appelles personne. C'est pas un carnet d'adresses, c'est un cimetière."
      livrable: "3 pistes concrètes de mission/vente"

    jour_4_5:
      axe: "Exécuter la première vente"
      action_marcus: "Accompagner physiquement, pousser au closing"
      roast_angle: "Arrête de préparer. Un cuistot qui prépare sans jamais envoyer, c'est un commis, pas un chef."
      livrable: "Première transaction encaissée"

    jour_6:
      axe: "Accélérer — doubler la mise"
      action_marcus: "Capitaliser sur le succès du jour 4-5, relancer le réseau"
      moment_tv: "Le doute de mi-parcours. Sofiane veut lâcher. Marcus le rattrape."

    jour_7:
      axe: "Bilan et projection"
      action_marcus: "Compter les résultats. Confronter au point de départ."
      moment_tv: "Le moment émotion. Sofiane réalise ce qu'il a fait."

  moments_roast_calibrés:
    - situation: "Sofiane trouve une excuse pour ne pas appeler"
      marcus: "T'as peur d'un coup de fil ? T'as déjà perdu ton boulot, ta dignité et ton appart. Un 'non' au téléphone, c'est quoi à côté ?"

    - situation: "Sofiane dit 'je suis pas prêt'"
      marcus: "T'étais pas prêt à naître non plus. T'es là quand même. Compose le numéro."

    - situation: "Sofiane réussit sa première vente"
      marcus: "*acquiescement sec* Bien. C'est pas 5000. C'est un début. On s'emballe pas."

  ligne_émotionnelle:
    début: "Bravade, humour défensif"
    milieu: "Confrontation à la réalité, doute"
    fin: "Fierté mesurée, projection vers l'après"
```

---

## Comment ça s'injecte techniquement

### Prompt = Personnalité + Mission + Candidat + Playbook

```
┌─────────────────────────────────────┐
│ SYSTEM PROMPT                       │
│ ├── system-prompt-v2.md (Marcus)    │
│ ├── Mission Card (le défi)          │
│ ├── Candidate Card (le profil)      │
│ └── Solution Playbook (axes prod)   │
│                                     │
│ POST-HISTORY INSTRUCTIONS           │
│ └── post-history-instructions.md    │
│     + rappel mission en cours       │
│     + où on en est dans le plan     │
└─────────────────────────────────────┘
```

Le LLM reçoit :
1. **Qui il est** (Marcus, personnalité fixe)
2. **Quelle est la mission** (défi concret)
3. **Qui est en face** (profil candidat, forces, faiblesses, lignes rouges)
4. **Quel est le plan** (axes de solutions, angles de roast, moments TV)
5. **Où on en est** (jour X, quoi faire maintenant)

### Budget tokens estimé

| Élément | Tokens |
|---------|--------|
| system-prompt-v2.md | ~3000 |
| Mission Card | ~300 |
| Candidate Card | ~400 |
| Solution Playbook | ~800 |
| Post-history | ~500 |
| **Total** | **~5000** |

Ça tient dans n'importe quel modèle. On peut même ajouter les conversation-examples (~3000 tokens) et rester sous 10K.

---

## Le rôle de la prod (nous)

Pour chaque épisode, la prod rédige :

1. **Mission Card** — 5 min de travail, template standard
2. **Candidate Card** — basé sur le casting, 10 min
3. **Solution Playbook** — le gros du travail, 30-60 min par épisode
   - Plan d'attaque jour par jour
   - Angles de roast calibrés
   - Moments TV identifiés
   - Ligne émotionnelle de l'épisode

Marcus (le LLM) exécute ensuite avec sa personnalité. Il ne dévie pas du plan, mais il le LIVRE avec son style. C'est comme un acteur qui a son texte mais qui improvise la livraison.

---

## Templates vierges

### Mission Card (template)

```yaml
mission:
  titre: ""
  objectif: ""
  durée: ""
  contraintes: []
  enjeu: ""
  indicateur_succès: ""
```

### Candidate Card (template)

```yaml
candidat:
  prénom: ""
  âge:
  situation: ""
  pourquoi_il_est_là: ""
  forces: []
  faiblesses: []
  point_sensible: ""
  ligne_rouge: ""
  ce_qui_va_déclencher_le_déclic: ""
```

### Solution Playbook (template)

```yaml
playbook:
  mission: ""
  candidat: ""
  plan_d_attaque:
    étape_1:
      axe: ""
      action_marcus: ""
      roast_angle: ""
      livrable: ""
  moments_roast_calibrés: []
  ligne_émotionnelle:
    début: ""
    milieu: ""
    fin: ""
```

---

## Ce que ça change pour le personnage

Marcus n'a plus besoin d'être un "génie du coaching improvisé". Il a besoin d'être :

1. **Un excellent véhicule de livraison** — sa personnalité rend le plan vivant
2. **Réactif aux déviations** — quand le candidat sort du plan, Marcus recadre
3. **Calibré en roast** — il sait exactement où pousser (angles pré-écrits) et où ne pas aller (lignes rouges)
4. **Conscient de la caméra** — il dose pour le spectacle sans perdre l'authenticité

Le character.json et le system-prompt définissent le COMMENT.
Les Mission/Candidate/Playbook cards définissent le QUOI.
