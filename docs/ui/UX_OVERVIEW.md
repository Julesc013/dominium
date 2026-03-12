Status: DERIVED
Last Reviewed: 2026-02-01
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: patched document aligned to current canon ownership and release scope

# UX Overview (UX-1)

## Patch Notes

- Current status: partially aligned to the Constitutional Architecture and release-freeze documentation set.
- Required updates: documentation surface exists, but current canon ownership is not explicit
- Cross-check with: `docs/audit/CANON_MAP.md` and `docs/audit/DOC_DRIFT_MATRIX.md`.


The Dominium UX is CLI-first, deterministic, and presentation-only. All UI surfaces are thin projections of stable intents and read-only data.

## Pillars
- CLI is canonical for all actions and intents.
- TUI/GUI parity is mandatory.
- Localization and accessibility are data-driven.
- HUDs are declarative overlays.
- Refusals are explicit, explainable, and consistent.

## Primary Documents
- docs/ui/UX_RULES.md
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
