Status: Quarantine
Last Reviewed: 2026-03-26
Stability: provisional
Replacement Target: XI-4b manual review resolution

# Quarantine Packet `duplicate.sig.7600d3670c0f207e`

- Symbol: `geo_cell_key_neighbors`
- Cluster Kind: `exact`
- Cluster Resolution: `quarantine`
- Risk Level: `HIGH`
- Canonical Candidate: `src/geo/index/__init__.py`
- Quarantine Reasons: `planned_quarantine`
- Planned Action Kinds: `quarantine`

## Competing Files

- `src/geo/__init__.py`
- `src/geo/index/__init__.py`

## Scorecard

- `src/geo/index/__init__.py` disposition=`canonical` rank=`1` total_score=`62.8` risk=`HIGH`
- `src/geo/__init__.py` disposition=`quarantine` rank=`2` total_score=`59.88` risk=`HIGH`

## Usage Sites

- Build Targets: `none`
- Docs: `docs/audit/EARTH1_RETRO_AUDIT.md, docs/audit/EARTH6_RETRO_AUDIT.md, docs/audit/GEO4_RETRO_AUDIT.md, docs/audit/GEO6_RETRO_AUDIT.md, docs/audit/GEO_IDENTITY_BASELINE.md, docs/audit/GEO_METRIC_BASELINE.md, docs/audit/MODULE_DUPLICATION_REPORT.md, docs/audit/REPO_TREE_INDEX.md`

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
