Status: DERIVED
Last Reviewed: 2026-03-07
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: canon-aligned documentation set for convergence and release preparation

# GR3 FAST Results

## Scope
- Profile: `FAST`
- Intent: repair-confirm the post-snapshot GR3 regressions without widening semantics.

## Commands Run
- `python tools/xstack/repox/check.py --repo-root . --profile FAST`
- `python tools/xstack/auditx/check.py --repo-root . --profile FAST`
- `python tools/xstack/testx/runner.py --repo-root . --profile FULL --cache off --subset test_breaker_trip_deterministic,test_breaker_trip_on_overload,test_control_resolution_deterministic,test_machine_operate_consumes_and_produces_batches,test_planning_requires_capability,test_provenance_anchor_validation,testx.reality.epistemic_invariance_on_expand,testx.net.pipeline_net_handshake_stage_authoritative,testx.net.pipeline_net_handshake_stage_srz_hybrid`
- `python tools/xstack/testx/runner.py --repo-root . --profile FULL --cache off --subset testx.control.plan_creation_deterministic,testx.control.manual_placement_via_plan`
- `python -c "from src.control.proof.control_proof_bundle import build_control_proof_bundle_from_markers; from tools.xstack.compatx.validator import validate_instance; ..."`

## Gate Outcome
- RepoX FAST: `PASS` on the clean post-commit tree (`findings=17`, all non-blocking warnings).
- AuditX FAST: `PASS`
- Impacted FAST/repair subset: `PASS` (11/11 targeted tests across control, system, electric, planning, reality, and net)
- Control proof bundle schema sanity: `PASS`

## Repaired FAST Blockers
- `tools/xstack/sessionx/process_runtime.py`
  - Renamed local state-machine maps that shadowed the imported `machine_rows_by_id(...)` helper and crashed machine/signal execution paths.
- `src/control/control_plane_engine.py`
  - Removed existence-based decision-log filename branching so identical control resolutions now emit stable `decision_log_ref` values.
- `src/system/system_expand_engine.py`
  - Revalidated the serialized state vector payload against the capsule provenance anchor before accepting expand.
- `src/electric/protection/protection_engine.py`
  - Compared overcurrent trips against the observed electrical measure instead of the normalized fault severity ratio.
- `schemas/control_proof_bundle.schema.json`
  - Added the already-emitted PROC/POLL/COMPILE/drift hash-chain fields to the schema so authoritative net boot no longer refuses valid proof bundles.
- `tools/xstack/testx/tests/plan_testlib.py`
  - Added deterministic planner capability bindings required by the stricter control-plane gate.
- `tools/xstack/testx/tests/lod_invariance_testlib.py`
  - Added deterministic quantity-dimension bindings required by the stricter conservation runtime.

## Notes
- No new domains, solvers, or mode-flag branches were introduced.
- Schema impact is additive-only: the control proof bundle schema now matches the runtime payload already in circulation.
- The hosted-size refusal introduced by the tracked SYS stress blob was cleared by replacing the raw archive at tip with compact manifests.
