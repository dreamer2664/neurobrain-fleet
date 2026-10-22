#!/usr/bin/env bash
# Survival sync: sandboxes roll back and often lose .git entirely.
# This re-creates the repo if needed, then commits + pushes the current branch.
#
#   ./scripts/sync.sh "message"
#
# Requires $GH_TOKEN (PAT with repo write). Never stores the token in the repo.
set -uo pipefail
cd "$(dirname "$0")/.."

MSG=${1:-"sync $(date -u +%FT%TZ)"}
AGENT_ID=${AGENT_ID:-coordinator}
BRANCH=$(git symbolic-ref --short HEAD 2>/dev/null || echo main)
: "${GH_TOKEN:?set GH_TOKEN first}"
FLEET="dreamer2664/neurobrain-fleet"

if [ ! -d .git ] || ! git rev-parse --git-dir >/dev/null 2>&1; then
  echo "[sync] no repo, re-initialising"
  rm -rf .git
  git init -q -b "$BRANCH"
  git config user.name "agent-$AGENT_ID"
  git config user.email "agent$AGENT_ID@fleet.local"
fi

git remote remove origin 2>/dev/null || true
git remote add origin "https://x-access-token:${GH_TOKEN}@github.com/${FLEET}.git"

if [ "$BRANCH" != "main" ]; then
  git fetch -q origin "$BRANCH" 2>/dev/null && git reset -q --soft "origin/$BRANCH" 2>/dev/null
fi

git add -A
if git diff --cached --quiet; then
  echo "[sync] nothing to commit"
else
  git commit -q -m "$MSG"
fi
git push -q -u origin "$BRANCH" && echo "[sync] pushed $BRANCH: $MSG" || echo "[sync] push failed"
git remote set-url origin "https://github.com/${FLEET}.git"
