Status: Quarantine
Last Reviewed: 2026-03-26
Stability: provisional
Replacement Target: XI-4b manual review resolution

# Quarantine Packet `duplicate.sig.764854ea1f96e934`

- Symbol: `d_env_tick`
- Cluster Kind: `exact`
- Cluster Resolution: `quarantine`
- Risk Level: `HIGH`
- Canonical Candidate: `engine/modules/env/d_env.c`
- Quarantine Reasons: `planned_quarantine`
- Planned Action Kinds: `quarantine`

## Competing Files

- `engine/modules/env/d_env.c`
- `engine/modules/env/d_env_field.h`

## Scorecard

- `engine/modules/env/d_env.c` disposition=`canonical` rank=`1` total_score=`81.43` risk=`HIGH`
- `engine/modules/env/d_env_field.h` disposition=`quarantine` rank=`2` total_score=`77.68` risk=`HIGH`

## Usage Sites

- Build Targets: `domino_core`
- Docs: `docs/SURVIVAL_SLICE.md, docs/architecture/REPORT_GAME_ARCH_DECISIONS.md, docs/architecture/srz_contract.md, docs/archive/ci/DOCS_VALIDATION_REPORT.md, docs/audit/DOC_INDEX.md, docs/audit/auditx/FINDINGS.md, docs/net/MULTIPLAYER_MODEL_OVERVIEW.md, docs/release/PROVISIONAL_FEATURE_LIST.md`

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
