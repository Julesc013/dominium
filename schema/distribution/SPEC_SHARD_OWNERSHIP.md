# SPEC_SHARD_OWNERSHIP (DIST0)

This specification defines ownership boundaries and authoritative placement
rules for shards.

## Ownership Rules

- Authoritative writes MUST execute on the shard that owns the written data.
- Each ownership scope must be deterministic and auditable.
- Ownership boundaries must be derived from data, not runtime behavior.

## Ownership Scopes

Supported scope shapes:
- `ENTITY_RANGE`: stable entity ID ranges or hash buckets.
- `REGION_RANGE`: world region or chunk ranges.
- `DOMAIN`: explicit system domain ownership (e.g., ECONOMY, WAR).

All scopes MUST be expressed as deterministic ranges or lists. No dynamic
repartitioning without explicit migration events.

## Migration Rules

Ownership migration must:
- create a migration event with a stable ID,
- schedule its effective tick in ACT time,
- log origin and destination shard IDs,
- preserve provenance and audit trails.

## Forbidden Patterns

- Implicit ownership change based on load.
- Cross-shard writes without migration.
- Placement decisions based on network timing.
