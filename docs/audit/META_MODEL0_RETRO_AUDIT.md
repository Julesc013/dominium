# META-MODEL-0 Retro Consistency Audit

Status: DRAFTED
Last Updated: 2026-03-03
Scope: Identify existing deterministic response logic that should migrate to ConstitutiveModel entries.

## 1) Existing Model-Like Parameter Systems

### 1.1 Wear multipliers and degradation curves
- `src/mobility/maintenance/wear_engine.py`
  - deterministic wear accumulation scaling by traffic/load/environment.
  - includes explicit wear-ratio -> modifier formulas (track/vehicle degradation).
- `src/mobility/micro/constrained_motion_solver.py`
  - derail threshold incorporates wear and maintenance multipliers.

### 1.2 Friction and traction multipliers
- `src/fields/field_engine.py`
  - traction and corrosion risk derivations from field values.
- `src/mobility/micro/free_motion_solver.py`
  - friction -> acceleration scaling and traction reduction in free-motion updates.
- `src/mobility/micro/constrained_motion_solver.py`
  - friction-informed derail threshold scaling.

### 1.3 Signal attenuation/loss policies
- `src/signals/transport/channel_executor.py`
  - per-hop attenuation and loss decisions from edge/channel policy.
- `src/signals/transport/transport_engine.py`
  - policy parsing and deterministic attenuation/loss parameter handling.

### 1.4 Derailment threshold policies
- `src/mobility/micro/constrained_motion_solver.py`
  - lateral acceleration and threshold checks are deterministic but embedded as inline response equations.

## 2) Duplicated Response Logic Candidates

The following response classes appear in multiple series and should converge on reusable ConstitutiveModel definitions:

- field-scaled multipliers (`friction`, `moisture`, `visibility`, `wind`, `radiation`)
- threshold comparison models (`derail`, `wear`, `signal quality`)
- nonlinear adjustment curves (caps, clamps, linearized slopes)
- policy-weighted environment modifiers (maintenance/wear/quality)

## 3) Migration Plan (No Runtime Semantic Change in META-MODEL-0)

1. Introduce constitutional model contract and catalog naming first (this series).
2. Add governance enforcement in warn mode:
   - RepoX `INV-REALISM-DETAIL-MUST-BE-MODEL`
   - AuditX `InlineResponseCurveSmell`
3. During META-MODEL-1+:
   - define schemas for model definitions and bindings
   - create deterministic evaluation engine + cache key contract
   - migrate inline response formulas to registered model IDs
4. Keep old formula paths as compatibility shims only during migration windows, then deprecate.

## 4) Risk Notes

- No direct nondeterminism found in current response logic; primary risk is architectural drift and duplication.
- Existing logic is deterministic but not uniformly registry-addressable, making future domain expansions harder to govern.
