# Launcher TUI

The TUI launcher is a curses-style front-end for power users and headless/server
setups. It drives the launcher core API (`dom_launch_*`) and renders Domino
models (tables/queries) in a split terminal layout.

## Layout
- Left pane (≈60% width): instances list from `instances_table` (id/name/path/flags),
  scrollable with a highlighted selection.
- Right pane (≈40% width): details for the selected instance via
  `DOM_QUERY_INST_INFO` and `dom_sim_get_state`; shows attached packages.
- Bottom status line: key hints and short status messages.

## Keys
- Up/Down: move selection
- PgUp/PgDn: scroll page
- F2: create a new instance (default name)
- F3: delete the selected instance (asks for confirmation)
- F5: launch the selected instance
- ESC or `q`: quit

Each action maps directly to a `dom_launch_action`:
`CREATE_INSTANCE`, `DELETE_INSTANCE`, `LAUNCH_INSTANCE`, and `EDIT_INSTANCE`
when selection changes.

## Requirements
- Curses-compatible terminal (ncurses/PDCurses); the target can be disabled via
  CMake if curses is unavailable (`DOMINIUM_ENABLE_LAUNCHER_TUI=OFF`).
- Runs under `DOM_UI_MODE_TUI`; no GUI/windowing required.

## Example session
```
$ dominium-launcher-tui
F2:New  F3:Delete  F5:Launch  Up/Down:Move  PgUp/PgDn:Scroll  ESC/q:Quit
[Instances list on left | details on right]
```
