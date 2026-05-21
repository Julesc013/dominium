Status: DERIVED
Last Reviewed: 2026-05-21
Supersedes: none
Superseded By: none
Stability: provisional

# Project Graph Service

The project graph service is a narrow contract-data helper for loading,
validating, sorting, and fingerprinting project graph payloads. It models
nodes, edges, dependencies, and proofs so validators and future governed tools
can reason over a bounded graph without inventing a Workbench project explorer
or release projection.

## Boundary

- Contract owner: `contracts/project_graph/project_graph_service.contract.toml`.
- Payload schema: `contracts/project_graph/project_graph.schema.json`.
- Runtime helper: `runtime/project_graph/service.py`.
- Validator: `tools/validators/contracts/check_project_graph_service.py`.

The helper is read-only over payloads. It does not mutate authoritative project
truth, does not write repository state, and does not create Process outcomes.
Any future truth mutation must remain process-only and must be introduced by a
separate, reviewed task.

## Payload Shape

Project graph payloads contain:

- `nodes`: stable dotted identifiers with kind, title, status, optional paths,
  and optional evidence references.
- `edges`: descriptive relationships between known nodes.
- `dependencies`: DAG-enforced ordering or validation requirements between
  known nodes.
- `proofs`: evidence-backed or result-backed proof rows for nodes.

Proof rows may reference `contracts/evidence/evidence_ref.schema.json` and
`contracts/result/result.schema.json`. Passing proofs must carry at least one
evidence or result reference.

## Determinism

The helper sorts known graph rows deterministically:

- nodes by `node_id`
- edges by `(source_node_id, target_node_id, edge_kind, edge_id)`
- dependencies by `(node_id, depends_on_node_id, dependency_kind, dependency_id)`
- proofs by `proof_id`

Dependency order is computed with a deterministic topological sort using
lexicographic tie-breaking. Cycles are refused as validation errors. The graph
fingerprint is `sha256` over canonical JSON of the sorted payload. No RNG
streams are used.

## Non-Goals

This service does not:

- implement a broad project UI or Workbench explorer
- publish release, install, or update projections
- infer canon from graph convenience
- promote generated graph outputs into semantic authority
- reconcile ownership splits outside the payload contract
- mutate authoritative state or bypass Process-only mutation

## Validation

The targeted validator is:

```text
python tools/validators/contracts/check_project_graph_service.py --repo-root . --strict --fixtures
```

The contract test script is:

```text
python tests/contract/project_graph_service/project_graph_service_contract_tests.py
```
