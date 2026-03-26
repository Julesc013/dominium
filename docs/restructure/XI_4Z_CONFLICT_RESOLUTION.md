Status: DERIVED
Last Reviewed: 2026-03-27
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: XI-5
Replacement Target: XI-5 bounded execution against approved mapping lock

# XI-4Z Conflict Resolution

## Resolved Conflict Table

| File | Category | Plausible Domains | Final Decision | Approved Domain | Rationale |
| --- | --- | --- | --- | --- | --- |
| `legacy/source/CMakeLists.txt` | `legacy` | `lib, compat, attic` | `approved_to_attic` | `attic` | Legacy provider/build surface approved for attic preservation. |
| `legacy/source/provider/CMakeLists.txt` | `legacy` | `lib` | `approved_to_attic` | `attic` | Legacy provider/build surface approved for attic preservation. |
| `legacy/source/provider/provider_content_local_fs.c` | `legacy` | `lib` | `approved_to_attic` | `attic` | Legacy provider/build surface approved for attic preservation. |
| `legacy/source/provider/provider_content_null.c` | `legacy` | `lib` | `approved_to_attic` | `attic` | Legacy provider/build surface approved for attic preservation. |
| `legacy/source/provider/provider_keychain_null.c` | `legacy` | `lib` | `approved_to_attic` | `attic` | Legacy provider/build surface approved for attic preservation. |
| `legacy/source/provider/provider_net_null.c` | `legacy` | `lib` | `approved_to_attic` | `attic` | Legacy provider/build surface approved for attic preservation. |
| `legacy/source/provider/provider_null.c` | `legacy` | `lib` | `approved_to_attic` | `attic` | Legacy provider/build surface approved for attic preservation. |
| `legacy/source/provider/provider_os_integration_null.c` | `legacy` | `lib` | `approved_to_attic` | `attic` | Legacy provider/build surface approved for attic preservation. |
| `legacy/source/provider/provider_registry.c` | `legacy` | `lib` | `approved_to_attic` | `attic` | Legacy provider/build surface approved for attic preservation. |
| `legacy/source/provider/provider_trust_null.c` | `legacy` | `lib` | `approved_to_attic` | `attic` | Legacy provider/build surface approved for attic preservation. |
| `libs/ui_backends/win32/src/ui_ir_parser_stub.c` | `platform` | `platform` | `approved_for_xi5` | `platform` | Win32 UI backend stubs are platform adapters and are approved under the platform domain. |
| `libs/ui_backends/win32/src/win32_accessibility_stub.c` | `platform` | `platform` | `approved_for_xi5` | `platform` | Win32 UI backend stubs are platform adapters and are approved under the platform domain. |
| `libs/ui_backends/win32/src/win32_control_factory_stub.c` | `platform` | `platform` | `approved_for_xi5` | `platform` | Win32 UI backend stubs are platform adapters and are approved under the platform domain. |
| `libs/ui_backends/win32/src/win32_layout_stub.c` | `platform` | `platform` | `approved_for_xi5` | `platform` | Win32 UI backend stubs are platform adapters and are approved under the platform domain. |
| `libs/ui_backends/win32/src/win32_shell_stub.c` | `platform` | `platform` | `approved_for_xi5` | `platform` | Win32 UI backend stubs are platform adapters and are approved under the platform domain. |
| `src/appshell/commands/command_engine.py` | `tools` | `tools, apps` | `approved_for_xi5` | `apps` | Appshell command routing belongs with application shell runtime rather than generic tools. |
| `src/appshell/config_loader.py` | `runtime_critical` | `apps, tools` | `approved_for_xi5` | `apps` | Appshell surfaces are approved with the application runtime shell baseline. |
| `src/appshell/diag/__init__.py` | `runtime_critical` | `apps` | `approved_for_xi5` | `apps` | Appshell surfaces are approved with the application runtime shell baseline. |
| `src/appshell/ipc/__init__.py` | `runtime_critical` | `apps` | `approved_for_xi5` | `apps` | Appshell surfaces are approved with the application runtime shell baseline. |
| `src/appshell/supervisor/__init__.py` | `runtime_critical` | `apps` | `approved_for_xi5` | `apps` | Appshell surfaces are approved with the application runtime shell baseline. |
| `src/client/interaction/__init__.py` | `tools` | `tools` | `deferred_to_xi5b` | `tools` | Low-signal tool-adjacent initializer deferred to keep XI-5a bounded and avoid unnecessary structural invention. |
| `src/client/render/__init__.py` | `ui` | `apps` | `approved_for_xi5` | `apps` | Client render surfaces remain product-facing app shell code under the approved layout. |
| `src/client/render/render_model_adapter.py` | `ui` | `apps` | `approved_for_xi5` | `apps` | Client render surfaces remain product-facing app shell code under the approved layout. |
| `src/client/render/renderers/__init__.py` | `ui` | `apps` | `approved_for_xi5` | `apps` | Client render surfaces remain product-facing app shell code under the approved layout. |
| `src/client/render/renderers/null_renderer.py` | `ui` | `apps` | `approved_for_xi5` | `apps` | Client render surfaces remain product-facing app shell code under the approved layout. |
| `src/client/render/renderers/software_renderer.py` | `ui` | `apps` | `approved_for_xi5` | `apps` | Client render surfaces remain product-facing app shell code under the approved layout. |
| `src/compat/descriptor/__init__.py` | `runtime_critical` | `compat, tools` | `approved_for_xi5` | `compat` | Negotiation, handshake, descriptor, and shim code belongs under compat. |
| `src/compat/handshake/__init__.py` | `tools` | `tools, compat` | `approved_for_xi5` | `compat` | Negotiation, handshake, descriptor, and shim code belongs under compat. |
| `src/compat/negotiation/__init__.py` | `runtime_critical` | `compat, tools` | `approved_for_xi5` | `compat` | Negotiation, handshake, descriptor, and shim code belongs under compat. |
| `src/compat/negotiation/negotiation_engine.py` | `tools` | `tools, compat` | `approved_for_xi5` | `compat` | Negotiation, handshake, descriptor, and shim code belongs under compat. |
| `src/compat/shims/__init__.py` | `runtime_critical` | `compat, tools` | `approved_for_xi5` | `compat` | Negotiation, handshake, descriptor, and shim code belongs under compat. |
| `src/geo/index/object_id_engine.py` | `tools` | `tools, engine` | `approved_for_xi5` | `engine` | Geo engine helpers are approved into the engine domain despite tool-skewed duplicate evidence. |
| `src/geo/lens/lens_engine.py` | `tools` | `tools, engine` | `approved_for_xi5` | `engine` | Geo engine helpers are approved into the engine domain despite tool-skewed duplicate evidence. |
| `src/geo/projection/projection_engine.py` | `tools` | `tools, engine` | `approved_for_xi5` | `engine` | Geo engine helpers are approved into the engine domain despite tool-skewed duplicate evidence. |
| `src/interaction/__init__.py` | `runtime_critical` | `apps` | `approved_for_xi5` | `apps` | Interaction surfaces are application runtime entry surfaces, not free-floating tools. |
| `src/interaction/mount/__init__.py` | `runtime_critical` | `apps` | `approved_for_xi5` | `apps` | Interaction surfaces are application runtime entry surfaces, not free-floating tools. |
| `src/lib/artifact/__init__.py` | `runtime_critical` | `lib` | `approved_for_xi5` | `lib` | Reusable runtime support code is approved under lib. |
| `src/lib/instance/__init__.py` | `runtime_critical` | `lib, tools` | `approved_for_xi5` | `lib` | Reusable runtime support code is approved under lib. |
| `src/lib/save/__init__.py` | `runtime_critical` | `lib, tools` | `approved_for_xi5` | `lib` | Reusable runtime support code is approved under lib. |
| `src/lib/store/__init__.py` | `tools` | `tools` | `deferred_to_xi5b` | `tools` | Low-signal tool-adjacent initializer deferred to keep XI-5a bounded and avoid unnecessary structural invention. |
| `src/modding/__init__.py` | `runtime_critical` | `game` | `approved_for_xi5` | `game` | Modding policy is approved with the game/content layer. |
| `src/net/testing/__init__.py` | `tests` | `tests, engine` | `approved_for_xi5` | `tests` | Testing-only network helpers should move with the tests domain. |
| `src/security/trust/__init__.py` | `runtime_critical` | `engine` | `approved_for_xi5` | `engine` | Trust verification remains an engine-level invariant surface. |
| `tools/ui_shared/src/dui/dui_caps.c` | `ui` | `tools` | `approved_for_xi5` | `ui` | Shared DUI code is reusable UI infrastructure and should move under the approved UI domain. |
| `tools/ui_shared/src/dui/dui_event_queue.c` | `ui` | `tools` | `approved_for_xi5` | `ui` | Shared DUI code is reusable UI infrastructure and should move under the approved UI domain. |
| `tools/ui_shared/src/dui/dui_event_queue.h` | `ui` | `tools` | `approved_for_xi5` | `ui` | Shared DUI code is reusable UI infrastructure and should move under the approved UI domain. |
| `tools/ui_shared/src/dui/dui_schema_parse.c` | `ui` | `tools` | `approved_for_xi5` | `ui` | Shared DUI code is reusable UI infrastructure and should move under the approved UI domain. |
| `tools/ui_shared/src/dui/dui_schema_parse.h` | `ui` | `tools` | `approved_for_xi5` | `ui` | Shared DUI code is reusable UI infrastructure and should move under the approved UI domain. |
