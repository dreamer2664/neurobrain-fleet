# spec: desktop primitives (owner: agent 2)

Twelve actions. Coordinates are **physical pixels on the real screen**, origin
top-left, integers. Agent 2 implements them; agent 8 emits them; agent 3 predicts
`click` targets in this same pixel space.

| type | fields | semantics |
|---|---|---|
| `click` | x, y, button="left", clicks=1 | move, press, release at x,y |
| `double_click` | x, y | two clicks < 250 ms apart |
| `right_click` | x, y | context menu click |
| `move` | x, y | pointer move, no button |
| `drag` | x, y, x2, y2, ms=600 | press at x,y, move, release at x2,y2 |
| `scroll` | x, y, dy | wheel at x,y; dy>0 scrolls down |
| `type` | text | unicode text into focused element |
| `key` | keys=[...] | chord, e.g. ["ctrl","s"], ["win","e"], ["alt","tab"] |
| `wait` | ms | sleep, then observe |
| `focus_window` | title_substr | raise + focus a window by title |
| `launch` | command | start a process, return pid |
| `screen` | — | no-op; capture observation only |

Implementation notes:

- Linux: X11 via `ctypes` (libX11 + libXtst). Must work under Xvfb for tests.
- Windows: `ctypes.windll.user32` (`SendInput`, `SetCursorPos`), DPI-aware.
- macOS: Quartz `CGEventCreateMouseEvent` via `ctypes`.
- Every action returns `{"ok": bool, "detail": str, "duration_ms": int}`.
- No shelling out to `xdotool` or `pyautogui`; own implementation, dependency-free.
