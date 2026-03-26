Status: Quarantine
Last Reviewed: 2026-03-26
Stability: provisional
Replacement Target: XI-4b manual review resolution

# Quarantine Packet `duplicate.cluster.e587909981aa4b90`

- Symbol: `require`
- Cluster Kind: `near`
- Cluster Resolution: `quarantine`
- Risk Level: `HIGH`
- Canonical Candidate: `tests/integration/client_refusal_codes_tests.py`
- Quarantine Reasons: `phase_boundary_deferred, planned_quarantine, requires_single_action_full_gate`
- Planned Action Kinds: `merge, rewire, deprecate, quarantine`

## Competing Files

- `tests/contract/srz_contract_tests.py`
- `tests/determinism/srz_determinism_tests.py`
- `tests/integration/animal_agent_tests.py`
- `tests/integration/autonomy_field_tests.py`
- `tests/integration/blueprint_refusal_tests.py`
- `tests/integration/capability_runtime_enforcement_tests.py`
- `tests/integration/client_flow_smoke_tests.py`
- `tests/integration/client_parity_tests.py`
- `tests/integration/client_refusal_codes_tests.py`
- `tests/integration/climate_field_tests.py`
- `tests/integration/conflict_field_tests.py`
- `tests/integration/crafting_field_tests.py`
- `tests/integration/economy_field_tests.py`
- `tests/integration/energy_field_tests.py`
- `tests/integration/exploration_baseline_tests.py`
- `tests/integration/exploration_scale_guard_tests.py`
- `tests/integration/exploration_scaling_tests.py`
- `tests/integration/fluid_field_tests.py`
- `tests/integration/freecam_epistemics_tests.py`
- `tests/integration/geology_field_tests.py`
- `tests/integration/hazard_field_tests.py`
- `tests/integration/heat_field_tests.py`
- `tests/integration/history_field_tests.py`
- `tests/integration/institution_field_tests.py`
- `tests/integration/interaction_baseline_tests.py`
- `tests/integration/interaction_scaling_tests.py`
- `tests/integration/knowledge_field_tests.py`
- `tests/integration/mining_field_tests.py`
- `tests/integration/network_field_tests.py`
- `tests/integration/risk_field_tests.py`
- `tests/integration/server_discovery_tests.py`
- `tests/integration/server_tools_operational_tests.py`
- `tests/integration/signal_baseline_tests.py`
- `tests/integration/signal_scaling_tests.py`
- `tests/integration/srz_field_tests.py`
- `tests/integration/standard_field_tests.py`
- `tests/integration/structure_field_tests.py`
- `tests/integration/terrain_geometry_tests.py`
- `tests/integration/travel_field_tests.py`
- `tests/integration/trust_field_tests.py`
- `tests/integration/vegetation_field_tests.py`
- `tests/integration/weather_event_tests.py`
- `tests/integration/world_manager_tests.py`
- `tests/invariant/srz_execution_mode_invariant.py`
- `tests/perf/animal_perf_tests.py`
- `tests/perf/autonomy_perf_tests.py`
- `tests/perf/climate_perf_tests.py`
- `tests/perf/conflict_perf_tests.py`
- `tests/perf/crafting_perf_tests.py`
- `tests/perf/economy_perf_tests.py`
- `tests/perf/energy_perf_tests.py`
- `tests/perf/exploration_fixture_contracts.py`
- `tests/perf/fluid_perf_tests.py`
- `tests/perf/geology_perf_tests.py`
- `tests/perf/hazard_perf_tests.py`
- `tests/perf/heat_perf_tests.py`
- `tests/perf/history_perf_tests.py`
- `tests/perf/institution_perf_tests.py`
- `tests/perf/knowledge_perf_tests.py`
- `tests/perf/mining_perf_tests.py`
- `tests/perf/network_perf_tests.py`
- `tests/perf/risk_perf_tests.py`
- `tests/perf/srz_perf_tests.py`
- `tests/perf/standard_perf_tests.py`
- `tests/perf/structure_perf_tests.py`
- `tests/perf/terrain_perf_tests.py`
- `tests/perf/travel_perf_tests.py`
- `tests/perf/trust_perf_tests.py`
- `tests/perf/vegetation_perf_tests.py`
- `tests/perf/weather_perf_tests.py`

## Scorecard

- `tests/integration/client_refusal_codes_tests.py` disposition=`canonical` rank=`1` total_score=`72.67` risk=`HIGH`
- `tests/integration/weather_event_tests.py` disposition=`quarantine` rank=`2` total_score=`67.39` risk=`HIGH`
- `tests/perf/network_perf_tests.py` disposition=`quarantine` rank=`3` total_score=`67.39` risk=`HIGH`
- `tests/integration/exploration_baseline_tests.py` disposition=`quarantine` rank=`4` total_score=`66.43` risk=`HIGH`
- `tests/integration/energy_field_tests.py` disposition=`quarantine` rank=`5` total_score=`63.6` risk=`HIGH`
- `tests/integration/history_field_tests.py` disposition=`quarantine` rank=`6` total_score=`63.6` risk=`HIGH`
- `tests/integration/interaction_baseline_tests.py` disposition=`quarantine` rank=`7` total_score=`63.6` risk=`HIGH`
- `tests/integration/signal_baseline_tests.py` disposition=`quarantine` rank=`8` total_score=`63.6` risk=`HIGH`
- `tests/integration/standard_field_tests.py` disposition=`quarantine` rank=`9` total_score=`63.37` risk=`HIGH`
- `tests/integration/institution_field_tests.py` disposition=`quarantine` rank=`10` total_score=`63.0` risk=`HIGH`
- `tests/determinism/srz_determinism_tests.py` disposition=`merge` rank=`11` total_score=`62.63` risk=`HIGH`
- `tests/integration/client_parity_tests.py` disposition=`merge` rank=`12` total_score=`62.63` risk=`HIGH`
- `tests/perf/conflict_perf_tests.py` disposition=`merge` rank=`13` total_score=`62.63` risk=`HIGH`
- `tests/perf/structure_perf_tests.py` disposition=`merge` rank=`14` total_score=`62.63` risk=`HIGH`
- `tests/perf/terrain_perf_tests.py` disposition=`merge` rank=`15` total_score=`62.63` risk=`HIGH`
- `tests/integration/client_flow_smoke_tests.py` disposition=`drop` rank=`16` total_score=`62.18` risk=`HIGH`
- `tests/integration/trust_field_tests.py` disposition=`merge` rank=`17` total_score=`62.18` risk=`HIGH`
- `tests/contract/srz_contract_tests.py` disposition=`merge` rank=`18` total_score=`61.21` risk=`HIGH`
- `tests/integration/blueprint_refusal_tests.py` disposition=`drop` rank=`19` total_score=`61.21` risk=`HIGH`
- `tests/integration/capability_runtime_enforcement_tests.py` disposition=`merge` rank=`20` total_score=`61.21` risk=`HIGH`
- `tests/integration/climate_field_tests.py` disposition=`merge` rank=`21` total_score=`61.21` risk=`HIGH`
- `tests/integration/conflict_field_tests.py` disposition=`merge` rank=`22` total_score=`61.21` risk=`HIGH`
- `tests/integration/fluid_field_tests.py` disposition=`merge` rank=`23` total_score=`61.21` risk=`HIGH`
- `tests/integration/hazard_field_tests.py` disposition=`merge` rank=`24` total_score=`61.21` risk=`HIGH`
- `tests/integration/heat_field_tests.py` disposition=`merge` rank=`25` total_score=`61.21` risk=`HIGH`
- `tests/integration/knowledge_field_tests.py` disposition=`merge` rank=`26` total_score=`61.21` risk=`HIGH`
- `tests/integration/network_field_tests.py` disposition=`merge` rank=`27` total_score=`61.21` risk=`HIGH`
- `tests/integration/risk_field_tests.py` disposition=`merge` rank=`28` total_score=`61.21` risk=`HIGH`
- `tests/integration/structure_field_tests.py` disposition=`merge` rank=`29` total_score=`61.21` risk=`HIGH`
- `tests/integration/terrain_geometry_tests.py` disposition=`merge` rank=`30` total_score=`61.21` risk=`HIGH`
- `tests/integration/travel_field_tests.py` disposition=`merge` rank=`31` total_score=`61.21` risk=`HIGH`
- `tests/invariant/srz_execution_mode_invariant.py` disposition=`merge` rank=`32` total_score=`61.21` risk=`HIGH`
- `tests/perf/standard_perf_tests.py` disposition=`merge` rank=`33` total_score=`61.21` risk=`HIGH`
- `tests/integration/interaction_scaling_tests.py` disposition=`merge` rank=`34` total_score=`60.25` risk=`HIGH`
- `tests/integration/signal_scaling_tests.py` disposition=`merge` rank=`35` total_score=`60.25` risk=`HIGH`
- `tests/perf/climate_perf_tests.py` disposition=`merge` rank=`36` total_score=`60.25` risk=`HIGH`
- `tests/perf/economy_perf_tests.py` disposition=`merge` rank=`37` total_score=`60.25` risk=`HIGH`
- `tests/perf/energy_perf_tests.py` disposition=`merge` rank=`38` total_score=`60.25` risk=`HIGH`
- `tests/perf/fluid_perf_tests.py` disposition=`merge` rank=`39` total_score=`60.25` risk=`HIGH`
- `tests/perf/hazard_perf_tests.py` disposition=`merge` rank=`40` total_score=`60.25` risk=`HIGH`
- `tests/perf/heat_perf_tests.py` disposition=`merge` rank=`41` total_score=`60.25` risk=`HIGH`
- `tests/perf/history_perf_tests.py` disposition=`merge` rank=`42` total_score=`60.25` risk=`HIGH`
- `tests/perf/knowledge_perf_tests.py` disposition=`merge` rank=`43` total_score=`60.25` risk=`HIGH`
- `tests/perf/risk_perf_tests.py` disposition=`merge` rank=`44` total_score=`60.25` risk=`HIGH`
- `tests/perf/srz_perf_tests.py` disposition=`merge` rank=`45` total_score=`60.25` risk=`HIGH`
- `tests/perf/travel_perf_tests.py` disposition=`merge` rank=`46` total_score=`60.25` risk=`HIGH`
- `tests/perf/trust_perf_tests.py` disposition=`merge` rank=`47` total_score=`60.25` risk=`HIGH`
- `tests/integration/srz_field_tests.py` disposition=`merge` rank=`48` total_score=`60.02` risk=`HIGH`
- `tests/integration/mining_field_tests.py` disposition=`merge` rank=`49` total_score=`59.29` risk=`HIGH`
- `tests/integration/server_discovery_tests.py` disposition=`drop` rank=`50` total_score=`59.06` risk=`HIGH`
- `tests/perf/institution_perf_tests.py` disposition=`merge` rank=`51` total_score=`59.06` risk=`HIGH`
- `tests/perf/weather_perf_tests.py` disposition=`merge` rank=`52` total_score=`59.06` risk=`HIGH`
- `tests/integration/autonomy_field_tests.py` disposition=`merge` rank=`53` total_score=`58.09` risk=`HIGH`
- `tests/integration/economy_field_tests.py` disposition=`merge` rank=`54` total_score=`58.09` risk=`HIGH`
- `tests/integration/exploration_scaling_tests.py` disposition=`merge` rank=`55` total_score=`58.09` risk=`HIGH`
- `tests/integration/geology_field_tests.py` disposition=`merge` rank=`56` total_score=`58.09` risk=`HIGH`
- `tests/integration/world_manager_tests.py` disposition=`drop` rank=`57` total_score=`58.09` risk=`HIGH`
- `tests/perf/autonomy_perf_tests.py` disposition=`merge` rank=`58` total_score=`58.09` risk=`HIGH`
- `tests/perf/geology_perf_tests.py` disposition=`merge` rank=`59` total_score=`58.09` risk=`HIGH`
- `tests/perf/mining_perf_tests.py` disposition=`merge` rank=`60` total_score=`58.09` risk=`HIGH`
- `tests/integration/animal_agent_tests.py` disposition=`merge` rank=`61` total_score=`56.9` risk=`HIGH`
- `tests/integration/crafting_field_tests.py` disposition=`merge` rank=`62` total_score=`56.9` risk=`HIGH`
- `tests/integration/freecam_epistemics_tests.py` disposition=`merge` rank=`63` total_score=`56.9` risk=`HIGH`
- `tests/integration/vegetation_field_tests.py` disposition=`merge` rank=`64` total_score=`56.9` risk=`HIGH`
- `tests/perf/animal_perf_tests.py` disposition=`merge` rank=`65` total_score=`56.9` risk=`HIGH`
- `tests/perf/exploration_fixture_contracts.py` disposition=`merge` rank=`66` total_score=`56.9` risk=`HIGH`
- `tests/perf/vegetation_perf_tests.py` disposition=`merge` rank=`67` total_score=`56.9` risk=`HIGH`
- `tests/perf/crafting_perf_tests.py` disposition=`merge` rank=`68` total_score=`55.12` risk=`HIGH`
- `tests/integration/server_tools_operational_tests.py` disposition=`merge` rank=`69` total_score=`54.3` risk=`HIGH`
- `tests/integration/exploration_scale_guard_tests.py` disposition=`merge` rank=`70` total_score=`53.93` risk=`HIGH`

## Usage Sites

- Build Targets: `none`
- Docs: `docs/audit/MODULE_DUPLICATION_REPORT.md, docs/audit/REPO_TREE_INDEX.md, docs/ci/CI_ENFORCEMENT_MATRIX.md, docs/governance/REPOX_RULESETS.md, docs/mobility/MOBILITY_EXTENSION_CONTRACT.md, docs/release/PROVISIONAL_FEATURE_LIST.md`

## Tests Involved

- `python tools/compat/tool_run_interop_stress.py --repo-root .`
- `python tools/convergence/tool_run_convergence_gate.py --repo-root .`
- `python tools/mvp/tool_run_disaster_suite.py --repo-root .`
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
