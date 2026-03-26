# XI-3 Final

- Generated: 2026-03-26
- Duplicate clusters: 6065
- Keep-only clusters: 1945
- Merge-required clusters: 2764
- Quarantine clusters: 1356

## Top HIGH Risk Items

- `duplicate.cluster.0075f9b78b2784df` -> canonical `src/meta_extensions_engine.py` vs secondary `src/meta/extensions/extensions_engine.py` (quarantine)
- `duplicate.cluster.0253285ae8918910` -> canonical `tools/xstack/registry_compile/bundle_profile.py` vs secondary `tools/xstack/pack_loader/loader.py` (quarantine)
- `duplicate.cluster.0260b746b91f764a` -> canonical `src/signals/transport/__init__.py` vs secondary `src/signals/__init__.py` (quarantine)
- `duplicate.cluster.0284e66e92fa82a8` -> canonical `game/include/dominium/rules/governance/governance_system.h` vs secondary `game/include/dominium/rules/war/war_system.h` (quarantine)
- `duplicate.cluster.02a76b808e9594ff` -> canonical `tools/ci/validate_earth_data.py` vs secondary `tools/ci/validate_milky_way_data.py` (quarantine)
- `duplicate.cluster.03a31072d7ac07a9` -> canonical `src/system/templates/__init__.py` vs secondary `src/system/templates/template_compiler.py` (quarantine)
- `duplicate.cluster.03ab149d795288bb` -> canonical `tools/distribution/profile_inspect.py` vs secondary `tools/fab/fab_validate.py` (quarantine)
- `duplicate.cluster.03d1718b6abbb996` -> canonical `tools/xstack/testx/tests/pack_compat0_testlib.py` vs secondary `tools/xstack/testx/tests/mod_policy0_testlib.py` (quarantine)
- `duplicate.cluster.0631a59ef2fe2be3` -> canonical `src/meta/extensions/__init__.py` vs secondary `src/meta_extensions_engine.py` (quarantine)
- `duplicate.cluster.065d7d23b936c46c` -> canonical `src/geo/overlay/__init__.py` vs secondary `src/geo/overlay/overlay_merge_engine.py` (quarantine)
- `duplicate.cluster.06f2c33736385885` -> canonical `tools/worldgen/worldgen_lock_common.py` vs secondary `tools/mvp/update_sim_common.py` (quarantine)
- `duplicate.cluster.07162c47dda2a254` -> canonical `src/worldgen/earth/water/__init__.py` vs secondary `src/worldgen/earth/water/water_view_engine.py` (quarantine)
- `duplicate.cluster.07c7e7b9365cb9dc` -> canonical `src/lib/provides/__init__.py` vs secondary `src/lib/provides/provider_resolution.py` (quarantine)
- `duplicate.cluster.0873f4be504cdfe1` -> canonical `tools/xstack/testx/tests/test_promotion_requires_replication.py` vs secondary `tools/xstack/testx/tests/test_proc9_candidate_promotion_requires_replication.py` (quarantine)
- `duplicate.cluster.0954e6658a2eb4fa` -> canonical `src/worldgen/earth/climate_field_engine.py` vs secondary `src/worldgen/earth/tide_field_engine.py` (quarantine)
- `duplicate.cluster.0a8e71d06f3c5f95` -> canonical `src/server/runtime/tick_loop.py` vs secondary `src/server/net/loopback_transport.py` (quarantine)
- `duplicate.cluster.0b7c5e4a1d1e1287` -> canonical `src/lib/bundle/__init__.py` vs secondary `src/lib/bundle/bundle_manifest.py` (quarantine)
- `duplicate.cluster.0bb6cc4d90e796fb` -> canonical `tests/ops/ops_manifest_tests.py` vs secondary `tests/ops/compatibility_tests.py` (quarantine)
- `duplicate.cluster.0bbdf1ddf2183c6a` -> canonical `setup/packages/scripts/gen_launcher_ui_schema_v1.py` vs secondary `game/tests/tests/vectors/gen_tlv_vectors.py` (quarantine)
- `duplicate.cluster.0c2a75870f52b0dd` -> canonical `src/worldgen/mw/mw_cell_generator.py` vs secondary `src/geo/worldgen/worldgen_engine.py` (quarantine)

## Recommended Manual Review

- `duplicate.cluster.1b2cac44712a5224` `tools/xstack/testx/tests/pack_compat0_testlib.py` score delta `0.0`
- `duplicate.cluster.1bec37cc2c0b2390` `tools/process/tool_replay_qc_window.py` score delta `0.0`
- `duplicate.cluster.1df1d8bf8a458b7f` `tools/xstack/testx/tests/gal1_testlib.py` score delta `0.0`
- `duplicate.cluster.1df1d8bf8a458b7f` `tools/xstack/testx/tests/sol2_testlib.py` score delta `0.0`
- `duplicate.cluster.247bcbbd2c68dad0` `tools/xstack/testx/tests/test_formalization_accept_creates_geometry.py` score delta `0.0`
- `duplicate.cluster.3b31f4cda90f9694` `src/models/model_engine.py` score delta `0.0`
- `duplicate.cluster.3da650173c632c38` `engine/modules/system/dsys_posix.c` score delta `0.0`
- `duplicate.cluster.415ed4b579603554` `tools/review/doc_inventory_common.py` score delta `0.0`
- `duplicate.cluster.488b950540e0191a` `tests/app/scale0_contract_tests.py` score delta `0.0`
- `duplicate.cluster.4bf0e6e0bfc79928` `tests/contract/public_header_cpp98_compile.py` score delta `0.0`
- `duplicate.cluster.54d0a140b8474567` `tools/xstack/testx/tests/test_worldgen_multi_seed_determinism.py` score delta `0.0`
- `duplicate.cluster.560c7a9931fa7db4` `tools/data/tool_srtm_import.py` score delta `0.0`
- `duplicate.cluster.5906b67b855e1749` `tools/ci/validate_milky_way_data.py` score delta `0.0`
- `duplicate.cluster.5fe02cf6f8f386dc` `tests/app/app_ui_contracts.py` score delta `0.0`
- `duplicate.cluster.6878dc4710739dca` `tools/ci/validate_milky_way_data.py` score delta `0.0`
- `duplicate.cluster.6b1d2d50fe54dcb6` `tests/contract/unit_annotation_validation.py` score delta `0.0`
- `duplicate.cluster.72d38007f31cd15b` `tests/renderer/renderer_contract_tests.py` score delta `0.0`
- `duplicate.cluster.8923df228349c5e2` `tools/release/dist_final_common.py` score delta `0.0`
- `duplicate.cluster.8b9d9afc9a141b30` `tools/xstack/testx/tests/net_hybrid_testlib.py` score delta `0.0`
- `duplicate.cluster.92bb4be87f2a8aa6` `src/worldgen/earth/sky/sky_gradient_model.py` score delta `0.0`

## Readiness

- Ξ-4 readiness: `ready_with_manual_review`

