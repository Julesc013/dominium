Status: DERIVED
Last Reviewed: 2026-02-07
Supersedes: none
Superseded By: none

# BR-0 Rerun Sequence (Post-Blocker)

This is the ordered prompt rerun plan starting at the first blocked prompt.
Do not execute prompts out of order.

## Entry checks (before each prompt)

Run these checks and require PASS:

1) RepoX:
   - `python scripts/ci/check_repox_rules.py --repo-root .`
2) TestX full gate:
   - `cmake --build out/build/vs2026/verify --config Debug --target testx_all`
3) Header compile sanity (optional if TestX already ran):
   - `ctest --test-dir out/build/vs2026/verify -C Debug -R public_header_c89_compile --output-on-failure`
   - `ctest --test-dir out/build/vs2026/verify -C Debug -R public_header_cpp98_compile --output-on-failure`

If any check fails: STOP and fix before running the prompt.

## Prompt sequence (in order)

1) POST-CANON L2 — Deterministic schema versioning and migration
2) POST-CANON L3 — Capability-stage gating enforcement
3) POST-CANON L4 — Stage-by-stage TestX matrix and anti-creep regression
4) IVRH prompts (integration, validation, real-world hardening)
5) Freecam/observation/cheat-model enforcement prompt
6) Universal Complexity Framework prompt (“THIS IS THE BIG ONE”)

## Between prompts

After each prompt execution:
- Run RepoX and full TestX (commands above).
- Only proceed if both are green.
