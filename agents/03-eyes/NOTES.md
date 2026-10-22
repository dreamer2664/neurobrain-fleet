# Agent 03 Engineering Notes (`03-eyes`)

## Cycle 0 (M0) — Baseline Reproduction, Diagnostic Harness & Root-Cause Analysis

### 1. Fixed Validation Split & Baseline Numbers (`N = 1000`, `seed = 202603`, 2 CPU threads)

| Checkpoint | Params | Step | `hit_widget` | `median_err_px` | `mean_err_px` | `p90_err_px` | `action_acc` | Latency (2 thr) | Peak RSS |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| From-scratch repro (`m0_repro`) | 441,256 | 500/750 | **45.0%** (`@250: 41.8%`) | 22.56 px | 28.16 px | 69.31 px | 100.0% | 9.05 ms | 442.6 MB |
| Coordinator `ckpt-1022` (`grip_best.pt`) | 441,256 | 750 | **50.3%** | 5.37 px | 26.04 px | 69.59 px | 97.9% | 8.13 ms | 430.6 MB |

### 2. Accuracy Breakdown (From-Scratch Baseline, `N = 1000`)

- **By Role**: `icon` 35.1% (worst, 32.9px med err), `checkbox` 38.5% (33.6px), `button` 44.5% (22.6px), `menu` 44.7% (22.9px), `field` 44.8% (24.2px), `slider` 52.8% (5.2px), `tab` 54.2% (5.2px).
- **By Theme**: `dark` 45.5% (22.4px), `light` 44.5% (22.8px).
- **By Size**: `small (<500 px^2)` 43.5% (24.2px, `n=856`), `medium (500–900 px^2)` 54.2% (5.2px, `n=144`).
- **Worst Labels**: `login` 25.8%, `save` 28.3%, `pause` 30.6%, `submit` 35.5%, `archive` 38.5%.

### 3. Miss Taxonomy & Three Worst Confusions

Out of **550 misses** (from-scratch baseline; **497 misses** on `ckpt-1022`):
- **Same-role, wrong-label distractor**: **541 / 550 (98.4%)** (`ckpt-1022`: **485 / 497 = 97.6%**)
- **Wrong-role widget**: **9 / 550 (1.6%)** — all 9 are `menu -> field` (off-white RGB `(230,230,235)` vs `(245,246,250)`)
- **Near-border / background misses**: **0 / 550 (0.0%)**

**Three Worst Confusions**:
1. **Role-level**: `checkbox -> checkbox` (91 misses), `icon -> icon` (87 misses), `button -> button` (81 misses); cross-role: `menu -> field` (9 misses).
2. **Label-level**: `delete -> home` (6), `pause -> upload` (5), `pause -> settings` (5) (`ckpt-1022`: `print -> filter` 6, `save -> refresh` 5, `search -> submit` 4).
3. **Exact `(role:label)` pair**: `menu:export -> menu:help` (4), `icon:pause -> icon:settings` (3), `field:logout -> field:print` (2).

### 4. Architectural Root-Cause Diagnosis (Why Baseline Plateaus at 40–50%)

1. **Position-locked text encoder (`Flatten + Linear(48*32, 96)`)**: `{label}` appears at character offset 6 (`"press save"`), 8 (`"turn on save"`), 10 (`"click the save button"`), or 14 (`"type into the save field"`). Flattening maps identical words at different offsets to disjoint weights, while the verb at index 0 makes role/action trivial (100% action acc). Thus the model matches **role color** and guesses nearly uniformly among same-role widgets (`~1 / 2.2 ≈ 45%`).
2. **Additive `1x1` matcher & narrow effective RF**: `Conv2d(96+d, 64, 1)` lacks multiplicative query-vision conditioning (FiLM / cross-attention / cosine similarity) and has too narrow an effective receptive field around widget centers when labels are left-aligned inside wide (`55 px`) widgets.
3. **Sub-pixel bottleneck on real UIs**: Downsampling screens with 8–14 px text to `128x128` blurs small glyphs; a Stage-2 native-resolution crop refiner/re-ranker around top-K Stage-1 candidates will directly read 8–14 px text and achieve sub-4px center precision.
