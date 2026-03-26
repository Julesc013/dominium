Status: Quarantine
Last Reviewed: 2026-03-26
Stability: provisional
Replacement Target: XI-4b manual review resolution

# Quarantine Packet `duplicate.sig.5e7c08fa33e9f55a`

- Symbol: `d_net_session_add_peer`
- Cluster Kind: `exact`
- Cluster Resolution: `quarantine`
- Risk Level: `HIGH`
- Canonical Candidate: `engine/modules/net/d_net_session.h`
- Quarantine Reasons: `planned_quarantine`
- Planned Action Kinds: `quarantine`

## Competing Files

- `engine/modules/net/d_net_session.c`
- `engine/modules/net/d_net_session.h`

## Scorecard

- `engine/modules/net/d_net_session.h` disposition=`canonical` rank=`1` total_score=`72.26` risk=`HIGH`
- `engine/modules/net/d_net_session.c` disposition=`quarantine` rank=`2` total_score=`70.69` risk=`HIGH`

## Usage Sites

- Build Targets: `none`
- Docs: `docs/audit/ANTI_CHEAT_FRAMEWORK_BASELINE.md, docs/contracts/refusal_contract.md, docs/net/HANDSHAKE_AND_COMPATIBILITY.md`

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
