Status: Quarantine
Last Reviewed: 2026-03-26
Stability: provisional
Replacement Target: XI-4b manual review resolution

# Quarantine Packet `duplicate.sig.f224f4fb18710a87`

- Symbol: `_read_lines`
- Cluster Kind: `exact`
- Cluster Resolution: `quarantine`
- Risk Level: `HIGH`
- Canonical Candidate: `tools/auditx/analyzers/e119_unlogged_refusal_smell.py`
- Quarantine Reasons: `planned_quarantine`
- Planned Action Kinds: `quarantine`

## Competing Files

- `tools/auditx/analyzers/e119_unlogged_refusal_smell.py`
- `tools/auditx/analyzers/e132_missing_decision_log_smell.py`
- `tools/auditx/analyzers/e225_infinite_leak_loop_smell.py`

## Scorecard

- `tools/auditx/analyzers/e119_unlogged_refusal_smell.py` disposition=`canonical` rank=`1` total_score=`56.55` risk=`HIGH`
- `tools/auditx/analyzers/e132_missing_decision_log_smell.py` disposition=`quarantine` rank=`2` total_score=`56.55` risk=`HIGH`
- `tools/auditx/analyzers/e225_infinite_leak_loop_smell.py` disposition=`quarantine` rank=`3` total_score=`56.55` risk=`HIGH`

## Usage Sites

- Build Targets: `none`
- Docs: `none`

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
