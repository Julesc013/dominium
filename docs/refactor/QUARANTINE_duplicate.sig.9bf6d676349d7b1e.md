Status: Quarantine
Last Reviewed: 2026-03-26
Stability: provisional
Replacement Target: XI-4b manual review resolution

# Quarantine Packet `duplicate.sig.9bf6d676349d7b1e`

- Symbol: `REFUSAL_CTRL_IR_COST_EXCEEDED`
- Cluster Kind: `exact`
- Cluster Resolution: `quarantine`
- Risk Level: `HIGH`
- Canonical Candidate: `src/control/ir/control_ir_verifier.py`
- Quarantine Reasons: `planned_quarantine`
- Planned Action Kinds: `quarantine`

## Competing Files

- `src/control/__init__.py`
- `src/control/ir/__init__.py`
- `src/control/ir/control_ir_verifier.py`
- `src/control/negotiation/__init__.py`
- `src/control/negotiation/negotiation_kernel.py`

## Scorecard

- `src/control/ir/control_ir_verifier.py` disposition=`canonical` rank=`1` total_score=`63.57` risk=`HIGH`
- `src/control/negotiation/__init__.py` disposition=`quarantine` rank=`2` total_score=`63.15` risk=`HIGH`
- `src/control/ir/__init__.py` disposition=`quarantine` rank=`3` total_score=`61.61` risk=`HIGH`
- `src/control/__init__.py` disposition=`quarantine` rank=`4` total_score=`59.88` risk=`HIGH`
- `src/control/negotiation/negotiation_kernel.py` disposition=`quarantine` rank=`5` total_score=`54.76` risk=`HIGH`

## Usage Sites

- Build Targets: `none`
- Docs: `docs/audit/CONTROL_IR_BASELINE.md, docs/audit/CTRL3_RETRO_AUDIT.md, docs/audit/FIDELITY_ARBITRATION_BASELINE.md, docs/audit/MODULE_DUPLICATION_REPORT.md, docs/audit/REPO_TREE_INDEX.md, docs/ci/CI_ENFORCEMENT_MATRIX.md, docs/contracts/refusal_contract.md, docs/release/PROVISIONAL_FEATURE_LIST.md`

## Tests Involved

- `python tools/compat/tool_run_interop_stress.py --repo-root .`
- `python tools/convergence/tool_run_convergence_gate.py --repo-root .`
- `python tools/mvp/tool_run_disaster_suite.py --repo-root .`
- `python tools/mvp/tool_verify_baseline_universe.py --repo-root .`
- `python tools/mvp/tool_verify_gameplay_loop.py --repo-root .`
- `python tools/validation/tool_run_validation.py --repo-root . --profile STRICT`
- `python tools/worldgen/tool_verify_worldgen_lock.py --repo-root .`
- `python tools/xstack/testx/runner.py --repo-root . --profile FAST --cache off --subset test_convergence_plan_deterministic,test_decision_rules_stable`

## Recommended Decision Options

- If ambiguity remains after review, keep the cluster quarantined for XI-4b instead of forcing convergence.
