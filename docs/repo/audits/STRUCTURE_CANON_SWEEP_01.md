Status: DERIVED
Last Reviewed: 2026-05-22
Supersedes: none
Superseded By: none
Stability: provisional
Task: STRUCTURE-CANON-SWEEP-01
Result: PASS_WITH_WARNINGS
Scope: repository structure canon sweep, path migration, validator reconciliation

# Structure Canon Sweep 01

## Summary

This sweep applied the user-directed structure cleanup where it could be done
without creating a new authority model or claiming unimplemented runtime
features. It kept the accepted top-level root model intact and focused on
active path debt that could be mechanically migrated with validator proof.

The sweep changed active paths for root helper shims, runtime projection/view
surfaces, and AIDE development docs. It also repaired repository gates that
still referenced the retired paths.

## Changes

- Retired root helper shims into `scripts/dev/shims/`.
- Moved the meta extension helper into `engine/foundation/meta/extensions/`.
- Reused `engine/foundation/meta/numeric.py` as the numeric discipline owner.
- Renamed active `cmake/legacy_libs/` to `cmake/libs/`.
- Moved rendered presentation code from `runtime/render/client/presentation/`
  to `runtime/projection/rendered/presentation/`.
- Moved text/TUI projection code from `runtime/ui/tui/` to
  `runtime/projection/text/`.
- Moved semantic UI IR code from `runtime/ui/ir/` to `runtime/view/ir/`.
- Moved DUI control code from `runtime/ui/dui/` to
  `runtime/ui/control/dui/`.
- Moved DUI public include paths from `runtime/ui/include/` to
  `runtime/include/`.
- Folded active AIDE docs from `docs/aide/` into `docs/development/aide/`.
- Updated RepoX rendered-projection checks to the canonical path.
- Registered the existing `INV-TOOL-NAME-ONLY` rule in the RepoX core ruleset.
- Reconciled `engine/kernel/det_invariants.h` with the active C17 build
  baseline while preserving C89-compatible deterministic source discipline.

## Determinism Header Note

`engine/kernel/det_invariants.h` previously rejected any compiler exposing
`__STDC_VERSION__ >= 199901L`. That contradicted the active repository language
baseline, which compiles C as C17 while requiring deterministic engine sources
to keep C-compatible, ABI-safe, deterministic discipline. The header now marks
the compiler mode with `D_DET_COMPILED_AS_C99_OR_LATER` instead of failing the
build solely because the active C17 baseline is in use.

This is a build-governance reconciliation, not a new engine feature. It does
not authorize C99/C17-only constructs in deterministic engine code, gameplay,
runtime package loading, provider runtime, renderer expansion, or native GUI
work.

## Validation

Targeted checks run during the sweep:

- `py -3 .aide/scripts/aide_lite.py doctor`
- `py -3 .aide/scripts/aide_lite.py validate`
- `python tools/validators/repo/check_path_terms.py --repo-root . --strict --json`
- `python tools/validators/repo/check_docs_taxonomy.py --repo-root . --strict`
- `python tools/validators/repo/check_content_layout.py --repo-root . --strict`
- `python tools/validators/repo/check_tools_taxonomy.py --repo-root . --strict`
- `python tools/validators/repo/check_workbench_module_names.py --repo-root . --strict`
- `python tools/validators/repo/check_bad_root_absence.py --repo-root . --strict`
- `python tools/validators/repo/check_dependency_directions.py --repo-root . --strict`
- `python tools/validators/repo/check_public_surface.py --repo-root . --strict`
- `python tools/validators/check_component_matrices.py --repo-root . --strict`
- `python tools/validators/platform/check_portability_matrix.py --repo-root . --strict`
- `python scripts/verify_docs_sanity.py --repo-root .`
- `python scripts/verify_build_target_boundaries.py --repo-root .`
- `python scripts/verify_ui_shell_purity.py --repo-root .`
- `python scripts/verify_abi_boundaries.py --repo-root .`
- `python tools/validators/repo/check_forbidden_root_names.py --repo-root . --strict`
- `python tools/validators/repo/check_repo_layout.py --repo-root . --strict`
- `python tools/validators/check_root_allowlist.py --repo-root . --strict`
- `python tools/validators/testing/check_test_tiers.py --repo-root . --strict`
- `python tools/validators/build/check_language_baseline.py --repo-root . --strict`
- `python tools/validators/build/check_cpp17_forbidden_library_use.py --repo-root . --strict`
- `cmake --build --preset verify --target ALL_BUILD --config Debug`
- `git diff --check`
- `git diff --cached --check`

Fast strict was run as the closeout gate and is recorded in
`.aide/reports/STRUCTURE-CANON-SWEEP-01-fast-strict.*`.

## Known Warnings

- Full CTest remains T4/full-gate debt and was not run.
- Dependency-direction strict remains PASS with known warnings and 0 violations.
- AIDE validate keeps known review-reference warnings.
- RepoX keeps the stale AuditX warning.
- Some archive/compatibility naming warnings remain advisory only.
- `check_language_baseline.py` reports known legacy projection warnings in
  `CMakePresets.json`.
- The targeted CMake build emits existing duplicate-symbol linker warnings but
  completed successfully.

## Residual Structure Debt

This sweep did not bulk-migrate every historical taxonomy issue. The following
remain better handled as dedicated follow-up tasks:

- `contracts/schema/**` still needs a guarded schema-identity route map before
  broad relocation.
- `tests/**` taxonomy drift should be migrated with test discovery and build
  references in one scoped task.
- `runtime/ui/client/**` still needs a focused route decision before moving
  live UI-client code.
- Broad content-pack re-layout should be handled with package identity and
  fixture validation, not path-only moves.

## Non-Goals Preserved

- No broad Workbench UI.
- No renderer or native GUI implementation.
- No package runtime, provider runtime, or runtime module loader.
- No gameplay/domain expansion.
- No release publication.
- No new top-level roots.

## Result

PASS_WITH_WARNINGS. The active root model remains intact, the migrated structure
paths validate, and remaining warnings are known governance or full-gate debt.
