# Stability Registry Convention

## Chosen Convention

Registry entries keep their existing payload shape and add an optional sibling field:

```json
{
  "existing_id_field": "...",
  "stability": {
    "...": "..."
  },
  "other_existing_fields": "..."
}
```

This repository does not adopt the wrapper form:

```json
{
  "id": "...",
  "stability": { "...": "..." },
  "data": { "...existing payload..." }
}
```

Reason:

- the sibling form is non-breaking for current loaders
- the wrapper form would move required fields such as `process_id`, `command_id`, `contract_id`, and `generator_id`
- many existing registry consumers already tolerate unknown entry fields

## Placement Rules

### Entry-Level

`stability` belongs on the entry object itself.

Examples:

- `record.sky_models[]`
- `record.logic_compile_policies[]`
- `record.compat_modes[]`
- `record.products[]`
- root `records[]` in registries such as `process_registry.json`

### Root-Level

Do not add a root-level registry-wide `stability` marker as a substitute for per-entry markers.

Reason:

- the change discipline applies to individual items, not just the file
- mixed classes inside the same registry must remain representable

## Deterministic Fingerprinting

- the `stability` object participates in the containing entry fingerprint
- the `stability.schema_version` is pinned to `1.0.0`
- the `stability.deterministic_fingerprint` is computed with its own fingerprint field blanked
- entry-level deterministic fingerprints must therefore change when stability metadata changes

This is intentional. Stability metadata is part of the deterministic contract surface for the scoped registry families.

## Shape Compatibility

The convention must work with both common registry shapes in the repository:

- `record.<collection>[]`
- top-level `records[]`

The validator must not assume a single collection key name. It must instead use a scoped registry specification that identifies:

- the file path
- the collection key
- the item ID field

## Empty Collections

Registries with empty collections remain valid.

Rule:

- the registry file may have zero entries
- if an entry exists, the entry must carry `stability`

## Pack Compatibility Hook

For `pack.compat` manifests, stability metadata is optional in META-STABILITY-0.

If present:

- use the same `stability` object shape
- keep it as a top-level sibling field on the manifest object
- include it in the manifest fingerprint

## Migration Rule

Because the sibling-field approach is non-breaking and current registry consumers are open-map tolerant, META-STABILITY-0 does not require a migration route for existing registry payloads.

Existing entries that do not yet declare `stability` are treated as:

- loadable at runtime
- governance-invalid once the scoped enforcement checks are enabled

## Initial Rollout Rule

META-STABILITY-0 applies mandatory tagging to the scoped registry families documented in the retro audit.

Outside that scope:

- files remain loadable
- no silent reinterpretation of existing `status`, `stub`, or `deprecated` fields occurs
