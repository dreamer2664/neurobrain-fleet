# Agent 02 notes

## M0 — 2026-10-22

- Added `deskhands` facade and direct ctypes X11/XTest backend.
- Implemented all 12 action dispatch paths with stable `{ok, detail, duration_ms}` results and one internal retry.
- Input primitives reject coordinates outside physical display bounds.
- Drag uses 20 interpolated points; launch returns PID; focus recursively searches X windows.
- Added contract tests before implementation.

Measured under Xvfb: **14 tests passed in 0.11 s; selftest 12/12 green**.

```text
action           result   latency_ms
click            GREEN             0
double_click     GREEN            40
right_click      GREEN             0
move             GREEN             0
drag             GREEN            23
scroll           GREEN             0
type             GREEN             0
key              GREEN             0
wait             GREEN             1
focus_window     GREEN             3
launch           GREEN             0
screen           GREEN             0
```

Focus selftest intentionally exercises the clean not-found path because bare Xvfb has no window manager/client. Full trial coverage belongs to M3.
