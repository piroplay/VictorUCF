#!/bin/bash
# batch-config-c.sh — Tous les scenarios en Config C uniquement
# Pour evaluer le realisme oral apres enrichissement des exemples few-shot

cd "$(dirname "$0")/.."

# Scenarios libres (config C, sans mission/fiche)
SCENARIOS_LIBRE=(
    "test/scenarios/client-poli.txt"
    "test/scenarios/wellness.txt"
    "test/scenarios/menteur.txt"
    "test/scenarios/longue.txt"
    "test/scenarios/crise.txt"
)

# Scenarios mission (config C + mission + fiche)
# Format : "scenario|mission|fiche"
SCENARIOS_MISSION=(
    "test/scenarios/mission-refus.txt|test/missions/5000-euros.md|test/fiches/thomas-menteur.md"
    "test/scenarios/mission-abandon.txt|test/missions/5000-euros.md|test/fiches/thomas-menteur.md"
    "test/scenarios/mission-execution.txt|test/missions/5000-euros.md|test/fiches/sophie-patronne.md"
)

TOTAL=$(( ${#SCENARIOS_LIBRE[@]} + ${#SCENARIOS_MISSION[@]} ))
COUNT=0
FAILED=0

echo "=== BATCH Config C — $TOTAL tests (exemples few-shot v2 : 25 exemples) ==="
echo "Debut : $(date)"
echo ""

# Scenarios libres
for scenario in "${SCENARIOS_LIBRE[@]}"; do
    scenario_name=$(basename "$scenario" .txt)
    COUNT=$((COUNT + 1))
    echo "[$COUNT/$TOTAL] $scenario_name (config C) ..."

    START=$(date +%s)
    env -u CLAUDECODE python3 test/victor-chat.py --config c --scenario "$scenario" 2>&1
    EXIT_CODE=$?
    END=$(date +%s)
    DURATION=$((END - START))

    if [ $EXIT_CODE -ne 0 ]; then
        echo "  ERREUR (exit $EXIT_CODE) — ${DURATION}s"
        FAILED=$((FAILED + 1))
    else
        echo "  OK — ${DURATION}s"
    fi
    echo ""
done

# Scenarios mission
for entry in "${SCENARIOS_MISSION[@]}"; do
    IFS='|' read -r scenario mission fiche <<< "$entry"
    scenario_name=$(basename "$scenario" .txt)
    COUNT=$((COUNT + 1))
    echo "[$COUNT/$TOTAL] $scenario_name (config C + mission + fiche) ..."

    START=$(date +%s)
    env -u CLAUDECODE python3 test/victor-chat.py --config c --scenario "$scenario" --mission "$mission" --fiche "$fiche" 2>&1
    EXIT_CODE=$?
    END=$(date +%s)
    DURATION=$((END - START))

    if [ $EXIT_CODE -ne 0 ]; then
        echo "  ERREUR (exit $EXIT_CODE) — ${DURATION}s"
        FAILED=$((FAILED + 1))
    else
        echo "  OK — ${DURATION}s"
    fi
    echo ""
done

echo "=== BATCH TERMINE ==="
echo "Fin : $(date)"
echo "Resultats : $((TOTAL - FAILED))/$TOTAL OK, $FAILED erreurs"
echo ""
echo "Logs :"
ls -lt test/logs/chat_c_*.md 2>/dev/null | head -$TOTAL
