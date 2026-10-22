# agent 01 — runtime & integration: NOTES

## Cycle 1 — 2026-10-22 — M0: skeleton + doctor + bench + 20-token generate

### What landed (neurobrain repo, branch `agent-01`)

- `brainbox/` package: `cli.py` (all 8 verbs; `doctor`/`bench` real, rest
  print their milestone and exit 2 — nothing faked), `host.py` (`BrainHost`:
  boot/generate/score/health, one execution at a time behind a lock),
  `checkpoints.py` (spec dir layout, sha256 verify, legacy `.pt` load,
  migrate, stub writer), `governor.py` (RSS via /proc + getrusage peak;
  refuse >3800 MB, resume <3200 MB, `BRAINBOX_RAM_CAP_MB` override).
- `pyproject.toml`: `pip install -e .` gives a working `brainbox` console
  script (smoke-tested: `brainbox doctor` OK). Early M5 groundwork.
- `scripts/migrate_checkpoint.py`: legacy `lm_best.pt` → checkpoint dir, plus
  `--make-stub`. M2 tooling landed early because M0 needed the writer.
- `tests/test_brainbox_m0.py`: 11 unittest cases, written first (red → green):
  governor hysteresis, dir round-trip, weights/tokenizer sha tamper rejection,
  legacy migration, host generate-20 + score, CLI doctor/bench JSON, help
  lists all verbs, unimplemented exits 2. Run: `python3 -m unittest discover -s tests -v`
- `.gitignore`: `checkpoints/*/weights*.pt` (config + card merge, weights
  don't, per COORDINATOR.md's ~5 MB rule) and `.brainbox/`.
- `checkpoints/lm-stub/{config.json,card.md}` committed; regenerate weights
  with `python3 scripts/migrate_checkpoint.py --make-stub checkpoints/lm-stub`.

### The checkpoint problem (read this before quoting M0)

There is **no trained LM checkpoint anywhere in git** — `checkpoints/*.pt` is
gitignored, there are no GitHub releases, and `reports/` only proves training
reached step 4652 in the coordinator's sandbox. Per "never block, stub what
is missing", M0 benches a seeded stub: same GPTConfig as `train_lm.py`
(6L/7H/d224/ctx256, vocab 2052 from the real `data/tokenizer.json`),
4,247,264 params — identical count to `reports/lm_summary.json`. Every
surface flags it: `config.json` `"stub": true`, `card.md`, bench/doctor JSON,
this file. Sample output is the expected noise:
`"# quicksort\nvectorchoose().().}<|uteldld�que .."`. Timing/RSS transfer to
the trained model; sample quality does not. When `lm_best.pt` appears:
`scripts/migrate_checkpoint.py checkpoints/lm_best.pt --out checkpoints/lm`
then re-run bench — no code change needed (`find_checkpoint` prefers
non-stub, highest step).

### Measured (fresh processes; internal getrusage peak cross-checked with /usr/bin/time -v — identical to 0.1 MB)

- boot 0.996 s median (0.988–1.014), of which torch import ≈ 0.92 s.
- 20 tokens in 63 ms = 317 tok/s (short prompt; cost grows with ctx fill —
  M1 will bench at ctx 256).
- Peak RSS 272.1 MB bench / 223 MB doctor. Budget spec allocates 400 MB to
  python+torch alone; measured total with fp32 weights (17 MB) is 272 MB, so
  we have ~10× headroom to the 3.0 GB real-machine target before int8 (M7).

### Decisions other agents should know

- **`spec-change` (published on bus before editing):** `specs/model_io.md`
  `config.json` += `weights_sha256`, `stub`, `params`. Loaders must surface
  `stub`.
- `/generate` "text" = prompt+continuation (matches `neurobrain.sample.complete`);
  host also returns `completion` (continuation only) as an extra field.
- `/score` `tokens` are decoded token strings; `token_ids` added as an extra
  field so nobody has to re-encode. If another agent needs ids *in* `tokens`,
  say so on the bus before M1 freezes the API.
- Prompts longer than ctx are left-truncated by the model's generate (last
  256 tokens); host does not pre-chunk. Flagged for M1 request validation.
- Checkpoint search order: `$BRAINBOX_CHECKPOINT` → `./checkpoints/*/`
  (non-stub, highest step first) → repo `checkpoints/` → `~/.brainbox/checkpoints/`
  → legacy `*.pt` → in-memory stub.

### Reproduce M0

```bash
git clone https://github.com/dreamer2664/neurobrain.git && cd neurobrain
git checkout agent-01
python3 -m unittest discover -s tests -v        # 11 tests, ~1 s
python3 -m brainbox doctor
python3 scripts/migrate_checkpoint.py --make-stub checkpoints/lm-stub
python3 -m brainbox bench --checkpoint checkpoints/lm-stub --tokens 20
```

## Cycle 2 — 2026-10-22 — M0 re-run on the real checkpoint

Coordinator published release `ckpt-1022` mid-cycle-1. Downloaded
`lm_best.pt` / `grip_best.pt` / `tokenizer.json`; **all three sha256 match the
GitHub release digests** (`0df9f2f6…`, `b449721d…`, `198316df…`), and the
release tokenizer is byte-identical to `data/tokenizer.json`.
`lm_best.pt` = step 4600, `best_val 1.4255` — exactly the eval line in
`reports/lm_log.jsonl`. Migrated with the M2 script to `checkpoints/lm/`
(config + card committed on `agent-01`; weights gitignored, rebuild command
in STATUS). GripNet: step 750, keys `{model, step, eval}` — config comes from
GripNet defaults (char_vocab 40, max_len 48, d 64, grid 32), noted for M1.

Re-benchmark (3 fresh processes, `artifacts/bench_m0_real.json`): boot
1.003 s, 20 tokens in 64 ms (312 tok/s), peak RSS 272.1 MB internal ==
external. Stub medians were 0.996 s / 317 tok/s / 272.1 MB — i.e. the stub
predicted real timing/RSS to within noise, as designed. Evidence the weights
are trained: real model's top next-token logprob after `"import "` is −1.72
and its 80-token continuation is word-shaped Python commentary; the stub sits
at −6.56 (≈ uniform over 2052 tokens) producing replacement-char noise.
Sample (real, 20 tok): `"# quicksort\nfrom numba.core.core.mypy.core.validation import (\n"`.

**M0 is now met literally**: skeleton + doctor + bench + 20 tokens from the
real checkpoint, boot time and RSS published.

### Next cycle: M1

HTTP API on 127.0.0.1 (`/generate`, `/score`, `/ground` stubbed until a grip
checkpoint exists, `/health` <50 ms), request queue in front of `BrainHost`,
429 from the governor, 200-sequential-request leak test (>20 MB growth fails).
Tests first, same ritual.

## Cycle 3 — 2026-10-22 — M1: local API + 200-request leak test

Fast-forwarded `agent-01` onto merged main first (deskhands, e2e_demo,
restore_data.sh are in-tree now). `spec-change` published before editing:
default API port 8321 (none was defined anywhere).

### What landed

- `brainbox/server.py` — stdlib `ThreadingHTTPServer`, hard-bound 127.0.0.1.
  One worker thread drains a job queue (peak model concurrency asserted == 1
  in tests under 8-way parallel load); `/health` bypasses the queue. Wire
  responses are spec-exact: `/generate {text,tokens,ms}`, `/score
  {tokens,logprobs}` (token strings; `token_ids` stayed host-internal —
  say so on the bus if you need ids on the wire, agent 04), `/ground
  {x,y,action}` in the *submitted image's* pixels, `/health {ok,rss_mb,step}`.
  Errors: 400 bad json/fields/base64, 404, 405, 413 (>12 MB body / >8 MB
  image), 429 governor (with `reason`), 503 missing grip checkpoint, 504 job
  timeout 120 s. `/generate` also accepts optional temperature/top_k/seed.
- `brainbox/grip.py` — real GripNet hosting. Preprocessing copied from
  training (`ui_world.encode_task`, /127.5−1, BILINEAR→128²), `click_xy`
  scaled back to input pixels. Loads legacy `grip_best.pt` (step 750) now,
  checkpoint dirs in M2. Defensively `model.eval()` per call (see below).
- `brainbox serve [--port 8321] [--checkpoint] [--grip-checkpoint]
  [--ram-cap-mb]`; boots LM + grip eagerly, grip failure degrades to
  `/ground` 503 instead of killing the server.
- `scripts/api_stress.py` — M1 acceptance harness (fresh server subprocess,
  real checkpoints; mix generate×100/score×50/ground×50, /health prober
  thread, RSS from both `/health` and `/proc/<pid>/status` incl. VmHWM).
- Tests: `tests/test_brainbox_m1.py` (10 tests; tiny stub LM + random GripNet
  injected — wire contract under test, not weights). 21/21 overall
  (`artifacts/tests_m1.txt`).

### Measured (`artifacts/api_m1_stress.json`)

| metric | value | bound |
|---|---|---|
| RSS growth over 200 seq. requests | **+0.3 MB** (/proc), +0 MB (/health) | ≤ 20 MB |
| /health during load (n=208) | p50 1.2 ms, p95 2.1 ms, max 9.1 ms | < 50 ms |
| /generate 16 tok (n=100) | p50 97 ms | — |
| /score (n=50) | p50 5.0 ms | — |
| /ground (n=50 unique screens) | p50 15.0 ms, hit 0.40 | — |
| server peak RSS (VmHWM) | 299.5 MB (LM+grip resident) | < 1600 MB |

### Grounding parity (a false alarm, documented so nobody repeats it)

First stress reported hit 0.20 vs the lab's ~0.48–0.52. Two artifacts of my
own harness, not the API: (1) `grounds[i % 10]` with ground slots at
`i % 4 == 3` only ever requested 5 of 10 screens — and only 1 of those 5 is
a hit for this checkpoint; (2) in my follow-up diagnostic,
`train_grip.evaluate()` helpfully leaves the model in `train()` mode, so
BatchNorm ran on single-image batch stats. Clean check
(`artifacts/api_m1_ground_parity.json`): reference `evaluate` 0.523 (n=256,
seed 0) vs PNG-round-trip API path **0.531** (n=256, seed 1234). The /ground
path is faithful. Stress now uses 50 unique screens (hit 0.40 at n=50 — same
checkpoint, sampling noise; use the n=256 number for comparisons, agent 03).

### Next cycle: M2

Checkpoint directories for both current `.pt` files (LM done in M0; grip dir
+ `doctor` reporting both + migration manifest). Then M4 undo (drive loop
needs trash before it deletes anything), then M3.
