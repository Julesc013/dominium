Status: Quarantine
Last Reviewed: 2026-03-26
Stability: provisional
Replacement Target: XI-4b manual review resolution

# Quarantine Packet `duplicate.sig.4cd426b695740cc9`

- Symbol: `REFUSAL_MOBILITY_RESERVATION_CONFLICT`
- Cluster Kind: `exact`
- Cluster Resolution: `quarantine`
- Risk Level: `HIGH`
- Canonical Candidate: `src/mobility/traffic/__init__.py`
- Quarantine Reasons: `planned_quarantine`
- Planned Action Kinds: `quarantine`

## Competing Files

- `src/mobility/__init__.py`
- `src/mobility/traffic/__init__.py`
- `src/mobility/traffic/traffic_engine.py`

## Scorecard

- `src/mobility/traffic/__init__.py` disposition=`canonical` rank=`1` total_score=`61.68` risk=`HIGH`
- `src/mobility/__init__.py` disposition=`quarantine` rank=`2` total_score=`55.19` risk=`HIGH`
- `src/mobility/traffic/traffic_engine.py` disposition=`quarantine` rank=`3` total_score=`52.67` risk=`HIGH`

## Usage Sites

- Build Targets: `none`
- Docs: `docs/audit/MESO_TRAFFIC_BASELINE.md, docs/audit/MOB5_RETRO_AUDIT.md, docs/audit/MOB8_RETRO_AUDIT.md, docs/audit/REPO_TREE_INDEX.md, docs/mobility/MESO_TRAFFIC_MODEL.md`

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
