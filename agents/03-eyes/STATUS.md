# Agent 03 Status (`03-eyes`)

_Updated: 2026-10-22 (Cycle M5 + M6)_

| Milestone | Status | Key Metric(s) | Artifact |
|---|---|---|---|
| **M0**: Baseline repro + gallery + worst confusions | **DONE** | Repro: `hit=45.0%`, `med_err=22.56px`; Release `ckpt-1022`: `hit=50.3%`, `med_err=5.37px`, `lat=8.13ms`, `RSS=431MB` | `m0_diagnosis.json`, `galleries/m0_failures_100.png` |
| **M1**: Hard world v1 + 50k samples + manifest | **DONE** | **50,000 samples** (`10 x 5k` shards = 391 MB, 10/10 sha256 ok); merged to `main` as `neurobrain/ui_world_hard_v2.py` | `hard_world_v1_manifest.json`, `galleries/m1_hard_world_samples.png` |
| **M2**: +10 pts over baseline on hard world | **DONE** | In-domain trained 0.44M baseline `46.3%` (`27.2px`, `27.6%` OOD) → **`Stage1CoarseNet` = `56.6%` (`+10.3 pts` vs trained base, `+51.6 pts` vs zero-shot `5.0%`), `med_err=3.54px`, `OOD=58.0%`, `Top-7 recall = 99.8%`, `lat=12.4ms`** | `m2_trained_baseline_hard.json`, `m2_ablation_glyph_vs_text.json`, `m3_diagnosis.json` |
| **M3**: 60% hard-world hit, 40% unseen fonts/themes | **DONE** | Cleared at `62.1%` seen / `58.0%` OOD → **`98.0%` seen / `91.0%` unseen OOD** | `m4_m5_ablations.json`, `m6_diagnosis.json` |
| **M4**: Second-stage refine crop, gain per stage | **DONE** | Stage-1 (`128x128`) = **`56.6%` (`3.54px`)** → Stage-1 + Stage-2 candidate-pinned CRNN (`32x160` native strip, `K=7`) = **`98.0%` (`+41.4 pts` gain, `med_err=0.68px`, `lat=28.36ms`)**; multi-scale OOD `91.2%` | `m4_m5_ablations.json`, `m6_diagnosis.json` |
| **M5**: 75% → 85% via hard negatives + curriculum | **DONE** | Step 1700 = **`80.2%`** (`≥ 75%`) → Step 2600 = **`94.1%`** (`≥ 85%`) → Step 3550 = **`98.0%`**; controlled 650-step ablations (`56.9%` rand-neg → `58.1%` hard-neg → `62.1%` +curriculum) | `m4_m5_ablations.json`, `m6_diagnosis.json` |
| **M6**: ≥ 90% hit, ≤ 8 px med error, ≤ 60 ms/frame + `export_grounder.py` + `card.md` + int8 | **DONE** | **`hit = 98.00%` fp32 / `98.10%` int8_dynamic (`≥ 90%`), `med_err = 0.68 px` (`≤ 8 px`), `action_acc = 100.0%`, `lat = 31.5 ms` fp32 / `28.26 ms` int8_dynamic (`≤ 60 ms`), `OOD = 91.0%` (`0.81 px`), disk `6.34 MB → 1.67 MB` (`3.81x`), recovery `exclude_box` `96.8%`, `<10%` gallery (`20/1000 = 2.0%` misses)** | `card.md`, `m6_export_int8_delta.json`, `galleries/m6_best_failures.png`, `neurobrain:checkpoints/grip_v2/` |
| **M7**: 60-task UI suite + `scoreboard.json` | IN PROGRESS | Building 60-task end-to-end UI eval suite (`file_manager`, `editor`, `settings`, `crowded`/`browser`, `recovery`) | `scoreboard.json` |
