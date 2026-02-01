Status: DERIVED
Last Reviewed: 2026-02-01
Supersedes: none
Superseded By: none

# Setup Operations Quickstart

Common commands:
- plan: `dominium-setup plan --manifest <file> --request <file> --out-plan <file>`
- apply: `dominium-setup apply --plan <file> --out-state <file> --out-audit <file> --out-journal <file>`
- resume: `dominium-setup resume --journal <file>`
- rollback: `dominium-setup rollback --journal <file>`
- verify: `dominium-setup verify --state <file>`
- doctor: `dominium-setup doctor --state <file> --audit <file> --journal <file>`

Where to find artifacts:
- state: pass `--out-state <file>` or read the CLI JSON output paths.
- audit: pass `--out-audit <file>` or read the CLI JSON output paths.
- journals: pass `--out-journal <file>` or read the CLI JSON output paths.

First-response recovery checklist:
- Capture `installed_state.tlv`, `setup_audit.tlv`, and `job_journal.tlv`.
- Run `dominium-setup status --journal <file>` to determine resumability.
- If resumable, run `dominium-setup resume --journal <file>`.
- If not resumable, run `dominium-setup rollback --journal <file>`.
- Re-run `dominium-setup verify --state <file>` after recovery.

Escalation path:
- docs/setup/RECOVERY_PLAYBOOK.md
- docs/setup/TROUBLESHOOTING.md
- docs/setup/AUDIT_MODEL.md
- docs/setup/ERROR_TAXONOMY.md