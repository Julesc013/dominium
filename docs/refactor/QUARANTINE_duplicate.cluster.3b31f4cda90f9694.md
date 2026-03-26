Status: Quarantine
Last Reviewed: 2026-03-26
Stability: provisional
Replacement Target: XI-4b manual review resolution

# Quarantine Packet `duplicate.cluster.3b31f4cda90f9694`

- Symbol: `_canon`
- Cluster Kind: `near`
- Cluster Resolution: `quarantine`
- Risk Level: `HIGH`
- Canonical Candidate: `src/mobility/vehicle/vehicle_engine.py`
- Quarantine Reasons: `phase_boundary_deferred, planned_quarantine, requires_single_action_full_gate`
- Planned Action Kinds: `merge, rewire, deprecate, quarantine`

## Competing Files

- `src/chem/degradation/degradation_engine.py`
- `src/control/effects/effect_engine.py`
- `src/control/planning/plan_engine.py`
- `src/control/view/view_engine.py`
- `src/electric/fault/fault_engine.py`
- `src/electric/power_network_engine.py`
- `src/electric/protection/protection_engine.py`
- `src/electric/storage/storage_engine.py`
- `src/fields/field_engine.py`
- `src/fluid/network/fluid_network_engine.py`
- `src/infrastructure/formalization/inference_engine.py`
- `src/logic/debug/debug_engine.py`
- `src/logic/debug/runtime_state.py`
- `src/logic/signal/carrier_adapters.py`
- `src/logic/signal/signal_store.py`
- `src/mechanics/structural_graph_engine.py`
- `src/meta/explain/explain_engine.py`
- `src/mobility/geometry/geometry_engine.py`
- `src/mobility/maintenance/wear_engine.py`
- `src/mobility/micro/constrained_motion_solver.py`
- `src/mobility/micro/free_motion_solver.py`
- `src/mobility/network/mobility_network_engine.py`
- `src/mobility/signals/signal_engine.py`
- `src/mobility/traffic/traffic_engine.py`
- `src/mobility/travel/itinerary_engine.py`
- `src/mobility/travel/reenactment.py`
- `src/mobility/travel/travel_engine.py`
- `src/mobility/vehicle/vehicle_engine.py`
- `src/models/model_engine.py`
- `src/physics/energy/energy_ledger_engine.py`
- `src/physics/entropy/entropy_engine.py`
- `src/physics/momentum_engine.py`
- `src/safety/safety_engine.py`
- `src/specs/spec_engine.py`
- `src/thermal/network/thermal_network_engine.py`
- `src/time/time_mapping_engine.py`

## Scorecard

- `src/mobility/vehicle/vehicle_engine.py` disposition=`canonical` rank=`1` total_score=`63.33` risk=`HIGH`
- `src/models/model_engine.py` disposition=`quarantine` rank=`2` total_score=`63.33` risk=`HIGH`
- `src/specs/spec_engine.py` disposition=`quarantine` rank=`3` total_score=`59.58` risk=`HIGH`
- `src/meta/explain/explain_engine.py` disposition=`quarantine` rank=`4` total_score=`58.62` risk=`HIGH`
- `src/thermal/network/thermal_network_engine.py` disposition=`quarantine` rank=`5` total_score=`57.5` risk=`HIGH`
- `src/electric/fault/fault_engine.py` disposition=`quarantine` rank=`6` total_score=`56.17` risk=`HIGH`
- `src/physics/energy/energy_ledger_engine.py` disposition=`quarantine` rank=`7` total_score=`55.74` risk=`HIGH`
- `src/electric/storage/storage_engine.py` disposition=`quarantine` rank=`8` total_score=`55.73` risk=`HIGH`
- `src/physics/entropy/entropy_engine.py` disposition=`quarantine` rank=`9` total_score=`55.73` risk=`HIGH`
- `src/fields/field_engine.py` disposition=`quarantine` rank=`10` total_score=`55.64` risk=`HIGH`
- `src/logic/debug/runtime_state.py` disposition=`quarantine` rank=`11` total_score=`55.58` risk=`HIGH`
- `src/control/view/view_engine.py` disposition=`quarantine` rank=`12` total_score=`53.87` risk=`HIGH`
- `src/logic/signal/signal_store.py` disposition=`quarantine` rank=`13` total_score=`53.45` risk=`HIGH`
- `src/electric/protection/protection_engine.py` disposition=`drop` rank=`14` total_score=`53.27` risk=`HIGH`
- `src/mobility/network/mobility_network_engine.py` disposition=`merge` rank=`15` total_score=`53.18` risk=`HIGH`
- `src/mobility/maintenance/wear_engine.py` disposition=`merge` rank=`16` total_score=`52.74` risk=`HIGH`
- `src/safety/safety_engine.py` disposition=`drop` rank=`17` total_score=`52.73` risk=`HIGH`
- `src/electric/power_network_engine.py` disposition=`drop` rank=`18` total_score=`52.1` risk=`HIGH`
- `src/infrastructure/formalization/inference_engine.py` disposition=`drop` rank=`19` total_score=`51.87` risk=`HIGH`
- `src/mobility/geometry/geometry_engine.py` disposition=`merge` rank=`20` total_score=`51.85` risk=`HIGH`
- `src/physics/momentum_engine.py` disposition=`drop` rank=`21` total_score=`51.77` risk=`HIGH`
- `src/control/effects/effect_engine.py` disposition=`drop` rank=`22` total_score=`50.98` risk=`HIGH`
- `src/mobility/micro/free_motion_solver.py` disposition=`merge` rank=`23` total_score=`50.81` risk=`HIGH`
- `src/chem/degradation/degradation_engine.py` disposition=`drop` rank=`24` total_score=`50.71` risk=`HIGH`
- `src/mobility/traffic/traffic_engine.py` disposition=`merge` rank=`25` total_score=`50.29` risk=`HIGH`
- `src/mobility/travel/reenactment.py` disposition=`merge` rank=`26` total_score=`50.21` risk=`HIGH`
- `src/mobility/travel/travel_engine.py` disposition=`merge` rank=`27` total_score=`50.06` risk=`HIGH`
- `src/mobility/travel/itinerary_engine.py` disposition=`merge` rank=`28` total_score=`49.69` risk=`HIGH`
- `src/time/time_mapping_engine.py` disposition=`drop` rank=`29` total_score=`49.19` risk=`HIGH`
- `src/mobility/micro/constrained_motion_solver.py` disposition=`merge` rank=`30` total_score=`48.79` risk=`HIGH`
- `src/fluid/network/fluid_network_engine.py` disposition=`drop` rank=`31` total_score=`48.5` risk=`HIGH`
- `src/mechanics/structural_graph_engine.py` disposition=`drop` rank=`32` total_score=`47.82` risk=`HIGH`
- `src/control/planning/plan_engine.py` disposition=`drop` rank=`33` total_score=`46.81` risk=`HIGH`
- `src/mobility/signals/signal_engine.py` disposition=`merge` rank=`34` total_score=`46.6` risk=`HIGH`
- `src/logic/signal/carrier_adapters.py` disposition=`drop` rank=`35` total_score=`46.15` risk=`HIGH`
- `src/logic/debug/debug_engine.py` disposition=`drop` rank=`36` total_score=`43.21` risk=`HIGH`

## Usage Sites

- Build Targets: `none`
- Docs: `docs/architecture/CANON_INDEX.md, docs/archive/ci/DOCS_VALIDATION_REPORT.md, docs/audit/CANON_MAP.md, docs/audit/CTRL7_RETRO_AUDIT.md, docs/audit/DOCS_AUDIT_PROMPT0.md, docs/audit/DOC_INDEX.md, docs/audit/GEO4_RETRO_AUDIT.md, docs/audit/GEO6_RETRO_AUDIT.md`

## Tests Involved

- `python tools/compat/tool_run_interop_stress.py --repo-root .`
- `python tools/convergence/tool_run_convergence_gate.py --repo-root .`
- `python tools/mvp/tool_run_all_stress.py --repo-root .`
- `python tools/mvp/tool_run_disaster_suite.py --repo-root .`
- `python tools/mvp/tool_run_product_boot_matrix.py --repo-root .`
- `python tools/mvp/tool_verify_baseline_universe.py --repo-root .`
- `python tools/mvp/tool_verify_gameplay_loop.py --repo-root .`
- `python tools/time/tool_verify_longrun_ticks.py --repo-root .`
- `python tools/validation/tool_run_validation.py --repo-root . --profile STRICT`
- `python tools/worldgen/tool_verify_worldgen_lock.py --repo-root .`
- `python tools/xstack/testx/runner.py --repo-root . --profile FAST --cache off --subset test_convergence_plan_deterministic,test_decision_rules_stable`

## Recommended Decision Options

- Review file-local deltas and port only unique behavior into the canonical file.
- Rewire call sites only after confirming the secondary file is not an active product entrypoint.
- Deprecate the secondary file only after it is removed from default build targets and no longer carries unrelated active symbols.
- If ambiguity remains after review, keep the cluster quarantined for XI-4b instead of forcing convergence.
