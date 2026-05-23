# Latest Warning Disposition

Current coordinator task: `AIDE-CHECKPOINT-LOOP-01`.

## Accepted Known Warnings

| Warning | Classification | Disposition |
| --- | --- | --- |
| Full CTest not run | full_gate_debt | Retained as T4/full-gate debt; this checkpoint/coordinator task ran lightweight validation only. |
| Dependency-direction strict warnings | dependency_direction_warning | Accepted because prior strict evidence reports `0` violations with known warnings. |
| AIDE review-packet reference warnings | review_ref_warning | Retired for this closeout; required review packet sections and refs are present and AIDE validate is PASS. |
| Stale AuditX output | stale_evidence_warning | Accepted as known RepoX warning; does not block narrow AIDE policy hardening. |
| Service conformance fixture/planned-support warnings | runtime_not_implemented_gap | Accepted; fixture/planned conformance does not imply runtime support. |
| Package runtime absent | runtime_not_implemented_gap | Accepted; package mount remains fixture/proof-level only. |
| Replay runtime absent | runtime_not_implemented_gap | Accepted; replay proof remains command-level fixture proof only. |
| Save/world/gameplay replay absent | runtime_not_implemented_gap | Accepted; not implemented by replay proof, workflow law, WorkUnit schemas, or checkpoint policy. |
| Barebones client is not playable | runtime_not_implemented_gap | Accepted; barebones client remains a no-content survival floor. |
| Workbench shell/rendered/native/TUI runtime absent | runtime_not_implemented_gap | Accepted; Workbench remains projection host, not authority. |
| Runtime composition/provider/module loading absent | runtime_not_implemented_gap | Accepted; not implemented by this checkpoint policy task. |

## New Or Updated Warnings

| Warning | Classification | Disposition |
| --- | --- | --- |
| Coordinator surfaces lagged behind committed AIDE policy work | stale_queue_state | Reconciled in this checkpoint/coordinator closeout without moving the queue backward. |
| `AIDE-CAPABILITY-REALITY-LEDGER-01` is already present in live history | prior_parallel_lane_evidence | Classified as completed live evidence; next open task is presentation/projection work. |
| Checkpoint policy exists but does not implement automation | planned_runtime_gap | Accepted; scheduler, branch automation, merge automation, promotion automation, and repair engine remain non-goals. |
| Limited parallel task execution is authorized only in bounded form | coordination_risk | Accepted with path isolation and explicit coordinator ownership requirements. Large parallel execution remains unauthorized. |

## Authorization

- Foundation Lock is `PASS_WITH_WARNINGS`.
- Product spine is complete through `PRODUCT-SPINE-REVIEW-01`.
- `AIDE-WORKFLOW-LAW-01` is complete.
- `AIDE-WORKUNIT-SCHEMA-01` is complete.
- `AIDE-DEV-MAIN-POLICY-01` is complete.
- `AIDE-CHECKPOINT-LOOP-01` is complete.
- `AIDE-CAPABILITY-REALITY-LEDGER-01` is present as completed live evidence.
- Limited parallel prompt generation is allowed.
- Limited parallel task execution is authorized only for path-isolated work with
  explicit coordinator ownership.
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
