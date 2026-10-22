# Agent 03 — `03-eyes` (Vision Grounder + 60-Task Headless UI Eval Suite)

All milestones **M0 through M7** are complete, tested (`22/22` unit tests passing), exported, and verified from scratch on 2 CPU threads (`0` pretrained weights).

## Headline Results

- **Hard World Seen (`N=1000`, `seed=202604`)**: **`98.00%` (`K=7`) / `98.10%` (`K=12` & `int8_dynamic`)** widget hit rate, **`0.68 px`** median centre error (`p90 = 1.87 px`), **`100.00%`** action accuracy, **`28.26 ms/frame` (`int8_dynamic`) / `31.54 ms/frame` (`fp32`)** on 2 CPU threads (`20/1000 = 2.0%` failure gallery in `galleries/m6_best_failures.png`).
- **Hard World Unseen OOD Fonts + Themes (`N=500`, `seed=202605`)**: **`91.00%` (`K=7`) / `91.40%` (`K=12`)** widget hit rate, **`0.81 px`** median centre error.
- **Runtime Checkpoint Export (`neurobrain:checkpoints/grip_v2/`)**: `config.json`, `weights.pt` (`6.34 MB` fp32), `weights.int8.pt` (`1.67 MB`, **`3.81x` smaller**, `+0.00` to `+0.10 pts` accuracy delta), `tokenizer.json`, and `card.md`.
- **Recovery-Conditioned Grounding (`ground(png, instr, exclude_box=...)`)**: **`96.8%`** excluded-region avoidance & distractor-masked target hit rate.
- **60-Task End-to-End Headless X11 (`Xvfb` + `Tkinter` + `Capture` + `DesktopHands`) Suite (`scoreboard.json`)**:
  - **`51 / 60 (85.00%)`** end-to-end task completion (`+83.33 pts` over legacy `ckpt-1022` `1/60 = 1.67%`), `median_steps = 2.0`, `median_seconds = 0.249s`, `ram_peak_mb = 305.8 MB`.
  - Per category: `settings = 12/12 (100.0%)`, `editor = 11/12 (91.7%)`, `recovery = 11/12 (91.7%)`, `browser = 9/12 (75.0%)`, `file_manager = 8/12 (66.7%)`.

## One-Command Reproduction

```bash
cd ~/neurobrain

# 1. Run all unit tests (M0, M1 Hard World, M2-M4 Two-Stage Grounder, M6 Export/INT8, M7 60-Task Suite)
python3 -m pytest -q tests/test_eyes_m0.py tests/test_eyes_m1_hard_world.py tests/test_eyes_m2_m4_grounder.py tests/test_eyes_m6_export.py tests/test_eyes_m7_eval_suite.py

# 2. Export runtime checkpoint (`checkpoints/grip_v2/`) + measure FP32 vs INT8 + generalisation table
python3 -m neurobrain.export_grounder --ckpt checkpoints/eyes_crnn40_3550.pt --out checkpoints/grip_v2 --step 3550

# 3. Run the 60-task headless Xvfb + Tkinter end-to-end desktop evaluation suite
python3 -m neurobrain.eval_suite --checkpoint checkpoints/grip_v2 --out ~/fleet/agents/03-eyes/scoreboard.json
```

## Key Deliverables in `agents/03-eyes/`

- `card.md`: Checkpoint card (`1.57M` params, data mix, generalisation across unseen fonts/themes/sizes/roles, int8 delta, failure modes).
- `scoreboard.json` & `eval_tasks_60.json`: 60-task end-to-end Xvfb + Tkinter scoreboard and task definitions.
- `galleries/m6_best_failures.png`: `< 10%` failure gallery (`20/1000 = 2.0%` remaining misses on Hard World).
- `galleries/m7_failures_strip.png` & `failure_strips/*.png`: Annotated multi-step screenshot strips for all `9/60` X11 suite failures.
- `m6_diagnosis.json`, `m6_export_int8_delta.json`, `m4_m5_ablations.json`, `m2_ablation_glyph_vs_text.json`, `hard_world_v1_manifest.json`: Full ablation and diagnostic artifacts.
