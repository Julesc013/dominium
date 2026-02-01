Status: DERIVED
Last Reviewed: 2026-02-01
Supersedes: none
Superseded By: none

# Settings Guide (P3)

Status: binding for P3. Applies to CLI, TUI, and GUI.

## Principles

- Settings never change simulation semantics.
- Changes are deterministic, reversible, and explicit.
- CLI is canonical; TUI/GUI wrap CLI intents.

## Presentation

- **renderer**: explicit renderer selection (no hidden fallback).
- **ui_scale**: scale percent (e.g., 100/125/150).
- **palette**: default or high-contrast.
- **ui_density**: standard/compact/expanded (profile-driven).
- **verbosity**: minimal/normal/verbose (profile-driven).

## Input

- **keybind_profile**: default or alternate profiles.
- **input_mode**: standard or keyboard-only.

## Accessibility

- **accessibility_preset** (built-in):
  - default
  - high-contrast
  - screen-reader
  - low-motion
- Presets set: `ui_scale`, `palette`, `reduced_motion`,
  `screen_reader`, `keyboard_only`, `low_cognitive_load`.

## Debug

- **log_verbosity**: info / warn / error.
- **debug_ui**: on/off (exposes inspect overlays).

## CLI Equivalents

- `settings` prints current effective settings.
- `accessibility-next` and `keybind-next` cycle presets.
- UI toggles map to CLI intents with identical output.