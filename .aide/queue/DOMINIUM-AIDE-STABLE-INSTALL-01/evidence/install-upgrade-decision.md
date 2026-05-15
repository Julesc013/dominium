# Install / Upgrade Decision

## Decision

`UPGRADE_EXISTING_AIDE`

## Reasons

- Dominium identity is confirmed.
- `.aide/` already existed.
- Q49 ended as `READY_FOR_Q50_WITH_WARNINGS`.
- Existing target memory, queue, reports, and managed AGENTS sections had to be preserved.
- The stable AIDE bundle was present and archive-level checksums matched.

## Apply Method

Q50 used targeted manifest-guided sync from the extracted ZIP. It did not run direct `import-pack` because the pack dry-run failed on a missing checksum entry for `.aide.local.example/secrets/README.md`.

## Target-Specific Adaptation

The stable script expected root `core/gateway/**` and `core/providers/**` helpers. Q50 did not copy those root helpers because product-root writes were outside scope. Instead, `.aide/scripts/aide_lite.py` now supplies report-only fallback helpers for gateway/provider status and self-test fixtures.

