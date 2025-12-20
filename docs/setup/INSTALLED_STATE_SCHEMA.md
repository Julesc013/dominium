# Dominium Setup Installed State Schema (`installed_state.dsustate`)

Installed-state is the single authoritative record of what is installed. It is written as the final step of a successful transaction commit and drives:

- component inventory (`list-installed`)
- touched paths reporting (`report`)
- integrity verification (`verify`)
- uninstall planning + execution (`uninstall-preview`, `uninstall`)

Canonical format: a DSU common file header wrapping a TLV payload. The TLV payload is deterministic (stable ordering + normalization) and is the input to state digests / forensics.

## File Header (DSU common header)

All integer fields are little-endian.

| Offset | Size | Field | Notes |
|---:|---:|---|---|
| 0 | 4 | `magic` | ASCII `DSUS` |
| 4 | 2 | `version` | `2` for this schema |
| 6 | 2 | `endian_marker` | `0xFFFE` (little-endian marker) |
| 8 | 4 | `header_size` | bytes (currently `20`) |
| 12 | 4 | `payload_size` | bytes (TLV payload length) |
| 16 | 4 | `header_checksum` | sum of bytes 0..15 (checksum bytes excluded) |
| 20 | … | `payload` | TLV stream |

## File location (default)

- `<install_root>/.dsu/installed_state.dsustate`

## CLI commands (exact)

- List installed components:
  - `dominium-setup list-installed --state <install_root>/.dsu/installed_state.dsustate --format json --deterministic 1`
- Verify integrity:
  - `dominium-setup verify --state <install_root>/.dsu/installed_state.dsustate --format json --deterministic 1`
- Report bundle:
  - `dominium-setup report --state <install_root>/.dsu/installed_state.dsustate --out <dir> --format json --deterministic 1`
- Uninstall preview:
  - `dominium-setup uninstall-preview --state <install_root>/.dsu/installed_state.dsustate --format json --deterministic 1`

Exit codes follow `docs/setup/CLI_REFERENCE.md` (verify uses `2` for integrity issues).

## TLV Encoding Rules (locked)

- `type`: `u16`
- `length`: `u32` (payload length only)
- `payload`: `length` raw bytes
- TLVs may nest: container TLVs store a sub‑TLV stream as their payload.
- Unknown TLVs are skipped (forward‑compat).
- Known TLVs with unsupported `*_VERSION` values are rejected deterministically with `DSU_STATUS_UNSUPPORTED_VERSION`.

Strings:
- Stored as raw bytes (no NUL terminator); readers reject embedded `NUL`.
- IDs are normalized to lowercase.

Paths:
- Stored with `/` separators in canonical form.
- Load canonicalization replaces `\\` with `/`.
- Install roots are absolute canonical paths.
- Component file `FILE_PATH` values are canonical **relative paths** under an install root.

## Schema Overview

The TLV payload contains (at least) one top-level `STATE_ROOT` container. Unknown top-level TLVs may appear and are skipped.

### TLV Type IDs

All IDs are stable.

**Root**
- `0x0001` `STATE_ROOT` (container)
- `0x0002` `ROOT_VERSION` (u32) — must be `2`
- `0x0010` `PRODUCT_ID` (string, ID)
- `0x0011` `PRODUCT_VERSION_INSTALLED` (string)
- `0x0012` `BUILD_CHANNEL` (string)
- `0x0013` `INSTALL_INSTANCE_ID` (u64)
- `0x0020` `PLATFORM_TRIPLE` (string)
- `0x0021` `INSTALL_SCOPE` (u8 enum; same values as the manifest install scope)
- `0x0022` `INSTALL_ROOT` (string) — compatibility alias for the primary install root
- `0x0023` `INSTALL_ROOT_ITEM` (container, repeatable)
  - `0x0024` `INSTALL_ROOT_VERSION` (u32) — must be `1`
  - `0x0025` `INSTALL_ROOT_ROLE` (u8 enum)
  - `0x0026` `INSTALL_ROOT_PATH` (string, absolute canonical path)
- `0x0030` `MANIFEST_DIGEST64` (u64)
- `0x0031` `RESOLVED_SET_DIGEST64` (u64)
- `0x0032` `PLAN_DIGEST64` (u64)
- `0x0060` `LAST_SUCCESSFUL_OPERATION` (u8 enum)
- `0x0061` `LAST_JOURNAL_ID` (u64)
- `0x0062` `LAST_AUDIT_LOG_DIGEST64` (u64, optional)

**Components**
- `0x0040` `COMPONENT` (container, repeatable)
  - `0x0041` `COMPONENT_VERSION` (u32) — must be `2`
  - `0x0042` `COMPONENT_ID` (string, ID)
  - `0x0043` `COMPONENT_VERSTR` (string)
  - `0x0044` `COMPONENT_KIND` (u8 enum; matches the manifest component kind)
  - `0x0045` `INSTALL_TIME_POLICY` (u64) — `0` in deterministic mode
  - `0x0046` `REGISTRATION` (string, repeatable; may be empty until S-6)
  - `0x0047` `MARKER` (string, repeatable; first-run markers, etc.)

**Installed files (per component)**
- `0x0050` `FILE` (container, repeatable)
  - `0x0051` `FILE_VERSION` (u32) — must be `2`
  - `0x0056` `ROOT_INDEX` (u32) — index into the install root array
  - `0x0052` `PATH` (string, relative canonical path)
  - `0x0055` `DIGEST64` (u64) — fast digest for comparisons (derived from SHA-256)
  - `0x0054` `SIZE` (u64)
  - `0x0057` `OWNERSHIP` (u8 enum)
  - `0x0058` `FLAGS` (u32 bitmask)
  - `0x0053` `SHA256` (bytes[32])

## Enums

**Install root role (`INSTALL_ROOT_ROLE`)**
- `0` primary
- `1` state
- `2` cache
- `3` user_data

**File ownership (`OWNERSHIP`)**
- `0` owned
- `1` user_data
- `2` cache

**Last successful operation (`LAST_SUCCESSFUL_OPERATION`)**
- `0` install
- `1` upgrade
- `2` repair
- `3` uninstall

**File flags (`FLAGS`)**
- `0x00000001` created_by_install
- `0x00000002` modified_after_install (reserved for later; may be unset)

## Deterministic Canonicalization

Setup Core canonicalizes the state on save:

- install roots sorted by `(role, path)`
- components sorted lexicographically by `component_id`
- per-component files sorted by `(root_index, path)`
- string paths slash-normalized (`\\` → `/`)

In deterministic mode:

- no timestamps are embedded in the state file
- `INSTALL_TIME_POLICY` is `0`
- `INSTALL_INSTANCE_ID` uses a seeded nonce for stable tests; set `DSU_TEST_SEED=<u64>` to override in CI

## Upgrade / Forward Compatibility Rules

- Readers must skip unknown TLVs (by length) at any nesting level.
- Writers may add new TLVs; existing TLV IDs are stable.
- A higher file `version` or `*_VERSION` value may be rejected if it blocks safety; otherwise prefer skip-unknown and continue.

## Safety Rules (enforced on load/validate)

- State must never reference paths outside its declared install roots.
- All component file paths are validated as canonical relative paths (no `..`, no absolute injections).
- Verification/uninstall must not follow symlinks out of root.

## See also

- `docs/setup/FORENSICS_AND_RECOVERY.md`
- `docs/setup/TRANSACTION_ENGINE.md`
