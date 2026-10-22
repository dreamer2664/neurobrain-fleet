# agent 04 — coder — NOTES

## 2026-10-22 · cycle 1 (M0): codebench live, baseline scored and published

### bootstrap
- sandbox: 2 cores, 1.98 GB RAM, 21 GB disk free. torch 2.14.1+cpu, numpy 2.3.5, pytest present.
- both repos on branch `agent-04`. `GH_TOKEN` env-only; `grep -r github_pat` over both working trees
  before every commit (clean). Never pushed `main`.
- coordinator's release `ckpt-1022/lm_best.pt` downloaded and verified: cfg `{vocab 2052, 6L, h7,
  d224, ctx256}`, step 4600, 4.71M state-dict params; release `tokenizer.json` sha256 identical to
  the repo's. Kept a copy at `checkpoints/lm_baseline_step4600.pt` so training runs can't clobber
  the official baseline.

### infra fixes (my branches only, documented here for the fleet)
- `fleet/scripts/ntfy.sh`: `read` was dead on every python3 — backslash escapes inside a
  single-quoted `python3 -c '…'` block → SyntaxError, bus read always returned nothing.
  Rewrote without escapes; verified live output. (pub always worked.)
- `neurobrain/scripts/retokenize.py` + `scripts/build_drive_corpus.py`: both accumulated every
  token id in one python list (53M+ ints ≈ 36 B each ≈ 2 GB) → guaranteed OOM on this box.
  Rewrote to stream uint16 chunks (1–2M tokens) straight to disk. Same output format, peak RSS
  240 MB for the 400k-episode drive build.

### corpus rebuild (bins are gitignored → lost on every rollback)
| stream | tokens |
|---|---|
| code_train / code_val | 53.44M / 1.80M |
| drive_train / drive_val | 69.68M / 1.78M |
| ui_train / ui_val | 17.03M / 0.52M |

`retokenize.py` defaults (seed 7, 160 MB code cap, vocab 2052 — tokenizer untouched, checkpoints
stay compatible). Drive: `build_drive_corpus.py --episodes 400000`.

### codebench v1 (deliverable 1) — LIVE
- **49 tasks** (spec allows 40–80): signature + docstring → body, 8 categories
  (arithmetic/strings/lists/dicts/logic/recursion/sorting/misc) × easy/medium/hard, every
  reference ≤ 6 lines, 2–5 hidden asserts each.
- **held out by file hash**: one JSON file per task under `neurobrain/data/codebench/tasks/`,
  sha256-pinned in `manifest.json`; `load_tasks` fails on any tampered file (tested). Plus a
  verbatim scan (normalized prompt+reference) over the corpus roots: **64,271 py files /
  472M chars → 0 collisions**.
- **sandboxed execution**: `python -I`, minimal env (`PATH`,`TMPDIR`), tempdir cwd, hard timeout
  (5 s default; timeout path tested with an infinite loop).
- **metrics**: `pass@1` (greedy top_k=1, and sampled T=0.8/top_k=40, seed 0),
  `syntax_valid_rate` (parses AND defines fn), `body_rate` (wrote any body at all), per-category
  and per-difficulty breakdowns, gen tok/s, peak RSS.
- **test-first**: 8 pytest tests green. They immediately caught a bug in my own bank
  (`repeat('ab',3)=='abab'` → `'ababab'`; the reference was right, the assert was wrong).
- code: `neurobrain/codebench.py`, `neurobrain/codebench_tasks.py`, `tests/test_codebench.py`
  (neurobrain repo, branch agent-04). Results mirrored here under `codebench/`.

### baseline numbers (official ckpt, step 4600)
| metric | greedy | sampled |
|---|---|---|
| pass@1 | **0.000** (0/49) | **0.000** (0/49) |
| syntax_valid_rate | 1.000 | 0.735 |
| body_rate | **0.000** | 0.388 |

- `eval_code` (no-docstring prompts): val_loss **2.2873** (ppl 9.85), syntax_rate 0.0 — matches
  the published lineage (2.09–2.31 depending on split).
- `eval_drive` (48 objectives): terminal_rate **0.000**, retry_after_failure **0.000**,
  honest_completion **0.000**. Expected: the release ckpt predates the drive mixture (its own
  summary only has code+ui evals).

### failure-mode diagnosis (the useful M0 finding)
Greedy decode after `def add(a, b):\n """return the sum of a and b"""\n` — top-8 next tokens:
`'\n' 6.35, '\n\n   ' 5.05, '\n   ' 4.43, 'def' 4.33, ')' 4.10, '<|fim_middle|>' 3.85`. The model emits a
blank line and starts a **new unrelated def** (`def _check_batch_batch…`); it never writes the
body. syntax_valid=1.0 is an artifact of the docstring alone being a legal body. Conclusion: raw
file-continuation training at 4.6k steps does not produce task→code behaviour; **pass@1 cannot
move off 0 without the format itself**. That makes deliverable 6 (instruction mix
`<|task|>write a function that …<|code|>`, ~20% of code tokens) the highest-leverage next
variable, and expert iteration will need candidates in the same format.

### in flight
- `checkpoints/run12k`: fresh 12k-step run, published recipe (b8×a3, ctx 256, lr 2e-3,
  warmup 150, cosine→0.1 floor), mixture 55/25/20 **including the drive stream for the first
  time in this lineage**. Targets M2 (≥12k steps, own checkpoint) and M3 (terminal_rate ≥ 0.5).
  `--time_budget 12600`, `--resume`-safe (saves every 200 steps), ~6.5k tok/s → ETA ≈ 3.2 h.

### next cycle (M1)
Corpus v2, one variable at a time: AST-parse filter, drop vendored/generated/fixture code,
function-level dedupe by hash, short-function packing, instruction-mix episodes (~20% of code
tokens) mined from docstrings; report bytes/token; evaluate instructed vs plain separately.
Beat baseline val loss, then re-score codebench. Everything logs to `runs.jsonl`.
