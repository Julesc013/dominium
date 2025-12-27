# Invocation Payload (dsu_invocation)

This document defines the canonical installer invocation payload consumed by Setup Core.
Every frontend (MSI, EXE, GUI, TUI, CLI, ZIP, macOS, Linux, legacy) must emit it.

## Format (locked)

Binary format is preferred and canonical:

- File magic: `DSUI`
- Format version: `1`
- Payload: TLV stream (u16 type, u32 length, payload bytes)

Deterministic JSON is allowed for import/export, but the TLV form is authoritative.
All frontends must be able to export/import the TLV form.

Recommended filename extension for TLV payloads: `.dsuinv`.

## TLV schema (v1)

Root container: `INVOCATION_ROOT`

Required fields:

- `ROOT_VERSION` (u32, value `1`)
- `OPERATION` (u8)
- `SCOPE` (u8)
- `PLATFORM_TRIPLE` (string, non-empty)
- `INSTALL_ROOT` (string, repeatable, at least one for install/upgrade)
- `POLICY_FLAGS` (u32 bitset)
- `UI_MODE` (string, informational)
- `FRONTEND_ID` (string, informational)

Optional fields:

- `SELECTED_COMPONENT` (string, repeatable)
- `EXCLUDED_COMPONENT` (string, repeatable)

### Enumerations

Operation:

- `0` install
- `1` upgrade
- `2` repair
- `3` uninstall

Scope:

- `0` portable
- `1` user
- `2` system

UI mode values:

- `gui`, `tui`, `cli`

### Policy flags (bitset)

- Bit 0: `offline`
- Bit 1: `deterministic`
- Bit 2: `allow_prerelease`
- Bit 3: `legacy_mode`
- Bit 4: `enable_shortcuts`
- Bit 5: `enable_file_assoc`
- Bit 6: `enable_url_handlers`

Unknown bits are rejected during validation.

## Canonicalization rules

Canonicalization is required before validation and digesting:

- Trim ASCII whitespace from string fields.
- Normalize list order:
  - `install_roots`, `selected_components`, `excluded_components` are sorted by
    ASCII lowercase + bytewise lexicographic order.
- Reject duplicate entries within a list.
- Reject overlap between `selected_components` and `excluded_components`.

`ui_mode` and `frontend_id` are informational and do not affect plan outcomes.

## Digest rules

`dsu_invocation_digest()` computes a deterministic FNV-1a digest over the canonical
payload fields that affect plan resolution:

Included in digest:

- `operation`, `scope`, `platform_triple`
- `install_roots`
- `selected_components`
- `excluded_components`
- `policy_flags`

Excluded from digest:

- `ui_mode`
- `frontend_id`

This allows MSI and EXE frontends (or GUI vs CLI) to produce identical digests when
their actual install choices are identical.

## Public ABI

Setup Core exposes:

- `dsu_invocation_load()`
- `dsu_invocation_validate()`
- `dsu_invocation_digest()`

See `source/dominium/setup/core/include/dsu/dsu_invocation.h` for exact signatures.

## JSON export (deterministic)

JSON keys are stable and lowercase. Lists are canonicalized as described above.

Example:

```
{
  "operation": "install",
  "scope": "user",
  "platform_triple": "win32-x86_64",
  "install_roots": ["C:/Users/Alice/AppData/Local/Dominium"],
  "selected_components": ["core", "launcher"],
  "excluded_components": [],
  "policy_flags": {
    "offline": false,
    "deterministic": true,
    "allow_prerelease": false,
    "legacy_mode": false,
    "enable_shortcuts": true,
    "enable_file_assoc": true,
    "enable_url_handlers": true
  },
  "ui_mode": "gui",
  "frontend_id": "msi"
}
```

## See also

- `docs/setup/INSTALLER_UX_CONTRACT.md`
- `docs/setup/SETUP_CORE_ARCHITECTURE.md`
