# Setup Core Architecture

This document describes the **Setup Core** control-plane foundation.
It is a deterministic, OS-agnostic engine that produces and consumes install **plans**,
installed-state snapshots, and **audit logs**. Platform-specific installers/adapters are thin shells.

## Module boundaries

Setup Core is organized as a set of small modules:

- `manifest/`: Load and validate a TLV manifest (`*.dsumanifest`).
- `resolve/`: Resolve requested components into a canonical resolved set.
- `plan/`: Build an ordered execution plan; serialize/deserialize `.dsuplan`.
- `txn/`: Journaled transaction engine + rollback (`*.dsujournal`).
- `fs/`: Filesystem abstraction (no OS headers outside this boundary).
- `state/`: Installed-state load/save (`installed_state.dsustate`).
- `log/`: Audit log event capture; serialize/deserialize `audit.dsu.log`.
- `report/`: Inventory, verify, touched-paths, and uninstall preview reports.
- `platform_iface/`: Platform intent encoding + adapter dispatch.
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
- `dsu_txn.h`: Apply/uninstall transactions + rollback.
- `dsu_state.h`: Installed state load/save + accessors.
- `dsu_report.h`: Reports and integrity summaries.
- `dsu_log.h`: Audit log capture + `.dsulog` read/write.
- `dsu_platform_iface.h`: Platform intent interface for adapters.

## Determinism guarantees

- **Deterministic mode is enabled by default** via `DSU_CONFIG_FLAG_DETERMINISTIC`.
- In deterministic mode:
  - Audit log timestamps are forced to `0`.
  - Component ordering is canonical and stable (ASCII lowercase + bytewise lexicographic sort).
  - `.dsuplan` and `audit.dsu.log` serialization is stable and independent of pointer order.
- Hashing:
  - Plan IDs include deterministic `hash32` + `hash64` digests over canonical plan content.

## Invariants and prohibitions

- Setup Core never performs network calls.
- Setup Core never writes outside the install roots and transaction root.
- Invalid inputs are rejected deterministically (see exit codes in `docs/setup/CLI_REFERENCE.md`).

## CLI usage

The minimal CLI target is `dominium-setup`:

- Version:
  - `dominium-setup version --format json --deterministic 1`
- Build a plan:
  - `dominium-setup plan --manifest <artifact_root>/setup/manifests/product.dsumanifest --op install --scope portable --components core --out out.dsuplan --format json --deterministic 1`
- Apply a plan:
  - `dominium-setup apply --plan out.dsuplan --deterministic 1`
- Verify integrity:
  - `dominium-setup verify --state <install_root>/.dsu/installed_state.dsustate --format json --deterministic 1`
- Roll back from a journal (dry-run):
  - `dominium-setup rollback --journal <path-to/txn.dsujournal> --dry-run --deterministic 1`

## Manifest format

Manifests are binary `*.dsumanifest` files (DSU header + TLV payload).
See `docs/setup/MANIFEST_SCHEMA.md` for the locked schema and validation rules.

## File formats (current)

- Plan files: `.dsuplan` (format v5) → `docs/setup/TRANSACTION_ENGINE.md`
- Installed state: `installed_state.dsustate` (format v2) → `docs/setup/INSTALLED_STATE_SCHEMA.md`
- Audit log: `audit.dsu.log` (format v2) → `docs/setup/AUDIT_LOG_FORMAT.md`
- Transaction journal: `txn.dsujournal` (format v1) → `docs/setup/JOURNAL_FORMAT.md`

## See also

- `docs/setup/MANIFEST_SCHEMA.md`
- `docs/setup/RESOLUTION_ENGINE.md`
- `docs/setup/TRANSACTION_ENGINE.md`
- `docs/setup/INSTALLED_STATE_SCHEMA.md`
- `docs/setup/AUDIT_LOG_FORMAT.md`
- `docs/setup/JOURNAL_FORMAT.md`
- `docs/setup/CLI_REFERENCE.md`
