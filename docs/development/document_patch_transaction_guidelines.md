Status: DERIVED
Last Reviewed: 2026-05-22
Supersedes: none
Superseded By: none
Stability: provisional

# Document Patch Transaction Guidelines

This compatibility note points development work at `docs/development/document_patch_transaction.md` and the contract surfaces under `contracts/document`, `contracts/patch`, and `contracts/transaction`.

The older narrow `contracts/document/document_patch_transaction.*` helper remains a provisional single-document helper. The law introduced by DOCUMENT-PATCH-TRANSACTION-RUNTIME-01 is broader and contract-only: it defines the envelopes future editors and command surfaces must use, without implementing a runtime transaction executor.
