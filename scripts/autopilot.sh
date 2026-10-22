#!/usr/bin/env bash
# Agent autopilot: work -> log -> push -> repeat. Never exits.
# Runs your work command every CYCLE seconds, commits and pushes everything.
#
#   ./scripts/autopilot.sh ./work.sh 900
set -uo pipefail
WORK=${1:?usage: autopilot.sh <work-command> [cycle-seconds]}
CYCLE=${2:-900}
AGENT_ID=${AGENT_ID:-00}
cd "$(dirname "$0")/.."

while true; do
  echo "=== cycle $(date -u +%FT%TZ) agent $AGENT_ID ==="
  bash -c "$WORK" 2>&1 | tee -a "agents/$AGENT_ID/run.log"
  AGENT_ID="$AGENT_ID" ./scripts/sync.sh "agent $AGENT_ID: $(date -u +%FT%TZ)"
  ./scripts/ntfy.sh pub "[$AGENT_ID] status: cycle done $(date -u +%H:%M). $(tail -1 agents/$AGENT_ID/STATUS.md)"
  sleep "$CYCLE"
done
