# Latest Warning Disposition

Current task: `PROVIDER-MODEL-01`.

## Accepted Known Warnings

- Full CTest remains T4 full/release proof debt and is not claimed green.
- Dependency-direction validator still reports existing active dependency debt from DEPENDENCY-DIRECTION-01.
- ABI public-header validator still reports provisional warning debt that blocks stable/frozen ABI promotion.
- Provider model is initial and provisional.
- Current providers, backends, Workbench modules, packs, and runtime systems are inventoried but not migrated in this task.
- Provider conformance suites are skeletal fixtures only.
- Runtime provider resolver, dynamic/native loading, renderer/platform fallback, package/profile runtime behavior, and Workbench presentation are not implemented.

## Not Hidden

- No failing full CTest result is reclassified as normal-gate success.
- No dependency-direction violation is silenced or broadly excepted.
- No provider, backend, capability, refusal, pack, or Workbench surface is promoted to stable.
- No current provider, renderer, platform, package, or Workbench behavior is rewritten.
- No release, package runtime, gameplay, renderer, native GUI, or Workbench behavior is implemented.
- No silent fallback or implementation-path provider identity policy is introduced.

## Next

Next task: `MODULE-COMPOSITION-LAW-01`.
