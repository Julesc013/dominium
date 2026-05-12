Status: PROVISIONAL
Phase: CONVERGE-04
Machine-Readable Authority: `contracts/distribution/layout.contract.toml`
Stability: provisional

# Distribution Layout Canon

`contracts/distribution/layout.contract.toml` is the machine-readable authority for Dominium distribution, install, media, package export, bundle, cache, staging, symbols, provenance, and runtime projection layout during convergence.

This document explains that contract. It does not override the machine-readable contract, and it does not authorize physical repository moves.

## Source Layout Boundary

The source repository layout is governed by `contracts/repo/layout.contract.toml`. It is separate from:

- build and release output under `dist/`
- `.dompkg` package internal export layout
- compressed archive layout
- portable install layout
- installed desktop/server layout
- offline media layout
- package cache, staging, rollback, and transaction layout
- runtime IPC, lock, log, and temp layout
- save, instance, replay, diagnostic, and compound bundle layout

`dist/` is generated release/build output. It is not source repository authority.

## Unified Model

Dominium uses one projection model:

```text
logical roots
  -> physical projections
  -> package export map
  -> install/store/runtime binding
  -> deterministic verification
```

Logical roots describe ownership and mutability. Physical projections map those roots into portable archives, installed desktops, server installs, offline media, CI output, cache/staging areas, and bundles. Package manifests export files into logical roots, not absolute host paths. Install and runtime binding resolves those logical roots through AppShell and install manifests. Verification is deterministic and manifest-driven.

## Projection Summary

| Projection | Role |
| --- | --- |
| `source_repo` | Current repository tree governed by `contracts/repo/layout.contract.toml`; not an install or package layout. |
| `dist_output` | Generated CI/build/release output with separate `dist/pkg`, `dist/sys`, `dist/sym`, `dist/meta`, `dist/cfg`, `dist/redist`, and `dist/res` roles. |
| `compressed_archive` | Downloadable archive whose extraction produces a valid portable install. |
| `portable_install` | Self-describing runnable tree with manifests, binaries, store, instances, saves, exports, logs, runtime, cache, ops, docs, and licenses. |
| `installed_desktop` | Immutable install root plus mutable store/user roots outside the immutable tree. |
| `server_install` | Headless/system projection with immutable root, mutable store, logs, and runtime IPC/locks split by platform policy. |
| `media_layout` | Read-only offline media payload with packages, portable projections, bootstrap setup, docs, redist, optional symbols/source, and writable templates. |
| `package_export` | `.dompkg` exports files into declared logical roots and must not encode absolute host paths. |
| `bundle_export` | Save, instance, replay, diagnostic, and compound bundles; bundles are not installs. |
| `cache_and_staging` | Content-hash package cache, download partials, verification outputs, setup-owned staging, and ops transactions. |
| `symbols_and_provenance` | Separate symbol channel plus build provenance, checksums, signatures, manifests, debug packages, and source archives when applicable. |

## Split Lock Roots

CONVERGE-04 refines generic lock terminology into three logical roots:

- `STORE_LOCK_ROOT`: deterministic content, pack, capability, compatibility, and store-resolution locks.
- `RUNTIME_LOCK_ROOT`: process, IPC, launch coordination, and transient runtime locks.
- `OPS_TRANSACTION_ROOT`: setup, update, repair, uninstall, rollback, stage, commit, and rollback transaction records.

Existing `VROOT_LOCKS` language in AppShell docs remains compatibility input. New projection planning should use the split-lock vocabulary.

## No Physical Moves

CONVERGE-04 adds a contract, validator, and explanatory docs only. It does not move folders, populate `dist/`, generate package bytes, change executable names, alter product IDs, change install IDs, or change virtual-root resolution implementation.

## Future Phases

- CONVERGE-05: archive/attic/legacy/quarantine convergence.
- CONVERGE-06: contracts/schema/registry/compat convergence.
- CONVERGE-10: blocking validation only after controlled convergence.
- CONVERGE-12: broader stale-doc and cross-reference cleanup.
