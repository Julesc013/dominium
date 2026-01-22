# Client UI Layer

The client GUI is renderer-driven and sits entirely in the application layer.
It does not use OS-native widget toolkits.

## Current implementation
- UI compositor: `client/ui/client_ui_compositor.c`
- Input flow: platform events are polled via `dsys_poll_event()` and forwarded
  to the compositor (no platform callbacks into game logic).
- Rendering: the compositor emits `d_gfx_*` commands and draws a procedural
  debug overlay. `H` toggles the overlay visibility.

## Assets and packs
No assets or packs are required for GUI startup. The overlay is procedural
text only.
