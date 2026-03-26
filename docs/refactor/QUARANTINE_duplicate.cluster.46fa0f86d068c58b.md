Status: Quarantine
Last Reviewed: 2026-03-26
Stability: provisional
Replacement Target: XI-4b manual review resolution

# Quarantine Packet `duplicate.cluster.46fa0f86d068c58b`

- Symbol: `_sorted_unique_strings`
- Cluster Kind: `near`
- Cluster Resolution: `quarantine`
- Risk Level: `HIGH`
- Canonical Candidate: `src/core/graph/network_graph_engine.py`
- Quarantine Reasons: `phase_boundary_deferred, planned_quarantine, requires_single_action_full_gate`
- Planned Action Kinds: `merge, rewire, deprecate, quarantine`

## Competing Files

- `src/core/constraints/constraint_engine.py`
- `src/core/flow/flow_engine.py`
- `src/core/graph/network_graph_engine.py`
- `src/core/graph/routing_engine.py`
- `src/interior/compartment_flow_builder.py`
- `src/interior/compartment_flow_engine.py`
- `src/interior/interior_engine.py`
- `src/materials/maintenance/decay_engine.py`
- `src/materials/materialization/materialization_engine.py`

## Scorecard

- `src/core/graph/network_graph_engine.py` disposition=`canonical` rank=`1` total_score=`64.17` risk=`HIGH`
- `src/core/graph/routing_engine.py` disposition=`quarantine` rank=`2` total_score=`62.74` risk=`HIGH`
- `src/core/flow/flow_engine.py` disposition=`quarantine` rank=`3` total_score=`59.29` risk=`HIGH`
- `src/interior/interior_engine.py` disposition=`quarantine` rank=`4` total_score=`56.59` risk=`HIGH`
- `src/core/constraints/constraint_engine.py` disposition=`merge` rank=`5` total_score=`55.48` risk=`HIGH`
- `src/interior/compartment_flow_builder.py` disposition=`drop` rank=`6` total_score=`53.31` risk=`HIGH`
- `src/materials/materialization/materialization_engine.py` disposition=`drop` rank=`7` total_score=`52.93` risk=`HIGH`
- `src/interior/compartment_flow_engine.py` disposition=`drop` rank=`8` total_score=`52.72` risk=`HIGH`
- `src/materials/maintenance/decay_engine.py` disposition=`drop` rank=`9` total_score=`48.67` risk=`HIGH`

## Usage Sites

- Build Targets: `none`
- Docs: `docs/audit/REPO_TREE_INDEX.md, docs/mobility/MOBILITY_EXTENSION_CONTRACT.md`

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

- Review file-local deltas and port only unique behavior into the canonical file.
- Rewire call sites only after confirming the secondary file is not an active product entrypoint.
- Deprecate the secondary file only after it is removed from default build targets and no longer carries unrelated active symbols.
- If ambiguity remains after review, keep the cluster quarantined for XI-4b instead of forcing convergence.
