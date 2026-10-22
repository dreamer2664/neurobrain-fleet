# Agent 03 Status (`03-eyes`)

_Updated: 2026-10-22 (Cycle M1)_

| Milestone | Status | Key Metric(s) | Artifact |
|---|---|---|---|
| **M0**: Baseline repro + gallery + worst confusions | **DONE** | Repro: `hit=45.0%`, `med_err=22.56px`; Release `ckpt-1022`: `hit=50.3%`, `med_err=5.37px` (`mean=26.04px`), `lat=8.13ms`, `RSS=431MB`; **98.4% of misses are same-role wrong-label** | `m0_diagnosis.json`, `galleries/m0_failures_100.png` |
| **M1**: Hard world v1 + 50k samples + manifest | **DONE** | **50,000 samples** (`10 x 5k` shards = 391 MB, 10/10 sha256 verified in 131s, RSS 461 MB); 5 UI archetypes, 8–14px real text, states, DPI 100–200%, cursor, JPEG noise, disjoint OOD split; zero-shot `ckpt-1022` = `5.0%` hit (`92.5px` med err) | `hard_world_v1_manifest.json`, `galleries/m1_hard_world_samples.png`, `m1_hard_zeroshot_baseline.json` |
| **M2**: +10 pts over baseline on hard world | IN PROGRESS | Train baseline 0.44M `GripNet` on 50k hard shards to set trained-baseline bar, then beat by ≥ +10 pts with shift-invariant text + FiLM/cross-attn matcher | — |
| **M3**: 60% hard-world hit, 40% unseen fonts/themes | PENDING | ≥ 60% seen, ≥ 40% OOD fonts/themes | — |
| **M4**: Second-stage refine crop, gain per stage | PENDING | Report Stage-1 vs Stage-1+Stage-2 hit & px error | — |
| **M5**: 75% → 85% via hard negatives + curriculum | PENDING | Ablation table: curriculum + hard-neg mining | — |
| **M6**: ≥ 90% hit, ≤ 8 px med error, ≤ 60 ms/frame | PENDING | Export fp32 + int8 (`export_grounder.py`) + `card.md` | — |
| **M7**: 60-task UI suite + `scoreboard.json` | PENDING | End-to-end headless Xvfb tkinter harness (60 tasks) | `scoreboard.json` |
