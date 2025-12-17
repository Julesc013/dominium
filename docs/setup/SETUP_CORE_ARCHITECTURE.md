# Setup Core Architecture (Plan S-1)

This document describes the **Setup Core** control-plane foundation added in Plan S-1.
It is a deterministic, OS-agnostic engine that produces and consumes install **plans**
and **audit logs**. Platform-specific installers/adapters should be thin shells.

## Module boundaries

Setup Core is organized as a set of small modules:

- `manifest/`: Load and validate an installation manifest (baseline text format for S-1).
- `resolve/`: Resolve requested components into a canonical resolved set (stub in S-1).
- `plan/`: Build an ordered execution plan; serialize/deserialize `.dsuplan`.
- `txn/`: Transaction/execution coordinator (S-1 implements `DRY_RUN` only).
- `fs/`: Filesystem abstraction (`stdio` adapter in S-1; no OS headers outside this boundary).
- `state/`: Installed-state load/save (stub in S-1).
- `log/`: Audit log event capture; serialize/deserialize `.dsulog`.
- `platform_iface/`: Future boundary for platform services (not used yet in S-1).
- `util/`: Deterministic helpers (hashing, stable sort, endian IO, safe ASCII parsing).

## C ABI overview

Public headers live under `source/dominium/setup/core/include/dsu/`:

- `dsu_types.h`: Fixed-width types + `dsu_status_t`.
- `dsu_config.h`: `dsu_config_t` flags (deterministic mode, IO limits).
- `dsu_callbacks.h`: Optional host callbacks (log/progress).
- `dsu_ctx.h`: `dsu_ctx_t` lifecycle and audit-log access.
- `dsu_manifest.h`: Manifest load + accessors.
- `dsu_resolve.h`: Resolve stub + accessors.
- `dsu_plan.h`: Plan build + accessors + `.dsuplan` read/write.
- `dsu_execute.h`: Execute a plan (S-1: `DRY_RUN` only).
- `dsu_state.h`: Installed state stubs (format TBD).
- `dsu_log.h`: Audit log capture + `.dsulog` read/write.

## Determinism guarantees (S-1)

- **Deterministic mode is enabled by default** via `DSU_CONFIG_FLAG_DETERMINISTIC`.
- In deterministic mode:
  - Audit log timestamps are forced to `0`.
  - Component ordering is canonical and stable (ASCII lowercase + bytewise lexicographic sort).
  - `.dsuplan` and `.dsulog` serialization is stable and independent of pointer order.
- Hashing:
  - Plan IDs use a deterministic non-cryptographic `hash32` (FNV-1a 32-bit).

## CLI usage

The minimal CLI target is `dominium-setup`:

- Version:
  - `dominium-setup version`
  - `dominium-setup version --json`
- Generate a plan + audit log (end-to-end):
  - `dominium-setup plan --manifest docs/setup/sample_manifest.dsumf --out out.dsuplan --log out.dsulog`
  - Add `--json` for machine-readable output.
- Dry-run a plan (reads `.dsuplan`, writes `.dsulog`):
  - `dominium-setup dry-run --plan out.dsuplan --log dry.dsulog`

## Baseline manifest format (S-1)

Plan S-1 uses a strict INI-like format (no external JSON dependency).

Required keys:

- `product_id` (normalized to lowercase ASCII id)
- `version` (ASCII printable token)
- `install_root` (ASCII printable token)
- `components` (bracket list of component ids)

Example: `docs/setup/sample_manifest.dsumf`

## Binary file formats (S-1)

Both `.dsuplan` and `.dsulog` start with the same **base header** (little-endian):

- `magic` (4 bytes)
- `format_version` (u16)
- `endian_marker` (u16) = `0xFFFE` (little-endian)
- `header_size` (u32) = `20` in S-1
- `payload_length` (u32)
- `header_checksum` (u32) = sum of base header bytes 0..15

### `.dsuplan` payload (v1)

Field order (little-endian):

- `flags` (u32)
- `plan_id_hash32` (u32)
- `product_id_len` (u32) + bytes
- `version_len` (u32) + bytes
- `install_root_len` (u32) + bytes
- `component_count` (u32)
- `step_count` (u32)
- components:
  - `id_len` (u32) + bytes (repeated)
- steps:
  - `kind` (u8)
  - `reserved` (u8)
  - `reserved` (u16)
  - `arg_len` (u32) + bytes (repeated)

### `.dsulog` payload (v1)

Field order (little-endian):

- `event_count` (u32)
- `flags` (u32)
- events:
  - `event_id` (u32)
  - `severity` (u8)
  - `category` (u8)
  - `reserved` (u16)
  - `timestamp` (u32) (0 in deterministic mode)
  - `message_len` (u32) + bytes (UTF-8; no embedded NUL)

