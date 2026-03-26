Status: Quarantine
Last Reviewed: 2026-03-26
Stability: provisional
Replacement Target: XI-4b manual review resolution

# Quarantine Packet `duplicate.sig.3543a9ebc9be015f`

- Symbol: `dg_graph_add_edge_dir`
- Cluster Kind: `exact`
- Cluster Resolution: `quarantine`
- Risk Level: `HIGH`
- Canonical Candidate: `engine/modules/core/graph/dg_graph.c`
- Quarantine Reasons: `planned_quarantine`
- Planned Action Kinds: `quarantine`

## Competing Files

- `engine/modules/core/graph/dg_graph.c`
- `engine/modules/core/graph/dg_graph.h`

## Scorecard

- `engine/modules/core/graph/dg_graph.c` disposition=`canonical` rank=`1` total_score=`85.71` risk=`HIGH`
- `engine/modules/core/graph/dg_graph.h` disposition=`quarantine` rank=`2` total_score=`85.3` risk=`HIGH`

## Usage Sites

- Build Targets: `domino_core`
- Docs: `docs/architecture/CORE_ABSTRACTIONS.md, docs/architecture/SCHEMA_CHANGE_NOTES.md, docs/architecture/truth_perceived_render.md, docs/audit/ELEC1_RETRO_AUDIT.md, docs/audit/FLUID2_RETRO_AUDIT.md, docs/audit/GEO6_RETRO_AUDIT.md, docs/audit/LOGIC_NETWORKGRAPH_BASELINE.md, docs/audit/LOGISTICS_BASELINE.md`

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
