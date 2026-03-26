Status: DERIVED
Last Reviewed: 2026-03-26
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: XI
Replacement Target: XI-2 boundary audit and XI-3 duplicate convergence

# XI-1 Final

- exact_duplicate_groups: `3674`
- near_duplicate_clusters: `2391`
- src_directory_count: `258`
- shadow_module_suspects: `4`

## SRC Directories

- `src` severity=`HIGH` duplicates=`2142`
- `src/logic` severity=`HIGH` duplicates=`224`
- `src/lib` severity=`HIGH` duplicates=`199`
- `src/geo` severity=`HIGH` duplicates=`185`
- `src/meta` severity=`HIGH` duplicates=`154`
- `src/worldgen` severity=`HIGH` duplicates=`148`
- `src/worldgen/earth` severity=`HIGH` duplicates=`137`
- `src/system` severity=`HIGH` duplicates=`119`
- `src/signals` severity=`HIGH` duplicates=`99`
- `src/control` severity=`HIGH` duplicates=`97`
- `src/appshell` severity=`HIGH` duplicates=`82`
- `src/compat` severity=`HIGH` duplicates=`60`
- `src/client` severity=`HIGH` duplicates=`52`
- `src/time` severity=`HIGH` duplicates=`52`
- `src/lib/install` severity=`HIGH` duplicates=`50`
- `src/lib/artifact` severity=`HIGH` duplicates=`45`
- `src/interaction` severity=`HIGH` duplicates=`42`
- `src/geo/worldgen` severity=`HIGH` duplicates=`42`
- `src/geo/overlay` severity=`HIGH` duplicates=`39`
- `src/platform` severity=`HIGH` duplicates=`37`
- `src/lib/bundle` severity=`HIGH` duplicates=`34`
- `src/lib/store` severity=`HIGH` duplicates=`33`
- `src/logic/compile` severity=`HIGH` duplicates=`33`
- `src/lib/provides` severity=`HIGH` duplicates=`33`
- `src/lib/save` severity=`HIGH` duplicates=`31`

## Suspected Shadow Modules

- `src/lib/bundle` -> `tools.lib` score=`0.4279` exact=`6` near=`0`
- `src/client/interaction` -> `tools.xstack.sessionx` score=`0.3105` exact=`4` near=`0`
- `src/compat` -> `tools.xstack.testx.tests` score=`0.3051` exact=`4` near=`0`
- `src/lib/install` -> `tools.lib` score=`0.2585` exact=`3` near=`0`

## Top 20 Convergence Candidates

1. `appshell_product_bootstrap` bucket=`product_entrypoint` score=`945`
2. `wWinMain` bucket=`product_entrypoint` score=`932`
3. `DOWNGRADE_POLICY` bucket=`core_semantic_engine` score=`929`
4. `extract_capabilities` bucket=`core_semantic_engine` score=`928`
5. `DOWNGRADE_BUDGET` bucket=`core_semantic_engine` score=`925`
6. `REFUSAL_CTRL_FIDELITY_DENIED` bucket=`core_semantic_engine` score=`925`
7. `REFUSAL_CTRL_IR_COST_EXCEEDED` bucket=`core_semantic_engine` score=`921`
8. `build_inspection_overlays` bucket=`core_semantic_engine` score=`917`
9. `load_semantic_contract_registry` bucket=`core_semantic_engine` score=`913`
10. `worldgen_stream_seed` bucket=`core_semantic_engine` score=`903`
11. `process_message_verify_claim` bucket=`core_semantic_engine` score=`899`
12. `validate_overlay_manifest_trust` bucket=`core_semantic_engine` score=`895`
13. `RNG_WORLDGEN_GALAXY` bucket=`core_semantic_engine` score=`891`
14. `RNG_WORLDGEN_PLANET` bucket=`core_semantic_engine` score=`891`
15. `RNG_WORLDGEN_SURFACE` bucket=`core_semantic_engine` score=`891`
16. `RNG_WORLDGEN_SYSTEM` bucket=`core_semantic_engine` score=`891`
17. `overlay_base_objects_from_worldgen_result` bucket=`core_semantic_engine` score=`891`
18. `due_bucket_ids` bucket=`core_semantic_engine` score=`881`
19. `DOWNGRADE_RANK_FAIRNESS` bucket=`core_semantic_engine` score=`879`
20. `REFUSAL_OVERLAY_CONFLICT` bucket=`core_semantic_engine` score=`879`

