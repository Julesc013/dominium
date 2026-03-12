Status: DERIVED
Last Reviewed: 2026-02-01
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: patched document aligned to current canon ownership and release scope

# CLI Canon (UX-1)

## Patch Notes

- Current status: partially aligned to the Constitutional Architecture and release-freeze documentation set.
- Required updates: documentation surface exists, but current canon ownership is not explicit
- Cross-check with: `docs/audit/CANON_MAP.md` and `docs/audit/DOC_DRIFT_MATRIX.md`.


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
