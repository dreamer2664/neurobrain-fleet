# spec: eval suite (owner: agent 3)

The scoreboard decides whether brainbox ships. It runs headless: Xvfb + a set of
tkinter "apps" (file manager, editor, browser-lookalike, settings dialog), each
with a scripted starting state.

## suite

```json
{"id": "fm-003",
 "category": "file_manager | editor | browser | settings | multi_app | recovery | code",
 "instruction": "delete every .iso file in Downloads",
 "app": "filemanager",
 "setup": "seed_downloads_with_isos",
 "success": {"check": "no_iso_in_downloads", "args": {}},
 "budget": {"max_steps": 20, "max_seconds": 120}}
```

Success checks are code, not vibes: filesystem assertions, widget-state queries,
process checks, or text extraction. Every task is idempotent and cleans up.

## scoreboard

```json
{"commit": "abc1234", "model": {"lm_step": 9000, "grip_step": 6000},
 "n": 60, "success": 0.0, "by_category": {...},
 "median_steps": 0, "median_seconds": 0.0, "ram_peak_mb": 0,
 "failures": [{"id": "fm-003", "why": "clicked rename instead of delete"}]}
```

Rules: 60 tasks minimum; every failure stores a screenshot strip; the scoreboard
is committed to `agents/06/scoreboard.json` and published on the bus. Nobody
merges a model change that drops the score.
