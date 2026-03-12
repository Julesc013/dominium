Status: DERIVED
Last Reviewed: 2026-02-28
Version: 1.0.0
Scope: INT-1 InteriorVolumeGraph doctrine for deterministic interior topology, portal state, and occlusion.
Stability: provisional
Future Series: DOC-ARCHIVE
Replacement Target: legacy reference surface retained without current binding authority

# Interior Volume Model

## A) InteriorVolume
- `InteriorVolume` is a bounded spatial node attached to `parent_spatial_id`.
- Each volume declares:
  - `volume_id`
  - `parent_spatial_id`
  - `local_transform`
  - `bounding_shape` (`aabb`/`convex_hull` payload)
  - `volume_type_id` (`volume.room`, `volume.corridor`, etc.)
  - optional occupancy capacity metadata in extensions
  - deterministic tags
- Interior volumes are data-defined and reusable across buildings, vehicles, machines, tunnels, ships, stations, and megastructures.

## B) Portal
- `Portal` connects two interior volumes and carries semantic traversal + visibility behavior.
- Each portal declares:
  - `portal_id`
  - `from_volume_id`
  - `to_volume_id`
  - `portal_type_id`
  - `state_machine_id`
  - `sealing_coefficient`
- Portal is both:
  - `NetworkEdge` for connectivity
  - `StateMachineComponent` host for `open|closed|locked|damaged` transitions
- Portal state transitions must be process-triggered; direct state mutation is forbidden.

## C) InteriorVolumeGraph
- `InteriorVolumeGraph` is a deterministic graph where:
  - node payload = `InteriorVolume`
  - edge payload = `Portal`
- Deterministic ordering:
  - volumes by `volume_id`
  - portals by `portal_id`
- Connectivity queries are deterministic and state-machine aware.

## D) Epistemic Rule
- Interior occlusion is deterministic and derives from:
  - reachable-volume topology under current portal states
  - active lens channel scope
  - law and authority context
- If no open portal path exists between viewer volume and target volume, PerceivedModel excludes the occluded entity by default.
- Freecam can bypass interior occlusion only when law explicitly permits.

## Integration
- `FlowSystem`: portals carry `sealing_coefficient` for later INT-2 air/fluid exchange.
- `StateMachineComponent`: portal open/close/lock state authority.
- `ConstraintComponent`: sealing/docking constraints can bind to portal participants.
- `SpatialNode`: volume transforms compose against parent spatial frames.
- `POSE/CTRL/MOB`: seating, entry rules, and vehicle interior movement attach to this substrate.

## Migration Rule
- Assemblies may optionally bind an `interior_graph_id`.
- No interior graph attached means no behavior change from current baseline.
- No building- or vehicle-specific hardcoded logic is permitted; all behavior is graph + state-machine driven.
