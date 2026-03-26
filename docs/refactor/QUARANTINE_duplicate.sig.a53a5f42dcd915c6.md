Status: Quarantine
Last Reviewed: 2026-03-26
Stability: provisional
Replacement Target: XI-4b manual review resolution

# Quarantine Packet `duplicate.sig.a53a5f42dcd915c6`

- Symbol: `d_state_machine_update`
- Cluster Kind: `exact`
- Cluster Resolution: `quarantine`
- Risk Level: `HIGH`
- Canonical Candidate: `engine/modules/state/state.c`
- Quarantine Reasons: `planned_quarantine`
- Planned Action Kinds: `quarantine`

## Competing Files

- `engine/include/domino/state/state.h`
- `engine/modules/state/state.c`

## Scorecard

- `engine/modules/state/state.c` disposition=`canonical` rank=`1` total_score=`87.26` risk=`HIGH`
- `engine/include/domino/state/state.h` disposition=`quarantine` rank=`2` total_score=`86.73` risk=`HIGH`

## Usage Sites

- Build Targets: `domino_core`
- Docs: `docs/architecture/CANON_INDEX.md, docs/architecture/COMPATIBILITY_MODEL.md, docs/architecture/PRODUCT_SHELL_CONTRACT.md, docs/audit/CANON_MAP.md, docs/audit/DOC_INDEX.md, docs/audit/FIELD_LAYER_BASELINE.md, docs/audit/GUIDE_GEOMETRY_BASELINE.md, docs/audit/MOBILITY_NETWORK_BASELINE.md`

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
