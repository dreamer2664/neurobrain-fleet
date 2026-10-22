# agent 05 — data forge · STATUS

updated: 2026-10-22 (M1 complete)

| milestone | what | state | number |
|---|---|---|---|
| **M0** | `dataforge` skeleton, `stats` + `verify` on existing corpora, publish dup + balance | **done** | 244.6M tokens, dup ≤ 0.03%, drive invariants 1.000/1.000/1.000, 17 tests green |
| **M1** | hard world v1 (8 tiles + 10k samples + manifest) | **done** | 661/1024 cells, clip 1.4%, entropy 5.56, 99 s / 702 MB, verify OK |
| M2 | 100k hard-UI samples, tiers, verified | next (≈16 min at 10 ms/sample) | — |
| M3 | instructions v1 with dedupe, 1M | queued | — |
| M4 | drive corpus v2, three invariants enforced, 1M episodes | seed part done at M0 | 1M eps, terminal 1.000 |
| M5 | trajectory forge, 10k tasks, schema-valid | queued | — |
| M6 | code corpus v2 + 4096 tokenizer + held-out split | queued | — |
| M7 | determinism proof across two clean builds | proven once at M0 | 11/11 shards identical |

## Current corpus (profile `standard`, seed 23)

`dataforge build --out data/forge --profile standard` → 238 s, peak RSS 1133 MB,
479 MB on disk:

| dataset | files | n | tokens |
|---|---|---|---|
| code | `code_train.bin` `code_val.bin` | 3,558 docs | 14.22M |
| drive | `drive_train.bin` `drive_val.bin` | 1,000,000 episodes | 213.23M |
| ui_protocol | `ui_train.bin` `ui_val.bin` | 150,000 docs | 17.15M |
| ui_seed | `ui_seed/shard-0000..0004.npz` | 25,000 images | — |

Machine-readable artifacts in `artifacts/`: `stats-standard.json`,
`verify-standard.json`, `determinism.json`, `tiles-seed.png`.

## Health line (paste into every cycle)

```
drive terminal_rate=1.000 retry_after_failure=1.000 failure_frac=1.000 mix 45/40/15 |
dup exact <=0.03% | ui_seed 72/1024 cells 2.27 bits (seed) | hard_ui 661/1024 cells,
clip 1.4%, 5.56 bits, tiers 20/45/35 | verify 13/13 sha256 OK | determinism 13/13 |
standard 238 s @ 1133 MB | hard_ui 10k 99 s @ 702 MB
```

## Known limitations (being fixed in M2–M6)

- seed world (`ui_seed`) is easy by construction: 72/1024 heat cells,
  2.27 bits entropy, 51.6% saturated offsets. Use `hard_ui` for training.
- hard world text is 5.2–7.8 px in the 128 px output (≈ 8–14 px on a 1920 px
  source screen before downsampling). Labels are truncated like a real UI.
- `hard_ui` at 10k touches 661/1024 cells; at 100k it will cover all of them
- code stream v1 is stdlib-only, no AST filter, no function-level dedupe (M6)

## Blockers

none.
