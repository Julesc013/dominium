# Setup2 TUI Reference

Executable: `dominium-setup2-tui`

## Modes
- Interactive wizard (default)
- Non-interactive generation and apply

## Non-Interactive Flags
- `--defaults`: accept default selections.
- `--yes`: auto-confirm prompts.
- `--out-request <file>`: write `install_request.tlv`.
- `--apply`: run plan + apply after request generation.
- `--deterministic 0|1`: default `1`.
- `--use-fake-services <sandbox_root>`
- `--platform <triple>` (fake services override)
- `--frontend-id <id>` (defaults to `tui`)

## Output
- Emits `install_request.tlv`.
- When `--apply` is set, emits:
  - `install_plan.tlv`
  - `installed_state.tlv`
  - `setup_audit.tlv`
  - `job_journal.tlv`
  - `txn_journal.tlv`
