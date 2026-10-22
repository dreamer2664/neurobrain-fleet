# spec: drive loop (owner: agent 1)

The model is trained to finish (see `neurobrain/drive.py`). The loop makes sure
finishing actually happens on a real machine, because no 4M-parameter model can
be trusted to police itself.

## Contract

A task ends in exactly one of:

| terminal | meaning |
|---|---|
| `done` | the success check passed |
| `done-partial` | some sub-goals passed, budget exhausted first |
| `failed` | budget exhausted with no measurable progress |

There is no other exit. `failed` is logged with the screenshot strip and the
last five actions so the next attempt can start from evidence.

## The retry ladder

Each task walks this ladder; a rung is only left when it has been tried twice:

1. **retry exact** — same action, same coordinates (flaky UI, slow repaint)
2. **retry shifted** — resample the click inside the target box
3. **replan** — ask the language brain for a new plan, keeping the evidence
4. **decompose** — split the objective into subtasks and run them serially
5. **tool switch** — use the shell/API path instead of the GUI path
6. **escalate** — write a `blocked` record, queue the task for the next idle
   window, and move to the next task. Never drop it silently.

After each rung the loop re-observes before acting. No blind retries.

## Never idle

When the queue is empty the runtime does not spin down. In priority order:

1. re-run the verification of the last ten `done` tasks (catch drift)
2. finish any `done-partial` tasks left in the backlog
3. compact its own run logs and delete screenshots older than 7 days
4. run a self-check: `/health`, model hashes, disk headroom
5. then sleep 30 s and repeat

Self-assigned work is always non-destructive and always recorded in
`~/.brainbox/runs/`.

## Budgets (hard)

| resource | limit | action on breach |
|---|---|---|
| steps per task | 60 | force `failed`, keep evidence |
| seconds per task | 600 | force `failed` |
| RSS | 3.8 GB | governor pauses the loop, drops caches, resumes at 3.2 GB |
| disk for runs | 2 GB | delete oldest screenshots first |

Destructive actions (`delete`, `overwrite`, `send`) move the target into
`~/.brainbox/trash/<task-id>/` first, so `brainbox undo` is always possible.
That is not a guardrail on willingness: it is what makes an unattended machine
safe to leave running for a week.

## Drive metrics (published every cycle)

```
terminal_rate      tasks that end in done / all tasks
retry_depth        mean ladder rung reached on failures
recovery_rate      tasks that hit >= 1 failure and still reached done
idle_work_rate     self-assigned maintenance tasks completed per hour
```

The brain's training objective (`reports/drive_eval.json`: `terminal_rate`,
`retry_after_failure`, `honest_completion`) and the loop's runtime numbers are
reported side by side. A model with high terminal rate in the lab and a low
recovery rate on the machine means the loop is wrong, not the model.
