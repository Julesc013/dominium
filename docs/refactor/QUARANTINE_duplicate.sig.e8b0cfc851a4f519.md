Status: Quarantine
Last Reviewed: 2026-03-26
Stability: provisional
Replacement Target: XI-4b manual review resolution

# Quarantine Packet `duplicate.sig.e8b0cfc851a4f519`

- Symbol: `dom_core_t`
- Cluster Kind: `exact`
- Cluster Resolution: `quarantine`
- Risk Level: `HIGH`
- Canonical Candidate: `engine/include/domino/sim.h`
- Quarantine Reasons: `phase_boundary_deferred, planned_quarantine, requires_single_action_full_gate`
- Planned Action Kinds: `rewire, deprecate, quarantine`

## Competing Files

- `engine/include/domino/inst.h`
- `engine/include/domino/pkg.h`
- `engine/include/domino/sim.h`
- `engine/modules/core/core_internal.h`
- `libs/contracts/include/dom_contracts/tool_api.h`

## Scorecard

- `engine/include/domino/sim.h` disposition=`canonical` rank=`1` total_score=`90.18` risk=`HIGH`
- `engine/include/domino/inst.h` disposition=`quarantine` rank=`2` total_score=`85.95` risk=`HIGH`
- `engine/modules/core/core_internal.h` disposition=`quarantine` rank=`3` total_score=`84.64` risk=`HIGH`
- `libs/contracts/include/dom_contracts/tool_api.h` disposition=`quarantine` rank=`4` total_score=`80.95` risk=`HIGH`
- `engine/include/domino/pkg.h` disposition=`drop` rank=`5` total_score=`77.26` risk=`HIGH`

## Usage Sites

- Build Targets: `none`
- Docs: `docs/app/COMPATIBILITY_ENFORCEMENT.md, docs/architecture/ARCH_REPO_LAYOUT.md, docs/architecture/REPORT_GAME_ARCH_DECISIONS.md, docs/archive/app/APR4_ENGINE_GAME_INTERFACE_INVENTORY.md, docs/archive/ci/PHASE1_AUDIT_REPORT.md, docs/audit/BR0_PUBLIC_HEADER_FAILS.md, docs/audit/DOC_INDEX.md, docs/audit/REPO_TREE_INDEX.md`

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
