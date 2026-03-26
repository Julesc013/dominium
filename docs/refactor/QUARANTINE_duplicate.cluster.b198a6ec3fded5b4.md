Status: Quarantine
Last Reviewed: 2026-03-26
Stability: provisional
Replacement Target: XI-4b manual review resolution

# Quarantine Packet `duplicate.cluster.b198a6ec3fded5b4`

- Symbol: `_violation`
- Cluster Kind: `near`
- Cluster Resolution: `quarantine`
- Risk Level: `HIGH`
- Canonical Candidate: `tools/security/trust_model_common.py`
- Quarantine Reasons: `phase_boundary_deferred, planned_quarantine, requires_single_action_full_gate`
- Planned Action Kinds: `merge, rewire, deprecate, quarantine`

## Competing Files

- `tools/governance/governance_model_common.py`
- `tools/release/archive_policy_common.py`
- `tools/security/trust_model_common.py`

## Scorecard

- `tools/security/trust_model_common.py` disposition=`canonical` rank=`1` total_score=`73.63` risk=`HIGH`
- `tools/release/archive_policy_common.py` disposition=`quarantine` rank=`2` total_score=`70.36` risk=`HIGH`
- `tools/governance/governance_model_common.py` disposition=`merge` rank=`3` total_score=`68.21` risk=`HIGH`

## Usage Sites

- Build Targets: `none`
- Docs: `docs/audit/MODULE_DUPLICATION_REPORT.md, docs/audit/REPO_TREE_INDEX.md, docs/audit/VALIDATION_STACK_MAP.md, docs/audit/auditx/FINDINGS.md, docs/audit/auditx/SUMMARY.md, docs/governance/REPOX_RULESETS.md, docs/logic/LOGIC_CONSTITUTION.md, docs/release/PROVISIONAL_FEATURE_LIST.md`

## Tests Involved

- `python tools/compat/tool_run_interop_stress.py --repo-root .`
- `python tools/convergence/tool_run_convergence_gate.py --repo-root .`
- `python tools/mvp/tool_run_disaster_suite.py --repo-root .`
- `python tools/mvp/tool_verify_baseline_universe.py --repo-root .`
- `python tools/mvp/tool_verify_gameplay_loop.py --repo-root .`
- `python tools/security/tool_run_trust_strict_suite.py --repo-root .`
- `python tools/validation/tool_run_validation.py --repo-root . --profile STRICT`
- `python tools/worldgen/tool_verify_worldgen_lock.py --repo-root .`
- `python tools/xstack/testx/runner.py --repo-root . --profile FAST --cache off --subset test_convergence_plan_deterministic,test_decision_rules_stable`

## Recommended Decision Options

- Review file-local deltas and port only unique behavior into the canonical file.
- Rewire call sites only after confirming the secondary file is not an active product entrypoint.
- Deprecate the secondary file only after it is removed from default build targets and no longer carries unrelated active symbols.
- If ambiguity remains after review, keep the cluster quarantined for XI-4b instead of forcing convergence.
