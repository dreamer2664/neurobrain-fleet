# agent 02 — desktop executor (the hands)

You build `deskhands`: the twelve primitives that move a real cursor on a real
screen, plus the reliability layer that makes retries meaningful.

Project: https://github.com/dreamer2664/neurobrain ·
https://github.com/dreamer2664/neurobrain-fleet. Read `specs/actions.md` (you own
it) and `specs/task_schema.md`. Publish `spec-change` before editing a contract.

## Bootstrap

```bash
export AGENT_ID=02 GH_TOKEN=<PAT FROM OPERATOR> TOPIC=neuralbrain
sudo apt-get update -qq && sudo apt-get install -y -qq git curl jq \
  xvfb x11-utils libx11-dev libxtst-dev tk >/dev/null
python3 -m pip install --quiet numpy pillow
git clone -q https://github.com/dreamer2664/neurobrain.git ~/neurobrain
git clone -q https://x-access-token:$GH_TOKEN@github.com/dreamer2664/neurobrain-fleet.git ~/fleet
cd ~/fleet && git checkout -q -B agent-02 && cd ~/neurobrain && git checkout -q -B agent-02
~/fleet/scripts/ntfy.sh pub "[02] claimed hands; starting M0"
```

Constraints: 2 cores, 2 GB RAM, headless. Use `xvfb-run` for every test.
Branch `agent-02`. Never push `main`, never touch another agent's directory.
Do not wait for other agents; your tests use your own demo app.

## Deliverables

1. **12 primitives** from `specs/actions.md` with zero third-party input
   libraries: X11 via ctypes (XTest/XGetImage), Windows via user32 SendInput
   (DPI-aware), macOS via Quartz CGEvent. Each returns
   `{ok, detail, duration_ms}`, retries once internally, refuses impossible
   coordinates.
2. **Demo app** (`deskhands/demo_app.py`): tkinter file-manager lookalike —
   list, buttons, entry, checkbox, dialog, slider — scriptable from JSON and
   able to dump its own state for assertions. This is the test rig.
3. **Capture**: full screen + region, ≤ 30 ms at 1280×720, downscale helpers
   (128×128, 640×360), monotonic timestamp.
4. **Windows/geometry**: enumerate windows (title, rect, pid), focus by title
   substring, report focused window, virtual-desktop bounds for multi-monitor.
5. **Reliability layer** (this is what the drive loop leans on):
   - post-action verification hook: "did the screen change where I clicked?"
   - `retry_shifted(action)`: resample the click within the target box ± a few
     pixels — the loop's rung 2 must be a single call
   - `type` handles unicode via clipboard fallback, `key` handles chords
   - `drag` interpolates ≥ 20 points and lands within 2 px
6. **Replay**: record an action list to JSON, replay deterministically, ship a
   before/after screenshot per action.
7. **Element hints** (heuristic, clearly marked): connected components of
   rectangular high-contrast regions → `[{x,y,w,h,contrast}]`, useful when the
   vision model is absent or unsure.

## Milestones

M0 (90 min): `xvfb-run python -m deskhands selftest` → table of 12 green rows
with latencies; push.
M1: capture path, 50 runs, no leak, latency table.
M2: demo app + scripted scenario (20 clicks, 200 chars, toggles, drag) at 100%.
M3: window enumeration + focus, 50 trials.
M4: unicode, chords, right click, scroll, 4K/DPI geometry matrix.
M5: verification hook + `retry_shifted` + replay artifacts.
M6: Windows backend with fake-user32 unit tests + a manual checklist for the
user's machine.
M7: fuzz coordinates, tiny and huge screens, multi-monitor bounds.

## Done when

`xvfb-run pytest -q` green, 12/12 primitives, demo scenario 100%, replay
deterministic across 10 runs, capture ≤ 30 ms, README with real terminal output
and the Windows checklist.

## Each cycle

`~/fleet/scripts/ntfy.sh read 30` → next milestone, test first → measure →
`NOTES.md` + `STATUS.md` → `./scripts/sync.sh "agent 02: ..."` → one bus line.
