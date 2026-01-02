# Transaction Engine (Plan S-4)

Setup Core applies installation changes through a journaled transaction engine (`dsu_txn`) built on a strict, root-scoped filesystem layer (`dsu_fs`). The engine is designed to be deterministic, auditable, and rollback-safe after mid-transaction failures.

## State Machine

### 1) Stage

- Derive the install root from the plan/state.
- Create a transaction root (default: `<install_root>.txn/<journal_id_hex>`).
- Materialize payload files under the transaction root:
  - Staged files: `.dsu_txn/staged/<target_relpath>`
  - Staged installed-state: `.dsu_txn/state/new.dsustate`
- Generate the full journal file before mutating the live install.

### 2) Verify

- Hash-verify all staged files against the expected SHA-256 digests stored in the plan.
- Validate protected paths (reject `..`, absolute injection, and internal prefix collisions).
- Validate journal path resolution for both forward and rollback paths.
- Best-effort disk free space check (via platform interface).

### 3) Commit

- Apply journal entries in deterministic order:
  - Directory entries first (parents before children)
  - File entries sorted by canonical target path
  - Installed-state write entry last
- Before each entry is executed, append a progress record to the journal (append-only).
- On any commit error, immediately roll back using the inverse journal in reverse order.

### 4) Rollback

- Execute inverse operations in exact reverse order.
- Leave the transaction root and journal intact for forensics.
- `dominium-setup rollback --journal <file>` replays rollback from the on-disk journal.

## File locations (defaults)

- Transaction root: `<install_root>.txn/<journal_id_hex>`
- Staging root: `<txn_root>/.dsu_txn/staged`
- State staging: `<txn_root>/.dsu_txn/state/new.dsustate`
- Journal file: `<txn_root>/.dsu_txn/journal/txn.dsujournal`
- Installed state: `<install_root>/.dsu/installed_state.dsustate`

## Journal Format

Journal files are binary and append-only. The full record-level format is locked in `docs/setup/JOURNAL_FORMAT.md`.

### Header

- `magic`: `DSUJ`
- `version`: `1`
- `endian_marker`
- `journal_id` (`u64`)
- `plan_digest` (`u64`)

### Records

Records are tagged containers containing TLVs and a record checksum (`u64` digest).

Metadata is stored as `NOOP` records:

- `install_root` (absolute canonical)
- `txn_root` (absolute canonical)
- `state_path` (relative to install root)
- `commit_progress` (`u32`, repeatable; last value wins)

Forward mutation entries (stored as a list and replayed deterministically):

- `CREATE_DIR`
- `REMOVE_DIR`
- `COPY_FILE`
- `MOVE_FILE`
- `DELETE_FILE`
- `WRITE_STATE`

Paths inside entries are stored as canonical relative DSU paths (`/` separators).

Root indices are stable:

- `0`: install root
- `1`: transaction root

## Entry Semantics (Forward + Rollback)

Every forward entry has an explicit inverse:

- `CREATE_DIR install:<dir>` → rollback removes the directory if it did not preexist.
- `MOVE_FILE install:<p> -> txn:<p>` (backup) → rollback moves `txn:<p> -> install:<p>`.
- `MOVE_FILE txn:.dsu_txn/staged:<p> -> install:<p>` (install) → rollback moves `install:<p> -> txn:.dsu_txn/staged:<p>`.
- `WRITE_STATE` behaves like a file move, and is ordered last in commit.

Progress records are written *before* executing each entry. Rollback treats missing forward targets as no-ops, so a crash between “progress append” and “entry execution” remains rollback-safe.

## Rollback Guarantees

- No live install is modified until a complete journal has been written.
- Commit is fail-fast and performs rollback automatically on any error.
- Rollback order is exact reverse of the commit order.
- Installed-state is updated only at the end of commit; the write is journaled and rollbackable.

## Failure Scenarios

- **Stage fails** (payload missing/corrupt, path rejection): no live install mutation occurs.
- **Verify fails** (hash mismatch, invalid paths): no live install mutation occurs.
- **Commit fails mid-way**: rollback restores pre-transaction state using the inverse journal.
- **Process crash mid-commit**: run `dominium-setup rollback --journal <file>` to restore.

## Failure injection (tests)

The transaction engine supports deterministic failpoints for rollback testing:

- `DSU_FAILPOINT=after_stage_write`
- `DSU_FAILPOINT=after_verify`
- `DSU_FAILPOINT=mid_commit:<N>` (fail after `N` commit entries)
- `DSU_FAILPOINT=before_state_write`

Failpoints must not be enabled in production; they are test-only knobs.

## CLI Surface

- `dominium-setup export-invocation --manifest <file> --op <install|upgrade|repair|uninstall> --out <invocation> --deterministic 1`
- `dominium-setup plan --manifest <file> --invocation <invocation> --out <planfile> --format json --deterministic 1`
- `dominium-setup apply --plan <planfile> [--dry-run] --deterministic 1`
- `dominium-setup uninstall --state <file> [--dry-run] --deterministic 1`
- `dominium-setup rollback --journal <file> [--dry-run] --deterministic 1`

Exit codes follow `docs/setup/CLI_REFERENCE.md`.

## See also

- `docs/setup/JOURNAL_FORMAT.md`
- `docs/setup/INSTALLED_STATE_SCHEMA.md`
- `docs/setup/FORENSICS_AND_RECOVERY.md`
