# SPLAT Selection Rules (SR-3)

## Inputs
- Manifest: `supported_targets`, optional `allowed_splats`.
- Request: `target_platform_triple`, `install_scope`, `ui_mode`, `ownership_preference`.
- Request caps: `required_caps`, `prohibited_caps`.
- Optional: `requested_splat_id`.

## Algorithm
Phase A: build candidate list from registry, sorted in lexicographic order by ID (bytewise). This is the canonical order.

Phase B: if `requested_splat_id` is present:
- If the ID is in the removed list, fail with `SPLAT_REMOVED`.
- If the ID is not found in the registry, fail with `SPLAT_NOT_FOUND`.
- Otherwise reject all non-requested candidates with `REQUESTED_ID_MISMATCH` and
  continue validating the requested candidate.

Phase C: for each candidate, apply checks in order and reject on the first failure:
1) Platform triple not supported by candidate.
2) Request scope not supported by candidate.
3) Request UI mode not supported by candidate.
4) Ownership preference incompatible with candidate.
5) Manifest allowlist excludes candidate.
6) Required caps are missing.
7) Prohibited caps are present.
8) Manifest `supported_targets` does not include the request target triple.

Phase D: if any compatible candidates remain, select the first compatible in canonical order.
If none remain, fail with `NO_COMPATIBLE_SPLAT`.

Phase E: emit audit evidence with candidate list, rejections, selected ID, and reason.

## Deprecation
- Deprecated SPLATs are still selectable but emit an audit warning event.

## Rejection codes
- `1` REQUESTED_ID_MISMATCH
- `2` PLATFORM_UNSUPPORTED
- `3` SCOPE_UNSUPPORTED
- `4` UI_MODE_UNSUPPORTED
- `5` OWNERSHIP_INCOMPATIBLE
- `6` MANIFEST_ALLOWLIST
- `7` REQUIRED_CAPS_MISSING
- `8` PROHIBITED_CAPS_PRESENT
- `9` MANIFEST_TARGET_MISMATCH

## Selected reason codes
- `0` NONE
- `1` REQUESTED
- `2` FIRST_COMPATIBLE
