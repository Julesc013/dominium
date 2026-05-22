# CANON-STRUCTURE-RESIDUALS-LOOP-01

Status: PASS_WITH_WARNINGS
Work class: refactor_convergence, validation_audit
Starting commit: 6e0dd93f263815667135bbf94b445c44cff6f733
Ending commit: task commit containing this audit
Branch: main

## Scope

This pass continued canonical structure convergence after
CANON_STRUCTURE_FINALIZE_NOW_01. It was limited to structure, naming,
ownership, validator, generated-map, and proof cleanup. It did not implement
runtime, product, Workbench, renderer, native GUI, gameplay, provider, module
loader, package runtime, or release behavior.

No-delete policy: retained evidence was not deleted. Historical/generated
references were preserved unless a current generated map was intentionally
regenerated.

## Worktree Status

Preflight status was clean on `main` at
`6e0dd93f263815667135bbf94b445c44cff6f733`.

During the pass, all edits stayed within canonical structure, contract,
validator, documentation, generated-map, and test-proof paths. Local evidence
was written under ignored `.dominium.local/`.

## Structure Report Source Of Truth

Fresh tracked-only local evidence was generated at:

`/.dominium.local/canon-structure-residuals-loop-01/`

Bundle contents:

- `tracked-files.txt`
- `tracked-dirs.txt`
- `tracked-roots.txt`
- `first-level-by-root.txt`
- `suspicious-active-paths-final.txt`
- `old-path-sweep-final.txt`
- `task-status-matrix.json`
- `validation-summary.md`
- `manifest.json`

`tools/validators/repo/check_structure_report_integrity.py --manifest
.dominium.local/canon-structure-residuals-loop-01/manifest.json --strict`
passed. The evidence directory remains ignored local state and was not
committed.

## Moves Performed

- `contracts/diagnostics/` -> `contracts/diagnostic/`
- `contracts/schema/astro/` -> `contracts/schema/domain/astronomy/`
- `contracts/schema/client/` -> `contracts/schema/runtime/client/`
- `contracts/schema/server/` -> `contracts/schema/runtime/server/`
- `contracts/schema/shell/` -> `contracts/schema/runtime/shell/`
- `contracts/schema/system/` -> `contracts/schema/runtime/system/`
- `contracts/schema/syscaps/` -> `contracts/schema/capability/syscaps/`
- `tests/perf/` -> `tests/performance/`

References, validators, docs, generated maps, CMake wiring, and focused tests
were updated for those routes.

## Validator Hardening

- Canonical structure validation now treats `contracts/diagnostics` as retired
  in favor of `contracts/diagnostic`.
- Canonical structure validation no longer reports the moved schema buckets as
  active legacy buckets.
- Workbench/module/workspace validation was hardened with workspace contract
  law, module implementation-path checks, and Workbench reusable-behavior
  rejection fixtures.
- `tests/performance` is wired into the test tree and no longer uses the
  retired `tests/perf` root.

## Generated Maps Regenerated

- AIDE Lite snapshot, index, context packet, repo map, and test map were
  regenerated.
- AIDE repo dependency, doc-link, inventory, ownership, orphan-candidate, and
  test maps were regenerated.
- Architecture graph bootstrap artifacts were regenerated under
  `archive/generated/architecture/` and `archive/generated/audit/`.

## Old Paths Found

The final active old-path sweep records only one finite active exception:

- `contracts/package/packs/README.md`: guard-only contract note retained by
  prior pack-authority policy; authored pack payloads remain under
  `content/packs/`.

The final suspicious active path report records one finite root-file exception:

- `sitecustomize.py`: documented by `docs/repo/ROOT_FILE_POLICY.md`.

Archive and historical mentions were not treated as active violations.

## Proof Results

| Command | Result |
| --- | --- |
| `git diff --check` | PASS |
| `py -3 -m py_compile ...` for touched Python validators/tests | PASS |
| `py -3 tools/validators/contracts/check_module_descriptors.py` | PASS |
| `py -3 tools/validators/contracts/check_workbench_workspaces.py` | PASS |
| `py -3 tools/validators/repo/check_workbench_module_names.py --strict` | PASS |
| `py -3 tools/validators/repo/check_canonical_structure.py --strict` | PASS_WITH_WARNINGS |
| `py -3 tools/validators/repo/check_structure_report_integrity.py --manifest .dominium.local/canon-structure-residuals-loop-01/manifest.json --strict` | PASS |
| `py -3 tools/validators/repo/check_path_terms.py` | PASS_WITH_WARNINGS; archive/historical info plus 3 warnings |
| `py -3 tools/validators/repo/check_bad_root_absence.py` | PASS |
| `py -3 tools/validators/check_root_allowlist.py` | PASS; strict mode not run by this wrapper |
| `py -3 .aide/scripts/aide_lite.py doctor` | PASS |
| `py -3 .aide/scripts/aide_lite.py validate` | PASS with existing review-packet evidence warnings |
| `py -3 tools/audit/review/tool_run_architecture_graph_bootstrap.py --repo-root .` | PASS with existing invalid-escape SyntaxWarnings |
| `cmake --preset verify` | PASS with known SDL/PkgConfig warnings |
| `cmake --build --preset verify --target ALL_BUILD` | PASS with known duplicate-symbol warnings |
| `ctest --preset verify -R "capability_matrix\|capability_regression" --output-on-failure` | PASS |
| `ctest --preset verify -R "exploration_scaling\|interaction_scaling\|signal_scaling" --output-on-failure` | PASS |
| `ctest --preset verify -L smoke --output-on-failure` | PASS |
| `py -3 tools/xstack/repox/check.py --repo-root . --profile STRICT` | Attempted; produced no result for several minutes and was terminated |

Full CTest was not run in this residual pass because the requested proof level
was focused residual cleanup and smoke/capability proof already covered the
changed structure routes.

## Remaining Warnings

`check_canonical_structure.py --strict` still reports:

- `apps/workbench/shell` missing.
- `contracts/schema/engine` and `contracts/schema/meta` remain focused schema
  taxonomy debt.
- Runtime projection roots `runtime/projection/cli`,
  `runtime/projection/headless`, and `runtime/projection/native` are absent.
- `runtime/ui/client` remains a finite exception pending a focused runtime UI
  versus app-client ownership decision.
- `sitecustomize.py` remains a documented root bootstrap exception.
- Several first-level test roots remain proof-taxonomy debt and require a
  focused tests taxonomy pass.

Known duplicate-symbol linker warnings remain unchanged from prior proof.

## Feature Readiness

Feature readiness: LIMITED.

The root model and several high-value canonical routes are tighter, smoke proof
passes, and package/runtime/product implementation remains intentionally
unchanged. Broad feature work should still avoid the remaining schema taxonomy,
runtime projection, Workbench shell, and tests taxonomy warning areas until
their focused cleanup passes complete.

## Next Recommended Run

Run the next residual pass on:

1. `contracts/schema/engine` and `contracts/schema/meta` routing.
2. Runtime projection root completion or documented absence policy.
3. Workbench shell root creation only if real shell content exists.
4. Focused tests proof-taxonomy routing.
5. RepoX STRICT investigation with a bounded timeout/reporting wrapper.
