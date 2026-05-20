# Latest Warning Disposition

Current task: `MOD-PACK-TRUST-MODEL-01`.

## Accepted Known Warnings

- Full CTest remains T4 full/release proof debt and is not claimed green.
- Dependency-direction validator still reports existing active dependency debt
  from DEPENDENCY-DIRECTION-01.
- ABI public-header validator still reports provisional warning debt that blocks
  stable/frozen ABI promotion.
- Mod/pack trust law is initial and provisional.
- Existing pack trust metadata is inventoried but not migrated.
- Runtime mod loader and sandbox are not implemented.
- Native provider loading, dynamic loading, and signed provider assurance are not implemented.
- Package mounting, Workbench UI, and provider runtime behavior are not implemented.
- Portability matrix remains the next Foundation Lock task.

## Not Hidden

- No failing full CTest result is reclassified as normal-gate success.
- No dependency-direction violation is silenced or broadly excepted.
- No public surface, artifact, schema, protocol, command, provider, module,
  app, pack, save, replay, or release surface is promoted to stable.
- No active pack manifest is migrated or rewritten.
- No runtime mod loader, sandbox, external adapter launcher, native loader,
  Workbench UI, product behavior, gameplay, renderer, or native GUI is implemented.
- No silent permission escalation, silent overlay overwrite, silent compatibility,
  silent migration, or path-as-identity policy is introduced.

## Next

Next task: `PORTABILITY-MATRIX-01`.
