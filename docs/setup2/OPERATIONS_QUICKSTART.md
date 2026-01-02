# Setup2 Operations Quickstart

Common commands:
- plan: `dominium-setup2 plan --manifest <file> --request <file> --out-plan <file>`
- apply: `dominium-setup2 apply --plan <file> --out-state <file> --out-audit <file> --out-journal <file>`
- resume: `dominium-setup2 resume --journal <file>`
- rollback: `dominium-setup2 rollback --journal <file>`
- verify: `dominium-setup2 verify --state <file>`
- doctor: `dominium-setup2 doctor --state <file> --audit <file> --journal <file>`

Where to find artifacts:
- state: pass `--out-state <file>` or read the CLI JSON output paths.
- audit: pass `--out-audit <file>` or read the CLI JSON output paths.
- journals: pass `--out-journal <file>` or read the CLI JSON output paths.

First-response recovery checklist:
- Capture `installed_state.tlv`, `setup_audit.tlv`, and `job_journal.tlv`.
- Run `dominium-setup2 status --journal <file>` to determine resumability.
- If resumable, run `dominium-setup2 resume --journal <file>`.
- If not resumable, run `dominium-setup2 rollback --journal <file>`.
- Re-run `dominium-setup2 verify --state <file>` after recovery.

Escalation path:
- docs/setup2/RECOVERY_PLAYBOOK.md
- docs/setup2/TROUBLESHOOTING.md
- docs/setup2/AUDIT_MODEL.md
- docs/setup2/ERROR_TAXONOMY.md
