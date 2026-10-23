# agent 04 — STATUS

updated: 2026-10-23T01:00Z · branch: `agent-04` (both repos) · milestone: **M0 done · M1 val-loss BEATEN (2.0790 vs 2.2873) · M3 MET (terminal_rate 1.0)** · M2 12k done/pass@1 open · v2-corpus run next

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
| training | **run12k DONE: 12,000 steps, 73.7M tok, peak 1124MB**; val_loss **2.0790** (-9.1% vs baseline; beats lineage 2.09-2.12); drive 0.112 ui 0.674 |
| codebench run12k | pass@1 0.000 (M2 open); body_rate 0.000->**0.653** greedy / 0.735 sampled; 428 tok/s w/ KV cache |
| drive (M3) | **MET**: terminal_rate **1.0**, retry_after_failure 1.0, honest_completion 1.0 (n=48, mean_steps 2.7) |
| self-repair (M5) | baseline 0.000 -> **run12k 0.0408** (2 genuine one-shot repairs: cb-dict-02, cb-misc-06; transcripts in report) |
| card (D7) | **lm-run12k shipped WITH weights.pt** (17MB) + config hashes + samples incl. failures |
| next | v2-corpus run (one variable; scripts/run_v2.sh) -> M1 comparison vs run12k -> anneal/depth/EMA experiment queue; EI gated on pass@1>0 |
| corpus v2 | **BUILT**: 22.72M train tok + 569k val-plain + 379k val-instr; instr share 0.1993; 2.37 B/tok; 83.6k dup units dropped (49% dup rate); 434 generated + 860 vendored files dropped; holdout collisions 0; peak RSS 305MB |
| v2 baseline controls | code_val_v2_plain 2.4326 · code_val_v2_instr 2.5074 · drive_val 5.8343 (step-4600 ckpt) |
| checkpoint card | lm-baseline-step4600 packed (config.json w/ weights_sha256 per agent-01 spec, card.md w/ samples); mirrored here |
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
