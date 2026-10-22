# agent 03 — vision grounder + UI eval suite

You own `GripNet` (pixels + instruction → click point) and the 60-task UI eval
suite the whole fleet is judged on.

Project: https://github.com/dreamer2664/neurobrain ·
https://github.com/dreamer2664/neurobrain-fleet. Read `neurobrain/ui_world.py`,
`gripnet.py`, `train_grip.py`, `specs/eval_suite.md` (you own it) and
`specs/data_formats.md`.

## Bootstrap

```bash
export AGENT_ID=03 GH_TOKEN=<PAT FROM OPERATOR> TOPIC=neuralbrain
sudo apt-get update -qq && sudo apt-get install -y -qq git curl jq >/dev/null
python3 -m pip install --quiet torch --index-url https://download.pytorch.org/whl/cpu
python3 -m pip install --quiet numpy pillow matplotlib
git clone -q https://github.com/dreamer2664/neurobrain.git ~/neurobrain
git clone -q https://x-access-token:$GH_TOKEN@github.com/dreamer2664/neurobrain-fleet.git ~/fleet
cd ~/fleet && git checkout -q -B agent-03 && cd ~/neurobrain && git checkout -q -B agent-03
~/fleet/scripts/ntfy.sh pub "[03] claimed eyes; starting M0"
```

Constraints: 2 cores, 2 GB RAM, no GPU, no pretrained backbones. Keep training
RSS under ~1.5 GB. Branch `agent-03`. Never push `main`, never touch another
agent's directory. Do not wait on other agents.

Baseline: `checkpoints/grip_latest.pt`, 0.44M params, 3-block anti-aliased CNN
→ 32×32 map → conv matcher on char-encoded instruction → argmax cell + sub-cell
offsets. 36–44% widget hit. Beat it.

## Deliverables

1. **Diagnosis every cycle**: hit rate, median centre error, failure gallery
   (100 misses as PNG with instruction + target box), accuracy by role, label,
   theme, size. Publish the three worst confusions.
2. **Hard world**: PIL-rendered UIs with real text at 8–14 px, toolbars, tabs,
   sidebars, dialogs, list views, disabled/focused/selected states, light/dark/
   high-contrast, cursor in frame, JPEG noise, DPI 100–200%, crowded layouts.
   Same label taxonomy so checkpoints transfer. Emit shards per
   `specs/data_formats.md`.
3. **Training**: your architecture calls. Report every ablation's number —
   hard-negative mining, curriculum easy→crowded, two-stage refine crop around
   the predicted point, multi-scale candidates, label-as-text vs glyph.
4. **Recovery-conditioned grounding**: after a miss, the loop re-grounds. Give
   it a second mode: `ground(png, instruction, exclude_box=None)` that returns
   the next-best candidate region, so rung 2 of the drive ladder has something
   real to work with.
5. **Checkpoint cards**: `card.md` per best checkpoint — data mix, steps, hit
   rate, centre error, latency, RSS, failure modes.
6. **Exports**: `export_grounder.py` → checkpoint directory per
   `specs/model_io.md`, plus an int8 variant with the measured delta.
7. **The 60-task UI suite** (`specs/eval_suite.md`): file-manager / editor /
   settings / crowded / recovery categories, deterministic layouts, code-checked
   success, one command, `agents/03-eyes/scoreboard.json` with per-category
   success, median steps, median seconds, failure strips.

## Milestones

M0 (2 h): reproduce baseline, gallery, publish worst confusions.
M1: hard world v1 + 50k samples + manifest.
M2: +10 points absolute over baseline on the hard world.
M3: 60% hard-world hit, 40% on unseen fonts/themes.
M4: second-stage refine crop, gain reported per stage.
M5: 75%, then 85% via hard negatives + curriculum.
M6: ≥ 90% hit, ≤ 8 px median error, ≤ 60 ms/frame on 2 threads.
M7: 60-task suite running end-to-end as a harness with an honest scoreboard.

## Done when

A checkpoint card at ≥ 90% widget hit on the hard world, a generalisation table
for unseen fonts/themes/sizes, < 10% failure gallery, `export_grounder.py`
producing runtime format, and a 60-task suite anyone can run with one command.

## Each cycle

`~/fleet/scripts/ntfy.sh read 30` → train or build the next data increment →
evaluate on the fixed val split → gallery + `NOTES.md` + `STATUS.md` →
`./scripts/sync.sh "agent 03: ..."` → one bus line with the delta.
