Status: DERIVED
Last Reviewed: 2026-02-10
Supersedes: none
Superseded By: none

# UI Pipeline And Workspaces

UI workspaces are data-defined projections over command/state streams.

## Contract

- UI workspaces do not own simulation or authority state.
- Stage progression is sourced from `client_session_pipeline`.
- Command actions are canonical command IDs only.

## Workspace Schemas

- Workspace schema: `schema/ui/ui_workspace.schema`
- IR schema: `schema/ui/ui_ir.schema`
- Layout schema: `schema/ui/ui_layout.schema`

## Session Workspaces

- Transition workspace: `client/ui/workspaces/session_transition/session_transition.default.json`
- Ready workspace: `client/ui/workspaces/session_ready/session_ready.default.json`
- Running workspace: `client/ui/workspaces/session_running/session_running.default.json`

All three are deterministic data surfaces that can be rendered in CLI/TUI/GUI.

## Deterministic Rendering Rules

- Panel order is stable (`panel_id` lexical ordering).
- Stage bindings are explicit and non-overlapping.
- Unknown workspace fields are preserved but ignored by strict runtime readers.
