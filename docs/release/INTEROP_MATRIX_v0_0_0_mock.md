Status: CANONICAL
Last Reviewed: 2026-03-14
Stability: provisional
Future Series: DIST
Replacement Target: release-pinned interop contract and signed archive compatibility guidance

# Interop Matrix v0.0.0 mock

DIST-6 defines the deterministic version-interop acceptance matrix for the `v0.0.0-mock` distribution bundles.

## Purpose

The matrix proves that distributed artifacts honor CAP-NEG and PACK-COMPAT guarantees when products are mixed within the supported `v0.0.0-mock` surface.

The governed outcomes are:

- clean negotiation for identical builds,
- stable negotiation-record hashes for deterministic rebuilds,
- lawful compatibility across same-version platform variants when the negotiated capability surface overlaps,
- deterministic refusal for pack-lock mismatches,
- explicit read-only fallback for allowed contract drift,
- explicit refusal when read-only fallback is not allowed.

## Cases

The canonical DIST-6 cases are:

- `same_build_same_build`
  - client and server are loaded from the same portable bundle
  - expected compatibility mode: `compat.degraded`
- `same_build_identical_rebuild`
  - client and server are loaded from separate bundles assembled from identical inputs
  - expected compatibility mode: `compat.degraded`
  - expected negotiation-record hash: identical to `same_build_same_build`
- `same_version_cross_platform`
  - client and server remain on the same semantic version while platform capability surfaces differ
  - if no alternate platform bundle is present, the client descriptor is deterministically projected through a supported alternate platform row
  - expected compatibility mode: `compat.degraded`
- `minor_protocol_drift`
  - the client advertises a wider minor protocol range while preserving overlap with the server
  - expected compatibility mode: `compat.degraded`
  - expected chosen protocol: `protocol.loopback.session@1.0.0`
- `pack_lock_mismatch`
  - bundle negotiation remains lawful, but save/session material guarded by a mismatched pack lock must refuse
  - expected save refusal code: `refusal.save.pack_lock_mismatch`
- `contract_mismatch_read_only`
  - contract drift is introduced with read-only fallback enabled
  - expected compatibility mode: `compat.read_only`
  - expected save-open result: `complete` with `read_only_required=true`
- `contract_mismatch_strict`
  - contract drift is introduced with read-only fallback disabled
  - expected compatibility refusal code: `refusal.compat.contract_mismatch`
  - expected save refusal code: `refusal.save.contract_mismatch`

## Runtime Inputs

DIST-6 accepts:

- bundle root A
- bundle root B
- case identifier

If bundle roots are omitted, the harness assembles deterministic temporary bundles from current repository inputs. The generated bundles are a test fixture only; they do not replace the governed DIST outputs.

## Expected Observations

Each case must record:

- client and server build IDs
- descriptor hashes
- negotiation record hash
- selected compatibility mode
- refusal code, when refusal is expected
- degrade/read-only events, when degradation is expected
- save-open outcome for save-compatibility cases

No silent fallback is allowed.

## Reporting

DIST-6 generates:

- `docs/audit/DIST6_INTEROP_<case>.md`
- `data/audit/dist6_interop_<case>.json`
- `docs/audit/DIST6_FINAL.md`

All outputs must use deterministic ordering and canonical serialization.
