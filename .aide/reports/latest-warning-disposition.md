# Latest Warning Disposition

Current coordinator task: `STATUS-RECONCILE-02`.

## Accepted Known Warnings

| Warning | Classification | Disposition |
| --- | --- | --- |
| Full CTest not run | full-gate debt | Retained as T4/full-gate debt; not required for this coordinator reconciliation. |
| Dependency-direction strict warnings | dependency-direction warning | Accepted because prior strict evidence reports `0` violations with known warnings. |
| AIDE review-packet reference warnings | AIDE review-ref warning | Accepted existing packet reference warnings when present; AIDE validate status remains non-blocking. |
| Stale AuditX output | stale evidence warning | Accepted as known RepoX warning; does not block narrow AIDE hardening. |
| Service conformance fixture/planned-support warnings | runtime-not-implemented gap | Accepted; fixture/planned conformance does not imply runtime support. |
| Package runtime absent | runtime-not-implemented gap | Accepted; package mount remains fixture/proof-level only. |
| Replay runtime absent | runtime-not-implemented gap | Accepted; replay proof remains command-level fixture proof only. |
| Save/world/gameplay replay absent | runtime-not-implemented gap | Accepted; not implemented by replay proof or AIDE workflow law. |
| Barebones client is not playable | runtime-not-implemented gap | Accepted; barebones client remains a no-content survival floor. |
| Workbench shell/rendered/native/TUI runtime absent | runtime-not-implemented gap | Accepted; Workbench remains projection host, not authority. |
| Runtime composition/provider/module loading absent | runtime-not-implemented gap | Accepted; not implemented by this reconciliation. |
| WorkUnit schemas not complete | follow-up candidate | Retained as `AIDE-WORKUNIT-SCHEMA-01`. |
| Dev/main policy not complete | follow-up candidate | Retained as `AIDE-DEV-MAIN-POLICY-01`. |
| Checkpoint loop policy not complete | follow-up candidate | Retained as a later AIDE hardening task. |
| Capability reality ledger not complete | follow-up candidate | Retained as a later AIDE hardening task. |

## New Warnings

| Warning | Classification | Disposition |
| --- | --- | --- |
| Requested handoff expected `AIDE-WORKFLOW-LAW-01` next, but live local history already contains that task as complete | sequencing/status mismatch | Non-blocking; queue was reconciled forward to `AIDE-WORKUNIT-SCHEMA-01` rather than backward to a completed task. |
| Unrelated AIDE workflow/schema residue remains dirty outside this task's allowed paths | unrelated dirty-worktree warning | Recorded as out-of-scope for `STATUS-RECONCILE-02`; not staged by this coordinator commit. |

## Authorization

- Foundation Lock is `PASS_WITH_WARNINGS`.
- Product spine is complete through `PRODUCT-SPINE-REVIEW-01`.
- `AIDE-WORKFLOW-LAW-01` is complete in live local history.
- `AIDE-WORKUNIT-SCHEMA-01` is the next recommended task.
- Limited parallel prompt generation is allowed.
- Limited parallel task execution is not yet authorized.
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
