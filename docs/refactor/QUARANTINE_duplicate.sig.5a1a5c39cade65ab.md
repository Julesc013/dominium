Status: Quarantine
Last Reviewed: 2026-03-26
Stability: provisional
Replacement Target: XI-4b manual review resolution

# Quarantine Packet `duplicate.sig.5a1a5c39cade65ab`

- Symbol: `_ordered_tokens`
- Cluster Kind: `exact`
- Cluster Resolution: `quarantine`
- Risk Level: `HIGH`
- Canonical Candidate: `src/platform/platform_probe.py`
- Quarantine Reasons: `planned_quarantine`
- Planned Action Kinds: `quarantine`

## Competing Files

- `src/appshell/ui_mode_selector.py`
- `src/compat/capability_negotiation.py`
- `src/platform/platform_probe.py`

## Scorecard

- `src/platform/platform_probe.py` disposition=`canonical` rank=`1` total_score=`61.19` risk=`HIGH`
- `src/compat/capability_negotiation.py` disposition=`quarantine` rank=`2` total_score=`59.29` risk=`HIGH`
- `src/appshell/ui_mode_selector.py` disposition=`quarantine` rank=`3` total_score=`52.14` risk=`HIGH`

## Usage Sites

- Build Targets: `none`
- Docs: `docs/app/RUNTIME_LOOP.md, docs/governance/REPOX_RULESETS.md`

## Tests Involved

- `python tools/compat/tool_run_interop_stress.py --repo-root .`
- `python tools/convergence/tool_run_convergence_gate.py --repo-root .`
- `python tools/mvp/tool_run_all_stress.py --repo-root .`
- `python tools/mvp/tool_run_disaster_suite.py --repo-root .`
- `python tools/mvp/tool_run_product_boot_matrix.py --repo-root .`
- `python tools/mvp/tool_verify_baseline_universe.py --repo-root .`
- `python tools/mvp/tool_verify_gameplay_loop.py --repo-root .`
- `python tools/time/tool_verify_longrun_ticks.py --repo-root .`
- `python tools/validation/tool_run_validation.py --repo-root . --profile STRICT`
- `python tools/worldgen/tool_verify_worldgen_lock.py --repo-root .`
- `python tools/xstack/testx/runner.py --repo-root . --profile FAST --cache off --subset test_convergence_plan_deterministic,test_decision_rules_stable`

## Recommended Decision Options

- If ambiguity remains after review, keep the cluster quarantined for XI-4b instead of forcing convergence.
