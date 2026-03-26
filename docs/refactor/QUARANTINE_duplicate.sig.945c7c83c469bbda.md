Status: Quarantine
Last Reviewed: 2026-03-26
Stability: provisional
Replacement Target: XI-4b manual review resolution

# Quarantine Packet `duplicate.sig.945c7c83c469bbda`

- Symbol: `_policy_registry`
- Cluster Kind: `exact`
- Cluster Resolution: `quarantine`
- Risk Level: `HIGH`
- Canonical Candidate: `tools/xstack/testx/tests/test_control_save_compat_replay.py`
- Quarantine Reasons: `planned_quarantine`
- Planned Action Kinds: `quarantine`

## Competing Files

- `tools/xstack/testx/tests/test_control_save_compat_replay.py`
- `tools/xstack/testx/tests/test_decision_log_hash_stable_across_peers.py`
- `tools/xstack/testx/tests/test_replay_mode_readonly.py`

## Scorecard

- `tools/xstack/testx/tests/test_control_save_compat_replay.py` disposition=`canonical` rank=`1` total_score=`63.86` risk=`HIGH`
- `tools/xstack/testx/tests/test_replay_mode_readonly.py` disposition=`quarantine` rank=`2` total_score=`63.23` risk=`HIGH`
- `tools/xstack/testx/tests/test_decision_log_hash_stable_across_peers.py` disposition=`quarantine` rank=`3` total_score=`62.03` risk=`HIGH`

## Usage Sites

- Build Targets: `none`
- Docs: `docs/architecture/CANON_INDEX.md, docs/audit/CANON_MAP.md, docs/audit/CONTROL_PLANE_ENGINE_BASELINE.md, docs/audit/DOCS_AUDIT_PROMPT0.md, docs/audit/DOC_INDEX.md, docs/audit/ELECTRICAL_PROTECTION_BASELINE.md, docs/audit/ENTROPY_POLICY_BASELINE.md, docs/audit/GEO_CONSTITUTION_BASELINE.md`

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
