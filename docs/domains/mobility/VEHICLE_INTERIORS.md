Status: DERIVED
Last Reviewed: 2026-03-16
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-ARCHIVE
Replacement Target: legacy reference surface retained without current binding authority

# Vehicle Interiors (MOB-10)

Status: Baseline constitutional contract for moving interior-capable assemblies.

## 1) Vehicle Spatial Frame

- Vehicle interiors use the same `InteriorVolumeGraph` substrate as buildings.
- Interior volumes are anchored by `parent_spatial_id` and resolve world transforms through spatial composition.
- For vehicles, `parent_spatial_id` is the vehicle spatial node (`vehicle.spatial_id`).
- Pose slots used for seating/driver control are scoped to the same vehicle assembly/interior graph and remain path-validated.

## 2) Boundary Exchange While Moving

- Interior flow simulation remains local to the interior graph and deterministic.
- Exterior boundary conditions are sampled from FieldLayer at outside-facing portals/leaks.
- Required exterior fields for boundary exchange:
  - `field.temperature`
  - `field.moisture`
  - `field.wind`
  - `field.visibility`
- Optional ram-air term (stub): uses wind vector plus vehicle micro velocity to scale air conductance at boundary portals.

## 3) Behavior Consistency (Vehicles == Buildings)

- No vehicle-only flow solver branch is allowed.
- Portal state machines, leak hazards, and compartment quantities use the same INT process paths for all interior graphs.
- Vehicle integration is adapter-level data binding:
  - spatial anchor binding,
  - boundary sampling position derivation,
  - dashboard/instrument projection.

## 4) Incidents and Failures

- Structural fracture that breaches a hull boundary must create or amplify leak behavior.
- Portal/hull seal breaches are represented through deterministic process mutations.
- Mobility/interior incident stream includes:
  - `incident.breach`
  - `incident.decompression` (stub classification)
  - `incident.flooding_started`
- Incidents are event-sourced and reenactable.

## 5) Doors, Access, and Seating in Motion

- Entering seats/pose slots requires a valid interior portal path.
- Motion-aware safety policy may forbid cross-compartment moves while vehicle is in motion.
- Door/hatch operations remain ACT task/process mediated (`process.portal_*`, `process.hatch_*`, `process.vent_*`).
- Driver control remains granted through pose-slot control binding and CTRL law gates.

## 6) Diegetic Instruments and Epistemics

- Vehicle dashboard readouts derive from instrument assemblies and perceived channels only.
- Required dashboard surfaces:
  - pressure status
  - oxygen status
  - smoke alarm
  - flood alarm
- Values are quantized/coarsened under diegetic policy; no direct truth-state bypass.

## 7) Performance and Determinism

- No CFD/HVAC global solver in MOB-10.
- Flow and dashboard updates remain deterministic and tick-driven.
- Under budget pressure:
  - deterministic partial processing,
  - explicit degrade metadata and decision logging,
  - no silent mutation.

## 8) Non-Goals

- No survival health effects.
- No full HVAC machine implementation.
- No nondeterministic or wall-clock driven behavior.
