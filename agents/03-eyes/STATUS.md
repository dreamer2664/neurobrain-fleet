# Agent 03 Status (`03-eyes`)

_Updated: 2026-10-22 (Cycle M3–M5)_

| Milestone | Status | Key Metric(s) | Artifact |
|---|---|---|---|
| **M0**: Baseline repro + gallery + worst confusions | **DONE** | Repro: `hit=45.0%`, `med_err=22.56px`; Release `ckpt-1022`: `hit=50.3%`, `med_err=5.37px`, `lat=8.13ms`, `RSS=431MB` | `m0_diagnosis.json`, `galleries/m0_failures_100.png` |
| **M1**: Hard world v1 + 50k samples + manifest | **DONE** | **50,000 samples** (`10 x 5k` shards = 391 MB, 10/10 sha256 ok); merged to `main` as `neurobrain/ui_world_hard_v2.py` | `hard_world_v1_manifest.json`, `galleries/m1_hard_world_samples.png` |
| **M2**: +10 pts over baseline on hard world | **DONE** | In-domain trained 0.44M baseline `46.3%` (`27.2px` med err, `27.6%` OOD) → **`Stage1CoarseNet` = `56.6%` (`+10.3 pts` vs trained base, `+51.6 pts` vs zero-shot `5.0%`), `med_err=3.54px`, `OOD=58.0%`, `Top-7 recall = 99.8%`, `lat=12.4ms`** | `m2_trained_baseline_hard.json`, `m2_ablation_glyph_vs_text.json`, `m3_diagnosis.json` |
| **M3**: 60% hard-world hit, 40% unseen fonts/themes | **DONE** | **`hit=62.1%` @ 650 steps → `80.2%` @ 1700 steps** (`≥ 60%`); **unseen OOD fonts+themes = `73.4%`** (`≥ 40%`, `1.18px` med err!) | `m4_m5_ablations.json`, `m6_crnn_1700_eval.json` |
| **M4**: Second-stage refine crop, gain per stage | **DONE** | Stage-1 (`128x128`) = **`56.6%` (`3.54px`)** → Stage-1 + Stage-2 candidate-pinned CRNN (`32x160` native strip, `K=7`) = **`80.2%` (`+23.6 pts` gain, `med_err=0.93px`, `lat=29.97ms`)** | `m4_m5_ablations.json`, `m6_crnn_1700_eval.json`, `galleries/m6_crnn_1700_failures.png` |
| **M5**: 75% → 85% via hard negatives + curriculum | **75% DONE → 85% IN FLIGHT** | Controlled 650-step ablation: random-neg uniform `56.9%` → hard-neg uniform `58.1%` (`+1.2 pts`) → hard-neg + curriculum `62.1%` (`+4.0 pts`) → 1700-step CRNN **`80.2%`** (`field=92.4%`, `checkbox=87.6%`, `tab=81.5%`); upgrading `c8` to `stride=(2,1)` (`80` cols = `2.0px/col`) + listwise Top-7 reranking for 85% → ≥ 90% | `m4_m5_ablations.json`, `m6_crnn_1700_eval.json` |
| **M6**: ≥ 90% hit, ≤ 8 px med error, ≤ 60 ms/frame | IN PROGRESS | Med err already **`0.93 px`** (`≤ 8 px`) & latency **`29.97 ms`** (`≤ 60 ms`); pushing hit `80.2% → ≥ 90%` + `export_grounder.py` + `card.md` | — |
| **M7**: 60-task UI suite + `scoreboard.json` | PENDING | End-to-end headless Xvfb tkinter harness (60 tasks) | `scoreboard.json` |
