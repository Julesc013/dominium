Status: DERIVED
Last Reviewed: 2026-02-07
Supersedes: none
Superseded By: none

# BR-0 Baseline Entry Checks

This report records the baseline gate checks required before BR-0 work.

Commands run:
1) RepoX:
   `python scripts/ci/check_repox_rules.py --repo-root .`
   - First attempt timed out at 14s.
   - Re-run with extended timeout: PASS.
2) Build (C89/C++98 targets):
   `cmake --build build\msvc-base --config Debug --target domino_engine dominium_game`
   - PASS.
3) TestX partial checks:
   `ctest -C Debug -R determinism` (in `out/build/vs2026/verify`) - PASS.
   `ctest -C Debug -R schema` (in `out/build/vs2026/verify`) - PASS.

Notes:
- RepoX timing suggests the default gate timeout should allow >30s on this machine.
