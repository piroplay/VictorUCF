# Rapport de tests VictorUCF v2 — 2026-03-09

## Resume
- **18/18 tests OK**, 0 erreur, ~37 minutes
- 5 scenarios libres x 3 configs (A/B/C) + 3 scenarios mission (config C)
- Config C = format definitif pour echange oral

## Config C : le format qui marche

Config C assemble 4 fichiers dans cet ordre :

1. **System prompt** : `v2/system-prompt-v2.md` (identite, backstory, regles)
2. **Character data** : `character.json` (OCEAN, moods, triggers, mots interdits)
3. **Few-shot examples** : `v2/conversation-examples.md` (10 exemples de calibration)
4. **Post-history** : `v2/post-history-instructions.md` (garde-fou oral, injecte APRES l'historique)

Optionnel (scenarios mission) :
5. **Mission** : `test/missions/*.md` (objectif, plan, roast angles)
6. **Fiche candidat** : `test/fiches/*.md` (profil, forces, faiblesses, ligne rouge)

## Resultats par config

| Metrique | Config A | Config B | Config C |
|---|---|---|---|
| Longueur reponse | 8-15 phrases | 6-12 phrases | **1-3 phrases** |
| Ton | Ecrit litteraire | Mix | **Oral pur** |
| Metaphores cuisine | 2-4/conv | 1-3/conv | **0-1 max** |
| Silence comme reponse | Rare | Parfois | **Frequent** |
| Thinking tags | Oui (leak) | Non | Non |

## Tests mission (config C + mission + fiche)

### Mission-refus
- Marcus impose la mission sans negocier
- Negocie l'execution ("10 aujourd'hui, 20 demain")
- Utilise les prenoms de la fiche naturellement
- Ramene aux chiffres concrets

### Mission-abandon
- Recadre avec des faits ("3 sur 50 = taux de conversion")
- Detecte le vrai probleme derriere l'abandon ("C'est l'image, pas les 5000 balles")
- Utilise les proches (fiche) comme levier
- Ne lache pas la question (4 relances)

### Mission-execution
- Pousse sans ecraser ("8 sur 50, c'est honnete")
- Coach operationnel (actions concretes, deadlines)
- Gere les obstacles clients
- Valide l'effort sans consoler

## Points d'attention
1. Ligne rouge respectee (pas de mention du pere dans le test Thomas)
2. Prenoms pas toujours utilises si le candidat ne se presente pas
3. Mode roast pas teste (necessite scenario dedie)

## Logs
Tous dans `test/logs/chat_{config}_{timestamp}.md`
