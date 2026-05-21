Status: DERIVED
Last Reviewed: 2026-05-22
Supersedes: none
Superseded By: none
Stability: provisional

# Document Patch Transaction Development Guide

Use document/patch/transaction law when a change affects an authority-bearing document, Workbench-visible document, package/mod/theme descriptor, schema/command descriptor, release/export artifact, AIDE/Codex review patch, CLI/headless edit, or future save/world mutation proof.

The minimum development sequence is:

```text
intent -> command -> capability decision -> patch envelope -> transaction envelope -> dry-run -> validation -> evidence -> commit/export/refusal
```

A direct file write is acceptable only as the output of an accepted transaction or as non-authoritative task scaffolding that does not claim product truth.

## Authoring Rules

Create a document type entry before claiming stable editing support. Planned or provisional document types must not claim stable runtime support.

Create a document reference with a logical identity. `path` is only a locator and must not be treated as authority.

Create patches with a `patch_id`, `patch_kind`, `document_ref`, one registered `operation`, a selector, preconditions, capability refs, and deterministic ordering. Unknown operations must refuse.

Create transactions with command linkage, affected documents/artifacts, validation results, diagnostics, dry-run result, commit policy, rollback policy, status, and evidence where required.

Use `python tools/validators/contracts/check_document_patch_transaction.py --repo-root . --strict` before promoting a new document type, patch kind, transaction fixture, or editor workflow.

## Future Editors

UI, HUD, theme, pack, module, schema, command, and release editors should adapt their visual gestures into patch commands. Rendering and panel state may preview a document, but cannot become document truth.

Headless scripts and AIDE/Codex work units should submit the same envelopes a future Workbench editor would submit. This keeps review, refusal, diagnostics, and evidence deterministic across GUI, CLI, and agent surfaces.
