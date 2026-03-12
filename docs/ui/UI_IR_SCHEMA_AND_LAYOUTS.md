Status: CANONICAL
Last Reviewed: 2026-02-10
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: patched document aligned to current canon ownership and release scope

# UI IR Schema And Layouts

## Patch Notes

- Current status: partially aligned to the Constitutional Architecture and release-freeze documentation set.
- Required updates: documentation surface exists, but current canon ownership is not explicit
- Cross-check with: `docs/audit/CANON_MAP.md` and `docs/audit/DOC_DRIFT_MATRIX.md`.


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
