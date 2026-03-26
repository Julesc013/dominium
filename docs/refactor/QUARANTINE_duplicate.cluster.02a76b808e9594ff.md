Status: Quarantine
Last Reviewed: 2026-03-26
Stability: provisional
Replacement Target: XI-4b manual review resolution

# Quarantine Packet `duplicate.cluster.02a76b808e9594ff`

- Symbol: `require_keys`
- Cluster Kind: `near`
- Cluster Resolution: `quarantine`
- Risk Level: `HIGH`
- Canonical Candidate: `tools/ci/validate_earth_data.py`
- Quarantine Reasons: `planned_quarantine`
- Planned Action Kinds: `quarantine`

## Competing Files

- `tools/ci/validate_earth_data.py`
- `tools/ci/validate_milky_way_data.py`
- `tools/ci/validate_sol_data.py`

## Scorecard

- `tools/ci/validate_earth_data.py` disposition=`canonical` rank=`1` total_score=`68.14` risk=`HIGH`
- `tools/ci/validate_milky_way_data.py` disposition=`quarantine` rank=`2` total_score=`65.25` risk=`HIGH`
- `tools/ci/validate_sol_data.py` disposition=`quarantine` rank=`3` total_score=`65.25` risk=`HIGH`

## Usage Sites

- Build Targets: `none`
- Docs: `docs/architecture/astronomy_catalogs.md, docs/audit/MODULE_DUPLICATION_REPORT.md, docs/audit/REPO_TREE_INDEX.md, docs/ci/CI_ENFORCEMENT_MATRIX.md`

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
