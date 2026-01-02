# Setup2 Job Engine

The job engine executes `install_plan.tlv` using a deterministic job DAG.

## Job Kinds
- STAGE: materialize artifacts into the stage root.
- VERIFY: hash verification of staged content.
- COMMIT: atomic swap or file-by-file commit into install roots.
- REGISTER: perform registration intents (may be no-op for unsupported caps).
- WRITE_STATE: write `installed_state.tlv` atomically.
- WRITE_AUDIT: write `setup_audit.tlv` (always).
- CLEANUP_STAGE: best-effort cleanup of stage root.

## Deterministic Job IDs
- Job IDs are assigned in canonical order based on:
  - job kind
  - install root
  - component id
  - artifact id
  - target path

## Journaling
- `job_journal.tlv` is created before execution and updated after each job.
- Checkpoints record `job_id`, `status`, and `last_completed_step`.
- Resume and rollback are driven solely by `job_journal.tlv`.

## Execution Order
1) STAGE
2) VERIFY
3) COMMIT
4) REGISTER
5) WRITE_STATE
6) WRITE_AUDIT
7) CLEANUP_STAGE
