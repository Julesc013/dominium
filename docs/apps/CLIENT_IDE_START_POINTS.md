Status: DERIVED
Last Reviewed: 2026-02-01
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: canon-aligned documentation set for convergence and release preparation

# Client IDE Start Points

These locations are intended as stable entry points for client-side game work
without touching engine/game.

- UI compositor: `runtime/ui/client/client_ui_compositor.h`,
  `runtime/ui/client/client_ui_compositor.c`
- Input bindings: `runtime/input/client/client_input_bindings.h`,
  `runtime/input/client/client_input_bindings.c`
- Read-only view model: `runtime/ui/client/observability/readonly_view_model.h`,
  `runtime/ui/client/observability/readonly_view_model.c`
- Entry point: `apps/client/main_client.c`
- Adapter boundary: `runtime/shell/lifecycle/include/dominium/app/readonly_adapter.h`
