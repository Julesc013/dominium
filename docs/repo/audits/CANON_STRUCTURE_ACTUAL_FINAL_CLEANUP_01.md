Status: DERIVED
Last Reviewed: 2026-05-23
Supersedes: CANON_STRUCTURE_RESIDUALS_LOOP_02
Superseded By: none
Result: PASS_WITH_WARNINGS
Stability: provisional
Task: CANON-STRUCTURE-ACTUAL-FINAL-CLEANUP-01

# Canon Structure Actual Final Cleanup 01

## Summary

This pass performed actual tracked structure routing, not only validator work.
The active tracked source tree now passes the canonical structure hard gate and
the generated local tracked-only structure export reports no suspicious active
paths.

Feature readiness verdict: LIMITED.

Reason: fast strict, CMake verify/build, smoke CTest, and targeted capability
tests pass. Full CTest remains a full-gate blocker because unrelated legacy/full
suite tests still expect old roots such as `game/rules`, `contracts/schemas`,
`data/profiles`, `libs/appcore`, and missing full-gate docs/assets.

## Baseline

- Branch: `main`
- Starting commit: `52ac5707e8225d3db4300918d205423ac7b02918`
- Ending commit: this cleanup commit; see git log after commit creation
- Initial worktree state: dirty with prior incomplete structure/provider/AIDE
  cleanup output, classified as current/prior structure work and included in
  this commit candidate
- Structure evidence source:
  `.dominium.local/canon-structure-actual-final-cleanup-01/`
- Changed files in staged candidate: 428
- Git rename entries in staged candidate: 275

## Primary Moves

- Renamed `engine/compatx/` to `engine/compatibility/`.
- Retired `runtime/compatx/` to `archive/legacy/runtime/compatx/`.
- Renamed active Dominium UI implementation paths:
  - `runtime/ui/control/dui/` to `runtime/ui/control/domui/`
  - `runtime/include/dui/` to `runtime/include/domino/ui/dui/`
  - `runtime/platform/win32/ui/dui/` to `runtime/platform/win32/ui/domui/`
  - `runtime/platform/win32/ui/include/dui/` to
    `runtime/platform/win32/ui/include/domui/`
- Routed legacy test roots:
  - `tests/ops/` to `tests/operations/`
  - `tests/services/` to `tests/contract/service/services_expiry/`
- Routed 130+ `contracts/schema` residuals into canonical taxonomy buckets:
  - domain: `civilization`, `fluids`, `geology`, `network`
  - game: `agents`, `economy`, `law`, `life`, `world`, `worldgen`
  - repo: `authority`
  - runtime: `control`, `engine/core`, `network`, `render`, `server`,
    `session`, `time`, `ui`
- Added README-guarded ownership boundaries:
  - `apps/workbench/shell/`
  - `runtime/projection/cli/`
  - `runtime/projection/headless/`
  - `runtime/projection/native/`

## Provider And Profile Structure

- Added provider plan registry:
  `contracts/provider/provider_plans.registry.json`.
- Added release provider profiles:
  - `release/profiles/dev/client.raylib.toml`
  - `release/profiles/dev/client.sdl2_opengl33.toml`
  - `release/profiles/dev/workbench.raylib.toml`
  - `release/profiles/dev/server.null.toml`
- Added third-party/provider validators:
  - `tools/validators/third_party/check_vendor_manifest.py`
  - `tools/validators/third_party/check_forbidden_includes.py`
  - `tools/validators/provider/check_provider_manifest.py`
  - `tools/validators/provider/check_provider_conformance.py`
- Preserved service-first provider doctrine: provider choice lives in provider
  records/profiles, not app path identity.

## Validators And Maps

- Extended `tools/validators/repo/check_structure_report_integrity.py` to write
  task-local tracked-only evidence files:
  `tracked-files.txt`, `tracked-dirs.txt`, `tracked-roots.txt`,
  `first-level-by-root.txt`, old-path sweeps, validation summary,
  task-status matrix, report manifest, and report integrity notes.
- Added `tools/validators/repo/check_schema_taxonomy.py` to block the retired
  schema buckets and flat schema prefixes routed by this pass.
- Updated canonical structure, provider structure, structure residual, RepoX,
  AIDE context, root migration, and architecture registry evidence to the new
  paths.
- Refreshed AIDE Lite snapshot, index, and map artifacts.

## Active Old Path Result

The tracked-source sweep is clear for these old active paths:

- `runtime/compatx`
- `runtime/ui/control/dui`
- `runtime/include/dui`
- `runtime/platform/win32/ui/dui`
- `runtime/platform/win32/ui/include/dui`
- `tests/ops`
- `tests/services`
- `contracts/schema/agents`
- `contracts/schema/authority`
- `contracts/schema/economy`
- `contracts/schema/law`
- `contracts/schema/life`
- `contracts/schema/session`
- `contracts/schema/time`
- `contracts/schema/ui`
- `contracts/schema/world`
- `contracts/schema/worldgen`

`suspicious-active-paths.txt` reports `none`.

## Retained Warnings

- `.aide/` state-like roots remain classified as tracked AIDE
  control-plane/evidence roots.
- Some `content/packs/**/content/` payload roots remain classified legacy pack
  layout pending `PACK-INTERNAL-LAYOUT-CANON-01`; no pack IDs or content hashes
  were silently changed.
- `contracts/schema` still has broad first-level buckets outside this pass's
  safely routed residual set.
- `engine/foundation`, `engine/serialization`, `engine/session`,
  `runtime/serialization`, and `runtime/session` remain classified residuals.
- Provider registry warnings remain for storage/package validator descriptors
  whose implementation paths are service paths pending a later provider split.
- Service conformance warnings remain for fixture/planned conformance records.
- Public header ABI warnings remain legacy/public-promotion debt.
- Dependency-direction warnings remain existing exception/unlisted dependency
  debt; strict mode passes with zero violations.

## Full CTest Status

Full CTest was attempted with:

```text
ctest --preset verify --output-on-failure
```

It was stopped after no further progress while already failing multiple
unrelated full-gate checks. Observed failures included:

- missing `docs/testing/ci/CI_ENFORCEMENT_MATRIX.md`
- hardcoded-name slice checks for Earth/Sol/Milky Way tokens
- missing `docs/architecture/TRANSITION_PLAYBOOK.md` token `c abi spine`
- missing `capability_baseline.schema`
- missing `modpack_cli.py`
- old `data/profiles` expectations
- old docs/runtime roots such as `docs/app`, `docs/platform`, `docs/render`,
  `runtime/app`, and `docs/repox`
- old schema/test references such as `contracts/schemas`, `game/rules`,
  `tools/schema_migration`, `libs/appcore`, and `srz_fields.h`
- frozen contract hash mismatches from pre-existing architecture docs
- process-only mutation and capability-scope invariant failures outside this
  structure cleanup scope

These failures are not fixed here because doing so would require either
recreating retired roots or changing broad full-gate doctrine outside this
cleanup task.

## Proof

| Command | Result |
| --- | --- |
| `git status --short` | PASS, dirty state classified before cleanup |
| `git rev-parse --abbrev-ref HEAD` | `main` |
| `git rev-parse HEAD` | `52ac5707e8225d3db4300918d205423ac7b02918` |
| `git log --oneline -30` | inspected |
| `python tools/validators/repo/check_structure_report_integrity.py --repo-root . --write-bundle .dominium.local/canon-structure-actual-final-cleanup-01 --strict` | PASS |
| `python tools/validators/repo/check_canonical_structure.py --repo-root . --strict` | PASS |
| `python tools/validators/repo/check_schema_taxonomy.py --repo-root . --strict` | PASS |
| `python tools/validators/repo/check_provider_structure.py --repo-root . --strict` | PASS_WITH_WARNINGS |
| `python tools/validators/third_party/check_forbidden_includes.py --repo-root . --strict` | PASS |
| `python tools/validators/third_party/check_vendor_manifest.py --repo-root . --strict` | PASS |
| `python tools/validators/provider/check_provider_manifest.py --repo-root . --strict` | PASS_WITH_WARNINGS |
| `python tools/validators/provider/check_provider_conformance.py --repo-root . --strict` | PASS_WITH_WARNINGS |
| `python tools/validators/repo/check_structure_residuals.py --repo-root . --strict` | PASS_WITH_WARNINGS |
| `python tools/validators/repo/check_content_layout.py --repo-root . --strict` | PASS |
| `python tools/validators/repo/check_tools_taxonomy.py --repo-root . --strict` | PASS |
| `python tools/validators/repo/check_docs_taxonomy.py --repo-root . --strict` | PASS |
| `python tools/validators/repo/check_workbench_module_names.py --repo-root . --strict` | PASS |
| `python tools/validators/repo/check_dependency_directions.py --repo-root . --strict` | PASS_WITH_WARNINGS |
| `python tools/validators/repo/check_public_surface.py --repo-root . --strict` | PASS |
| `python tools/validators/check_root_allowlist.py --repo-root .` | PASS |
| `python tools/validators/check_component_matrices.py` | PASS |
| `python tools/validators/check_distribution_layout.py` | PASS |
| `python tools/validators/repo/check_no_src_source_dirs.py --repo-root . --strict` | PASS_WITH_WARNINGS |
| `python tools/validators/repo/check_forbidden_root_names.py --repo-root . --strict` | PASS_WITH_WARNINGS |
| `python tools/validators/repo/check_bad_root_absence.py --repo-root . --strict` | PASS |
| `python tools/validators/contracts/check_command_result_view.py` | PASS |
| `python tools/validators/contracts/check_document_patch_transaction.py` | PASS |
| `python tools/validators/contracts/check_module_descriptors.py` | PASS |
| `python tools/validators/contracts/check_workbench_workspaces.py` | PASS |
| `python tools/validators/contracts/check_app_descriptors.py` | PASS |
| `python tools/validators/contracts/check_composition_plan.py` | PASS |
| `python tools/validators/contracts/check_provider_model.py` | PASS |
| `python tools/validators/contracts/check_service_conformance.py` | PASS_WITH_WARNINGS |
| `python tools/validators/package/check_package_mount_slice.py` | PASS |
| `python tools/validators/package/check_mod_pack_trust.py` | PASS |
| `python tools/validators/testing/check_test_tiers.py` | PASS |
| `python tools/validators/abi/check_public_headers.py` | PASS_WITH_WARNINGS |
| `python .aide/scripts/aide_lite.py doctor` | PASS |
| `python .aide/scripts/aide_lite.py validate` | PASS |
| `python -m tools.aide.doctor` | UNAVAILABLE: module not present |
| `python -m tools.aide.validate` | UNAVAILABLE: module not present |
| `python -m compileall -q ...` | PASS |
| `python tools/test/run_fast_strict.py --repo-root .` | PASS, 33 commands, 397.125s |
| `ctest --preset verify -R "capability_matrix|capability_regression" --output-on-failure` | PASS, 47/47 |
| `ctest --preset verify --output-on-failure` | FAIL/INTERRUPTED, full-gate debt |
| `git diff --check --cached` | PASS |

## Non-Goals Preserved

- No top-level `profiles/`, `labs/`, `modules/`, `plugins/`, or `services/`
  roots were created.
- Product/runtime behavior was not intentionally changed.
- Retired roots were not recreated to satisfy stale full-suite tests.
- Pack IDs, schema IDs, save/replay/artifact IDs, and content hashes were not
  silently mutated.
- Generated/local structure export remains under ignored `.dominium.local/`.

## Next Task

Recommended next task: `FULL-GATE-LEGACY-TEST-ROUTE-01`.

Scope should update or retire the full CTest checks that still expect old roots,
without recreating those old roots or weakening the fast strict structure gate.
