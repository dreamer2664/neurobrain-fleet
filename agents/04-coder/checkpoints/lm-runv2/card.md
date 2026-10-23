# checkpoint card: runv2

- packed: 2026-10-23T04:52:44Z
- arch: 6L d224 h7 ctx256 vocab2052 (4,247,264 params)
- step: 12000
- weights_sha256: `7b3315faa2307fd1f4c7c70211526010f0fa527ad247c37303afd516a74dfa0c`
- tokenizer_sha256: `198316dfad27b115e58868edc9b850e58ad23ebf596aed063aec023c8f30f8ab`

## numbers

| metric | value |
|---|---|
| codebench pass@1 (greedy) | 0.0 |
| codebench pass@1 (sampled) | 0.0 |
| codebench syntax_valid (greedy) | 0.0 |
| codebench body_rate (greedy) | 1.0 |
| codebench step | 12000 |
| terminal_rate | 1.0 |
| retry_after_failure | 1.0 |
| honest_completion | 1.0 |
| code val_loss | 2.2149 |
| code val_ppl | 9.16 |

## sample generations (verbatim, failures included)

### code

prompt:
```
def average(values):

```
generation:
```
#893946972, since these are not incorrect
    """
    if not (isinstance(value, str) and value.lower() in {None, "raw": "future"}):
        raise TypeError(
            f"All keywords must be a name of {value.lower()} with "
            f"exc. {value.lower()}. "
            f"
```

### drive

prompt:
```
<|drive|>objective: pick export
```
generation:
```
<|step|>1<|act|>click(510,1410)<|obs|>button help highlighted<|check|>objective not satisfied: wrong element<|retry|>that was help, not export. target the menu labelled export<|step|>2<|act|>click(960,510)<|obs|>no visible change<|check|>objective not satisfied: click landed off target<|retry|>aim at the centre of the menu, export<|step|>3<|act|>click(930,510)<|obs|>menu closed after export<|check
```

