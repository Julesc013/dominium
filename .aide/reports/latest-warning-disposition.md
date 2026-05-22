# Latest Warning Disposition

Current task: `AIDE-WORKFLOW-LAW-01`.

## Accepted Known Warnings

| Warning | Classification | Disposition |
| --- | --- | --- |
| Full CTest not run | full-gate debt | Retained as T4/full-gate debt; not required for this workflow-law slice. |
| Dependency-direction strict warnings | dependency-direction warning | Accepted because strict reports `0` violations and known warnings. |
| AIDE review-packet reference warnings | AIDE review-ref warning | Accepted existing packet reference warning when present; AIDE validate status is PASS. |
| Stale AuditX output | stale evidence warning | Accepted as known RepoX warning; does not block narrow governance progress. |
| Service conformance fixture/planned-support warnings | runtime-not-implemented gap | Accepted; fixture/planned conformance does not imply runtime support. |
| Package runtime absent | runtime-not-implemented gap | Accepted; package mount remains fixture/proof-level only. |
| Replay runtime absent | runtime-not-implemented gap | Accepted; replay proof remains command-level fixture proof only. |
| Save/world/gameplay replay absent | runtime-not-implemented gap | Accepted; not implemented by replay proof slice or workflow law. |
| Barebones client is not playable | runtime-not-implemented gap | Accepted; barebones client remains a no-content survival floor. |
| Workbench shell/rendered/native/TUI runtime absent | runtime-not-implemented gap | Accepted; Workbench remains projection host, not authority. |
| Runtime composition/provider/module loading absent | runtime-not-implemented gap | Accepted; not implemented by workflow law. |
| WorkUnit schemas not complete | follow-up candidate | Retained as `AIDE-WORKUNIT-SCHEMA-01`. |
| Pointer-width serialization audit not run | follow-up candidate | Retained as `POINTER-WIDTH-SERIALIZATION-AUDIT-01`. |

## New Warnings

None promoted to blocker.

## Authorization

- Foundation Lock is `PASS_WITH_WARNINGS`.
- Narrow governed product-spine slices are complete through barebones client shell.
- `AIDE-WORKFLOW-LAW-01` is complete with provisional law only.
- `AIDE-WORKUNIT-SCHEMA-01` is the next recommended task.
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
