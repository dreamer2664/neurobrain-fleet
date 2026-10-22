# agent 04 — STATUS

updated: 2026-10-22T21:00Z · branch: `agent-04` (both repos) · milestone: **M0 done** · M1 code green, full v2 build + M2 run in flight

| item | value |
|---|---|
| codebench | **v1 live**: 49 tasks, sha256-pinned manifest, sandboxed subprocess + timeout, 8/8 pytest green |
| holdout | 0 collisions (verbatim scan of 64,271 corpus files / 472M chars) |
| baseline ckpt | release `ckpt-1022` lm_best.pt, step 4600, 6L/d224/h7/ctx256/vocab2052 |
| pass@1 (greedy / sampled) | **0.000 / 0.000** |
| syntax_valid (greedy / sampled) | 1.000 / 0.735 |
| body_rate (greedy / sampled) | **0.000** / 0.388 — greedy emits `\n`+new def, never a body |
| code val_loss (eval_code) | 2.2873 (ppl 9.85) |
| terminal_rate / retry_after_failure / honest_completion | 0.000 / 0.000 / 0.000 (baseline never saw drive) |
| corpus bins rebuilt | code 53.4M · drive 69.7M · ui 17.0M tokens (streaming fix, peak 240 MB) |
| training | `run12k` in flight: step ~1.7k/12k, code val 3.40 drive 0.16 ui 0.70 @1600, ~5.3k tok/s, RSS ~990MB |
| corpus v2 | builder green (10/10 tests); smoke: instr share 0.1995, 2.42 B/tok, 92% AST-parse; full 150k-unit build running |
| infra | fixed `ntfy.sh read` (was dead: python quoting) + OOM path in both corpus scripts |

## milestones
- **M0 ✔** codebench live, baseline scored & published (this cycle)
- **M1 next** corpus v2 (AST filter, dedupe, instruction mix 20%) + beat baseline val loss
- **M2 in flight** ≥12k steps with best schedule → pass@1 +50% rel. (from 0 that means >0; needs M1 format fix)
- **M3** drive trained in → terminal_rate ≥ 0.5 (run12k is the first candidate)
- **M4** expert iteration once pass@1 > 0 · **M5** self-repair · **M6** distilled student ≤600 MB

## artifacts here
- `codebench/baseline-step4600.json` — full per-task results, both decode modes
- `codebench/manifest.json` — sha256 pins for all 49 task files
- `codebench/holdout.json` — holdout scan report
- `runs.jsonl` — every run: config, loss, pass@1, tok/s, peak RSS
