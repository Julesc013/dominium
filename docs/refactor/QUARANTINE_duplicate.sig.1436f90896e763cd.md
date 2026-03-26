Status: Quarantine
Last Reviewed: 2026-03-26
Stability: provisional
Replacement Target: XI-4b manual review resolution

# Quarantine Packet `duplicate.sig.1436f90896e763cd`

- Symbol: `dg_agent_db_count`
- Cluster Kind: `exact`
- Cluster Resolution: `quarantine`
- Risk Level: `HIGH`
- Canonical Candidate: `engine/modules/agent/dg_agent.c`
- Quarantine Reasons: `planned_quarantine`
- Planned Action Kinds: `quarantine`

## Competing Files

- `engine/modules/agent/dg_agent.c`
- `engine/modules/agent/dg_agent.h`

## Scorecard

- `engine/modules/agent/dg_agent.c` disposition=`canonical` rank=`1` total_score=`88.69` risk=`HIGH`
- `engine/modules/agent/dg_agent.h` disposition=`quarantine` rank=`2` total_score=`87.2` risk=`HIGH`

## Usage Sites

- Build Targets: `domino_core`
- Docs: `docs/GLOSSARY.md, docs/architecture/PERFORMANCE_METRICS.md, docs/audit/MODULE_DUPLICATION_REPORT.md, docs/audit/REPO_TREE_INDEX.md, docs/canon/glossary_v1.md, docs/ci/CI_ENFORCEMENT_MATRIX.md, docs/contracts/refusal_contract.md, docs/net/ANTI_CHEAT_MODULES.md`

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
