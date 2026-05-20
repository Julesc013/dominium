# VERSION-DEPRECATION-LAW-01 Initial Versioning Inventory

Status: warning inventory

Task: `VERSION-DEPRECATION-LAW-01`

Inventory command:

```text
python tools/validators/contracts/check_version_deprecation.py --repo-root . --inventory
```

Result:

```text
version/deprecation law: pass
lifecycle_states: 9
errors: 0
warnings: 0
inventory: warning files_scanned=17970 version_like=2479
- artifact_with_version: 8
- command_with_version: 4
- descriptor_with_version: 24
- fixture_schema: 584
- historical_or_audit_lifecycle: 76
- release_surface_with_version: 177
- replacement_policy_with_version: 9
- schema_protocol_with_version: 1593
- surface_with_version: 4
```

## Summary

This inventory is descriptive only. It records current version-like surfaces and
does not migrate, rewrite, deprecate, retire, remove, or promote any active
surface.

## Categories

- `surface_with_version`: public-surface registry and related governance.
- `artifact_with_version`: artifact identity contracts and registries.
- `schema_protocol_with_version`: schema, protocol, registry, serialization, and migration policy surfaces.
- `command_with_version`: command-surface contract/schema entries.
- `descriptor_with_version`: provider/module/workbench/app descriptors and policy surfaces.
- `replacement_policy_with_version`: replacement protocol surfaces.
- `pack_manifest_with_version`: content pack manifests when present.
- `release_surface_with_version`: release and release-doc surfaces.
- `historical_or_audit_lifecycle`: audit records and historical proof.
- `fixture_schema`: tests and fixtures.

## Risks

- Many existing schemas and release docs carry version-like fields but are not
  migrated into formal version policies in this task.
- Compatibility corpus remains future work.
- Version/deprecation law is provisional until downstream laws and release gates
  consume it.

## Next

`MOD-PACK-TRUST-MODEL-01`
