Status: DERIVED
Last Reviewed: unknown
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-ARCHIVE
Replacement Target: legacy reference surface retained without current binding authority

# Stability Tagging Final

## Summary

META-STABILITY-1 completes the global registry tagging sweep for `data/registries`.

Validated inventory:

- registry files: `387`
- governed registry entries: `3353`
- validator result: `complete`
- validator deterministic fingerprint: `4363c60b70f1432c32f9244404680238a64b721869cb8764d2b4e4c11c67de0f`

Class totals:

- `stable`: `43`
- `provisional`: `3310`
- `experimental`: `0`

## Stable Entries

Stable remains intentionally small in MVP.

Frozen stable surfaces:

- semantic contract registry: `12`
  - includes `contract.overlay.merge.v1`, `contract.cap_neg.negotiation.v1`, `contract.pack.compat.v1`, and `contract.time.anchor.v1`
- domain contract registry: `10`
  - conservation, determinism, and epistemic transition contracts
- capability fallback registry: `6`
  - release-governed fallback semantics for MVP negotiation
- degrade ladder registry: `7`
  - release-governed degrade ladder semantics
- compat mode registry: `4`
  - `compat.full`, `compat.degraded`, `compat.read_only`, `compat.refuse`
- pack degrade mode registry: `3`
  - deterministic pack refusal/degrade semantics
- time anchor policy registry: `1`
  - `time.anchor.mvp_default`

## Provisional Entries By Future Series

Largest provisional groups:

- `INF/TOOLING`: `1765`
- `PROC`: `332`
- `DOMAIN`: `252`
- `DIAG`: `192`
- `APPSHELL`: `190`
- `SYS`: `146`
- `CONTROL/LAW`: `116`
- `GEO/MW`: `76`
- `LIB`: `60`
- `CAP-NEG/PACK-COMPAT`: `44`
- `LOGIC`: `40`
- `EARTH/SOL`: `29`

Smaller provisional groups still present from earlier targeted passes:

- `GAL+/ASTRO`: `12`
- `MAT`: `7`
- `CAP-NEG`: `7`
- `SOL`: `6`
- `DOM`: `6`
- `SOL/EARTH`: `4`
- `ASTRO`: `4`
- `EARTH/MW`: `4`
- `MAT/DOM`: `3`
- `ASTRO-DOMAIN`: `3`
- `LOGIC/CAP-NEG`: `3`
- `LIB/PACK-COMPAT`: `2`
- `SOL/GAL`: `1`
- `MW`: `1`
- `MW/EARTH/SOL`: `1`
- `SOL/GEO`: `1`
- `SOL/LIB`: `1`
- `LIB/SERVER`: `1`
- `EARTH`: `1`

## Experimental Entries

- `0`

No registry entries currently depend on experimental profile/entitlement gating.

## Frozen Invariants For v0.0.0

The release-frozen registry invariants are:

- semantic contract entries themselves
- overlay merge semantics via `contract.overlay.merge.v1`
- CAP-NEG negotiation semantics via `contract.cap_neg.negotiation.v1`
- pack compatibility degrade/refusal semantics via `contract.pack.compat.v1`
- domain conservation and deterministic transition contracts
- canonical time anchor policy via `contract.time.anchor.v1`

## Compatibility Notes

The sweep remains non-breaking:

- existing dict-entry registries use sibling `stability`
- singleton entry dicts use sibling `stability`
- scalar-list registries retain their original scalar lists and add companion tagged entry collections
- legacy line registries remain line-oriented and use preceding `# key: value` stability comment blocks

## Release Readiness

The registry surface is now globally tagged and validator-clean.

Readiness after this pass:

- ready for release-note inclusion
- ready for ARCH-AUDIT, TIME-ANCHOR, and MVP gate follow-up validation
- ready for future replacement tracking without leaving untagged registry semantics behind
