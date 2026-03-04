# Pose And Mount Model

Status: Canonical (POSE-1)
Version: 1.0.0

## Purpose
POSE-1 introduces deterministic, process-driven posture occupancy and assembly attachment semantics without hardcoded vehicle/item rules.

## PoseSlot
- `PoseSlot` is a physical posture anchor attached to an assembly and interior volume.
- Canonical fields:
  - `allowed_postures` (`posture.sit|posture.stand|posture.crouch|posture.lie`)
  - `allowed_body_tags`
  - `interior_volume_id`
  - `requires_access_path`
  - `control_binding_id` (optional)
  - `exclusivity` (`single|multiple`)
- Deterministic identity:
  - `pose_slot_id = H(parent_assembly_id, local_index)` (pack-compiled deterministic assignment).

## MountPoint
- `MountPoint` is a generic deterministic attachment interface between assemblies.
- Canonical use cases:
  - docking ports
  - trailer hitches
  - rail couplers
  - turret/module attachment
- Canonical fields:
  - `mount_tags`
  - `alignment_constraints` (deterministic stub in POSE-1)
  - `state_machine_id`
  - `connected_to_mount_point_id`

## Portal Access Requirement
- `process.pose_enter` must enforce interior reachability when `requires_access_path=true`.
- Reachability uses InteriorVolumeGraph path checks through open/permeable portals only.
- Occupancy without reachable path is refused with `refusal.pose.no_access_path`.

## Meta-Law Override
- `process.meta_pose_override` is admin-only and deterministic.
- Override may bypass access/exclusivity, but must emit:
  - explicit provenance event
  - explicit conservation exception entry (`exception.meta_law_override` when ledger runtime is active)
- Silent bypass is forbidden.

## Determinism And Mutation Contract
- Pose/mount state mutates only through process runtime.
- No teleport-like occupancy without explicit process.
- Attach/detach ordering and IDs are stable under deterministic sort (`pose_slot_id`, `mount_point_id`).

## ControlBinding Hook (CTRL Prep)
- Occupied PoseSlots may reference a `control_binding_id`.
- Binding grants (`grants_process_ids`, `grants_surface_ids`) are exposed to affordance resolution metadata.
- POSE-1 does not enforce control policy semantics beyond deterministic exposure/gating hooks.
