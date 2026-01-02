# Transaction Journal Format (`*.dsujournal`)

The transaction journal is a binary, append-only record of filesystem mutations and rollback metadata.
It is written by `apply`/`uninstall` and consumed by `rollback`.

## File locations (default)

- Journal file: `<install_root>.txn/<journal_id_hex>/.dsu_txn/journal/txn.dsujournal`
- Transaction root: `<install_root>.txn/<journal_id_hex>`

## Header (fixed 24 bytes)

All integer fields are little-endian.

| Offset | Size | Field | Notes |
|---:|---:|---|---|
| 0 | 4 | `magic` | ASCII `DSUJ` |
| 4 | 2 | `version` | `1` |
| 6 | 2 | `endian_marker` | `0xFFFE` |
| 8 | 8 | `journal_id` | u64 |
| 16 | 8 | `plan_digest` | u64 |

## Records

Records repeat to end-of-file. Each record is:

| Field | Size | Notes |
|---|---:|---|
| `type` | u16 | Entry type enum |
| `payload_len` | u32 | Payload bytes |
| `payload` | `payload_len` | TLV stream |

### Entry types (stable)

- `0x0000` `NOOP` (metadata/progress checkpoints)
- `0x0001` `CREATE_DIR`
- `0x0002` `REMOVE_DIR`
- `0x0003` `COPY_FILE`
- `0x0004` `MOVE_FILE`
- `0x0005` `DELETE_FILE`
- `0x0006` `WRITE_STATE`

### Entry payload TLVs

All entries start with:

- `0x0001` `ENTRY_VERSION` (u32) — must be `1`

Path/root fields:

- `0x0010` `TARGET_ROOT` (u8)
- `0x0011` `TARGET_PATH` (string, relative DSU path)
- `0x0012` `SOURCE_ROOT` (u8)
- `0x0013` `SOURCE_PATH` (string, relative DSU path)
- `0x0014` `ROLLBACK_ROOT` (u8)
- `0x0015` `ROLLBACK_PATH` (string, relative DSU path)
- `0x0020` `FLAGS` (u32)

Root indices are stable:

- `0` install root
- `1` transaction root

Metadata/progress fields (in `NOOP` entries):

- `0x0100` `META_INSTALL_ROOT` (string, absolute canonical)
- `0x0101` `META_TXN_ROOT` (string, absolute canonical)
- `0x0102` `META_STATE_PATH` (string, relative DSU path)
- `0x0103` `META_PROGRESS` (u32, repeatable; last value wins)

Checksum field (all entries):

- `0x00FF` `CHECKSUM64` (u64)

`CHECKSUM64` is computed over: `entry_type` + payload bytes **before** the checksum TLV.

## CLI commands (exact)

- Roll back using a journal:
  - `dominium-setup rollback --journal <path-to/txn.dsujournal> [--dry-run] --deterministic 1`

Exit codes follow `docs/setup/CLI_REFERENCE.md`.

## Invariants and prohibitions

- Journal files are append-only; writers never rewrite earlier records.
- `META_PROGRESS` is monotonic during commit; rollback clamps progress to `entry_count`.
- Paths inside entries are canonical relative paths; absolute paths are forbidden in entry payloads.

## See also

- `docs/setup/TRANSACTION_ENGINE.md`
- `docs/setup/FORENSICS_AND_RECOVERY.md`
- `docs/setup/AUDIT_LOG_FORMAT.md`
