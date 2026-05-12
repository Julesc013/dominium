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

- UI compositor: `apps/client/ui/client_ui_compositor.h`,
  `apps/client/ui/client_ui_compositor.c`
- Input bindings: `apps/client/input/client_input_bindings.h`,
  `apps/client/input/client_input_bindings.c`
- Read-only view model: `apps/client/observability/readonly_view_model.h`,
  `apps/client/observability/readonly_view_model.c`
- Entry point: `apps/client/app/main_client.c`
- Adapter boundary: `runtime/app/include/dominium/app/readonly_adapter.h`
