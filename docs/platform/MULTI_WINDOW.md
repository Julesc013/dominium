Status: DERIVED
Last Reviewed: 2026-02-01
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: patched document aligned to current canon ownership and release scope

# Multi-Window Foundations

## Patch Notes

- Current status: partially aligned to the Constitutional Architecture and release-freeze documentation set.
- Required updates: documentation surface exists, but current canon ownership is not explicit
- Cross-check with: `docs/audit/CANON_MAP.md` and `docs/audit/DOC_DRIFT_MATRIX.md`.


## Window identity
- `dsys_window` is an opaque, stable handle.
- `dsys_window_get_id` returns a numeric id assigned at creation time.

## Event routing
- Every window-related event includes `dsys_event.window` and
  `dsys_event.window_id`.
- Non-window events set `window=NULL` and `window_id=0`.
- Applications filter the global event queue by window handle/id.

## Creation and lifetime
- `dsys_window_create` may be called multiple times per process.
- `dsys_window_destroy` removes the window from routing; ids are not reused.

## Renderer binding
- `d_gfx_bind_surface(native_window, w, h)` binds the active renderer instance
  to a native window.
- Soft renderer presents via `d_system_present_framebuffer(native_window, ...)`.
- Multi-window rendering is achieved by rebinding or using multiple renderer
  instances (future work).
