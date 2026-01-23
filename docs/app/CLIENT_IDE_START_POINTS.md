# Client IDE Start Points

These locations are intended as stable entry points for client-side game work
without touching engine/game.

- UI compositor: `client/ui/client_ui_compositor.h`,
  `client/ui/client_ui_compositor.c`
- Input bindings: `client/input/client_input_bindings.h`,
  `client/input/client_input_bindings.c`
- Read-only view model: `client/observability/readonly_view_model.h`,
  `client/observability/readonly_view_model.c`
- Entry point: `client/app/main_client.c`
- Adapter boundary: `app/include/dominium/app/readonly_adapter.h`
