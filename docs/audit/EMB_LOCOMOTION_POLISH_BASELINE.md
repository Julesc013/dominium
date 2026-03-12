Status: DERIVED
Last Reviewed: 2026-03-10
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: canon-aligned documentation set for convergence and release preparation

# EMB Locomotion Polish Baseline

## Scope

This report records the EMB-2 locomotion polish baseline delivered for Dominium v0.0.0.

## Jump Behavior And Gating

Implemented jump surface:

- `process.body_jump`
- entitlement gated by `ent.move.jump`
- grounded-only execution
- deterministic tick cooldown

Jump remains process-only and law-gated.
No UI or renderer path writes jump results directly into truth.

## Impact Hooks

Implemented impact surface:

- pre-clamp vertical speed is captured at ground contact
- above-threshold contacts emit canonical `impact_event` rows
- impact rows carry deterministic IDs, tick, subject, and impact speed

Impact events are informational only.
They do not change survival or injury state.

## Camera Smoothing Guarantees

Implemented render-only smoothing:

- FP and TP target camera transforms are resolved first
- bounded fixed-point smoothing is then applied in a derived viewer/render path
- authoritative body/camera truth remains unsmoothed

Freecam and inspect remain unsmoothed.

## Friction Tuning

Implemented damping model:

- base damping from body template movement params
- slope-aware modifier from EARTH-6 terrain response
- optional `field.friction` sampling when present
- deterministic fallback when the field is absent

## Forward Readiness

EMB-2 is ready for:

- SERVER-MVP-0 authoritative embodiment playback
- APPSHELL command routing for movement affordances
- later injury/fall-damage systems layered on top of the `impact_event` surface
- future richer surface material/friction profiles without changing body identity or jump command semantics
