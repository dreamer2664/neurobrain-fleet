# agent 01 — runtime & integration: STATUS

**M0–M7 done** (2026-10-22, cycles 1–9; M4 landed before M3 by design). Code: `neurobrain` repo, branch
`agent-01` (fast-forwarded onto main after the M0 merge). brainbox 0.7.0.
Next: M8 20-task end-to-end suite.

## M1 numbers (`artifacts/api_m1_stress.json`, real ckpts, 2 threads)

| metric | value | bound |
|---|---|---|
| RSS growth, 200 sequential requests | **+0.3 MB** | ≤ 20 MB |
| /health during load (n=208) | p50 1.2 ms · max 9.1 ms | < 50 ms |
| /generate 16 tok p50 | 97 ms | — |
| /score p50 · /ground p50 | 5.0 ms · 15.0 ms | — |
| server peak RSS (LM+grip) | 299.5 MB (VmHWM) | < 1600 MB sandbox |
| /ground parity vs lab evaluate (n=256) | 0.531 vs 0.523 | — |
| tests | **61/61** | — |

API: `brainbox serve` → http://127.0.0.1:8321 (spec-change published:
default port). Wire keys spec-exact; 429 from governor with `reason`;
one model job at a time behind a queue; /health never queues.

## M0 numbers (kept for reference)

Real LM step 4600 (release ckpt-1022, sha-verified → `checkpoints/lm/`):
boot 1.003 s, peak RSS 272.1 MB, 20 tok @ 312 tok/s. `artifacts/bench_m0_real.json`.

Rebuild checkpoints after a rollback: `bash scripts/restore_data.sh` then
`python3 scripts/migrate_checkpoint.py checkpoints/lm_best.pt --out checkpoints/lm`.

## M2 numbers (`artifacts/migration_m2.json`)

Both current `.pt` files migrated to spec dirs and sha-verified against the
release: `checkpoints/lm/` (step 4600) + `checkpoints/grip/` (step 750,
441k params). Grip dir-vs-legacy predictions 20/20 identical; `doctor`
reports both with `verified=True` and fails (exit 1) on corruption.

## M4 numbers (`artifacts/undo_m4.json`)

100 delete/restore cycles (80 files + 20 dir trees): **100/100 byte-identical**
(sha256 verified both directions), p50 0.97 ms/cycle. `brainbox undo <task-id>`
restores from `~/.brainbox/trash/<task-id>/`; overwrite only with `--force`.

## M3 numbers (`artifacts/drive_m3.json`, 10 scripted tasks)

| | oracle grounder | real GripNet step 750 |
|---|---|---|
| terminal_rate (done/all) | 0.70 | 0.60 |
| closed_rate (any terminal state) | **1.00** | **1.00** |
| recovery_rate | 0.625 | 0.60 |
| retry_depth (non-done) | 4.67 | 5.0 |

The 3 non-done tasks are designed failures (unreachable widget ×2, starved
budget) plus a half-completed two-target task (done-partial, progress 0.5).
Perception gap oracle→real = exactly 1 task. Only remaining CLI stub: `kill` (M6).

## M5 numbers (`artifacts/packaging_m5.json`)

zipapp 212 KB builds in 0.05 s; wheel 77 KB in 1.0 s. Clean isolated venv
(create + install incl. torch CPU): **28.4 s < 60 s**, doctor ok (28.4 s had
torch from pip cache; brainbox's own share is <1 s — see NOTES for the failed
default-index attempt and why the CPU index is the documented command).
Windows: `docs/windows.md` (repo root `docs/`).

## M6 numbers (`artifacts/crash_m6.json`)

kill -9 mid-task → restart: interrupted task recorded `failed` (summary +
fatal history + run record), queued task behind it completed, 9/9 acceptance
checks pass, no stuck process. `brainbox run --watch ~/.brainbox/inbox`,
`brainbox autostart install` (systemd --user / schtasks), `brainbox kill`.
All 8 CLI verbs implemented.

## M7 numbers (`artifacts/quant_m7.json`)

int8 sidecars: LM 17.0→4.81 MB, grip 1.79→0.47 MB. Accuracy delta ~0
(LM loss +0.0005, top-1 40/40, grip hit −0.004). Runtime today: fp32 wins
(speed ~300 vs ~140–195 tok/s; peak RSS within noise either way, max 319 MB
vs 3000 MB target) — fp32 remains default; int8 is the disk/scale path.
Governor proven live (cap 200 MB → 429 on /generate, /health stays 200).
