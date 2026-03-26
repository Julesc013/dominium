Status: Quarantine
Last Reviewed: 2026-03-26
Stability: provisional
Replacement Target: XI-4b manual review resolution

# Quarantine Packet `duplicate.sig.8734f085d16e0e8c`

- Symbol: `_pick`
- Cluster Kind: `exact`
- Cluster Resolution: `quarantine`
- Risk Level: `HIGH`
- Canonical Candidate: `tools/fluid/tool_generate_fluid_stress.py`
- Quarantine Reasons: `phase_boundary_deferred, planned_quarantine, requires_single_action_full_gate`
- Planned Action Kinds: `merge, rewire, deprecate, quarantine`

## Competing Files

- `tools/chem/tool_generate_chem_stress.py`
- `tools/electric/tool_generate_elec_stress_scenario.py`
- `tools/fluid/tool_generate_fluid_stress.py`
- `tools/geo/geo10_stress_common.py`
- `tools/logic/logic10_stress_common.py`
- `tools/pollution/tool_generate_poll_stress.py`
- `tools/process/tool_generate_proc_stress.py`
- `tools/system/tool_generate_sys_stress.py`
- `tools/thermal/tool_generate_therm_stress_scenario.py`

## Scorecard

- `tools/fluid/tool_generate_fluid_stress.py` disposition=`canonical` rank=`1` total_score=`67.55` risk=`HIGH`
- `tools/thermal/tool_generate_therm_stress_scenario.py` disposition=`quarantine` rank=`2` total_score=`66.05` risk=`HIGH`
- `tools/electric/tool_generate_elec_stress_scenario.py` disposition=`quarantine` rank=`3` total_score=`61.99` risk=`HIGH`
- `tools/chem/tool_generate_chem_stress.py` disposition=`quarantine` rank=`4` total_score=`61.55` risk=`HIGH`
- `tools/geo/geo10_stress_common.py` disposition=`quarantine` rank=`5` total_score=`61.12` risk=`HIGH`
- `tools/system/tool_generate_sys_stress.py` disposition=`quarantine` rank=`6` total_score=`60.52` risk=`HIGH`
- `tools/process/tool_generate_proc_stress.py` disposition=`quarantine` rank=`7` total_score=`59.62` risk=`HIGH`
- `tools/pollution/tool_generate_poll_stress.py` disposition=`merge` rank=`8` total_score=`56.54` risk=`HIGH`
- `tools/logic/logic10_stress_common.py` disposition=`merge` rank=`9` total_score=`54.45` risk=`HIGH`

## Usage Sites

- Build Targets: `none`
- Docs: `none`

## Tests Involved

- `python tools/convergence/tool_run_convergence_gate.py --repo-root .`
- `python tools/mvp/tool_run_disaster_suite.py --repo-root .`
- `python tools/mvp/tool_verify_baseline_universe.py --repo-root .`
- `python tools/mvp/tool_verify_gameplay_loop.py --repo-root .`
- `python tools/validation/tool_run_validation.py --repo-root . --profile STRICT`
- `python tools/worldgen/tool_verify_worldgen_lock.py --repo-root .`
- `python tools/xstack/testx/runner.py --repo-root . --profile FAST --cache off --subset test_convergence_plan_deterministic,test_decision_rules_stable`

## Recommended Decision Options

- Review file-local deltas and port only unique behavior into the canonical file.
- Rewire call sites only after confirming the secondary file is not an active product entrypoint.
- Deprecate the secondary file only after it is removed from default build targets and no longer carries unrelated active symbols.
- If ambiguity remains after review, keep the cluster quarantined for XI-4b instead of forcing convergence.
