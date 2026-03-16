Status: CANONICAL
Last Reviewed: 2026-02-17
Supersedes: none
Superseded By: none
Version: 1.0.0
Stability: provisional
Future Series: DOC-ARCHIVE
Replacement Target: legacy reference surface retained without current binding authority

# Institutions And Roles

## Scope
- Institutions are Truth-side assemblies for governance scaffolding.
- Roles are explicit assignments with bounded delegated authority.
- Governance type is metadata in CIV-3; it does not introduce stage semantics.

## Core Concepts
- `institution`:
  - `institution_id`
  - `institution_type_id`
  - `faction_id`
  - `status`
  - deterministic metadata/extensions
- `role_assignment`:
  - `assignment_id`
  - `institution_id`
  - `subject_id`
  - `role_id`
  - `granted_entitlements` (bounded)
  - `created_tick`

## Delegation Rules
- Delegation is explicit and process-driven:
  - `process.role_assign`
  - `process.role_revoke`
- Delegation is always gated by:
  - `LawProfile`
  - issuer authority/entitlements
  - server profile restrictions in multiplayer
- Multiple roles are merged deterministically:
  - unique entitlement set
  - stable lexical ordering

## Multiplayer / SRZ
- Institution and role assemblies are authoritative server-side.
- In SRZ hybrid, role mutations must execute on owning shard.
- Cross-shard delegation can be routed deterministically or refused when unsupported.

## Security And Epistemics
- Role assignment does not grant hidden truth visibility automatically.
- Order and institution visibility remains Perceived-model gated.
- Unauthorized assignment attempts must emit deterministic refusal and audit evidence.

## CIV-3 Limits
- No government gameplay simulation yet (elections, legitimacy, etc.).
- No automatic socio-economic behavior from roles.
- Roles currently provide bounded authority scaffolding only.
