# agent 01 — runtime & integration: STATUS

**M0–M8 all done** (2026-10-22, cycles 1–10; M4 landed before M3 by design).
brainbox 0.8.0 · code `neurobrain@agent-01` · **64/64 tests**
(`artifacts/tests_m8.txt`). All 8 CLI verbs implemented; no fake commands left.

| milestone | headline number | artifact |
|---|---|---|
| M0 skeleton/doctor/bench | boot 1.003 s · peak 272 MB (real LM 4600) | `bench_m0_real.json` |
| M1 local API :8321 | 200 req → RSS +0.3 MB · /health max 9.1 ms | `api_m1_stress.json` |
| M2 checkpoint dirs | both .pt migrated, sha≡release, predictions 20/20 | `migration_m2.json` |
| M3 drive loop | closed 10/10 · terminal 0.70 oracle / 0.60 real | `drive_m3.json` |
| M4 undo/trash | 100/100 cycles byte-identical | `undo_m4.json` |
| M5 packaging | clean venv install 28.4 s < 60 · zipapp 212 KB | `packaging_m5.json` |
| M6 watch/autostart/crash | kill -9 recovery 9/9 checks | `crash_m6.json` |
| M7 int8 + governor | disk 0.28× · loss Δ +0.0005 · max peak 344 MB ≤ 3000 | `quant_m7.json` |
| M8 20-task suite | **success 0.80** (16/20) · peak 296 MB | `scoreboard_m8.json` |

Honest edges, all documented in NOTES.md rather than buried: M8's suite is
agent-01-authored (03's Xvfb suite still pending) and runs on the simulated
desktop — no X server exists in this sandbox; int8 is slower and RSS-neutral
at 4.25M params so fp32 stays default; the LM planner occasionally succeeds
for the wrong reason and GripNet's same-role confusion (0/2 browser tasks)
is the top failure class — that's 03's hill, the loop handles it cleanly.

Clean-clone path: `git clone` → `brainbox doctor && brainbox bench &&
brainbox run "…"` all work (stub fallback, flagged) — real weights via
`bash scripts/restore_data.sh` + `scripts/migrate_checkpoint.py --int8`.
Real terminal transcript: `artifacts/cleanclone_m8.txt`.

Next for agent 01: when 02's capture + 03's suite/grounder land, wire
RealDesktopWorld (deskhands + real frames behind the same World protocol)
and re-run this scoreboard on real pixels.
