Status: DERIVED
Last Reviewed: 2026-02-12
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: patched document aligned to current canon ownership and release scope

# Experiences And Defaults

## Patch Notes

- Current status: partially aligned to the Constitutional Architecture and release-freeze documentation set.
- Required updates: documentation surface exists, but current canon ownership is not explicit
- Cross-check with: `docs/audit/CANON_MAP.md` and `docs/audit/DOC_DRIFT_MATRIX.md`.


Dominium experiences are profile compositions, not hardcoded game modes.

## Built-In Experiences
- `exp.observer`
  - truth-oriented exploration with watermark
  - freecam and world-layer overlays only when entitled
- `exp.survival`
  - constrained intent set with survival HUD/workspace
- `exp.hardcore`
  - survival law + stricter persistence and tuning bundle
- `exp.creative`
  - scenario-level authoring tools with explicit law gating
- `exp.lab`
  - assumptions/metrics/ensemble workflow
- `exp.mission`
  - mission evaluator surfaces and constrained mission intents

## Defaults
- Runtime minimum is `bundle.core.runtime`.
- Additional experiences, scenarios, and lessons are shipped as optional bundle profiles.
- Missing optional content returns deterministic refusal with recovery hints.

## Safe Customization
- Choose a different experience profile.
- Choose a scenario from installed/visible sets.
- Choose a parameter bundle for tuning.
- Customization stays deterministic when schema-valid and hash-pinned.
