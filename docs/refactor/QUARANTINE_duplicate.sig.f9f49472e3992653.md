Status: Quarantine
Last Reviewed: 2026-03-26
Stability: provisional
Replacement Target: XI-4b manual review resolution

# Quarantine Packet `duplicate.sig.f9f49472e3992653`

- Symbol: `dom_sys_vtable`
- Cluster Kind: `exact`
- Cluster Resolution: `quarantine`
- Risk Level: `HIGH`
- Canonical Candidate: `libs/contracts/include/dom_contracts/dom_plat_sys.h`
- Quarantine Reasons: `planned_quarantine`
- Planned Action Kinds: `quarantine`

## Competing Files

- `libs/contracts/include/dom_contracts/dom_plat_sys.h`
- `libs/contracts/include/dom_contracts/dom_plat_term.h`
- `libs/contracts/include/dom_contracts/dom_plat_ui.h`

## Scorecard

- `libs/contracts/include/dom_contracts/dom_plat_sys.h` disposition=`canonical` rank=`1` total_score=`58.55` risk=`HIGH`
- `libs/contracts/include/dom_contracts/dom_plat_ui.h` disposition=`quarantine` rank=`2` total_score=`58.55` risk=`HIGH`
- `libs/contracts/include/dom_contracts/dom_plat_term.h` disposition=`quarantine` rank=`3` total_score=`56.62` risk=`HIGH`

## Usage Sites

- Build Targets: `none`
- Docs: `none`

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
