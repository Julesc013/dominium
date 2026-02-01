Status: DERIVED
Last Reviewed: 2026-02-01
Supersedes: none
Superseded By: none

# Setup CLI Reference (SR-7)

Executable: `dominium-setup`

## Commands
- `manifest validate --in <file> [--json]`
- `manifest dump --in <file> --out <file> --format json [--json]`
- `request validate --in <file> [--json]`
- `request dump --in <file> --out <file> --format json [--json]`
- `request make --manifest <file> --op <install|upgrade|repair|uninstall|verify|status> --scope <user|system|portable> --ui-mode <cli|tui|gui>`
  - `--components <csv>` optional
  - `--exclude <csv>` optional
  - `--root <path>` optional
  - `--frontend-id <id>` optional (defaults to `dominium-setup-cli`)
  - `--requested-splat <id>` optional
  - `--ownership <portable|pkg|steam|any>` optional
  - `--platform <triple>` optional
  - `--payload-root <path>` optional
  - `--required-caps <u32>` optional
  - `--prohibited-caps <u32>` optional
  - `--deterministic 0|1` optional (default `1`)
  - `--out-request <file>` required
- `plan --manifest <file> --request <file> --out-plan <file> [--json]`
- `resolve --manifest <file> --request <file> [--json]`
- `dump-plan --plan <file> [--json]`
- `apply --plan <file> [--out-state <file>] [--out-audit <file>] [--out-journal <file>] [--dry-run] [--json]`
- `resume --journal <file> [--out-state <file>] [--out-audit <file>] [--json]`
- `rollback --journal <file> [--out-audit <file>] [--json]`
- `status --journal <file> [--json]`
- `verify --state <file> [--format json|txt] [--json]`
- `uninstall-preview --state <file> [--components <csv>] [--format json|txt] [--json]`
- `audit dump --in <file> --out <file> --format json [--json]`
- `state dump --in <file> --out <file> --format json [--json]`
- `doctor --state <file> --plan <file> --journal <file> --txn-journal <file> --audit <file> [--json]`
- `explain-refusal --audit <file> [--json]`
- `import-legacy-state --in <file> --out <file> --out-audit <file> [--json]`
- `dump-splats [--json]`
- `select-splat --manifest <file> --request <file> [--json]`
- `run --manifest <file> --request <file> --out-state <file> --out-audit <file> [--out-plan <file>] [--out-log <file>] [--json]`

## Aliases
- `dump-audit` is a shorthand for `audit dump`.

## Global Options
- `--use-fake-services <sandbox_root>`: use the fake services backend rooted at `sandbox_root`.
- `--platform <triple>`: when combined with `--use-fake-services`, sets the fake platform triple override.
- `--json`: emit deterministic JSON output.

## Examples
- `dominium-setup request make --manifest manifest.tlv --op install --scope system --ui-mode cli --frontend-id dominium-setup-cli --out-request request.tlv`
- `dominium-setup plan --manifest manifest.tlv --request request.tlv --out-plan plan.tlv`
- `dominium-setup apply --plan plan.tlv --out-state installed_state.tlv --out-audit setup_audit.tlv --out-journal job_journal.tlv --dry-run`
- `dominium-setup dump-splats --json`