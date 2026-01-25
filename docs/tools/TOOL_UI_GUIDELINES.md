# TOOL UI GUIDELINES

Tool UIs are read-only, non-authoritative views. They must operate on snapshots,
event streams, history artifacts, and capability lists only.

## Requirements
- Must be parity-locked with CLI commands.
- Must be headless-capable and scriptable via CLI.
- Must emit deterministic event logs.
- Must surface the same errors and refusal reasons as the CLI.

## Mandatory tool UIs
- World Inspector
- Agent Inspector
- Institution Inspector
- History / Replay Viewer
- Pack / Capability Inspector

## Prohibitions
- No mutation of simulation state.
- No authority bypass or epistemic leaks.
- No GUI-only or TUI-only features.

References:
- docs/tools/TOOLING_OVERVIEW.md
- docs/ui/CLI_TUI_GUI_PARITY.md
- docs/ui/UI_FORBIDDEN_BEHAVIORS.md
