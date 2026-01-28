# Fabrication Model (FAB0)

Status: binding.
Scope: fabrication ontology, schema design rules, and authoring contracts.

## Core principles (binding)
- Code interprets; data defines.
- No schema implies progression or era.
- All identifiers are namespaced and stable.
- All numeric fields carry unit annotations.
- All schemas are extension-preserving.
- Unknown fields MUST round-trip without loss.

## Data-only contract
Fabrication schemas define *what exists* and *how it may be described*.
They MUST NOT define how things work beyond declarative constraints.

## Schema requirements
All fabrication schemas MUST:
- Declare `schema_id`, `schema_version`, and `stability`.
- Use reverse-DNS identifiers for all IDs and tags.
- Provide `extensions` maps for forward compatibility.
- Preserve unknown fields at load/save boundaries.
- Declare unit annotations for any numeric values.

## Non-goals
Fabrication schemas MUST NOT:
- encode real-world meaning
- enforce gameplay, balance, or progression
- assume a specific era or technology tier

## References
- `docs/arch/ID_AND_NAMESPACE_RULES.md`
- `docs/arch/UNIT_SYSTEM_POLICY.md`
- `docs/arch/CODE_KNOWLEDGE_BOUNDARY.md`
- `docs/arch/CONTRACTS_INDEX.md`
