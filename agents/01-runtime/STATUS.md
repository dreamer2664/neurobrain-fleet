# agent 01 — runtime & integration: STATUS

**M0 + M1 + M2 + M4 done** (2026-10-22, cycles 1–5). Code: `neurobrain` repo, branch
`agent-01` (fast-forwarded onto main after the M0 merge). brainbox 0.3.0.
Next: M3 (drive loop, 10 scripted tasks), then M5 packaging.

## M1 numbers (`artifacts/api_m1_stress.json`, real ckpts, 2 threads)

| metric | value | bound |
|---|---|---|
| RSS growth, 200 sequential requests | **+0.3 MB** | ≤ 20 MB |
| /health during load (n=208) | p50 1.2 ms · max 9.1 ms | < 50 ms |
| /generate 16 tok p50 | 97 ms | — |
| /score p50 · /ground p50 | 5.0 ms · 15.0 ms | — |
| server peak RSS (LM+grip) | 299.5 MB (VmHWM) | < 1600 MB sandbox |
| /ground parity vs lab evaluate (n=256) | 0.531 vs 0.523 | — |
| tests | **34/34** (M0–M2+M4) | — |

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
