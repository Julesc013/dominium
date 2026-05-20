Status: DERIVED
Last Reviewed: 2026-05-21
Supersedes: none
Superseded By: none

# Foundation Lock

Foundation Lock is the repository decision gate that determines whether Dominium can leave the Foundation Lock queue and begin a first narrow governed product slice.

Current closeout result: BLOCKED.

Foundation Lock is not passed as of FOUNDATION-CLOSEOUT-01 because `python tools/validators/repo/check_dependency_directions.py --repo-root . --strict` reports active dependency-direction violations in required closeout scope.

## What It Means

Foundation Lock means the governance spine exists, validates in required scope, is documented, and is integrated with the normal fast strict proof gate. It allows only narrow product slices that obey the public surface, command, diagnostics, artifact, capability, provider, module, replacement, versioning, trust, and portability laws.

Foundation Lock does not mean full CTest is green, every compatibility corpus exists, every provider is implemented, every runtime trust rule is enforced, Workbench UI exists, or broad feature work is open.

## Required Layers

- Fast strict test tier.
- Public surface registry.
- API/ABI canon.
- Dependency direction law.
- Command/refusal/result surface law.
- Diagnostic and evidence registry.
- Artifact identity law.
- Schema/protocol evolution law.
- Capability/refusal law.
- Provider model.
- Module/workspace/app composition law.
- Replacement protocol.
- Version/deprecation law.
- Mod/pack trust model.
- Portability matrix.

## Closeout Decision

All required files for the 15 Foundation Lock layers are present. Most validators pass in strict and fixture scope. The dependency-direction validator fails with 358 violations and 38 warnings, so the lock cannot be declared closed.

Fast strict passes, including RepoX STRICT, CMake configure/build, and smoke CTest. It is not sufficient by itself to authorize the product slice while dependency-direction strict validation remains red.

## Allowed Work

- Repair the dependency-direction blocker under a focused repair task.
- Continue documentation and evidence updates that do not hide the blocker.
- Keep Queue B hardening planned but not a substitute for the blocker repair.

## Blocked Work

- `WORKBENCH-VALIDATION-SLICE-01` is not authorized yet.
- Broad feature work remains blocked.
- Workbench UI, runtime module loading, provider runtime, package runtime, gameplay, renderer, native GUI, release publication, and broad rewrites remain blocked.

## Feature Rules After Lock

When the lock eventually passes, future narrow slices must register public surfaces, expose typed commands, use diagnostic and refusal codes, preserve artifact identity, declare capabilities and providers, use module descriptors where applicable, and use the replacement protocol for rewrites.

Next repair task: `FOUNDATION-REPAIR-DEPENDENCY-DIRECTION-01`.
