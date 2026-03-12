Status: DERIVED
Last Reviewed: 2026-02-01
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: patched document aligned to current canon ownership and release scope

# UI Guidelines (DEV-OPS-0)

## Patch Notes

- Current status: partially aligned to the Constitutional Architecture and release-freeze documentation set.
- Required updates: documentation surface exists, but current canon ownership is not explicit
- Cross-check with: `docs/audit/CANON_MAP.md` and `docs/audit/DOC_DRIFT_MATRIX.md`.


Scope: application GUIs (setup, launcher, client, server status UI, tools UI).

Accessibility (mandatory)
- Keyboard-only navigation for all interactive elements.
- Screen-reader tags for every interactive element.
- UI IR keys (strings, required when interactive):
  - `accessibility.name`
  - `accessibility.role`
  - `accessibility.description`
- Resizable layouts (no fixed-only layouts).
- No color-only meaning (add text or icons).

Internationalization (mandatory)
- All strings are externalized.
- Locale packs are normal packs.
- Missing locale keys must fall back to raw keys.

Modularity (mandatory)
- UI is data-driven via UI IR.
- UI contains no business logic.
- UI binds only to canonical commands.
- UI backends are replaceable and must not change behavior.

Determinism and safety
- UI must not mutate authoritative state.
- UI must not alter replay or determinism.
- UI logs must be deterministic for identical inputs.

References
- docs/specs/SPEC_DUI.md
- docs/architecture/GUI_BASELINE.md
