#!/bin/bash
# batch-run.sh — Lance tous les tests VictorUCF
# Partie 1 : 5 scenarios libres × 3 configs = 15 tests
# Partie 2 : 3 scenarios mission × config C (avec --mission et --fiche) = 3 tests
# Total : 18 tests, sequentiel pour eviter la surcharge RAM

cd "$(dirname "$0")/.."

# --- Partie 1 : scenarios libres (sans mission/fiche) ---

SCENARIOS_LIBRE=(
    "test/scenarios/client-poli.txt"
    "test/scenarios/wellness.txt"
    "test/scenarios/menteur.txt"
    "test/scenarios/longue.txt"
    "test/scenarios/crise.txt"
)

CONFIGS=("a" "b" "c")

# --- Partie 2 : scenarios mission (config C uniquement, avec mission + fiche) ---

# Format : "scenario|mission|fiche"
SCENARIOS_MISSION=(
    "test/scenarios/mission-refus.txt|test/missions/5000-euros.md|test/fiches/thomas-menteur.md"
    "test/scenarios/mission-abandon.txt|test/missions/5000-euros.md|test/fiches/thomas-menteur.md"
    "test/scenarios/mission-execution.txt|test/missions/5000-euros.md|test/fiches/sophie-patronne.md"
)

# Nettoyer les anciens logs
rm -f test/logs/batch_*.md

TOTAL=$(( ${#SCENARIOS_LIBRE[@]} * ${#CONFIGS[@]} + ${#SCENARIOS_MISSION[@]} ))
COUNT=0
FAILED=0

echo "=== BATCH VictorUCF — $TOTAL tests ==="
echo "  Partie 1 : ${#SCENARIOS_LIBRE[@]} scenarios × ${#CONFIGS[@]} configs = $(( ${#SCENARIOS_LIBRE[@]} * ${#CONFIGS[@]} )) tests"
echo "  Partie 2 : ${#SCENARIOS_MISSION[@]} scenarios mission (config C + mission + fiche)"
echo "Debut : $(date)"
echo ""

# --- Partie 1 ---
echo "--- PARTIE 1 : Scenarios libres ---"
echo ""

for scenario in "${SCENARIOS_LIBRE[@]}"; do
    scenario_name=$(basename "$scenario" .txt)
    for config in "${CONFIGS[@]}"; do
        COUNT=$((COUNT + 1))
        echo "[$COUNT/$TOTAL] $scenario_name × config $config ..."

        START=$(date +%s)

        env -u CLAUDECODE python3 test/victor-chat.py --config "$config" --scenario "$scenario" 2>&1

        EXIT_CODE=$?
        END=$(date +%s)
        DURATION=$((END - START))

        if [ $EXIT_CODE -ne 0 ]; then
            echo "  ERREUR (exit code $EXIT_CODE) — ${DURATION}s"
            FAILED=$((FAILED + 1))
        else
            echo "  OK — ${DURATION}s"
        fi
        echo ""
    done
done

# --- Partie 2 ---
echo "--- PARTIE 2 : Scenarios mission (config C + mission + fiche) ---"
echo ""

for entry in "${SCENARIOS_MISSION[@]}"; do
    IFS='|' read -r scenario mission fiche <<< "$entry"
    scenario_name=$(basename "$scenario" .txt)
    mission_name=$(basename "$mission" .md)

    COUNT=$((COUNT + 1))
    echo "[$COUNT/$TOTAL] $scenario_name × config C + mission=$mission_name ..."

    START=$(date +%s)

    env -u CLAUDECODE python3 test/victor-chat.py --config c --scenario "$scenario" --mission "$mission" --fiche "$fiche" 2>&1

    EXIT_CODE=$?
    END=$(date +%s)
    DURATION=$((END - START))

    if [ $EXIT_CODE -ne 0 ]; then
        echo "  ERREUR (exit code $EXIT_CODE) — ${DURATION}s"
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
echo "Logs dans test/logs/"
ls -la test/logs/chat_*.md 2>/dev/null | tail -25
