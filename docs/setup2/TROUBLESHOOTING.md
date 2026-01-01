# Setup2 Troubleshooting

## Common failures
- `TLV_BAD_MAGIC` or `TLV_BAD_CRC`: input file is corrupt or wrong format.
- `NO_COMPATIBLE_SPLAT`: request and manifest have no compatible provider.
- `PLAN_DIGEST_MISMATCH`: plan file was modified or does not match request.
- `REQUEST_MISMATCH`: request bytes differ from plan digest.

## First steps
1) Inspect the audit: `dominium-setup2 audit dump --in setup_audit.tlv --out audit.json --format json`
2) Check job status: `dominium-setup2 status --journal job_journal.tlv --json`
3) Validate state: `dominium-setup2 doctor --state installed_state.tlv --plan install_plan.tlv --journal job_journal.tlv --audit setup_audit.tlv --json`

## Recovery
- Resume: `dominium-setup2 resume --journal job_journal.tlv`
- Rollback: `dominium-setup2 rollback --journal job_journal.tlv`

## Support bundle
- Use diagnostics scripts under `scripts/diagnostics/` to capture logs and artifacts.
