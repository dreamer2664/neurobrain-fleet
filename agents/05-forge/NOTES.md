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

### Next

M1: `ui_world_hard` v1 — real 8–14 px text, toolbars/tabs/sidebars/dialogs,
disabled/focused/selected states, light/dark/high-contrast, cursor in frame,
JPEG noise, DPI 100–200%. Deliverable is 8 tiles in this file plus 10k samples
and a verified manifest. The gates I set for it: heat cells ≥ 150/1024,
entropy ≥ 2.5 bits, offset clip ≤ 5%, dup ≤ 2%.
