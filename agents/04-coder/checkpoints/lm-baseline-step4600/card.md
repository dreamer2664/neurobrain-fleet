# checkpoint card: lm-baseline-step4600

- packed: 2026-10-22T21:34:50Z
- arch: 6L d224 h7 ctx256 vocab2052 (4,247,264 params)
- step: 4600
- weights_sha256: `ae7599cfd681afc9117fd3a978afd458e44e862052115a7a6325863b639d22a1`
- tokenizer_sha256: `198316dfad27b115e58868edc9b850e58ad23ebf596aed063aec023c8f30f8ab`

## numbers

| metric | value |
|---|---|
| codebench pass@1 (greedy) | 0.0 |
| codebench pass@1 (sampled) | 0.0 |
| codebench syntax_valid (greedy) | 1.0 |
| codebench body_rate (greedy) | 0.0 |
| codebench step | 4600 |
| terminal_rate | 0.0 |
| retry_after_failure | 0.0 |
| honest_completion | 0.0 |
| code val_loss | 2.2873 |
| code val_ppl | 9.85 |

## sample generations (verbatim, failures included)

### code

prompt:
```
def average(values):

```
generation:
```

from collections.abc import Callable
from typing import Any
from typing import TYPE_CHECKING
from typing import TypedDict
from typing import TypedDict
from typing import TypedDict
from typing import TypedDict
from typing import TypedDict
from typing import TypedDict
from typing import Typed
```

### drive

prompt:
```
<|drive|>objective: pick export
```
generation:
```
er.DefaultScope
        format_objects: dict[str, Any] = {},
    ) -> None:
        """
        Return the format of the format.
        """
        self.format_object_objects: dict[str, Any] = {}
        self.format_objects: dict[str, Any] = {}
        self.format_objects: dict[str, Any] = {}
        self.format_objects: dict[str, Any] = {}
        self.format_objects: dict[str, Any] = {}
        self.format_objects: dict[str, Any] = {}
        self.format_objects: dict[str, Any] = {
            "__dict__": [
```

## lineage / notes

Official fleet baseline: release ckpt-1022 (coordinator), trained ~4.6k steps on v1 corpus (code+ui only, no drive). Rebuilt-and-verified copy kept as lm_baseline_step4600.pt. Weights source: github.com/dreamer2664/neurobrain/releases/tag/ckpt-1022

