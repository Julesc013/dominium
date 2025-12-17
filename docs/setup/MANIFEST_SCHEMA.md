# Dominium Setup Manifest Schema (`*.dsumanifest`)

Canonical format: a versioned binary file header wrapping a TLV payload. The TLV payload is canonicalized (stable ordering + normalization) and is the input to manifest digests / plan IDs.

## File Header (DSU common header)

All integer fields are little-endian.

| Offset | Size | Field | Notes |
|---:|---:|---|---|
| 0 | 4 | `magic` | ASCII `DSUM` |
| 4 | 2 | `version` | `2` for TLV manifests |
| 6 | 2 | `endian_marker` | `0xFFFE` (little-endian marker) |
| 8 | 4 | `header_size` | bytes (currently `20`) |
| 12 | 4 | `payload_size` | bytes (TLV payload length) |
| 16 | 4 | `header_checksum` | sum of bytes 0..15 (checksum bytes excluded) |
| 20 | … | `payload` | TLV stream |

## TLV Encoding Rules (locked)

- `type`: `u16`
- `length`: `u32` (payload length only)
- `payload`: `length` raw bytes
- TLVs may nest: container TLVs store a sub‑TLV stream as their payload.
- Unknown TLVs are skipped (forward‑compat).
- Known TLVs with unsupported `*_VERSION` values are rejected deterministically with `DSU_STATUS_UNSUPPORTED_VERSION`.

Strings:
- Stored as raw bytes (no NUL terminator); readers reject embedded `NUL`.
- IDs must match `[a-z0-9._-]+` and are normalized to lowercase.

Paths:
- Stored with `/` separators in canonical form.
- Load canonicalization replaces `\\` with `/`.

## Platform Triple Grammar

Current strict grammar (extensible by adding tokens):

`<os>-<arch>`

Allowed `<os>`: `win32`, `win64`, `linux`, `macos`, `any`  
Allowed `<arch>`: `x86`, `x64`, `arm64`, `any`

Examples:
- `win32-x86`
- `win64-x64`
- `linux-x64`
- `linux-arm64`
- `macos-x64`
- `macos-arm64`

## Schema Overview

The TLV payload contains (at least) one top-level `MANIFEST_ROOT` container. Unknown top-level TLVs may appear and are skipped.

### TLV Type IDs

All IDs are stable.

**Root**
- `0x0001` `MANIFEST_ROOT` (container)
- `0x0002` `ROOT_VERSION` (u32) — must be `1`
- `0x0010` `PRODUCT_ID` (string, ID)
- `0x0011` `PRODUCT_VERSION` (string, semver‑ish)
- `0x0012` `BUILD_CHANNEL` (string) — `stable|beta|dev|nightly`
- `0x0020` `PLATFORM_TARGET` (string, platform triple) — repeatable

**Default Install Roots**
- `0x0030` `DEFAULT_INSTALL_ROOT` (container)
  - `0x0031` `INSTALL_ROOT_VERSION` (u32) — must be `1`
  - `0x0032` `INSTALL_SCOPE` (u8 enum)
  - `0x0033` `INSTALL_PLATFORM` (string, platform triple)
  - `0x0034` `INSTALL_PATH` (string, path)

**Components**
- `0x0040` `COMPONENT` (container)
  - `0x0041` `COMPONENT_VERSION` (u32) — must be `1`
  - `0x0042` `COMPONENT_ID` (string, ID)
  - `0x0043` `COMPONENT_VERSTR` (string, optional; empty/absent ⇒ inherits product version)
  - `0x0044` `COMPONENT_KIND` (u8 enum)
  - `0x0045` `COMPONENT_FLAGS` (u32 bitmask)
  - `0x0046` `DEPENDENCY` (container, repeatable)
    - `0x0047` `DEP_VERSION` (u32) — must be `1`
    - `0x0048` `DEP_COMPONENT_ID` (string, ID)
    - `0x0049` `DEP_CONSTRAINT_KIND` (u8 enum)
    - `0x004A` `DEP_CONSTRAINT_VERSION` (string, optional depending on kind)
  - `0x004B` `CONFLICT` (string, ID, repeatable)
  - `0x004C` `PAYLOAD` (container, repeatable)
    - `0x004D` `PAYLOAD_VERSION` (u32) — must be `1`
    - `0x004E` `PAYLOAD_KIND` (u8 enum)
    - `0x004F` `PAYLOAD_PATH` (string, path; optional for blobs)
    - `0x0050` `PAYLOAD_SHA256` (bytes[32])
    - `0x0051` `PAYLOAD_SIZE` (u64, optional)
  - `0x0052` `ACTION` (container, repeatable)
    - `0x0053` `ACTION_VERSION` (u32) — must be `1`
    - `0x0054` `ACTION_KIND` (u8 enum)
    - `0x0055` `ACTION_APP_ID` (string, ID)
    - `0x0056` `ACTION_DISPLAY_NAME` (string, UTF‑8)
    - `0x0057` `ACTION_EXEC_RELPATH` (string, path)
    - `0x0058` `ACTION_ARGUMENTS` (string, UTF‑8)
    - `0x0059` `ACTION_ICON_RELPATH` (string, path)
    - `0x005A` `ACTION_EXTENSION` (string)
    - `0x005B` `ACTION_PROTOCOL` (string)
    - `0x005C` `ACTION_MARKER_RELPATH` (string, path)
    - `0x005D` `ACTION_CAPABILITY_ID` (string, ID)
    - `0x005E` `ACTION_CAPABILITY_VALUE` (string, UTF‑8)
    - `0x005F` `ACTION_PUBLISHER` (string, UTF‑8)

**Uninstall Policy**
- `0x0060` `UNINSTALL_POLICY` (container, optional)
  - `0x0061` `POLICY_VERSION` (u32) — must be `1`
  - `0x0062` `POLICY_REMOVE_OWNED` (u8 bool)
  - `0x0063` `POLICY_PRESERVE_USER_DATA` (u8 bool)
  - `0x0064` `POLICY_PRESERVE_CACHE` (u8 bool)

## Enums

**Install scope (`INSTALL_SCOPE`)**
- `0` portable
- `1` user
- `2` system

**Component kind (`COMPONENT_KIND`)**
- `0` launcher
- `1` runtime
- `2` tools
- `3` pack
- `4` driver
- `5` other

**Component flags (`COMPONENT_FLAGS`)**
- `0x00000001` optional
- `0x00000002` default-selected
- `0x00000004` hidden

**Version constraint kind (`DEP_CONSTRAINT_KIND`)**
- `0` any (no `DEP_CONSTRAINT_VERSION`)
- `1` exact (requires `DEP_CONSTRAINT_VERSION`)
- `2` at_least (requires `DEP_CONSTRAINT_VERSION`)

**Payload kind (`PAYLOAD_KIND`)**
- `0` fileset
- `1` archive
- `2` blob

**Action kind (`ACTION_KIND`)**
- `0` `REGISTER_APP_ENTRY`
- `1` `REGISTER_FILE_ASSOC`
- `2` `REGISTER_URL_HANDLER`
- `3` `REGISTER_UNINSTALL_ENTRY`
- `4` `WRITE_FIRST_RUN_MARKER`
- `5` `DECLARE_CAPABILITY`

## Declarative Action Vocabulary (data-only)

Actions are pure data. They are validated during manifest load and executed later by platform adapters (not by Setup Core).

Required fields by kind:

- `REGISTER_APP_ENTRY`: `ACTION_APP_ID`, `ACTION_DISPLAY_NAME`, `ACTION_EXEC_RELPATH` (optional: `ACTION_ARGUMENTS`, `ACTION_ICON_RELPATH`)
- `REGISTER_FILE_ASSOC`: `ACTION_EXTENSION`, `ACTION_APP_ID`
- `REGISTER_URL_HANDLER`: `ACTION_PROTOCOL`, `ACTION_APP_ID`
- `REGISTER_UNINSTALL_ENTRY`: `ACTION_DISPLAY_NAME` (optional: `ACTION_PUBLISHER`)
- `WRITE_FIRST_RUN_MARKER`: `ACTION_MARKER_RELPATH`
- `DECLARE_CAPABILITY`: `ACTION_CAPABILITY_ID`, `ACTION_CAPABILITY_VALUE`

## Deterministic Canonicalization + Digests

Setup Core canonicalizes manifests on load:

- IDs lowercased
- payload paths slash-normalized (`\\` → `/`)
- stable ordering:
  - platform targets sorted
  - install roots sorted by `(platform, scope, path)`
  - components sorted by `component_id`
  - dependency/conflict/payload/action lists sorted by stable keys

Manifest digests are computed over the canonical TLV payload bytes (the `payload` section only; not the file header).

## Examples (component sketches)

Launcher component (conceptual):

```json
{
  "component_id": "launcher",
  "component_kind": "launcher",
  "dependencies": [{"id":"runtime","constraint":"any","version":""}],
  "actions": [{
    "kind": "REGISTER_APP_ENTRY",
    "app_id": "dominium.launcher",
    "display_name": "Dominium Launcher",
    "exec_relpath": "bin/dominium-launcher.exe"
  }]
}
```

