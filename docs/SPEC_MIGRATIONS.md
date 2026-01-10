# SPEC_MIGRATIONS - Schema Registry and Migration Rules

This spec defines deterministic migration rules for versioned schemas and
containers. It applies to all persisted formats that participate in identity
binding or deterministic replay.

## 1. Schema identity
Each schema is identified by:
- `schema_id` (`u64`): FNV-1a hash of a UTF-8 string ID.
- `schema_ver` (`u32`): monotonically increasing version.

## 2. Migration registration
- Migrations are registered as explicit `(schema_id, from_ver, to_ver)` edges.
- Only single-step migrations are registered; chains are computed at runtime.
- Migrations must be deterministic and side-effect free (no wall-clock,
  network, or host state).

## 3. Chain selection (deterministic)
- If `from_ver == to_ver`, no migration is required.
- Otherwise, a deterministic path is selected:
  - Graph search order is ascending `schema_ver`.
  - Prefer the shortest path; ties are broken by ascending version order.
- If no path exists, refuse with `MIGRATION_REQUIRED`.

## 4. Policy
- Read old, write new.
- Unknown or higher versions are refused by default.
- All formats must support skip-unknown for forward compatibility.

## 5. Audit requirements
Every migration chain must emit an audit record containing:
- `schema_id`, `from_ver`, `to_ver`
- selected path (version sequence)
- success/refusal code

Audit records are deterministic and must not contain absolute paths.

## 6. Tooling
- Tools and validators must use the same registry and refusal rules.
- Missing migration paths are a refusal, not a best-effort fallback.

## Related specs
- `docs/SPEC_CONTAINER_TLV.md`
- `docs/SPEC_UNIVERSE_BUNDLE.md`
- `docs/SPEC_DETERMINISM.md`
