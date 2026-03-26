# Convergence Risk Report

- Generated: 2026-03-26
- Fingerprint: `73aac832765e57652be4b887b21ed0921dcd29647971d4707ff93f0d11fee505`
- HIGH risk actions: 16676
- MED risk actions: 9465
- LOW risk actions: 920

## Top HIGH Risk Items

| Cluster | Symbol | Canonical | Secondary | Resolution | Reasons |
| --- | --- | --- | --- | --- | --- |
| `duplicate.cluster.0075f9b78b2784df` | `normalize_extensions_map` | `src/meta_extensions_engine.py` | `src/meta/extensions/extensions_engine.py` | `quarantine` | `protocol_negotiation, semantic_contracts` |
| `duplicate.cluster.0253285ae8918910` | `_rel` | `tools/xstack/registry_compile/bundle_profile.py` | `tools/xstack/pack_loader/loader.py` | `quarantine` | `pack_compat_install_resolver` |
| `duplicate.cluster.0260b746b91f764a` | `REFUSAL_SIGNAL_ROUTE_UNAVAILABLE` | `src/signals/transport/__init__.py` | `src/signals/__init__.py` | `quarantine` | `semantic_contracts` |
| `duplicate.cluster.0284e66e92fa82a8` | `system_id` | `game/include/dominium/rules/governance/governance_system.h` | `game/include/dominium/rules/war/war_system.h` | `quarantine` | `semantic_contracts` |
| `duplicate.cluster.02a76b808e9594ff` | `require_keys` | `tools/ci/validate_earth_data.py` | `tools/ci/validate_milky_way_data.py` | `quarantine` | `worldgen_lock_or_overlay` |
| `duplicate.cluster.03a31072d7ac07a9` | `REFUSAL_TEMPLATE_INVALID` | `src/system/templates/__init__.py` | `src/system/templates/template_compiler.py` | `quarantine` | `semantic_contracts` |
| `duplicate.cluster.03ab149d795288bb` | `normalize_list` | `tools/distribution/profile_inspect.py` | `tools/fab/fab_validate.py` | `quarantine` | `pack_compat_install_resolver, semantic_contracts` |
| `duplicate.cluster.03d1718b6abbb996` | `load_fixture_lockfile` | `tools/xstack/testx/tests/pack_compat0_testlib.py` | `tools/xstack/testx/tests/mod_policy0_testlib.py` | `quarantine` | `pack_compat_install_resolver, semantic_contracts` |
| `duplicate.cluster.0631a59ef2fe2be3` | `validate_extensions_map` | `src/meta/extensions/__init__.py` | `src/meta_extensions_engine.py` | `quarantine` | `semantic_contracts` |
| `duplicate.cluster.065d7d23b936c46c` | `property_patch_hash_chain` | `src/geo/overlay/__init__.py` | `src/geo/overlay/overlay_merge_engine.py` | `quarantine` | `pack_compat_install_resolver, worldgen_lock_or_overlay` |
| `duplicate.cluster.06f2c33736385885` | `_write_canonical_json` | `tools/worldgen/worldgen_lock_common.py` | `tools/mvp/update_sim_common.py` | `quarantine` | `trust_enforcement, worldgen_lock_or_overlay` |
| `duplicate.cluster.07162c47dda2a254` | `build_water_view_surface` | `src/worldgen/earth/water/__init__.py` | `src/worldgen/earth/water/water_view_engine.py` | `quarantine` | `worldgen_lock_or_overlay` |
| `duplicate.cluster.07c7e7b9365cb9dc` | `RESOLUTION_POLICY_EXPLICIT_REQUIRED` | `src/lib/provides/__init__.py` | `src/lib/provides/provider_resolution.py` | `quarantine` | `semantic_contracts` |
| `duplicate.cluster.0873f4be504cdfe1` | `_refusal_reason` | `tools/xstack/testx/tests/test_promotion_requires_replication.py` | `tools/xstack/testx/tests/test_proc9_candidate_promotion_requires_replication.py` | `quarantine` | `semantic_contracts` |
| `duplicate.cluster.0954e6658a2eb4fa` | `_material_or_surface_class` | `src/worldgen/earth/climate_field_engine.py` | `src/worldgen/earth/tide_field_engine.py` | `quarantine` | `worldgen_lock_or_overlay` |
| `duplicate.cluster.0a8e71d06f3c5f95` | `_runtime` | `src/server/runtime/tick_loop.py` | `src/server/net/loopback_transport.py` | `quarantine` | `protocol_negotiation, time_anchor` |
| `duplicate.cluster.0b7c5e4a1d1e1287` | `canonical_sha256` | `src/lib/bundle/__init__.py` | `src/lib/bundle/bundle_manifest.py` | `quarantine` | `pack_compat_install_resolver, worldgen_lock_or_overlay` |
| `duplicate.cluster.0bb6cc4d90e796fb` | `run_ops` | `tests/ops/ops_manifest_tests.py` | `tests/ops/compatibility_tests.py` | `quarantine` | `pack_compat_install_resolver, semantic_contracts` |
| `duplicate.cluster.0bbdf1ddf2183c6a` | `tlv_u32` | `setup/packages/scripts/gen_launcher_ui_schema_v1.py` | `game/tests/tests/vectors/gen_tlv_vectors.py` | `quarantine` | `pack_compat_install_resolver, semantic_contracts` |
| `duplicate.cluster.0c2a75870f52b0dd` | `_hash_int` | `src/worldgen/mw/mw_cell_generator.py` | `src/geo/worldgen/worldgen_engine.py` | `quarantine` | `worldgen_lock_or_overlay` |

## Manual Review Queue

| Cluster | Symbol | Canonical | Secondary | Score delta | Reasons |
| --- | --- | --- | --- | --- | --- |
| `duplicate.cluster.1b2cac44712a5224` | `cleanup_temp_repo` | `tools/xstack/testx/tests/mod_policy0_testlib.py` | `tools/xstack/testx/tests/pack_compat0_testlib.py` | `0.0` | `pack_compat_install_resolver, semantic_contracts` |
| `duplicate.cluster.1bec37cc2c0b2390` | `_as_int` | `tools/process/tool_replay_process_window.py` | `tools/process/tool_replay_qc_window.py` | `0.0` | `pack_compat_install_resolver, protocol_negotiation, semantic_contracts, time_anchor, trust_enforcement, worldgen_lock_or_overlay` |
| `duplicate.cluster.1df1d8bf8a458b7f` | `_ensure_repo_root` | `tools/xstack/testx/tests/earth10_testlib.py` | `tools/xstack/testx/tests/gal1_testlib.py` | `0.0` | `worldgen_lock_or_overlay` |
| `duplicate.cluster.1df1d8bf8a458b7f` | `_ensure_repo_root` | `tools/xstack/testx/tests/earth10_testlib.py` | `tools/xstack/testx/tests/sol2_testlib.py` | `0.0` | `worldgen_lock_or_overlay` |
| `duplicate.cluster.247bcbbd2c68dad0` | `_infer` | `tools/xstack/testx/tests/test_accept_candidate_creates_commitments.py` | `tools/xstack/testx/tests/test_formalization_accept_creates_geometry.py` | `0.0` | `worldgen_lock_or_overlay` |
| `duplicate.cluster.3b31f4cda90f9694` | `_canon` | `src/mobility/vehicle/vehicle_engine.py` | `src/models/model_engine.py` | `0.0` | `pack_compat_install_resolver, time_anchor, worldgen_lock_or_overlay` |
| `duplicate.cluster.3da650173c632c38` | `timeval` | `engine/modules/system/dsys_platform_stub.c` | `engine/modules/system/dsys_posix.c` | `0.0` | `time_anchor` |
| `duplicate.cluster.415ed4b579603554` | `_token` | `tools/release/dist_final_common.py` | `tools/review/doc_inventory_common.py` | `0.0` | `pack_compat_install_resolver, protocol_negotiation, semantic_contracts, time_anchor, trust_enforcement` |
| `duplicate.cluster.488b950540e0191a` | `check_invariants` | `tests/app/mmo0_distributed_contract_tests.py` | `tests/app/scale0_contract_tests.py` | `0.0` | `semantic_contracts` |
| `duplicate.cluster.4bf0e6e0bfc79928` | `find_compiler` | `tests/contract/public_header_c89_compile.py` | `tests/contract/public_header_cpp98_compile.py` | `0.0` | `semantic_contracts` |
| `duplicate.cluster.54d0a140b8474567` | `_load_module_registry` | `tools/xstack/testx/tests/test_worldgen_constraints_refusal_codes.py` | `tools/xstack/testx/tests/test_worldgen_multi_seed_determinism.py` | `0.0` | `semantic_contracts, worldgen_lock_or_overlay` |
| `duplicate.cluster.560c7a9931fa7db4` | `_read_json_object` | `tools/data/tool_spice_import.py` | `tools/data/tool_srtm_import.py` | `0.0` | `pack_compat_install_resolver, worldgen_lock_or_overlay` |
| `duplicate.cluster.5906b67b855e1749` | `detect_cycles` | `tools/ci/validate_earth_data.py` | `tools/ci/validate_milky_way_data.py` | `0.0` | `worldgen_lock_or_overlay` |
| `duplicate.cluster.5fe02cf6f8f386dc` | `ensure_clean_dir` | `tests/app/app_cli_contracts.py` | `tests/app/app_ui_contracts.py` | `0.0` | `ipc_attach, semantic_contracts, supervisor` |
| `duplicate.cluster.6878dc4710739dca` | `detect_cycles.visit` | `tools/ci/validate_earth_data.py` | `tools/ci/validate_milky_way_data.py` | `0.0` | `worldgen_lock_or_overlay` |
| `duplicate.cluster.6b1d2d50fe54dcb6` | `parse_units_block` | `tests/contract/namespace_validation.py` | `tests/contract/unit_annotation_validation.py` | `0.0` | `semantic_contracts` |
| `duplicate.cluster.72d38007f31cd15b` | `test_locklist` | `tests/platform/platform_contract_tests.py` | `tests/renderer/renderer_contract_tests.py` | `0.0` | `semantic_contracts` |
| `duplicate.cluster.8923df228349c5e2` | `_as_map` | `tools/process/tool_replay_capsule_window.py` | `tools/release/dist_final_common.py` | `0.0` | `pack_compat_install_resolver, protocol_negotiation, semantic_contracts, time_anchor, trust_enforcement, worldgen_lock_or_overlay` |
| `duplicate.cluster.8b9d9afc9a141b30` | `clone_runtime` | `tools/xstack/testx/tests/net_authoritative_testlib.py` | `tools/xstack/testx/tests/net_hybrid_testlib.py` | `0.0` | `time_anchor` |
| `duplicate.cluster.92bb4be87f2a8aa6` | `_mix_color` | `src/worldgen/earth/lighting/illumination_engine.py` | `src/worldgen/earth/sky/sky_gradient_model.py` | `0.0` | `worldgen_lock_or_overlay` |

