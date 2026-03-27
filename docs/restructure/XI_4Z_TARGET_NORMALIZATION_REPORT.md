Status: DERIVED
Last Reviewed: 2026-03-27
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: XI-5
Replacement Target: XI-5a bounded execution against v2 approved lock

# XI-4Z Target Normalization Report

## Outcome

- Selected option preserved: `C`
- Old approved-for-XI-5 count: `770`
- New approved-for-XI-5 count: `769`
- Approved-to-attic count: `23`
- Deferred count after normalization: `3`
- Rows where approved decision metadata differs from Option C candidate metadata: `78`
- Remaining ambiguous rows: `1`

## Normalization Rule

- XI-4z decision metadata remains authoritative for classification and approved domain/module.
- Option C target paths are bound exactly as the Xi-5a execution surface whenever they are unique, source-like-free, and unoccupied.
- Rows that still cannot execute mechanically are deferred rather than reinterpreted.

## Newly Deferred Rows

- `src/worldgen/__init__.py`

## Representative Decision/Target Mismatches

| File | Approved Domain | Approved Module | Candidate Domain | Candidate Module | Exact Target Path |
| --- | --- | --- | --- | --- | --- |
| `src/appshell/__init__.py` | `apps` | `apps.appshell` | `tools` | `tools.xstack.sessionx` | `appshell/__init__.py` |
| `src/appshell/bootstrap.py` | `apps` | `apps.appshell` | `tools` | `tools.worldgen_offline` | `appshell/bootstrap.py` |
| `src/appshell/command_registry.py` | `apps` | `apps.appshell` | `tools` | `tools.fluid` | `appshell/command_registry.py` |
| `src/appshell/commands/__init__.py` | `apps` | `apps.appshell.commands` | `tools` | `tools.xstack.sessionx` | `appshell/commands/__init__.py` |
| `src/appshell/commands/command_engine.py` | `apps` | `apps.appshell.commands` | `tools` | `tools.xstack.testx.tests` | `appshell/commands/command_engine.py` |
| `src/appshell/diag/diag_snapshot.py` | `apps` | `apps.appshell.diag` | `tools` | `tools.ci` | `appshell/diag/diag_snapshot.py` |
| `src/appshell/ipc/ipc_client.py` | `apps` | `apps.appshell.ipc` | `tools` | `tools.appshell` | `appshell/ipc/ipc_client.py` |
| `src/appshell/ipc/ipc_endpoint_server.py` | `apps` | `apps.appshell.ipc` | `tools` | `tools.appshell` | `appshell/ipc/ipc_endpoint_server.py` |
| `src/appshell/ipc/ipc_transport.py` | `apps` | `apps.appshell.ipc` | `tools` | `tools.ci` | `appshell/ipc/ipc_transport.py` |
| `src/appshell/logging/log_engine.py` | `apps` | `apps.appshell.logging` | `tools` | `tools.meta` | `appshell/logging/log_engine.py` |
| `src/appshell/paths/virtual_paths.py` | `apps` | `apps.appshell.paths` | `tools` | `tools.meta` | `appshell/paths/virtual_paths.py` |
| `src/appshell/product_bootstrap.py` | `apps` | `apps.appshell` | `tools` | `tools.fluid` | `appshell/product_bootstrap.py` |
| `src/appshell/supervisor/args_canonicalizer.py` | `apps` | `apps.appshell.supervisor` | `tools` | `tools.release` | `appshell/supervisor/args_canonicalizer.py` |
| `src/appshell/supervisor/supervisor_engine.py` | `apps` | `apps.appshell.supervisor` | `tools` | `tools.auditx` | `appshell/supervisor/supervisor_engine.py` |
| `src/appshell/tui/tui_engine.py` | `apps` | `apps.appshell.tui` | `tools` | `tools.fluid` | `appshell/tui/tui_engine.py` |
| `src/appshell/ui_mode_selector.py` | `apps` | `apps.appshell` | `tools` | `tools.fluid` | `appshell/ui_mode_selector.py` |
| `src/client/render/renderers/hw_renderer_gl.py` | `apps` | `apps.client.render.renderers` | `tools` | `tools.xstack.registry_compile` | `client/render/renderers/hw_renderer_gl.py` |
| `src/client/render/representation_resolver.py` | `apps` | `apps.client.render` | `tools` | `tools.xstack.registry_compile` | `client/render/representation_resolver.py` |
| `src/client/render/snapshot_capture.py` | `apps` | `apps.client.render` | `tools` | `tools.ci` | `client/render/snapshot_capture.py` |
| `src/compat/__init__.py` | `compat` | `compat.compat` | `tools` | `tools.xstack.sessionx` | `compat/__init__.py` |
| `src/compat/capability_negotiation.py` | `compat` | `compat.compat` | `tools` | `tools.compatx.core` | `compat/capability_negotiation.py` |
| `src/compat/data_format_loader.py` | `compat` | `compat.compat` | `tools` | `tools.data` | `compat/data_format_loader.py` |
| `src/compat/descriptor/descriptor_engine.py` | `compat` | `compat.compat.descriptor` | `tools` | `tools.fluid` | `compat/descriptor/descriptor_engine.py` |
| `src/compat/handshake/__init__.py` | `compat` | `compat.handshake` | `tools` | `tools.xstack.testx.tests` | `compat/handshake/__init__.py` |
| `src/compat/handshake/handshake_engine.py` | `compat` | `compat.handshake` | `tools` | `tools.process` | `compat/handshake/handshake_engine.py` |

## Remaining Ambiguities

- `src/worldgen/__init__.py` `occupied_target_path` `worldgen/__init__.py`
