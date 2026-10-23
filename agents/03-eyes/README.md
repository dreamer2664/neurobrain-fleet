# Agent 03 — `03-eyes` (Open-Vocabulary Vision Grounder `grip_v3` + MockDesktopOS + Autonomous Googling Brain)

All foundation milestones (**M0–M7**) and continuous desktop/search brain milestones (**M8–M10**) are complete, tested (`26/26` unit tests passing), exported, and verified 100% from scratch on 2 CPU threads (`0` pretrained weights, `0` external AI services).

## Headline Results

- **Open-Vocabulary Two-Stage `EyesGrounder` (`checkpoints/grip_v3/`, `1,568,492` params)**:
  - **Hard World Seen (`N=1000`, `seed=202604`)**: **`98.60%` (`fp32` & `int8`)**, **`0.68 px`** median centre error, **`100.00%`** action accuracy, **`38.2–39.2 ms/frame`** on 2 CPU threads (`+0.50 pts` over `grip_v2` `98.10%`).
  - **Hard World Unseen OOD Fonts + Themes (`N=500`, `seed=202605`)**: **`96.00%` (`fp32`) / `95.80%` (`int8`)**, **`0.79 px`** median centre error (`+4.60 pts` over `grip_v2` `91.40%`).
  - **Strictly Held-Out Unseen Open-Vocab Multi-Word + Digit Phrases (`N=250`, `seed=202609`)**: **`58.80%` (`fp32`) / `59.20%` (`int8`)**, **`2.14 px`** median error (`+33.60 pts` over `grip_v2` `25.20%` chance baseline).
  - **INT8 Compression**: `6.34 MB` fp32 → **`1.67 MB` int8 (`3.81x` smaller)** with **`0.00 pts`** delta on Hard Seen.
- **M7 60-Task Headless X11 Desktop Suite (`scoreboard.json`)**:
  - **`60 / 60 (100.00%)`** (`+15.00 pts` over `grip_v2` `51/60 = 85.00%`, `+98.33 pts` over `ckpt-1022` `1/60 = 1.67%`): **`12/12` in all 5 categories** (`browser`, `editor`, `file_manager`, `recovery`, `settings`), `6/6 (100%)` Rung-2 recovery, `med_sec = 0.227s`, `RAM = 305.7 MB`.
- **M8/M9 40-Task Multi-Window `MockDesktopOS` + "MiniGoogle" Search Suite (`m9_desktop_grip_v3.json`)**:
  - **`36 / 40 (90.00%)`** (`+67.50 pts` over zero-shot `grip_v2` `9/40 = 22.50%`): `desktop_nav = 10/10 (100%)`, `research_workflow = 9/10 (90%)`, `adversarial_desktop = 9/10 (90%)`, `google_search = 8/10 (80%)`.
- **M10 30-Task Unscripted Autonomous Desktop & Googling Suite (`DesktopBrainPolicy` + `grip_v3`, `m10_unscripted_autonomous_x11.json`)**:
  - Single natural-language user goal → pure closed-loop X11 pixel perception & control (`0` scripted sub-steps, `0` DOM access): **`24 / 30 (80.00%)`** (`+80.00 pts` over random baseline `0/30`), **`18 / 20 (90.0%)`** on seen phrasing templates and **`6 / 10 (60.0%)`** on strictly held-out unseen OOD phrasings (`google_lookup = 6/6`, `google_bookmark = 5/5`, including live X11 browser `back`-button visual self-recovery).

## One-Command Reproduction

```bash
cd ~/neurobrain

# 1. Run all 26 unit tests (M0..M10)
python3 -m pytest -q tests/test_eyes_m0.py tests/test_eyes_m1_hard_world.py tests/test_eyes_m2_m4_grounder.py tests/test_eyes_m6_export.py tests/test_eyes_m7_eval_suite.py tests/test_eyes_m8_mock_desktop.py tests/test_eyes_m9_openvocab.py tests/test_eyes_m10_desktop_policy.py

# 2. Run M7 60-task headless X11 desktop suite (60/60 = 100.00%)
python3 -m neurobrain.eval_suite --checkpoint checkpoints/grip_v3 --out ~/fleet/agents/03-eyes/scoreboard.json

# 3. Run M8/M9 40-task multi-window MockDesktopOS + MiniGoogle search suite (36/40 = 90.00%)
python3 -m neurobrain.mock_desktop --checkpoint checkpoints/grip_v3 --out ~/fleet/agents/03-eyes/m9_desktop_grip_v3.json

# 4. Train & evaluate M10 autonomous unscripted DesktopBrainPolicy + grip_v3 (24/30 = 80.00%)
python3 -m neurobrain.desktop_policy --steps 1500 --episodes 700 --policy-dir checkpoints/desktop_brain_v1 --grounder-dir checkpoints/grip_v3
```

## Key Deliverables in `agents/03-eyes/`

- `card.md`: Updated checkpoint card covering `grip_v3`, `grip_v2`, and `desktop_brain_v1`.
- `scoreboard.json`: `60 / 60 (100.00%)` 60-task X11 scoreboard.
- `m8_desktop_zeroshot_grip_v2.json` & `m9_desktop_grip_v3.json`: `9/40 (22.50%) -> 36/40 (90.00%)` 40-task MockDesktopOS + MiniGoogle scoreboards.
- `m10_unscripted_random_baseline.json` & `m10_unscripted_autonomous_x11.json`: `0/30 (0.00%) -> 24/30 (80.00%)` unscripted autonomous live X11 scoreboards.
- `galleries/m10_autonomous_googling_showcase.png`: Step-by-step live X11 strips showing unscripted Googling, ad avoidance, browser `back`-button visual self-correction, and cross-app Notes persistence.
