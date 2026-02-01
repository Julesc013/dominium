Status: DERIVED
Last Reviewed: 2026-02-01
Supersedes: none
Superseded By: none

# Accessibility Model (UX-1)

Accessibility presets are data-only profiles that change presentation and input ergonomics. They must never alter simulation, authority, or outcomes.

## Presets
Presets are identified by stable ids and may adjust:
- Key bindings
- UI density
- Animation presence
- Color contrast
- Verbosity of explanations

Presets must be optional and composable. If a preset cannot be fully applied by a front-end, it must degrade gracefully and report which fields were ignored.

## File Format (Authoring)
Presets are stored as deterministic key/value files.

```
DOMINIUM_ACCESSIBILITY_V1
preset_id=accessibility.high_contrast
preset_version=1.0.0
ui_scale_percent=125
palette=high-contrast
log_level=info
ui_density=standard
verbosity=normal
keybind_profile_id=default
reduced_motion=1
keyboard_only=0
screen_reader=0
low_cognitive_load=0
```

Notes:
- Unknown keys must be preserved by tools.
- Boolean values accept `0/1`, `true/false`, `yes/no`.
- UI-only fields must never be forwarded into simulation state.

## CLI Integration
Front-ends may accept:
- `--accessibility-preset <path>`

If a preset is provided, its fields override defaults for the current session only.

## Schema
- `schema/accessibility_preset.schema`

## References
- docs/ui/CLI_CANON.md
- docs/ui/UX_OVERVIEW.md