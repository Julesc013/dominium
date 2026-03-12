Status: DERIVED
Last Reviewed: unknown
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: canon-aligned documentation set for convergence and release preparation

# FIELD1 Retro-Consistency Audit

Status: AUDIT
Date: 2026-03-01
Scope: FIELD-1 Global Field Substrate onboarding.

## Findings

1. Ad-hoc temporary weather/friction style modifiers are currently represented through direct effect writes and interior flow side-effects in `tools/xstack/sessionx/process_runtime.py`.
   - Existing inline patterns include smoke-driven visibility writes and access restrictions in `process.compartment_flow_tick`.
   - Migration target: derive these via `FieldLayer` sampling plus effect triggers.

2. Canonical field substrate exists but remaining inline logic still appears outside strict field-query paths.
   - `src/fields/field_engine.py`, `schema/fields/*`, and field registries are present.
   - Existing worldgen field payloads under `data/packs/.../fields.json` require explicit process routing to become authoritative runtime inputs.

3. Instrumentation has partial weather-like warnings but no formal field instrument channels.
   - Existing channels: `ch.diegetic.warning.speed_cap`, `...low_visibility`, `...restricted_access`.
   - Missing channels: field thermometer/hygrometer/dosimeter/wind/visibility indicators.

4. Render/observation currently has no first-class field query abstraction.
   - Risk: future direct render hacks for wind/visibility if not enforced.

## Migration Plan

1. Introduce strict schemas and registries for field type and field update policy.
2. Add deterministic `field_engine` with:
   - macro cell store
   - deterministic update ordering
   - tick-only update semantics
   - deterministic budget degradation
3. Add process path `process.field_tick` and state normalization/persistence in process runtime.
4. Route mobility/mechanics/interior interactions through field queries and effect emission.
5. Add diegetic field instruments/channels and epistemic redaction hooks.
6. Add RepoX/AuditX blockers for ad-hoc weather/temperature/friction logic.
7. Refactor remaining inline weather logic to field-query + effect composition.

## Deprecation Targets

- Inline ad-hoc visibility/friction/weather calculations outside `src/fields/field_engine.py` and approved process handlers.
- Future direct UI/render weather branches that bypass control/effect/field process path.
