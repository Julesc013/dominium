Status: DERIVED
Last Reviewed: 2026-05-22
Supersedes: prior narrow project graph service note dated 2026-05-21
Superseded By: none
Stability: provisional

# Project Graph Service

The project graph is an indexed, machine-readable, evidence-bearing map over repo source truth. It exists so validators, Workbench, AIDE/Codex, release tooling, and future agents can ask impact and provenance questions without treating the graph as a second authority.

Source truth remains in contracts, manifests, registries, public headers, package manifests, app descriptors, module descriptors, provider descriptors, tests, and evidence packets. A graph fact must cite `source_ref`; missing graph facts do not imply missing functionality. Graph drift must be detectable by comparing source commit, generator identity, generator version, schema version, and source references.

## Contract Surface

- Model law: `contracts/project_graph/project_graph_model.contract.toml`
- Derivation policy: `contracts/project_graph/project_graph_derivation_policy.contract.toml`
- Node schema: `contracts/project_graph/node.schema.json`
- Edge schema: `contracts/project_graph/edge.schema.json`
- Snapshot schema: `contracts/project_graph/snapshot.schema.json`
- Impact query schema: `contracts/project_graph/impact_query.schema.json`
- Registries: `node_kind`, `edge_kind`, `confidence`, `completeness_level`, and `query_kind`
- Validator: `tools/validators/contracts/check_project_graph.py`
- Fixtures: `tests/contract/project_graph/fixtures/**`

The earlier narrow runtime helper and payload schema remain separate and read-only. This task does not extend runtime graph behavior.

## Node And Edge Model

Nodes identify typed entities such as files, roots, components, contracts, schemas, registries, commands, results, refusals, diagnostics, services, providers, capabilities, modules, workspaces, apps, packs, profiles, artifacts, tests, evidence packets, release artifacts, replacement packets, version surfaces, portability rows, AIDE tasks, domains, document types, patch types, and transaction types.

Edges identify explicit relationships such as ownership, containment, declaration, implementation, consumption, invocation, production, emission, validation, test coverage, packaging, mounting, dependency, supersession, replacement, deprecation, refusal, capability requirement/provision, selection, display, generation, documentation, proof, impact, blocking, and unblocking.

Graph edges are not source include/import dependencies unless a source explicitly emits an edge with a graph `edge_kind`.

## Snapshot And Evidence

A graph snapshot records `snapshot_id`, repo ref, source commit, generator id/version, graph schema version, node/edge counts, diagnostics, evidence, completeness level, and known gaps. `proof_index` and `release_index` snapshots require evidence. Fixture-level snapshots are sufficient for this task.

## Non-Goals

This task does not implement a graph generator, runtime project graph engine, Workbench graph viewer, Project Graph Explorer, graph-driven AIDE routing, package runtime, module loader, release publisher, gameplay code, renderer code, or CMake target.