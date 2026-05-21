Status: DERIVED
Last Reviewed: 2026-05-21
Supersedes: none
Superseded By: none
Stability: provisional
Task: PROJECT-GRAPH-SERVICE-01
Result: PASS

# PROJECT_GRAPH_SERVICE_01

PROJECT-GRAPH-SERVICE-01 defines a narrow project graph contract and
deterministic helper for graph nodes, edges, dependencies, and proofs.

## Scope

Changed surface is limited to:

- `contracts/project_graph/**`
- `runtime/project_graph/**`
- `tools/validators/contracts/check_project_graph_service.py`
- `tests/contract/project_graph_service/**`
- `docs/architecture/project_graph_service.md`
- `docs/repo/audits/PROJECT_GRAPH_SERVICE_01.md`

## Boundary And Non-Goals

The service is a read-only contract-data helper. It loads, validates,
canonicalizes, topologically sorts, and fingerprints project graph payloads.

It does not implement a broad project UI, Workbench explorer, release
projection, install/update graph, or authoritative truth mutation path. Future
truth mutation remains process-only and out of scope for this task.

## Contract Impact

Added provisional contract/schema surfaces:

- `contracts/project_graph/project_graph.schema.json`
- `contracts/project_graph/project_graph_service.contract.toml`

No existing schema, canon, planning, release, public surface, or Workbench files
were changed.

## Determinism

The helper uses deterministic sorting for nodes, edges, dependencies, proofs,
evidence references, result references, and known string-list fields. Dependency
ordering is DAG-based and lexicographically tie-broken. Cycles are refused.
No RNG streams are used.

## Validation

Completed targeted validation:

- `py -3 -B tools/validators/contracts/check_project_graph_service.py --repo-root . --strict --fixtures`:
  PASS, 0 errors, 0 warnings, 6 fixtures checked.
- `py -3 -B tests/contract/project_graph_service/project_graph_service_contract_tests.py`:
  PASS.
- `py -3 -B -c "<python syntax parse for project graph helper, validator, and test script>"`:
  PASS, 4 Python files parsed.
- `py -3 -B -c "<JSON parse for project graph schema and fixtures>"`:
  PASS, 7 JSON files parsed.
