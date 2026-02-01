Status: DERIVED
Last Reviewed: 2026-02-01
Supersedes: none
Superseded By: none

# CLI Canon (UX-1)

CLI is the authoritative UX contract. Every player or operator action must be expressible as a CLI intent. TUI and GUI are pure projections that call the same intent APIs.

## Rules
- CLI is the source of truth for intent semantics.
- TUI and GUI must emit identical intent streams for identical actions.
- No GUI-only or TUI-only behaviors are allowed.
- Presentation changes must never alter simulation outcomes.

## Guarantees
- CLI output is deterministic and stable across platforms.
- UI logs capture intent identifiers, not localized text.
- Any UI feature must have a CLI equivalent command.

## References
- docs/ui/CLI_TUI_GUI_PARITY.md
- docs/ui/UI_FORBIDDEN_BEHAVIORS.md