# Dominium Setup Audit Log Format (`audit.dsu.log`)

The audit log is an append-only structured event stream for forensic traceability (what happened, in what order, with what result). It is **not** authoritative for installed state; the installed-state file is the authority.

Canonical format: a DSU common file header wrapping a TLV payload. The TLV payload is deterministic (stable field ordering, stable key ordering in JSON export). In deterministic mode, timestamps are `0`.

## File Header (DSU common header)

All integer fields are little-endian.

| Offset | Size | Field | Notes |
|---:|---:|---|---|
| 0 | 4 | `magic` | ASCII `DSUL` |
| 4 | 2 | `version` | `2` for this schema |
| 6 | 2 | `endian_marker` | `0xFFFE` (little-endian marker) |
| 8 | 4 | `header_size` | bytes (currently `20`) |
| 12 | 4 | `payload_size` | bytes (TLV payload length) |
| 16 | 4 | `header_checksum` | sum of bytes 0..15 (checksum bytes excluded) |
| 20 | … | `payload` | TLV stream |

## File location (default)

- `audit.dsu.log` in the current working directory (CLI default; override with `--log`)

## CLI commands (exact)

- Export to JSON:
  - `dominium-setup export-log --log audit.dsu.log --out audit.json --format json --deterministic 1`
- Export to deterministic TSV:
  - `dominium-setup export-log --log audit.dsu.log --out audit.tsv --format txt --deterministic 1`

Exit codes follow `docs/setup/CLI_REFERENCE.md`.

## TLV Encoding Rules (locked)

- `type`: `u16`
- `length`: `u32` (payload length only)
- `payload`: `length` raw bytes
- TLVs may nest: container TLVs store a sub‑TLV stream as their payload.
- Unknown TLVs are skipped (forward‑compat).
- Known TLVs with unsupported `*_VERSION` values are rejected deterministically with `DSU_STATUS_UNSUPPORTED_VERSION`.

Strings:
- Stored as raw bytes (no NUL terminator); readers reject embedded `NUL`.
- `MESSAGE` is UTF‑8.
- `PATH` is a canonical DSU path (`/` separators).

## Schema Overview

The TLV payload contains one `LOG_ROOT` container with `EVENT` entries.

### TLV Type IDs

**Root**
- `0x0001` `LOG_ROOT` (container)
- `0x0002` `ROOT_VERSION` (u32) — must be `2`

**Event**
- `0x0010` `EVENT` (container, repeatable)
  - `0x0011` `EVENT_VERSION` (u32) — must be `1`
  - `0x0012` `EVENT_SEQ` (u32) — monotonic per file
  - `0x0013` `EVENT_ID` (u32) — stable constant (see `source/dominium/setup/core/src/log/dsu_events.h`)
  - `0x0014` `SEVERITY` (u8)
  - `0x0015` `CATEGORY` (u8)
  - `0x0016` `PHASE` (u8)
  - `0x0017` `TIMESTAMP` (u32) — `0` in deterministic mode

**Event payload fields (optional)**
- `0x0100` `MESSAGE` (string, UTF‑8)
- `0x0101` `PATH` (string, canonical DSU path)
- `0x0102` `COMPONENT_ID` (string, ID)
- `0x0103` `STATUS_CODE` (u32)
- `0x0104` `DIGEST64_A` (u64)
- `0x0105` `DIGEST64_B` (u64)
- `0x0106` `DIGEST64_C` (u64)

## Phases

The `PHASE` field is an enum:

- `0` stage
- `1` verify
- `2` commit
- `3` rollback
- `4` state
- `5` cli

## Determinism

- Events are serialized in `EVENT_SEQ` order.
- In deterministic mode, `TIMESTAMP` is `0`.
- JSON export uses stable key ordering and prints `digests` as a fixed 3-element array of hex strings (`0x…`).

## JSON Export

Use `dsu_log_export_json` (or `dominium-setup report`, which exports reports) to produce machine-readable output.

The exported JSON shape is stable:

```json
{
  "format_version": 2,
  "event_count": 3,
  "events": [
    {
      "seq": 1,
      "event_id": 5388,
      "severity": 1,
      "category": 2,
      "phase": 4,
      "timestamp": 0,
      "message": "state written",
      "path": ".dsu/installed_state.dsustate",
      "component_id": "",
      "status_code": 0,
      "digests": ["0x0123...","0x0000...","0x0000..."]
    }
  ]
}
```

## See also

- `docs/setup/FORENSICS_AND_RECOVERY.md`
- `docs/setup/CLI_JSON_SCHEMAS.md`
