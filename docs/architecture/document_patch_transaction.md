Status: DERIVED
Last Reviewed: 2026-05-22
Supersedes: none
Superseded By: none
Stability: provisional
Binding Sources: `docs/canon/constitution_v1.md`, `docs/canon/glossary_v1.md`, `AGENTS.md`, `contracts/document/document_type.schema.json`, `contracts/document/document_ref.schema.json`, `contracts/patch/patch.schema.json`, `contracts/transaction/transaction.schema.json`

# Document, Patch, Transaction, And Evidence Law

Dominium treats meaningful mutation as a deterministic process, not a private file edit. The required shape is:

```text
intent -> command -> capability/refusal check -> document patch or transaction -> validation/dry-run -> diagnostics/evidence -> commit/export/package or refusal
```

## Vocabulary

A document is a typed editable or presentable logical object. Document identity is not a file path.

An artifact is a persisted or versioned thing with identity, hash, and provenance. A document may point at an artifact, but artifact identity and document identity are separate.

A patch is a typed proposed change to a document, artifact-backed document, or logical object. Patch identity is not a git diff path.

A transaction is a bounded collection of patches plus capability decisions, validation results, diagnostics, evidence, dry-run result, commit/refusal state, and rollback policy. Transaction identity is not a commit hash.

A command is the invocation surface that may create, validate, dry-run, apply, export, or refuse patches and transactions.

Evidence is the proof record of what was requested, validated, changed, refused, exported, committed, or rolled back.

Workbench panel state is not document truth. AIDE and Codex patches must become reviewable transactions when entering product or Workbench law. File writes must be outputs of accepted transactions, not arbitrary side effects.

## Contract Surfaces

Document type law is defined by `contracts/document/document_type.schema.json` and `contracts/document/document_type.registry.json`. Document references use `contracts/document/document_ref.schema.json`; their `path` field is only a locator.

Patch law is defined by `contracts/patch/patch.schema.json`, `contracts/patch/patch_operation.registry.json`, and `contracts/patch/patch_policy.contract.toml`. The initial operation set is `set`, `insert`, `remove`, `move`, `replace`, `merge`, `annotate`, `import_asset`, `generate`, and `no_op`.

Transaction law is defined by `contracts/transaction/transaction.schema.json`, `contracts/transaction/transaction_status.registry.json`, `contracts/transaction/transaction_commit_policy.registry.json`, `contracts/transaction/transaction_policy.contract.toml`, `contracts/transaction/evidence_binding.schema.json`, and `contracts/transaction/rollback_handle.schema.json`.

Diagnostic and refusal links for this lane are local provisional surfaces in `contracts/transaction/transaction_diagnostic.registry.json` and `contracts/transaction/transaction_refusal.registry.json`. They avoid claiming stable global diagnostic/refusal registration while parallel registry work is active.

## Lifecycle

A transaction moves through explicit statuses only: `proposed`, `validated`, `refused`, `dry_run_passed`, `dry_run_failed`, `committed`, `rolled_back`, `superseded`, or `retired`.

Commit policy is explicit: `dry_run_only`, `manual_review_required`, `auto_commit_allowed`, `package_export_only`, or `evidence_only`. A `dry_run_only` transaction cannot claim `committed`. A committed transaction must cite `evidence_packet_ref` and a passed dry-run result.

Rollback must be explicit. If rollback is unavailable, the transaction must say so and carry a diagnostic/refusal when rollback was required.

## Non-Goals

This law does not implement a runtime transaction executor, Workbench editor, UI/HUD editor, module loader, package runtime, renderer, platform layer, native GUI, gameplay system, CRDT/OT engine, or broad save/world mutation engine.
