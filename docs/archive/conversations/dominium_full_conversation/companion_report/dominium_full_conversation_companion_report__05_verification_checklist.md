# Verification Checklist and Audit — Dominium Companion Report

## Verification queue

1. Check `.aide/queue/current.toml` before generating or executing the next prompt.
2. Check whether `FULL-GATE-LEGACY-TEST-ROUTE-01` has already been run.
3. Check whether the current repo still reports `PRESENTATION-CONTRACT-01` as latest completed mainline task.
4. Check whether the six maintenance tasks remain the selected next sequence.
5. Verify C17/C++17 in live build files.
6. Verify current full CTest/T4 debt status.
7. Verify whether provider manifest/service/fence tasks already exist in repo.
8. Verify whether the previous preservation package is complete and not superseded.

## Self-audit

| Issue | Severity | Correction needed | Correction applied? | Residual risk |
|---|---|---|---|---|
| No raw complete transcript export | High | Mark coverage as partial-to-broad | Yes | Some early details may be missing |
| Live repo facts may be stale | High | Add verification queue | Yes | Must verify before action |
| Assistant suggestions could be mistaken for decisions | Medium | Label decisions and inferences | Yes | Some acceptance inferred from user agreement |
| Screenshots could be overinterpreted | Medium | Treat as visual references | Yes | Future visual spec should review them |
| Prior generated files may be superseded | Medium | Bundle but mark as supporting material | Yes | Future package may be needed |

## Reliability

- Completeness: 4/5
- Reliability: 4/5 for chat doctrine, 3/5 for live repo state
- Human-readability: 4/5
- Aggregation-readiness: 4/5

Manual review is recommended before merging into a master Project Spec Book.
