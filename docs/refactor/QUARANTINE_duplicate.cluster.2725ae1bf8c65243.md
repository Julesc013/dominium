Status: Quarantine
Last Reviewed: 2026-03-26
Stability: provisional
Replacement Target: XI-4b manual review resolution

# Quarantine Packet `duplicate.cluster.2725ae1bf8c65243`

- Symbol: `_write_canonical_json`
- Cluster Kind: `near`
- Cluster Resolution: `quarantine`
- Risk Level: `HIGH`
- Canonical Candidate: `tools/xstack/packagingx/dist_build.py`
- Quarantine Reasons: `planned_quarantine`
- Planned Action Kinds: `quarantine`

## Competing Files

- `tools/xstack/packagingx/dist_build.py`
- `worldgen/core/constraint_commands.py`

## Scorecard

- `tools/xstack/packagingx/dist_build.py` disposition=`canonical` rank=`1` total_score=`76.07` risk=`HIGH`
- `worldgen/core/constraint_commands.py` disposition=`quarantine` rank=`2` total_score=`68.99` risk=`HIGH`

## Usage Sites

- Build Targets: `none`
- Docs: `docs/architecture/deterministic_packaging.md, docs/audit/DIST2_RETRO_AUDIT.md, docs/audit/MODULE_DUPLICATION_REPORT.md, docs/audit/MVP1_RETRO_AUDIT.md, docs/audit/PACK_COMPAT1_RETRO_AUDIT.md, docs/audit/REPO_TREE_INDEX.md, docs/audit/TIER_TRANSITION_CONSTITUTION_BASELINE.md, docs/release/DIST_VERIFICATION_RULES.md`

## Tests Involved

- `python tools/compat/tool_run_interop_stress.py --repo-root .`
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
