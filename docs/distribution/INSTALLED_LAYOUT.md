Status: PROVISIONAL
Phase: CONVERGE-04
Machine-Readable Authority: `contracts/distribution/layout.contract.toml`

# Installed Layout

Installed projections separate immutable install roots from mutable store, user, runtime, log, cache, and ops roots. Multiple installs, versions, and forks may coexist on the same host.

Shared stores are reusable by hash and contract identity. They are not selected by a singleton install path assumption.

## Desktop Projection

| Platform family | Immutable root examples | Mutable root examples |
| --- | --- | --- |
| Windows | `Program Files/Dominium` | `ProgramData/Dominium`, `LocalAppData/Dominium` |
| macOS | `.app` bundle, `/Applications/Dominium.app` | `Library/Application Support/Dominium` |
| Linux | `/opt/dominium`, distro package roots | XDG data roots, `/var/lib/dominium` for system installs |

The immutable root carries binaries, descriptors, docs, licenses, release manifests, and redistributables. Mutable roots carry stores, instances, saves, exports, logs, runtime IPC/locks/temp, cache, and ops transactions.

## Server/System Projection

Example server layout families:

```text
/opt/dominium/          immutable install root
/var/lib/dominium/      mutable store, instances, saves, exports
/var/log/dominium/      logs
/run/dominium/          runtime IPC, runtime locks, temp coordination
```

Headless operation must not require GUI roots. Server installs still use manifests, semantic contract registries, pack locks, and explicit refusal semantics.

## AppShell Resolution

AppShell virtual roots resolve physical locations for installed and portable modes. CONVERGE-04 does not change virtual-root resolution implementation.

The split-lock model refines physical targets:

- deterministic store locks resolve under `STORE_LOCK_ROOT`
- process and IPC locks resolve under `RUNTIME_LOCK_ROOT`
- setup/update/rollback records resolve under `OPS_TRANSACTION_ROOT`

## Rollback And Ops

Rollback and operations state belongs under `ops/transactions/` or its installed projection. Rollback is lockfile/projection based and must restore previous layout digest exactly. It is not ad hoc directory copying.
