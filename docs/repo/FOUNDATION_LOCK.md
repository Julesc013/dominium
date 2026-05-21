Status: DERIVED
Last Reviewed: 2026-05-21
Supersedes: none
Superseded By: none

# Foundation Lock

Foundation Lock is the repository decision gate that determines whether Dominium can leave the Foundation Lock queue and begin a first narrow governed product slice.

Current repair result: READY_FOR_FOUNDATION-CLOSEOUT-02.

Foundation Lock is not yet declared closed by this document. `FOUNDATION-REPAIR-DEPENDENCY-DIRECTION-01` repaired the dependency-direction strict blocker and the lock must now be rerun by `FOUNDATION-CLOSEOUT-02`.

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

All required files for the 15 Foundation Lock layers are present. Most validators pass in strict and fixture scope.

`FOUNDATION-CLOSEOUT-01` was blocked because dependency-direction strict reported `358` violations and `38` warnings.

`FOUNDATION-REPAIR-DEPENDENCY-DIRECTION-01` now reports dependency-direction strict PASS with `0` violations and `68` warnings. Fast strict also passes, including RepoX STRICT, CMake configure/build, and smoke CTest.

This repair is not a closeout decision by itself. `FOUNDATION-CLOSEOUT-02` must rerun the closeout gate before any product slice is authorized.

## Allowed Work

- Run `FOUNDATION-CLOSEOUT-02`.
- Continue documentation and evidence updates that do not bypass closeout.
- Continue documentation and evidence updates that keep remaining warnings and full-gate debt visible.
- Keep Queue B hardening planned but not a substitute for the blocker repair.

## Blocked Work

- `WORKBENCH-VALIDATION-SLICE-01` is not authorized by this repair task.
- Broad feature work remains blocked.
- Workbench UI, runtime module loading, provider runtime, package runtime, gameplay, renderer, native GUI, release publication, and broad rewrites remain blocked.

## Feature Rules After Lock

When the lock eventually passes, future narrow slices must register public surfaces, expose typed commands, use diagnostic and refusal codes, preserve artifact identity, declare capabilities and providers, use module descriptors where applicable, and use the replacement protocol for rewrites.

Next task: `FOUNDATION-CLOSEOUT-02`.
