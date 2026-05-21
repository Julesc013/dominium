Status: DERIVED
Last Reviewed: 2026-05-21
Supersedes: none
Superseded By: none

# Foundation Lock

Foundation Lock is the repository decision gate that determines whether Dominium can leave the Foundation Lock queue and begin a first narrow governed product slice.

Current closeout result: PASS_WITH_WARNINGS.

`FOUNDATION-CLOSEOUT-02` reran the Foundation Lock gate after `FOUNDATION-REPAIR-DEPENDENCY-DIRECTION-01` and closed the lock with warnings.

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

All required files for the 15 Foundation Lock layers are present.

`FOUNDATION-CLOSEOUT-01` was blocked because dependency-direction strict reported `358` violations and `38` warnings.

`FOUNDATION-REPAIR-DEPENDENCY-DIRECTION-01` reports dependency-direction strict PASS with `0` violations and `68` warnings.

`FOUNDATION-CLOSEOUT-02` reports:

- dependency-direction strict: PASS with `0` violations and `68` warnings.
- Foundation validator matrix: PASS.
- AIDE doctor/validate/test/selftest/tools/roots/repo: PASS.
- RepoX STRICT: PASS with stale AuditX warning.
- fast strict: PASS, `32` commands, `272.607` seconds.
- CMake configure/build and smoke CTest: PASS through fast strict.
- full CTest: T4/full-gate debt, not run.

Foundation Lock is PASS_WITH_WARNINGS.

## Allowed Work

- Run `PORTABILITY-ARCH-POLICY-02`.
- Run `WORKBENCH-VALIDATION-SLICE-01` after the architecture-policy follow-up unless the operator explicitly chooses the product slice first.
- Continue documentation and evidence updates that do not bypass Foundation laws.
- Continue documentation and evidence updates that keep remaining warnings and full-gate debt visible.
- Keep Queue B hardening planned but not a substitute for the blocker repair.

## Blocked Work

- Broad feature work remains blocked.
- Workbench UI, runtime module loading, provider runtime, package runtime, gameplay, renderer, native GUI, release publication, and broad rewrites remain blocked.

## Feature Rules After Lock

When the lock eventually passes, future narrow slices must register public surfaces, expose typed commands, use diagnostic and refusal codes, preserve artifact identity, declare capabilities and providers, use module descriptors where applicable, and use the replacement protocol for rewrites.

## Authorized Narrow Product Slice

`WORKBENCH-VALIDATION-SLICE-01` is authorized by `FOUNDATION-CLOSEOUT-02`.

This authorization is narrow. It does not authorize broad Workbench UI, gameplay, renderer, native GUI, runtime provider expansion, release publication, or domain feature work.

Next recommended tasks:

1. `PORTABILITY-ARCH-POLICY-02`
2. `WORKBENCH-VALIDATION-SLICE-01`
