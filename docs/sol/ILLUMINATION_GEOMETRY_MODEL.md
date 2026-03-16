Status: DERIVED
Last Reviewed: 2026-03-16
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: canon-aligned documentation set for convergence and release preparation

# Illumination Geometry Model

## Purpose

SOL-1 unifies lunar and planetary illumination around emitter/receiver/viewer geometry so Moon phase is derived from sunlight, receiver shape, and viewer position rather than from a standalone phase shortcut.

## Emitters

- `emitter.star`
- Required fields:
  - `position_ref`
  - `luminosity_proxy`
  - optional `spectrum_proxy` stub

Stars are light emitters only. In MVP they use coarse procedural or Sol-pin positions and deterministic luminosity proxies.

## Receivers

- `receiver.planet`
- `receiver.moon`
- Required fields:
  - `position_ref`
  - `radius`
  - `albedo_proxy`

Receivers are treated as spherical bodies in MVP. Surface-normal detail is not modeled yet.

## Viewer Geometry

- `viewer_ref` is a canonical position reference.
- For Moon phase in MVP, the viewer is the current Earth observer position.

## Derived Outputs

`illumination_fraction_visible(viewer, receiver, emitter)` is derived from the phase angle seen from the receiver center.

- Let `phase_angle` be the angle between:
  - receiver -> emitter
  - receiver -> viewer
- Visible illumination fraction is:
  - `(1 + cos(phase_angle)) / 2`

MVP implementation rules:

- fixed-point math only
- deterministic lookup-based phase-angle inversion
- deterministic ordering by `(tick, emitter_object_id, receiver_object_id, viewer_ref fingerprint)`
- albedo remains a multiplier/proxy input, not a truth-state phase variable

## Occlusion Stub

`occlusion_query(emitter, receiver, occluder)` is a policy hook.

- `occlusion.none_stub` returns `1.0`
- `occlusion.future_shadow` reserves the future eclipse path

MVP does not compute eclipse shadowing. It only preserves the canonical hook and the deterministic report surface.

## No Stored Phase

- Moon phase is never stored as canonical truth state.
- Moon illumination fraction is a derived illumination artifact.
- EARTH sky and lighting consume geometry-derived illumination outputs only.

## MVP Defaults

- Sun uses emitter role only
- Earth body albedo proxy default: `300` permille
- Moon body albedo proxy default: `120` permille
- Occlusion policy default: `occlusion.none_stub`

## Future Compatibility

This model is intentionally compatible with:

- multi-star systems
- planetary reflections
- eclipse queries
- per-body albedo refinement
- later MAT/DOM/SOL body semantics

No simulation law changes are introduced by SOL-1. This is a deterministic derived-view unification pass only.
