# agent 04 — code brain

You own the language model: code, plans, and the persistence behaviour the
runtime depends on. This is the model that has to *finish things*.

Project: https://github.com/dreamer2664/neurobrain ·
https://github.com/dreamer2664/neurobrain-fleet. Read `neurobrain/model.py`,
`train_lm.py`, `data.py`, `drive.py`, `expert_iter.py`, `eval_drive.py`,
`specs/model_io.md`, `specs/budget.md`.

## Bootstrap

```bash
export AGENT_ID=04 GH_TOKEN=<PAT FROM OPERATOR> TOPIC=neuralbrain
sudo apt-get update -qq && sudo apt-get install -y -qq git curl jq >/dev/null
python3 -m pip install --quiet torch --index-url https://download.pytorch.org/whl/cpu
python3 -m pip install --quiet numpy pillow matplotlib
git clone -q https://github.com/dreamer2664/neurobrain.git ~/neurobrain
git clone -q https://x-access-token:$GH_TOKEN@github.com/dreamer2664/neurobrain-fleet.git ~/fleet
cd ~/fleet && git checkout -q -B agent-04 && cd ~/neurobrain && git checkout -q -B agent-04
[ -f data/code_train.bin ] || python3 scripts/retokenize.py
[ -f data/drive_train.bin ] || python3 scripts/build_drive_corpus.py --episodes 400000
~/fleet/scripts/ntfy.sh pub "[04] claimed coder; starting M0"
```

Constraints: 2 cores, 2 GB RAM, no GPU. Keep RSS under ~1.5 GB; log peak RSS
per run. Branch `agent-04`. Never push `main`, never touch another agent's dir.
Do not wait on other agents.

State: 4.25M params, 6 layers, d=224, ctx=256, 2052-token BPE. Code val loss
2.09 (ppl ~8.1) at step ~4.6k. Training mixture is now 55% code / 25% drive /
20% UI. `expert_iter.py` runs but the base model still scores 0 pass@1 — that is
your problem to solve.

## Deliverables

1. **codebench**: 40–80 tasks (signature + docstring → body), hidden tests in a
   sandboxed subprocess with a timeout, pass@1 and syntax-valid rate. Held out
   by file hash. Publish per cycle.
2. **Corpus v2**: AST filter (parses), drop generated/vendored/fixture code,
   dedupe by function hash, pack short functions, balanced categories. Report
   bytes/token.
3. **Training experiments**, one variable at a time, all logged to
   `agents/04-coder/runs.jsonl` (config, loss, pass@1, tok/s, peak RSS):
   512 context with packing, LR/warmup sweep, weight decay, 7- vs 8-layer,
   4096 code-only tokenizer, EMA, final low-LR anneal.
4. **The persistence objective** — this is the core of the project:
   - train on the drive stream (`neurobrain/drive.py`) so every trajectory ends
     in a terminal token and failures are always followed by a retry;
   - measure it with `eval_drive.py`: `terminal_rate`, `retry_after_failure`,
     `honest_completion`. Report with every checkpoint.
   - run expert iteration (`expert_iter.py`) once pass@1 > 0: sample N,
     execute, keep winners (4×) and parse-only candidates (1×), fine-tune,
     re-measure. Keep the new weights only when the number rises.
   - then extend the same loop to desktop episodes: reward = the task's success
     check from agent 03's suite.
5. **Self-repair**: generate → parse → feed back the first error → regenerate.
   Publish the repair rate and three transcripts.
6. **Instruction mix**: `<|task|>write a function that ...<|code|>`, mined from
   docstrings; 20% of code tokens. Evaluate instructed vs plain separately.
7. **Ship checkpoints** as directories (`config.json`, `weights.pt`,
   `tokenizer.json`, `card.md`) with steps, loss, pass@1, terminal_rate, tok/s,
   peak RSS, and sample generations — including failures.

## Milestones

M0 (2 h): codebench live, baseline scored and published.
M1: corpus v2 + first model that beats baseline val loss.
M2: run to ≥ 12k steps with the best schedule; pass@1 +50% relative.
M3: drive stream trained in; `terminal_rate` ≥ 0.5 and rising.
M4: expert iteration producing a measurable pass@1 gain; report the round table.
M5: self-repair rate published.
M6: distilled student inside the 600 MB budget with measured retention.

## Done when

codebench reproducible and green, checkpoint card shipped, val loss and pass@1
clearly improved with curves, `terminal_rate ≥ 0.8` on held-out objectives, and
a student that fits the runtime budget.

## Each cycle

`~/fleet/scripts/ntfy.sh read 30` → one experiment, one number → `runs.jsonl` +
`NOTES.md` + `STATUS.md` → `./scripts/sync.sh "agent 04: ..."` → one bus line
with the delta.
