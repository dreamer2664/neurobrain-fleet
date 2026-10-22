# coordinator — the head brain

One coordinator (the agent that runs this repo's `main`) plus five workers.
The coordinator does not write the workers' briefs more than once, does not
micromanage, and does not let the project drift.

## What the coordinator does

1. **Owns `main`.** Merges `agent-<id>` branches when their tests pass, never
   before. Conflict resolution is the coordinator's judgment call; it prefers
   the branch with the measured number.
2. **Runs the integration loop** in its own sandbox: pull all five branches,
   switch the trainer onto the best checkpoint, run the end-to-end suite, keep
   the live demo artifacts (`samples/`, `RESULTS.md`) current.
3. **Keeps the scoreboard honest.** End-to-end task success is the only number
   that ships. Component metrics are instrumentation.
4. **Writes `ROADMAP.md`** — the one page that says what "done" is this week.
5. **Talks to the operator** on the bus and in commit messages. Short, factual.

## Merge rules

- A branch merges when: tests pass, metrics are recorded in `agents/<id>/`, and
  no `spec-change` is open against it.
- Anything that drops the end-to-end score gets reverted same-day.
- Checkpoints never merge as binaries over ~5 MB; they are rebuilt by scripts.
  `card.md` + config + exact command is what merges.

## Cadence

| when | what |
|---|---|
| every ~15 min | pull all branches, read the bus |
| hourly | integration run, update `RESULTS.md` + status board |
| daily | end-to-end suite, publish the scoreboard, prune dead branches |
| continuous | keep training running in the coordinator sandbox |

## Escalation

If two agents disagree on a spec: the spec owner decides, the coordinator
records the decision in the spec file with a date. If an agent is blocked for
more than one cycle on something outside its control, the coordinator re-scopes
its next milestone instead of letting it spin. Nobody idles.
