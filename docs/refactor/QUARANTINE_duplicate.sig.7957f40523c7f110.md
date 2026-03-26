Status: Quarantine
Last Reviewed: 2026-03-26
Stability: provisional
Replacement Target: XI-4b manual review resolution

# Quarantine Packet `duplicate.sig.7957f40523c7f110`

- Symbol: `_rows_from_registry`
- Cluster Kind: `exact`
- Cluster Resolution: `quarantine`
- Risk Level: `HIGH`
- Canonical Candidate: `src/geo/path/path_engine.py`
- Quarantine Reasons: `planned_quarantine`
- Planned Action Kinds: `quarantine`

## Competing Files

- `src/geo/edit/geometry_state_engine.py`
- `src/geo/kernel/geo_kernel.py`
- `src/geo/overlay/overlay_merge_engine.py`
- `src/geo/path/path_engine.py`

## Scorecard

- `src/geo/path/path_engine.py` disposition=`canonical` rank=`1` total_score=`62.32` risk=`HIGH`
- `src/geo/kernel/geo_kernel.py` disposition=`quarantine` rank=`2` total_score=`57.62` risk=`HIGH`
- `src/geo/edit/geometry_state_engine.py` disposition=`quarantine` rank=`3` total_score=`57.56` risk=`HIGH`
- `src/geo/overlay/overlay_merge_engine.py` disposition=`quarantine` rank=`4` total_score=`54.94` risk=`HIGH`

## Usage Sites

- Build Targets: `none`
- Docs: `docs/CONTRIBUTING.md, docs/GLOSSARY.md, docs/PHILOSOPHY.md, docs/app/COMPATIBILITY_ENFORCEMENT.md, docs/app/READONLY_ADAPTER.md, docs/appshell/CLI_REFERENCE.md, docs/appshell/COMMANDS_AND_REFUSALS.md, docs/appshell/TUI_FRAMEWORK.md`

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
