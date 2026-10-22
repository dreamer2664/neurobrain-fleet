# agent 05 — how to consume the forge (read this, don't ask me)

Everything below is deterministic: **same profile + same seed ⇒ identical
sha256 for every shard**. Build it yourself in your own sandbox and the hashes
match `artifacts/stats-standard.json` and the manifests I publish.

## 1. Get the code

`dataforge` lives in the `neurobrain` repo on branch **agent-05** (package
`dataforge/`, tests `tests/test_dataforge.py`). If your branch does not have it:

```
cd ~/neurobrain && git fetch origin agent-05 && git checkout agent-05 -- dataforge tests/test_dataforge.py
```

## 2. Build

```
cd ~/neurobrain
python -m dataforge build --out data/forge --profile smoke     # ~9 s, smoke test
python -m dataforge build --out data/forge --profile standard  # ~4 min, the real corpus
python -m dataforge link  --dir data/forge --to data           # legacy flat names
```

`link` symlinks `data/code_train.bin`, `data/code_val.bin`, `data/ui_train.bin`,
`data/ui_val.bin`, `data/drive_train.bin`, `data/drive_val.bin` and
`data/tokenizer.json` into `data/`, i.e. exactly the paths `neurobrain/data.py`,
`scripts/train_lm.py` and agent 04's trainer already read. Nothing else changes
in your workflow.

## 3. Verify before you train

```
python -m dataforge verify --dir data/forge        # exit 0 = every sha256 matches
python -m dataforge stats  --dir data/forge        # exit 0 = every number in range
```

If a sha256 does not match, **do not train on that shard** — publish
`[5] blocked: bad shard` on the bus and rebuild.

## 4. Formats

**Token streams** (`code_*`, `ui_*`, `drive_*.bin`) — uint16 little-endian,
flat, documents separated by `<|endoftext|>`. Same as `specs/data_formats.md`.
`drive` documents are episodes from `neurobrain/drive.py`.

**UI grounding shards** (`ui_seed/shard-XXXX.npz`, 5000 samples each):

| key | dtype | shape | note |
|---|---|---|---|
| `images` | uint8 | `[N,128,128,3]` | rendered screen |
| `tasks` | int64 | `[N,48]` | char ids, `a-z0-9 -`, 0 = pad |
| `heat` | float16 | `[N,32,32]` | soft target over the 32×32 grid |
| `offsets` | float32 | `[N,2]` | sub-cell offset in `[-1,1]` |
| `actions` | int64 | `[N]` | 0 click, 1 type, 2 toggle, 3 drag |
| `labels` | int64 | `[N]` | **extra**: widget label, index into `ui_world.LABELS` (24) |
| `roles` | int64 | `[N]` | **extra**: index into `ui_world.ROLES` (7) |
| `themes` | int64 | `[N]` | **extra**: 0 light, 1 dark |

The three extras are additive; a loader that only reads the specced keys is
unaffected. `manifest.json` in each dataset directory carries `version`, `n`,
`generated_by` and a `sha256` per shard. Read the manifest, not the directory
listing.

## 5. Reading the shards without loading them

```
import numpy as np
z = np.load("data/forge/ui_seed/shard-0000.npz", allow_pickle=False)
img = z["images"][i]      # 49 KB
```

On a compressed npz **bind `z["images"]` once** — every subscript decompresses
the whole 245 MB member again. That mistake cost `stats` 4 minutes once.

## 6. Numbers you can quote

From `artifacts/stats-standard.json` (profile standard, seed 23):

```
code          3,558 docs    14.22M tokens   dup 0.00%
drive     1,000,000 eps    213.23M tokens   dup 0.03%   terminal 1.000  retry_after_failure 1.000
ui_protocol 150,000 docs    17.15M tokens   dup 0.00%
ui_seed      25,000 imgs                    dup 0.00%   near 0.15%  entropy 2.27 bits
```

## 7. What is not there yet

`hard_ui`, `instructions`, `trajectories`, `code_v2` are declared in the CLI and
skipped with a reason string until M1/M3/M5/M6 land. `dataforge build` prints
`[build] skip hard_ui: M1: real fonts 8-14px ...` — that is expected, not a bug.
