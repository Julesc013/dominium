Status: DERIVED
Version: 1.0.0

# Migration Status

- deprecations_registry: `data/governance/deprecations.json`
- topology_map: `docs/audit/TOPOLOGY_MAP.json`
- registry_validation: `pass`

## Lifecycle Counts
- deprecated: 1
- quarantined: 1

## Deadlines
- `data/registries/deprecation_registry.json` -> target `2.0.0` (deprecated)
- `schema/deprecation/deprecation_entry.schema` -> target `2.0.0` (quarantined)

## Deprecated and Quarantined
- `data/registries/deprecation_registry.json` (deprecated) -> `data/governance/deprecations.json`
- `schema/deprecation/deprecation_entry.schema` (quarantined) -> `schema/governance/deprecation_entry.schema`

## Remaining References
- `data/registries/deprecation_registry.json`: 10
  - `build/impact_graph.json`
  - `build/impact_graph.test.a.json`
  - `build/impact_graph.test.b.json`
  - `build/impact_graph.test.det.json`
  - `build/semantic_impact.latest.json`
  - `docs/audit/RETRO_CONSISTENCY_FRAMEWORK_BASELINE.md`
  - `docs/audit/TOPOLOGY_MAP.json`
  - `schemas/deprecation_entry.schema.json`
  - `tools/governance/adapters/deprecation_registry_adapter.py`
  - `tools/xstack/testx/tests/test_deprecation_registry_consistency.py`
- `schema/deprecation/deprecation_entry.schema`: 9
  - `build/auditx/changed_only_a/FINDINGS.json`
  - `build/auditx/changed_only_b/FINDINGS.json`
  - `build/auditx/smoke/FINDINGS.json`
  - `build/impact_graph.json`
  - `build/semantic_impact.latest.json`
  - `docs/architecture/DEPRECATION_AND_QUARANTINE.md`
  - `docs/audit/RETRO_CONSISTENCY_FRAMEWORK_BASELINE.md`
  - `docs/audit/TOPOLOGY_MAP.json`
  - `docs/audit/auditx/FINDINGS.json`

## Validation Errors
- none
