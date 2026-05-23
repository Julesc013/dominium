Status: DERIVED
Last Reviewed: 2026-05-23
Supersedes: none
Superseded By: none
Result: PASS_WITH_WARNINGS
Task: PROVIDER-STRUCTURE-CANON-01
Date: 2026-05-23
Baseline Commit: e9de4787bf1382bd47bd52a45e8bfc90cf83621a

# Provider Structure Canon 01

## Summary

This pass tightened Dominium provider structure around the service-first rule:
service identity is first-party, providers are replaceable implementations, and
profiles select providers. It moved the existing null and software render
providers under `runtime/render/providers/`, versioned provider IDs, added a
provider structure contract and validator, and created minimal external/profile
policy roots without introducing future raylib, SDL2, Lua, or GUI
implementations.

## Files Inspected

- `AGENTS.md`
- `docs/repo/FOUNDATION_LOCK.md`
- `docs/repo/audits/PRODUCT_SPINE_REVIEW_01.md`
- `contracts/provider/provider.registry.json`
- `contracts/provider/provider_descriptor.schema.json`
- `contracts/provider/provider.contract.toml`
- `contracts/capability/capability.registry.json`
- `contracts/platform/renderer_portability.matrix.json`
- `contracts/profile/profile.registry.json`
- `docs/architecture/provider_model.md`
- `docs/development/provider_guidelines.md`
- `engine/CMakeLists.txt`
- `runtime/render/backend/*`
- `runtime/render/null/*`
- `runtime/render/software/*`
- `tools/validators/repo/*`
- `tools/validators/contracts/check_provider_model.py`
- `tools/xstack/repox/check.py`
- `tools/xstack/auditx/analyzers/*renderer*`
- `tools/xstack/testx/tests/*renderer*`

## Files Changed

- Added `docs/repo/provider_structure_canon.md`.
- Added `contracts/provider/provider_structure.contract.toml`.
- Added `external/README.md` and `external/manifests/third_party.toml`.
- Added `release/profiles/README.md` and `release/profiles/dev/render.null.toml`.
- Added `tools/validators/repo/check_provider_structure.py`.
- Moved render provider files from `runtime/render/null/` and
  `runtime/render/software/` to `runtime/render/providers/null/` and
  `runtime/render/providers/software/`.
- Moved Python snapshot provider modules from `runtime/render/backend/` to the
  matching provider directories while preserving backend API imports.
- Updated provider/capability/profile/portability registries and affected
  contract fixtures to use versioned provider IDs.
- Updated validator and XStack references to the new provider paths.

## Policy Created

- `dominium.provider.structure.v1` defines the path law
  `runtime/<service>/providers/<provider>`.
- `external/manifests/third_party.toml` records third-party source as
  provider input only. It does not claim any introduced third-party dependency.
- `dominium.profile.dev.render_null` records a minimal dev validation profile
  for explicit null render selection.

## Moves Performed

- `runtime/render/null/` -> `runtime/render/providers/null/`
- `runtime/render/software/` -> `runtime/render/providers/software/`
- `runtime/render/backend/null_renderer.py` ->
  `runtime/render/providers/null/null_renderer.py`
- `runtime/render/backend/software_renderer.py` ->
  `runtime/render/providers/software/software_renderer.py`

## Non-Goals Preserved

- No raylib, rlgl, rlsw, raygui, raudio, SDL2, or Lua implementation was added.
- No provider loader, dynamic selection engine, or scheduler was implemented.
- No Workbench shell, native GUI, renderer feature, package mount, gameplay, or
  product runtime behavior was added.
- No top-level `profiles/`, `labs/`, `modules/`, `plugins/`, or `services/`
  root was created.
- No full CTest or broad build was run.

## Validation

- `py -3 -m py_compile tools/validators/repo/check_provider_structure.py tools/validators/contracts/check_provider_model.py tools/validators/repo/check_canonical_structure.py tools/validators/repo/check_path_terms.py` -> PASS
- `py -3 -m py_compile runtime/render/backend/__init__.py runtime/render/backend/snapshot_capture.py runtime/render/backend/hw_renderer_gl.py runtime/render/providers/null/null_renderer.py runtime/render/providers/software/software_renderer.py tools/xstack/repox/check.py tools/xstack/auditx/analyzers/e50_renderer_truth_leak_smell.py tools/xstack/testx/tests/test_renderer_truth_isolation.py` -> PASS
- `py -3 -c "from runtime.render.backend import render_null_snapshot, render_software_snapshot; print(render_null_snapshot.__name__, render_software_snapshot.__name__)"` -> PASS
- `py -3 -c "from runtime.render.providers.null.null_renderer import render_null_snapshot; from runtime.render.providers.software.software_renderer import render_software_snapshot; print('provider imports ok')"` -> PASS
- `py -3 tools/validators/repo/check_provider_structure.py --repo-root . --strict` -> PASS_WITH_WARNINGS
- `py -3 tools/validators/contracts/check_provider_model.py --repo-root . --strict --fixtures` -> PASS
- `py -3 tools/validators/platform/check_portability_matrix.py --repo-root . --strict` -> PASS
- `py -3 tools/validators/contracts/check_service_conformance.py --repo-root . --strict --fixtures` -> PASS_WITH_WARNINGS
- `py -3 tools/validators/contracts/check_app_descriptors.py --repo-root . --strict --fixtures` -> PASS
- `py -3 tools/validators/contracts/check_module_descriptors.py --repo-root . --strict --fixtures` -> PASS
- `py -3 tools/validators/contracts/check_composition_plan.py --repo-root . --strict --fixtures` -> PASS
- `py -3 tools/validators/package/check_mod_pack_trust.py --repo-root . --strict --fixtures` -> PASS
- `py -3 tools/validators/repo/check_replacement_packet.py --repo-root . --strict` -> PASS
- `py -3 tools/validators/repo/check_canonical_structure.py --repo-root . --strict --max-findings 120` -> PASS_WITH_WARNINGS
- `py -3 tools/validators/repo/check_structure_residuals.py --repo-root . --strict --max-findings 120` -> PASS_WITH_WARNINGS
- `py -3 tools/validators/repo/check_path_terms.py --repo-root . --strict --max-findings 120` -> PASS_WITH_WARNINGS
- `py -3 .aide/scripts/aide_lite.py doctor` -> PASS
- `py -3 .aide/scripts/aide_lite.py validate` -> PASS
- `py -3 tools/xstack/testx/runner.py --repo-root . --profile FAST --cache off --subset testx.render.null_renderer_summary_deterministic,testx.render.software_renderer_produces_image,testx.render.renderer_truth_isolation,testx.render.backend_selection_fallback,testx.render.render_snapshot_schema_valid` -> PASS
- `py -3 tests/runtime/render/renderer_contract_tests.py --repo-root .` -> PASS

## Warnings Preserved

- Storage and package provider descriptors remain pending provider splits.
- Workbench shell remains deferred until real shell ownership exists.
- Projection mode roots remain deferred pending `PROJECTION-CONFORMANCE-01`.
- Pack-internal `content/` payload roots remain pending
  `PACK-INTERNAL-LAYOUT-CANON-01`.
- `contracts/schema` remains broad pending `SCHEMA-CANON-RESIDUAL-02`.
- Runtime/engine residual taxonomy warnings remain pending
  `RUNTIME-RESIDUAL-TAXONOMY-01`.
- Test taxonomy warnings remain non-blocking.
- Path-term findings are historical/archive or existing allowed exceptions;
  blocker count was zero.

## Result

Limited provider-structure cleanup is complete with warnings. The repo now has
an enforceable service-first provider structure law and a validator that blocks
vendor-shaped runtime/contract/app roots and top-level profile/lab/module/plugin
roots.

## Next Tasks

- `THIRD-PARTY-MANIFEST-01`
- `PROVIDER-CONFORMANCE-01`
- `RAYLIB-SEED-PROVIDER-01`
- `SDL2-PROVIDER-01`
- `LUA-PROVIDER-PIN-01`
- `PROJECTION-CONFORMANCE-01`
- `SCHEMA-CANON-RESIDUAL-02`
