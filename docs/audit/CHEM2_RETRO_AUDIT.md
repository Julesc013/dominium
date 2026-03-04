# CHEM-2 Retro Consistency Audit

Status: AUDIT  
Last Updated: 2026-03-05  
Scope: CHEM-2 processing/refining/catalyst/quality preflight over current CHEM-1 + MAT + process registries.

## 1) Existing Batch Quality Mechanisms

Observed:

- `tools/xstack/sessionx/process_runtime.py`
  - `material_batches` rows exist with `quality_distribution` map and open `extensions`.
  - `process.material_transform_phase` mutates phase tags and preserves `parent_batch_ids`.
- No canonical `batch_quality` row set exists yet.
- No deterministic process-run state (`run_id`, `equipment_id`, tick window) exists yet.

Assessment:

- Batch provenance roots are present.
- Quality semantics are implicit and not yet standardized as gameplay-grade truth rows.

## 2) Recipe/Crafting Overlap Audit

Observed:

- Crafting and recipe surfaces exist (`process.craft.execute`, crafting docs/registries).
- CHEM-1 combustion path is already process + reaction-profile driven.
- No dedicated industrial processing runtime path currently exists for smelting/refining/polymerization/distillation/cracking.

Assessment:

- Chemistry processing is not implemented as recipe hacks in runtime yet.
- Governance risk remains if future processing is added through craft recipe pathways instead of reaction profiles.

## 3) Energy-Ledger Bypass Audit

Observed:

- CHEM-1 combustion uses `_record_energy_transformation_in_state(...)`.
- `transform.chemical_to_thermal` and `transform.chemical_to_electrical` are registered.
- No direct CHEM process-run pathway currently mutates energy totals.

Assessment:

- Existing combustion path is ledger-compliant.
- CHEM-2 must preserve this for all industrial process profiles.

## 4) Migration Plan (CHEM-2)

1. Introduce canonical processing schemas:
   - `schema/chem/process_equipment_profile.schema`
   - `schema/materials/batch_quality.schema`
   - `schema/chem/process_run_state.schema`
2. Extend reaction/rate registries with processing stubs and yield model registry.
3. Add constitutive model types:
   - `model_type.chem_yield_factor`
   - `model_type.chem_contamination_risk`
4. Add deterministic process handlers:
   - `process.process_run_start`
   - `process.process_run_tick`
   - `process.process_run_end`
5. Keep mass/energy mutation process-only and ledgered.
6. Persist output-batch traceability:
   - `input_batch_ids`, `reaction_id`, `equipment_id`, tick window.
7. Add explain/inspection/proof surfaces for low-yield and contamination outcomes.

## 5) Non-Goals Confirmed

- No molecule-level kinetics solver.
- No wall-clock dependence.
- No POLL solver requirement in CHEM-2 baseline.
