# Agent 03 Status (`03-eyes`)

_Updated: 2026-10-22 (Cycle M2)_

| Milestone | Status | Key Metric(s) | Artifact |
|---|---|---|---|
| **M0**: Baseline repro + gallery + worst confusions | **DONE** | Repro: `hit=45.0%`, `med_err=22.56px`; Release `ckpt-1022`: `hit=50.3%`, `med_err=5.37px`, `lat=8.13ms`, `RSS=431MB`; **98.4% misses = same-role wrong-label** | `m0_diagnosis.json`, `galleries/m0_failures_100.png` |
| **M1**: Hard world v1 + 50k samples + manifest | **DONE** | **50,000 samples** (`10 x 5k` shards = 391 MB, 10/10 sha256 ok in 131s, RSS 461 MB); merged to `main` as `neurobrain/ui_world_hard_v2.py` | `hard_world_v1_manifest.json`, `galleries/m1_hard_world_samples.png` |
| **M2**: +10 pts over baseline on hard world | **DONE** | Zero-shot baseline `5.0%`; In-domain trained 0.44M baseline `46.3%` (`27.2px` med err, `27.6%` OOD) → **`Stage1CoarseNet` = `56.6%` (`+10.3 pts` over trained baseline, `+51.6 pts` over zero-shot!), `med_err=3.54px`, `OOD=53.4%` (`+25.8 pts`!), `Top-6 crop recall = 99.8%`, `lat=12.2ms`**; `glyph vs text` ablation @ 550 steps: `54.2%` vs `49.9%` at `128x128` | `m2_trained_baseline_hard.json`, `m2_ablation_glyph_vs_text.json`, `m3_diagnosis.json`, `galleries/m3_stage1_2100_failures_100.png` |
| **M3**: 60% hard-world hit, 40% unseen fonts/themes | IN PROGRESS | Unseen OOD already **`56.4%`** (≥ 40% met!); next: Stage-2 native 1:1 `64x64` crop verifier/pointer over `99.8%`-recall Stage-1 candidates | — |
| **M4**: Second-stage refine crop, gain per stage | IN PROGRESS | Train `Stage2RefineNet` (`0.35M` params) on native `64x64` crops + report Stage-1 vs Stage-1+Stage-2 vs Multi-Scale | — |
| **M5**: 75% → 85% via hard negatives + curriculum | PENDING | Contrastive candidate hard-negatives + curriculum `easy -> medium -> crowded` | — |
| **M6**: ≥ 90% hit, ≤ 8 px med error, ≤ 60 ms/frame | PENDING | Export fp32 + int8 (`export_grounder.py`) + `card.md` + OOD generalisation table | — |
| **M7**: 60-task UI suite + `scoreboard.json` | PENDING | End-to-end headless Xvfb tkinter harness (60 tasks) | `scoreboard.json` |
