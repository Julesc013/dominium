Status: DERIVED
Last Reviewed: 2026-02-01
Supersedes: none
Superseded By: none

# UI Binding Rules

These rules are enforced mechanically by UI_BIND_PHASE. No manual exceptions.

## Binding requirements (per interactive element)

Each interactive UI element MUST provide:
- unique `ui_element_id` (doc + widget name)
- `action` bound to a canonical command name
- command argument schema present and recognized
- declared failure codes for the command
- accessibility metadata:
  - `accessibility.name`
  - `accessibility.role`
  - `accessibility.description`
- `localization.key`

## Allowed enable/disable predicates

UI enablement may only use:
- `instance.selected`
- `profile.present`
- `capability:<id>`

Any other predicate causes build failure.

## UI code behavior

UI code MAY ONLY call:
- `appcore_dispatch_command(...)` using a descriptor from
  `appcore_ui_command_desc_for_action(...)`.

UI code MUST NOT:
- call authoritative logic directly
- perform filesystem or network access
- implement command branching in UI code

## Generated artifacts

The following files are generated and immutable:
- `libs/appcore/ui_bind/ui_command_binding_table.h`
- `libs/appcore/ui_bind/ui_command_binding_table.c`
- `libs/appcore/ui_bind/ui_accessibility_map.h`
- `libs/appcore/ui_bind/ui_accessibility_map.c`
- `libs/appcore/ui_bind/ui_localisation_usage_report.json`

Edits to these files must be made by regenerating via `tool_ui_bind --write`.
