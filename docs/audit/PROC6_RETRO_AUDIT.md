# PROC6 Retro-Consistency Audit

Status: AUDIT
Last Updated: 2026-03-06
Scope: PROC-6 drift detection, escalation, and revalidation readiness.

## Existing Drift-Relevant Signals

Available deterministic inputs identified in current runtime:

- QC outcomes:
  - `qc_result_record_rows`
  - fail/pass rate summaries in `process_run_engine`
- Quality/maturity metrics:
  - `yield_mean`, `yield_variance`, `defect_rate`, `qc_pass_rate`
  - `env_deviation_score`, `calibration_deviation_score`
- Environment snapshots:
  - `environment_snapshot_hash` carried in run traceability
- Tool condition:
  - quality input `tool_wear_permille`
- Entropy:
  - quality input `entropy_index`
- Reliability signals:
  - optional `reliability_failure_count` uplift path in drift helpers

## Existing Gaps

- Drift policy registry exists but is legacy-only (`warning/forced_expand/revocation` threshold fields) and lacks explicit weights/bands.
- No canonical `process_drift_state` or `drift_event_record` schema/rows yet.
- No deterministic revalidation trial scheduling records in process runtime state.
- Explain registry has `explain.drift_detected` but lacks `warning/critical/revalidation/capsule-invalidated-by-drift` contracts.
- Inspection registry does not yet expose dedicated drift/QC-escalation sections.

## Migration Plan

1. Add strict PROC-6 schemas:
   - `drift_policy`
   - `process_drift_state`
   - `drift_event_record`
2. Upgrade drift policy registry with:
   - weighted deterministic score inputs
   - threshold bands (`normal|warning|critical`)
   - QC escalation rules
   - deterministic revalidation trial count
   - retain legacy fields for backward compatibility
3. Integrate drift engine evaluation into `process_run_end`:
   - deterministic score/band rows
   - escalation/invalidation/revocation actions
   - revalidation scheduling and completion updates
4. Extend proof/replay:
   - drift/revalidation hash chains
   - replay verifier tool
5. Enforce via RepoX/AuditX and add PROC-6 TestX coverage.
