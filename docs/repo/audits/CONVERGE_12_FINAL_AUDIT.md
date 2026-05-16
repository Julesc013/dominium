Status: DERIVED
Last Reviewed: 2026-05-16
Supersedes: none
Superseded By: none

# CONVERGE-12 Final Audit

Status: PROVISIONAL

Phase: CONVERGE-12

Date: 2026-05-12

## Summary

CONVERGE-00 through CONVERGE-12 established a machine-readable source layout authority, root allowlist, exception ledger, distribution projection contract, component matrix contract, physical convergence for low-risk roots, and final stale-document audit cleanup.

CONVERGE-12 performed no physical moves and implemented no platform, render, native shell, backend, package, worldgen, domain, runtime, AppShell, or product behavior.

## Series Summary

| Phase | Result |
| --- | --- |
| CONVERGE-00 | Baseline layout audit recorded. |
| CONVERGE-01 | Source repo layout contract and audit validator added. |
| CONVERGE-02 | Root allowlist and stale layout authority handling added. |
| CONVERGE-03 | Root inventory and move map refined. |
| CONVERGE-04 | Distribution/install/media projection contract added. |
| CONVERGE-05 | Archive-family roots converged under `archive/`. |
| CONVERGE-06 | Root `schema/` and `schemas/` converged under `contracts/schemas/`; mixed contract roots left review-backed. |
| CONVERGE-07 | Runtime/AppShell roots converged under `runtime/`; mixed runtime roots left review-backed. |
| CONVERGE-08 | Product roots converged under `apps/`. |
| CONVERGE-09 | Safe Python domain roots split under `game/domains/`; mixed roots left review-backed. |
| CONVERGE-10 | Strict layout validation enabled with explicit exceptions. |
| CONVERGE-11 | Release component/support matrices added. |
| CONVERGE-12 | High-risk stale layout docs patched and final audits added. |

## Final Canonical Authority Stack

- `contracts/repo/layout.contract.toml`
- `contracts/repo/root_allowlist.toml`
- `contracts/repo/layout_exceptions.toml`
- `contracts/distribution/layout.contract.toml`
- `contracts/release/component_matrix.contract.toml`
- `docs/repo/REPO_LAYOUT_TARGET.md`
- `docs/repo/DISTRIBUTION_LAYOUT_CANON.md`
- `docs/release/COMPONENT_MATRIX.md`

Older docs may explain intent or history, but they do not override these sources for current physical layout or support posture.

## Final Canonical Source Roots

Canonical source roots are:

- `apps/`
- `engine/`
- `game/`
- `runtime/`
- `contracts/`
- `content/`
- `docs/`
- `tests/`
- `tools/`
- `scripts/`
- `cmake/`
- `external/`
- `release/`
- `archive/`

Optional future roots remain `sdk/` and `examples/` when explicitly introduced by contract.

## Generated And Ephemeral Policy

`build/`, `out/`, `dist/`, and `artifacts/` are generated or generated-adjacent roots. They are not source authority. `dist/` is governed as generated distribution output by `contracts/distribution/layout.contract.toml`.

## Distribution Projection Doctrine

Source repo layout is not install, runtime store, media, package, cache, staging, save, bundle, or distribution layout. Those physical projections are governed by `contracts/distribution/layout.contract.toml` and explained by `docs/repo/DISTRIBUTION_LAYOUT_CANON.md`.

## Matrix Doctrine

Product/platform/render/native/toolchain/package/audio/input/network/storage status is governed by `contracts/release/component_matrix.contract.toml` and `docs/release/COMPONENT_MATRIX.md`.

Planned, stub, experimental, research, unknown, unsupported, and blocked rows are not supported implementations.

## Remaining Exceptions

Active layout exceptions: 37.

Unexcepted strict layout violations: 0.

All active exceptions now carry `POST-CONVERGE` retirement metadata. They are explicit follow-up items, not hidden root authority.

## Remaining Unresolved Stale References

Grouped unresolved stale-reference count: 12.

These are mainly historical docs, older matrix mocks, and active exception-backed roots. They are tracked in `docs/repo/audits/STALE_PATH_REFERENCE_AUDIT.md` and do not override current contracts.

## Risks

- Some historical docs still mention old paths as history.
- Active exceptions must be retired or narrowed by future scoped work.
- Older release/platform docs may still include aspirational language; matrix docs now govern support posture.
- Local full build validation is blocked by missing Visual Studio 17 2022 generator.
- The broader FAST gate still reports a structural xstack failure outside this task.

## Recommended Next Work

- Begin post-CONVERGE AppShell/product mode enforcement work.
- Begin platform host proof work through `runtime/` and the component matrix.
- Begin renderer backend proof work through `runtime/` and the renderer matrix.
- Build native setup/launcher/admin shells only as thin projections over product semantics.
- Continue worldgen/domain realism work through the contracts/game/content/docs/tests split.
- Retire active layout exceptions through scoped follow-up tasks.

## Confirmation

CONVERGE-12 added final audit and stale-reference cleanup only. It did not implement new platform, render, native, domain, worldgen, product, runtime, AppShell, toolchain, packaging, install, or distribution behavior.

## POST-CONVERGE-00 Follow-up Note

POST-CONVERGE-00 health, exception, and build triage completed after this final audit. Active exceptions remain 37, unexcepted strict layout violations remain 0, local CMake verify remains blocked by the missing Visual Studio 2022 instance, FAST remains blocked in `repox_runner` by mod policy/schema validation, and the recommended next queue item is `POST-CONVERGE-01 - Generated / Output Root Cleanup`.
