# Latest Warning Disposition

Current coordinator task: `AIDE-WORKUNIT-SCHEMA-01`.

## Accepted Known Warnings

| Warning | Classification | Disposition |
| --- | --- | --- |
| Full CTest not run | full_gate_debt | Retained as T4/full-gate debt; this schema task ran lightweight validation only. |
| Dependency-direction strict warnings | dependency_direction_warning | Accepted because prior strict evidence reports `0` violations with known warnings. |
| AIDE review-packet reference warnings | review_ref_warning | Accepted existing packet reference warnings; AIDE validate remains PASS with warnings. |
| Stale AuditX output | stale_evidence_warning | Accepted as known RepoX warning; does not block narrow AIDE schema hardening. |
| Service conformance fixture/planned-support warnings | runtime_not_implemented_gap | Accepted; fixture/planned conformance does not imply runtime support. |
| Package runtime absent | runtime_not_implemented_gap | Accepted; package mount remains fixture/proof-level only. |
| Replay runtime absent | runtime_not_implemented_gap | Accepted; replay proof remains command-level fixture proof only. |
| Save/world/gameplay replay absent | runtime_not_implemented_gap | Accepted; not implemented by replay proof, workflow law, or WorkUnit schemas. |
| Barebones client is not playable | runtime_not_implemented_gap | Accepted; barebones client remains a no-content survival floor. |
| Workbench shell/rendered/native/TUI runtime absent | runtime_not_implemented_gap | Accepted; Workbench remains projection host, not authority. |
| Runtime composition/provider/module loading absent | runtime_not_implemented_gap | Accepted; not implemented by this schema task. |
| Dev/main policy not complete | planned_schema_gap | Retained as `AIDE-DEV-MAIN-POLICY-01`. |
| Checkpoint loop policy not complete | planned_schema_gap | Retained as `AIDE-CHECKPOINT-LOOP-01`. |
| Capability reality ledger not complete | planned_schema_gap | Retained as `AIDE-CAPABILITY-REALITY-LEDGER-01`; only a small record schema exists. |

## New Warnings

| Warning | Classification | Disposition |
| --- | --- | --- |
| Pre-existing AIDE workflow-law/status files were dirty before this task | dirty_worktree_same_task / prior task evidence | Classified as compatible AIDE prerequisite evidence; no product/runtime paths were touched. |
| WorkUnit schemas exist but do not authorize large parallel execution | planned_schema_gap | Large parallel execution remains blocked pending dev/main policy, checkpoint policy, repair/resume policy, and path-isolated future task sets. |

## Authorization

- Foundation Lock is `PASS_WITH_WARNINGS`.
- Product spine is complete through `PRODUCT-SPINE-REVIEW-01`.
- `AIDE-WORKFLOW-LAW-01` is complete and remains governing policy.
- `AIDE-WORKUNIT-SCHEMA-01` is complete with `PASS_WITH_WARNINGS`.
- `AIDE-DEV-MAIN-POLICY-01` is the next recommended task.
- Limited parallel prompt generation is allowed.
- Limited parallel task execution is not authorized by this closeout.
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
- `release_publication = BLOCKED`
