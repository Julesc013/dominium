Status: Quarantine
Last Reviewed: 2026-03-26
Stability: provisional
Replacement Target: XI-4b manual review resolution

# Quarantine Packet `duplicate.cluster.ae5bc131a9a3fcb9`

- Symbol: `set_inputs`
- Cluster Kind: `near`
- Cluster Resolution: `quarantine`
- Risk Level: `MED`
- Canonical Candidate: `game/include/dominium/rules/governance/governance_system.h`
- Quarantine Reasons: `phase_boundary_deferred, planned_quarantine, requires_medium_risk_batch_gate, requires_single_action_full_gate`
- Planned Action Kinds: `rewire, deprecate, quarantine`

## Competing Files

- `client/presentation/render_prep_system.h`
- `game/include/dominium/rules/agents/agent_system.h`
- `game/include/dominium/rules/economy/economy_system.h`
- `game/include/dominium/rules/governance/governance_system.h`
- `game/include/dominium/rules/scale/interest_system.h`
- `game/include/dominium/rules/war/war_system.h`

## Scorecard

- `game/include/dominium/rules/governance/governance_system.h` disposition=`canonical` rank=`1` total_score=`70.89` risk=`MED`
- `game/include/dominium/rules/agents/agent_system.h` disposition=`drop` rank=`2` total_score=`64.88` risk=`HIGH`
- `game/include/dominium/rules/war/war_system.h` disposition=`drop` rank=`3` total_score=`64.45` risk=`MED`
- `game/include/dominium/rules/economy/economy_system.h` disposition=`drop` rank=`4` total_score=`64.14` risk=`MED`
- `game/include/dominium/rules/scale/interest_system.h` disposition=`quarantine` rank=`5` total_score=`64.05` risk=`HIGH`
- `client/presentation/render_prep_system.h` disposition=`drop` rank=`6` total_score=`59.31` risk=`MED`

## Usage Sites

- Build Targets: `none`
- Docs: `docs/GLOSSARY.md, docs/architecture/ADOPTION_PROTOCOL.md, docs/archive/ci/PHASE6_AUDIT_REPORT.md, docs/audit/CANON_CONFORMANCE_REPORT.md, docs/audit/COMPILE0_RETRO_AUDIT.md, docs/audit/CONCURRENCY0_RETRO_AUDIT.md, docs/audit/DOC_INDEX.md, docs/audit/GEO_CONSTITUTION_BASELINE.md`

## Tests Involved

- `python tools/convergence/tool_run_convergence_gate.py --repo-root .`
- `python tools/mvp/tool_run_disaster_suite.py --repo-root .`
- `python tools/mvp/tool_verify_baseline_universe.py --repo-root .`
- `python tools/mvp/tool_verify_gameplay_loop.py --repo-root .`
- `python tools/security/tool_run_trust_strict_suite.py --repo-root .`
- `python tools/validation/tool_run_validation.py --repo-root . --profile STRICT`
- `python tools/worldgen/tool_verify_worldgen_lock.py --repo-root .`
- `python tools/xstack/testx/runner.py --repo-root . --profile FAST --cache off --subset test_convergence_plan_deterministic,test_decision_rules_stable`

## Recommended Decision Options

- Rewire call sites only after confirming the secondary file is not an active product entrypoint.
- Deprecate the secondary file only after it is removed from default build targets and no longer carries unrelated active symbols.
- If ambiguity remains after review, keep the cluster quarantined for XI-4b instead of forcing convergence.
