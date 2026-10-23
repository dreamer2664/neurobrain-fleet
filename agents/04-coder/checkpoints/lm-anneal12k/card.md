# checkpoint card: anneal12k

- packed: 2026-10-23T05:41:15Z
- arch: 6L d224 h7 ctx256 vocab2052 (4,247,264 params)
- step: 13200
- weights_sha256: `e0ebe819d47f996cdde154f5d17197d6d84c452694c305557a77733e264804bc`
- tokenizer_sha256: `198316dfad27b115e58868edc9b850e58ad23ebf596aed063aec023c8f30f8ab`

## numbers

| metric | value |
|---|---|
| codebench pass@1 (greedy) | 0.0 |
| codebench pass@1 (sampled) | 0.0 |
| codebench syntax_valid (greedy) | 1.0 |
| codebench body_rate (greedy) | 0.7755 |
| codebench step | 13200 |
| terminal_rate | 1.0 |
| retry_after_failure | 1.0 |
| honest_completion | 1.0 |
| code val_loss | 2.0486 |
| code val_ppl | 7.76 |

## sample generations (verbatim, failures included)

### code

prompt:
```
def average(values):

```
generation:
```
def average(values):
    return round(values):
    return round(total) % len(values), 2)<|run|>pytest -q<|err|>assert mean([2, 4, 6]) == 4.0  ->  AssertionError<|think|>the branch checks the wrong variable<|retry|>attempt 1 failed, patch the logic and re
```

### drive

prompt:
```
<|drive|>objective: pick export
```
generation:
```
<|step|>1<|act|>click(1455,510)<|obs|>menu closed after refresh<|check|>objective not satisfied: wrong element<|retry|>that was refresh, not export. target the menu labelled export<|step|>2<|act|>click(450,1770)<|obs|>no visible change<|check|>objective not satisfied: click landed off target<|retry|>aim at the centre of the menu, export<|step|>3<|act|>click(1425,825)<|obs|>menu closed after export<|
```

