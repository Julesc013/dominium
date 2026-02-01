Status: DERIVED
Last Reviewed: 2026-02-01
Supersedes: none
Superseded By: none

# Schema Index

This index is canonical for schema files under `schema/`. It lists the core
cross-cutting schemas and the rules they follow.

## Versioning Rules
- All schemas MUST declare `schema_id`, `schema_version`, and `stability`.
- Versions are semantic and monotonically increasing.
- See `schema/SCHEMA_VERSIONING.md` and `schema/SCHEMA_MIGRATION.md`.

## Forward Compatibility Rules
- Readers MUST preserve unknown fields, tags, and records.
- See `docs/schema/FORWARD_COMPATIBILITY.md`.

## Core Schema Set (Canonical)
- `schema/topology.schema` - Topology nodes, relationships, traits, and domain attachments.
- `schema/domain.schema` - Domains, domain volumes, and abstract bounds.
- `schema/field.schema` - Fields, units, representation tiers, and knowledge state flags.
- `schema/process.schema` - Process descriptors, IO references, and required capabilities.
- `schema/capability.schema` - Capability identifiers, tags, providers, and qualifiers.
- `schema/authority.schema` - Authority tokens and scope descriptors.
- `schema/snapshot.schema` - Snapshot identifiers, coverage, and provenance.
- `schema/material.schema` - Materials, composition descriptors, and property traits.
- `schema/part_and_interface.schema` - Parts, interfaces, mass/volume, and capability links.
- `schema/assembly.schema` - Assemblies, part graphs, and interface connections.
- `schema/network.schema` - Networks, nodes, edges, and flow descriptors.
- `schema/knowledge.schema` - Knowledge artifacts and uncertainty descriptors.
- `schema/institution.schema` - Institutions, jurisdictions, and enforcement tags.
- `schema/pack_manifest.schema` - Pack identity, versions, and capability dependencies.
- `schema/save_and_replay.schema` - Save/replay identifiers, pack references, and determinism metadata.
- `schema/worldgen_model.schema` - Worldgen model families and declared scope.
- `schema/refinement_plan.schema` - Refinement layers, precedence, and ceilings.
- `schema/measurement_artifact.schema` - Measurement artifacts and epistemic access metadata.

## Domain-Specific Schemas
Domain schemas live under `schema/*/README.md` and are scoped to specific
subsystems (economy, war, governance, world, etc.). This index intentionally
focuses on the core, cross-cutting schemas that all systems defer to.