Status: DERIVED
Last Reviewed: 2026-02-01
Supersedes: none
Superseded By: none

# UI Naming Conventions

These conventions are required for deterministic binding and localization.

## UI document names

- `doc_name` MUST be stable and lowercase with underscores.
- Example: `launcher_ui`, `setup_ui`, `tool_editor_ui`.

## Widget names

- `widget.name` MUST be stable, lowercase, and underscore-separated.
- Example: `nav_play`, `instances_list`, `settings_apply`.

## Localization keys

Localization keys are derived as:

```
ui.<doc_name>.<widget_name>
```

Example:
- `ui.launcher_ui.nav_play`

## Action keys

- Action keys are namespaced by application and scope.
- Use dot-separated lower-case segments.
- Examples:
  - `launcher.nav.play`
  - `setup.nav.install`
  - `tool_editor.add_widget`

## Accessibility roles

Use stable, lower-case roles:
- `button`, `textbox`, `combobox`, `checkbox`, `radio`, `tab`, `tablist`,
  `tabpanel`, `list`, `listbox`, `tree`, `slider`, `control`
