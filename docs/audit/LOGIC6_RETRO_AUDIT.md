Status: DERIVED
Last Reviewed: unknown
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: canon-aligned documentation set for convergence and release preparation

## LOGIC-6 Retro Audit

Date: 2026-03-08
Scope: LOGIC compilation eligibility, proofability, and SYS collapse seams.

### Relevant Invariants
- `docs/canon/constitution_v1.md` A1 Determinism
- `docs/canon/constitution_v1.md` A2 Process-only mutation
- `docs/canon/constitution_v1.md` A9 Pack-driven integration
- `docs/canon/constitution_v1.md` A10 Explicit degradation and refusal
- `docs/canon/glossary_v1.md` canonical terminology binding

### Existing Eligibility Surface
- LOGIC-3 validation already classifies loops as `combinational`, `sequential`, or `mixed`, and supports `allow_compiled_only` policy resolution when a compiled proof reference is present on the binding.
- LOGIC-4 evaluation already operates on a deterministic `Sense -> Compute -> Commit -> Propagate` cycle where:
  - `SENSE` snapshots `port_in` signal values deterministically.
  - `COMPUTE` is pure over `(snapshot, explicit state_vector)`.
  - `COMMIT` and `PROPAGATE` remain authoritative and process-mediated.
- Because `COMPUTE` already consumes the per-tick sense snapshot rather than mutating topology during evaluation, compilation can target the exact per-tick relation:
  - current `port_in` snapshot
  - explicit element/system state vectors
  - deterministic outputs and next-state

### Network Classes Eligible For LOGIC-6
1. Loop-free combinational networks
   - Eligible for `compiled.reduced_graph`.
   - Eligible for `compiled.lookup_table` when bounded input width policy allows exhaustive enumeration.
2. Sequential networks with bounded state vectors
   - Eligible for `compiled.automaton` when bounded state exploration policy allows exhaustive exploration.
3. Mixed networks
   - Only eligible when policy permits compiled-only handling and an exact compiled proof is present.

### Existing Preconditions Confirmed
- State vectors are already explicit for LOGIC elements via LOGIC-2 element definitions and materialized instance definitions in LOGIC-4.
- Timing constraints and timing policy seams are already declared through LOGIC-5 timing policy, timing constraints, and explain surfaces.
- Generic COMPILE-0 already provides:
  - compiled model rows
  - validity domain rows
  - equivalence proof rows
  - compile request/result rows
  - `ref.compiled_model_verify` proof verification pathway
- SessionX already persists compile artifacts and proof hash chains generically.

### Integration Points
- LOGIC binding rows can carry compiled model references and proof references without schema breakage through `extensions`.
- LOGIC-4 evaluator can swap only the `COMPUTE` phase to compiled execution while preserving:
  - `COMMIT`
  - `PROPAGATE`
  - timing/oscillation/watchdog analysis
  - proof/replay surfaces
- SYS collapse seam exists through:
  - `build_system_macro_capsule_row`
  - `build_forced_expand_event_row`
  - macro model set and system template registries

### Existing Risks / Gaps Before This Pass
- No `process.logic_compile_request` yet.
- No logic-specific compile policy registry yet.
- No runtime preference for compiled execution in LOGIC-4 yet.
- No explicit explain artifact for compiled invalidation or logged fallback yet.
- No logic-specific replay tool comparing compiled vs L1 execution.

### Reserved Naming / Glossary Check
- No glossary conflict found for:
  - Logic
  - Signal
  - Carrier
  - State Vector
  - Compiled model
  - Proof
  - Macro capsule
- New identifiers in this pass should preserve existing canonical prefixes:
  - `compile.logic.*`
  - `process.logic_*`
  - `explain.logic_*`
  - `template.logic_*`

### Refactor Direction
- Reuse COMPILE-0 proof rows and validity-domain rows.
- Keep authoritative mutation in existing LOGIC-4 `COMMIT` and `PROPAGATE`.
- Route compile selection and fallback through explicit process/eval records.
- Reuse SYS forced-expand events for compiled invalidation and debug expansion.
