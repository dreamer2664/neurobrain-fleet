# Agent 03 Status (`03-eyes`)

_Updated: 2026-10-22 (Cycle M0)_

| Milestone | Status | Key Metric(s) | Artifact |
|---|---|---|---|
| **M0**: Baseline repro + gallery + worst confusions | **DONE** | Repro: `hit=45.0%`, `med_err=22.56px`; Release `ckpt-1022`: `hit=50.3%`, `med_err=5.37px` (`mean=26.04px`), `lat=8.13ms`, `RSS=431MB`; **98.4% of misses are same-role wrong-label** | `m0_diagnosis.json`, `galleries/m0_failures_100.png` |
| **M1**: Hard world v1 + 50k samples + manifest | IN PROGRESS | Target: 50k shards (`10 x 5k`), real 8–14px fonts, toolbars/tabs/sidebars/dialogs/lists, states, DPI, JPEG/cursor | `neurobrain/ui_world_hard.py` |
| **M2**: +10 pts over baseline on hard world | PENDING | Beat baseline GripNet on hard world by ≥ +10.0 pts | — |
| **M3**: 60% hard-world hit, 40% unseen fonts/themes | PENDING | ≥ 60% seen, ≥ 40% OOD fonts/themes | — |
| **M4**: Second-stage refine crop, gain per stage | PENDING | Report Stage-1 vs Stage-1+Stage-2 hit & px error | — |
| **M5**: 75% → 85% via hard negatives + curriculum | PENDING | Ablation table: curriculum + hard-neg mining | — |
| **M6**: ≥ 90% hit, ≤ 8 px med error, ≤ 60 ms/frame | PENDING | Export fp32 + int8 (`export_grounder.py`) + `card.md` | — |
| **M7**: 60-task UI suite + `scoreboard.json` | PENDING | End-to-end headless Xvfb tkinter harness (60 tasks) | `scoreboard.json` |
