Status: DERIVED
Last Reviewed: 2026-03-01
Supersedes: none
Superseded By: none
Scope: CTRL-5 Phase 0 retro-consistency audit
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: canon-aligned documentation set for convergence and release preparation

# CTRL5 Retro-Consistency Audit

## Canon Inputs
- `docs/canon/constitution_v1.md`
- `docs/canon/glossary_v1.md`
- `docs/control/CONTROL_PLANE_CONSTITUTION.md`
- `docs/contracts/refusal_contract.md`

## Audit Method
- Domain-local fidelity downgrade scan:
  - `rg -n "_resolve_fidelity|desired_fidelity|fidelity_achieved|micro -> meso|budget_refusal_code|strict_budget" src/materials src/inspection tools/xstack/sessionx/process_runtime.py -g "*.py"`
- Domain-local cost envelope checks scan:
  - `rg -n "max_cost_units|max_micro_parts|max_inspection_cost_units_per_tick|inspection_runtime_budget_state|fair_share|budget_allocated" src/materials src/inspection tools/xstack/sessionx/process_runtime.py -g "*.py"`
- Negotiation vs dedicated fidelity routing scan:
  - `rg -n "negotiate_request\(|arbitrate_fidelity_requests\(" src tools -g "*.py"`

## Findings

### F1 - MAT-9 still performs domain-local fidelity downgrade through negotiation kernel calls
- Paths:
  - `src/inspection/inspection_engine.py` (`_resolve_fidelity`)
  - `tools/xstack/sessionx/process_runtime.py` (`_execute_inspection_snapshot_process`)
- Current state:
  - inspection request fidelity is normalized and downgraded in domain flow.
  - per-tick inspection fair-share budget logic is separate from reusable fidelity subsystem.
- Risk:
  - fidelity arbitration behavior can drift between inspection call paths and other domains.

### F2 - MAT-7 materialization performs inline fidelity/budget downgrade
- Path:
  - `src/materials/materialization/materialization_engine.py` (`materialize_structure_roi`)
- Current state:
  - materialization uses inline negotiation-driven budget checks and truncates micro candidate set locally.
  - downgrade semantics are embedded in MAT-7 implementation details.
- Risk:
  - domain-specific downgrade logic can diverge from ranked fairness and future MOB fidelity requests.

### F3 - MAT-8 reenactment fidelity degradation is implemented directly in commitment engine
- Path:
  - `src/materials/commitments/commitment_engine.py` (`build_reenactment_artifact`)
- Current state:
  - micro/meso/macro degradation is computed directly from local cost formulas.
  - refusal logic is local and not represented as reusable fidelity allocation artifact.
- Risk:
  - cross-domain fidelity policy consistency and proof reporting are fragmented.

### F4 - Direct cost-unit checks remain outside dedicated fidelity subsystem
- Paths:
  - `src/materials/materialization/materialization_engine.py`
  - `src/materials/commitments/commitment_engine.py`
  - `src/inspection/inspection_engine.py`
  - `tools/xstack/sessionx/process_runtime.py`
- Current state:
  - domains perform local `max_cost_units`/`max_micro_parts` handling and refusal/degrade decisions.
- Risk:
  - RS-5 budget behavior remains deterministic but duplicated and not centrally auditable for fidelity requests.

## Migration Plan to Unified Fidelity Subsystem
1. Add canonical schemas for `fidelity_request`, `fidelity_allocation`, and `budget_allocation_record` + CompatX entries.
2. Implement `src/control/fidelity/fidelity_engine.py` with deterministic ordering, downgrade chain, and fairness policies (`default`, `rank_fair`, `singleplayer_relaxed`).
3. Migrate domain request paths:
   - MAT-7 materialization must call fidelity engine before micro instantiation.
   - MAT-9 inspection arbitration must use fidelity engine outputs for resolved fidelity/cost.
   - MAT-8 reenactment must resolve fidelity through fidelity engine, not inline downgrade code.
4. Persist deterministic fidelity allocation artifacts for auditing/replay (`state` decision artifacts + decision-log hooks).
5. Add RepoX + AuditX enforcement for "no domain-local fidelity downgrade" and "fidelity uses engine".
6. Add TestX coverage for deterministic allocation, downgrade chain, ranked fairness, envelope cap, and migration equivalence.

## Invariants Mapped
- A1 Determinism primary (`constitution_v1.md` §3 A1)
- A2 Process-only mutation (`constitution_v1.md` §3 A2)
- A3 Law-gated authority (`constitution_v1.md` §3 A3)
- A10 Explicit degradation/refusal (`constitution_v1.md` §3 A10)
