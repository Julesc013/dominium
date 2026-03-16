Status: DERIVED
Last Reviewed: 2026-03-01
Supersedes: none
Superseded By: none
Version: 1.0.0
Scope: CTRL-8 retro-consistency audit for deterministic temporary modifiers
Stability: provisional
Future Series: DOC-ARCHIVE
Replacement Target: legacy reference surface retained without current binding authority

# CTRL8 Retro Audit

## Canon/Invariant Frame
- `docs/canon/constitution_v1.md` A1, A2, A3, A7, A10.
- `docs/canon/glossary_v1.md` (AuthorityContext, Budget Envelope, Capability, Canonical).
- `AGENTS.md` process-only mutation, no hidden fallback, deterministic ordering.
- Target CTRL-8 invariants:
  - `INV-NO-ADHOC-TEMP-MODIFIERS`
  - `INV-EFFECT-USES-ENGINE`

## Audit Method
- Ad hoc modifier scan:
  - `rg -n "if .*damag|\\*=|multiplier|slow|blocked|degrad|visibility|smoke|flood|backlog" src tools -g "*.py"`
- Temporary state flag scan:
  - `rg -n "temporary|temp_|movement_constraints|alarm_state|paused_reason|degraded" src tools -g "*.py"`
- Control/refusal integration scan:
  - `rg -n "build_control_resolution|decision_log|downgrade|refusal" src tools -g "*.py"`

## Findings

### F1 - Interior movement restrictions are stored as domain-local derived flags
- Paths:
  - `src/interior/compartment_flow_engine.py`
  - `tools/xstack/sessionx/process_runtime.py`
- Current state:
  - Flood/pressure produce `movement_state` and `pressure_exposure_low` rows directly.
  - Runtime writes `state["interior_movement_constraints"]` with no unified effect artifact.
- Risk:
  - Temporary access restrictions exist as domain-specific side tables instead of common modifier semantics.

### F2 - Tool efficiency uses inline multiplier path
- Paths:
  - `src/interaction/task/task_engine.py`
- Current state:
  - `tool_effect.efficiency_multiplier` is applied directly during task delta calculation.
- Risk:
  - Temporary performance modifiers are encoded ad hoc; no shared stacking or expiration semantics.

### F3 - Maintenance backlog/wear multipliers are applied inline
- Paths:
  - `src/materials/maintenance/decay_engine.py`
- Current state:
  - Backlog-based multiplier impacts wear accumulation inside decay tick loop.
- Risk:
  - Degraded performance behavior exists without reusable effect records or consistent visibility policy.

### F4 - Control-plane decisions are not effect-aware yet
- Paths:
  - `src/control/control_plane_engine.py`
- Current state:
  - Decision log extensions normalize IR metadata but do not include effect influence metadata.
- Risk:
  - Refusals/downgrades caused by temporary constraints are not explicitly auditable as effect-driven outcomes.

### F5 - Diegetic warning channels do not include CTRL-8 warning set
- Paths:
  - `tools/xstack/sessionx/observation.py`
  - `data/registries/instrument_type_registry.json`
- Current state:
  - Interior alarms exist, but dedicated channels for speed-cap/visibility/access warnings are absent.
- Risk:
  - Effect visibility cannot be consistently projected through diegetic instrumentation.

## Migration Plan
1. Add canonical effect contracts:
   - `schema/control/effect.schema`
   - `schema/control/effect_type.schema`
   - `schema/control/stacking_policy.schema`
   - JSON schemas under `schemas/`.
2. Add deterministic registries:
   - `data/registries/effect_type_registry.json`
   - `data/registries/stacking_policy_registry.json`
3. Implement pure deterministic effect engine:
   - `src/control/effects/effect_engine.py`
   - deterministic stacking/expiration/query APIs.
4. Integrate process entrypoints:
   - `process.effect_apply`
   - `process.effect_remove`
   - refusal codes `refusal.effect.forbidden` and `refusal.effect.invalid_target`.
5. Integrate control-plane influence tracking:
   - record effect influence metadata in decision-log extensions.
   - refuse/transform actions when access/visibility effects apply.
6. Replace domain-local temporary modifiers with effect artifacts progressively:
   - interior flood/smoke/access restrictions
   - maintenance degraded state
   - tool efficiency modifiers.
7. Add enforcement and smell detection:
   - RepoX: `INV-NO-ADHOC-TEMP-MODIFIERS`, `INV-EFFECT-USES-ENGINE`
   - AuditX: `TempModifierSmell`, `EffectBypassSmell`.

## Invariants Mapped
- A1 Determinism primary
- A2 Process-only mutation
- A3 Law-gated authority
- A7 Observer/Renderer/Truth separation
- A10 Explicit degradation/refusal
