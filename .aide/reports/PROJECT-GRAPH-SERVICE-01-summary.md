# PROJECT-GRAPH-SERVICE-01 Summary

Status: PASS_WITH_WARNINGS

## Changed Files

- `contracts/project_graph/project_graph_model.contract.toml`
- `contracts/project_graph/project_graph_derivation_policy.contract.toml`
- `contracts/project_graph/node.schema.json`
- `contracts/project_graph/edge.schema.json`
- `contracts/project_graph/snapshot.schema.json`
- `contracts/project_graph/impact_query.schema.json`
- `contracts/project_graph/node_kind.registry.json`
- `contracts/project_graph/edge_kind.registry.json`
- `contracts/project_graph/confidence.registry.json`
- `contracts/project_graph/completeness_level.registry.json`
- `contracts/project_graph/query_kind.registry.json`
- `tools/validators/contracts/check_project_graph.py`
- `tests/contract/project_graph/fixtures/**`
- `docs/architecture/project_graph_service.md`
- `docs/architecture/project_graph_impact_model.md`
- `docs/workbench/project_graph_model.md`
- `docs/aide/project_graph_context.md`
- `docs/repo/audits/PROJECT_GRAPH_SERVICE_01.md`
- `.aide/reports/PROJECT-GRAPH-SERVICE-01-*`

## Node Kinds Added

file, source_root, component, public_surface, contract, schema, registry, protocol, command, result, refusal, diagnostic, service, provider, capability, module, workspace, app, pack, profile, artifact, test, validator, evidence_packet, release_artifact, replacement_packet, version_surface, portability_row, aide_task, domain, document_type, patch_type, transaction_type.

## Edge Kinds Added

owns, contains, declares, implements, consumes, invokes, produces, emits, validates, tests, packages, mounts, depends_on, supersedes, replaces, deprecates, refuses_with, requires_capability, provides_capability, selected_by, displayed_by, generated_by, documented_by, proven_by, affected_by, blocks, unblocks.

## Validator And Fixtures

Added `check_project_graph.py` with strict, json, fixtures, and inventory modes. Added 11 fixtures covering valid node, edge, snapshot, impact query, and negative unknown-kind, missing-reference, path-identity, proof-evidence, source-ref, and source-truth-authority cases.

## Warnings

- AuditX stale warning remains known debt.
- Dependency-direction strict remains 0 violations with 68 warnings.
- AIDE validate review-packet warnings remain.
- Runtime graph service, graph generator, and Workbench graph viewer were not implemented.
- Graph snapshots are fixture/contract-level only.

## Non-Goals

No runtime graph engine, Workbench graph viewer, Project Graph Explorer, AIDE graph-driven routing, release publication, CMake target, package runtime, gameplay, renderer, or native GUI work was implemented.

## Next Recommended Task

COMPOSITION-RESOLVER-LAW-01