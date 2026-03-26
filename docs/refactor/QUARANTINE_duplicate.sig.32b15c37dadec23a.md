Status: Quarantine
Last Reviewed: 2026-03-26
Stability: provisional
Replacement Target: XI-4b manual review resolution

# Quarantine Packet `duplicate.sig.32b15c37dadec23a`

- Symbol: `geo_geodesic`
- Cluster Kind: `exact`
- Cluster Resolution: `quarantine`
- Risk Level: `HIGH`
- Canonical Candidate: `src/geo/metric/__init__.py`
- Quarantine Reasons: `phase_boundary_deferred, planned_quarantine, requires_single_action_full_gate`
- Planned Action Kinds: `merge, rewire, deprecate, quarantine`

## Competing Files

- `src/geo/__init__.py`
- `src/geo/metric/__init__.py`
- `src/geo/metric/metric_engine.py`

## Scorecard

- `src/geo/metric/__init__.py` disposition=`canonical` rank=`1` total_score=`69.35` risk=`HIGH`
- `src/geo/__init__.py` disposition=`quarantine` rank=`2` total_score=`67.02` risk=`HIGH`
- `src/geo/metric/metric_engine.py` disposition=`merge` rank=`3` total_score=`49.7` risk=`HIGH`

## Usage Sites

- Build Targets: `none`
- Docs: `docs/audit/GEO3_RETRO_AUDIT.md, docs/audit/GEO_CONSTITUTION_BASELINE.md, docs/audit/GEO_FINAL_BASELINE.md, docs/audit/GEO_FRAMES_BASELINE.md, docs/audit/GEO_METRIC_BASELINE.md, docs/audit/NUMERIC_DISCIPLINE0_RETRO_AUDIT.md, docs/audit/NUMERIC_DISCIPLINE_BASELINE.md, docs/audit/REPO_TREE_INDEX.md`

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
