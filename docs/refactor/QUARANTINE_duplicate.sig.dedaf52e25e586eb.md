Status: Quarantine
Last Reviewed: 2026-03-26
Stability: provisional
Replacement Target: XI-4b manual review resolution

# Quarantine Packet `duplicate.sig.dedaf52e25e586eb`

- Symbol: `_fingerprint`
- Cluster Kind: `exact`
- Cluster Resolution: `quarantine`
- Risk Level: `HIGH`
- Canonical Candidate: `tools/xstack/testx/tests/test_handshake_deterministic_outputs.py`
- Quarantine Reasons: `planned_quarantine`
- Planned Action Kinds: `quarantine`

## Competing Files

- `tests/invariant/process_registry_execution_tests.py`
- `tools/xstack/testx/tests/test_handshake_deterministic_outputs.py`

## Scorecard

- `tools/xstack/testx/tests/test_handshake_deterministic_outputs.py` disposition=`canonical` rank=`1` total_score=`63.63` risk=`HIGH`
- `tests/invariant/process_registry_execution_tests.py` disposition=`quarantine` rank=`2` total_score=`61.11` risk=`HIGH`

## Usage Sites

- Build Targets: `none`
- Docs: `docs/audit/MODULE_DUPLICATION_REPORT.md, docs/audit/MULTIPLAYER_CONTRACT_FOUNDATION_REPORT.md, docs/audit/REPO_TREE_INDEX.md, docs/audit/TIME_CONSTITUTION_BASELINE.md, docs/audit/UNIVERSE_PHYSICS_PROFILE_BASELINE.md, docs/governance/REPOX_RULESETS.md, docs/guides/RELEASE_READINESS_CHECKLIST.md, docs/release/PROVISIONAL_FEATURE_LIST.md`

## Tests Involved

- `python tools/compat/tool_run_interop_stress.py --repo-root .`
- `python tools/convergence/tool_run_convergence_gate.py --repo-root .`
- `python tools/mvp/tool_run_disaster_suite.py --repo-root .`
- `python tools/mvp/tool_verify_baseline_universe.py --repo-root .`
- `python tools/mvp/tool_verify_gameplay_loop.py --repo-root .`
- `python tools/time/tool_verify_longrun_ticks.py --repo-root .`
- `python tools/validation/tool_run_validation.py --repo-root . --profile STRICT`
- `python tools/worldgen/tool_verify_worldgen_lock.py --repo-root .`
- `python tools/xstack/testx/runner.py --repo-root . --profile FAST --cache off --subset test_convergence_plan_deterministic,test_decision_rules_stable`

## Recommended Decision Options

- If ambiguity remains after review, keep the cluster quarantined for XI-4b instead of forcing convergence.
