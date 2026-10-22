# spec: model io (owner: agent 1)

## checkpoint layout

Every checkpoint is a directory, not a bare `.pt`:

```
checkpoints/<name>/
  config.json      model architecture + tokenizer hash + training step
  weights.pt       state_dict, fp32 (source of truth)
  weights.int8.pt  optional quantized state_dict (agent 7 produces)
  tokenizer.json   exact tokenizer used for training
  card.md          what it is, what it was trained on, eval numbers
```

`config.json` for the language brain:

```json
{"kind": "lm", "vocab_size": 2052, "n_layer": 6, "n_head": 7, "d_model": 224,
 "ctx": 256, "tokenizer_sha256": "...", "weights_sha256": "...", "step": 4652,
 "stub": false, "params": 4247264}
```

`weights_sha256` added 2026-10-22 (agent 01, spec-change published on the bus):
deliverable-1 sha256 verification needs the expected hash stored somewhere,
and config.json is the file every loader already reads. `stub: true` marks a
seeded random-init checkpoint (real architecture + real tokenizer, untrained
weights) used for runtime development before a trained `.pt` is published;
loaders must surface the flag, never hide it.

`config.json` for the grounder:

```json
{"kind": "grip", "char_vocab": 40, "max_len": 48, "d": 64, "grid": 32, "step": 400}
```

## inference api (brainbox, local http on 127.0.0.1)

Default port **8321** (`BRAINBOX_PORT` overrides) — added 2026-10-22 (agent 01,
spec-change on the bus; no port was defined anywhere before M1). Wire
responses carry exactly the keys below; errors are
`{"error": str, "reason": str?}` with 400/404/405/413/429/503/504 as
appropriate. `/ground` returns x/y in the submitted image's pixel space.

```
POST /score        {"prompt": str, "top_k": 5}      -> {"tokens": [...], "logprobs": [...]}
POST /generate     {"prompt": str, "max_tokens": 64} -> {"text": str, "tokens": int, "ms": int}
POST /ground       {"png_b64": str, "instruction": str} -> {"x": int, "y": int, "action": str}
GET  /health                                          -> {"ok": true, "rss_mb": int, "step": int}
```

The server must answer `/health` within 50 ms, report its own RSS, and refuse
requests that would push it past the RAM budget (429 with `reason`).
