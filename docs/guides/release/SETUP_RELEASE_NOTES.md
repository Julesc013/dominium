Status: DERIVED
Last Reviewed: 2026-02-01
Supersedes: none
Superseded By: none

# Setup Release Notes

## Summary
Setup is the authoritative installer system with deterministic planning and resumable execution.

## Guarantees
- Deterministic planning and plan digests.
- Stage → verify → commit with atomic transactions.
- Audit and journals for every run.

## Compatibility
- Legacy installs can be imported into `installed_state.tlv`.
- Legacy setup binaries remain buildable behind explicit flags.

## Recovery
- Resume: `dominium-setup resume --journal job_journal.tlv`
- Rollback: `dominium-setup rollback --journal job_journal.tlv`
- Audit: `dominium-setup audit dump --in setup_audit.tlv --out audit.json --format json`