Status: Quarantine
Last Reviewed: 2026-03-26
Stability: provisional
Replacement Target: XI-4b manual review resolution

# Quarantine Packet `duplicate.cluster.89003e55999f4931`

- Symbol: `migration_state`
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
- `game/include/dominium/rules/scale/interest_system.h`
- `game/include/dominium/rules/scale/world_streaming_system.h`
- `game/include/dominium/rules/war/war_system.h`

## Scorecard

- `game/include/dominium/rules/governance/governance_system.h` disposition=`canonical` rank=`1` total_score=`73.27` risk=`HIGH`
- `game/include/dominium/rules/economy/economy_system.h` disposition=`quarantine` rank=`2` total_score=`66.07` risk=`HIGH`
- `game/include/dominium/rules/scale/interest_system.h` disposition=`drop` rank=`3` total_score=`65.98` risk=`HIGH`
- `game/include/dominium/rules/agents/agent_system.h` disposition=`drop` rank=`4` total_score=`65.85` risk=`HIGH`
- `game/include/dominium/rules/war/war_system.h` disposition=`quarantine` rank=`5` total_score=`64.45` risk=`HIGH`
- `game/include/dominium/rules/scale/world_streaming_system.h` disposition=`drop` rank=`6` total_score=`62.71` risk=`HIGH`
- `client/presentation/render_prep_system.h` disposition=`drop` rank=`7` total_score=`61.69` risk=`HIGH`

## Usage Sites

- Build Targets: `none`
- Docs: `docs/ARCHITECTURE.md, docs/GLOSSARY.md, docs/architecture/ADOPTION_PROTOCOL.md, docs/architecture/CANON_INDEX.md, docs/architecture/CONTRACTS_INDEX.md, docs/architecture/EXTENSION_MAP.md, docs/architecture/SCHEMA_CHANGE_NOTES.md, docs/architecture/SYSTEM_TOPOLOGY_MAP.md`

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
