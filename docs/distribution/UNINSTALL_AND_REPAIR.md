Status: DERIVED
Last Reviewed: 2026-02-01
Supersedes: none
Superseded By: none

# Uninstall and Repair (SHIP-1)

Status: binding.
Scope: safe uninstall, repair, and rollback behavior.

## Repair

- Validates install integrity.
- Re-stages missing or corrupted binaries.
- Preserves user data.
- Emits a compat_report and ops log entry.

## Uninstall

- Removes install_root only.
- NEVER deletes data_root by default.
- Provides an explicit `--remove-data` option for data removal.
- If data_root is nested under install_root, it is preserved by relocation.

## Rollback

- Restores the most recent backup created during repair/update.
- Preserves data_root.
- Logs the rollback reason and transaction id.

## References

- `docs/architecture/SETUP_TRANSACTION_MODEL.md`
- `docs/distribution/SETUP_GUARANTEES.md`