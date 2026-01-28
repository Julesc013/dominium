# Template Registry (WD-0)

Status: binding.
Scope: world template registry and provider rules.

## Template definition
A template is a generator that outputs a WorldDefinition.

Each template MUST declare:
- template_id (stable string)
- version
- description
- parameter schema (seed, toggles, sizes)
- required capabilities (if any)
- output guarantees (what it produces)
- refusal conditions

Templates MUST output the WorldDefinition schema without extra runtime state.

## Template providers
There are two provider types:
1) Built-in providers
   - compiled into the executable
   - always available
   - minimal and deterministic
2) Pack providers
   - discovered via UPS capability
   - optional
   - removable

Both provider types:
- register into the SAME registry
- are presented identically in UI
- produce the SAME WorldDefinition format
- are not privileged over one another

## Pack template manifest
Pack providers advertise capability `world.template.registry` in their
`pack_manifest.json` and ship a `world_templates.json` file at pack root.

`world_templates.json` REQUIRED SHAPE (minimum):
```
{
  "schema_id": "dominium.schema.world_template_registry",
  "schema_version": "1.0.0",
  "records": [
    {
      "template_id": "...",
      "version": "...",
      "description": "...",
      "parameter_schema": { "...": "..." },
      "required_capabilities": [ "..." ],
      "output_guarantees": [ "..." ],
      "refusal_conditions": [ "..." ],
      "builtin_equivalent": "builtin.minimal_system",
      "equivalence_hash": "<sha256 of normalized WorldDefinition>",
      "equivalence_seed": 0
    }
  ]
}
```

If `builtin_equivalent` is present, `equivalence_hash` is mandatory.
`equivalence_seed` defaults to 0 when omitted.

## Registry behavior
- Deterministic listing and ordering.
- No silent fallback: if a template is missing, refuse explicitly.
- Template metadata is data-only; no hidden defaults.
- Unknown fields are preserved by tools and registries.

## Equivalence
Templates are equivalent if their output WorldDefinitions are identical after
normalization (sorted keys, stable ordering, and ignored unknown fields).

Template equivalence testing is mandatory when a pack-provided template claims
parity with a built-in template.

## References
- `docs/architecture/WORLDDEFINITION.md`
- `docs/worldgen/BUILTIN_TEMPLATES.md`
- `schema/world_definition.schema`
