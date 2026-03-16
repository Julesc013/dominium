Status: DERIVED
Last Reviewed: 2026-03-13
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: release-pinned install discovery and virtual root contract

# Virtual Paths Baseline

Fingerprint: `035898f504e80489de4423dbaea083b9c12e414c549a9d359ed7914a77405193`

## Roots Table

| VROOT | Portable Default | Installed Pattern |
| --- | --- | --- |
| `VROOT_BIN` | `.` | `{bin_root}` |
| `VROOT_EXPORTS` | `exports` | `{store_root}/exports` |
| `VROOT_INSTALL` | `.` | `{install_root}` |
| `VROOT_INSTANCES` | `instances` | `{store_root}/instances` |
| `VROOT_IPC` | `runtime` | `{store_root}/runtime` |
| `VROOT_LOCKS` | `locks` | `{store_root}/locks` |
| `VROOT_LOGS` | `logs` | `{store_root}/logs` |
| `VROOT_PACKS` | `packs` | `{store_root}/packs` |
| `VROOT_PROFILES` | `profiles` | `{store_root}/profiles` |
| `VROOT_SAVES` | `saves` | `{store_root}/saves` |
| `VROOT_STORE` | `.` | `{store_root}` |

## Resolution Order

- 1. explicit CLI overrides: --root, --store-root, or per-vroot overrides
- 2. install discovery explicit CLI: --install-root or --install-id
- 3. install discovery portable mode: install.manifest.json adjacent to the product binary
- 4. install discovery environment override: DOMINIUM_INSTALL_ROOT or DOMINIUM_INSTALL_ID
- 5. install discovery installed registry mode: install_registry.json entry resolved by executable match or install_id
- 6. refusal: refusal.install.not_found when no governed install root can be discovered

## Repo Wrapper Projection

- result: `complete`
- resolution_source: `repo_wrapper_shim`

| Root | Repo-Normalized Path |
| --- | --- |
| `VROOT_BIN` | `<repo>/dist/bin` |
| `VROOT_EXPORTS` | `<repo>/exports` |
| `VROOT_INSTALL` | `<repo>/dist` |
| `VROOT_INSTANCES` | `<repo>/instances` |
| `VROOT_IPC` | `<repo>/dist/runtime` |
| `VROOT_LOCKS` | `<repo>/locks` |
| `VROOT_LOGS` | `<repo>/build/appshell/logs` |
| `VROOT_PACKS` | `<repo>/packs` |
| `VROOT_PROFILES` | `<repo>/profiles` |
| `VROOT_SAVES` | `<repo>/saves` |
| `VROOT_STORE` | `<repo>/dist` |

## Integration Coverage

| Surface | File | Status | Markers |
| --- | --- | --- | --- |
| `bootstrap` | `src/appshell/bootstrap.py` | `integrated` | `3/3` |
| `command_engine` | `src/appshell/commands/command_engine.py` | `integrated` | `4/4` |
| `config_loader` | `src/appshell/config_loader.py` | `integrated` | `2/2` |
| `diag_snapshot` | `src/appshell/diag/diag_snapshot.py` | `integrated` | `3/3` |
| `ipc_transport` | `src/appshell/ipc/ipc_transport.py` | `integrated` | `3/3` |
| `log_sink` | `src/appshell/logging/log_engine.py` | `integrated` | `3/3` |
| `pack_verifier` | `src/appshell/pack_verifier_adapter.py` | `integrated` | `3/3` |
| `supervisor` | `src/appshell/supervisor/supervisor_engine.py` | `integrated` | `5/5` |
| `diag_bundle_writer` | `src/diag/repro_bundle_builder.py` | `integrated` | `3/3` |
| `export_engine` | `src/lib/export/export_engine.py` | `integrated` | `3/3` |
| `import_engine` | `src/lib/import/import_engine.py` | `integrated` | `4/4` |
| `install_validator` | `src/lib/install/install_validator.py` | `integrated` | `3/3` |
| `save_validator` | `src/lib/save/save_validator.py` | `integrated` | `3/3` |
| `ui_model` | `src/ui/ui_model.py` | `integrated` | `4/4` |
| `launcher_runtime` | `tools/launcher/launch.py` | `integrated` | `3/3` |
| `launcher_cli` | `tools/launcher/launcher_cli.py` | `integrated` | `5/5` |
| `setup_cli` | `tools/setup/setup_cli.py` | `integrated` | `4/4` |

## Remaining Hardcoded Path Coverage

- remaining hardcoded hits: `0`
- shim hits: `30`
- allowed packaging-layout hits: `8`
- OS separator hits: `0`

| Classification | File | Line |
| --- | --- | --- |
| `allowed_packaging_layout` | `tools/setup/setup_cli.py` | `270` |
| `allowed_packaging_layout` | `tools/setup/setup_cli.py` | `287` |
| `allowed_packaging_layout` | `tools/setup/setup_cli.py` | `288` |
| `allowed_packaging_layout` | `tools/setup/setup_cli.py` | `315` |
| `allowed_packaging_layout` | `tools/setup/setup_cli.py` | `316` |
| `allowed_packaging_layout` | `tools/setup/setup_cli.py` | `317` |
| `allowed_packaging_layout` | `tools/setup/setup_cli.py` | `318` |
| `allowed_packaging_layout` | `tools/setup/setup_cli.py` | `1197` |
| `shim` | `src/appshell/commands/command_engine.py` | `371` |
| `shim` | `src/appshell/commands/command_engine.py` | `376` |
| `shim` | `src/appshell/commands/command_engine.py` | `419` |
| `shim` | `src/appshell/commands/command_engine.py` | `420` |
| `shim` | `src/appshell/config_loader.py` | `47` |
| `shim` | `src/appshell/config_loader.py` | `48` |
| `shim` | `src/appshell/config_loader.py` | `82` |
| `shim` | `src/appshell/diag/diag_snapshot.py` | `104` |
| `shim` | `src/appshell/ipc/ipc_transport.py` | `79` |
| `shim` | `src/appshell/ipc/ipc_transport.py` | `170` |
| `shim` | `src/appshell/pack_verifier_adapter.py` | `30` |
| `shim` | `src/appshell/supervisor/supervisor_engine.py` | `178` |
| `shim` | `src/appshell/supervisor/supervisor_engine.py` | `179` |
| `shim` | `src/appshell/supervisor/supervisor_engine.py` | `180` |
| `shim` | `src/appshell/supervisor/supervisor_engine.py` | `181` |
| `shim` | `src/appshell/supervisor/supervisor_engine.py` | `182` |

## Integration Coverage Report

- Path resolution is centralized in `src/appshell/paths/virtual_paths.py` after install discovery is resolved by `src/lib/install/install_discovery_engine.py`.
- AppShell now refuses launches that do not resolve a governed install root with `refusal.install.not_found`.
- Remaining path literals are limited to explicit shims and packaging-layout builders, not authoritative runtime root discovery.
