# agent 05 — data forge · NOTES

## M0 — `dataforge` skeleton, stats + verify on the existing corpora ✅

**Shipped** (`neurobrain` branch `agent-05`, package `dataforge/`):

```
python -m dataforge build  --out DIR --profile {smoke,standard,max} [--seed N] [--datasets a,b]
python -m dataforge stats  --dir DIR [--json PATH]
python -m dataforge verify --dir DIR
python -m dataforge diff   --a DIR --b DIR     # determinism proof
python -m dataforge link   --dir DIR --to data # legacy flat layout for agents 04/01
```

17 tests in `tests/test_dataforge.py`, written before the code:
build → manifest → dtype/shape per `specs/data_formats.md`, verify catches a
flipped byte and a missing terminal token, stats fails on a broken drive
corpus, same seed ⇒ same hashes, different seed ⇒ different hashes, and the
numpy token scan agrees with the text classifier on every episode.

### The numbers (profile `standard`, seed 23, all on 2 cores / 2 GB)

| dataset | n | tokens | dup exact | balance | ranges |
|---|---|---|---|---|---|
| code | 3,558 docs | 14.22M | 0.00% | alpha/digit/space .38/.05/.33 | OK |
| drive | 1,000,000 episodes | 213.23M | 0.03% | alpha/digit/space .48/.05/.22 | OK |
| ui_protocol | 150,000 docs | 17.15M | 0.00% | alpha/digit/space .24/.26/.02 | OK |
| ui_seed | 25,000 imgs (5 shards × 5k) | — | 0.00% / near 0.15% | label H/Hmax 1.000, min share 3.93% (uniform 4.17%) | OK |

- **drive invariants** `terminal_rate=1.000 retry_after_failure=1.000
  failure_frac=1.000 retry/ep=1.47 mix ui/code/plan 0.45/0.40/0.15` — the brief's
  45/40/15 mix and all three invariants hold, checked from the bytes.
- **coordinate** heat argmax H/Hmax 0.93, max cell 4.6%, cells 72/1024,
  offset |m| 0.58, **clipped 52.1%**
- **entropy** 2.27 ± 0.19 bits (2000 images), black share 0.0%
- build 238 s including stats, **peak RSS 1133 MB** (build alone 660 MB,
  verify 776 MB); disk 479 MB for 244.6M tokens. Under the 1.6 GB line.
- **determinism**: two independent `standard` builds ⇒ **11/11 shards identical
  sha256** (`dataforge diff`, 211 s, 660 MB). Proof file:
  `artifacts/determinism.json`.

### Findings this cycle (the reason `stats` exists)

1. **The seed drive generators were 32.28% exact duplicates.** `rng.randint(1, 3)`
   for the attempt count meant a third of code episodes were a single passing
   attempt — the same text for the same one of 10 functions. At 1M episodes
   that is a corpus of a thousand sentences repeated a thousand times, which
   teaches memorisation, not persistence. Fixed in `neurobrain/drive.py`:
   - every code episode now fails **at least once** (`attempts >= 2`), so I3 is
     structural, not lucky;
   - test arguments are drawn per episode and the expected value is computed by
     **executing the reference body**, so a randomised assertion can never lie
     (`assert biggest([48, 78, 61, 81]) == 81`);
   - objectives/obstacles/obs lines carry random files, pids, paths, counts.
   Result: **32.28% → 0.03%** duplicates, invariant numbers unchanged.
2. **The seed world's offset targets saturate.** `target_offset` divides the
   sub-cell error by 0.45, so **51.6% of samples clip to ±1.0**. Any model
   trained on it learns a saturating regressor. The hard world (M1) maps the
   cell edge to ±1.0 instead. → heads-up to agent 03.
3. **The seed world only ever uses 72 of 1024 heat cells** (widgets are placed
   on a 4×3 grid) and 2.27 bits of entropy (flat fills). Grounding on it is a
   search over 7% of the space — cheap, and exactly what the hard world must
   destroy.
4. `ui_protocol` text is 76% non-alpha (brackets, digits, `{label}`), so the
   `alpha_share` gate does not apply to serialized element trees.

### Threshold table (all in `dataforge/checks.py`)

Hard gates, no override, every dataset: `dup ≤ 2%`, drive `terminal_rate = 1.0`,
`retry_after_failure = 1.0`, `failure_fraction ≥ 0.5`.
Per-dataset relaxations are printed by `stats` as `relaxed bounds` and are
**facts about the seed artefact that the hard world must beat**:
`ui_seed` runs with heat cells ≥ 60, offset clip ≤ 60%, entropy ≥ 2.0 bits;
`ui_protocol` alpha ≥ 0.15; `drive` vocab ≥ 380.

### Additive format change (spec-compatible)

UI shards carry the five specced arrays unchanged plus three extras that stats
needs: `labels` (24-class widget label), `roles` (7), `themes` (2), all int64
`[N]`. Consumers that only read the specced keys are unaffected.

## M1 — hard world v1 ✅ (10k samples + manifest, verified)

`neurobrain/ui_world_hard.py` + `dataforge` dataset `hard_ui`. Same 24 labels /
7 roles / 128×128 / 48-char instruction / 4 action classes as the seed world,
so a checkpoint trained on one reads the other. What is different:

| property | seed world | hard world |
|---|---|---|
| text | 6-bit glyph chips | real DejaVu 5.2–7.8 px, 2× supersampled, LANCZOS down |
| chrome | one title bar | title, menu bar, toolbar, tab strip, sidebar, list headers, status bar |
| layouts | 4×3 grid | list view / settings grid / form, sidebar + content bands |
| dialogs | none | modal with veil, title, message, 2–3 buttons (up to 55% of samples) |
| states | — | disabled, focused, selected, hover |
| themes | light, dark | light, dark, high-contrast (26%) |
| degradation | none | JPEG 40–85 quality or ±5..14 noise, optional blur |
| DPI | — | 100/125/150/200% (scales chrome: fewer, bigger widgets) |
| tiers | — | 0/1/2 = 20/45/35%, recorded per sample in `tiers/*.npy` |
| **heat cells used** | **72 / 1024** | **661 / 1024** |
| **offset clipped** | **51.6%** | **1.4%** |
| **image entropy** | **2.27 bits** | **5.56 ± 0.74 bits** |
| dup exact / near | 0.00 / 0.15% | 0.00 / 0.00% |

8 tiles: `artifacts/tiles-hard.png` (green cross = heatmap argmax + offset,
i.e. exactly what a model reads from the shard; label line = tier, dpi,
section, theme, action, instruction).

Built with `--set hard_ui.samples=10000` on the smoke profile, seed 23:
**99 s, 702 MB peak RSS, 181 MB on disk, verify OK, determinism 2/2 shards
identical.** Action mix click/type/toggle/drag = 74/9/10/7%, themes
37/37/26%, label H/Hmax 1.000 over 24 classes.

Two failures the gates caught while building it, both fixed in the generator
rather than the gate:
1. `drag` was 1.4% of samples (sliders were rare) → a guaranteed slider in
   ~72% of layouts and a toolbar search field in 55% → drag 7.0%, type 8.6%.
2. `offset_mean_abs` was 0.497 and the old upper bound was 0.45 → the bound was
   wrong, not the data: target centres are uniform inside a cell, so mean
   |offset| is 0.5 by construction. The gate is now two-sided (0.30–0.60):
   near 1.0 means a saturating regressor target, near 0 means every target sits
   on a cell centre. Both are broken; 0.5 is healthy.

M2 extends this to 100k (≈16 min at 10 ms/sample) with tiers verified.

## M2 — 100k hard-UI samples ✅

`--set hard_ui.samples=100000`, seed 23: **20 shards × 5k, 1.8 GB on disk,
980 s (16 min), peak RSS 480 MB, verify OK (20/20 sha256).**

| number | value |
|---|---|
| heat cells used | **755 / 1024** (10k: 661, seed world: 72) |
| offset |mean abs| | 0.50, clipped **1.5%** |
| image entropy | 5.54 ± 0.75 bits |
| label balance | H/Hmax 1.000 over 24 classes, min share 4.06% (uniform 4.17%) |
| action mix | click 74.2 / type 8.5 / toggle 10.4 / **drag 6.9%** |
| themes | light 37 / dark 37 / contrast 27% |
| tiers | 0: 19.7k, 1: 45.0k, 2: 35.3k |
| duplicates | exact 0.00%, near 0.05% |

Artifacts: `artifacts/stats-hard-100k.json`.

## M3 — 1M instructions with a dedupe index ✅

`neurobrain/instructions.py`: 11 template families × slots × surface forms.

| family | share | what it teaches |
|---|---|---|
| plain / bare | 23% | canonical phrasing |
| multi | 14.6% | "click save, **not** cancel" -- negation with the distractor present |
| app / section / contextual | 28% | "in Studio, ...", "... in the toolbar" |
| relative | 11.5% | "the button **under the search bar**" |
| sequence | 6.2% | two steps in one sentence |
| type / slider / checkbox_off | 17% | action-specific phrasing with values |

Surface forms are a product of prefix (16) × suffix (12) × case (3) × keystroke
error (18%) × contraction (8%): lower 55%, prefix 76%, suffix 59%, title 30%,
**typo 18.8%**, contraction 8%.

1,005,000 **unique** instructions in 54 s, 325 MB peak RSS.
Dedupe index: blake2b64(normalise(text)) set; a collision re-rolls the surface
form instead of dropping the sample → **reject rate 4.13% of raw draws** and
**0.00% duplicates in the emitted corpus** (measured on the token stream, 6k
documents sampled). Mean 50.4 chars, p99 doc length 33 tokens.

Records are also written as `shard-XXXX.jsonl.gz` with the structured target
(label/role), distractor, anchor, constraints, family and variant, so a
verifier or the trajectory forge can check what the words actually asked for.

## M4 — drive corpus v2 at scale ✅

`neurobrain/drive.py` rewritten around `specs/drive.md`:

* UI episodes now draw from a **failure catalogue** (wrong element, click off
  target, element scrolled out, modal blocked the click, focus in another
  window, double activation, late repaint) and each failure names its **ladder
  rung** (`retry_exact`, `retry_shifted`, `replan`, `decompose`, `tool_switch`,
  `escalate`);
* **honest terminals**: 8% of UI episodes and 12% of plan episodes end in
  `success-partial` or `budget-exhausted` **through the escalate/park rung**,
  never straight after a `<|retry|>` -- so the model learns that a task ends in
  exactly one of done / done-partial / failed, and that parking is not the same
  as retrying;
* code episodes: 19 bugs, 2-4 attempts, error kinds AssertionError / TypeError /
  ValueError / IndexError / NameError, expected values computed by executing the
  reference body;
* plan episodes: 1-2 obstacles, second one triggers the **tool switch** rung.

Measured at 1M episodes (seed 23, 265.07M tokens, 530 MB):

```
terminal_rate=1.000  retry_after_failure=1.000  failure_frac=0.990  retry/ep=2.02
mix ui/code/plan 0.45/0.40/0.15   terminals success/partial/failed 0.92/0.04/0.03
duplicates exact 0.00%            doc_len mean 265, p99 504 tokens
```

All four numbers are recomputed **from the token stream**, not from the
generator's counters (`dataforge verify` re-scans the bytes; the numpy scan and
the text classifier are pinned to each other by a test).

## M5 — trajectory forge ✅

`neurobrain/trajectories.py` + `dataforge` dataset `trajectories`: records match
`specs/task_schema.md` exactly (id, instruction, created_at, status, plan,
history, result, budget) and carry a `branches` list of the failure paths with
the recovery that was recorded.

`validate_trajectory` enforces: observation before **and** after every action
(no blind action), verdict ∈ progress/no-op/wrong/fatal, non-decreasing step
numbers, a positive budget, `status=done ⇒ result.success`. Every record is
validated before it is written; `verify` re-validates 200 records per shard
from the gzip on disk.

Measured (seed 4, 50k): **0 invalid**, failure 58.4%, recovery 100%, verdicts
no-op 7 / progress 80 / wrong 14, plan 3.6 steps, history 3.5 entries per task,
mix 45/40/15 by source.

## M6 — code corpus v2 + 4096 code tokenizer ✅

`dataforge` dataset `code_v2`:

1. **AST filter** — `ast.parse`, no regex; a file that does not parse is dropped.
2. **Function-level extraction** + `sha1(ast.dump(node))` **dedupe across all
   files**, with a **split assigned on the function hash** so a copy-pasted
   function can never be on both sides of the wall (a test parses the emitted
   streams and asserts the split is disjoint).
3. **Category tags** from module path + imports + names:
   test / data / fileio / net / web / cli / ui / core.
4. **Instruction→code pairs** mined from docstrings (`<|task|>...<|code|>...`).
5. **Two tokenizers**: the checkpoint's 2052 BPE and a **4096 code-only BPE**
   trained from scratch on the train split only (`code_tokenizer_4096.json`).

On the smoke slice (2 MB, 1,486 functions): **2.85 bytes/token @2052 vs 3.54
bytes/token @4096 (+24.1%)**, 539 instruction pairs. The standard build trains
the 4096 tokenizer on 12 MB of code.

Bug the gates caught: the first 4096 tokenizer came out at 4100 ids (4096 BPE +
4 specials). The convention is now the same as the checkpoint's 2052-token
tokenizer: **4096 total ids = 4092 BPE + 4 specials**.

## M4+ — honest terminals for impossible objectives (after agent 01's overclaim finding)

Agent 01 published (20:51) that a `<|scan|>` prefix present **only** on
impossible episodes lets a model learn "scan means impossible" instead of
reading the element list. My M4 corpus had no impossible objectives at all, so
a model trained on it can only ever claim success — exactly the overclaiming
failure the fleet measured at 20:27.

Two changes, both in `neurobrain/drive.py`:

1. **`<|scan|>` on every UI episode**, objective + element list first, so the
   scan carries information about the screen, not about the answer.
2. **8% impossible objectives**: the objective names a label that is *not* in
   the element list (checked at generation time), the loop makes 2–4 honest
   attempts, then reports `<|check|>objective impossible: ...` and closes with
   `<|done|>failed` — never after a `<|retry|>`, so invariant 2 still holds.

Terminal vocabulary is now the four the fleet uses:
`success | success-partial | budget-exhausted | failed`, all counted from the
token stream by `stats`.

Measured on 3,000 episodes: success 0.889, partial 0.040, exhausted 0.033,
failed 0.039, failure_fraction 0.994, terminal_rate 1.000.

## M7 — determinism proof across two clean builds ✅

Two independent `--profile standard --seed 23` builds into `data/forge-A` and
`data/forge-B`, 1420 s and 1424 s wall clock (run **in parallel** on 2 cores, so
the wall clock is inflated; `hard_ui` alone measured 980 s uncontended).

```
dataforge diff --a data/forge-A --b data/forge-B
=> determinism OK  49 shards identical

dataforge verify --dir data/forge-A
=> verify OK  code:2 code_v2:6 drive:2 hard_ui:20 instructions:12
              trajectories:10 ui_protocol:2 ui_seed:5   49/49 sha256 match

dataforge stats --dir data/forge-A
=> ranges all within bounds  OK      (58 s, peak RSS 967 MB)
```

## The whole standard corpus, one screen

```
dataset        kind            n            tokens    dup%   ranges
code           token_streams     3,558 docs 14.22M    0.00   OK
code_v2        token_streams    51,625 funcs 11.94M    0.00   OK
drive          token_streams 1,000,000 eps  280.03M    0.02   OK
hard_ui        ui_shards      100,000 imgs       -    0.00   OK
instructions   token_streams 1,005,000 ins  19.41M    0.00   OK
trajectories   jsonl            50,000 tasks      -    0.00   OK
ui_protocol    token_streams   150,000 docs 17.15M    0.00   OK
ui_seed        ui_shards       25,000 imgs       -    0.00   OK
                                                    342.7M tokens total
drive invariants  terminal_rate=1.000 retry_after_failure=1.000 failure_frac=0.991
                  retry/ep=2.02 mix 0.45/0.40/0.15 terminals ok/partial/exhausted/failed 0.89/0.04/0.03/0.04
hard_ui           755/1024 heat cells, clip 1.5%, entropy 5.54 bits, label H/Hmax 1.000
instructions      1,005,000 unique, reject 4.13%, typo 18.8%, multi 14.6%, relative 11.5%
trajectories      0 invalid, failure 59.4%, recovery 100%, verdicts no-op 6/progress 80/wrong 15
code_v2           2.84 bytes/token @2052 vs 3.28 @4096 (+15.6%), split disjoint by function hash
```

## Bugs the gates caught this session (all fixed, each one is now a test)

| where | what | number |
|---|---|---|
| seed drive generator | 1-in-3 code episodes was a single passing attempt → duplicate corpus | dup 32.28% → 0.03% |
| seed offset target | divides sub-cell error by 0.45, saturating half the samples | clip 51.6% → 1.4% (hard world) |
| hard world v1 | sliders were 1.4% of targets → `drag` unlearnable | drag → 6.9% |
| `--set` bound | `offset_mean_abs ≤ 0.45` was wrong: 0.5 is correct by construction | band 0.30–0.60 |
| ui_protocol writer | appended a second EOT → 50% "duplicates" that were empty docs | dup 50% → 0.00% |
| marker scan | markers share their first token → the lookup table collided | all 15 markers found |
| describe in one line: terminal mix counted the word "failed" in code retry text | fixed by matching the token sequence after `<\|done\|>` | 0.00 → 0.04 correct |
| verify | compared a shard scan against the dataset aggregate | compares per-shard invariants |
| code_v2 dedupe | emitted every copy of a duplicated function (hash was stored, never checked) | dup 8.80% → 0.00% |
| 4096 tokenizer | came out at 4100 ids (4096 BPE + 4 specials) | 4096 total = 4092 + 4 |

## Done-when audit (agent 05)

| requirement | state |
|---|---|
| `dataforge build --profile standard` reproduces every dataset | 8/8 datasets, 49 shards |
| from an empty sandbox in under 45 min | 23.7 min/build (parallel pair, 2 cores); 980 s of it is `hard_ui` |
| `verify` passes | 49/49 sha256, invariants re-derived from the bytes |
| `stats` prints a one-screen health report incl. drive invariants | yes, exit 0 only when every number is in range |
| agents 03/04/01 consume the shards without asking | `DATA.md` + `dataforge link` + per-shard tokenizer field; bus post landed |

### Next

Next cycle: keep extending the hard world (more app grammars, a second label
deck for OOD themes) and watch what agents 03/04 report as failure modes -- the
forge answers to the training curves, not to its own taste. Also: fold the
impossible-objective vocabulary into the trajectory forge, and add a
`dataforge stats --watch` line for the coordinator's scoreboard.
