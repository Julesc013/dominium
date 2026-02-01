Status: DERIVED
Last Reviewed: 2026-02-01
Supersedes: none
Superseded By: none

# Launcher TUI (Keyboard‑Only Front‑End)

Doc Version: 1

The TUI is a keyboard‑only front‑end for the Dominium launcher control plane. It is designed for headless/remote use and for environments where a GUI is unavailable.

The TUI is a thin adapter: it dispatches launcher core operations and/or control-plane commands and renders their results. UI choices do not affect determinism.

## Running

- Run the interactive TUI:
  - `dominium-launcher --front=tui`
- Use a custom state root:
  - `dominium-launcher --front=tui --home=<state_root>`

## Non‑Interactive Smoke Mode

Used by CI and tests to ensure the TUI entrypoint can run without a terminal:

- `dominium-launcher --smoke-tui --home=<state_root>`

## Layout

- Top: tab strip (Play / Instances / Packs / Options / Diagnostics / Quit)
- Left: instance list
- Center: tab content (read‑only summaries)
- Right: actions for the active tab
- Bottom: status line (last operation outcome)

## Navigation (Keys)

- Up/Down: move selection within a list, or move focus between widgets
- Left/Right: move focus between widgets
- Enter: activate the focused button/action
- Quit: activate the `Quit` action in the tab strip

## Tabs

### Play

- Readouts: selected instance, target (`game` or `tool:<tool_id>`), offline flag
- Actions: Toggle Target, Toggle Offline, Verify, Launch, Safe Launch, Audit Last

### Instances

- Readouts: selected instance paths (root/manifest/logs)
- Actions: Refresh, Create Empty, Create Template, Clone, Delete, Import, Export Def, Export Bundle, Mark Known‑Good

### Packs

- Readouts: ordered pack list for the selected instance
- Actions: Toggle Enabled, Cycle Policy, Apply (transactional), Discard

### Options

- Readouts: instance config overrides (allow_network, gfx_backend, renderer_api, window_mode, width/height)
- Actions: Toggle Offline, Set Gfx Backend, Set Renderer API, Cycle Window Mode, Set Width, Set Height, Reset Graphics

### Diagnostics

- Readouts: recent run directory ids for the selected instance
- Actions: Refresh, Audit Last, Diag Bundle

## Related Docs

- `docs/launcher/CLI.md`
- `docs/launcher/DEV_UI.md`
- `docs/launcher/TESTING.md`
- `docs/launcher/ECOSYSTEM_INTEGRATION.md`