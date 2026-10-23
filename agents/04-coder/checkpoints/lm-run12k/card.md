# checkpoint card: run12k

- packed: 2026-10-23T00:53:24Z
- arch: 6L d224 h7 ctx256 vocab2052 (4,247,264 params)
- step: 12000
- weights_sha256: `d09cfd37f5bbaa7319787e76fe998ee0abee2f24b3325667fb04295abd4db6ff`
- tokenizer_sha256: `198316dfad27b115e58868edc9b850e58ad23ebf596aed063aec023c8f30f8ab`

## numbers

| metric | value |
|---|---|
| codebench pass@1 (greedy) | 0.0 |
| codebench pass@1 (sampled) | 0.0 |
| codebench syntax_valid (greedy) | 0.5306 |
| codebench body_rate (greedy) | 0.6531 |
| codebench step | 12000 |
| terminal_rate | 1.0 |
| retry_after_failure | 1.0 |
| honest_completion | 1.0 |
| code val_loss | 2.079 |
| code val_ppl | 8.0 |

## sample generations (verbatim, failures included)

### code

prompt:
```
def average(values):

```
generation:
```
def is_false_for_instruction(values):
    """
    Converage from a string.

    The value of the value is a false sorted by the named of
    `values`, and `values` must be infinitely sorted by the
    `values` elements. So, it's alternate to a `values`.
    """
    # the record of the value is simil
```

### drive

prompt:
```
<|drive|>objective: pick export
```
generation:
```
<|step|>1<|act|>click(1410,870)<|obs|>no visible change<|check|>objective not satisfied: click landed off target<|retry|>aim at the centre of the menu, export<|step|>2<|act|>click(495,1140)<|obs|>menu closed after export<|check|>objective satisfied<|done|>success<|endoftext|>
```

