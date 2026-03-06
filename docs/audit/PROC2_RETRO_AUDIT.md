# PROC2 Retro Consistency Audit

Date: 2026-03-06  
Scope: Yield/defect quality outcomes for ProcessDefinition and ProcessRun paths.

## Existing quality/yield behavior

- `CHEM-2` already contains deterministic quality outcomes through:
  - `src/models/model_engine.py` (`model_type.chem_yield_factor`, `model_type.chem_contamination_risk`)
  - `src/chem/process_run_engine.py` (`build_batch_quality_row`)
  - `schema/materials/batch_quality.schema`
  - `data/registries/yield_model_registry.json`
- Existing quality fields in truth rows:
  - `quality_grade`
  - `defect_flags`
  - `contamination_tags`
  - `yield_factor`

## Ad hoc risk check

- No direct inline yield writes were identified in `src/process/` (PROC-1 layer).
- CHEM runtime paths still carry CHEM-specific quality logic and should remain canonical until PROC-2 quality model hooks are integrated.

## Migration routing for PROC-2

- Introduce process-domain quality schemas:
  - `schema/process/yield_model.schema`
  - `schema/process/defect_model.schema`
  - `schema/process/process_quality_record.schema`
- Keep `batch_quality` as canonical output metadata and add explicit process traceability links.
- Extend ProcessDefinition to optionally declare:
  - `yield_model_id`
  - `defect_model_id`
- Evaluate quality at process run completion through constitutive models (default deterministic; optional named RNG policy-gated).

## Candidate existing paths to route through PROC-2

- CHEM process runs with output batches:
  - smelting/refining/polymerization/distillation/cracking paths
- Generic PROC step-graph outputs that produce `ref_type=batch`

## Audit conclusion

- Repository already has deterministic primitives and canonical quality carriers.
- PROC-2 can be implemented as a strict extension without semantic breaks to existing CHEM process behavior.
