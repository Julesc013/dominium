
# POST-CONVERGE-10K Contract Registry Findings

## Summary

POST-CONVERGE-10K checked 9 contract-registry failures from `INV-NEW-CONTRACT-REQUIRES-ENTRY`. All checked failures were caused by four current architecture contract IDs already declared in architecture data/spec/tooling but missing semantic registry acceptance rows.

## Findings

| Contract ID | Failure Count | Classification | Safe Fix | Registry | Authority Basis |
| --- | ---: | --- | --- | --- | --- |
| `contract.arch.graph.v1` | 3 | accepted_current_missing_metadata | yes | `data/registries/semantic_contract_registry.json` | Declared by architecture_graph.v1.json, ARCHITECTURE_GRAPH_SPEC_v1.md, and Xi architecture review tooling. |
| `contract.arch.module_boundaries.v1` | 2 | accepted_current_missing_metadata | yes | `data/registries/semantic_contract_registry.json` | Declared by module_boundary_rules.v1.json and consumed by Xi architecture review tooling. |
| `contract.arch.module_registry.v1` | 2 | accepted_current_missing_metadata | yes | `data/registries/semantic_contract_registry.json` | Declared by module_registry.v1.json and consumed by Xi architecture review tooling. |
| `contract.arch.single_engine_registry.v1` | 2 | accepted_current_missing_metadata | yes | `data/registries/semantic_contract_registry.json` | Declared by single_engine_registry.json and consumed by Xi architecture review tooling. |

## Safe Fixes Applied

- Added four acceptance rows to `data/registries/semantic_contract_registry.json`.
- Preserved existing contract/schema/data semantics.
- Did not accept product/distribution-proof-dependent entries.

## Deferred/Blocked

No contract-registry backlog entries remain after the safe metadata update. The focused RepoX tuple still fails on non-contract families recorded in the blocker report.
