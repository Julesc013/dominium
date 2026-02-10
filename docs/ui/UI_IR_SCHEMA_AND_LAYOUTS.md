Status: CANONICAL
Last Reviewed: 2026-02-10
Supersedes: none
Superseded By: none

# UI IR Schema And Layouts

This document defines the UI data contract used by CLI, TUI, and GUI renderers.

## Canonical Artifacts

- `schema/ui/ui_ir.schema`
- `schema/ui/ui_layout.schema`
- `schema/ui/ui_node.schema`
- `schema/ui/ui_event.schema`
- `schema/ui/ui_accessibility.schema`

## Representation Rules

- UI IR is a document containing nodes and bindings.
- Layout is declared as docking, splits, tabs, and constraints.
- Command bindings reference canonical command IDs.
- Observable bindings reference read-only state keys.
- Unknown extension fields are preserved.

## Determinism Requirements

- Stable traversal order for nodes and panels.
- Stable ordering for command/action lists.
- No renderer-specific command behavior.
- No implicit defaults for required layout fields.

## Compatibility

- Schema version bumps are required for incompatible shape changes.
- Transform-only migrations are allowed for compatible shape evolution.
- Deprecated fields remain readable until explicitly retired.

