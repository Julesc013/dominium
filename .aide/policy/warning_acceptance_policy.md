Status: DERIVED
Last Reviewed: 2026-05-22
Task: AIDE-WORKFLOW-LAW-01
Stability: provisional
Binding Sources: `.aide/reports/latest-warning-disposition.md`, `.aide/policies/promotion-rules.yaml`, `docs/repo/FOUNDATION_LOCK.md`

# AIDE Warning Acceptance Policy

## Core Rules

- Warnings must be classified.
- Warnings may be accepted on `dev` if known, bounded, and recorded.
- Warnings may not be hidden.
- Warnings must not be upgraded to `PASS clean`.
- Warning acceptance for `main` requires checkpoint policy.
- Full CTest debt remains explicit unless resolved.
- Fixture-only or planned implementation warnings must not be called
  implemented.

## Warning Classes

| Class | Dev Acceptance | Main Acceptance | Notes |
| --- | --- | --- | --- |
| `full_gate_debt` | Allowed when not required by task. | Requires checkpoint disposition. | Full CTest remains T4 debt. |
| `dependency_direction_warning` | Allowed with `0` violations. | Requires strict gate evidence. | Warning count must stay visible. |
| `review_ref_warning` | Allowed if AIDE validate still passes. | Requires review packet disposition. | Do not hide missing refs. |
| `stale_evidence_warning` | Allowed for narrow progress. | Requires refreshed evidence or explicit acceptance. | Stale AuditX output remains known debt. |
| `runtime_not_implemented_gap` | Allowed only when task is docs/contract/fixture/proof-level. | Not a support claim. | Package/replay/provider/runtime gaps stay blocked. |
| `planned_schema_gap` | Allowed as follow-up. | Not promotable as implemented. | WorkUnit schemas are next. |
| `new_warning` | Must be classified before acceptance. | Not accepted without checkpoint review. | Unknown warnings are not clean passes. |

## Status Wording

Use `PASS_WITH_WARNINGS` when warnings are accepted. Use `PASS` only when the
task's validation and warning policy have no known accepted warnings in scope.

Do not use clean wording for:

- unrun full CTest
- stale generated evidence
- fixture-only support
- planned implementation
- missing runtime/product features
