Status: DERIVED
Last Reviewed: 2026-05-16
Supersedes: none
Superseded By: none

Phase: CONVERGE-06
Supersedes: none
Superseded By: none
Stability: provisional

# Contract Convergence

CONVERGE-06 consolidates safe contract-adjacent root material under `contracts/` without changing schema meaning, product identity, runtime behavior, or build semantics beyond required path-reference updates.

## What Moved

- `schema/` moved to `contracts/schema/`.
- `schemas/` merged into `contracts/schema/`.
- Active tooling, scripts, tests, CMake helpers, and GitHub automation references to those root paths were updated to `contracts/schema/`.

## What Did Not Move

- `compat/` stayed at the repository root because it contains Python implementation and shim code.
- `locks/` stayed at the repository root because it contains a concrete deterministic pack lock artifact, not only lockfile schemas.
- `data/registries/` stayed under `data/` because CONVERGE-06 does not split nested data/content ownership.
- Product, runtime, AppShell, domain, content, archive, and generated-output roots were not moved.

## Contracts Are Not Docs

`contracts/` owns machine-readable and version-pinned authority. `docs/` explains contracts, records rationale, and provides human guidance, but documentation does not override machine-readable contract IDs, schemas, registries, or layout contracts.

## Contracts Are Not Runtime Mutable Data

Runtime stores, process locks, IPC locks, package caches, setup transactions, update state, and rollback state are physical projections. They do not belong under `contracts/`.

## Contracts Are Not Game Implementation

Domain schemas and registries may live under `contracts/`, but Process execution, game rules, and domain implementation remain under `game/` or transitional domain roots until CONVERGE-09.

## Lock-Root Split

- `contracts/lock/`: deterministic lockfile schemas and contract definitions.
- `store/locks/`: deterministic content, pack, capability, and compatibility lock artifacts in install/runtime projections.
- `runtime/locks/`: process, IPC, and transient runtime locks.
- `ops/transactions/`: setup, update, rollback plans, stages, commits, and rollback records.

## Future Work

- CONVERGE-07: runtime, AppShell, platform, render, network, diagnostics, and UI convergence.
- CONVERGE-09: domain split into contracts, game, content, docs, and tests.
- CONVERGE-12: stale-doc and cross-reference cleanup.

Domain roots still need file-level split. Do not move a root domain folder wholesale just because its schema material is now under `contracts/schema/`.
