Status: Quarantine
Last Reviewed: 2026-03-26
Stability: provisional
Replacement Target: XI-4b manual review resolution

# Quarantine Packet `duplicate.sig.c4dd65a03072664f`

- Symbol: `iter_files`
- Cluster Kind: `exact`
- Cluster Resolution: `quarantine`
- Risk Level: `HIGH`
- Canonical Candidate: `tests/contract/determinism_hardlock_tests.py`
- Quarantine Reasons: `planned_quarantine`
- Planned Action Kinds: `quarantine`

## Competing Files

- `tests/contract/determinism_hardlock_tests.py`
- `tests/invariant/capability_scope_tests.py`
- `tests/invariant/content_id_reference_tests.py`
- `tools/ci/arch_checks.py`

## Scorecard

- `tests/contract/determinism_hardlock_tests.py` disposition=`canonical` rank=`1` total_score=`52.14` risk=`HIGH`
- `tests/invariant/content_id_reference_tests.py` disposition=`quarantine` rank=`2` total_score=`51.81` risk=`HIGH`
- `tests/invariant/capability_scope_tests.py` disposition=`quarantine` rank=`3` total_score=`50.62` risk=`HIGH`
- `tools/ci/arch_checks.py` disposition=`quarantine` rank=`4` total_score=`42.66` risk=`HIGH`

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
