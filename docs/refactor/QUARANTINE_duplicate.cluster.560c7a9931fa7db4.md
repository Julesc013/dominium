Status: Quarantine
Last Reviewed: 2026-03-26
Stability: provisional
Replacement Target: XI-4b manual review resolution

# Quarantine Packet `duplicate.cluster.560c7a9931fa7db4`

- Symbol: `_read_json_object`
- Cluster Kind: `near`
- Cluster Resolution: `quarantine`
- Risk Level: `HIGH`
- Canonical Candidate: `tools/data/tool_spice_import.py`
- Quarantine Reasons: `planned_quarantine`
- Planned Action Kinds: `quarantine`

## Competing Files

- `tools/data/tool_spice_import.py`
- `tools/data/tool_srtm_import.py`
- `tools/xstack/packagingx/dist_build.py`
- `worldgen/core/constraint_commands.py`

## Scorecard

- `tools/data/tool_spice_import.py` disposition=`canonical` rank=`1` total_score=`67.12` risk=`HIGH`
- `tools/data/tool_srtm_import.py` disposition=`quarantine` rank=`2` total_score=`67.12` risk=`HIGH`
- `worldgen/core/constraint_commands.py` disposition=`quarantine` rank=`3` total_score=`63.71` risk=`HIGH`
- `tools/xstack/packagingx/dist_build.py` disposition=`quarantine` rank=`4` total_score=`60.82` risk=`HIGH`

## Usage Sites

- Build Targets: `none`
- Docs: `docs/audit/MODULE_DUPLICATION_REPORT.md, docs/audit/REPO_TREE_INDEX.md, docs/audit/UNIVERSE_PHYSICS_PROFILE_BASELINE.md`

## Tests Involved

- `python tools/convergence/tool_run_convergence_gate.py --repo-root .`
- `python tools/mvp/tool_run_all_stress.py --repo-root .`
- `python tools/mvp/tool_run_disaster_suite.py --repo-root .`
- `python tools/mvp/tool_run_product_boot_matrix.py --repo-root .`
- `python tools/mvp/tool_verify_baseline_universe.py --repo-root .`
- `python tools/mvp/tool_verify_gameplay_loop.py --repo-root .`
- `python tools/validation/tool_run_validation.py --repo-root . --profile STRICT`
- `python tools/worldgen/tool_verify_worldgen_lock.py --repo-root .`
- `python tools/xstack/testx/runner.py --repo-root . --profile FAST --cache off --subset test_convergence_plan_deterministic,test_decision_rules_stable`

## Recommended Decision Options

- If ambiguity remains after review, keep the cluster quarantined for XI-4b instead of forcing convergence.
