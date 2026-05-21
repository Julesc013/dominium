Status: DERIVED
Last Reviewed: 2026-05-21
Supersedes: none
Superseded By: none
Task: FOUNDATION-REPAIR-DEPENDENCY-DIRECTION-01
Result: PASS

# FOUNDATION-REPAIR-DEPENDENCY-DIRECTION-01 Audit

## Status

FOUNDATION-REPAIR-DEPENDENCY-DIRECTION-01 repaired the dependency-direction strict blocker from `FOUNDATION-CLOSEOUT-01`.

Baseline blocker:

- `358` dependency-direction violations.
- `38` warnings.

Final dependency-direction strict result:

- PASS.
- `0` violations.
- `68` warnings.
- `16579` files scanned.

## Repairs

- Moved reusable deterministic helper ownership away from `tools` into engine/runtime-owned namespaces.
- Removed newly tracked `engine -> game` helper violations by localizing state-vector substrate support and removing game-domain reference evaluators from the engine namespace.
- Removed newly tracked `runtime -> tools` helper violations by adding runtime-owned build-id support, inlining runtime shim stability marker construction, and keeping validation shims tools-owned.
- Added exact provisional dependency-direction exceptions for remaining transitional app/runtime tool adapter edges.

## Exceptions

The exception ledger contains `12` active provisional entries created for this repair. They apply to `28` import edges.

All entries are path/from/to/edge scoped, owner-declared, and retire by `FOUNDATION-REPAIR-DEPENDENCY-DIRECTION-02`.

No broad allow edge was added.

## Validation

- Dependency-direction strict: PASS.
- AIDE doctor/validate/test/selftest/tools/roots/repo: PASS.
- Repo layout/root/distribution/component validators: PASS.
- Foundation contract validators: PASS.
- RepoX STRICT: PASS with stale AuditX warning.
- FAST strict: PASS, `32` commands, `312.147` seconds.
- CMake configure/build: PASS through FAST strict.
- Smoke CTest: PASS through FAST strict.

Full CTest was not run and remains T4/full-gate debt.

## Readiness

Foundation Lock is ready to be rerun by `FOUNDATION-CLOSEOUT-02`.

This task does not authorize `WORKBENCH-VALIDATION-SLICE-01` directly. Workbench and broad feature work remain blocked until Foundation closeout passes.
