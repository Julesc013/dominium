# SPLAT Lifecycle Management

## Adding a SPLAT
- Define caps in the registry with conservative defaults.
- Document in `docs/setup2/SPLAT_REGISTRY.md`.
- Add selection tests and adapter mapping if applicable.

## Deprecating a SPLAT
- Mark `is_deprecated=true` in the registry.
- Emit audit warning `SPLAT_DEPRECATED` when selected.
- Document rationale and replacement target.

## Removing a SPLAT
- Provide at least two releases of deprecation notice.
- Requests for removed IDs fail with `SPLAT_REMOVED`.
- Document the removal in release notes and registry.
