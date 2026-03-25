# XI-3 Final

- Generated: 2026-03-26
- Duplicate clusters: 6066
- Keep-only clusters: 996
- Merge-required clusters: 3454
- Quarantine clusters: 1616

## Top HIGH Risk Items

- `duplicate.cluster.001766fd09987b8e` -> canonical `tests/invariant/test_optional_bundles_core_runtime.py` vs secondary `tests/invariant/test_survival_no_nondiegetic_lenses.py` (quarantine)
- `duplicate.cluster.0075f9b78b2784df` -> canonical `src/meta_extensions_engine.py` vs secondary `src/meta/extensions/extensions_engine.py` (quarantine)
- `duplicate.cluster.01941b70f1147be9` -> canonical `game/tests/tests/contract/dominium_perf_tests.cpp` vs secondary `game/tests/tests/contract/dominium_universe_bundle_tests.cpp` (quarantine)
- `duplicate.cluster.0253285ae8918910` -> canonical `tools/xstack/registry_compile/bundle_profile.py` vs secondary `tools/xstack/pack_loader/loader.py` (quarantine)
- `duplicate.cluster.0260b746b91f764a` -> canonical `src/signals/transport/__init__.py` vs secondary `src/signals/__init__.py` (quarantine)
- `duplicate.cluster.0284e66e92fa82a8` -> canonical `game/include/dominium/rules/governance/governance_system.h` vs secondary `game/include/dominium/rules/war/war_system.h` (quarantine)
- `duplicate.cluster.02a76b808e9594ff` -> canonical `tools/ci/validate_earth_data.py` vs secondary `tools/ci/validate_milky_way_data.py` (quarantine)
- `duplicate.cluster.03182cd42634b77c` -> canonical `tools/xstack/testx/tests/test_no_direct_field_mutation.py` vs secondary `tools/xstack/testx/tests/test_cross_shard_field_blocked.py` (quarantine)
- `duplicate.cluster.03a31072d7ac07a9` -> canonical `src/system/templates/__init__.py` vs secondary `src/system/templates/template_compiler.py` (quarantine)
- `duplicate.cluster.03ab149d795288bb` -> canonical `tools/distribution/profile_inspect.py` vs secondary `tools/fab/fab_validate.py` (quarantine)
- `duplicate.cluster.03d1718b6abbb996` -> canonical `tools/xstack/testx/tests/pack_compat0_testlib.py` vs secondary `tools/xstack/testx/tests/mod_policy0_testlib.py` (quarantine)
- `duplicate.cluster.0631a59ef2fe2be3` -> canonical `src/meta/extensions/__init__.py` vs secondary `src/meta_extensions_engine.py` (quarantine)
- `duplicate.cluster.065d7d23b936c46c` -> canonical `src/geo/overlay/__init__.py` vs secondary `src/geo/overlay/overlay_merge_engine.py` (quarantine)
- `duplicate.cluster.06f2c33736385885` -> canonical `tools/worldgen/worldgen_lock_common.py` vs secondary `tools/mvp/update_sim_common.py` (quarantine)
- `duplicate.cluster.0701ac0ca5fc5bc9` -> canonical `tools/release/entrypoint_unify_common.py` vs secondary `tools/auditx/analyzers/e179_inline_response_curve_smell.py` (quarantine)
- `duplicate.cluster.07162c47dda2a254` -> canonical `src/worldgen/earth/water/__init__.py` vs secondary `src/worldgen/earth/water/water_view_engine.py` (quarantine)
- `duplicate.cluster.07c7e7b9365cb9dc` -> canonical `src/lib/provides/__init__.py` vs secondary `src/lib/provides/provider_resolution.py` (quarantine)
- `duplicate.cluster.07f923702826c909` -> canonical `tests/share/share_bundle_tests.py` vs secondary `tests/ops/export_import_bundle_tests.py` (quarantine)
- `duplicate.cluster.0873f4be504cdfe1` -> canonical `tools/xstack/testx/tests/test_promotion_requires_replication.py` vs secondary `tools/xstack/testx/tests/test_proc9_candidate_promotion_requires_replication.py` (quarantine)
- `duplicate.cluster.0954e6658a2eb4fa` -> canonical `src/worldgen/earth/climate_field_engine.py` vs secondary `src/worldgen/earth/tide_field_engine.py` (quarantine)

## Recommended Manual Review

- `duplicate.cluster.01941b70f1147be9` `game/tests/tests/contract/dominium_universe_bundle_tests.cpp` score delta `0.0`
- `duplicate.cluster.0b0e8fb5fe94502e` `tools/release/component_graph_common.py` score delta `0.0`
- `duplicate.cluster.18b9b8c3ea9b2715` `tests/testx/capability_regression/test_no_tools_without_capability.py` score delta `0.0`
- `duplicate.cluster.18e02e8d2f9d6a71` `tools/auditx/analyzers/e349_adhoc_worldgen_smell.py` score delta `0.0`
- `duplicate.cluster.1a47c681251f2a58` `tools/xstack/testx/tests/test_ui_descriptor_validation.py` score delta `0.0`
- `duplicate.cluster.1b2cac44712a5224` `tools/xstack/testx/tests/pack_compat0_testlib.py` score delta `0.0`
- `duplicate.cluster.1bec37cc2c0b2390` `tools/process/tool_replay_qc_window.py` score delta `0.0`
- `duplicate.cluster.1df1d8bf8a458b7f` `tools/xstack/testx/tests/gal1_testlib.py` score delta `0.0`
- `duplicate.cluster.1df1d8bf8a458b7f` `tools/xstack/testx/tests/sol2_testlib.py` score delta `0.0`
- `duplicate.cluster.213a8a90f157b44f` `tools/xstack/testx/tests/test_all_registries_have_stability_markers.py` score delta `0.0`
- `duplicate.cluster.23b8ea6130a40a1d` `tools/auditx/analyzers/e232_direct_time_write_smell.py` score delta `0.0`
- `duplicate.cluster.247bcbbd2c68dad0` `tools/xstack/testx/tests/test_formalization_accept_creates_geometry.py` score delta `0.0`
- `duplicate.cluster.2978f37b0c9cf4df` `tools/xstack/testx/tests/test_pipeline_net_handshake_stage_srz_hybrid.py` score delta `0.0`
- `duplicate.cluster.38cb0cfca0afc910` `tools/auditx/analyzers/e145_geometry_mutation_bypass_smell.py` score delta `0.0`
- `duplicate.cluster.38cb0cfca0afc910` `tools/auditx/analyzers/e149_vehicle_hardcode_smell.py` score delta `0.0`
- `duplicate.cluster.3b31f4cda90f9694` `src/models/model_engine.py` score delta `0.0`
- `duplicate.cluster.3da650173c632c38` `engine/modules/system/dsys_posix.c` score delta `0.0`
- `duplicate.cluster.415ed4b579603554` `tools/review/doc_inventory_common.py` score delta `0.0`
- `duplicate.cluster.4607c992362ad2f4` `tools/performx/performx.py` score delta `0.0`
- `duplicate.cluster.4607c992362ad2f4` `tools/securex/securex.py` score delta `0.0`

## Readiness

- Ξ-4 readiness: `ready_with_manual_review`

