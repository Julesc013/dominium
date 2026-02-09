Status: DERIVED
Last Reviewed: 2026-02-08
Supersedes: none
Superseded By: none

# PKG Install And Rollback

## Scope

This contract defines cache ingestion, install projection, verification, and
rollback semantics for package-based setup flows.

## Cache Operations

Canonical setup commands:

- `setup cache-add <path>`
- `setup verify-cache`
- `setup export-cache --dest <path>`

Rules:

- `cache-add` verifies every `.dompkg` before admission.
- Cache keys are content hashes.
- Cache verification is deterministic and side-effect free.

## Install Projection

Canonical package install command:

- `setup install --profile <profile_id> --from-cache <path> --platform <p> --arch <a>`

Rules:

- Resolution is capability-based only.
- Missing required capabilities refuse loudly.
- Install projection writes an install lock file and projection digest.
- Same lock file and same cache inputs produce identical projection digest.

## Rollback

Canonical rollback command:

- `setup rollback --install <id> --to previous`

Rules:

- Rollback is lockfile pointer reversal plus deterministic reprojection.
- Rollback must restore previous layout digest exactly.
- Rollback refusal is explicit when no prior lock exists.

## Required Refusal Codes

- `refuse.cache_invalid_package`
- `refuse.cache_verify_failed`
- `refuse.install_profile_missing`
- `refuse.install_capability_mismatch`
- `refuse.install_projection_failed`
- `refuse.rollback_unavailable`
- `refuse.rollback_projection_failed`
