Status: Quarantine
Last Reviewed: 2026-03-26
Stability: provisional
Replacement Target: XI-4b manual review resolution

# Quarantine Packet `duplicate.cluster.37595cfb84bb09c8`

- Symbol: `degrade`
- Cluster Kind: `near`
- Cluster Resolution: `quarantine`
- Risk Level: `HIGH`
- Canonical Candidate: `game/include/dominium/rules/governance/governance_system.h`
- Quarantine Reasons: `phase_boundary_deferred, planned_quarantine, requires_single_action_full_gate`
- Planned Action Kinds: `rewire, deprecate, quarantine`

## Competing Files

- `client/presentation/render_prep_system.h`
- `game/include/dominium/rules/agents/agent_system.h`
- `game/include/dominium/rules/economy/economy_system.h`
- `game/include/dominium/rules/governance/governance_system.h`
- `game/include/dominium/rules/war/war_system.h`

## Scorecard

- `game/include/dominium/rules/governance/governance_system.h` disposition=`canonical` rank=`1` total_score=`70.89` risk=`HIGH`
- `game/include/dominium/rules/war/war_system.h` disposition=`quarantine` rank=`2` total_score=`67.35` risk=`HIGH`
- `game/include/dominium/rules/economy/economy_system.h` disposition=`drop` rank=`3` total_score=`67.04` risk=`HIGH`
- `game/include/dominium/rules/agents/agent_system.h` disposition=`drop` rank=`4` total_score=`65.85` risk=`HIGH`
- `client/presentation/render_prep_system.h` disposition=`drop` rank=`5` total_score=`59.31` risk=`HIGH`

## Usage Sites

- Build Targets: `none`
- Docs: `docs/architecture/CANON_INDEX.md, docs/architecture/CONTRACTS_INDEX.md, docs/audit/CANON_MAP.md, docs/audit/COMPUTE_BUDGET_BASELINE.md, docs/audit/DOC_INDEX.md, docs/audit/META_COMPUTE0_RETRO_AUDIT.md, docs/audit/MODULE_DUPLICATION_REPORT.md, docs/audit/PROC0_RETRO_AUDIT.md`

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

- Rewire call sites only after confirming the secondary file is not an active product entrypoint.
- Deprecate the secondary file only after it is removed from default build targets and no longer carries unrelated active symbols.
- If ambiguity remains after review, keep the cluster quarantined for XI-4b instead of forcing convergence.
