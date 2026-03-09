# Roadmap Marcus Redingote — Prochaines ameliorations

> Cree le 09/03/2026 apres validation Config C (18/18 tests OK)

## Priorite 1 — Exemples few-shot

**Probleme** : 10 exemples dans conversation-examples.md, c'est pas assez. Marcus tombe dans des patterns repetitifs (*petit rire rauque*, *silence*, *se penche en avant*).

**Action** : Ecrire plus d'exemples, varier les registres physiques et verbaux, puis re-tester pour affiner. Objectif : au moins 25-30 exemples couvrant plus de situations et plus de gestes.

**Statut** : A faire

---

## Priorite 2 — Scenario declic

**Probleme** : On n'a aucun test du moment ou le candidat craque et dit la verite. C'est le moment cle de l'emission. Comment Marcus reagit quand le mur tombe ?

**Action** : Ecrire un scenario dedie (le candidat resiste puis lache le vrai sujet). Tester les 3 configs, valider que Marcus change de ton sans consoler gratuitement.

**Statut** : A faire

---

## A concevoir (pas a implementer maintenant)

### Arc emotionnel — systeme de phase

Marcus doit savoir ou il en est avec le candidat (BRAVADE > CONFRONTATION > EXECUTION > LE MUR > LE DECLIC > L'ACCELERATION > LE BILAN).

Deux approches possibles :
- **Production-driven** : la prod envoie l'indication de phase a Marcus (injection dans le prompt entre les sequences)
- **Auto-detection** : Marcus garde en memoire l'etat de la conversation via un script de memorisation (similaire au systeme workspaces/ETAT.md du serveur Hetzner — un script qui resume l'echange et injecte l'etat au tour suivant)

La deuxieme approche est plus autonome mais plus complexe. A decider au moment de l'integration reelle.

### Proactivite — memoire inter-sessions

Pour que Marcus revienne sur ce qui a ete dit ("T'as rappele le mec du restau ?"), il faut une memoire persistante entre les sequences. Meme logique que le systeme de workspaces : un script qui extrait les faits cles apres chaque session et les reinjecte au debut de la suivante.

### Conversations longues — timer et sequencage

Une sequence ne doit pas depasser ~15 minutes pour eviter d'exploser le contexte tokens. Prevoir un systeme de timer qui decoupe l'echange en sequences. Entre deux sequences : extraction memoire + reinjection. A tester quand on aura la voix.

---

## Parque (pas prioritaire)

- **Roast plateau** : mode specifique du format (2 phrases max, vise comportement pas identite). A ajouter plus tard comme scenario dedie.
- **Voix** : integration Unmute sur Shadow PC. Depend du deblocage WSL/Hyper-V.
