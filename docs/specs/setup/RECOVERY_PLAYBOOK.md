Status: DERIVED
Last Reviewed: 2026-02-01
Supersedes: none
Superseded By: none

# Setup Recovery Playbook

All recovery flows are driven by `job_journal.tlv` and `txn_journal.tlv`.

## Resume After Failure
1) Inspect status:
   - `dominium-setup status --journal <job_journal.tlv> --json`
2) Resume:
   - `dominium-setup resume --journal <job_journal.tlv> --out-state <installed_state.tlv> --out-audit <setup_audit.tlv>`

## Rollback After Failure
1) Inspect status:
   - `dominium-setup status --journal <job_journal.tlv> --json`
2) Rollback:
   - `dominium-setup rollback --journal <job_journal.tlv> --out-audit <setup_audit.tlv>`

## Forensic Artifacts
- `installed_state.tlv` is written only after successful commit.
- `setup_audit.tlv` is written on success and failure.
- `job_journal.tlv` and `txn_journal.tlv` are required to resume or rollback.