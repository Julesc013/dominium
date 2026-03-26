Status: Quarantine
Last Reviewed: 2026-03-26
Stability: provisional
Replacement Target: XI-4b manual review resolution

# Quarantine Packet `duplicate.cluster.4d2bc81e05be315a`

- Symbol: `_queue_sort_key`
- Cluster Kind: `near`
- Cluster Resolution: `merge`
- Risk Level: `MED`
- Canonical Candidate: `src/net/policies/policy_server_authoritative.py`
- Quarantine Reasons: `cross_domain_helper_collision, file_scope_ambiguity, near_duplicate_requires_review, phase_boundary_deferred, requires_medium_risk_batch_gate, source_like_surface, test_runtime_split`
- Planned Action Kinds: `merge, rewire, deprecate`

## Competing Files

- `src/net/policies/policy_server_authoritative.py`
- `src/net/srz/shard_coordinator.py`
- `tools/xstack/testx/tests/net_mp9_testlib.py`

## Scorecard

- `src/net/policies/policy_server_authoritative.py` disposition=`canonical` rank=`1` total_score=`58.93` risk=`MED`
- `tools/xstack/testx/tests/net_mp9_testlib.py` disposition=`merge` rank=`2` total_score=`54.33` risk=`LOW`
- `src/net/srz/shard_coordinator.py` disposition=`merge` rank=`3` total_score=`40.32` risk=`MED`

## Usage Sites

- Build Targets: `none`
- Docs: `docs/audit/MODULE_DUPLICATION_REPORT.md, docs/audit/REPO_TREE_INDEX.md, docs/ci/CI_ENFORCEMENT_MATRIX.md, docs/release/PROVISIONAL_FEATURE_LIST.md`

## Tests Involved

- `python tools/mvp/tool_run_disaster_suite.py --repo-root .`
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
