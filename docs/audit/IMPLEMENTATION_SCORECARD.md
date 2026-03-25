Status: DERIVED
Last Reviewed: 2026-03-26
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: XI
Replacement Target: XI-3 convergence winner selection

# Implementation Scorecard

- duplicate_clusters_ranked: `6066`
- scored_implementations: `24122`
- unique_candidates: `15896`

## Highest Confidence Canonical Implementations

- `verify_pack_set` -> `src/packs/compat/__init__.py` score=`79.05` gap=`19.88` module=`unknown.src.packs.compat`
- `REFUSAL_PACK_REGISTRY_MISSING` -> `src/packs/compat/__init__.py` score=`79.05` gap=`24.65` module=`unknown.src.packs.compat`
- `REFUSAL_SAVE_PACK_LOCK_MISMATCH` -> `src/lib/save/__init__.py` score=`79.05` gap=`21.25` module=`unknown.src.lib.save`
- `DEFAULT_CONTRACT_BUNDLE_REF` -> `src/lib/save/__init__.py` score=`79.05` gap=`16.49` module=`unknown.src.lib.save`
- `load_semantic_contract_registry` -> `tools/compatx/core/semantic_contract_validator.py` score=`84.05` gap=`24.76` module=`tools.compatx.core`
- `mod_manifest_init` -> `game/include/dominium/mods/mod_manifest.h` score=`89.4` gap=`25.1` module=`game.include.dominium.mods`
- `dom_data_schema_find` -> `engine/include/domino/io/data_validate.h` score=`85.95` gap=`15.23` module=`engine.include.domino.io`
- `dom_data_schema_register` -> `engine/include/domino/io/data_validate.h` score=`78.81` gap=`16.49` module=`engine.include.domino.io`
- `generate_explain_artifact` -> `src/meta/explain/__init__.py` score=`79.05` gap=`21.4` module=`unknown.src.meta.explain`
- `REFUSAL_PROVIDES_HASH_MISMATCH` -> `src/lib/provides/__init__.py` score=`79.05` gap=`13.7` module=`unknown.src.lib.provides`
- `REFUSAL_COMPILE_INVALID` -> `src/meta/compile/__init__.py` score=`79.05` gap=`10.95` module=`unknown.src.meta.compile`
- `deterministic_geometry_id` -> `src/mobility/geometry/__init__.py` score=`79.05` gap=`10.48` module=`unknown.src.mobility.geometry`
- `geometry_type_rows_by_id` -> `src/mobility/geometry/__init__.py` score=`79.05` gap=`10.48` module=`unknown.src.mobility.geometry`
- `verify_install_registry` -> `src/lib/install/__init__.py` score=`78.45` gap=`22.56` module=`unknown.src.lib.install`
- `validate_install_manifest` -> `src/lib/install/__init__.py` score=`78.45` gap=`22.56` module=`unknown.src.lib.install`
- `build_protocol_event_record_row` -> `src/logic/protocol/__init__.py` score=`78.45` gap=`8.81` module=`unknown.src.logic.protocol`
- `normalize_protocol_event_record_rows` -> `src/logic/protocol/__init__.py` score=`78.45` gap=`8.81` module=`unknown.src.logic.protocol`
- `_required_file_violations` -> `tools/release/release_manifest_common.py` score=`78.63` gap=`24.46` module=`tools.release`
- `DEFAULT_DIST_ROOT` -> `tools/release/release_manifest_common.py` score=`85.77` gap=`13.75` module=`tools.release`
- `_status_from_findings` -> `tools/xstack/auditx/check.py` score=`85.95` gap=`12.14` module=`tools.xstack.auditx`

## Medium Confidence Merges Required

- `build_degrade_runtime_state` lead=`src/compat/negotiation/__init__.py` score=`65.71` gap=`13.31`
- `REFUSAL_PACK_TRUST_DENIED` lead=`src/packs/compat/__init__.py` score=`67.14` gap=`17.5`
- `REFUSAL_PACK_PROTOCOL_RANGE_MISMATCH` lead=`src/packs/compat/__init__.py` score=`67.14` gap=`15.12`
- `build_compat_status_payload` lead=`src/compat/negotiation/__init__.py` score=`75.24` gap=`21.87`
- `validate_overlay_manifest_trust` lead=`src/geo/overlay/__init__.py` score=`63.93` gap=`6.43`
- `mod_compat_result_to_string` lead=`game/include/dominium/mods/mod_compat.h` score=`76.57` gap=`13.46`
- `mod_compat_refusal_to_string` lead=`game/include/dominium/mods/mod_compat.h` score=`71.81` gap=`8.7`
- `REFUSAL_ARTIFACT_HASH_MISMATCH` lead=`src/lib/artifact/__init__.py` score=`77.44` gap=`19.52`
- `REFUSAL_ARTIFACT_MANIFEST_REQUIRED` lead=`src/lib/artifact/__init__.py` score=`77.44` gap=`14.76`
- `REFUSAL_GC_VERIFY_FAILED` lead=`src/lib/store/__init__.py` score=`71.55` gap=`14.59`
- `PACK_TRUST_DESCRIPTOR_NAME` lead=`src/modding/__init__.py` score=`67.14` gap=`19.28`
- `REFUSAL_MOD_TRUST_DENIED` lead=`src/modding/__init__.py` score=`67.14` gap=`15.94`
- `validate_pack_compat` lead=`src/meta/stability/__init__.py` score=`66.55` gap=`11.91`
- `verify_repro_bundle` lead=`src/diag/__init__.py` score=`65.54` gap=`14.59`
- `verify_license_capability_artifact` lead=`src/security/trust/__init__.py` score=`64.17` gap=`18.71`
- `build_time_stamp_artifact` lead=`src/time/__init__.py` score=`63.57` gap=`17.27`
- `normalize_time_stamp_artifact_rows` lead=`src/time/__init__.py` score=`63.57` gap=`17.27`
- `REFUSAL_PROTOCOL_DEFINITION_INVALID` lead=`src/logic/signal/__init__.py` score=`63.57` gap=`8.21`
- `REFUSAL_GEO_WORLDGEN_INVALID` lead=`src/geo/worldgen/__init__.py` score=`63.15` gap=`5.65`
- `REFUSAL_PACK_NAMESPACE_INVALID` lead=`src/lib/provides/__init__.py` score=`62.98` gap=`6.56`

## Low Confidence Clusters Needing Manual Review

- `REFUSAL_COMPAT_FEATURE_DISABLED` lead=`src/compat/negotiation/degrade_enforcer.py` score=`62.5` gap=`1.55`
- `enforce_negotiated_capability` lead=`src/compat/negotiation/__init__.py` score=`55.45` gap=`6.84`
- `_run_verify` lead=`tools/compatx/compatx.py` score=`68.93` gap=`2.38`
- `DEFAULT_UI_CAPABILITY_PREFERENCE` lead=`src/compat/negotiation/__init__.py` score=`59.48` gap=`7.08`
- `_semver_tuple` lead=`src/compat/capability_negotiation.py` score=`59.29` gap=`10.23`
- `_read_json` lead=`src/compat/capability_negotiation.py` score=`73.57` gap=`2.8`
- `verify_bundle_directory` lead=`src/lib/bundle/__init__.py` score=`76.37` gap=`1.43`
- `REFUSAL_GEO_PATH_INVALID` lead=`src/geo/path/__init__.py` score=`65.18` gap=`2.92`
- `REFUSAL_GEO_METRIC_INVALID` lead=`src/geo/metric/__init__.py` score=`64.58` gap=`2.32`
- `REFUSAL_GEO_GEOMETRY_INVALID` lead=`src/geo/edit/__init__.py` score=`63.15` gap=`3.27`
- `REFUSAL_GEO_PROFILE_MISSING` lead=`src/geo/__init__.py` score=`62.26` gap=`1.25`
- `REFUSAL_GEO_INVALID` lead=`src/geo/__init__.py` score=`62.26` gap=`2.44`
- `REFUSAL_GEO_OVERLAY_INVALID` lead=`src/geo/overlay/__init__.py` score=`61.55` gap=`4.05`
- `REFUSAL_GEO_POSITION_INVALID` lead=`src/geo/frame/frame_engine.py` score=`61.31` gap=`0.89`
- `REFUSAL_GEO_FRAME_INVALID` lead=`src/geo/frame/frame_engine.py` score=`61.31` gap=`0.89`
- `evaluate_vehicle_edge_compatibility` lead=`src/mobility/vehicle/vehicle_engine.py` score=`60.95` gap=`4.68`
- `REFUSAL_GEO_PATH_NOT_FOUND` lead=`src/geo/path/__init__.py` score=`60.42` gap=`2.92`
- `REFUSAL_GEO_PROJECTION_REQUEST_INVALID` lead=`src/geo/projection/__init__.py` score=`60.42` gap=`2.92`
- `REFUSAL_GEO_OBJECT_KIND_MISSING` lead=`src/geo/index/__init__.py` score=`60.42` gap=`2.92`
- `REFUSAL_GEO_CELL_KEY_INVALID` lead=`src/geo/index/__init__.py` score=`60.42` gap=`2.92`

## Focus Areas

### Worldgen

- `normalize_geometry_metric_rows` lead=`src/mobility/geometry/__init__.py` score=`79.05` confidence=`high`
- `build_geometry_metric_row` lead=`src/mobility/geometry/__init__.py` score=`79.05` confidence=`high`
- `d_rng_seed` lead=`engine/include/domino/core/rng.h` score=`91.37` confidence=`medium`
- `_seed_state` lead=`tools/system/tool_run_sys_stress.py` score=`81.19` confidence=`medium`
- `normalize_worldgen_request` lead=`src/geo/worldgen/__init__.py` score=`77.44` confidence=`medium`
- `worldgen_request_hash` lead=`src/geo/worldgen/__init__.py` score=`77.44` confidence=`medium`

### Contracts

- `dom_data_schema_find` lead=`engine/include/domino/io/data_validate.h` score=`85.95` confidence=`high`
- `load_semantic_contract_registry` lead=`tools/compatx/core/semantic_contract_validator.py` score=`84.05` confidence=`high`
- `_refusal` lead=`tools/xstack/ui_bind.py` score=`80.48` confidence=`high`
- `REFUSAL_PACK_REGISTRY_MISSING` lead=`src/packs/compat/__init__.py` score=`79.05` confidence=`high`
- `REFUSAL_COMPILE_INVALID` lead=`src/meta/compile/__init__.py` score=`79.05` confidence=`high`
- `REFUSAL_SAVE_PACK_LOCK_MISMATCH` lead=`src/lib/save/__init__.py` score=`79.05` confidence=`high`

### Protocol Negotiation

- `normalize_protocol_frame_rows` lead=`src/logic/protocol/__init__.py` score=`78.45` confidence=`high`
- `build_protocol_frame_row` lead=`src/logic/protocol/__init__.py` score=`78.45` confidence=`high`
- `normalize_protocol_definition_rows` lead=`src/logic/signal/__init__.py` score=`77.86` confidence=`medium`
- `build_protocol_definition_row` lead=`src/logic/signal/__init__.py` score=`77.86` confidence=`medium`
- `build_negotiation_request` lead=`src/control/negotiation/__init__.py` score=`77.44` confidence=`medium`
- `normalize_logic_protocol_event_record_rows` lead=`src/logic/eval/__init__.py` score=`76.67` confidence=`medium`

### Pack Verification

- `mod_manifest_init` lead=`game/include/dominium/mods/mod_manifest.h` score=`89.4` confidence=`high`
- `render_report_bundle` lead=`tools/review/doc_inventory_common.py` score=`88.33` confidence=`high`
- `REFUSAL_PACK_REGISTRY_MISSING` lead=`src/packs/compat/__init__.py` score=`79.05` confidence=`high`
- `migrate_save_manifest` lead=`src/lib/save/__init__.py` score=`79.05` confidence=`high`
- `generate_explain_artifact` lead=`src/meta/explain/__init__.py` score=`79.05` confidence=`high`
- `REFUSAL_SAVE_PACK_LOCK_MISMATCH` lead=`src/lib/save/__init__.py` score=`79.05` confidence=`high`

### Trust Enforcement

- `verify_pack_set` lead=`src/packs/compat/__init__.py` score=`79.05` confidence=`high`
- `verify_install_registry` lead=`src/lib/install/__init__.py` score=`78.45` confidence=`high`
- `sig_receipt_to_message_value_payload` lead=`src/logic/signal/__init__.py` score=`77.86` confidence=`medium`
- `verify_store_root` lead=`src/lib/store/__init__.py` score=`76.31` confidence=`medium`
- `dom_verify_reduction_rules` lead=`engine/include/domino/execution/access_set.h` score=`76.19` confidence=`medium`
- `process_trust_decay_tick` lead=`src/signals/trust/__init__.py` score=`75.3` confidence=`medium`

### Time Anchors

- `dom_time_core_init` lead=`engine/include/domino/core/dom_time_core.h` score=`91.9` confidence=`medium`
- `_registry_payloads_for_runtime` lead=`tools/xstack/testx/tests/net_authoritative_testlib.py` score=`88.45` confidence=`medium`
- `dom_time_get_act` lead=`engine/include/domino/core/dom_time_core.h` score=`84.76` confidence=`medium`
- `_select_time_control_policy` lead=`tools/xstack/sessionx/creator.py` score=`84.64` confidence=`medium`
- `load_runtime_install_registry` lead=`src/lib/install/__init__.py` score=`78.45` confidence=`medium`
- `build_time_adjust_event` lead=`src/time/__init__.py` score=`77.86` confidence=`medium`

## src/ Directory Impact Summary

- `src/geo` candidates=`785` avg_score=`61.89` low_arch=`785` max_score=`77.44`
- `src/logic` candidates=`763` avg_score=`59.13` low_arch=`763` max_score=`78.45`
- `src/lib` candidates=`742` avg_score=`64.95` low_arch=`742` max_score=`79.05`
- `src/mobility` candidates=`701` avg_score=`61.13` low_arch=`701` max_score=`79.05`
- `src/worldgen` candidates=`697` avg_score=`57.84` low_arch=`697` max_score=`76.9`
- `src/meta` candidates=`567` avg_score=`64.27` low_arch=`567` max_score=`79.64`
- `src/system` candidates=`510` avg_score=`62.42` low_arch=`510` max_score=`79.05`
- `src/signals` candidates=`485` avg_score=`60.24` low_arch=`485` max_score=`75.83`
- `src/control` candidates=`483` avg_score=`62.22` low_arch=`483` max_score=`79.05`
- `src/process` candidates=`391` avg_score=`62.46` low_arch=`391` max_score=`77.62`
- `src/appshell` candidates=`231` avg_score=`63.03` low_arch=`231` max_score=`79.05`
- `src/electric` candidates=`194` avg_score=`58.59` low_arch=`194` max_score=`75.83`

