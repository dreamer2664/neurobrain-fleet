# agent 01 — runtime & integration: STATUS

**M0 done** (2026-10-22, cycle 1). Code: `neurobrain` repo, branch `agent-01`
(package `brainbox/`, tests `tests/test_brainbox_m0.py`). Next: M1 (HTTP API).

## M0 numbers (measured, sandbox 2 CPU / 1982 MB, torch 2.14.1+cpu, 2 threads)

| metric | value | bound | artifact |
|---|---|---|---|
| boot (torch import + load) | **0.996 s** median of 3 | < 20 s | `artifacts/bench_m0.json` |
| peak RSS, bench | **272.1 MB** (internal == `/usr/bin/time -v`) | < 1600 MB sandbox | `artifacts/bench_m0.json` |
| generate 20 tokens | 0.063 s → 317 tok/s | — | `artifacts/bench_m0.json` |
| doctor RSS | 223 MB, exit 0 | — | `artifacts/doctor_m0.json` |
| tests | **11/11 pass** in 1.1 s | — | `artifacts/tests_m0.txt` |

⚠ Checkpoint is a **stub**: seeded random init, step 0, `stub: true`
everywhere. No trained `.pt` exists in git (`checkpoints/*.pt` is gitignored;
no releases). Architecture is exact — 4,247,264 params, matching
`reports/lm_summary.json` (step 4652) — and the tokenizer is the real one
(vocab 2052, sha256 `198316df…`), so timing/RSS numbers are representative;
generated text is noise. Blocked-on-coordinator (not blocking me): publish
`lm_best.pt` or a rebuild command so M0 can be re-run on trained weights.
