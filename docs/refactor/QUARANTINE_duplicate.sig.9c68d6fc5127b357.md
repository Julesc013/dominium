Status: Quarantine
Last Reviewed: 2026-03-26
Stability: provisional
Replacement Target: XI-4b manual review resolution

# Quarantine Packet `duplicate.sig.9c68d6fc5127b357`

- Symbol: `geometry_length_mm`
- Cluster Kind: `exact`
- Cluster Resolution: `quarantine`
- Risk Level: `HIGH`
- Canonical Candidate: `src/mobility/micro/__init__.py`
- Quarantine Reasons: `phase_boundary_deferred, planned_quarantine, requires_single_action_full_gate`
- Planned Action Kinds: `merge, rewire, deprecate, quarantine`

## Competing Files

- `src/mobility/__init__.py`
- `src/mobility/micro/__init__.py`
- `src/mobility/micro/constrained_motion_solver.py`

## Scorecard

- `src/mobility/micro/__init__.py` disposition=`canonical` rank=`1` total_score=`66.27` risk=`HIGH`
- `src/mobility/__init__.py` disposition=`quarantine` rank=`2` total_score=`63.3` risk=`HIGH`
- `src/mobility/micro/constrained_motion_solver.py` disposition=`merge` rank=`3` total_score=`45.21` risk=`HIGH`

## Usage Sites

- Build Targets: `none`
- Docs: `docs/audit/GEO3_RETRO_AUDIT.md, docs/audit/GEO6_RETRO_AUDIT.md, docs/audit/GEO_METRIC_BASELINE.md, docs/audit/MACRO_TRAVEL_BASELINE.md, docs/geo/GEO_CONSTITUTION.md, docs/geo/METRIC_QUERY_ENGINE.md, docs/mobility/GUIDE_GEOMETRY.md, docs/release/PROVISIONAL_FEATURE_LIST.md`

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
