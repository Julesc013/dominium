# Installed State Evolution

## Versioning
- `state_version` is required in `installed_state.tlv`.
- Missing `state_version` triggers a deterministic backfill migration.

## Migration policy
- Forward-only automatic migrations are allowed.
- Backward migrations are not automatic.
- `migration_applied` records applied steps in canonical order.

## Compatibility rules
- Unknown future fields are ignored deterministically.
- Older clients must skip unknown fields without failure.
