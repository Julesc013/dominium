Status: Quarantine
Last Reviewed: 2026-03-26
Stability: provisional
Replacement Target: XI-4b manual review resolution

# Quarantine Packet `duplicate.cluster.33b8e7eba7858b47`

- Symbol: `_as_list`
- Cluster Kind: `near`
- Cluster Resolution: `quarantine`
- Risk Level: `HIGH`
- Canonical Candidate: `tools/worldgen/worldgen_lock_common.py`
- Quarantine Reasons: `phase_boundary_deferred, planned_quarantine, requires_single_action_full_gate`
- Planned Action Kinds: `merge, rewire, deprecate, quarantine`

## Competing Files

- `src/appshell/ui_mode_selector.py`
- `src/compat/capability_negotiation.py`
- `src/compat/descriptor/descriptor_engine.py`
- `src/compat/migration_lifecycle.py`
- `src/embodiment/collision/macro_heightfield_provider.py`
- `src/geo/edit/geometry_state_engine.py`
- `src/geo/overlay/overlay_merge_engine.py`
- `src/geo/worldgen/worldgen_engine.py`
- `src/governance/governance_profile.py`
- `src/lib/artifact/artifact_validator.py`
- `src/lib/bundle/bundle_manifest.py`
- `src/lib/install/install_validator.py`
- `src/lib/instance/instance_validator.py`
- `src/lib/provides/provider_resolution.py`
- `src/lib/save/save_validator.py`
- `src/lib/store/reachability_engine.py`
- `src/meta/identity/identity_validator.py`
- `src/meta_extensions_engine.py`
- `src/modding/mod_policy_engine.py`
- `src/packs/compat/pack_compat_validator.py`
- `src/packs/compat/pack_verification_pipeline.py`
- `src/platform/platform_probe.py`
- `src/platform/target_matrix.py`
- `src/release/archive_policy.py`
- `src/release/build_id_engine.py`
- `src/release/component_graph_resolver.py`
- `src/release/release_manifest_engine.py`
- `src/release/update_resolver.py`
- `src/security/trust/license_capability.py`
- `src/security/trust/trust_verifier.py`
- `src/worldgen/earth/climate_field_engine.py`
- `src/worldgen/earth/hydrology_engine.py`
- `src/worldgen/earth/material/material_proxy_engine.py`
- `src/worldgen/earth/water/water_view_engine.py`
- `src/worldgen/galaxy/galaxy_proxy_field_engine.py`
- `src/worldgen/mw/mw_surface_refiner_l3.py`
- `src/worldgen/mw/mw_system_refiner_l2.py`
- `src/worldgen/mw/system_query_engine.py`
- `tools/compat/cap_neg4_common.py`
- `tools/compat/migration_lifecycle_common.py`
- `tools/dist/dist_platform_matrix_common.py`
- `tools/earth/earth9_stress_common.py`
- `tools/engine/numeric_discipline_common.py`
- `tools/governance/governance_model_common.py`
- `tools/lib/store_gc_common.py`
- `tools/meta/observability_common.py`
- `tools/mvp/baseline_universe_common.py`
- `tools/mvp/prod_gate0_common.py`
- `tools/perf/performance_envelope_common.py`
- `tools/release/arch_matrix_common.py`
- `tools/release/archive_policy_common.py`
- `tools/release/distribution_model_common.py`
- `tools/release/platform_formalize_common.py`
- `tools/release/release_identity_common.py`
- `tools/release/update_model_common.py`
- `tools/security/trust_model_common.py`
- `tools/worldgen/earth0_probe.py`
- `tools/worldgen/earth10_probe.py`
- `tools/worldgen/earth1_probe.py`
- `tools/worldgen/earth2_probe.py`
- `tools/worldgen/earth3_probe.py`
- `tools/worldgen/earth7_probe.py`
- `tools/worldgen/earth8_probe.py`
- `tools/worldgen/gal0_probe.py`
- `tools/worldgen/gal1_probe.py`
- `tools/worldgen/worldgen_lock_common.py`
- `tools/xstack/testx/tests/sol0_testlib.py`

## Scorecard

- `tools/worldgen/worldgen_lock_common.py` disposition=`canonical` rank=`1` total_score=`85.24` risk=`HIGH`
- `tools/release/arch_matrix_common.py` disposition=`quarantine` rank=`2` total_score=`84.76` risk=`HIGH`
- `tools/compat/migration_lifecycle_common.py` disposition=`quarantine` rank=`3` total_score=`84.64` risk=`HIGH`
- `tools/mvp/baseline_universe_common.py` disposition=`quarantine` rank=`4` total_score=`84.64` risk=`HIGH`
- `tools/release/archive_policy_common.py` disposition=`quarantine` rank=`5` total_score=`84.64` risk=`HIGH`
- `tools/release/update_model_common.py` disposition=`quarantine` rank=`6` total_score=`84.64` risk=`HIGH`
- `tools/meta/observability_common.py` disposition=`quarantine` rank=`7` total_score=`84.29` risk=`HIGH`
- `tools/lib/store_gc_common.py` disposition=`quarantine` rank=`8` total_score=`83.57` risk=`HIGH`
- `tools/security/trust_model_common.py` disposition=`quarantine` rank=`9` total_score=`83.16` risk=`HIGH`
- `tools/governance/governance_model_common.py` disposition=`quarantine` rank=`10` total_score=`82.5` risk=`HIGH`
- `tools/compat/cap_neg4_common.py` disposition=`quarantine` rank=`11` total_score=`80.96` risk=`HIGH`
- `src/meta_extensions_engine.py` disposition=`quarantine` rank=`12` total_score=`79.64` risk=`HIGH`
- `src/platform/platform_probe.py` disposition=`quarantine` rank=`13` total_score=`78.45` risk=`HIGH`
- `src/compat/migration_lifecycle.py` disposition=`quarantine` rank=`14` total_score=`77.62` risk=`HIGH`
- `tools/perf/performance_envelope_common.py` disposition=`quarantine` rank=`15` total_score=`76.01` risk=`HIGH`
- `tools/dist/dist_platform_matrix_common.py` disposition=`quarantine` rank=`16` total_score=`75.89` risk=`HIGH`
- `tools/release/release_identity_common.py` disposition=`merge` rank=`17` total_score=`75.0` risk=`HIGH`
- `src/platform/target_matrix.py` disposition=`drop` rank=`18` total_score=`75.0` risk=`HIGH`
- `tools/earth/earth9_stress_common.py` disposition=`merge` rank=`19` total_score=`74.58` risk=`HIGH`
- `tools/xstack/testx/tests/sol0_testlib.py` disposition=`drop` rank=`20` total_score=`74.19` risk=`HIGH`
- `tools/mvp/prod_gate0_common.py` disposition=`merge` rank=`21` total_score=`74.05` risk=`HIGH`
- `src/governance/governance_profile.py` disposition=`drop` rank=`22` total_score=`73.87` risk=`HIGH`
- `src/compat/capability_negotiation.py` disposition=`merge` rank=`23` total_score=`73.57` risk=`HIGH`
- `src/release/archive_policy.py` disposition=`drop` rank=`24` total_score=`72.38` risk=`HIGH`
- `tools/release/distribution_model_common.py` disposition=`merge` rank=`25` total_score=`72.02` risk=`HIGH`
- `src/compat/descriptor/descriptor_engine.py` disposition=`drop` rank=`26` total_score=`70.77` risk=`HIGH`
- `src/lib/instance/instance_validator.py` disposition=`drop` rank=`27` total_score=`70.77` risk=`HIGH`
- `src/lib/artifact/artifact_validator.py` disposition=`drop` rank=`28` total_score=`69.82` risk=`HIGH`
- `src/worldgen/earth/water/water_view_engine.py` disposition=`drop` rank=`29` total_score=`69.82` risk=`HIGH`
- `src/lib/save/save_validator.py` disposition=`drop` rank=`30` total_score=`69.7` risk=`HIGH`
- `src/meta/identity/identity_validator.py` disposition=`drop` rank=`31` total_score=`69.64` risk=`HIGH`
- `tools/worldgen/earth0_probe.py` disposition=`drop` rank=`32` total_score=`69.4` risk=`HIGH`
- `tools/engine/numeric_discipline_common.py` disposition=`merge` rank=`33` total_score=`68.94` risk=`HIGH`
- `src/lib/provides/provider_resolution.py` disposition=`drop` rank=`34` total_score=`68.69` risk=`HIGH`
- `tools/release/platform_formalize_common.py` disposition=`merge` rank=`35` total_score=`67.45` risk=`HIGH`
- `src/geo/worldgen/worldgen_engine.py` disposition=`drop` rank=`36` total_score=`67.26` risk=`HIGH`
- `src/release/build_id_engine.py` disposition=`drop` rank=`37` total_score=`67.26` risk=`HIGH`
- `src/release/component_graph_resolver.py` disposition=`drop` rank=`38` total_score=`66.43` risk=`HIGH`
- `tools/worldgen/earth8_probe.py` disposition=`merge` rank=`39` total_score=`65.46` risk=`HIGH`
- `src/security/trust/trust_verifier.py` disposition=`drop` rank=`40` total_score=`65.42` risk=`HIGH`
- `tools/worldgen/earth2_probe.py` disposition=`merge` rank=`41` total_score=`63.94` risk=`HIGH`
- `tools/worldgen/earth1_probe.py` disposition=`drop` rank=`42` total_score=`63.35` risk=`HIGH`
- `tools/worldgen/gal1_probe.py` disposition=`merge` rank=`43` total_score=`63.2` risk=`HIGH`
- `tools/worldgen/earth3_probe.py` disposition=`merge` rank=`44` total_score=`62.98` risk=`HIGH`
- `src/release/release_manifest_engine.py` disposition=`drop` rank=`45` total_score=`62.56` risk=`HIGH`
- `tools/worldgen/earth10_probe.py` disposition=`merge` rank=`46` total_score=`62.44` risk=`HIGH`
- `tools/worldgen/earth7_probe.py` disposition=`merge` rank=`47` total_score=`62.38` risk=`HIGH`
- `src/appshell/ui_mode_selector.py` disposition=`drop` rank=`48` total_score=`61.67` risk=`HIGH`
- `src/worldgen/earth/climate_field_engine.py` disposition=`drop` rank=`49` total_score=`59.64` risk=`HIGH`
- `src/packs/compat/pack_verification_pipeline.py` disposition=`drop` rank=`50` total_score=`59.17` risk=`HIGH`
- `src/worldgen/mw/system_query_engine.py` disposition=`drop` rank=`51` total_score=`59.05` risk=`HIGH`
- `src/lib/install/install_validator.py` disposition=`merge` rank=`52` total_score=`58.27` risk=`HIGH`
- `src/worldgen/earth/hydrology_engine.py` disposition=`drop` rank=`53` total_score=`58.1` risk=`HIGH`
- `tools/worldgen/gal0_probe.py` disposition=`merge` rank=`54` total_score=`58.02` risk=`HIGH`
- `src/geo/edit/geometry_state_engine.py` disposition=`drop` rank=`55` total_score=`57.56` risk=`HIGH`
- `src/packs/compat/pack_compat_validator.py` disposition=`drop` rank=`56` total_score=`57.38` risk=`HIGH`
- `src/worldgen/mw/mw_surface_refiner_l3.py` disposition=`drop` rank=`57` total_score=`57.2` risk=`HIGH`
- `src/worldgen/mw/mw_system_refiner_l2.py` disposition=`drop` rank=`58` total_score=`57.06` risk=`HIGH`
- `src/worldgen/earth/material/material_proxy_engine.py` disposition=`drop` rank=`59` total_score=`55.54` risk=`HIGH`
- `src/geo/overlay/overlay_merge_engine.py` disposition=`drop` rank=`60` total_score=`54.94` risk=`HIGH`
- `src/lib/store/reachability_engine.py` disposition=`drop` rank=`61` total_score=`54.29` risk=`HIGH`
- `src/release/update_resolver.py` disposition=`drop` rank=`62` total_score=`54.29` risk=`HIGH`
- `src/modding/mod_policy_engine.py` disposition=`drop` rank=`63` total_score=`51.2` risk=`HIGH`
- `src/worldgen/galaxy/galaxy_proxy_field_engine.py` disposition=`drop` rank=`64` total_score=`51.14` risk=`HIGH`
- `src/security/trust/license_capability.py` disposition=`drop` rank=`65` total_score=`49.77` risk=`HIGH`
- `src/embodiment/collision/macro_heightfield_provider.py` disposition=`drop` rank=`66` total_score=`49.75` risk=`HIGH`
- `src/lib/bundle/bundle_manifest.py` disposition=`merge` rank=`67` total_score=`46.76` risk=`HIGH`

## Usage Sites

- Build Targets: `none`
- Docs: `docs/ARCHITECTURE.md, docs/STATUS_NOW.md, docs/appshell/CLI_REFERENCE.md, docs/appshell/TOOL_REFERENCE.md, docs/architecture/CANON_INDEX.md, docs/architecture/REPO_INTENT.md, docs/architecture/lockfile.md, docs/architecture/registry_compile.md`

## Tests Involved

- `python tools/appshell/tool_run_ipc_unify.py --repo-root .`
- `python tools/appshell/tool_run_supervisor_hardening.py --repo-root .`
- `python tools/compat/tool_run_interop_stress.py --repo-root .`
- `python tools/convergence/tool_run_convergence_gate.py --repo-root .`
- `python tools/mvp/tool_run_all_stress.py --repo-root .`
- `python tools/mvp/tool_run_disaster_suite.py --repo-root .`
- `python tools/mvp/tool_run_product_boot_matrix.py --repo-root .`
- `python tools/mvp/tool_verify_baseline_universe.py --repo-root .`
- `python tools/mvp/tool_verify_gameplay_loop.py --repo-root .`
- `python tools/security/tool_run_trust_strict_suite.py --repo-root .`
- `python tools/time/tool_verify_longrun_ticks.py --repo-root .`
- `python tools/validation/tool_run_validation.py --repo-root . --profile STRICT`
- `python tools/worldgen/tool_verify_worldgen_lock.py --repo-root .`
- `python tools/xstack/testx/runner.py --repo-root . --profile FAST --cache off --subset test_convergence_plan_deterministic,test_decision_rules_stable`

## Recommended Decision Options

- Review file-local deltas and port only unique behavior into the canonical file.
- Rewire call sites only after confirming the secondary file is not an active product entrypoint.
- Deprecate the secondary file only after it is removed from default build targets and no longer carries unrelated active symbols.
- If ambiguity remains after review, keep the cluster quarantined for XI-4b instead of forcing convergence.
