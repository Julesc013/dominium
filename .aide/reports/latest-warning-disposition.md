# Latest Warning Disposition

Current task: `REPLACEMENT-PROTOCOL-01`.

## Accepted Known Warnings

- Full CTest remains T4 full/release proof debt and is not claimed green.
- Dependency-direction validator still reports existing active dependency debt
  from DEPENDENCY-DIRECTION-01.
- ABI public-header validator still reports provisional warning debt that blocks
  stable/frozen ABI promotion.
- Replacement protocol is initial and provisional.
- Historical refactors are inventoried but not retroactively converted into full
  replacement packets.
- Runtime migration and rollback are not implemented.
- Version/deprecation law is not implemented in this task.

## Not Hidden

- No failing full CTest result is reclassified as normal-gate success.
- No dependency-direction violation is silenced or broadly excepted.
- No replacement, public surface, artifact, provider, module, schema, protocol,
  or ABI surface is promoted to stable.
- No actual implementation replacement, broad directory move, migration runtime,
  rollback runtime, Workbench UI, provider runtime, app behavior, release,
  gameplay, renderer, or native GUI work is implemented.
- No path identity, silent migration, silent fallback, or silent compatibility
  reinterpretation policy is introduced.

## Next

Next task: `VERSION-DEPRECATION-LAW-01`.
