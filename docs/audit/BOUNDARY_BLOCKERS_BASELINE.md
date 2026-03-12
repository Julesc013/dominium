Status: DERIVED
Last Reviewed: unknown
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: canon-aligned documentation set for convergence and release preparation

# Boundary Blockers Baseline

Status: ARCH-REF-3 baseline
Date: 2026-02-28

## Scope

Hard boundary blockers were added to prevent architectural drift in CTRL/MOB expansion tracks.
The enforcement is tooling/build governance only and does not alter simulation semantics.

## Blocked Invariants (Hard)

- `INV-NO-DUPLICATE-GRAPH-SUBSTRATE`
- `INV-NO-DUPLICATE-FLOW-SUBSTRATE`
- `INV-NO-ADHOC-STATE-FLAG`
- `INV-NO-ADHOC-SCHEDULER`
- `INV-PLATFORM-ISOLATION`
- `INV-RENDER-TRUTH-ISOLATION`
- `INV-NO-TOOLS-IN-RUNTIME`
- `INV-NO-DIRECT-INTENT-ENVELOPE-CONSTRUCTION`

FAST profile emits `fail`; STRICT/FULL emit `refusal`.

## Whitelist and Rationale

Intent envelope construction is constrained by:
- `data/registries/intent_dispatch_whitelist.json`

Default allowed patterns are limited to net ingress/control pipeline and test harness paths.
Any non-whitelisted construction triggers `INV-NO-DIRECT-INTENT-ENVELOPE-CONSTRUCTION`.

## Build/CI Boundary Controls

- Configure-time gate:
  - `scripts/verify_build_target_boundaries.py`
- CMake target:
  - `check_build_boundaries`
- Included in:
  - `check_all`

## AuditX Upgrades

Added analyzers:
- `E109_BOUNDARY_VIOLATION_ANALYZER` (aggregates hard blocker findings)
- `E110_TOOLS_CONTAMINATION_SMELL`
- `E111_INTENT_BYPASS_SMELL`

## Developer Workflow

1. Add/change code.
2. Run boundary checks locally:
   - `python scripts/verify_build_target_boundaries.py --repo-root .`
   - `python tools/xstack/repox/check.py --profile STRICT`
3. If intent-envelope construction is required in a new canonical ingress path, update `data/registries/intent_dispatch_whitelist.json` with explicit rationale.
4. Re-run TestX boundary tests and AuditX.

## Notes

Debug-only runtime assertions are available via `DOM_BOUNDARY_DEBUG_ASSERT=1` and are disabled by default.

## Gate Snapshot (2026-02-28)

- RepoX (`STRICT`): PASS (`status=pass`, 1 warning-only finding on existing AuditX risk threshold report volume).
- AuditX (`scan --changed-only`): RUN COMPLETE.
- TestX (ARCH3 boundary subset):
  - `test_build_boundaries_enforced`: PASS
  - `test_platform_isolation`: PASS
  - `test_tools_removable`: PASS
  - `test_no_direct_intent_dispatch`: PASS
- Strict build path:
  - CMake configure with strict boundary scanner: PASS (`DOM_PLATFORM=win32`).
  - `check_build_boundaries` target: PASS.
  - `check_all`: FAIL on pre-existing unrelated `ARCH-TOP-001` (`legacy source/ or src/ directories at repo root`) in `tools/ci/arch_checks.py`.
