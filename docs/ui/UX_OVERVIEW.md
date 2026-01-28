# UX Overview (UX-1)

The Dominium UX is CLI-first, deterministic, and presentation-only. All UI surfaces are thin projections of stable intents and read-only data.

## Pillars
- CLI is canonical for all actions and intents.
- TUI/GUI parity is mandatory.
- Localization and accessibility are data-driven.
- HUDs are declarative overlays.
- Refusals are explicit, explainable, and consistent.

## Primary Documents
- docs/ui/CLI_CANON.md
- docs/ui/LOCALIZATION_MODEL.md
- docs/accessibility/ACCESSIBILITY_MODEL.md
- docs/ui/HUD_COMPOSITION.md
- docs/ui/ONBOARDING_GUIDE.md

## Tooling
Use read-only tooling to explain refusals and diagnose data:
- `refusal_explain`
- `capability_inspect`
- `replay_metrics`

These tools provide the same information surfaced by inspectors in CLI/TUI/GUI.
