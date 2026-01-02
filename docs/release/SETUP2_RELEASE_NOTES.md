# Setup2 Release Notes

## Summary
Setup2 is the authoritative installer system with deterministic planning and resumable execution.

## Guarantees
- Deterministic planning and plan digests.
- Stage → verify → commit with atomic transactions.
- Audit and journals for every run.

## Compatibility
- Legacy installs can be imported into `installed_state.tlv`.
- Legacy setup binaries remain buildable behind explicit flags.

## Recovery
- Resume: `dominium-setup2 resume --journal job_journal.tlv`
- Rollback: `dominium-setup2 rollback --journal job_journal.tlv`
- Audit: `dominium-setup2 audit dump --in setup_audit.tlv --out audit.json --format json`
