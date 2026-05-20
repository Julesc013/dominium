# Latest Warning Disposition

Current task: `MODULE-COMPOSITION-LAW-01`.

## Accepted Known Warnings

- Full CTest remains T4 full/release proof debt and is not claimed green.
- Dependency-direction validator still reports existing active dependency debt from DEPENDENCY-DIRECTION-01.
- ABI public-header validator still reports provisional warning debt that blocks stable/frozen ABI promotion.
- Module/workspace/app composition law is initial and provisional.
- Current app, Workbench, runtime, pack, and tool files are inventoried but not migrated in this task.
- Runtime module loader, Workbench UI, App Composer, pack runtime, provider runtime, and module discovery runtime are not implemented.

## Not Hidden

- No failing full CTest result is reclassified as normal-gate success.
- No dependency-direction violation is silenced or broadly excepted.
- No module, workspace, app, pack, provider, capability, or Workbench surface is promoted to stable.
- No Workbench implementation, app implementation, pack runtime, or runtime module loader is rewritten.
- No release, package runtime, gameplay, renderer, native GUI, or Workbench behavior is implemented.
- No path identity, private tool call, or Workbench-authority policy is introduced.

## Next

Next task: `REPLACEMENT-PROTOCOL-01`.
