Status: DERIVED
Last Reviewed: 2026-02-01
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: canon-aligned documentation set for convergence and release preparation

# Client Read-Only Integration

The client uses the app-layer read-only adapter for observability while keeping
engine/game APIs isolated.

## Modules
- Adapter API: `runtime/shell/lifecycle/include/dominium/app/readonly_adapter.h`
- View model: `apps/client/observability/readonly_view_model.h`,
  `apps/client/observability/readonly_view_model.c`
- Input bindings: `runtime/input/client/client_input_bindings.h`,
  `runtime/input/client/client_input_bindings.c`
- UI overlay: `runtime/ui/client/client_ui_compositor.h`,
  `runtime/ui/client/client_ui_compositor.c`
- Entry point wiring: `apps/client/main_client.c`

## CLI
- `--topology` outputs `packages_tree` summary in text or JSON.
- `--snapshot` and `--events` are explicit unsupported paths and return
  non-zero.

## UI
- TUI uses the view model to populate a list and metadata panel.
- GUI overlay uses view-model summary data; `H` toggles the overlay and
  `B` requests borderless mode (best-effort via the window mode extension).
