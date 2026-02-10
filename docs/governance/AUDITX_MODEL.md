Status: DERIVED
Last Reviewed: 2026-02-10
Supersedes: none
Superseded By: none

# AuditX Model

AuditX is the semantic audit axis in the governance stack.

## Scope

- RepoX enforces structural invariants.
- TestX validates runtime behavior.
- AuditX reports semantic drift, debt, and ambiguity.

## Initial Contract

- Findings are deterministic and machine-readable.
- AuditX is non-gating by default.
- AuditX emits reports; it does not auto-mutate runtime code.

## Shared Analysis Graph

- Graph nodes: files, symbols, commands, schemas, packs, tests, products.
- Graph edges: includes/imports, command bindings, schema usage, pack dependencies.
- Traversal and graph hashing are deterministic.
