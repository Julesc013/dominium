Status: DERIVED
Last Reviewed: unknown
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: canon-aligned documentation set for convergence and release preparation

# CHEM-3 Retro Consistency Audit

Date: 2026-03-05
Scope: Corrosion, fouling, scaling, and chemical degradation baseline preflight.

## Inputs Audited
- `tools/xstack/sessionx/process_runtime.py`
- `src/models/model_engine.py`
- `src/chem/process_run_engine.py`
- `data/registries/reaction_profile_registry.json`
- `data/registries/constitutive_model_registry.json`
- `data/registries/coupling_contract_registry.json`
- `data/registries/core_hazard_type_registry.json`

## Findings
1. Existing wear/corrosion behavior is partial and domain-local.
- Generic hazard IDs exist (`hazard.corrosion.basic`, `hazard.wear.general`), but there is no CHEM-owned degradation state substrate for deterministic cross-domain corrosion/fouling/scaling tracking.

2. Pipe-loss and conductance degradation coupling is not CHEM-declared.
- FLUID and THERM have independent model hooks; CHEM-3 coupling contracts for degradation-driven reduction are not yet declared.

3. CHEM process paths (CHEM-1/CHEM-2) are present and ledger-safe.
- Combustion and process-run pathways are process-driven and energy-ledgered.
- No immediate direct energy-bypass discovered in CHEM paths.

4. No dedicated degradation proof chains exist.
- Proof surfaces include combustion/process-run chains, but no CHEM degradation chain or maintenance-action chain.

5. No dedicated CHEM-3 maintenance actions are registered in process runtime.
- Existing maintenance process exists (`process.maintenance_perform`) but no CHEM-specific cleaning/coating/replacement process family.

## Migration Plan
1. Introduce CHEM-3 schemas/registries:
- `degradation_state`
- `degradation_profile`
- degradation kind/profile registries.

2. Add CHEM constitutive model types:
- corrosion rate
- fouling rate
- scaling rate.

3. Add deterministic CHEM degradation engine and runtime process handlers:
- `process.degradation_tick`
- `process.clean_heat_exchanger`
- `process.flush_pipe`
- `process.apply_coating`
- `process.replace_section`.

4. Route cross-domain impacts through declared effects/hazards and coupling contracts only.

5. Extend proof/replay with degradation and maintenance hash chains.

6. Add strict enforcement and tests for model-only degradation discipline.

## Risk Notes
- Coupling adjustments must remain derived/process-mediated; no direct FLUID/THERM/MECH state mutation.
- Deterministic ordering must be target-sorted and kind-sorted each tick.
- Null boot must remain valid with empty degradation registries.
