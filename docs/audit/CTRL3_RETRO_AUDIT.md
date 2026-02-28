Status: DERIVED
Last Reviewed: 2026-03-01
Scope: CTRL-3 Phase 0 retro-consistency audit

# CTRL3 Retro-Consistency Audit

## Canon Inputs
- `docs/canon/constitution_v1.md`
- `docs/canon/glossary_v1.md`
- `docs/control/CONTROL_PLANE_CONSTITUTION.md`
- `docs/contracts/refusal_contract.md`

## Audit Method
- Control downgrade scan:
  - `rg -n "downgrade|degrade|resolved_vector|reasons|control_policy_id" src/control -g "*.py"`
- MAT-9 inspection downgrade/fallback scan:
  - `rg -n "_resolve_fidelity|desired_fidelity|strict_budget|budget_exceeded" src/inspection tools/xstack/sessionx -g "*.py"`
- MAT-7 materialization budget degrade scan:
  - `rg -n "materialize_structure_roi|strict_budget|max_micro_parts|truncated" src/materials tools/xstack/sessionx -g "*.py"`
- RS-5 arbitration scan:
  - `rg -n "reserve_inspection_budget|fair_share|budget_envelope|max_inspection_cost_units_per_tick" src/performance tools/xstack/sessionx -g "*.py"`

## Findings

### F1 - Control downgrade logic is embedded in control-plane implementation
- Paths:
  - `src/control/control_plane_engine.py`
- Current state:
  - Abstraction/view/fidelity downgrade decisions are computed inline in `build_control_resolution`.
  - Decision reasons exist (`downgrade_reasons`), but negotiation is not isolated as a reusable deterministic kernel.
- Impact:
  - Other domains cannot reuse the same deterministic downgrade/refusal arbitration without duplicating logic.

### F2 - MAT-9 inspection fidelity fallback is domain-local
- Paths:
  - `src/inspection/inspection_engine.py` (`_resolve_fidelity`, `build_inspection_snapshot_artifact`)
  - `tools/xstack/sessionx/process_runtime.py` (`_execute_inspection_snapshot_process`)
- Current state:
  - Requested fidelity is downgraded in domain code (`micro -> meso -> macro`) when budget/law constraints fail.
  - Fair-share arbitration and per-tick reservation are done separately in process runtime.
- Silent fallback observed:
  - Non-strict path downgrades fidelity without a shared kernel decision artifact.
  - Invalid desired fidelity token normalizes to `macro`.

### F3 - MAT-7 materialization budget degrade is domain-local
- Paths:
  - `src/materials/materialization/materialization_engine.py` (`materialize_structure_roi`)
  - `tools/xstack/sessionx/process_runtime.py` (`process.materialize_structure_roi`)
- Current state:
  - When requested parts exceed budget:
    - strict path refuses.
    - non-strict path truncates candidates and marks `truncated=True`.
- Silent fallback observed:
  - Non-strict truncation is local to MAT-7 and not produced by shared negotiation logic.

### F4 - RS-5 inspection budget arbitration is split from control negotiation
- Paths:
  - `src/performance/cost_engine.py` (`reserve_inspection_budget`)
  - `tools/xstack/sessionx/process_runtime.py` (`_execute_inspection_snapshot_process`)
- Current state:
  - Budget envelope fair-share and reservation checks are deterministic but isolated from control-plane negotiation.
  - Arbitration outcomes are not currently emitted as canonical per-axis negotiation artifacts.

## Migration Plan to Negotiation Kernel
1. Add canonical negotiation contracts (`negotiation_request`, `negotiation_result`, `downgrade_entry`) and upgrade DecisionLog schema.
2. Implement deterministic `src/control/negotiation/negotiation_kernel.py` with fixed axis order:
   - abstraction -> view -> epistemic -> fidelity -> budget
3. Replace control-plane inline downgrade logic with kernel invocation.
4. Replace MAT-9 fidelity fallback with kernel negotiation result (no inline downgrade policy).
5. Replace MAT-7 budget truncate decision path with kernel arbitration output (engine enforces negotiated allocation only).
6. Route RS-5 inspection arbitration through kernel budget negotiation helper while preserving deterministic reservation semantics.
7. Emit full canonical decision log rows for downgraded/refused outcomes and include in proof hooks.

## Invariants Mapped
- A1 Determinism primary (`constitution_v1.md` §3 A1)
- A2 Process-only mutation (`constitution_v1.md` §3 A2)
- A3 Law-gated authority (`constitution_v1.md` §3 A3)
- A10 Explicit degradation/refusal (`constitution_v1.md` §3 A10)

