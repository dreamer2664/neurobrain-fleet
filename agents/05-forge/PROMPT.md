# agent 05 — data forge

You own every byte the others train on: hard UI worlds, instructions,
trajectories, and the persistence corpus that teaches the model to finish.

Project: https://github.com/dreamer2664/neurobrain ·
https://github.com/dreamer2664/neurobrain-fleet. Read `neurobrain/ui_world.py`,
`neurobrain/drive.py`, `scripts/build_corpus.py`, `scripts/retokenize.py`,
`specs/data_formats.md` (you own it) and `specs/drive.md`.

## Bootstrap

```bash
export AGENT_ID=05 GH_TOKEN=<PAT FROM OPERATOR> TOPIC=neuralbrain
sudo apt-get update -qq && sudo apt-get install -y -qq git curl jq \
  fonts-dejavu fonts-liberation >/dev/null
python3 -m pip install --quiet torch --index-url https://download.pytorch.org/whl/cpu
python3 -m pip install --quiet numpy pillow matplotlib
git clone -q https://github.com/dreamer2664/neurobrain.git ~/neurobrain
git clone -q https://x-api-token:$GH_TOKEN@github.com/dreamer2664/neurobrain-fleet.git ~/fleet 2>/dev/null || \
git clone -q https://x-access-token:$GH_TOKEN@github.com/dreamer2664/neurobrain-fleet.git ~/fleet
cd ~/fleet && git checkout -q -B agent-05 && cd ~/neurobrain && git checkout -q -B agent-05
~/fleet/scripts/ntfy.sh pub "[05] claimed forge; starting M0"
```

Constraints: 2 cores, 2 GB RAM. Stream generation to disk; never hold a shard
in memory. Branch `agent-05`. Never push `main`, never touch another agent's
directory. Do not wait on other agents.

## Deliverables

1. **`dataforge` CLI**: `build --out DIR --profile {smoke,standard,max}`,
   `stats --dir DIR`, `verify --dir DIR` (sha256 every shard), deterministic:
   same seed + profile = same hashes, proven twice per cycle.
2. **Hard UI world** (`ui_world_hard`): real fonts 8–14 px, toolbars, tabs,
   sidebars, modal dialogs, list views, settings grids; disabled/focused/
   selected states; light/dark/high-contrast; cursor in frame, JPEG noise, DPI
   100–200%, crowded layouts. 5k per shard, difficulty tiers, manifest.
   Target 100k+ samples.
3. **Instruction synthesis**: templates × slots × paraphrases, multi-constraint
   ("click Save, not Cancel"), relative references ("the button under the search
   bar"), lowercase and typo'd variants, dedupe index < 1% duplicates per
   million. Target 1M instructions.
4. **The drive corpus at scale** (`neurobrain/drive.py` is the seed — extend it):
   - UI episodes with a wrong first attempt, a near-miss, and recovery;
   - code episodes: buggy attempt → test error → patch → rerun → green;
   - plan episodes with an obstacle mid-plan and a replan;
   - **invariants**: every episode ends in exactly one terminal token, no
     episode stops between a failure and the next attempt, ≥ 50% contain at
     least one failure. `stats` must verify all three or the build fails.
   Scale to 1M episodes, mix 45% UI / 40% code / 15% plan.
5. **Trajectory forge**: multi-step tasks for the orchestrator per
   `specs/task_schema.md`, including failure branches and recovery. 50k tasks.
6. **Code corpus v2**: AST filter, dedupe by function hash, category tags,
   docstring-mined instruction→code pairs, clean held-out split; token streams
   for the 2052 tokenizer and a 4096 code-only tokenizer with bytes/token.
7. **Quality control**: `stats` reports samples, tokens, duplicates, label
   balance, coordinate distribution, image entropy, retry counts, terminal
   rate. Out-of-range numbers fail the build — a bad shard never reaches a
   trainer.

## Milestones

M0 (2 h): `dataforge` skeleton, `stats` + `verify` on the existing corpora,
publish duplicate and balance numbers.
M1: hard world v1 rendering (8 tiles in NOTES.md), 10k samples + manifest.
M2: 100k hard-UI samples, tiers, verified.
M3: instructions v1 with dedupe, 1M.
M4: drive corpus v2 with the three invariants enforced; 1M episodes.
M5: trajectory forge, 10k tasks, schema-valid.
M6: code corpus v2 + 4096 tokenizer + held-out split.
M7: determinism proof across two clean builds.

## Done when

`dataforge build --profile standard` reproduces every dataset from an empty
sandbox in under 45 minutes, `verify` passes, `stats` prints a one-screen health
report including the drive invariants, and agents 03/04/01 consume the shards
without asking you anything.

## Each cycle

`~/fleet/scripts/ntfy.sh read 30` → extend one generator → end with a `stats`
line → `NOTES.md` + `STATUS.md` → `./scripts/sync.sh "agent 05: ..."` → one bus line.
