Status: Quarantine
Last Reviewed: 2026-03-26
Stability: provisional
Replacement Target: XI-4b manual review resolution

# Quarantine Packet `duplicate.sig.af46b7cb9240a580`

- Symbol: `dg_graph_sort_node_ids`
- Cluster Kind: `exact`
- Cluster Resolution: `quarantine`
- Risk Level: `HIGH`
- Canonical Candidate: `engine/modules/core/graph/dg_graph_sort.c`
- Quarantine Reasons: `planned_quarantine`
- Planned Action Kinds: `quarantine`

## Competing Files

- `engine/modules/core/graph/dg_graph_sort.c`
- `engine/modules/core/graph/dg_graph_sort.h`

## Scorecard

- `engine/modules/core/graph/dg_graph_sort.c` disposition=`canonical` rank=`1` total_score=`88.69` risk=`HIGH`
- `engine/modules/core/graph/dg_graph_sort.h` disposition=`quarantine` rank=`2` total_score=`87.2` risk=`HIGH`

## Usage Sites

- Build Targets: `domino_core`
- Docs: `docs/architecture/CORE_ABSTRACTIONS.md, docs/architecture/DUPLICATION_DETECTION_RULES.md, docs/architecture/EXECUTION_MODEL.md, docs/architecture/EXECUTION_REORDERING_POLICY.md, docs/architecture/FLOWSYSTEM_STANDARD.md, docs/architecture/INFORMATION_MODEL.md, docs/architecture/NETWORKGRAPH_STANDARD.md, docs/architecture/SCHEMA_CHANGE_NOTES.md`

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
