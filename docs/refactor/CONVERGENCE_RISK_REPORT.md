# Convergence Risk Report

- Generated: 2026-03-26
- Fingerprint: `4c0aec29ba48b85173f84e03f9a56d92e8954b970aca4abfa200811144c2cff5`
- HIGH risk actions: 31160
- MED risk actions: 10089
- LOW risk actions: 4262

## Top HIGH Risk Items

| Cluster | Symbol | Canonical | Secondary | Resolution | Reasons |
| --- | --- | --- | --- | --- | --- |
| `duplicate.cluster.001766fd09987b8e` | `main` | `tests/invariant/test_optional_bundles_core_runtime.py` | `tests/invariant/test_survival_no_nondiegetic_lenses.py` | `quarantine` | `pack_compat_install_resolver, time_anchor` |
| `duplicate.cluster.0075f9b78b2784df` | `normalize_extensions_map` | `src/meta_extensions_engine.py` | `src/meta/extensions/extensions_engine.py` | `quarantine` | `protocol_negotiation, semantic_contracts` |
| `duplicate.cluster.01941b70f1147be9` | `fail` | `game/tests/tests/contract/dominium_perf_tests.cpp` | `game/tests/tests/contract/dominium_universe_bundle_tests.cpp` | `quarantine` | `pack_compat_install_resolver, semantic_contracts` |
| `duplicate.cluster.0253285ae8918910` | `_rel` | `tools/xstack/registry_compile/bundle_profile.py` | `tools/xstack/pack_loader/loader.py` | `quarantine` | `pack_compat_install_resolver` |
| `duplicate.cluster.0260b746b91f764a` | `REFUSAL_SIGNAL_ROUTE_UNAVAILABLE` | `src/signals/transport/__init__.py` | `src/signals/__init__.py` | `quarantine` | `semantic_contracts` |
| `duplicate.cluster.0284e66e92fa82a8` | `system_id` | `game/include/dominium/rules/governance/governance_system.h` | `game/include/dominium/rules/war/war_system.h` | `quarantine` | `semantic_contracts` |
| `duplicate.cluster.02a76b808e9594ff` | `require_keys` | `tools/ci/validate_earth_data.py` | `tools/ci/validate_milky_way_data.py` | `quarantine` | `worldgen_lock_or_overlay` |
| `duplicate.cluster.03182cd42634b77c` | `run` | `tools/xstack/testx/tests/test_no_direct_field_mutation.py` | `tools/xstack/testx/tests/test_cross_shard_field_blocked.py` | `quarantine` | `semantic_contracts, time_anchor` |
| `duplicate.cluster.03a31072d7ac07a9` | `REFUSAL_TEMPLATE_INVALID` | `src/system/templates/__init__.py` | `src/system/templates/template_compiler.py` | `quarantine` | `semantic_contracts` |
| `duplicate.cluster.03ab149d795288bb` | `normalize_list` | `tools/distribution/profile_inspect.py` | `tools/fab/fab_validate.py` | `quarantine` | `pack_compat_install_resolver, semantic_contracts` |
| `duplicate.cluster.03d1718b6abbb996` | `load_fixture_lockfile` | `tools/xstack/testx/tests/pack_compat0_testlib.py` | `tools/xstack/testx/tests/mod_policy0_testlib.py` | `quarantine` | `pack_compat_install_resolver, semantic_contracts` |
| `duplicate.cluster.0631a59ef2fe2be3` | `validate_extensions_map` | `src/meta/extensions/__init__.py` | `src/meta_extensions_engine.py` | `quarantine` | `semantic_contracts` |
| `duplicate.cluster.065d7d23b936c46c` | `property_patch_hash_chain` | `src/geo/overlay/__init__.py` | `src/geo/overlay/overlay_merge_engine.py` | `quarantine` | `pack_compat_install_resolver, worldgen_lock_or_overlay` |
| `duplicate.cluster.06f2c33736385885` | `_write_canonical_json` | `tools/worldgen/worldgen_lock_common.py` | `tools/mvp/update_sim_common.py` | `quarantine` | `trust_enforcement, worldgen_lock_or_overlay` |
| `duplicate.cluster.0701ac0ca5fc5bc9` | `_read_text` | `tools/release/entrypoint_unify_common.py` | `tools/auditx/analyzers/e179_inline_response_curve_smell.py` | `quarantine` | `pack_compat_install_resolver, protocol_negotiation, semantic_contracts, time_anchor, trust_enforcement, worldgen_lock_or_overlay` |
| `duplicate.cluster.07162c47dda2a254` | `build_water_view_surface` | `src/worldgen/earth/water/__init__.py` | `src/worldgen/earth/water/water_view_engine.py` | `quarantine` | `worldgen_lock_or_overlay` |
| `duplicate.cluster.07c7e7b9365cb9dc` | `RESOLUTION_POLICY_EXPLICIT_REQUIRED` | `src/lib/provides/__init__.py` | `src/lib/provides/provider_resolution.py` | `quarantine` | `semantic_contracts` |
| `duplicate.cluster.07f923702826c909` | `write_json` | `tests/share/share_bundle_tests.py` | `tests/ops/export_import_bundle_tests.py` | `quarantine` | `pack_compat_install_resolver` |
| `duplicate.cluster.0873f4be504cdfe1` | `_refusal_reason` | `tools/xstack/testx/tests/test_promotion_requires_replication.py` | `tools/xstack/testx/tests/test_proc9_candidate_promotion_requires_replication.py` | `quarantine` | `semantic_contracts` |
| `duplicate.cluster.0954e6658a2eb4fa` | `_material_or_surface_class` | `src/worldgen/earth/climate_field_engine.py` | `src/worldgen/earth/tide_field_engine.py` | `quarantine` | `worldgen_lock_or_overlay` |

## Manual Review Queue

| Cluster | Symbol | Canonical | Secondary | Score delta | Reasons |
| --- | --- | --- | --- | --- | --- |
| `duplicate.cluster.01941b70f1147be9` | `fail` | `game/tests/tests/contract/dominium_perf_tests.cpp` | `game/tests/tests/contract/dominium_universe_bundle_tests.cpp` | `0.0` | `pack_compat_install_resolver, semantic_contracts` |
| `duplicate.cluster.0b0e8fb5fe94502e` | `_write_json` | `tools/meta/identity_common.py` | `tools/release/component_graph_common.py` | `0.0` | `pack_compat_install_resolver, semantic_contracts, trust_enforcement` |
| `duplicate.cluster.18b9b8c3ea9b2715` | `main` | `tests/testx/capability_regression/test_no_future_without_capability.py` | `tests/testx/capability_regression/test_no_tools_without_capability.py` | `0.0` | `protocol_negotiation` |
| `duplicate.cluster.18e02e8d2f9d6a71` | `run` | `tools/auditx/analyzers/e347_unlogged_terrain_edit_smell.py` | `tools/auditx/analyzers/e349_adhoc_worldgen_smell.py` | `0.0` | `worldgen_lock_or_overlay` |
| `duplicate.cluster.1a47c681251f2a58` | `_load_json` | `tools/xstack/testx/tests/test_policy_registry_determinism.py` | `tools/xstack/testx/tests/test_ui_descriptor_validation.py` | `0.0` | `pack_compat_install_resolver, semantic_contracts, worldgen_lock_or_overlay` |
| `duplicate.cluster.1b2cac44712a5224` | `cleanup_temp_repo` | `tools/xstack/testx/tests/mod_policy0_testlib.py` | `tools/xstack/testx/tests/pack_compat0_testlib.py` | `0.0` | `pack_compat_install_resolver, semantic_contracts` |
| `duplicate.cluster.1bec37cc2c0b2390` | `_as_int` | `tools/process/tool_replay_process_window.py` | `tools/process/tool_replay_qc_window.py` | `0.0` | `pack_compat_install_resolver, protocol_negotiation, semantic_contracts, time_anchor, trust_enforcement, worldgen_lock_or_overlay` |
| `duplicate.cluster.1df1d8bf8a458b7f` | `_ensure_repo_root` | `tools/xstack/testx/tests/earth10_testlib.py` | `tools/xstack/testx/tests/gal1_testlib.py` | `0.0` | `worldgen_lock_or_overlay` |
| `duplicate.cluster.1df1d8bf8a458b7f` | `_ensure_repo_root` | `tools/xstack/testx/tests/earth10_testlib.py` | `tools/xstack/testx/tests/sol2_testlib.py` | `0.0` | `worldgen_lock_or_overlay` |
| `duplicate.cluster.213a8a90f157b44f` | `run` | `tools/xstack/testx/tests/test_all_registries_have_stability.py` | `tools/xstack/testx/tests/test_all_registries_have_stability_markers.py` | `0.0` | `semantic_contracts` |
| `duplicate.cluster.23b8ea6130a40a1d` | `run` | `tools/auditx/analyzers/e230_future_receipt_reference_smell.py` | `tools/auditx/analyzers/e232_direct_time_write_smell.py` | `0.0` | `time_anchor, trust_enforcement` |
| `duplicate.cluster.247bcbbd2c68dad0` | `_infer` | `tools/xstack/testx/tests/test_accept_candidate_creates_commitments.py` | `tools/xstack/testx/tests/test_formalization_accept_creates_geometry.py` | `0.0` | `worldgen_lock_or_overlay` |
| `duplicate.cluster.2978f37b0c9cf4df` | `run` | `tools/xstack/testx/tests/test_pipeline_net_handshake_stage_authoritative.py` | `tools/xstack/testx/tests/test_pipeline_net_handshake_stage_srz_hybrid.py` | `0.0` | `protocol_negotiation` |
| `duplicate.cluster.38cb0cfca0afc910` | `run` | `tools/auditx/analyzers/e143_direct_position_mutation_smell.py` | `tools/auditx/analyzers/e145_geometry_mutation_bypass_smell.py` | `0.0` | `worldgen_lock_or_overlay` |
| `duplicate.cluster.38cb0cfca0afc910` | `run` | `tools/auditx/analyzers/e143_direct_position_mutation_smell.py` | `tools/auditx/analyzers/e149_vehicle_hardcode_smell.py` | `0.0` | `worldgen_lock_or_overlay` |
| `duplicate.cluster.3b31f4cda90f9694` | `_canon` | `src/mobility/vehicle/vehicle_engine.py` | `src/models/model_engine.py` | `0.0` | `pack_compat_install_resolver, time_anchor, worldgen_lock_or_overlay` |
| `duplicate.cluster.3da650173c632c38` | `timeval` | `engine/modules/system/dsys_platform_stub.c` | `engine/modules/system/dsys_posix.c` | `0.0` | `time_anchor` |
| `duplicate.cluster.415ed4b579603554` | `_token` | `tools/release/dist_final_common.py` | `tools/review/doc_inventory_common.py` | `0.0` | `pack_compat_install_resolver, protocol_negotiation, semantic_contracts, time_anchor, trust_enforcement` |
| `duplicate.cluster.4607c992362ad2f4` | `_repo_root` | `tools/compatx/compatx.py` | `tools/performx/performx.py` | `0.0` | `pack_compat_install_resolver, semantic_contracts` |
| `duplicate.cluster.4607c992362ad2f4` | `_repo_root` | `tools/compatx/compatx.py` | `tools/securex/securex.py` | `0.0` | `pack_compat_install_resolver, semantic_contracts` |

