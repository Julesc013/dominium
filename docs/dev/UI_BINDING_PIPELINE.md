Status: DERIVED
Last Reviewed: 2026-02-01
Supersedes: none
Superseded By: none

# UI Binding Pipeline (UI_BIND_PHASE)

UI_BIND_PHASE is a mandatory build phase that validates UI IR bindings and
generates the binding artifacts used by GUI shells.

## What runs

UI_BIND_PHASE runs:
- locally during GUI builds
- in CI
- in TestX

The phase is executed by:
- `tool_ui_bind --check`

## Inputs

- UI index: `tools/ui_index/ui_index.json`
- UI IR documents (canonical entries): `.tlv` files referenced by the index
- Canonical command registry: `libs/appcore/command/command_registry.c`

## Outputs

Generated outputs are written under:
- `libs/appcore/ui_bind/`

Files:
- `ui_command_binding_table.h`
- `ui_command_binding_table.c`
- `ui_accessibility_map.h`
- `ui_accessibility_map.c`
- `ui_localisation_usage_report.json`

These files are committed and must not be edited by hand.

## Failure conditions (build errors)

UI_BIND_PHASE fails if any of the following occur:
- UI element lacks a unique identifier
- Action key does not map to a canonical command
- Command has no argument schema
- Command has no failure codes
- Accessibility metadata missing (name/role/description)
- Localization key missing
- Generated outputs are missing or stale

## Manual regeneration

Use `--write` only when updating UI IR or command registry:

```sh
tool_ui_bind --repo-root . --ui-index tools/ui_index/ui_index.json --out-dir libs/appcore/ui_bind --write
```

## Guarantees

When UI_BIND_PHASE passes:
- GUI actions map only to canonical commands
- Accessibility metadata is present for interactive UI elements
- Localization keys are present for interactive UI elements
- GUI bindings are deterministic and reproducible
