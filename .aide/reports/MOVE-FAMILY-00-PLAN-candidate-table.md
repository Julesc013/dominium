# MOVE-FAMILY-00 Candidate Table

Status: DERIVED
Last Reviewed: 2026-05-17

## Summary

No candidate is included for MOVE-FAMILY-00 apply. `ide/README.md` was already moved by AIDE-MOVE-01; all remaining family material is active Python/tooling or machine-readable IDE projection metadata.

| Root | Current tracked files | Included now | Fate | Reason |
| --- | ---: | ---: | --- | --- |
| `governance/` | 2 | 0 | preserve/defer | Active policy/governance Python helpers with release, setup, dist, tool, and test consumers. |
| `meta/` | 26 | 0 | preserve/defer | Broad active Python subsystem with runtime, game, release, tool, AuditX, RepoX, TestX, and test consumers. |
| `performance/` | 3 | 0 | preserve/defer | Active product/runtime performance helpers imported by client, materials, and XStack session runtime. |
| `validation/` | 2 | 0 | preserve/defer | Active validation pipeline imported by runtime, tools, shims, AuditX, RepoX, and TestX. |
| `ide/` | 3 | 0 | convert later | Remaining manifests are machine-readable projection schema/examples with CMake, script, docs, and registry consumers. |

## File-Level Classification

| Source Path | Fate | Risk | Reference Count | Include? |
| --- | --- | --- | ---: | --- |
| `governance/__init__.py` | preserve_defer | medium | 41 | no |
| `governance/governance_profile.py` | preserve_defer | medium | 51 | no |
| `meta/__init__.py` | preserve_defer | high | 38 | no |
| `meta/compile/__init__.py` | preserve_defer | high | 35 | no |
| `meta/compile/compile_engine.py` | preserve_defer | high | 55 | no |
| `meta/compute/__init__.py` | preserve_defer | high | 39 | no |
| `meta/compute/compute_budget_engine.py` | preserve_defer | high | 56 | no |
| `meta/explain/__init__.py` | preserve_defer | high | 42 | no |
| `meta/explain/explain_engine.py` | preserve_defer | high | 51 | no |
| `meta/extensions/__init__.py` | preserve_defer | high | 50 | no |
| `meta/extensions/extensions_engine.py` | preserve_defer | high | 53 | no |
| `meta/identity/__init__.py` | preserve_defer | high | 25 | no |
| `meta/identity/identity_validator.py` | preserve_defer | high | 49 | no |
| `meta/instrumentation/__init__.py` | preserve_defer | high | 32 | no |
| `meta/instrumentation/instrumentation_engine.py` | preserve_defer | high | 56 | no |
| `meta/numeric.py` | preserve_defer | high | 49 | no |
| `meta/observability.py` | preserve_defer | high | 33 | no |
| `meta/profile/__init__.py` | preserve_defer | high | 33 | no |
| `meta/profile/profile_engine.py` | preserve_defer | high | 43 | no |
| `meta/provenance/__init__.py` | preserve_defer | high | 25 | no |
| `meta/provenance/compaction_engine.py` | preserve_defer | high | 47 | no |
| `meta/reference/__init__.py` | preserve_defer | high | 34 | no |
| `meta/reference/geo_small_reference.py` | preserve_defer | high | 40 | no |
| `meta/reference/logic_small_reference.py` | preserve_defer | high | 40 | no |
| `meta/reference/reference_engine.py` | preserve_defer | high | 43 | no |
| `meta/stability/__init__.py` | preserve_defer | high | 33 | no |
| `meta/stability/stability_scope.py` | preserve_defer | high | 35 | no |
| `meta/stability/stability_validator.py` | preserve_defer | high | 53 | no |
| `performance/__init__.py` | preserve_defer | medium | 30 | no |
| `performance/cost_engine.py` | preserve_defer | medium | 38 | no |
| `performance/inspection_cache.py` | preserve_defer | medium | 38 | no |
| `validation/__init__.py` | preserve_defer | medium | 30 | no |
| `validation/validation_engine.py` | preserve_defer | medium | 67 | no |
| `ide/manifests/projection_manifest.schema.json` | convert_later | medium | 7 | no |
| `ide/manifests/projection_manifest_examples/example_linux_clang_modern_client_gui.projection.json` | convert_later | medium | 5 | no |
| `ide/manifests/projection_manifest_examples/example_win_vc6_win9x_client_gui.projection.json` | convert_later | medium | 5 | no |
