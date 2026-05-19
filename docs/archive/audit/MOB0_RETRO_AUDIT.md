Status: DERIVED
Last Reviewed: 2026-03-16
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-ARCHIVE
Replacement Target: legacy reference surface retained without current binding authority

# MOB0 Retro-Consistency Audit

Status: AUDIT
Date: 2026-03-02
Scope: MOB-0 mobility constitution baseline audit.

## 1) Pre-existing movement and path systems

1. Deterministic movement processes already exist in `tools/xstack/sessionx/process_runtime.py`:
   - `process.agent_move` (movement intent path).
   - `process.body_move_attempt` (direct body delta application and collision resolution).
   - `process.agent_rotate` and `process.srz_transfer_entity` (mobility-adjacent control paths).
2. Order-based movement/pathing is present as a stub:
   - `order.move` and `order.migrate` are handled in `_tick_orders`.
   - Non-cohort/faction route execution currently refuses with `refusal.civ.order_requires_pathing_not_supported` and reason `micro_pathing_not_implemented`.

## 2) Train/road special-case code

1. `spec.track` has explicit branch logic in `process.spec_check_compliance`:
   - Derived `recommended_speed_cap_permille` is clamped and auto-emits/removes `effect.speed_cap` rows marked `auto_spec_track_speed_cap`.
2. Formalization target handling includes movement-surface enums in runtime:
   - `track|road|path|canal|tunnel|custom` normalization is embedded directly in process runtime paths.
3. Mechanics exports rail-like risk/speed values:
   - `src/mechanics/structural_graph_engine.py` computes `derailment_risk_permille` and `recommended_speed_cap_permille`.

## 3) Direct position mutation outside processes

1. Authoritative transform mutation appears process-scoped:
   - `camera["position_mm"]` and `camera["velocity_mm_per_tick"]` mutate under `process.camera_move` / `process.camera_teleport`.
   - `body["transform_mm"]` and `body["velocity_mm_per_tick"]` mutate under `process.body_move_attempt`.
2. No new non-process authoritative movement mutation hotspots were found in `src/` during this pass.
3. Non-authoritative edits exist and should remain non-authoritative:
   - `tools/xstack/sessionx/observation.py` camera quantization writes are PerceivedModel shaping.
   - `src/materials/blueprint_engine.py` transform writes are blueprint compile-time graph derivation, not live truth mutation.

## 4) Ad-hoc speed-limit and traction logic

1. Inline movement scalar composition currently exists in `_apply_body_move_attempt`:
   - `move_permille = min(speed_cap_permille, traction_permille)` with direct delta scaling.
2. Aircraft wind behavior uses string/type heuristics:
   - `is_aircraft` is inferred from `inputs`, `mobility_kind`, and ID substrings, then applies wind drift delta directly.
3. Inline speed policy coupling exists in field/spec paths:
   - `process.field_tick` computes `speed_cap_permille` from visibility (`visibility + 100`, clamped).
   - `spec.track` branch applies direct auto speed-cap effect emission.

## 5) Deprecation and migration plan toward MOB substrate

1. Route all movement modifiers through MOB policy resolution:
   - Keep Field/MECH as inputs, but remove inline mobility formulas from generic process runtime branches.
2. Replace mobility-kind string heuristics with registry-driven class/constraint metadata:
   - No ID-substring checks (for example `"aircraft"` in entity IDs).
3. Move route/path execution from CIV order stub handling to MOB networked substrate:
   - CIV order emits commitments/intents only; MOB owns meso routing/signal occupancy.
4. Keep process-only mutation invariant:
   - Movement remains committed through deterministic process branches only.
5. Preserve deterministic refusal pathways until MOB-1+ solvers land:
   - `refusal.civ.order_requires_pathing_not_supported` remains valid transitional behavior.
