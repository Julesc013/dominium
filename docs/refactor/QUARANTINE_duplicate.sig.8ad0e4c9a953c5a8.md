Status: Quarantine
Last Reviewed: 2026-03-26
Stability: provisional
Replacement Target: XI-4b manual review resolution

# Quarantine Packet `duplicate.sig.8ad0e4c9a953c5a8`

- Symbol: `field_get_value`
- Cluster Kind: `exact`
- Cluster Resolution: `quarantine`
- Risk Level: `MED`
- Canonical Candidate: `src/fields/__init__.py`
- Quarantine Reasons: `planned_quarantine`
- Planned Action Kinds: `quarantine`

## Competing Files

- `src/field/__init__.py`
- `src/fields/__init__.py`

## Scorecard

- `src/fields/__init__.py` disposition=`canonical` rank=`1` total_score=`77.62` risk=`MED`
- `src/field/__init__.py` disposition=`quarantine` rank=`2` total_score=`73.27` risk=`HIGH`

## Usage Sites

- Build Targets: `none`
- Docs: `docs/audit/GEO4_RETRO_AUDIT.md, docs/audit/GEO_FIELD_BINDING_BASELINE.md, docs/audit/POLL1_RETRO_AUDIT.md, docs/audit/VEHICLE_MODEL_BASELINE.md, docs/governance/REPOX_RULESETS.md, docs/specs/SPEC_CLIMATE_WEATHER.md, docs/specs/SPEC_FIELDS.md, docs/specs/SPEC_ORBITS.md`

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
