Status: Quarantine
Last Reviewed: 2026-03-26
Stability: provisional
Replacement Target: XI-4b manual review resolution

# Quarantine Packet `duplicate.cluster.aab72a95c9d4499a`

- Symbol: `_sorted_unique_strings`
- Cluster Kind: `near`
- Cluster Resolution: `merge`
- Risk Level: `LOW`
- Canonical Candidate: `tools/release/arch_matrix_common.py`
- Quarantine Reasons: `file_scope_ambiguity, near_duplicate_requires_review, phase_boundary_deferred, requires_single_action_full_gate`
- Planned Action Kinds: `merge, rewire, deprecate`

## Competing Files

- `src/release/archive_policy.py`
- `tools/meta/observability_common.py`
- `tools/release/arch_matrix_common.py`

## Scorecard

- `tools/release/arch_matrix_common.py` disposition=`canonical` rank=`1` total_score=`67.13` risk=`LOW`
- `tools/meta/observability_common.py` disposition=`merge` rank=`2` total_score=`61.83` risk=`LOW`
- `src/release/archive_policy.py` disposition=`merge` rank=`3` total_score=`53.27` risk=`HIGH`

## Usage Sites

- Build Targets: `none`
- Docs: `docs/audit/REPO_TREE_INDEX.md`

## Tests Involved

- `python tools/convergence/tool_run_convergence_gate.py --repo-root .`
- `python tools/mvp/tool_run_all_stress.py --repo-root .`
- `python tools/mvp/tool_run_disaster_suite.py --repo-root .`
- `python tools/mvp/tool_run_product_boot_matrix.py --repo-root .`
- `python tools/mvp/tool_verify_baseline_universe.py --repo-root .`
- `python tools/mvp/tool_verify_gameplay_loop.py --repo-root .`
- `python tools/validation/tool_run_validation.py --repo-root . --profile FAST`
- `python tools/validation/tool_run_validation.py --repo-root . --profile STRICT`
- `python tools/worldgen/tool_verify_worldgen_lock.py --repo-root .`
- `python tools/xstack/testx/runner.py --repo-root . --profile FAST --cache off --subset test_convergence_plan_deterministic,test_decision_rules_stable`

## Recommended Decision Options

- Review file-local deltas and port only unique behavior into the canonical file.
- Rewire call sites only after confirming the secondary file is not an active product entrypoint.
- Deprecate the secondary file only after it is removed from default build targets and no longer carries unrelated active symbols.
- If ambiguity remains after review, keep the cluster quarantined for XI-4b instead of forcing convergence.
