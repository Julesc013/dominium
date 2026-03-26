Status: Quarantine
Last Reviewed: 2026-03-26
Stability: provisional
Replacement Target: XI-4b manual review resolution

# Quarantine Packet `duplicate.cluster.e4fbc0e7ca0b3fd1`

- Symbol: `REFUSAL_MOBILITY_SPEC_NONCOMPLIANT`
- Cluster Kind: `near`
- Cluster Resolution: `quarantine`
- Risk Level: `HIGH`
- Canonical Candidate: `src/mobility/vehicle/vehicle_engine.py`
- Quarantine Reasons: `planned_quarantine`
- Planned Action Kinds: `quarantine`

## Competing Files

- `src/mobility/vehicle/__init__.py`
- `src/mobility/vehicle/vehicle_engine.py`

## Scorecard

- `src/mobility/vehicle/vehicle_engine.py` disposition=`canonical` rank=`1` total_score=`68.09` risk=`HIGH`
- `src/mobility/vehicle/__init__.py` disposition=`quarantine` rank=`2` total_score=`61.49` risk=`HIGH`

## Usage Sites

- Build Targets: `none`
- Docs: `docs/audit/MACRO_TRAVEL_BASELINE.md, docs/audit/MOBILITY_CONSTITUTION_BASELINE.md, docs/audit/SPECSHEET_BASELINE.md, docs/audit/VEHICLE_MODEL_BASELINE.md, docs/mobility/MACRO_TRAVEL_MODEL.md, docs/mobility/VEHICLE_MODEL.md, docs/release/PROVISIONAL_FEATURE_LIST.md, docs/specs/SPECSHEET_CONSTITUTION.md`

## Tests Involved

- `python tools/compat/tool_run_interop_stress.py --repo-root .`
- `python tools/convergence/tool_run_convergence_gate.py --repo-root .`
- `python tools/mvp/tool_run_disaster_suite.py --repo-root .`
- `python tools/mvp/tool_verify_baseline_universe.py --repo-root .`
- `python tools/mvp/tool_verify_gameplay_loop.py --repo-root .`
- `python tools/validation/tool_run_validation.py --repo-root . --profile STRICT`
- `python tools/worldgen/tool_verify_worldgen_lock.py --repo-root .`
- `python tools/xstack/testx/runner.py --repo-root . --profile FAST --cache off --subset test_convergence_plan_deterministic,test_decision_rules_stable`

## Recommended Decision Options

- If ambiguity remains after review, keep the cluster quarantined for XI-4b instead of forcing convergence.
