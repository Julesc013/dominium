Status: DERIVED
Last Reviewed: 2026-05-22
Supersedes: prior PROJECT_GRAPH_SERVICE_01 narrow helper audit dated 2026-05-21
Superseded By: none
Stability: provisional
Task: PROJECT-GRAPH-SERVICE-01
Result: PASS_WITH_WARNINGS

# PROJECT_GRAPH_SERVICE_01

PROJECT-GRAPH-SERVICE-01 adds the first contract-level project graph model for Dominium. The graph is defined as a derived, evidence-bearing index over contracts, manifests, registries, descriptors, tests, and evidence packets. It is not source truth.

## Changed Surface

- `contracts/project_graph/project_graph_model.contract.toml`
- `contracts/project_graph/project_graph_derivation_policy.contract.toml`
- `contracts/project_graph/node.schema.json`
- `contracts/project_graph/edge.schema.json`
- `contracts/project_graph/snapshot.schema.json`
- `contracts/project_graph/impact_query.schema.json`
- `contracts/project_graph/*_kind.registry.json`
- `contracts/project_graph/confidence.registry.json`
- `contracts/project_graph/completeness_level.registry.json`
- `tools/validators/contracts/check_project_graph.py`
- `tests/contract/project_graph/fixtures/**`
- Project graph architecture, Workbench, AIDE, and impact docs

## Validation Summary

Targeted project graph validation passed before closeout. Broader related validators are recorded in `.aide/reports/PROJECT-GRAPH-SERVICE-01-validation.json`.

## Known Warnings

- Runtime project graph service not implemented.
- Workbench graph viewer not implemented.
- Graph generator not implemented.
- Snapshots are fixture/contract level only.
- Full CTest remains out of scope for this contract/docs/validator task.
