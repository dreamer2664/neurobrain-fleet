# Checkpoint Card — `grip_v3` & `desktop_brain_v1` (`EyesGrounder` Open-Vocab CRNN + Autonomous Desktop & Googling Policy)

## 1. Summary & Architecture

- **Exported Checkpoints**:
  - `checkpoints/grip_v3/` (`config.json`, `weights.pt` `6.34 MB`, `weights.int8.pt` `1.67 MB`, `tokenizer.json`, `card.md`) — Open-Vocabulary + Hard Lexical/Numeric SERP + Cross-Role `EyesGrounder` (`@6350`)
  - `checkpoints/grip_v2/` — Closed-vocab Hard World foundation (`@3550`, preserved for reproducibility)
  - `checkpoints/desktop_brain_v1/` (`config.json`, `weights.pt`) — Autonomous closed-loop visuomotor desktop & search policy (`@1500`)
- **Trained From Scratch**: Yes (`0` pretrained weights, `0` external AI services, pure PyTorch CPU on 2 threads, peak training RSS `<= 1,376 MB`)
- **Parameters**:
  - `EyesGrounder` (`grip_v3`): **1,568,492** params (`Stage1CoarseNet` = **882,460** + `Stage2RefineNet` `40`-col `32x160` native BiGRU CRNN = **686,032**)
  - `DesktopBrainPolicy` (`desktop_brain_v1`): **~565,000** params (`128x128` 4x4 spatial CNN + `96`-char Goal `1D-Conv + BiGRU` + `8`-step Episodic Action-History `GRU` + `20`-way Primitive Head + Open-Vocabulary Character BIO Span Tagger)
  - **Combined Autonomous Brain**: **~2.13M parameters** (`< 8.6 MB fp32`, `< 2.6 MB int8`)

## 2. Headline Progression Across All 6 Benchmarks (2 CPU Threads)

| Benchmark / Split | Legacy `ckpt-1022` | `grip_v2` (`@3550`) | **`grip_v3` (`@6350`)** | Delta (`v3 - v2`) |
|---|---:|---:|---:|---:|
| **Hard World Seen (`N=1000`, `fp32`)** | 5.00% (`92.5px`) | 98.10% (`0.68px`) | **98.60%** (`0.68px`, `38.2ms`) | **+0.50 pts** |
| **Hard World Seen (`N=1000`, `int8`, `1.67 MB`)** | — | 98.10% (`0.68px`) | **98.60%** (`0.68px`, `39.2ms`) | **+0.50 pts** |
| **Hard World Unseen OOD (`N=500`, `fp32`)** | — | 91.40% (`0.82px`) | **96.00%** (`0.79px`) | **+4.60 pts** |
| **Hard World Unseen OOD (`N=500`, `int8`)** | — | 91.00% (`0.81px`) | **95.80%** (`0.79px`) | **+4.80 pts** |
| **Held-Out Unseen Open-Vocab Phrases (`N=250`)** | — | 25.20% (`38.4px`) | **58.80% fp32 / 59.20% int8** (`2.14px`) | **+34.00 pts** |
| **M7 60-Task Headless X11 Desktop Suite** | 1 / 60 (1.67%) | 51 / 60 (85.00%) | **60 / 60 (100.00%!)** | **+15.00 pts** |
| **M8 40-Task Multi-Window Desktop & Googling Suite** | — | 9 / 40 (22.50%) | **36 / 40 (90.00%!)** | **+67.50 pts** |
| **M10 30-Task Unscripted Autonomous X11 Goals** | — | 0 / 30 (0.00% rand) | **24 / 30 (80.00%!)** (`18/20` seen, `6/10` OOD) | **+80.00 pts** |

## 3. Live Headless X11 Breakdown (`Xvfb` + `Tkinter` + `Capture` + `DesktopHands`)

### A. M7 60-Task Desktop Suite (`scoreboard.json` — `60 / 60 = 100.00%`)
- `browser`: **12 / 12 (100.0%)** (up from `9/12 = 75.0%`)
- `editor`: **12 / 12 (100.0%)** (up from `11/12 = 91.7%`)
- `file_manager`: **12 / 12 (100.0%)** (up from `8/12 = 66.7%`)
- `recovery`: **12 / 12 (100.0%)** (`6/6 = 100.0%` runtime Rung-2 recovery rate)
- `settings`: **12 / 12 (100.0%)**
- `median_steps = 2.0`, `median_seconds = 0.227s`, `ram_peak_mb = 305.7 MB`.

### B. M8/M9 40-Task Multi-Window `MockDesktopOS` + "MiniGoogle" Search Suite (`m9_desktop_grip_v3.json` — `36 / 40 = 90.00%`)
- `desktop_nav` (desktop icons, taskbar tabs, window raise/close): **10 / 10 (100.0%)** (up from `5/10`)
- `research_workflow` (7–8 step Google -> SERP -> Copy -> Notes -> Paste -> Save): **9 / 10 (90.0%)** (up from `0/10`)
- `adversarial_desktop` (skipping Rank-1 `[ad]` traps, modal popups, stale decoys): **9 / 10 (90.0%)** (up from `1/10`)
- `google_search` (open-vocab SERP + numeric port/status/mode queries): **8 / 10 (80.0%)** (up from `3/10`)
- `median_steps = 4.0`, `median_seconds = 0.379s`, `ram_peak_mb = 308.7 MB`.

### C. M10 30-Task Unscripted Autonomous Goal Suite (`m10_unscripted_autonomous_x11.json` — `24 / 30 = 80.00%`)
- `google_lookup`: **6 / 6 (100.0%)** (including unseen OOD surface phrasings)
- `google_bookmark`: **5 / 5 (100.0%)** (including unseen OOD surface phrasings)
- `popup_then_google`: **3 / 4 (75.0%)** (includes live X11 `CLICK_BROWSER_BACK` visual self-recovery on `ug-028`)
- `terminal_to_notes`: **3 / 4 (75.0%)**
- `files_cleanup_export`: **2 / 3 (66.7%)**
- `google_to_notes`: **5 / 8 (62.5%)**

## 4. Key Engineering Findings & Remaining Failure Modes

1. **Prefix-Shortcut Discovery on SERP Lists**: Training SERP screens with 4 independent random phrases (`72.5%` on M8) let the CRNN match only the first word (`"http"`, `"chmod"`, `"sql"`). Switching to **Hard Lexical & Numeric Sibling SERP Quads** (`http 429` vs `http 503` vs `http 301` vs `http 8080`, BM25 sibling clusters, and shared-middle-word quads) lifted M8 from `72.5% -> 90.0%`, M7 from `98.3% -> 100.0%`, and Unseen Open-Vocab Phrases from `46.0% -> 58.8%`.
2. **Remaining Misses**:
   - On M8 (`4 / 40` misses: `gs-003`, `gs-006`, `rw-009`, `ad-002`): 1-digit/2-letter SERP collisions under tight `7–8pt` Xft rendering (`chmod 600` vs `chmod 755` on bright `light` theme, `http 429` vs `http 503`).
   - On M10 (`6 / 30` misses): `3` misses come from Rank-1 `[ad]` SERP clicks where `DesktopBrainPolicy`'s `4x4`-pooled `128x128` vision stem blurs small `ads.local` header text; `2` misses come from completely novel OOD verbs (`"purge ... dump"`, `"execute whoami"`) outside the character span tagger's training distribution.
