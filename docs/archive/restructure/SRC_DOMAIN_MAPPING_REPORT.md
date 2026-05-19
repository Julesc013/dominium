Status: DERIVED
Last Reviewed: 2026-03-27
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: XI-5
Replacement Target: approved mapping lock for XI-5

# SRC Domain Mapping Report

## Domain Summary

- apps: `137`
- attic: `13`
- compat: `3`
- engine: `183`
- game: `2`
- lib: `18`
- platform: `17`
- tests: `83`
- tools: `338`
- ui: `1`

## Category Summary

- generated: `13`
- legacy: `20`
- platform: `17`
- runtime_critical: `230`
- runtime_support: `86`
- tests: `84`
- tools: `324`
- ui: `21`

## High-Confidence Sample

| File | Domain | Module | Confidence | Category |
| --- | --- | --- | --- | --- |
| `app/src/readonly_adapter.c` | `apps` | `apps.app` | `0.98` | `runtime_support` |
| `app/src/readonly_format.c` | `apps` | `apps.app` | `0.98` | `runtime_support` |
| `app/src/ui_event_log.c` | `apps` | `apps.app` | `0.98` | `runtime_support` |
| `app/src/ui_presentation.c` | `apps` | `apps.app` | `0.98` | `runtime_support` |
| `legacy/launcher_core_launcher/launcher/core/source/audit/launcher_audit.cpp` | `apps` | `apps.legacy.launcher_core_launcher.launcher.core.audit` | `0.98` | `runtime_critical` |
| `legacy/launcher_core_launcher/launcher/core/source/installed_state/launcher_installed_state.cpp` | `apps` | `apps.legacy.launcher_core_launcher.launcher.core.installed_state` | `0.98` | `runtime_critical` |
| `legacy/launcher_core_launcher/launcher/core/source/instance/launcher_instance.cpp` | `apps` | `apps.legacy.launcher_core_launcher.launcher.core.instance` | `0.98` | `runtime_critical` |
| `legacy/launcher_core_launcher/launcher/core/source/instance/launcher_instance_artifact_ops.cpp` | `apps` | `apps.legacy.launcher_core_launcher.launcher.core.instance` | `0.98` | `runtime_critical` |
| `legacy/launcher_core_launcher/launcher/core/source/instance/launcher_instance_config.cpp` | `apps` | `apps.legacy.launcher_core_launcher.launcher.core.instance` | `0.98` | `runtime_critical` |
| `legacy/launcher_core_launcher/launcher/core/source/instance/launcher_instance_known_good.cpp` | `apps` | `apps.legacy.launcher_core_launcher.launcher.core.instance` | `0.98` | `runtime_critical` |
| `legacy/launcher_core_launcher/launcher/core/source/instance/launcher_instance_launch_history.cpp` | `apps` | `apps.legacy.launcher_core_launcher.launcher.core.instance` | `0.98` | `runtime_critical` |
| `legacy/launcher_core_launcher/launcher/core/source/instance/launcher_instance_ops.cpp` | `apps` | `apps.legacy.launcher_core_launcher.launcher.core.instance` | `0.98` | `runtime_critical` |
| `legacy/launcher_core_launcher/launcher/core/source/instance/launcher_instance_payload_refs.cpp` | `apps` | `apps.legacy.launcher_core_launcher.launcher.core.instance` | `0.98` | `runtime_critical` |
| `legacy/launcher_core_launcher/launcher/core/source/instance/launcher_instance_tx.cpp` | `apps` | `apps.legacy.launcher_core_launcher.launcher.core.instance` | `0.98` | `runtime_critical` |
| `legacy/launcher_core_launcher/launcher/core/source/job/launcher_job.cpp` | `apps` | `apps.legacy.launcher_core_launcher.launcher.core.job` | `0.98` | `runtime_critical` |
| `legacy/launcher_core_launcher/launcher/core/source/launch/launcher_exit_status.cpp` | `apps` | `apps.legacy.launcher_core_launcher.launcher.core.launch` | `0.98` | `runtime_critical` |
| `legacy/launcher_core_launcher/launcher/core/source/launch/launcher_handshake.cpp` | `apps` | `apps.legacy.launcher_core_launcher.launcher.core.launch` | `0.98` | `runtime_critical` |
| `legacy/launcher_core_launcher/launcher/core/source/launch/launcher_launch_attempt.cpp` | `apps` | `apps.legacy.launcher_core_launcher.launcher.core.launch` | `0.98` | `runtime_critical` |
| `legacy/launcher_core_launcher/launcher/core/source/launch/launcher_prelaunch.cpp` | `apps` | `apps.legacy.launcher_core_launcher.launcher.core.launch` | `0.98` | `runtime_critical` |
| `legacy/launcher_core_launcher/launcher/core/source/launcher_core.cpp` | `apps` | `apps.legacy.launcher_core_launcher.launcher.core` | `0.98` | `runtime_critical` |

## Runtime-Critical Sample

- `src/embodiment` blocked_files=`537` domains=`engine`
- `src/field` blocked_files=`537` domains=`engine`
- `src/fields` blocked_files=`537` domains=`engine`
- `src/fluid` blocked_files=`537` domains=`engine`
- `src/interior` blocked_files=`537` domains=`engine`
- `src/physics` blocked_files=`537` domains=`engine`
- `src/pollution` blocked_files=`537` domains=`engine`
- `src/specs` blocked_files=`537` domains=`engine`
- `src/thermal` blocked_files=`537` domains=`engine`
- `src/archive` blocked_files=`537` domains=`engine`
- `src/astro` blocked_files=`537` domains=`engine`
- `src/chem` blocked_files=`537` domains=`engine`
- `src/control` blocked_files=`537` domains=`engine`
- `src/diag` blocked_files=`537` domains=`engine`
- `src/electric` blocked_files=`537` domains=`engine`
- `src/governance` blocked_files=`537` domains=`engine`
- `src/materials` blocked_files=`537` domains=`engine`
- `src/meta` blocked_files=`537` domains=`engine`
- `src/mobility` blocked_files=`537` domains=`engine`
- `src/models` blocked_files=`537` domains=`engine`

## Missing Inputs

- none

## Conflict Sample

- `src/appshell/config_loader.py` -> `apps, tools` question=`Which canonical domain best matches this file without inventing new structure prematurely?`
- `src/appshell/commands/command_engine.py` -> `tools, apps` question=`Which canonical domain best matches this file without inventing new structure prematurely?`
- `src/lib/instance/__init__.py` -> `lib, tools` question=`Which canonical domain best matches this file without inventing new structure prematurely?`
- `src/lib/save/__init__.py` -> `lib, tools` question=`Which canonical domain best matches this file without inventing new structure prematurely?`
- `src/geo/lens/lens_engine.py` -> `tools, engine` question=`Which canonical domain best matches this file without inventing new structure prematurely?`
- `src/geo/projection/projection_engine.py` -> `tools, engine` question=`Which canonical domain best matches this file without inventing new structure prematurely?`
- `legacy/source/CMakeLists.txt` -> `lib, compat, attic` question=`Is this compatibility glue or reusable library support?`
- `src/net/testing/__init__.py` -> `tests, engine` question=`Which canonical domain best matches this file without inventing new structure prematurely?`
- `src/geo/index/object_id_engine.py` -> `tools, engine` question=`Which canonical domain best matches this file without inventing new structure prematurely?`
- `src/compat/handshake/__init__.py` -> `tools, compat` question=`Which canonical domain best matches this file without inventing new structure prematurely?`
- `src/compat/negotiation/negotiation_engine.py` -> `tools, compat` question=`Which canonical domain best matches this file without inventing new structure prematurely?`
- `src/compat/descriptor/__init__.py` -> `compat, tools` question=`Which canonical domain best matches this file without inventing new structure prematurely?`
- `src/compat/negotiation/__init__.py` -> `compat, tools` question=`Which canonical domain best matches this file without inventing new structure prematurely?`
- `src/compat/shims/__init__.py` -> `compat, tools` question=`Which canonical domain best matches this file without inventing new structure prematurely?`
- `src/client/render/render_model_adapter.py` -> `apps` question=`Which canonical domain best matches this file without inventing new structure prematurely?`
- `legacy/source/provider/CMakeLists.txt` -> `lib` question=`Should this legacy path be normalized into an active product/domain root now or preserved for later manual migration?`
- `legacy/source/provider/provider_content_local_fs.c` -> `lib` question=`Should this legacy path be normalized into an active product/domain root now or preserved for later manual migration?`
- `legacy/source/provider/provider_content_null.c` -> `lib` question=`Should this legacy path be normalized into an active product/domain root now or preserved for later manual migration?`
- `legacy/source/provider/provider_keychain_null.c` -> `lib` question=`Should this legacy path be normalized into an active product/domain root now or preserved for later manual migration?`
- `legacy/source/provider/provider_net_null.c` -> `lib` question=`Should this legacy path be normalized into an active product/domain root now or preserved for later manual migration?`
