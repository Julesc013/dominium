Status: CANONICAL
Last Reviewed: 2026-03-13
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: APPSHELL/LIB
Replacement Target: release-pinned install discovery and virtual root contract

# Virtual Paths

AppShell owns deterministic logical-root resolution for packs, profiles, instances, saves, exports, logs, and IPC metadata.

## Logical Roots

| VROOT | Portable Default | Installed Pattern | Purpose |
| --- | --- | --- | --- |
| `VROOT_BIN` | `.` | `{bin_root}` | Primary executable directory for the current product surface. |
| `VROOT_EXPORTS` | `exports` | `{store_root}/exports` | Export and diagnostic bundle output root. |
| `VROOT_INSTALL` | `.` | `{install_root}` | Install root containing install.manifest.json and product binaries or their bin directory. |
| `VROOT_INSTANCES` | `instances` | `{store_root}/instances` | Linked and portable instance manifests and runtime instance roots. |
| `VROOT_IPC` | `runtime` | `{store_root}/runtime` | IPC endpoint discovery and transport metadata directory. |
| `VROOT_LOCKS` | `locks` | `{store_root}/locks` | Pack locks and other deterministic lock artifacts. |
| `VROOT_LOGS` | `logs` | `{store_root}/logs` | Structured log sink root for AppShell and wrapper products. |
| `VROOT_PACKS` | `packs` | `{store_root}/packs` | Pack manifest and content root. |
| `VROOT_PROFILES` | `profiles` | `{store_root}/profiles` | Profile bundle and profile manifest root. |
| `VROOT_SAVES` | `saves` | `{store_root}/saves` | Save manifests and save payload roots. |
| `VROOT_STORE` | `.` | `{store_root}` | Primary store root for runtime packs, profiles, instances, saves, and exports. |

## Resolution Order

1. explicit CLI overrides: --root, --store-root, or per-vroot overrides
2. install discovery explicit CLI: --install-root or --install-id
3. install discovery portable mode: install.manifest.json adjacent to the product binary
4. install discovery environment override: DOMINIUM_INSTALL_ROOT or DOMINIUM_INSTALL_ID
5. install discovery installed registry mode: install_registry.json entry resolved by executable match or install_id
6. refusal: refusal.install.not_found when no governed install root can be discovered

## API

- `vpath_init(context)` resolves and fingerprints the active root map.
- `vpath_resolve(vroot_id, relative_path)` normalizes separators and joins under the resolved root.
- `vpath_exists`, `vpath_list`, `vpath_open_read`, and `vpath_open_write` operate only through resolved virtual roots.

## Refusal And Logging

- AppShell refuses launch with `refusal.install.not_found` when no governed install root can be resolved.
- Successful initialization emits `appshell.paths.initialized` before pack validation, negotiation, or UI startup.
- Repo-wrapper runs remain available through the explicit `repo_wrapper_shim` resolution source and are logged as a warning-bearing development shim outside the authoritative install discovery order.
