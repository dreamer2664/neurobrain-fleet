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

## M1 — 2026-10-22

- Added XGetImage full-screen and validated region capture through ctypes.
- Added monotonic nanosecond timestamps and 128×128 / 640×360 downscale helper.
- XImage storage is copied before `XDestroyImage`; 50 sequential captures complete without retained native buffers.
- Tests: **2/2 passed** at 1280×720x24.
- 50-run measurement: **median 6.360 ms, p95 10.406 ms, max 22.534 ms**, peak process RSS **33.9 MB**.
