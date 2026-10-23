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

## 2026-10-22 · cycle 2 (M1 in progress): corpus v2 builder green, full build + 12k run in flight

### environment hazard logged for the fleet: string mangling in edit channels
While patching files via shell heredocs I observed (byte-proven with od): typed
special-token literals can arrive on disk altered (a typed doc-separator token landed as a
fim-style token; typed double-backslash-n collapsed to a real newline), and grep/cat output can
display different bytes than od shows. Symptom: "impossible" ValueErrors where a list visibly
contains the searched string. Policy adopted: never type special-token literals or backslash
escapes in patches — derive from `tok.specials` / build by concatenation / `chr(10)`; verify
writes with ord-scans, not eyeballed greps; gate every commit on `ast.parse` + pytest.
Files fixed after audit: `neurobrain/codebench.py` (STOP_MARKERS), `tests/test_codebench.py`
(extract test), `neurobrain/corpus_v2.py`, `tests/test_corpus_v2.py`. All 10/10 tests green,
committed `aaa1b28`, `d03e466`.

### corpus v2 (deliverables 2 + 6) — code green
`neurobrain/corpus_v2.py` (+ `tests/test_corpus_v2.py`, hermetic synthetic corpus):
- AST-parse filter; drops generated (AUTO-GENERATED/DO-NOT-EDIT markers), vendored/fixture dirs,
  minified-like files (>30% of lines >160 chars)
- function/class-level units (80..6000 B), dedupe by normalized-source sha1 AND AST-dump sha1
- **unconditional codebench holdout**: task prompt+reference normalized-sha1 checked BEFORE size
  filter; v1 mechanism (sha256 manifest pins) still applies at file level
- category tagging (io/net/text/numeric/data/os_sys/time_date/concurrency/runtime/misc) with
  per-category cap (balance)
- short-unit packing separated by the `<|code|>` special (there is no fim token in this vocab)
- instruction episodes: `<|task|>write a function that <doc-summary><|code|>` + unit source,
  budgeted to 20% of code tokens; val split keeps plain vs instructed streams separate
  (`code_val_v2_plain.bin` / `code_val_v2_instr.bin`) so deliverable-6 evals can be reported apart
- streamed uint16 writes (flat RSS), full report json

Smoke on the real corpus (3000 units, nice 19, concurrent with training): 382 files walked,
353 parsed (92.4%), **instr_share_est 0.1995** (target 0.20), **2.42 bytes/token** (v1: 2.90),
1.54M train tokens in 55 s. Full build (150k units, cap 12k/cat) launched right after.

### train_lm.py
Added optional stream-path overrides (`--code-train`, `--code-val`, `--drive-*`, `--ui-*`) so a
v2 run doesn't require touching the live default bins. Defaults unchanged; running process
unaffected.

### run12k (M2/M3 candidate) — in flight
Step 1700/12000 @ ~5.3k tok/s (2 cores shared with bench work); eval@1600: code 3.40,
drive 0.162, ui 0.70. RSS ~990 MB (mostly reclaimable mmap of the token streams; anon ~400 MB).
Budget stop at 12600 s ≈ step 10.9k → one `--resume` leg to reach 12k. On completion:
score codebench + eval_drive + eval_code, publish round 1 table.

### next
- when v2 build lands: report tokens/categories/bytes-per-token, then v2 training run
  (one variable: corpus) vs run12k baseline recipe
- self-repair loop (deliverable 5) + checkpoint packer (deliverable 7) while GPUs... err, CPUs spin

## 2026-10-22 · cycle 3 (M1): corpus v2 built; baseline controls on v2 streams; card shipped

### corpus v2 — FULL BUILD (report: corpus_v2_report.json here + neurobrain/reports/)
54,867 files walked → 48,362 parsed (88.1%): dropped 5,211 size, 434 generated-marker,
860 vendored/fixture; minified-like 0 at real-corpus scale. Units: 19,633 size-dropped,
**83,589 dup_source + 105 dup_ast deduped (~49% duplication rate in stdlib+site-packages!)**,
holdout collisions 0 (mechanism proven on the synthetic bench file in tests).
86,398 units kept → **50,124 after category balance** (cap 12k/cat; data, io, runtime at cap;
text 5,491 · os_sys 3,153 · numeric 2,764 · net 1,842 · concurrency 466 · time_date 402 · misc 6).
Streams: **code_train_v2 22.72M tok · code_val_v2_plain 569k · code_val_v2_instr 379k**,
instr share **0.1993** (target 0.20), **2.37 bytes/token** (v1: 2.90). Build: 40 min wall,
peak RSS 305 MB (streamed writes).

### scheduling lesson (logged for the fleet)
nice 19 against two nice-0 training threads gets ~1% CPU under CFS (build crawled: 2 min CPU in
38 min wall). Also: 4 concurrent heavy jobs on 2 cores/2 GB pushed available memory to 200 MB —
killed the extras, and switched to SEQUENTIAL heavy jobs: paused training (clean stop after the
step-3600 eval+save; optimizer state verified in lm_latest.pt), ran the build at nice 0, resumed
training after. Rule adopted: one heavy job at a time; light eval jobs nice 10 alongside.

### baseline controls for the v2 experiment (same bins the v2 run will be judged on)
eval_streams on lm_baseline_step4600 (reports/streams_baseline.json):
code_val(v1) 2.2448 · **code_val_v2_plain 2.4326 · code_val_v2_instr 2.5074** ·
drive_val 5.8343 (never saw drive) · ui_val 2.0120 (my rebuilt ui bins differ from the
original run's — their summary said 0.76; internal comparisons on identical bins remain valid).

### checkpoint card (deliverable 7) — first one shipped
checkpoints/lm-baseline-step4600/ (mirrored here: card.md + config.json; weights stay in the
coordinator's release ckpt-1022 to avoid double-hosting 17 MB): config.json carries
tokenizer_sha256 198316df… and **weights_sha256 ae7599cf…** (agent-01's spec change),
source_ckpt_sha256 0df9f2f6… = release download, 2 sample generations included (failures kept).

### run12k — resumed
Resumed from step 3600 (code 2.8159 / drive 0.1490 / ui 0.6855 at that eval) with optimizer
state; single budget leg to 12k (time_budget 11400 s, ETA ~00:45 UTC). Code-eval trajectory so
far: 4.78@200 → 3.40@1600 → 3.15@2000 → 2.96@2800 → 2.82@3600.

### next
self-repair baseline (running, nice 10) → publish M5 baseline row; when run12k lands: score
codebench + eval_drive + streams + self-repair on it, pack card WITH weights here, publish the
round table; then launch the v2 training run (one variable: corpus v2 + instruction mix;
--code-val stays on the v1 val bin for comparability, v2 streams evaluated via eval_streams).

### addendum (cycle 3b): self-repair baseline + KV cache + push
- **self-repair baseline (M5 row)**: repair_rate **0.000** (0/49 repaired), final_pass 0.000,
  1545 s, peak 267 MB, reports/self_repair_baseline.json (3 transcripts + all rows). Attempt-1
  modes: 26 AssertionError (valid syntax, wrong logic), 13 syntax, ~10 timeout/NameError.
  Attempt-2 is WORSE (33+ syntax fails): the <|try|>2 repair protocol is OOD for a model never
  trained on drive — exactly what run12k's 25% drive mix should fix. Transcript cb-arith-01:
  attempt-1 = "__rgba__ = _operator(a, b)" → UI-marker cross-contamination + hallucinated helper.
- **KV cache in model.generate (60603e6)**: cacheless generate re-ran the full 256-ctx forward
  per token (~2.2 GFLOP/step) — the 51-min self-repair run was ~2 h projected. Added
  forward_cached (per-block (k,v), RoPE at absolute offsets, bottom-right tril mask on decode),
  sliding-window fallback beyond ctx, 4 token-exact parity tests (top_k=1 same seed vs old path;
  21/21 green). Real-model bench: 3.1x on 32 tok under contention; self-repair CPU/task 38→8.8 s.
  Remaining cost is Python/op overhead per decode step, not FLOPs.
- **neurobrain agent-04 pushed through df9c9d9** (6 commits incl. corpus v2 builder, self-repair,
  packer, EI-on-codebench adapter, KV cache, reports). Note: `oauth2:` URL form works for push;
  `x-access-token:` intermittently 401s on write (reads fine).
- Training at step ~6.5k/12k during the above; budget stop ~00:45Z (may need one short final
  resume leg if it lands just under 12k).

## 2026-10-23 · cycle 4 (M2/M3/M5): run12k complete + full battery + card shipped WITH weights

### run12k training (M2 schedule leg)
12,000 steps exactly (budget-stopped at 11,922 + 78-step final resume leg, clean exits, cosine
to 2.0e-4 floor). 73.7M tokens seen (22.7M code x ~1.8 epochs would be v2; this run = v1 code
53.4M bin at 55% mix ~ 0.75 epoch). Peak RSS 1124 MB (leg 2: 951 MB). 5.3-5.9k tok/s solo.
lm_best == final step (best_val 1.04050 = eval_mean at 12000).

### ROUND TABLE (same bins, same protocol, battery 6/6 rc=0)
| metric | baseline step4600 | run12k step12000 | delta |
|---|---|---|---|
| eval_code val_loss (v1 code_val) | 2.2873 | **2.0790** (ppl 8.0) | **-9.1%** |
| streams code_val | 2.2448 | **2.0412** | -9.1% |
| streams code_val_v2_plain | 2.4326 | **2.1924** | -9.9% |
| streams code_val_v2_instr | 2.5074 | **2.2379** | -10.7% |
| streams drive_val | 5.8343 | **0.1120** | 52x better |
| streams ui_val | 2.0120 | **0.6737** | 3.0x better |
| eval_drive terminal_rate | 0.0 | **1.0** | M3 MET (>=0.5 rising; done-criterion >=0.8 too) |
| eval_drive retry_after_failure | 0.0 | **1.0** | n=48 held-out episodes, mean_steps 2.7 |
| eval_drive honest_completion | 0.0 | **1.0** | |
| codebench pass@1 greedy/sampled | 0.000/0.000 | 0.000/0.000 | M2 pass@1 goal NOT met; EI stays gated |
| codebench body_rate greedy/sampled | 0.000/0.388 | **0.653/0.735** | the real sub-pass@1 signal |
| codebench parses greedy/sampled | -/- | 0.531/0.653 | |
| self-repair rate | 0.000 | **0.0408** | first repairs (M5) |

Interpretation notes:
- Baseline "syntax_valid 1.000 greedy" was VACUOUS: empty completions still exec the prompt's
  def line, so parses+defines held trivially. body_rate is the honest metric; on it run12k went
  0.000 -> 0.653 greedy. The apparent syntax-rate "drop" (1.000 -> 0.531) is that artifact ending.
- **val_loss 2.0790 beats the published lineage's 2.09-2.12** on comparable measurement, and
  beats the baseline ckpt by 9.1% on identical bins -> M1's "beat baseline val loss" is MET by
  run12k already; the v2-corpus run (one variable: corpus) now has to beat run12k.
- M3 is MET with margin: every one of 48 held-out drive episodes terminates in the terminal
  marker, retries after failure, and completes honestly (mean 2.7 steps).

### self-repair receipts (deliverable 5: rate + transcripts)
rate 0.0408 = 2/49 repaired (first_pass 0). Both are genuine one-shot repairs after error
feedback (attempt 1 failed AssertionError, attempt 2 passes):
1. cb-dict-02 keys_positive(d): attempt 2 returned the list comprehension over d with d[k] > 0.
2. cb-misc-06 summarize(items): attempt 2 returned the ok/n dict built from len(items).
3. (failure transcript kept in the report) cb-arith family: attempt 2 stayed syntactically
   broken - full transcripts incl. failures: reports/self_repair_run12k.json (all_rows).
Baseline comparison: repair context was OOD for the no-drive baseline (attempt-2 degraded);
with 25% drive mix the protocol is in-distribution and repair starts working.

### card shipped (deliverable 7) - WITH weights this time
checkpoints/lm-run12k/ here = card.md + config.json (weights_sha256, tokenizer_sha256,
source sha 7f0a17fc..., steps/losses) + tokenizer.json + weights.pt (17 MB). Sample
generations incl. failures embedded in card.md. neurobrain repo: checkpoints/run12k/.

### infra that made this cycle fast
KV-cached generate (60603e6, token-exact parity, 21/21 tests) + idle-box battery: codebench
428 tok/s (30 s stage), streams 6 s, self-repair 22.5 s (vs 1545 s under contention).
score_battery.sh smoke-validated 6/6 rc=0 on baseline before the real run (numbers matched
published reports exactly - deterministic evals).

### next
v2-corpus run launching now (scripts/run_v2.sh: ONE variable = code corpus v1->v2 w/ 20%
instruction mix; v1 code_val kept for lineage-comparable selection; 12k steps; budget 10800s
+ final leg if needed). Then: M1 comparison vs run12k (val + v2 streams + instructed-vs-plain),
battery + card, and the experiment queue (low-LR anneal, 7-vs-8 layer, EMA, LR/warmup, wd,
4096 code tokenizer, 512-ctx packing). EI (M4) runs the moment pass@1 > 0; v2's instruction
mix is the designed lever (baseline greedy emits no body; instructed format teaches
task->code completion).

## 2026-10-23 · cycle 5 (M1): corpus-v2 run complete + instructed eval mode + harness v1.1

### runv2 training (ONE variable vs run12k: code corpus v1 -> v2)
12,000 steps (budget stop 9297 + 2703-step resume leg, both exit 0), same recipe
(batch8 accum3 ctx256 lr2e-3 warmup150 cosine->2e-4, mix 55/25/20, drive/ui bins unchanged v1).
Code tokens: 22.72M v2 bin = ~1.77 epochs (run12k: 53.4M v1 = ~0.75). Peak RSS 1079 MB.
lm_best == step 12000 (best_val 1.0735).

### ROUND TABLE v1.1-harness (all three ckpts re-scored identically; reports here + neurobrain)
| metric | baseline 4.6k | run12k (v1) 12k | runv2 (v2) 12k |
|---|---|---|---|
| streams code_val (v1) | 2.2448 | **2.0412** | 2.2246 |
| streams code_val_v2_plain | 2.4326 | 2.1924 | **2.0671** |
| streams code_val_v2_instr | 2.5074 | 2.2379 | **1.8582** |
| streams drive_val / ui_val | 5.8343 / 2.0120 | 0.1120 / 0.6737 | 0.1127 / 0.6736 |
| eval_code val_loss | 2.2873 | **2.0790** | 2.2149 |
| eval_drive terminal/retry/honest | 0/0/0 | **1.0/1.0/1.0** | **1.0/1.0/1.0** (mean_steps 2.5) |
| codebench pass@1 greedy/sampled | 0/0 | 0/0 | 0/0 |
| body_rate greedy/sampled | 0.000/0.388 | 0.653/0.735 | **1.000**/0.796 |
| syntax+defines greedy/sampled | 1.000*/0.735 | **0.531/0.653** | 0.000/0.204 |
| self-repair rate | 0.000 | **0.0408** | 0.000 |
* vacuous (empty completions still define fn via prompt) - body_rate is the honest metric.

### honest reading
- **M1 on the v2 distribution: decisive.** v2 plain -15.0% and instructed -25.9% vs baseline
  controls; vs run12k: plain -5.7%, **instructed -17.0%** - the 20% instruction mix works
  exactly as designed on its own eval stream (deliverable 6: instructed and plain evaluated
  separately, both val-stream level and bench prompt-mode level).
- **On v1 file-level val + continuation-style bench: runv2 regresses vs run12k**
  (2.2246 vs 2.0412; greedy syntax 0/49 vs 26/49). Diagnosis from transcripts:
  (a) greedy decode = repetition collapse (name-token loops, e.g. def X_X_X_...);
  (b) sampled emits def scaffolding (docstrings, type hints, numpydoc sections!) but
  semantically incoherent and often truncated - the model tries to write WHOLE units
  (its training format) incl. its own docstring, eating the token budget;
  (c) function-unit distribution != continuation-prompt distribution (v1 files and
  codebench prompts are header-then-body).
- Primary checkpoint stays **run12k** for v1-comparable numbers; runv2 wins for
  instructed/unit-style generation. Both cards shipped WITH weights (checkpoints/
  lm-run12k, lm-runv2 here; source shas in config.json).
- pass@1 0.000 across the board at 4.25M params / <=24M-token code corpora: capability
  wall, not harness. EI (M4) remains gated on pass@1 > 0.

### harness v1.1 (committed, pushed b2abfa9)
- extract_completion now takes text after the LAST code-sep marker (corpus-v2 models
  announce code with the separator; v1 models unaffected - run12k scores identical).
- codebench score --prompt-mode plain|instructed: instructed replicates the corpus-v2
  template (task marker + 'write a function that ' + one-line docstring summary +
  code-sep + LF); whole-def candidates exec standalone, body-glue fallback otherwise.
  Probes: instructed@128tok 0/6, instructed@220tok 0/6 (truncation was NOT the main
  blocker - incoherence is). 23/23 tests green; bench field bumped codebench-v1.1.

### next (cycle 6): decoding + anneal levers for pass@1
1. repetition penalty option in generate (default 1.0 = bit-identical, parity-tested) ->
   re-score sampled with 1.15/1.3; repetition collapse is the biggest sampled-syntax killer.
2. E1 low-LR anneal (deliverable 3): resume run12k best, lr 2e-4 -> 0 over ~1.2k steps;
   re-battery. Cheapest real shot at sharper decoding + lower val.
3. queue after: LR/warmup sweep, wd sweep (needs --wd flag; currently hardcoded 0.1),
   7-vs-8 layer, EMA (needs trainer support), 512-ctx packing, 4096 code-only tokenizer.
4. when agent-05's push lands: consume drive v4.1 (318M tok) + hard_ui v5 corpora as a
   separate one-variable experiment (their rebuild changes drive/ui hashes).
