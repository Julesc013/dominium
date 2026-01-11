# SPEC_TIME_KNOWLEDGE — Diegetic Time and Epistemic Gating

Status: draft
Version: 1

## Purpose
Define how time knowledge is acquired, gated, and represented. Time knowledge is
diegetic and subject to uncertainty; it does not affect authoritative ACT.

This spec is documentation-only. It introduces no runtime logic.

## Core rules
- At start, actors may have no clock, no calendar, and no HUD time.
- Time knowledge is unlocked via devices, documents, astronomy, organizations,
  or networks.
- HUD time is strictly diegetic: remove device -> info disappears.
- Damaged devices produce drift and uncertainty.

ASCII diagram:

  ACT -> Time Standard -> Device/Knowledge Gate -> UI Label/UNKNOWN

## Knowledge gating
Time standards (calendar, clock, frame preference) are usable only if known and
authorized. Lack of knowledge produces UNKNOWN, not defaults.

## Uncertainty and drift
- Devices can drift deterministically over ACT.
- Uncertainty is explicit and bounded.
- No RNG-based jitter.

## Examples
Positive:
- An actor without a clock sees UNKNOWN for time labels.
- A damaged clock shows a bounded interval, not a precise time.

Negative (forbidden):
- Always showing time in UI regardless of devices.
- Using wall-clock time to fill gaps.

## References
- docs/SPEC_STANDARDS_AND_RENDERERS.md
- docs/SPEC_INFORMATION_MODEL.md
- docs/SPEC_EPISTEMIC_GATING.md
- docs/SPEC_TIME_STANDARDS.md
- docs/SPEC_EFFECT_FIELDS.md

## Test and validation requirements (spec-only)
- Time knowledge gating tests
- Device loss drift tests
- UNKNOWN propagation tests
