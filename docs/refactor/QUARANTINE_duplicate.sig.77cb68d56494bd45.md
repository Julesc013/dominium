Status: Quarantine
Last Reviewed: 2026-03-26
Stability: provisional
Replacement Target: XI-4b manual review resolution

# Quarantine Packet `duplicate.sig.77cb68d56494bd45`

- Symbol: `dg_frame_id_is_world`
- Cluster Kind: `exact`
- Cluster Resolution: `quarantine`
- Risk Level: `HIGH`
- Canonical Candidate: `engine/modules/world/frame/dg_frame.c`
- Quarantine Reasons: `planned_quarantine`
- Planned Action Kinds: `quarantine`

## Competing Files

- `engine/modules/world/frame/dg_frame.c`
- `engine/modules/world/frame/dg_frame.h`

## Scorecard

- `engine/modules/world/frame/dg_frame.c` disposition=`canonical` rank=`1` total_score=`88.69` risk=`HIGH`
- `engine/modules/world/frame/dg_frame.h` disposition=`quarantine` rank=`2` total_score=`86.85` risk=`HIGH`

## Usage Sites

- Build Targets: `domino_core`
- Docs: `docs/GLOSSARY.md, docs/app/CLI_CONTRACTS.md, docs/appshell/CLI_REFERENCE.md, docs/appshell/TOOL_REFERENCE.md, docs/architecture/EXPLORATION_SCALING_PROOF.md, docs/architecture/SLICE_0_CONTRACT.md, docs/architecture/WORLDDEFINITION.md, docs/architecture/WORLDDEFINITION_CONTRACT.md`

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
