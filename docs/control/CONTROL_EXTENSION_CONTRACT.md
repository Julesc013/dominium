Status: CANONICAL
Version: 1.0.0
Last Reviewed: 2026-03-01
Scope: CTRL domain-extension contract for MOB/SIG/DOM/INF/ECO/SCI integration

# Control Extension Contract

## Purpose

This contract defines how future domains integrate with control-plane resolution without creating side channels or bypass paths.

## Required Integration Steps

Any new user-facing domain capability must:

1. Register control actions in `data/registries/control_action_registry.json`.
2. Register required capabilities in `data/registries/capability_registry.json` and bind them through capability bindings.
3. Register domain effect types and stacking policies for temporary modifiers (when applicable).
4. Route all interaction-originated commands through `ControlIntent` and `build_control_resolution(...)`.
5. Use negotiation/fidelity kernels for downgrade/refusal handling under RS-5 constraints.
6. Emit deterministic decision-log artifacts for every control resolution (allowed or refused).
7. Declare topology dependency on `module:src/control/control_plane_engine.py` when control APIs are consumed.

## Compatibility and Proof Obligations

Domain extensions that touch control behavior must:

1. Preserve deterministic fingerprints for control decisions under fixed inputs.
2. Preserve replay/proof compatibility by keeping control artifact schemas versioned in CompatX.
3. Include control decision markers in proof artifacts for authoritative/hybrid and lockstep composite anchors.
4. Provide explicit migration route or refusal path for any control schema major-version bump.

## Forbidden Patterns

The following are forbidden:

1. Domain-specific control bypass (direct process dispatch from UI/tool interaction surfaces).
2. Direct invocation of `process.*` from public interaction entrypoints without control-plane mediation.
3. Inline downgrade branches in domain runtime logic that bypass negotiation kernel and decision logging.
4. Direct camera/view mutation outside control/view process paths.
5. Temporary modifier flags/multipliers outside the effect system.

## RepoX Enforcement Mapping

- `INV-CONTROL-PLANE-ONLY-DISPATCH`
- `INV-CONTROL-INTENT-REQUIRED`
- `INV-DOMAIN-CONTROL-REGISTERED`
- `INV-NO-DOMAIN-DOWNGRADE-LOGIC`
- `INV-NO-ADHOC-TEMP-MODIFIERS`
- `INV-VIEW-CHANGES-THROUGH-CONTROL`

## MOB-Ready Safe Extension Points

For MOB integration:

1. Add mobility actions as control action registry rows.
2. Express weather/terrain temporary limits as effect rows (`effect.speed_cap`, `effect.traction_reduction`, etc.).
3. Keep mobility output limiting as parameter modification at control/process boundaries, not truth mutation shortcuts.
4. Record all mobility-driven downgrades/refusals in DecisionLog and proof bundles.
