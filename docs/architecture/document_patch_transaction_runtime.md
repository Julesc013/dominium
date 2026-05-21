Status: DERIVED
Last Reviewed: 2026-05-21
Supersedes: none
Superseded By: none
Stability: provisional
Binding Sources: `docs/canon/constitution_v1.md`, `docs/canon/glossary_v1.md`, `AGENTS.md`, `docs/reference/specs/setup/TRANSACTIONS.md`, `docs/architecture/SETUP_TRANSACTION_MODEL.md`, `contracts/document/document_patch_transaction.schema.json`

# Document Patch Transaction Runtime

## Purpose

The document patch transaction runtime is a narrow substrate for applying explicit, typed patch transactions to JSON-like Dominium documents.

Its only runtime target is the `content` member of a single document matching `contracts/document/document.schema.json`.
It exists to support deterministic contract-level document mutation where a caller has already supplied a lawful transaction.

This runtime is not:

- a save system
- a product editor
- a storage commit layer
- a package/update transaction manager
- a UI mutation path
- a schema migration path
- a broad document authoring model

## Contract Boundary

The contract surface is:

- `contracts/document/document_patch_transaction.schema.json`
- `contracts/document/document_patch_transaction.contract.toml`
- `runtime/document/patch_transaction.py`
- `tools/validators/contracts/check_document_patch_transactions.py`

A transaction must declare:

- exact transaction schema identity and version
- target `document_id`
- target document `schema_id`
- expected canonical content hash
- minimal authority context metadata
- an ordered list of explicit operations

The runtime applies operations in listed order. There is no discovery order, hash-map order, wall-clock order, thread timing, or background mutation path.

## Supported Operations

Supported operations are intentionally small:

- `test`: verify an existing path has an exact JSON value
- `add`: add a new object member or insert at an explicit array index
- `replace`: replace an existing object member or array item
- `remove`: remove an existing object member or array item

Paths are arrays of explicit segments. Object targets require string keys. Array targets require integer indexes. The runtime does not parse JSON Pointer strings and does not create missing parents.

## Refusal Semantics

The helper refuses rather than repairing or migrating when:

- transaction schema identity or version differs
- target document id or schema id differs
- expected content hash differs
- authority metadata is absent or malformed
- content or values are not JSON-like
- operation paths are malformed
- an operation would create implicit parents
- an operation would replace, remove, or test a missing target
- an `add` would overwrite an existing object member

Refusal is atomic. A refused transaction returns no patched document.

## Doctrine Alignment

This substrate upholds:

- `docs/canon/constitution_v1.md` A1 determinism
- `docs/canon/constitution_v1.md` A2 process-only mutation
- `docs/canon/constitution_v1.md` A3 law-gated authority and explicit refusal
- `docs/canon/constitution_v1.md` C1 version semantics
- `docs/canon/constitution_v1.md` C4 no silent coercion
- `AGENTS.md` Sections 5.2, 5.3, 5.5, and 5.6

The runtime helper is Process-like but does not itself grant authority or commit authoritative truth. It validates and applies a declared transaction to an in-memory document copy. Higher layers must still route authoritative truth mutation through lawful Process execution and commit boundaries.

## Non-Goals

This patch does not introduce:

- persistent document storage
- save or replay integration
- package or release transaction logic
- UI controls
- provider or network calls
- document schema migration
- unknown-field reinterpretation
- broad runtime orchestration under `runtime/`

Those remain separate governed work and are not authorized by this substrate.
