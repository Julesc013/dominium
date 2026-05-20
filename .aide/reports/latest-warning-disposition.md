# Latest Warning Disposition

Current task: `VERSION-DEPRECATION-LAW-01`.

## Accepted Known Warnings

- Full CTest remains T4 full/release proof debt and is not claimed green.
- Dependency-direction validator still reports existing active dependency debt
  from DEPENDENCY-DIRECTION-01.
- ABI public-header validator still reports provisional warning debt that blocks
  stable/frozen ABI promotion.
- Version/deprecation law is initial and provisional.
- Existing version-like surfaces are inventoried but not migrated.
- Runtime migration and release promotion gates are not implemented.
- Compatibility corpus is not populated.
- Mod/pack trust model remains the next Foundation Lock task.

## Not Hidden

- No failing full CTest result is reclassified as normal-gate success.
- No dependency-direction violation is silenced or broadly excepted.
- No public surface, artifact, schema, protocol, command, provider, module,
  app, pack, save, replay, or release surface is promoted to stable.
- No active surface is deprecated, retired, removed, or migrated.
- No runtime migration, release promotion, Workbench UI, product behavior,
  gameplay, renderer, native GUI, or mod/pack trust behavior is implemented.
- No silent compatibility, silent migration, or path-as-identity policy is introduced.

## Next

Next task: `MOD-PACK-TRUST-MODEL-01`.
