# SPEC_DOMAIN_VOLUMES (DOMAIN0)

Schema ID: DOMAIN_VOLUMES
Schema Version: 1.0.0
Status: binding.
Scope: domain identity, metadata, and runtime volume bindings.

## Purpose
Define a general, future-proof domain volume system that encodes where
simulation, travel, laws, and refinement may occur without hard-coded bounds.

## Domain Definition
A Domain is a spatial container defining where:
- simulation may occur
- travel may occur
- laws may apply
- refinement may be requested

Domains do NOT imply fidelity, authority, ownership, or activity.

## Domain Identity (Required Fields)
- domain_id: stable identifier.
- existence_state: from `schema/existence/SPEC_EXISTENCE_STATES.md`.
- archival_state: from `schema/existence/SPEC_ARCHIVAL_STATES.md`.
- parent_domain_id: optional (0 or null for root).
- precedence: integer (higher wins when overlaps remain).
- runtime_volume_id: reference to runtime SDF volume data.
- authoring_volume_id: optional reference to authoring source.
- flags: optional bitset (e.g., allow_refine, allow_travel).

## Invariants (Absolute)
- Domain identity is explicit; no implicit domains.
- Existence and archival states are explicit and auditable.
- Domain membership is never inferred outside domain queries.

## Integration Points
- EXISTENCE: existence_state determines if domain is active.
- ARCHIVAL: archival_state determines mutability and simulation.
- REFINEMENT: domains may allow/forbid refinement requests.
- LAW: jurisdictions attach to domains for gating.
- TRAVEL: travel edges reference domains.
- SHARDING: shard ownership partitions by domain.
- INTEREST: interest sampling constrained by domains.

## References
- `schema/domain/SPEC_DOMAIN_RUNTIME_SDF.md`
- `schema/domain/SPEC_DOMAIN_AUTHORING.md`
- `schema/domain/SPEC_DOMAIN_NESTING.md`
