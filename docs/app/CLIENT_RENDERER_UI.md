Status: DERIVED
Last Reviewed: 2026-02-01
Supersedes: none
Superseded By: none

# Client Renderer UI

Client GUI rendering is backend-agnostic:

- UI draw calls are issued through `d_gfx_cmd_buffer` and friends.
- Backends (software or GPU) share the same UI path; no backend-specific UI
  assets are required.
- The null renderer remains headless and bypasses GUI entirely.

Renderer selection follows the standard policy: explicit selection fails loudly
when unavailable, and auto selection logs the chosen backend.