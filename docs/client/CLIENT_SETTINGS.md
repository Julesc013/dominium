Status: CANONICAL
Last Reviewed: 2026-02-10
Supersedes: none
Superseded By: none

# Client Settings

Client settings are local presentation settings. They do not alter simulation semantics.

## NOW (implemented)

- `ui.mode_preference` (`cli|tui|gui`)
- `ui.scale`
- `ui.font_size`
- `ui.contrast`
- `input.keybindings`
- `audio.volume`
- `audio.mute`
- `renderer.selection`
- `accessibility.reduced_motion`
- `accessibility.keyboard_only`
- `accessibility.screen_reader`
- `replay.recording_enabled`
- `debug_overlay.visibility`
- `network.preference` (`timeout_ms`, `sort_mode`)

## SOON (scaffolded)

- `controller.profiles`
- `accessibility.advanced`
- `server_browser.advanced_filters`

SOON settings must refuse deterministically when unavailable.

## LATER (deferred)

- theming packs
- animated transitions
- visual replay timeline

## Canonical Commands

- `client.settings.get`
- `client.settings.set`
- `client.settings.reset`

CLI is canonical; TUI/GUI route through the same command graph.

