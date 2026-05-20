# Latest Warning Disposition

Current task: `DIAGNOSTIC-CODE-REGISTRY-01`.

## Accepted Known Warnings

- Full CTest remains T4 full/release proof debt and is not claimed green.
- Dependency-direction validator still reports existing active dependency debt
  from DEPENDENCY-DIRECTION-01.
- ABI public-header validator still reports provisional warning debt that blocks
  stable/frozen ABI promotion.
- The diagnostic registry is initial and provisional.
- Runtime diagnostic dispatch is not implemented by this task.
- Workbench diagnostic presentation is not implemented by this task.
- Capability/refusal law and artifact identity law remain later tasks.

## Not Hidden

- No failing full CTest result was reclassified as normal-gate success.
- No dependency-direction violation was silenced or broadly excepted.
- No diagnostic code was promoted to stable.
- No release, package runtime, gameplay, renderer, or Workbench behavior was
  implemented.

## Next

Next task: `ARTIFACT-IDENTITY-LAW-01`.
