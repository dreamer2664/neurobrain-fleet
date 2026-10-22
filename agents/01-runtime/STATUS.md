# agent 01 — runtime & integration: STATUS

**M0 done on the real checkpoint** (2026-10-22, cycles 1–2). Code:
`neurobrain` repo, branch `agent-01` (package `brainbox/`,
`tests/test_brainbox_m0.py`). Next: M1 (HTTP API).

## M0 numbers (sandbox 2 CPU / 1982 MB, torch 2.14.1+cpu, 2 threads)

Real LM = release `ckpt-1022` `lm_best.pt` (step 4600, sha256 `0df9f2f6…`
verified against the release digest), migrated to `checkpoints/lm/`.
Rebuild locally:

```bash
curl -L -o checkpoints/lm_best.pt https://github.com/dreamer2664/neurobrain/releases/download/ckpt-1022/lm_best.pt
python3 scripts/migrate_checkpoint.py checkpoints/lm_best.pt --out checkpoints/lm
python3 -m brainbox bench --checkpoint checkpoints/lm --tokens 20
```

| metric | real (step 4600) | stub (cycle 1) | bound | artifact |
|---|---|---|---|---|
| boot (torch import + load) | **1.003 s** median of 3 | 0.996 s | < 20 s | `artifacts/bench_m0_real.json` |
| peak RSS, bench | **272.1 MB** (internal == `/usr/bin/time -v`) | 272.1 MB | < 1600 MB sandbox | `artifacts/bench_m0_real.json` |
| generate 20 tokens | 0.064 s → 312 tok/s | 317 tok/s | — | `artifacts/bench_m0_real.json` |
| doctor | exit 0, 223 MB, finds real ckpt | stub-flagged | — | `artifacts/doctor_m0_real.json` |
| tests | **11/11 pass** in ~1.1 s | — | — | `artifacts/tests_m0.txt` |

Cycle 1 ran on a seeded stub (exact 4,247,264-param architecture + real
tokenizer, `stub: true` everywhere) because no trained `.pt` was published
yet; its timing/RSS predictions matched the real checkpoint to within noise.
Stub artifacts (`bench_m0.json`, `doctor_m0.json`) kept for the record.
