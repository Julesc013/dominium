Status: Quarantine
Last Reviewed: 2026-03-26
Stability: provisional
Replacement Target: XI-4b manual review resolution

# Quarantine Packet `duplicate.sig.58077b5e45de94ee`

- Symbol: `apply_override`
- Cluster Kind: `exact`
- Cluster Resolution: `quarantine`
- Risk Level: `HIGH`
- Canonical Candidate: `src/meta/profile/__init__.py`
- Quarantine Reasons: `planned_quarantine`
- Planned Action Kinds: `quarantine`

## Competing Files

- `src/meta/__init__.py`
- `src/meta/profile/__init__.py`

## Scorecard

- `src/meta/profile/__init__.py` disposition=`canonical` rank=`1` total_score=`77.44` risk=`HIGH`
- `src/meta/__init__.py` disposition=`quarantine` rank=`2` total_score=`68.1` risk=`HIGH`

## Usage Sites

- Build Targets: `none`
- Docs: `docs/CONTRIBUTING.md, docs/accessibility/ACCESSIBILITY_MODEL.md, docs/app/CLI_CONTRACTS.md, docs/app/UI_MODES.md, docs/appshell/COMMANDS_AND_REFUSALS.md, docs/appshell/TUI_FRAMEWORK.md, docs/appshell/VIRTUAL_PATHS.md, docs/architecture/ANTI_CHEAT_AS_LAW.md`

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
