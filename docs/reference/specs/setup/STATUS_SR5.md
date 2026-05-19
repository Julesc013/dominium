Status: DERIVED
Last Reviewed: 2026-02-01
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-ARCHIVE
Replacement Target: legacy reference surface retained without current binding authority

# SR-5 Status

SR-5 implements execution: job DAG, journals, and transactions.

## Added
- `job_journal.tlv` and `txn_journal.tlv` schemas.
- Stage → verify → commit pipeline with resume/rollback.
- Failpoints for deterministic crash testing.

## Not yet implemented
- Full adapter packaging execution in CI.
- Platform-specific registration behavior (stubbed).
