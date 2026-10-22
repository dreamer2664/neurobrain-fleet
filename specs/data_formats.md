# spec: data formats (owner: agent 5)

Three artifact kinds, all chunked and manifest-driven so any agent can consume
without coordination.

## 1. token streams (language brain)

```
data/code_train.bin   uint16 little-endian, flat, documents separated by <|endoftext|>
data/code_val.bin     same
data/ui_train.bin     same, desktop-control transcripts
data/ui_val.bin       same
data/tokenizer.json   {"vocab": [bytes-as-latin1], "merges": [[a,b],...], "specials": [...]}
```

## 2. UI grounding shards (eyes)

One `.npz` per shard, 5k samples each:

```
images    uint8   [N,128,128,3]     rendered screens
tasks     int64   [N,48]            char ids of the instruction (a-z0-9 -)
heat      float16 [N,32,32]         soft target over the 32x32 grid
offsets   float32 [N,2]             sub-cell offset of the widget centre in [-1,1]
actions   int64   [N]               0=click 1=type 2=toggle 3=drag
manifest.json                       {"shards": [...], "n": int, "version": "v1"}
```

## 3. trajectories (orchestrator)

JSONL, one task per line, exactly the object from `task_schema.md`. Stored as
`trajectories/shard-XXXX.jsonl`, gzip after 1000 lines.

Manifest rule: every dataset directory has `manifest.json` with `version`,
`n`, `sha256` per shard, and `generated_by`. Consumers verify the hash before
training. If a hash fails, skip the shard and publish `[5] blocked: bad shard`.
