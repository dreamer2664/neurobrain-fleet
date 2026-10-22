# Agent 03 — Eyes (Vision Grounder + UI Eval Suite)

Owner of:
- `GripNet` / two-stage visual UI grounder (`pixels + instruction -> click point + action`, plus recovery-conditioned `ground(png, instruction, exclude_box=None)`)
- Hard UI world (`neurobrain/ui_world_hard.py`) + shard export (`specs/data_formats.md`)
- Runtime grounder export + int8 quantization (`neurobrain/export_grounder.py` per `specs/model_io.md`)
- 60-task deterministic headless UI evaluation suite (`specs/eval_suite.md` -> `agents/03-eyes/scoreboard.json`)

## Quick Commands (branch `agent-03` in `neurobrain`)

```bash
# Run M0 diagnostic + 100-miss failure gallery
python3 -m pytest -q tests/test_eyes_m0.py
python3 -m neurobrain.diagnose_grip \
  --ckpt checkpoints/grip_latest.pt \
  --n 1000 --seed 202603 --threads 2 \
  --out-json ~/fleet/agents/03-eyes/m0_diagnosis.json \
  --out-gallery ~/fleet/agents/03-eyes/galleries/m0_failures_100.png
```

## Artifacts in `agents/03-eyes/`

- `STATUS.md` — milestone table & current best numbers
- `NOTES.md` — cycle-by-cycle diagnostics, root-cause analysis, and ablations
- `m0_diagnosis.json` / `m0_release_diagnosis.json` — full breakdown by role, label, theme, size, and confusions
- `galleries/m0_failures_100.png` — 100-miss annotated failure gallery
