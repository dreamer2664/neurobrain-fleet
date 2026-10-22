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
 "ctx": 256, "tokenizer_sha256": "...", "step": 4652}
```

`config.json` for the grounder:

```json
{"kind": "grip", "char_vocab": 40, "max_len": 48, "d": 64, "grid": 32, "step": 400}
```

## inference api (brainbox, local http on 127.0.0.1)

```
POST /score        {"prompt": str, "top_k": 5}      -> {"tokens": [...], "logprobs": [...]}
POST /generate     {"prompt": str, "max_tokens": 64} -> {"text": str, "tokens": int, "ms": int}
POST /ground       {"png_b64": str, "instruction": str} -> {"x": int, "y": int, "action": str}
GET  /health                                          -> {"ok": true, "rss_mb": int, "step": int}
```

The server must answer `/health` within 50 ms, report its own RSS, and refuse
requests that would push it past the RAM budget (429 with `reason`).
