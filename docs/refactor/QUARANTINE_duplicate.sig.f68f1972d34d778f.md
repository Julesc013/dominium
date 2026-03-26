Status: Quarantine
Last Reviewed: 2026-03-26
Stability: provisional
Replacement Target: XI-4b manual review resolution

# Quarantine Packet `duplicate.sig.f68f1972d34d778f`

- Symbol: `d_container_state_init`
- Cluster Kind: `exact`
- Cluster Resolution: `quarantine`
- Risk Level: `HIGH`
- Canonical Candidate: `engine/modules/core/d_container_state.c`
- Quarantine Reasons: `planned_quarantine`
- Planned Action Kinds: `quarantine`

## Competing Files

- `engine/modules/core/d_container_state.c`
- `engine/modules/core/d_container_state.h`

## Scorecard

- `engine/modules/core/d_container_state.c` disposition=`canonical` rank=`1` total_score=`83.93` risk=`HIGH`
- `engine/modules/core/d_container_state.h` disposition=`quarantine` rank=`2` total_score=`80.06` risk=`HIGH`

## Usage Sites

- Build Targets: `domino_core`
- Docs: `docs/architecture/BUGREPORT_MODEL.md, docs/architecture/BUNDLE_MODEL.md, docs/architecture/CANON_INDEX.md, docs/architecture/CHECKPOINTING_MODEL.md, docs/architecture/CONTRACTS_INDEX.md, docs/architecture/ECONOMIC_MODEL.md, docs/architecture/LOCKLIST.md, docs/architecture/REPLAY_FORMAT.md`

## Tests Involved

- `python tools/compat/tool_run_interop_stress.py --repo-root .`
- `python tools/convergence/tool_run_convergence_gate.py --repo-root .`
- `python tools/mvp/tool_run_all_stress.py --repo-root .`
- `python tools/mvp/tool_run_disaster_suite.py --repo-root .`
- `python tools/mvp/tool_run_product_boot_matrix.py --repo-root .`
- `python tools/mvp/tool_verify_baseline_universe.py --repo-root .`
- `python tools/mvp/tool_verify_gameplay_loop.py --repo-root .`
- `python tools/validation/tool_run_validation.py --repo-root . --profile STRICT`
- `python tools/worldgen/tool_verify_worldgen_lock.py --repo-root .`
- `python tools/xstack/testx/runner.py --repo-root . --profile FAST --cache off --subset test_convergence_plan_deterministic,test_decision_rules_stable`

## Recommended Decision Options

- If ambiguity remains after review, keep the cluster quarantined for XI-4b instead of forcing convergence.
