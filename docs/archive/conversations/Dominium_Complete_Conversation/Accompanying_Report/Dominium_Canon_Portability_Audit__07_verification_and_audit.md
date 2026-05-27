# SELF-AUDIT AND REVISION — Dominium Canon, Repository Alignment, and Portability Doctrine

## 32. Adversarial Self-Audit

| Issue | Severity | Correction needed | Correction applied? | Residual risk |
| --- | --- | --- | --- | --- |
| Full hidden transcript unavailable | High | Mark coverage partial and avoid pretending complete extraction | Yes | Some prior context may be missing |
| Repo state may have changed or connector evidence partial | High | Add verification queue for current tree/tests | Yes | Needs local checkout or GitHub tree API |
| Assistant recommendations might be mistaken for user decisions | High | Separate decisions, inferences, rejected/options, tasks | Yes | Aggregator must preserve labels |
| Docs may be ahead of code | High | State docs/schema/code/test distinction repeatedly | Yes | Still needs runtime audit |
| Potential apps/client vs client path inconsistency | Medium | Add open question and verification item | Yes | Requires current repo tree validation |
| External examples not reverified in preservation task | Medium | Mark as verification item if used in spec book | Yes | External facts can stale |
| Over-compression risk | Medium | Create files with report/registers/spec/aggregator | Yes | Files still summarize, not full transcript |

## 33. Corrections Applied

- Marked access as partial rather than full.
- Added a verification item for current physical layout vs converged-layout docs.
- Kept assistant portability doctrine as recommendation/inference unless clearly accepted.
- Separated repo docs, schemas, code, and tests in maturity claims.
- Included specific risks about overclaiming implementation status.
- Added a reuse-proof workstream rather than claiming reuse is already proven.

## 34. Final Reliability Assessment

* Completeness rating: 4/5 for visible chat; lower for inaccessible prior hidden context.
* Reliability rating: 4/5 with explicit caveats.
* Human-readability rating: 4/5.
* Aggregation-readiness rating: 4/5 with caveats.
* Main uncertainty sources: current repo physical tree, latest validator/test status, full implementation state of survival/process runtime, older hidden context outside visible transcript.
* Manual review before merge: recommended.


## Verification Queue

| ID | Item requiring verification | Why verification is needed | Suggested source/type | Priority | Related workstream | Label |
| --- | --- | --- | --- | --- | --- | --- |
| VERIFY-01 | Current physical repo tree vs claimed converged `apps/` layout. | Potential doc/code inconsistency observed in this session. | Local checkout tree listing or GitHub tree API. | P0 | WORKSTREAM-04 | UNCERTAIN |
| VERIFY-02 | Current strict layout/root validator status and active exceptions. | Needed before claiming cleanup completion. | Run `tools/validators/check_repo_layout.py --strict` and root allowlist validators. | P1 | WORKSTREAM-04 | UNCERTAIN |
| VERIFY-03 | Survival process runtime implementation status. | Registry existence does not prove behavior. | Code search/local tests for process executor/handlers. | P1 | WORKSTREAM-06 | UNCERTAIN |
| VERIFY-04 | XStack/RepoX/TestX latest pass/fail status. | Earlier chat audit may be stale. | Current CI/local `scripts/dev/gate.py verify` and CTest outputs. | P1 | WORKSTREAM-02 | UNCERTAIN |
| VERIFY-05 | External examples cited in prior answer: Linux, SQLite, NASA cFS, SemVer. | External-world facts may have changed or were not reverified in this preservation task. | Official docs/web verification. | P2 | WORKSTREAM-03 | UNVERIFIED |
