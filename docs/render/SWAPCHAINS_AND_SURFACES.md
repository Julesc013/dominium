# Swapchains and Surfaces

## Surface binding
- `d_gfx_bind_surface(native_window, w, h)` binds the active renderer instance
  to a platform native window handle.
- `d_gfx_resize(w, h)` updates the bound surface/backbuffer size.

## Soft backend
- Uses a CPU framebuffer sized by `d_gfx_bind_surface`.
- Presents via `d_system_present_framebuffer(native_window, pixels, w, h, pitch)`.
- If the window is minimized/occluded, presentation is a no-op.

## Null backend
- Ignores surface binding and presentation.
- Intended for headless/server/test paths.

## GPU backends
- GPU backends are not implemented in APR2.
- When implemented, they will own swapchain/surface resources per native window.
