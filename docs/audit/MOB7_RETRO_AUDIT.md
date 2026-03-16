Status: DERIVED
Last Reviewed: 2026-03-16
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-ARCHIVE
Replacement Target: legacy reference surface retained without current binding authority

# MOB7 Retro-Consistency Audit

Date: 2026-03-02
Scope: MOB-7 micro free-motion enablement
Canonical refs: docs/canon/constitution_v1.md, docs/canon/glossary_v1.md, docs/mobility/MOBILITY_CONSTITUTION.md

## Findings

### Existing free-move logic beyond EB movement
- Existing authoritative free movement is centered on:
  - `process.agent_move` in `tools/xstack/sessionx/process_runtime.py`
  - `process.body_move_attempt` in `tools/xstack/sessionx/process_runtime.py`
- No dedicated mobility free-motion process exists yet for vehicle/agent micro free state rows.
- Current body movement path is process-gated and deterministic, but it is generic EB movement rather than a mobility-tiered free-motion solver.

### Ad-hoc friction/wind modifiers
- `_apply_body_move_attempt` contains inline traction/speed/wind application logic:
  - reads `traction_permille`, `max_speed_permille`, and `wind_drift_permille` effect values
  - includes aircraft heuristics (`is_aircraft` and body-id/name inference)
  - computes drift deltas inline
- This logic is deterministic and process-contained, but not yet MOB-7 canonicalized as a reusable micro free-motion solver path.

### Corridor handling logic
- GuideGeometry supports `geo.corridor2D` and `geo.volume3D` artifacts and render previews.
- No dedicated runtime enforcement path currently clamps/refuses free motion against corridor/volume bounds.
- No `constraint.follow_volume` token currently exists in mobility constraint type registry.

## Migration Plan to MOB-7 Substrate

1. Introduce canonical free-motion rows:
- `free_motion_states` with deterministic fingerprints and body references.

2. Introduce deterministic free-motion policy registries:
- `free_motion_policy_registry`
- `traction_model_registry`
- `wind_model_registry`

3. Add mobility free-motion process path:
- `process.mobility_free_tick`
- explicit ROI list required
- deterministic budget/degrade handling
- no wall-clock usage

4. Implement reusable free-motion solver module:
- deterministic accel/velocity integration
- field-sampled friction and wind drift application
- effect-aware speed caps/traction reduction
- corridor/volume clamp/refuse/warn handling

5. Integrate corridor/volume constraints:
- consume `geo.corridor2D`/`geo.volume3D` bounds
- validate/use `constraint.follow_corridor` and `constraint.follow_volume` through core constraint hooks

6. Preserve EB collision integration:
- free-motion updates apply through process runtime and invoke EB collision resolution
- no direct truth mutation outside process path

7. Add enforcement:
- RepoX invariants for ROI-only free motion, no ad-hoc friction/wind, and process-only position updates
- AuditX analyzer for direct velocity mutation

8. Add TestX coverage:
- deterministic free-motion stepping
- deterministic corridor clamp/refuse behavior
- friction/wind influence checks
- budget downgrade logging
- collision integration behavior

## Canon/Invariant Notes
- Upholds A1 determinism and A2 process-only mutation.
- Preserves A5 event-driven advancement.
- No runtime mode flags are introduced (A4).
