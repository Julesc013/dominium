# POLL-3 Retro-Consistency Audit

Date: 2026-03-05
Scope: POLL stress/proof/regression envelope hardening over POLL-0/1/2.

## Inputs Audited
- `src/pollution/dispersion_engine.py`
- `src/pollution/exposure_engine.py`
- `src/pollution/compliance_engine.py`
- `src/pollution/measurement_engine.py`
- `tools/xstack/sessionx/process_runtime.py`
- `tools/pollution/tool_replay_dispersion_window.py`
- `tools/pollution/tool_replay_exposure_window.py`

## Audit Findings
1. Unbudgeted field update loops
- `evaluate_pollution_dispersion` already enforces deterministic cell budgets via `max_cell_updates_per_tick` and bucketing.
- Runtime path (`process.pollution_dispersion_tick`) records degrade rows, but POLL-specific stress envelope tooling and budget assertions are not yet present.
- Gap: no POLL stress harness currently validates bounded field workload at scale.

2. Exposure accumulation bypass risk
- Exposure state mutation is currently process-mediated through `process.pollution_dispersion_tick` + `evaluate_pollution_exposure_tick`.
- Existing guard rails (RepoX/AuditX E254) exist for direct exposure writes.
- Gap: no POLL-3 stress verification currently proves deterministic degradation order for exposure budgeting under pressure.

3. Compliance reports through SIG
- Compliance reports are emitted as REPORT artifacts in `process.pollution_compliance_tick`.
- SIG dispatch is attempted through `process_signal_send`; degraded dispatch is logged when channel missing.
- Gap: no dedicated POLL stress/proof envelope currently locks compliance report stability and dispatch behavior under heavy load.

4. Explain artifact input completeness
- POLL explain artifacts exist for dispersion/decay/exposure/compliance violation.
- Explain generation references expected inputs (threshold rows, source rows, compliance rows).
- Gap: no POLL-3 replay verifier currently checks proof/hash stability across stress windows that include degrade decisions and compliance flows.

## Migration and Hardening Plan
1. Add deterministic POLL stress scenario generator (`tool_generate_poll_stress`) covering industrial emissions, spills, fires, wind, subjects, sensors, and compliance schedules.
2. Add deterministic POLL stress harness (`tool_run_poll_stress`) with bounded-work assertions, deterministic ordering checks, and proof-hash summary.
3. Codify POLL degradation order under RS-5-like pressure and persist DecisionLog entries for every degradation action.
4. Add pollution mass-balance verification tool with declared proxy-mass residual bounds.
5. Add POLL replay-window verifier for stress outputs and explicit pollution proof hash-chain verification.
6. Add regression lock (`data/regression/poll_full_baseline.json`) with `POLL-REGRESSION-UPDATE` gate.
7. Extend RepoX/AuditX/TestX for POLL-3 envelope invariants.

## Risk Notes
- Concentration fields are meso proxies; strict mass conservation must be validated within declared tolerance rather than exact per-cell equality.
- Existing repository-wide strict-lane blockers are out of POLL scope and should not be conflated with POLL envelope correctness.
