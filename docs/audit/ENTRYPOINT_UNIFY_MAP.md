Status: DERIVED
Last Reviewed: 2026-03-13
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: canon-aligned documentation set for convergence and release preparation

# Entrypoint Unify Map

Status source: `tools/release/entrypoint_unify_common.py`

| Product | Executables | Source | Main Implementation | Boot Flow | UI Init | Pack Gate | IPC Start | Steps | Compliance |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `client` | `client`, `dominium_client` | `tools/mvp/runtime_entry.py` | `return appshell_main(` | `AppShell -> bootstrap context -> appshell_product_bootstrap` | `AppShell mode handoff -> tools/mvp/runtime_entry.py::_legacy_main` | `tools/mvp/runtime_bundle.py::build_runtime_bootstrap` | `src/appshell/bootstrap.py::AppShellIPCEndpointServer` | `mode_select -> descriptor_emit -> negotiation_preflight -> artifact_validate -> session_start -> local_server_attach` | `compliant` |
| `engine` | `engine` | `tools/appshell/product_stub_cli.py` | `return appshell_main(` | `AppShell -> stub dispatch` | `AppShell stub mode only` | `none` | `src/appshell/bootstrap.py::AppShellIPCEndpointServer` | `mode_select -> descriptor_emit -> negotiation_preflight -> stub_dispatch` | `compliant` |
| `game` | `game` | `tools/appshell/product_stub_cli.py` | `return appshell_main(` | `AppShell -> stub dispatch` | `AppShell stub mode only` | `none` | `src/appshell/bootstrap.py::AppShellIPCEndpointServer` | `mode_select -> descriptor_emit -> negotiation_preflight -> stub_dispatch` | `compliant` |
| `launcher` | `launcher` | `tools/launcher/launch.py` | `return appshell_main(` | `AppShell -> bootstrap context -> appshell_product_bootstrap` | `AppShell mode handoff -> tools/launcher/launch.py::_legacy_main` | `src.appshell.pack_verifier_adapter.verify_pack_root` | `src/appshell/bootstrap.py::AppShellIPCEndpointServer` | `mode_select -> descriptor_emit -> negotiation_preflight -> session_spec_validate -> pack_validate -> session_start` | `compliant` |
| `server` | `server`, `dominium_server` | `src/server/server_main.py` | `return appshell_main(` | `AppShell -> bootstrap context -> appshell_product_bootstrap` | `AppShell mode handoff -> src/server/server_main.py::_legacy_main` | `src/server/server_boot.py::boot_server_runtime` | `src/appshell/bootstrap.py::AppShellIPCEndpointServer; src/server/net/loopback_transport.py` | `mode_select -> descriptor_emit -> negotiation_preflight -> contract_validate -> pack_validate -> session_start -> loopback_listen` | `compliant` |
| `setup` | `setup` | `tools/setup/setup_cli.py` | `return appshell_main(` | `AppShell -> bootstrap context -> appshell_product_bootstrap` | `AppShell mode handoff -> tools/setup/setup_cli.py::_legacy_main` | `src.appshell.pack_verifier_adapter.verify_pack_root` | `src/appshell/bootstrap.py::AppShellIPCEndpointServer` | `mode_select -> descriptor_emit -> negotiation_preflight -> pack_validate` | `compliant` |
| `tool.attach_console_stub` | `tool_attach_console_stub` | `tools/appshell/product_stub_cli.py` | `return appshell_main(` | `AppShell -> stub dispatch` | `AppShell stub mode only` | `none` | `src/appshell/bootstrap.py::AppShellIPCEndpointServer` | `mode_select -> descriptor_emit -> negotiation_preflight -> stub_dispatch` | `compliant` |

## Compliance Summary

- All governed product entrypoints are unified under AppShell bootstrap.
