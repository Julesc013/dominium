# Lockfile Contracts

Status: PROVISIONAL
Phase: CONVERGE-06

This directory is reserved for deterministic lockfile schemas and lockfile contract definitions.

Concrete lock artifacts belong in install/runtime projections such as `store/locks/`. Process and IPC locks belong under `runtime/locks/`. Setup, update, and rollback transaction state belongs under `ops/transactions/`.

## POST-CONVERGE-04 Note

`locks/pack_lock.mvp_default.json` remains a concrete source lock artifact with embedded identity metadata and distribution copy behavior. Move only lockfile schemas or contract definitions here after protected lock ownership review.
