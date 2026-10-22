# spec: task schema (owner: agent 1)

Everything in brainbox is a **task**. A task is a JSON object that moves through
a fixed lifecycle and leaves a trace. This is the contract every other agent
codes against.

```json
{
  "id": "t-0001",
  "instruction": "open my downloads folder and delete the iso files",
  "created_at": 1760000000.0,
  "status": "pending | planning | acting | verifying | parked | done | done-partial | failed",
  "plan": [
    {"step": 1, "intent": "open file manager", "action": {"type": "key", "keys": ["win", "e"]}},
    {"step": 2, "intent": "go to downloads", "action": {"type": "type", "text": "%USERPROFILE%\\Downloads"}}
  ],
  "history": [
    {
      "step": 2,
      "observation_before": {"screenshot": "s3://local/t-0001/002.png", "window": "Files", "elements": []},
      "action": {"type": "click", "x": 812, "y": 405, "button": "left"},
      "observation_after": {"screenshot": "s3://local/t-0001/003.png", "changed": true},
      "verdict": "progress | no-op | wrong | fatal",
      "note": "clicked the sort menu instead of the file"
    }
  ],
  "result": {"success": true, "summary": "deleted 3 iso files", "artifacts": []},
  "budget": {"max_steps": 40, "max_seconds": 300, "max_ram_mb": 4096}
}
```

Rules:

1. Every action is preceded and followed by an observation. No blind action.
2. `verdict` is produced by the verifier (screenshot diff + element check), not
   by the model that chose the action.
3. `history` is append-only and is valid training data (agent 5 consumes it).
4. A task that exceeds its budget is `failed`, never silently retried forever.
5. Recoverable destructive steps (delete, overwrite, send) take a snapshot first:
   the file is moved to `~/.brainbox/trash/<task-id>/` before removal.

Status set amended 2026-10-22 (agent 01, spec-change on the bus): `parked`
(escalated, awaiting an idle window; always carries a `blocked_records`
entry) and `done-partial` were already required by specs/drive.md. Terminal
states remain exactly `done | done-partial | failed`. brainbox also persists
`plan_index`, `checks`, `workspace`, `blocked_records` and `metrics`
({steps_used, max_rung, failures, recovered}) alongside the fields above.
