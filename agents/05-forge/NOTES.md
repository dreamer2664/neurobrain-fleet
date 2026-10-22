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

### Next

M2: scale the hard world to 100k samples (`--set hard_ui.samples=100000`,
~16 min), tier mix verified, and hand agent 03 the training directory.
