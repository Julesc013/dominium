# Latest Warning Disposition

Current task: `CAPABILITY-REFUSAL-LAW-01`.

## Accepted Known Warnings

- Full CTest remains T4 full/release proof debt and is not claimed green.
- Dependency-direction validator still reports existing active dependency debt from DEPENDENCY-DIRECTION-01.
- ABI public-header validator still reports provisional warning debt that blocks stable/frozen ABI promotion.
- Capability/refusal law is initial and provisional.
- Current providers, backends, Workbench modules, packs, and runtime systems are inventoried but not migrated in this task.
- Compatibility corpus is not populated in this task.
- Runtime capability resolver, provider model, renderer/platform fallback, package/mod trust runtime, and Workbench presentation are not implemented.

## Not Hidden

- No failing full CTest result is reclassified as normal-gate success.
- No dependency-direction violation is silenced or broadly excepted.
- No capability, refusal, provider, pack, or backend surface is promoted to stable.
- No current provider, renderer, platform, package, or Workbench behavior is rewritten.
- No release, package runtime, gameplay, renderer, or Workbench behavior is implemented.
- No silent fallback or free-text-only refusal policy is introduced.

## Next

Next task: `PROVIDER-MODEL-01`.
