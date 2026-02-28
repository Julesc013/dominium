Status: DERIVED
Version: 1.0.0
Last Reviewed: 2026-03-01
Scope: CTRL-6 retro-consistency audit for view/camera/epistemic control

# CTRL6 Retro Audit

## Canon/Invariant Frame

- `docs/canon/constitution_v1.md` A1/A2/A3/A7/A10.
- `AGENTS.md` process-only mutation, truth/perceived/render separation, no silent fallback.
- Target invariants for this migration:
  - `INV-VIEW-CHANGES-THROUGH-CONTROL`
  - `INV-NO-DIRECT-CAMERA-TOGGLE`
  - `INV-NO-TRUTH-ACCESS-IN-RENDER`

## Current Camera/View Paths

## 1) Control-plane view action path (already present)

- `data/registries/control_action_registry.json`
  - `action.view.change` -> `process.camera_set_view_mode`.
- `src/control/control_plane_engine.py`
  - Negotiates `request_vector.view_requested` and emits process intent.

## 2) Direct process runtime camera mutation paths (ad hoc risk)

- `tools/xstack/sessionx/process_runtime.py`
  - `process.control_bind_camera` / `process.camera_bind_target`.
  - `process.control_unbind_camera` / `process.camera_unbind_target`.
  - `process.camera_set_view_mode`.
  - `process.control_set_view_lens` / `process.camera_set_lens`.
- These branches perform policy checks and mutate `universe_state.camera_assemblies` directly.
- Legacy aliases (`process.control_*`) remain active and can be called without explicit `ControlIntent` envelope provenance.

## 3) Freecam / debug / spectator / replay behavior sources

- View-mode declarations currently live in `data/registries/view_mode_registry.json`:
  - `view.free.lab` (freecam-style).
  - `view.follow.spectator`.
  - `view.free.observer_truth`.
- Ranked/casual/profile restrictions are partly split between:
  - `src/control/negotiation/negotiation_kernel.py`
  - `tools/xstack/sessionx/process_runtime.py` control-policy checks.
- Replay policy exists at control-policy level (`ctrl.policy.replay`) but mutation forbiddance is not centralized enough in control-plane refusal routing.

## Direct Camera Manipulation Outside Control Plane

- Runtime process branches listed above mutate camera fields in-place:
  - `view_mode_id`
  - `target_type` / `target_id`
  - `binding_id`
  - lens compatibility fields
- Current implementation can still be reached by raw process intents in script/runtime flows.
- Required migration: one deterministic camera binding engine and one process entrypoint (`process.view_bind`) used by control-plane emitted intents; legacy process IDs become adapters only.

## Truth Access Risk Areas for Camera/UI Decisions

- `tools/xstack/sessionx/observation.py`
  - Camera viewpoint currently derived from `universe_state.camera_assemblies` via `_camera_main`.
  - Observer watermark logic reads view mode and toggles truth overlay channels.
- This is acceptable only when policy-gated. Risk is policy drift if view/epistemic rules are split across runtime and observation code.

## Omniscient/Debug Overlay Surfaces

- `tools/xstack/sessionx/observation.py` supports:
  - `ch.truth.overlay.terrain_height`
  - `ch.truth.overlay.anchor_hash`
- Entitlement + policy checks exist, but current policy IDs and view IDs are fragmented (`view_mode` vs upcoming `view_policy` contract), creating leak-risk during future extension.

## Migration Plan to CTRL-6

1. Introduce canonical `view_policy` + `view_binding` schemas and registries, retaining `view_mode` as compatibility alias.
2. Extend negotiation kernel view axis to deterministic downgrade chain:
   - freecam -> third_person -> first_person
   - refuse if no lawful fallback.
3. Add `src/control/view/view_engine.py`:
   - single deterministic binding mutation path.
   - process entrypoint `process.view_bind`.
   - legacy camera processes delegate to this path.
4. Bind epistemic policy to view policy:
   - enforce allowed epistemic policy IDs per view policy.
   - add explicit inspection/reenactment level caps.
5. Enforce replay read-only mutation refusal in control plane:
   - `refusal.ctrl.replay_mutation_forbidden`.
6. Add RepoX/AuditX enforcement for:
   - camera bypass
   - epistemic leak patterns.

## Migration Safety Notes

- Keep deterministic ordering and canonical hashing unchanged for existing control decisions.
- Maintain backward compatibility for `view_mode_registry` consumers during transition.
- Do not allow renderer to access Truth; continue consuming PerceivedModel-only contracts.
