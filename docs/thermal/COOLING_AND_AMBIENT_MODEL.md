Status: DERIVED
Last Reviewed: unknown
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: patched document aligned to current canon ownership and release scope

# Cooling And Ambient Model

## Patch Notes

- Current status: partially aligned to the Constitutional Architecture and release-freeze documentation set.
- Required updates: documentation surface exists, but current canon ownership is not explicit
- Cross-check with: `docs/audit/CANON_MAP.md` and `docs/audit/DOC_DRIFT_MATRIX.md`.


Status: CANONICAL  
Last Updated: 2026-03-03  
Scope: THERM-3 deterministic cooling systems and ambient coupling.

## 1) Ambient Coupling

Thermal nodes may be designated as ambient boundaries through deterministic metadata:

- `boundary_to_ambient` flag (node extensions or ambient-boundary rows)
- `ambient_coupling_coefficient` (permille-scaled conductance coefficient)
- `insulation_factor` (permille scaling)

Ambient temperature is sampled deterministically from FieldLayer-derived inputs for the current tick.

Canonical exchange rule:

`Q = k_eff * (T_node - T_ambient)`

where `k_eff = ambient_coupling_coefficient * insulation_factor / 1000`.

Positive `Q` removes heat from the node; negative `Q` adds ambient heat into the node.

## 2) Radiator / Heat Sink

Radiators and heat sinks are represented as assemblies backed by thermal nodes and model bindings.

Radiator exchange uses profile-driven parameters:

- `base_conductance`
- `forced_cooling_multiplier` (permille)

Forced cooling is a deterministic coefficient multiplier (fan/pump state), not CFD.

## 3) Insulation

Insulation modifies ambient exchange and conductive exchange via model output coefficients.

- Lower insulation factor reduces absolute ambient heat exchange.
- No direct hardcoded cooling branch is allowed outside model-driven outputs.

## 4) Tiering

- `T0`: simplified ambient bookkeeping exchange only.
- `T1`: graph conduction plus boundary/radiator coupling (this tier).
- `T2`: future ROI-only convection/diffusion detail.

## 5) Determinism and Budget

- Node ordering: `node_id` lexicographic.
- Model ordering: `binding_id` lexicographic.
- Budget degradation is deterministic:
  - evaluate ambient/radiator bindings by stride selection
  - defer deterministic subset and log reason code

No wall-clock sources are used.

## 6) Safety Coupling

- Overheat remains hazard + `safety.overtemp_trip` path.
- Optional escalation to `hazard.thermal_runaway` may trigger when repeated overtemp conditions persist.

## 7) Epistemics and UX

- Diegetic indicators: radiator hot/cold, fan state, ambient readout.
- Inspector/admin views can expose detailed ambient-coupling summaries per policy.
- Truth-level full thermal overlays remain policy-gated.
