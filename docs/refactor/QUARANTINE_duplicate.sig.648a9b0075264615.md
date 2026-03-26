Status: Quarantine
Last Reviewed: 2026-03-26
Stability: provisional
Replacement Target: XI-4b manual review resolution

# Quarantine Packet `duplicate.sig.648a9b0075264615`

- Symbol: `dg_rebuild_init`
- Cluster Kind: `exact`
- Cluster Resolution: `quarantine`
- Risk Level: `HIGH`
- Canonical Candidate: `engine/modules/sim/dg_rebuild.c`
- Quarantine Reasons: `planned_quarantine`
- Planned Action Kinds: `quarantine`

## Competing Files

- `engine/modules/sim/dg_rebuild.c`
- `engine/modules/sim/dg_rebuild.h`

## Scorecard

- `engine/modules/sim/dg_rebuild.c` disposition=`canonical` rank=`1` total_score=`76.79` risk=`HIGH`
- `engine/modules/sim/dg_rebuild.h` disposition=`quarantine` rank=`2` total_score=`70.66` risk=`HIGH`

## Usage Sites

- Build Targets: `domino_core`
- Docs: `docs/architecture/CANON_INDEX.md, docs/audit/CANON_MAP.md, docs/audit/DOC_INDEX.md, docs/net/HANDSHAKE_AND_COMPATIBILITY.md, docs/specs/SPEC_DETERMINISM.md, docs/specs/SPEC_GRAPH_TOOLKIT.md, docs/specs/SPEC_SIM_SCHEDULER.md, docs/specs/SPEC_TRANS.md`

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
