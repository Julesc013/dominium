Status: Quarantine
Last Reviewed: 2026-03-26
Stability: provisional
Replacement Target: XI-4b manual review resolution

# Quarantine Packet `duplicate.cluster.358afd73ec603557`

- Symbol: `sha256_file`
- Cluster Kind: `near`
- Cluster Resolution: `quarantine`
- Risk Level: `HIGH`
- Canonical Candidate: `tests/determinism/determinism_replay_hash_invariance.py`
- Quarantine Reasons: `planned_quarantine`
- Planned Action Kinds: `quarantine`

## Competing Files

- `tests/determinism/determinism_replay_hash_invariance.py`
- `tests/perf/perf_fixture_contracts.py`

## Scorecard

- `tests/determinism/determinism_replay_hash_invariance.py` disposition=`canonical` rank=`1` total_score=`55.26` risk=`HIGH`
- `tests/perf/perf_fixture_contracts.py` disposition=`quarantine` rank=`2` total_score=`54.07` risk=`HIGH`

## Usage Sites

- Build Targets: `none`
- Docs: `docs/testing/xstack_profiles.md`

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
