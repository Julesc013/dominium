# SPEC_LANES_AND_BUBBLES - Lane Scheduler and Activation Bubbles

This spec defines the lane scheduler that governs which simulation lane each
vessel/entity occupies, how transitions occur, and how local activation
bubbles are created and collapsed.

## 1. Lane types
Lane membership is per vessel (or controllable entity).

- `LANE_ORBITAL`: on-rails orbit lane (patched conics).
- `LANE_APPROACH`: transitional lane (optional; may be stubbed).
- `LANE_LOCAL_KINEMATIC`: local bubble with kinematic updates only.
- `LANE_DOCKED_LANDED`: constrained lane; no free motion.

Only one lane is active per vessel at a time.

## 2. Activation bubbles
Activation bubbles enable local updates in a bounded region:

- Each bubble has a center vessel and radii in meters (fixed-point).
- Hysteresis is required:
  - `enter_radius_m`: activates the bubble when crossed inward.
  - `exit_radius_m`: deactivates the bubble when crossed outward.
  - `exit_radius_m` MUST be greater than `enter_radius_m`.

Budget rules:
- At most `N` bubbles can be active (baseline `N=1`).
- If a request would exceed the budget, the scheduler must refuse activation
  or collapse an existing bubble deterministically.

Bubble contents:
- Vessels inside the bubble.
- Surface chunks, constructions, and derived data (see
  `docs/SPEC_SURFACE_STREAMING.md`).
- Construction placement/removal commands are accepted only while a matching
  bubble is active; otherwise they are refused.

Bubble creation and teardown must never block the UI/render thread. Any heavy
work must be queued as derived jobs.

## 3. Transitions and determinism
- Lane transitions occur only at tick boundaries.
- Illegal transitions are refused with explicit codes.
- When multiple transitions occur on a tick, ordering must be deterministic
  (e.g., ascending vessel id).

## 4. Collapse-to-rails projection
When leaving a local lane, vessels must be projected back into the orbital
lane deterministically:

- Projection derives on-rails orbital elements from local state.
- The projection must be deterministic and idempotent.
- If projection cannot be computed, the scheduler must refuse the transition.

## 5. Warp gating
- Warp is a pacing change only; it does not change canonical state directly.
- While in `LANE_LOCAL_KINEMATIC`, warp factor is capped.
- If a warp request exceeds the cap, the scheduler must either refuse or force
  a collapse to `LANE_ORBITAL` before accepting the warp (policy-defined).

## 6. Surface constraints (v1)
- `LANE_DOCKED_LANDED` attaches to a deterministic surface position (body id +
  lat/long + altitude).
- Landed attachment does not advance physics; it constrains local motion until
  detachment.
- Surface attachment must not block streaming; missing surface data degrades
  fidelity only.

## Related specs
- `docs/SPEC_ORBITS_TIMEWARP.md`
- `docs/SPEC_REFERENCE_FRAMES.md`
- `docs/SPEC_SPACETIME.md`
- `docs/SPEC_SURFACE_STREAMING.md`
