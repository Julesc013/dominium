Status: DERIVED
Last Reviewed: 2026-03-13
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: regenerated shim coverage report after convergence cleanup

# Shim Coverage Report

- Fingerprint: `43d7cfda42397498d8dad980a86a4943db33e40f5b1471c9e22c05d4378f0723`
- Violations: `0`

## Shim Surfaces

| Category | Legacy Surface | Replacement | Shim ID |
| --- | --- | --- | --- |
| `path` | `./data | data` | `VROOT_STORE/data` | `shim.path.legacy_data_root` |
| `path` | `../packs | ./packs | packs | data/packs | ./data/packs` | `VROOT_PACKS` | `shim.path.legacy_packs_root` |
| `path` | `./profiles | profiles | data/profiles | ./data/profiles` | `VROOT_PROFILES` | `shim.path.legacy_profiles_root` |
| `path` | `./locks | ./instances | ./saves | ./exports | ./logs | ./runtime` | `governed store vroots` | `shim.path.legacy_store_children` |
| `flag` | `--ui gui|cli` | `--mode rendered|cli rendered|cli` | `shim.flag.legacy_client_ui` |
| `flag` | `--no-gui` | `--mode tui|cli` | `shim.flag.legacy_no_gui` |
| `flag` | `--portable` | `--install-root <portable adjacency root>` | `shim.flag.legacy_portable` |
| `flag` | `--ui headless|cli` | `--mode headless|cli headless|cli` | `shim.flag.legacy_server_ui` |
| `tool` | `tools/pack/migrate_capability_gating.py` | `dom pack migrate-capability-gating` | `shim.tool.pack_migrate_capability_gating` |
| `tool` | `tools/pack/pack_validate.py` | `dom pack validate-manifest` | `shim.tool.pack_validate` |
| `validation` | `tools/ci/validate_all.py` | `validate --all --profile FAST|STRICT|FULL` | `shim.validation.validate_all_py` |

## Integration Coverage

| File | Status | Required Tokens |
| --- | --- | --- |
| `src/appshell/bootstrap.py` | `integrated` | `apply_flag_shims(` |
| `tools/ci/validate_all.py` | `integrated` | `run_legacy_validate_all(` |
| `tools/distribution/distribution_lib.py` | `integrated` | `redirect_legacy_path(` |
| `tools/pack/migrate_capability_gating.py` | `integrated` | `emit_legacy_tool_warning(`, `redirect_legacy_path(` |
| `tools/pack/pack_validate.py` | `integrated` | `emit_legacy_tool_warning(`, `redirect_legacy_path(` |
| `tools/release/entrypoint_unify_common.py` | `integrated` | `apply_flag_shims(` |

## Warning Coverage

| File | Status | Required Tokens |
| --- | --- | --- |
| `src/compat/shims/flag_shims.py` | `complete` | `warn.deprecated_flag_usage`, `build_shim_stability(` |
| `src/compat/shims/path_shims.py` | `complete` | `warn.deprecated_path_usage`, `emit_deprecation_warning(`, `vpath_resolve(` |
| `src/compat/shims/tool_shims.py` | `complete` | `warn.deprecated_tool_usage`, `emit_deprecation_warning(` |
| `src/compat/shims/validation_shims.py` | `complete` | `warn.deprecated_validator_usage`, `build_validation_report(`, `write_validation_outputs(` |

## Known Remaining Legacy Assumptions

- surface_id=`legacy.capability_negotiation` path=`src/compat/capability_negotiation.py` status=`active_adapter` replacement_target=`src/validation/validation_engine.py`
- surface_id=`legacy.artifact_validator` path=`src/lib/artifact/artifact_validator.py` status=`active_adapter` replacement_target=`src/validation/validation_engine.py`
- surface_id=`legacy.install_validator` path=`src/lib/install/install_validator.py` status=`active_adapter` replacement_target=`src/validation/validation_engine.py`
- surface_id=`legacy.instance_validator` path=`src/lib/instance/instance_validator.py` status=`active_adapter` replacement_target=`src/validation/validation_engine.py`
- surface_id=`legacy.save_validator` path=`src/lib/save/save_validator.py` status=`active_adapter` replacement_target=`src/validation/validation_engine.py`
- surface_id=`legacy.stability_validator` path=`src/meta/stability/stability_validator.py` status=`active_adapter` replacement_target=`src/validation/validation_engine.py`
- surface_id=`legacy.arch_audit` path=`tools/audit/tool_run_arch_audit.py` status=`active_adapter` replacement_target=`src/validation/validation_engine.py`
- surface_id=`legacy.compatx_cli` path=`tools/compatx/compatx.py` status=`active_adapter` replacement_target=`src/validation/validation_engine.py`
- surface_id=`legacy.time_compaction_check` path=`tools/time/tool_compaction_anchor_check.py` status=`active_adapter` replacement_target=`src/validation/validation_engine.py`
- surface_id=`legacy.time_verify` path=`tools/time/tool_verify_longrun_ticks.py` status=`active_adapter` replacement_target=`src/validation/validation_engine.py`
- surface_id=`legacy.compatx_check` path=`tools/xstack/compatx/check.py` status=`active_adapter` replacement_target=`src/validation/validation_engine.py`
- surface_id=`legacy.pack_verification_pipeline` path=`src/packs/compat/pack_verification_pipeline.py` status=`deprecated` replacement_target=`src/validation/validation_engine.py::validate.packs_release_lock`
- surface_id=`legacy.graph_validate` path=`tools/core/tool_graph_validate.py` status=`deprecated` replacement_target=`tools/xstack/compatx/check.py`
- surface_id=`legacy.coredata_validate` path=`tools/coredata_validate/coredata_validate_main.cpp` status=`deprecated` replacement_target=`tools/xstack/compatx/check.py`
- surface_id=`legacy.data_validate_c` path=`tools/data_validate/data_validate_main.c` status=`deprecated` replacement_target=`tools/xstack/compatx/check.py`
- surface_id=`legacy.domain_validate` path=`tools/domain/tool_domain_validate.py` status=`deprecated` replacement_target=`src/meta/stability/stability_validator.py`
- surface_id=`legacy.fab_validate` path=`tools/fab/fab_validate.py` status=`deprecated` replacement_target=`src/meta/stability/stability_validator.py`
- surface_id=`legacy.hygiene_validate_cli` path=`tools/validate/hygiene_validate_cli.cpp` status=`deprecated` replacement_target=`tools/audit/tool_run_arch_audit.py`
- surface_id=`legacy.validate_all_cpp` path=`tools/validation/validate_all_main.cpp` status=`deprecated` replacement_target=`src/validation/validation_engine.py::validate.determinism`
- surface_id=`legacy.validation_registry_cpp` path=`tools/validation/validators_registry.cpp` status=`deprecated` replacement_target=`data/registries/validation_suite_registry.json`
