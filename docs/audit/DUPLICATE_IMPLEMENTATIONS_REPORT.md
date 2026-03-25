Status: DERIVED
Last Reviewed: 2026-03-26
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: XI
Replacement Target: XI-3 duplicate convergence plan

# Duplicate Implementations Report

- exact_duplicate_groups: `3674`
- near_duplicate_clusters: `2392`
- shadow_module_suspects: `4`
- src_directory_count: `258`

## Ranked Convergence Candidates

_XI-1 does not choose winners; these are evidence-ranked candidates only._

1. `appshell_product_bootstrap` bucket=`product_entrypoint` score=`945`
   duplicates: `3` definitions across `3` modules
   build_targets/products: `none` / `none`
   docs_refs: `docs/audit/ENTRYPOINT_UNIFY_FINAL.md, docs/audit/ENTRYPOINT_UNIFY_MAP.md`
   architecture_placement_violation: `yes`
2. `wWinMain` bucket=`product_entrypoint` score=`932`
   duplicates: `5` definitions across `5` modules
   build_targets/products: `client_app_win32, launcher_app_win32, server_app_win32, setup_app_win32, tools_app_win32` / `client, launcher, server, setup, tools`
   docs_refs: `none`
   architecture_placement_violation: `no`
3. `DOWNGRADE_POLICY` bucket=`core_semantic_engine` score=`929`
   duplicates: `5` definitions across `3` modules
   build_targets/products: `none` / `none`
   docs_refs: `docs/audit/CONTROL_PLANE_CONSTITUTION_BASELINE.md, docs/audit/CTRL3_RETRO_AUDIT.md, docs/audit/VIEW_EPISTEMIC_CONTROL_BASELINE.md, docs/contracts/refusal_contract.md`
   architecture_placement_violation: `no`
4. `extract_capabilities` bucket=`core_semantic_engine` score=`928`
   duplicates: `8` definitions across `5` modules
   build_targets/products: `none` / `none`
   docs_refs: `none`
   architecture_placement_violation: `no`
5. `DOWNGRADE_BUDGET` bucket=`core_semantic_engine` score=`925`
   duplicates: `5` definitions across `3` modules
   build_targets/products: `none` / `none`
   docs_refs: `docs/audit/CONTROL_NEGOTIATION_BASELINE.md, docs/audit/CONTROL_PLANE_CONSTITUTION_BASELINE.md, docs/contracts/refusal_contract.md`
   architecture_placement_violation: `no`
6. `REFUSAL_CTRL_FIDELITY_DENIED` bucket=`core_semantic_engine` score=`925`
   duplicates: `5` definitions across `3` modules
   build_targets/products: `none` / `none`
   docs_refs: `docs/audit/CONTROL_PLANE_CONSTITUTION_BASELINE.md, docs/audit/FIDELITY_ARBITRATION_BASELINE.md, docs/contracts/refusal_contract.md`
   architecture_placement_violation: `no`
7. `REFUSAL_CTRL_IR_COST_EXCEEDED` bucket=`core_semantic_engine` score=`921`
   duplicates: `5` definitions across `3` modules
   build_targets/products: `none` / `none`
   docs_refs: `docs/audit/CONTROL_IR_BASELINE.md, docs/contracts/refusal_contract.md`
   architecture_placement_violation: `no`
8. `build_inspection_overlays` bucket=`core_semantic_engine` score=`917`
   duplicates: `2` definitions across `2` modules
   build_targets/products: `none` / `none`
   docs_refs: `docs/audit/PLANNING_EXECUTION_BASELINE.md`
   architecture_placement_violation: `yes`
9. `load_semantic_contract_registry` bucket=`core_semantic_engine` score=`913`
   duplicates: `2` definitions across `2` modules
   build_targets/products: `none` / `none`
   docs_refs: `none`
   architecture_placement_violation: `yes`
10. `worldgen_stream_seed` bucket=`core_semantic_engine` score=`903`
   duplicates: `3` definitions across `2` modules
   build_targets/products: `none` / `none`
   docs_refs: `docs/audit/MW0_RETRO_AUDIT.md, docs/audit/WORLDGEN_LOCK0_RETRO_AUDIT.md, docs/worldgen/WORLDGEN_LOCK_v0_0_0.md`
   architecture_placement_violation: `no`
11. `process_message_verify_claim` bucket=`core_semantic_engine` score=`899`
   duplicates: `3` definitions across `2` modules
   build_targets/products: `none` / `none`
   docs_refs: `docs/audit/TRUST_BELIEF_BASELINE.md, docs/signals/TRUST_AND_BELIEF_MODEL.md`
   architecture_placement_violation: `no`
12. `validate_overlay_manifest_trust` bucket=`core_semantic_engine` score=`895`
   duplicates: `3` definitions across `2` modules
   build_targets/products: `none` / `none`
   docs_refs: `docs/audit/COMPAT_SEM3_RETRO_AUDIT.md`
   architecture_placement_violation: `no`
13. `RNG_WORLDGEN_GALAXY` bucket=`core_semantic_engine` score=`891`
   duplicates: `3` definitions across `2` modules
   build_targets/products: `none` / `none`
   docs_refs: `docs/audit/GALAXY_OBJECT_STUBS_BASELINE.md, docs/audit/GEO8_RETRO_AUDIT.md, docs/audit/MW0_RETRO_AUDIT.md, docs/audit/MW2_RETRO_AUDIT.md`
   architecture_placement_violation: `no`
14. `RNG_WORLDGEN_PLANET` bucket=`core_semantic_engine` score=`891`
   duplicates: `3` definitions across `2` modules
   build_targets/products: `none` / `none`
   docs_refs: `docs/audit/GEO8_RETRO_AUDIT.md, docs/audit/MW0_RETRO_AUDIT.md, docs/audit/MW2_RETRO_AUDIT.md, docs/audit/WORLDGEN_LOCK0_RETRO_AUDIT.md`
   architecture_placement_violation: `no`
15. `RNG_WORLDGEN_SURFACE` bucket=`core_semantic_engine` score=`891`
   duplicates: `3` definitions across `2` modules
   build_targets/products: `none` / `none`
   docs_refs: `docs/audit/GEO8_RETRO_AUDIT.md, docs/audit/MW0_RETRO_AUDIT.md, docs/audit/MW2_RETRO_AUDIT.md, docs/audit/WORLDGEN_LOCK0_RETRO_AUDIT.md`
   architecture_placement_violation: `no`
16. `RNG_WORLDGEN_SYSTEM` bucket=`core_semantic_engine` score=`891`
   duplicates: `3` definitions across `2` modules
   build_targets/products: `none` / `none`
   docs_refs: `docs/audit/GEO8_RETRO_AUDIT.md, docs/audit/MW0_RETRO_AUDIT.md, docs/audit/MW2_RETRO_AUDIT.md, docs/audit/WORLDGEN_LOCK0_RETRO_AUDIT.md`
   architecture_placement_violation: `no`
17. `overlay_base_objects_from_worldgen_result` bucket=`core_semantic_engine` score=`891`
   duplicates: `3` definitions across `2` modules
   build_targets/products: `none` / `none`
   docs_refs: `none`
   architecture_placement_violation: `no`
18. `due_bucket_ids` bucket=`core_semantic_engine` score=`881`
   duplicates: `4` definitions across `2` modules
   build_targets/products: `none` / `none`
   docs_refs: `none`
   architecture_placement_violation: `no`
19. `DOWNGRADE_RANK_FAIRNESS` bucket=`core_semantic_engine` score=`879`
   duplicates: `3` definitions across `2` modules
   build_targets/products: `none` / `none`
   docs_refs: `docs/audit/CONTROL_PLANE_CONSTITUTION_BASELINE.md, docs/audit/VIEW_EPISTEMIC_CONTROL_BASELINE.md, docs/contracts/refusal_contract.md`
   architecture_placement_violation: `no`
20. `REFUSAL_OVERLAY_CONFLICT` bucket=`core_semantic_engine` score=`879`
   duplicates: `3` definitions across `2` modules
   build_targets/products: `none` / `none`
   docs_refs: `docs/audit/OVERLAY_CONFLICT_BASELINE.md, docs/geo/OVERLAY_CONFLICT_POLICIES.md, docs/governance/REPOX_RULESETS.md`
   architecture_placement_violation: `no`

## Core Semantic Engines

- `DOWNGRADE_POLICY` files=`5` products=`none` docs=`docs/audit/CONTROL_PLANE_CONSTITUTION_BASELINE.md,docs/audit/CTRL3_RETRO_AUDIT.md` placement_violation=`no`
- `extract_capabilities` files=`8` products=`none` docs=`none` placement_violation=`no`
- `DOWNGRADE_BUDGET` files=`5` products=`none` docs=`docs/audit/CONTROL_NEGOTIATION_BASELINE.md,docs/audit/CONTROL_PLANE_CONSTITUTION_BASELINE.md` placement_violation=`no`
- `REFUSAL_CTRL_FIDELITY_DENIED` files=`5` products=`none` docs=`docs/audit/CONTROL_PLANE_CONSTITUTION_BASELINE.md,docs/audit/FIDELITY_ARBITRATION_BASELINE.md` placement_violation=`no`
- `REFUSAL_CTRL_IR_COST_EXCEEDED` files=`5` products=`none` docs=`docs/audit/CONTROL_IR_BASELINE.md,docs/contracts/refusal_contract.md` placement_violation=`no`
- `build_inspection_overlays` files=`2` products=`none` docs=`docs/audit/PLANNING_EXECUTION_BASELINE.md` placement_violation=`yes`
- `load_semantic_contract_registry` files=`2` products=`none` docs=`none` placement_violation=`yes`
- `worldgen_stream_seed` files=`3` products=`none` docs=`docs/audit/MW0_RETRO_AUDIT.md,docs/audit/WORLDGEN_LOCK0_RETRO_AUDIT.md` placement_violation=`no`

## Product Entrypoints And Shells

- `appshell_product_bootstrap` files=`3` products=`none` docs=`docs/audit/ENTRYPOINT_UNIFY_FINAL.md,docs/audit/ENTRYPOINT_UNIFY_MAP.md` placement_violation=`yes`
- `wWinMain` files=`5` products=`client,launcher,server,setup` docs=`none` placement_violation=`no`
- `dom_app_ui_locale_text` files=`3` products=`client,launcher,tools` docs=`none` placement_violation=`no`
- `now_timestamp` files=`7` products=`none` docs=`none` placement_violation=`no`
- `refusal_payload` files=`6` products=`none` docs=`none` placement_violation=`no`
- `sorted_unique` files=`5` products=`none` docs=`none` placement_violation=`no`
- `dom_app_ensure_directory_exists` files=`3` products=`client,server` docs=`none` placement_violation=`no`
- `tm` files=`2` products=`client,server` docs=`none` placement_violation=`no`

## Domain Systems

- `is_sim_affecting` files=`9` products=`game` docs=`none` placement_violation=`no`
- `system_id` files=`9` products=`game` docs=`none` placement_violation=`no`
- `degrade` files=`8` products=`none` docs=`none` placement_violation=`no`
- `get_next_due_tick` files=`8` products=`none` docs=`none` placement_violation=`no`
- `last_emitted_task_count` files=`6` products=`none` docs=`none` placement_violation=`no`
- `law_targets` files=`8` products=`none` docs=`none` placement_violation=`no`
- `migration_state` files=`7` products=`none` docs=`none` placement_violation=`no`
- `set_next_due_tick` files=`7` products=`none` docs=`none` placement_violation=`no`

## Tools And Docs

- `clear` files=`6` products=`none` docs=`none` placement_violation=`yes`
- `resolve_profile` files=`3` products=`none` docs=`none` placement_violation=`yes`
- `in` files=`9` products=`game,setup` docs=`none` placement_violation=`no`
- `REFUSAL_GC_EXPLICIT_FLAG` files=`3` products=`none` docs=`none` placement_violation=`yes`
- `ARTIFACT_KIND_IDS` files=`2` products=`none` docs=`none` placement_violation=`yes`
- `DECISION_MIGRATE` files=`2` products=`none` docs=`none` placement_violation=`yes`
- `DECISION_READ_ONLY` files=`2` products=`none` docs=`none` placement_violation=`yes`
- `DEFAULT_RELEASE_CHANNEL` files=`2` products=`none` docs=`none` placement_violation=`yes`

## Future RepoX Recommendations

- `INV-NO-SRC-DIRECTORY` except test-only trees.
- `INV-SINGLE-SEMANTIC-ENGINE` for negotiation, overlay/merge, identity, worldgen, time-anchor, pack, and trust surfaces.
- `INV-NO-DUPLICATE-SYMBOL-DEFINITIONS` across production-visible modules.

