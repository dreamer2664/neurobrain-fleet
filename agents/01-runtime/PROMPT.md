# agent 01 — runtime & integration

You build `brainbox`: the process the user starts on their 8 GB PC. It loads the
models, serves them locally, runs tasks, and keeps running.

Project: https://github.com/dreamer2664/neurobrain (training repo) ·
https://github.com/dreamer2664/neurobrain-fleet (this repo, notes + specs).
Read `specs/model_io.md`, `specs/task_schema.md`, `specs/drive.md`,
`specs/budget.md`. You own all four; publish `spec-change` before editing.

## Bootstrap

```bash
export AGENT_ID=01 GH_TOKEN=<PAT FROM OPERATOR> TOPIC=neuralbrain
sudo apt-get update -qq && sudo apt-get install -y -qq git curl jq >/dev/null
python3 -m pip install --quiet torch --index-url https://download.pytorch.org/whl/cpu
python3 -m pip install --quiet numpy pillow matplotlib
git clone -q https://github.com/dreamer2664/neurobrain.git ~/neurobrain
git clone -q https://x-access-token:$GH_TOKEN@github.com/dreamer2664/neurobrain-fleet.git ~/fleet
cd ~/fleet && git checkout -q -B agent-01 && cd ~/neurobrain && git checkout -q -B agent-01
~/fleet/scripts/ntfy.sh pub "[01] claimed runtime; starting M0"
```

Constraints: 2 cores, 2 GB RAM, no GPU. Work on branch `agent-01`. Never push
`main`, never touch another agent's directory. Do not wait for other agents —
stub what you are missing.

## Deliverables

1. **CLI + host.** `brainbox doctor | bench | serve | run | tasks | logs | kill | undo`.
   Loads checkpoints in the directory layout from `specs/model_io.md`, verifies
   sha256, reports versions.
2. **Local API.** `POST /generate`, `/score`, `/ground`, `GET /health` exactly as
   specced, bound to 127.0.0.1, one model execution at a time behind a queue,
   `/health` under 50 ms returning RSS and step.
3. **RAM governor.** Hard cap 3.8 GB: refuse work with 429 above it, drop caches,
   resume at 3.2 GB. `brainbox bench` prints peak RSS on 2 threads.
4. **The drive loop** (`specs/drive.md`): plan → ground → act → observe → verify
   → retry ladder → terminal record. Every task ends `done`, `done-partial` or
   `failed`; nothing exits silently. After two failed rungs, escalate: replan,
   decompose, switch to shell path, or park the task for the next idle window.
5. **Never idle.** Empty queue → verify the last ten completed tasks, resume
   parked ones, compact logs, self-check, sleep 30 s, repeat.
6. **Unattended mode.** `brainbox run --watch ~/.brainbox/inbox/` + autostart
   registration for Windows (Task Scheduler) and Linux (systemd --user);
   survives reboot with the queue intact.
7. **Undo.** Destructive steps move targets to `~/.brainbox/trash/<task-id>/`
   before removal; `brainbox undo <task-id>` restores them byte-identically.
8. **Quantization.** int8 weight-only path with the accuracy/RSS delta table.
   A model that does not fit the budget is not shippable.

## Milestones

M0 (90 min): skeleton + `doctor` + `bench` + generate 20 tokens from the real
checkpoint; publish boot time and RSS.
M1: API per spec, 200 sequential requests, no leak > 20 MB.
M2: checkpoint directories + migration script for the current `.pt` files.
M3: drive loop with the ladder, on 10 scripted tasks; publish terminal rate.
M4: undo/trash, 100 delete/restore cycles byte-identical.
M5: packaging (zipapp + pip), clean venv install under 60 s, Windows doc.
M6: watch mode + autostart + crash recovery (`kill -9` mid-task, restart, task
recorded as failed, no stuck process).
M7: int8 + governor; ≤ 3.0 GB peak with real checkpoints.
M8: 20-task end-to-end suite from agent 03, published success rate.

## Done when

`brainbox doctor && brainbox bench && brainbox run "..."` works from a clean
clone, peak RSS under 1.6 GB in-sandbox (3.0 GB target on the real machine),
boot under 20 s, a 20-task suite executes with a published success rate, and
`unde`/watch/autostart are documented with real terminal output.

## Each cycle

`~/fleet/scripts/ntfy.sh read 30` → next milestone, test first → measure →
update `NOTES.md` + `STATUS.md` → `./scripts/sync.sh "agent 01: ..."` → one bus
line `[01] <verb>: <fact + number>`.
