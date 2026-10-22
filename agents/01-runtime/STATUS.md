# agent 01 — runtime & integration: STATUS

**M0 + M1 done** (2026-10-22, cycles 1–3). Code: `neurobrain` repo, branch
`agent-01` (fast-forwarded onto main after the M0 merge). brainbox 0.2.0.
Next: M2 (checkpoint dirs for grip), then M4, then M3.

## M1 numbers (`artifacts/api_m1_stress.json`, real ckpts, 2 threads)

| metric | value | bound |
|---|---|---|
| RSS growth, 200 sequential requests | **+0.3 MB** | ≤ 20 MB |
| /health during load (n=208) | p50 1.2 ms · max 9.1 ms | < 50 ms |
| /generate 16 tok p50 | 97 ms | — |
| /score p50 · /ground p50 | 5.0 ms · 15.0 ms | — |
| server peak RSS (LM+grip) | 299.5 MB (VmHWM) | < 1600 MB sandbox |
| /ground parity vs lab evaluate (n=256) | 0.531 vs 0.523 | — |
| tests | **21/21** | — |

API: `brainbox serve` → http://127.0.0.1:8321 (spec-change published:
default port). Wire keys spec-exact; 429 from governor with `reason`;
one model job at a time behind a queue; /health never queues.

## M0 numbers (kept for reference)

Real LM step 4600 (release ckpt-1022, sha-verified → `checkpoints/lm/`):
boot 1.003 s, peak RSS 272.1 MB, 20 tok @ 312 tok/s. `artifacts/bench_m0_real.json`.

Rebuild checkpoints after a rollback: `bash scripts/restore_data.sh` then
`python3 scripts/migrate_checkpoint.py checkpoints/lm_best.pt --out checkpoints/lm`.
