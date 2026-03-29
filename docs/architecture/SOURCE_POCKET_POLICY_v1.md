Status: DERIVED
Last Reviewed: 2026-03-30
Stability: provisional
Future Series: XI-5
Replacement Target: Xi-6 freeze inputs after residual convergence

# Source Pocket Policy v1

## Taxonomy

- `FORBIDDEN_CODE_SRC`: Generic code source directories that violate canonical domain placement and must not remain.
- `MOVE_TO_DOMAIN`: Residual source pocket whose active implementation belongs under a canonical domain root.
- `QUARANTINE_REQUIRED`: Ambiguous residual source pocket that cannot be justified safely in this pass.
- `VALID_CONTENT_SOURCE`: Content or provenance source trees kept as upstream raw inputs rather than runtime code.
- `VALID_LEGACY_ARCHIVE_SOURCE`: Legacy source trees retained as archival reference and fenced from active build/runtime ownership.
- `VALID_PACKAGING_SOURCE`: Packaging or IDE-convention source trees that are semantically correct for toolchain ownership.
- `VALID_THIRDPARTY_SOURCE`: Vendored or external source trees retained for third-party reasons.

## Allowlisted Residual Roots

- `packs/source` -> `VALID_CONTENT_SOURCE` (`13` files)
- `legacy/source/tests` -> `VALID_LEGACY_ARCHIVE_SOURCE` (`82` files)
