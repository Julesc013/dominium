# Troubleshooting (Setup Core + CLI)

This guide covers deterministic, headless diagnostics for Setup Core workflows.

## Quick checks (exact commands)

- CLI version:
  - `dominium-setup version --format json --deterministic 1`
- Validate a manifest:
  - `dominium-setup manifest validate --in <path-to.dsumanifest> --format json --deterministic 1`
- Verify integrity:
  - `dominium-setup verify --state <install_root>/.dsu/installed_state.dsustate --format json --deterministic 1`
- Export audit log:
  - `dominium-setup export-log --log audit.dsu.log --out audit.json --format json --deterministic 1`
- Dry-run rollback:
  - `dominium-setup rollback --journal <path-to/txn.dsujournal> --dry-run --deterministic 1`

## Exit codes (stable)

Exit codes follow `docs/setup/CLI_REFERENCE.md`:

- `0` success
- `1` failure
- `2` verification issues detected
- `3` invalid input (manifest/state/plan/args)
- `4` unsupported operation (platform/build limitations)

## Common failures and fixes

### `status_code=3` / `invalid_input`

Typical causes:

- Manifest path wrong or corrupt.
- Installed state missing or invalid.
- Plan file missing or wrong format.

Fix:

- Re-run `manifest validate` or `plan` with correct paths.
- Ensure `installed_state.dsustate` exists under `<install_root>/.dsu/`.

### `status_code=2` on `verify`

Meaning:

- Verification completed but found missing/modified/extra files.

Fix:

- Re-run `export-invocation` + `plan --invocation` + `apply` using the same manifest/state.
- If state is trusted but files are not, reinstall/repair to restore owned files.

### Apply fails mid-commit

Meaning:

- Transaction engine halted and may have rolled back automatically.

Fix:

- Run `dominium-setup rollback --journal <path-to/txn.dsujournal> --deterministic 1`.
- Inspect `audit.dsu.log` and journal entries for the failing step.

### Platform adapter missing

Meaning:

- `platform-register`/`platform-unregister` returns `status_code=3`.

Fix:

- Ensure the appropriate adapter binary is available:
  - Steam: `dominium-setup-steam`
  - Linux: `dominium-setup-linux`
  - Windows: `dominium-setup-win`

## Invariants and prohibitions

- Do not edit `installed_state.dsustate` manually; it is authoritative.
- Do not delete `.dsu_txn/` while a rollback is pending; it contains the journal.
- Do not infer install roots from logs; only the installed state is authoritative.

## See also

- `docs/setup/FORENSICS_AND_RECOVERY.md`
- `docs/setup/TRANSACTION_ENGINE.md`
- `docs/setup/JOURNAL_FORMAT.md`
