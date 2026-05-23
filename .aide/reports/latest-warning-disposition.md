# Latest Warning Disposition

Current coordinator task: `PRESENTATION-CONTRACT-01`.

## Accepted Known Warnings

| Warning | Classification | Disposition |
| --- | --- | --- |
| Full CTest not green | full_gate_debt | Retained as T4/full-gate debt; narrow product-spine work uses fast strict and targeted validators. |
| Stale full-gate tests expect retired roots/contracts | stale_full_gate_contract | Routed by `FULL-GATE-LEGACY-TEST-ROUTE-01` for the known active full-gate tests; old roots must not be recreated to satisfy remaining evidence. |
| Foundation Lock remains PASS_WITH_WARNINGS | foundation_warning | Accepted; it authorizes only narrow governed product-spine slices. |
| Stale AuditX output | stale_evidence_warning | Accepted as known RepoX warning; not hidden. |
| Workbench shell absent | runtime_not_implemented_gap | Accepted; `PRESENTATION-CONTRACT-01` is contract-only and `WORKBENCH-SHELL-READONLY-01` remains a later task. |
| Renderer/native GUI absent | runtime_not_implemented_gap | Accepted; presentation law does not implement rendered or native runtime surfaces. |
| Provider/package/module runtime absent | runtime_not_implemented_gap | Accepted; provider runtime, package runtime, and runtime module loader remain blocked. |
| Gameplay/embodiment/materialization absent | runtime_not_implemented_gap | Accepted; future Universe Explorer work starts as read-only inspection, not gameplay. |

## New Or Updated Warnings

| Warning | Classification | Disposition |
| --- | --- | --- |
| Presentation descriptors are contract-only | planned_runtime_gap | Accepted; validator forbids claiming runtime implementation here. |
| Read-only inspection is a contract target, not a product UI | product_spine_gap | Accepted; next task is projection conformance before Workbench shell or Universe Explorer implementation. |
| No-modal-loading is specified but not implemented | future_proof_required | Accepted; future tasks must prove pending/degraded states and non-blocking behavior before visual explorer claims. |

## Maintenance Update: FULL-GATE-LEGACY-TEST-ROUTE-01

| Warning | Classification | Disposition |
| --- | --- | --- |
| Active full-gate tests required retired paths | repaired_full_gate_route | Known active expectations for `game/rules`, `contracts/schemas`, `data/profiles`, `libs/appcore`, `docs/app`, `docs/platform`, `docs/render`, `docs/repox`, `runtime/app`, `tools/modpack`, `tools/workspace`, and `tools/distribution` were routed to canonical paths. |
| Retired-root mentions remain in compatibility and structure guards | guard_or_compat_reference | Preserved; these references are compatibility metadata or negative canonical-structure enforcement, not active source requirements. |
| Full CTest is not claimed green | full_gate_debt | Accepted; targeted stale-root/full-gate subset passes, but full CTest was not rerun in this maintenance task. |

## Authorization

- Foundation Lock is `PASS_WITH_WARNINGS`.
- Product spine is complete through `PRODUCT-SPINE-REVIEW-01`.
- AIDE workflow, WorkUnit schema, dev/main policy, checkpoint loop, and
  capability reality ledger tasks are complete.
- `PRESENTATION-CONTRACT-01` is complete.
- Limited parallel prompt generation is allowed.
- Limited parallel task execution is authorized only for path-isolated work
  with explicit coordinator ownership.
- Large parallel execution remains blocked.
- Broad feature work remains blocked.

## Blocked Work

- `broad_workbench_ui = BLOCKED`
- `runtime_module_loader = BLOCKED`
- `provider_runtime = BLOCKED`
- `package_runtime = BLOCKED`
- `gameplay = BLOCKED`
- `renderer_implementation = BLOCKED`
- `native_gui = BLOCKED`
- `materialization_engine = BLOCKED`
- `release_publication = BLOCKED`
