Status: DERIVED
Last Reviewed: 2026-03-16
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: canon-aligned documentation set for convergence and release preparation

# FLUID1 Retro Consistency Audit

Status: BASELINE
Last Updated: 2026-03-04
Scope: FLUID-1 PipeNetworkGraph + F1 meso flow/head solve readiness.

## 1) Existing Pipe-Like Flow Logic

Repository scan over `src/`, `tools/xstack/sessionx/`, and registry payloads found:

- No dedicated `src/fluid/` network runtime existed before this pass.
- Core flow substrate exists in `src/core/flow/flow_engine.py` and is reusable.
- Existing domain-specific network engines are present for ELEC/THERM/MOB/SIG.
- No parallel bespoke fluid solver implementation was found.

## 2) INT/Compartment Flow Separation Check

Interior-scale flow logic remains under INT surfaces:

- `src/interior/compartment_flow_engine.py`
- `src/interior/compartment_flow_builder.py`

Conclusion:

- INT remains interior-scale (`air/smoke/flood/portal`) as expected.
- FLUID infrastructure-scale solver can be added without merging scales.
- Coupling boundary must remain contract-driven (`FLUID -> INT`) via declared model bindings.

## 3) Ad-hoc Pressure/Flooding Patterns

Static scan did not identify an existing FLUID domain runtime doing direct pressure-head solving.
Pressure-like handling currently appears in interior and observation layers, which are already covered by:

- RepoX: `INV-NO-ADHOC-PRESSURE-LOGIC`
- AuditX: `E219_INLINE_PRESSURE_SMELL`, `E220_ADHOC_VALVE_SMELL`

Migration note:

- Keep infrastructure pressure/head solve in FLUID engine only.
- Keep interior pressure semantics in INT and treat cross-scale interaction as explicit coupling.

## 4) Migration Decisions

- Introduce `FluidNetworkGraph` payload schemas for node/edge/tank state.
- Route F1 behavior through:
  - `FlowSystem` channels (`bundle.fluid_basic`)
  - `META-MODEL` constitutive outputs
  - SAFETY relief hook
- Preserve F0 fallback mode with deterministic downgrade logging.

## 5) Deprecation Notes

- No prior FLUID runtime path required deprecation in this phase.
- Any future direct valve/pressure logic outside model-engine mediated flow paths is non-compliant and should be treated as governance drift.
