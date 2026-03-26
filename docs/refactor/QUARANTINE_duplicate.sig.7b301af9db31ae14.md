Status: Quarantine
Last Reviewed: 2026-03-26
Stability: provisional
Replacement Target: XI-4b manual review resolution

# Quarantine Packet `duplicate.sig.7b301af9db31ae14`

- Symbol: `d_input_init`
- Cluster Kind: `exact`
- Cluster Resolution: `quarantine`
- Risk Level: `HIGH`
- Canonical Candidate: `engine/include/domino/input/input.h`
- Quarantine Reasons: `planned_quarantine`
- Planned Action Kinds: `quarantine`

## Competing Files

- `engine/include/domino/input/input.h`
- `engine/modules/input/input.c`

## Scorecard

- `engine/include/domino/input/input.h` disposition=`canonical` rank=`1` total_score=`86.13` risk=`HIGH`
- `engine/modules/input/input.c` disposition=`quarantine` rank=`2` total_score=`85.24` risk=`HIGH`

## Usage Sites

- Build Targets: `none`
- Docs: `docs/GLOSSARY.md, docs/accessibility/ACCESSIBILITY_MODEL.md, docs/agents/AGENT_NON_GOALS.md, docs/app/CLIENT_IDE_START_POINTS.md, docs/app/CLIENT_READONLY_INTEGRATION.md, docs/app/CLIENT_UI_LAYER.md, docs/app/CLI_CONTRACTS.md, docs/app/RUNTIME_LOOP.md`

## Tests Involved

- `python tools/compat/tool_run_interop_stress.py --repo-root .`
- `python tools/convergence/tool_run_convergence_gate.py --repo-root .`
- `python tools/mvp/tool_run_disaster_suite.py --repo-root .`
- `python tools/mvp/tool_verify_baseline_universe.py --repo-root .`
- `python tools/mvp/tool_verify_gameplay_loop.py --repo-root .`
- `python tools/time/tool_verify_longrun_ticks.py --repo-root .`
- `python tools/validation/tool_run_validation.py --repo-root . --profile STRICT`
- `python tools/worldgen/tool_verify_worldgen_lock.py --repo-root .`
- `python tools/xstack/testx/runner.py --repo-root . --profile FAST --cache off --subset test_convergence_plan_deterministic,test_decision_rules_stable`

## Recommended Decision Options

- If ambiguity remains after review, keep the cluster quarantined for XI-4b instead of forcing convergence.
