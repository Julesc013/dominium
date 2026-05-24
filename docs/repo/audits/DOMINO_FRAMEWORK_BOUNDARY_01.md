Status: DERIVED
Last Reviewed: 2026-05-24
Supersedes: none
Superseded By: none
Result: PASS_WITH_WARNINGS
Task: DOMINO-FRAMEWORK-BOUNDARY-01
Date: 2026-05-24
Branch: main
Starting Commit: 39d262ff0afed6edf8df76408380f1dc91fbf894
Ending Commit: pending; see task commit

# DOMINO-FRAMEWORK-BOUNDARY-01 Audit

## Goal

Capture the Domino Framework idea without adding a top-level `framework/`,
`profiles/`, `labs/`, `modules/`, `plugins`, `services/`, or `sdk/` source root.

## Changes

- Added `docs/architecture/domino_framework_boundary.md`.
- Added `tools/validators/repo/check_domino_framework_boundary.py`.
- Added `tests/integration/domino_framework_boundary_validator_tests.py`.
- Registered the validator in `tests/integration/CMakeLists.txt`.
- Documented `content/profiles/` as authored runtime/user/game profile payloads.
- Tightened `check_canonical_structure.py` and `check_provider_structure.py` so
  `framework` and `sdk` are blocked by focused root guardrails.
- Narrowed public-surface header entries to:
  - `engine/include/domino`
  - `runtime/include/domino`
  - `game/include/dominium`

## Boundary Verdict

Domino Framework is defined as:

```text
contracts/public_surface
contracts/abi
contracts/service
contracts/provider
contracts/capability
engine/include/domino
runtime/include/domino
release/profiles
tests/conformance and validators
```

The current Domino reference implementation remains in `engine/` and `runtime/`.
The current Dominium product implementation remains in `game/`, `content/`, and
`apps/`.

## Non-Goals Preserved

- No new top-level source roots were created.
- No active source directories were moved.
- No runtime provider loader, package runtime, module loader, Workbench shell,
  renderer, native GUI, gameplay, or release publication work was implemented.
- `runtime/provider/suite/` was documented as an optional helper location only;
  it was not created because no shared suite helper implementation exists yet.

## Validation

Validation run:

```text
python tools/validators/repo/check_domino_framework_boundary.py --repo-root . --strict
python tests/integration/domino_framework_boundary_validator_tests.py --repo-root .
python -m py_compile tools/validators/repo/check_domino_framework_boundary.py tests/integration/domino_framework_boundary_validator_tests.py tools/validators/repo/check_canonical_structure.py tools/validators/repo/check_provider_structure.py
git diff --check
python tools/validators/repo/check_public_surface.py --repo-root . --strict
python tools/validators/repo/check_canonical_structure.py --repo-root . --strict
python tools/validators/repo/check_provider_structure.py --repo-root . --strict
python tools/validators/check_root_allowlist.py --repo-root . --strict
python tools/validators/repo/check_bad_root_absence.py --repo-root . --strict
python .aide/scripts/aide_lite.py doctor
python .aide/scripts/aide_lite.py validate
python tools/validators/repo/check_full_gate_legacy_paths.py --repo-root . --strict
python tools/validators/testing/check_test_tiers.py --repo-root . --strict
python scripts/ci/check_repox_rules.py --repo-root . --profile STRICT
cmake --preset verify
cmake --build --preset verify --target ALL_BUILD
ctest --preset verify -R "domino_framework_boundary_validator_tests" --output-on-failure
ctest --preset verify -L smoke --output-on-failure
python tools/test/run_fast_strict.py --repo-root .
```

Results:

- New framework-boundary validator: PASS.
- New validator fixture test: PASS.
- Public-surface, canonical-structure, root-allowlist, bad-root, AIDE, full-gate
  legacy path, and test-tier checks: PASS.
- Provider structure: PASS_WITH_WARNINGS for the pre-existing storage/package
  provider split-pending warnings.
- CMake configure/build: PASS, with pre-existing duplicate-symbol linker
  warnings.
- Smoke CTest: PASS, 57/57.
- RepoX STRICT and fast strict: fail only on pre-existing stale AuditX/identity
  fingerprint evidence and launcher pack-verification marker debt; the
  `INV-CANON-INDEX` and `INV-DOC-STATUS-HEADER` findings introduced during this
  task were repaired.

## Remaining Warnings

- Public header surfaces are still provisional, not frozen ABI.
- Full CTest remains T4 proof debt from `FULL-CTEST-AUDIT-NONPATH-01`; this task
  does not claim release readiness.
- RepoX retains pre-existing stale generated-evidence and launcher
  pack-verification failures.

## Feature Readiness

LIMITED. The framework boundary is clearer, but broad feature work remains
blocked by Foundation Lock policy.
