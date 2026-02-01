Status: DERIVED
Last Reviewed: 2026-02-01
Supersedes: none
Superseded By: none

# Client Read-Only Integration

The client uses the app-layer read-only adapter for observability while keeping
engine/game APIs isolated.

## Modules
- Adapter API: `app/include/dominium/app/readonly_adapter.h`
- View model: `client/observability/readonly_view_model.h`,
  `client/observability/readonly_view_model.c`
- Input bindings: `client/input/client_input_bindings.h`,
  `client/input/client_input_bindings.c`
- UI overlay: `client/ui/client_ui_compositor.h`,
  `client/ui/client_ui_compositor.c`
- Entry point wiring: `client/app/main_client.c`

## CLI
- `--topology` outputs `packages_tree` summary in text or JSON.
- `--snapshot` and `--events` are explicit unsupported paths and return
  non-zero.

## UI
- TUI uses the view model to populate a list and metadata panel.
- GUI overlay uses view-model summary data; `H` toggles the overlay and
  `B` requests borderless mode (best-effort via the window mode extension).