Status: DERIVED
Last Reviewed: 2026-02-08
Supersedes: none
Superseded By: none

# Freecam Modes

## Definitions
- `truth`: authoritative world state; never rendered in normal play.
- `observation`: current epistemic artifacts produced by lawful observation.
- `memory`: persisted epistemic artifacts from prior observation.
- `presentation`: camera and UI composition only; no authority mutation.

## Global Rules
- Freecam is presentation-only and cannot request additional authority data.
- Freecam mode switches are logged to the UI event log.
- Mode refusal is explicit and includes a reason code.

## Modes
- `EMBODIED_FREECAM`
  - Diegetic mode.
  - Observation-only rendering.
  - Camera movement is constrained by policy leash.
  - Occlusion does not reveal unknown entities.
- `MEMORY_FREECAM`
  - Diegetic mode.
  - Memory-only rendering.
  - Memory may be stale or incorrect until re-observed.
- `OBSERVER_FREECAM`
  - Non-diegetic tooling mode.
  - Requires explicit entitlement.
  - Output is watermarked and audit logged.

## Refusal Reason Codes
- `CAMERA_REFUSE_POLICY`: camera mode blocked by local policy.
- `CAMERA_REFUSE_ENTITLEMENT`: tooling entitlement missing.
- `CAMERA_REFUSE_WORLD_INACTIVE`: no active world context.
- `CAMERA_REFUSE_USAGE`: invalid or incomplete command arguments.

