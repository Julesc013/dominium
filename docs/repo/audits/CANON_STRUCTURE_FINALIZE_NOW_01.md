Status: DERIVED
Last Reviewed: 2026-05-22
Supersedes: queued structure cleanup prompts for this bounded pass
Superseded By: none
Result: PASS_WITH_WARNINGS
Stability: provisional
Task: CANON-STRUCTURE-FINALIZE-NOW-01

# CANON-STRUCTURE-FINALIZE-NOW-01

## Status

PASS_WITH_WARNINGS.

This pass completed a safe, independently valid subset of the requested
canonical structure finalization. It removed the clear legacy test proof buckets,
updated active references, refreshed architecture structure maps, added
structure/report validators, and proved the changed subset with build, smoke,
and targeted TestX validation.

Full repository finalization remains incomplete because deeper schema, runtime,
Workbench, and test taxonomy debt is still active and needs focused routing
tasks with compatibility review.

## Baseline

- Starting commit: `3fdd78a3bf7bac5c7369ac264a4e83b215dd1bdd`
- Branch: `main`
- Initial worktree status: clean
- Ending commit: the commit containing this audit; final response records the
  concrete hash after commit creation.

## Scope

The pass was limited to tracked repo structure, structure evidence, validators,
test taxonomy moves with clear routes, active reference updates, generated
architecture maps, and audit evidence.

No product/runtime behavior was intentionally changed. No source identity,
schema identity, pack identity, replay identity, ABI, or save identity was
renamed.

## No-Delete Policy

No tracked evidence or source files were deleted. Tracked test files were moved
with `git mv`. Generated AuditX output created under `docs/audit/` by validation
was moved into ignored local evidence under:

` .dominium.local/canon-structure-finalize-now-01/`

That local output is not committed.

## Move Phases Completed

Clear legacy test buckets were routed to canonical proof taxonomy targets:

- `tests/app/` -> `tests/apps/`
- `tests/control/` -> `tests/runtime/control/`
- `tests/data_1/` -> `tests/contract/data1/`
- `tests/renderer/` -> `tests/runtime/render/`
- `tests/schema/` -> `tests/contract/schema/`
- `tests/share/` -> `tests/packaging/share/`
- `tests/systemic/` -> `tests/integration/systemic/`
- `tests/testx/` -> `tests/tools/testx/`
- `tests/tourist/` -> `tests/integration/tourist/`
- `tests/ui_parity/` -> `tests/runtime/ui/parity/`

Active references in CMake, docs, contracts, scripts, validators, and tests were
updated for those moves.

## Structure Report Integrity

No tracked `dirfiles_manifest.json`, `dir_tree.json`, `dir_tree.txt`,
`dirfiles.zip`, or `dirfiles_run.log` bundle was present at the start of this
pass.

Added:

- `docs/repo/structure_report_integrity.md`
- `tools/validators/repo/check_structure_report_integrity.py`

Local tracked-only structure export was generated under ignored local evidence
with manifest hashes.

## Generated Maps Regenerated

The architecture graph bootstrap generator was run with UTF-8 output:

`py -3 tools/audit/review/tool_run_architecture_graph_bootstrap.py --repo-root .`

Result:

- `result`: `complete`
- module count: `2356`
- include edge count: `41658`
- symbol count: `51547`
- architecture fingerprint:
  `7ad8e2cdf021b7c96446abb471bb4b592854415d695c3df814eeda7dc6afe9d2`

Generated architecture artifacts and reports were refreshed. The generator
emitted pre-existing Python string escape warnings in unrelated files; those
warnings were not changed by this structure pass.

## Validators Added

Added:

- `tools/validators/repo/check_canonical_structure.py`
- `tools/validators/repo/check_structure_report_integrity.py`

Updated:

- `tools/validators/repo/README.md`

`check_canonical_structure.py --strict` fails hard on clear retired active
paths and tracked generated/local roots. Remaining taxonomy debt is reported as
warnings unless `--strict-final` is used.

## Proof Results

Passing proof:

- `py -3 -m py_compile <changed Python files>`: PASS
- `py -3 .aide/scripts/aide_lite.py doctor`: PASS
- `py -3 .aide/scripts/aide_lite.py validate`: PASS with existing review-ref
  warnings
- `py -3 tools/validators/check_root_allowlist.py --repo-root . --strict --json`:
  PASS
- `py -3 tools/validators/repo/check_bad_root_absence.py --repo-root . --strict --json`:
  PASS
- `py -3 tools/validators/repo/check_forbidden_root_names.py --repo-root . --strict --json`:
  PASS_WITH_WARNINGS, archive/name warnings only
- `py -3 tools/validators/repo/check_no_src_source_dirs.py --repo-root . --strict --json`:
  PASS_WITH_WARNINGS, archive-only `src/source` findings
- `py -3 tools/validators/repo/check_docs_taxonomy.py --repo-root . --strict --json --max-findings 50`:
  PASS
- `py -3 tools/validators/repo/check_tools_taxonomy.py --repo-root . --strict --json --max-findings 50`:
  PASS
- `py -3 tools/validators/repo/check_content_layout.py --repo-root . --strict --json --max-findings 50`:
  PASS
- `py -3 tools/validators/repo/check_workbench_module_names.py --repo-root . --strict --json --max-findings 50`:
  PASS
- `py -3 tools/validators/repo/check_canonical_structure.py --repo-root . --strict --json`:
  PASS_WITH_WARNINGS, no hard blockers
- `py -3 tools/validators/repo/check_structure_report_integrity.py --repo-root . --json`:
  PASS
- `py -3 tests/tools/testx/capability_matrix_contracts.py --repo-root .`:
  PASS
- `py -3 tests/apps/workbench_validation_slice_tests.py`: PASS
- `py -3 tests/contract/schema/schema_taxonomy_validator_tests.py`: PASS
- `ctest --preset verify -R "capability_matrix|capability_regression" --output-on-failure`:
  PASS, 47/47
- `cmake --preset verify`: PASS
- `cmake --build --preset verify --target ALL_BUILD`: PASS with known duplicate
  symbol warnings
- `ctest --preset verify -L smoke --output-on-failure`: PASS, 57/57
- `git diff --check`: PASS

Unavailable:

- `py -3 -m tools.aide.doctor`: unavailable, no `tools.aide.doctor` module
- `py -3 -m tools.aide.validate`: unavailable, no `tools.aide.validate` module

RepoX/full-suite status:

- `py -3 scripts/ci/check_repox_rules.py --repo-root . --profile STRICT`:
  FAIL due pre-existing stale AuditX/identity evidence and missing status
  headers in earlier AIDE audit files.
- `ctest --preset verify --output-on-failure`: attempted, then stopped as an
  impractical gate for this pass after long-running AuditX checks and unrelated
  failures. Attributable TestX path failures from the move were repaired and
  reproved with the 47-test targeted TestX CTest selection.

## Warnings Preserved

Known preserved warnings/debt:

- SDL/CMake deprecation and missing `PkgConfig` messages during configure.
- Duplicate symbol link warnings in `domino_engine` remained unchanged.
- RepoX STRICT remains blocked by pre-existing stale AuditX/identity evidence
  and prior AIDE audit status headers.
- Full CTest has existing unrelated failures, including phase6 audit/CI matrix,
  process-only mutation, workspace isolation, missing legacy schema paths, Omega
  plan path debt, old FAB/tool script path debt, and related invariant failures.
- `runtime/ui/client/` remains a finite documented exception pending a focused
  route decision.
- `contracts/schema/tool/` remains a finite schema taxonomy exception.
- `sitecustomize.py` remains a documented root-file exception.

## Ambiguous Or Deferred Paths

Deferred rather than moved in this pass:

- `runtime/ui/client/`: documented reusable UI-facing systems; routing between
  shared runtime UI and app-local client glue needs focused review.
- `apps/workbench/shell/`: absent; Workbench has `module/` and `workspace/`
  content, but no shell content to move safely.
- `contracts/diagnostic/`: absent; existing active root is
  `contracts/diagnostics/`. Moving or aliasing singular/plural diagnostic law
  needs a compatibility decision.
- `runtime/projection/cli/`, `runtime/projection/native/`,
  `runtime/projection/headless/`: absent; no implementation content was created
  solely to satisfy grammar.
- Legacy schema buckets such as `contracts/schema/astro`,
  `contracts/schema/client`, `contracts/schema/engine`, `contracts/schema/meta`,
  `contracts/schema/server`, `contracts/schema/shell`,
  `contracts/schema/syscaps`, and `contracts/schema/system`.
- Remaining non-final test roots such as `tests/ai`, `tests/authority`,
  `tests/bugreport`, `tests/contentlib`, `tests/coverage`, `tests/demo`,
  `tests/determinism`, `tests/distribution`, `tests/engine`,
  `tests/entitlement`, `tests/fab`, `tests/game`, `tests/invariant`,
  `tests/launcher`, `tests/operations`, `tests/perf`, `tests/piracy_containment`,
  `tests/platform`, `tests/playtest`, `tests/regression`, `tests/server`,
  `tests/contract/service/services_expiry`, `tests/setup`, `tests/signal`, and `tests/ux`.

## Non-Goals Preserved

This pass did not implement runtime package mounting, provider runtime, runtime
module loading, Workbench shell, renderer/native GUI, gameplay/domain runtime,
release publication, automatic branch automation, automatic promotion, or a
repair engine.

## Remaining Exceptions

The hard active top-level root allowlist passes. No forbidden top-level active
root is tracked.

Finite exceptions and deferred debt remain as warning-level findings in:

`py -3 tools/validators/repo/check_canonical_structure.py --repo-root . --strict --json`

## Feature-Readiness Verdict

LIMITED.

The clearest structure churn in the test proof taxonomy is resolved and
validated. Real feature work is safer than before for affected test and TestX
surfaces, but broad feature readiness is still limited by remaining schema
taxonomy debt, Workbench shell absence, runtime projection gaps, RepoX strict
evidence debt, and full CTest failures unrelated to this pass.

## Next Recommended Task

Run a focused checkpoint repair task for RepoX/full-suite debt before declaring
large-scale feature readiness:

`CANON-STRUCTURE-FULL-GATE-REPAIR-01`

Suggested scope:

- Repair stale RepoX/AuditX/identity evidence.
- Add or route missing status headers in older AIDE audit docs.
- Classify or repair full CTest invariant failures unrelated to this structure
  pass.
- Decide the `contracts/diagnostic` versus `contracts/diagnostics` compatibility
  route.
- Split remaining non-final test roots by proof type in smaller safe batches.
