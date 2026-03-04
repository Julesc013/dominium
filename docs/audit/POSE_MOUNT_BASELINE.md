Status: DERIVED
Last Reviewed: 2026-02-28
Version: 1.0.0
Scope: POSE-1 PoseSlots, MountPoints, and Portal Access baseline completion report.

# Pose And Mount Baseline

## Pose Slot Model
- PoseSlots are defined by `schema/interaction/pose_slot.schema` and `schemas/pose_slot.schema.json`.
- Runtime normalization and deterministic occupancy helpers are implemented in `src/interaction/pose/pose_engine.py`.
- Canonical enter/exit flows are process-driven in `tools/xstack/sessionx/process_runtime.py`:
  - `process.pose_enter`
  - `process.pose_exit`
  - `process.meta_pose_override` (admin/meta-law path)
- Deterministic pose occupancy provenance rows are emitted into `pose_mount_provenance_events`.

## Mount Point Model
- MountPoints are defined by `schema/interaction/mount_point.schema` and `schemas/mount_point.schema.json`.
- Runtime normalization and attach/detach rules are implemented in `src/interaction/mount/mount_engine.py`.
- Canonical process handlers are integrated in process runtime:
  - `process.mount_attach`
  - `process.mount_detach`
- Symmetric connection links and deterministic state tags are maintained (`attached` / `detached`).

## Access Path Enforcement
- Pose entry checks `requires_access_path` and validates interior reachability through `InteriorVolumeGraph` open-portal connectivity.
- Refusal path:
  - `refusal.pose.no_access_path`
- Teleport occupancy bypass is prevented in normal law path.
- Meta override remains explicit and logged via `exception.meta_law_override`.

## Control Binding Hooks
- Control binding schema/registry integrated:
  - `schema/interaction/control_binding.schema`
  - `data/registries/control_binding_registry.json`
- Pose registries are integrated into registry compile and lockfile hashing:
  - `posture_registry`
  - `mount_tag_registry`
  - `control_binding_registry`
- Occupied pose slots expose deterministic control grants:
  - `pose_control_binding_ids`
  - `pose_granted_process_ids`
  - `pose_granted_surface_ids`
- Observation and affordance layers propagate grants as derived metadata (no direct truth mutation).

## Render And Inspection Integration
- Inspection sections integrated:
  - `section.pose_slots_summary`
  - `section.mount_points_summary`
- Overlay path adds deterministic pose/mount marker glyphs and occupancy/attachment indicators.
- Epistemic behavior:
  - default views return accessible summaries
  - hidden detail remains gated by law/entitlement policy

## Guardrails
- RepoX invariants integrated:
  - `INV-POSE-REQUIRES-PROCESS`
  - `INV-MOUNT-REQUIRES-PROCESS`
  - `INV-NO-TELEPORT-OCCUPY`
- AuditX analyzers integrated:
  - `PoseBypassSmell` (`E102_POSE_BYPASS_SMELL`)
  - `MountBypassSmell` (`E103_MOUNT_BYPASS_SMELL`)
- TestX coverage added:
  - `test_pose_access_path_required`
  - `test_pose_exclusivity`
  - `test_mount_attach_deterministic`
  - `test_control_binding_exposed`
  - `test_meta_override_logged`

## Gate Summary
- RepoX (`python tools/xstack/repox/check.py --repo-root . --profile STRICT`):
  - PASS
  - `repox scan passed (files=1030, findings=1)` with non-gating warn in `INV-AUDITX-REPORT-STRUCTURE`.
- AuditX (`python tools/xstack/auditx/check.py --repo-root . --profile STRICT`):
  - run complete / PASS status
  - `auditx scan complete (changed_only=false, findings=1008)` (warnings reported).
- TestX POSE subset (`python tools/xstack/testx/runner.py --repo-root . --profile STRICT --cache off --subset ...`):
  - PASS for:
    - `test_pose_access_path_required`
    - `test_pose_exclusivity`
    - `test_mount_attach_deterministic`
    - `test_control_binding_exposed`
    - `test_meta_override_logged`
- strict profile run (`python tools/xstack/run.py strict --repo-root . --cache on`):
  - REFUSAL (`exit_code=2`)
  - blocking steps include:
    - `01.compatx.check` refusal with existing compatibility findings (`findings=161`)
    - `07.session_boot.smoke` refusal (`session create refused`)
    - `10.testx.run` fail (`selected_tests=381`, global strict suite outside POSE subset)
    - `13.packaging.verify` refusal (`lab build validation refused`)
  - report: `tools/xstack/out/strict/latest/report.json`
- ui_bind (`python tools/xstack/ui_bind.py --repo-root . --check`):
  - PASS (`checked_windows=21`)

## Extension Points
- CTRL series can consume `control_binding_id` grants without adding vehicle-specific branches.
- MOB series can reuse mount/pose process outputs for driver/turret occupancy and docking control surfaces.
- POSE-2 can add richer posture/body-shape constraints without changing process-only mutation invariants.
