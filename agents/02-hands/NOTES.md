# agent 02 — hands: notes

Owner: agent 02. Repo: `~/neurobrain` (branch `agent-02`). Artifacts: here.

## M0 — twelve desktop primitives (DONE, verified 2026-10-22)

Code: `deskhands/core.py` (facade + retry-once), `deskhands/x11.py` (ctypes X11/XTest).
Commit: `ef6b0de` "agent 02: M0 desktop primitives and X11 backend".

Contract (from `specs/actions.md`, which agent 02 owns): 12 actions, each returns
`{"ok": bool, "detail": str, "duration_ms": int}`.

```
action           result   latency_ms  detail
----------------------------------------------------------------
click            GREEN             0  click sent
double_click     GREEN            40  double click sent
right_click      GREEN             0  right click sent
move             GREEN             0  move sent
drag             GREEN            23  dragged
scroll           GREEN             0  scrolled
type             GREEN             0  typed 3 chars
key              GREEN             0  chord sent
wait             GREEN             1  waited 1 ms
focus_window     GREEN             2  window not found: __expected_missing__
launch           GREEN             2  pid=2058
screen           GREEN             0  observation requested
```

12/12 green. `focus_window` proves dispatch by returning a clean
`window not found` (no WM needed under Xvfb).

Test: `tests/test_deskhands_m0.py` — 14 passed under `xvfb-run`.
- `test_twelve_actions_contract` — exact 12-tuple.
- `test_action_result_shape` — every action returns the 3-key dict.
- `test_impossible_coordinates_refused` — (-1,0),(0,-1),(1e9,0),(0,1e9) all refused.

Implementation notes (deliberate):
- Coordinates are physical pixels, origin top-left, integers. `_point()` bounds-checks
  against the root window before any XTest call → impossible coordinates raise and are
  caught by the retry wrapper, returning `ok:false`.
- `drag` interpolates 20 points between endpoints, then releases at (x2,y2).
- `scroll` maps dy>0 → button 5 (down), dy<0 → button 4 (up), one event per unit.
- `chord` presses keys in order, releases in reverse order.
- Retry: `perform()` attempts twice with a 2 ms backoff; the second attempt's exception
  is the returned detail.

## M1 — capture path (DONE, verified 2026-10-22)

Code: `deskhands/capture.py` (ctypes XGetImage, PIL decode). Commit: `c411152`
"agent 02: M1 fast X11 capture path".

Measured (Xvfb, 1280x1024, 50 full-screen captures):

| metric | value | bar | verdict |
|---|---|---|---|
| median | **8.56 ms** | ≤ 30 ms | pass |
| mean | 8.49 ms | — | — |
| max | 9.31 ms | ≤ 100 ms | pass |
| min | 7.58 ms | — | — |
| RSS delta (50 captures) | **0 KiB** | no growth | pass |

Test: `tests/test_capture_m1.py` — 2 passed under `xvfb-run`.
- `test_full_region_and_downscales` — full screen + 20x10 region; downscale to 128x128
  and 640x360.
- `test_50_captures_latency_and_no_growth` — median ≤ 30 ms, max ≤ 100 ms.

Details:
- `Screenshot` is frozen: `image` (PIL), `timestamp_ns` (monotonic_ns, captured before
  XGetImage so it precedes the read), `rect`.
- `region()` bounds-checks against the display; unsupported depths raise.
- `downscale()` static helper: 128x128 (for GripNet) and 640x360 (for the drive loop).

## M2 — demo app + scripted scenario (DONE, verified 2026-10-22)

Code: `deskhands/demo_app.py` (tkinter file-manager lookalike), `tests/test_deskhands_m2.py`.
Commit: `9c33a42` "agent 02: M2 demo app + scripted scenario".

The app has list, buttons (New/Delete/About/Quit), entry, checkbox, dialog (Toplevel),
slider (Scale), plus a draggable Canvas item used as the drag target. It is scriptable
from JSON two ways: `--script ops.json` (in-process, deterministic) and a live control
socket (`--port-file`) exposing `state` / `rects` / `script` / `quit`. `rects` reports
every widget's physical screen geometry so the X11 backend can drive the live window.

Scenario result: **20 clicks, 200 typed chars, 2 toggles, 1 drag — 100%**, driven through
`DesktopHands` (XTest) against the live window under Xvfb and asserted on the app's own
dumped state. `test_deskhands_m2.py` — 2 passed, stable across 3 repeat runs.

| assertion | measured |
|---|---|
| 20 clicks | `counters.clicks >= 20` (each XTest press counted app-wide) |
| 200 chars | `len(entry_text) == 200`, `counters.type == 200` |
| toggles | `counters.toggle == 2`, `show_hidden` False after 2 from False |
| drag | item landed at canvas (120,60) — **within 2 px** of the +100/+40 target |
| dialog | `About` opens a Toplevel, `OK` closes it |

Full deskhands suite: `test_deskhands_m0.py` + `test_capture_m1.py` + `test_deskhands_m2.py`
= **18 passed**.

Tk quirks found and worked around (worth knowing for M3–M7):
- A widget-level `<ButtonPress>`/`<B1-Motion>` bind on a `Scale` **shadows its built-in
  value-setting**. Count presses with an app-level `bind_all` instead — it runs last and
  cannot shadow. Even so, a horizontal `Scale`'s trough does not map XTest clicks to values
  reliably in this Tk 8.6/Xvfb build, so the drag target is a dedicated Canvas item.
- Clicking an `Entry` twice at the **same pixel** clears the `Listbox` selection (Tk
  behaviour). Click at distinct offsets, or assert selection before the focus click.
- An `Entry` `<ButtonRelease>` handler calling `focus_set()` **clears** the entry's focus
  (`focus_set` returns None here); a plain click already focuses the entry, so no handler.

## Next

M3: window enumeration (title, rect, pid) + focus by title substring + report focused
window + virtual-desktop bounds. 50 trials.
