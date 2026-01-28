# WorldDefinition Contract (WD-0a)

Status: binding.
Scope: minimum required shape, forbidden contents, provenance, extensions, and template equivalence.
This document extends (does not replace) `docs/architecture/WORLDDEFINITION.md`.

## Required minimum shape
A valid WorldDefinition MUST include at minimum:
- schema_id + schema_version
- worlddef_id (stable id)
- topology (root node, nodes, edges)
- initial_fields (possibly empty)
- policy_sets (all required policy lists present)
- spawn_spec (node + frame + position + orientation)
- provenance (template_id, template_version, generator_source, seed)
- extensions (open map, may be empty)

WorldDefinition is the ONLY world creation input.

## Forbidden contents
WorldDefinitions MUST NOT contain:
- Runtime state deltas or live sim objects
- Cached geometry or derived LOD data
- UI state or presentation artifacts
- Asset paths or pack-specific file paths
- Era or progression markers
- Execution schedules or pending Work IR

## Provenance requirements
Provenance is mandatory and MUST be explicit:
- template_id and template_version
- generator_source (built_in | pack | tool)
- seed set(s) and template parameters used
- generator_ref or provenance_ref when available

Provenance is part of the semantic contract and MUST be preserved.

## Extension bag rules
- extensions are namespaced and opaque.
- unknown extensions MUST be preserved.
- extensions MUST NOT be required for core validity.
- extension semantics MUST be documented by the provider.

## Template equivalence rules
Template output equivalence is defined by:
- same template_id + template_version
- same input parameters (including seed)
- same capability resolution lockfile
- same pack set (or no packs)

Built-in and pack templates are equivalent; they must converge on identical
WorldDefinition output when parameters and capabilities match.

Equivalence is verified by a deterministic WorldDefinition hash.
If the hash differs, the templates are NOT equivalent.

## Refusal rules
- Missing required fields -> refusal (WD-REFUSAL-INVALID).
- Unsupported schema_version -> refusal (WD-REFUSAL-SCHEMA).
- Missing required capability -> refusal (WD-REFUSAL-CAPABILITY).
- Template refusal -> WD-REFUSAL-TEMPLATE.

## Save embedding
- WorldDefinition is embedded by value in saves.

## See also
- `docs/architecture/WORLDDEFINITION.md`
- `schema/world_definition.schema`
- `docs/architecture/SEMANTIC_STABILITY_POLICY.md`
