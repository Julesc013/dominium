Status: DERIVED
Last Reviewed: unknown
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: canon-aligned documentation set for convergence and release preparation

# PROC3 Retro-Consistency Audit

Status: AUDIT
Last Updated: 2026-03-06
Scope: PROC-3 QC sampling + inspection discipline baseline readiness.

## Existing Batch Quality Handling

- `src/process/process_run_engine.py` already emits deterministic:
  - `process_quality_record_rows`
  - `batch_quality_rows`
  - `process_quality_hash_chain`
  - `batch_quality_hash_chain`
- Quality modeling is currently run-completion scoped (PROC-2) and always evaluates for produced batches when quality models are declared.
- No QC sampling policy is currently applied at run completion.

## Existing Inspection/Measurement Paths

- Process step kind `measure` currently emits `artifact.process.measurement` observations in `process_run_tick`.
- POLL measurement path exists (`src/pollution/measurement_engine.py`) and is deterministic + artifact-based, but process-QC specific sampling decisions are not yet represented.
- Session/runtime inspection stack exists (inspection snapshot pipelines), but process QC pass/fail/rework outcomes are not represented as dedicated canonical process QC records.

## Ad-hoc / Implicit QC Gaps

- No first-class `qc_policy_id` on ProcessDefinition.
- No deterministic sampling strategy registry for process-quality inspection.
- No canonical `qc_result_record` rows in process run state/proof chain.
- No explicit deterministic decision trace for sampled vs non-sampled output batches.
- No process-native fail-action mapping (`reject`, `rework`, `accept_warning`, `quarantine`) in process-run closeout.

## Measurement Artifact Consistency

- Measurement artifacts are emitted for measure steps (`artifact.process.measurement`) and are already represented as derived observations.
- Gap: no canonical linkage from sampled QC decisions to their measurement observations and thresholds.

## Migration Notes to PROC-3

1. Add ProcessDefinition `qc_policy_id` (optional, policy-controlled).
2. Add QC policy/test-procedure schemas + registries.
3. Add deterministic `src/process/qc/qc_engine.py` for:
   - hash-based / every-N / risk-weighted sampling
   - deterministic threshold evaluation
   - canonical qc result row generation
4. Integrate QC evaluation in `process_run_end` without bypassing existing PROC-2 quality records.
5. Extend proof/replay with QC decision + result hash chains.

## Risk Notes

- Preserve deterministic ordering: batches by `batch_id`, tests by `test_id`.
- Preserve no-omniscience by storing sampled evidence only and attaching visibility hints for epistemic filtering.
- Keep `qc.none` viable so QC remains policy-gated and non-mandatory for null boot.
