Status: Quarantine
Last Reviewed: 2026-03-26
Stability: provisional
Replacement Target: XI-4b manual review resolution

# Quarantine Packet `duplicate.sig.511b31bf4b674361`

- Symbol: `d_agent_validate`
- Cluster Kind: `exact`
- Cluster Resolution: `quarantine`
- Risk Level: `HIGH`
- Canonical Candidate: `engine/modules/ai/d_agent.h`
- Quarantine Reasons: `planned_quarantine`
- Planned Action Kinds: `quarantine`

## Competing Files

- `engine/modules/ai/d_agent.c`
- `engine/modules/ai/d_agent.h`

## Scorecard

- `engine/modules/ai/d_agent.h` disposition=`canonical` rank=`1` total_score=`77.2` risk=`HIGH`
- `engine/modules/ai/d_agent.c` disposition=`quarantine` rank=`2` total_score=`76.67` risk=`HIGH`

## Usage Sites

- Build Targets: `none`
- Docs: `docs/app/CLI_CONTRACTS.md, docs/audit/MOB7_RETRO_AUDIT.md, docs/audit/MODULE_DUPLICATION_REPORT.md, docs/audit/REPO_TREE_INDEX.md, docs/ci/CI_ENFORCEMENT_MATRIX.md, docs/ci/HYGIENE_QUEUE.md, docs/contracts/refusal_contract.md, docs/embodiment/MOVEMENT_PROCESSES.md`

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
