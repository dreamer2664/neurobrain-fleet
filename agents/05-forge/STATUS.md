# agent 05 — data forge · STATUS

updated: 2026-10-22 (M0–M7 done — all milestones complete)

| milestone | what | state | number |
|---|---|---|---|
| **M0** | `dataforge` CLI, `stats` + `verify` on the corpora | **done** | 244.6M tokens, dup ≤0.03%, 18→28 tests |
| **M1** | hard world v1, 10k samples + manifest | **done** | cells 72→661/1024, clip 51.6%→1.4%, 5.56 bits |
| **M2** | 100k hard-UI samples, tiers, verified | **done** | 755/1024 cells, clip 1.5%, 5.54 bits, 980 s @480 MB |
| **M3** | 1M instructions with dedupe index | **done** | 1,005,000 unique, 0.00% dups, reject 4.13%, 54 s |
| **M4** | drive corpus v2, invariants enforced, 1M episodes | **done** | 265.07M tokens, terminal 1.000, retry-ok 1.000, failure 0.990 |
| **M5** | trajectory forge, schema-valid | **done** | 50k tasks, 0 invalid, failure 58%, recovery 100% |
| **M6** | code corpus v2 + 4096 tokenizer + held-out | **done** | 3.54 vs 2.85 bytes/token (+24.1%), disjoint split |
| **M7** | determinism proof across two clean builds | **done** | **49/49 shards identical**, verify 49/49, stats OK |

**Full standard build: 8 datasets, 49 shards, 342.7M tokens, 23.7 min, verify OK,
determinism 49/49, stats peak RSS 967 MB.**

## CLI

```
python -m dataforge build  --out DIR --profile {smoke,standard,max} [--seed N]
                           [--datasets a,b] [--set ds.knob=value] [--no-stats]
python -m dataforge stats  --dir DIR [--json PATH]
python -m dataforge verify --dir DIR        # sha256 every shard + semantics
python -m dataforge diff   --a DIR --b DIR  # determinism proof
python -m dataforge index  --dir DIR        # rebuild the top-level manifest
python -m dataforge link   --dir DIR --to data
```

29 tests in `tests/test_dataforge.py`, written before each increment; 29/29 green.

## Health line

```
drive terminal 1.000 / retry_after_failure 1.000 / failure 0.991 / mix 45-40-15
      terminals ok/partial/exhausted/failed 0.89/0.04/0.03/0.04, 280.03M tokens, dup 0.02%
hard_ui 100k: cells 755/1024, clip 1.5%, entropy 5.54 bits, label H/Hmax 1.000
instructions 1.005M unique, reject 4.13%, typo 18.8%, multi 14.6%, relative 11.5%
trajectories 50k, 0 invalid, failure 58.4%, recovery 100%
code_v2 3.28 bytes/token @4096 vs 2.84 @2052 (+15.6%), split disjoint by function hash
```

## Consumers

`agents/05-forge/DATA.md` — build, verify, formats, per-dataset quirks, and what
is not there yet. Artifacts in `agents/05-forge/artifacts/`:
`stats-standard.json`, `stats-hard-10k.json`, `stats-hard-100k.json`,
`stats-drive-1M.json`, `verify-standard.json`, `determinism.json`,
`tiles-seed.png`, `tiles-hard.png`.

## Known limitations

- hard world text is 5.2–7.8 px in the 128 px output; labels truncate like a real UI
- `ui_seed` is easy by construction (72 cells, 2.27 bits, 51.6% clipped offsets) — train on `hard_ui`
- hard world has 4 layout grammars; more app types are the next increment
- drive/plan episodes are synthetic; they teach the protocol, not a real app

## Blockers

none.
