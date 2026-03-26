Status: Quarantine
Last Reviewed: 2026-03-26
Stability: provisional
Replacement Target: XI-4b manual review resolution

# Quarantine Packet `duplicate.cluster.782634fd63c50965`

- Symbol: `_geo_cell_key_sort_tuple`
- Cluster Kind: `near`
- Cluster Resolution: `quarantine`
- Risk Level: `HIGH`
- Canonical Candidate: `src/fields/field_engine.py`
- Quarantine Reasons: `planned_quarantine`
- Planned Action Kinds: `quarantine`

## Competing Files

- `src/fields/field_engine.py`
- `src/geo/projection/projection_engine.py`

## Scorecard

- `src/fields/field_engine.py` disposition=`canonical` rank=`1` total_score=`56.61` risk=`HIGH`
- `src/geo/projection/projection_engine.py` disposition=`quarantine` rank=`2` total_score=`54.29` risk=`HIGH`

## Usage Sites

- Build Targets: `none`
- Docs: `docs/appshell/CLI_REFERENCE.md, docs/audit/ARCH_AUDIT_FIX_PLAN.md, docs/audit/EARTH0_RETRO_AUDIT.md, docs/audit/EARTH10_RETRO_AUDIT.md, docs/audit/EARTH2_RETRO_AUDIT.md, docs/audit/EARTH7_RETRO_AUDIT.md, docs/audit/GEO0_RETRO_AUDIT.md, docs/audit/GEO1_RETRO_AUDIT.md`

## Tests Involved

- `python tools/convergence/tool_run_convergence_gate.py --repo-root .`
- `python tools/mvp/tool_run_disaster_suite.py --repo-root .`
- `python tools/mvp/tool_verify_baseline_universe.py --repo-root .`
- `python tools/mvp/tool_verify_gameplay_loop.py --repo-root .`
- `python tools/validation/tool_run_validation.py --repo-root . --profile STRICT`
- `python tools/worldgen/tool_verify_worldgen_lock.py --repo-root .`
- `python tools/xstack/testx/runner.py --repo-root . --profile FAST --cache off --subset test_convergence_plan_deterministic,test_decision_rules_stable`

## Recommended Decision Options

- If ambiguity remains after review, keep the cluster quarantined for XI-4b instead of forcing convergence.
