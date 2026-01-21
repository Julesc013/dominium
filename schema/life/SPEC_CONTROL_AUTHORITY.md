--------------------------------
OWNERSHIP & RESPONSIBILITY
--------------------------------
ENGINE:
- Stable IDs, hashing, deterministic ordering helpers.
GAME:
- Control authority rules, consent logic, and delegation resolution.
SCHEMA:
- Control authority and controller binding record formats.
TOOLS:
- Future inspectors/editors only (no runtime behavior).
FORBIDDEN:
- No runtime logic in schema specs.
- No implicit control transfer without authority.
DEPENDENCIES:
- Engine -> (no dependencies outside engine/).
- Game -> engine public API only.
- Schema -> none (formats only).
- Tools -> schema + engine/game public APIs only.
--------------------------------
# SPEC_CONTROL_AUTHORITY — Control Authority and Delegation Canon

Status: legacy (superseded by LIFE0+)
Version: 1

Note: LIFE0+ canonical specs live in `schema/life/SPEC_LIFE_ENTITIES.md` and
`schema/life/SPEC_IDENTITY_AND_LINEAGE.md`. This document remains for legacy
context; if any statement conflicts with LIFE0+, LIFE0+ wins.

## Purpose
Define who may control whom, how authority is delegated, and how controller
bindings are resolved. This spec defines schema records and deterministic
resolution order only.

## Control authority rules (mandatory)
Valid authority sources:
- Consent-based transfer
- Guardianship-based transfer
- Organization authority delegation
- Jurisdiction/legal constraints
- Contract-based delegation

Control authority resolution order (locked):
1) Explicit contract/context
2) Organization rules
3) Jurisdiction rules
4) Personal preferences
5) Refusal (no implicit fallback)

## Controller binding (conceptual)
Controller bindings link a player session to a person or to NONE (spectator).

### ControllerBinding schema (conceptual)
Required fields:
- controller_id
- controlled_person_id (or NONE)
- ability_package_id
- authority_scope_id
- bind_tick (ACT)

Optional fields:
- bind_reason_code
- bind_request_id

## Authority delegation records (conceptual)

### ControlAuthorityRecord schema (conceptual)
Required fields:
- authority_id
- grantor_person_id (or org_id)
- grantee_person_id or controller_id
- scope_kind (person | org | jurisdiction | estate)
- scope_ref_id
- start_tick
- end_tick or NONE
- consent_state (granted | revoked | expired)
- source_contract_id or NONE

Optional fields:
- delegation_reason_code
- audit_trail_ref

## Determinism and scheduling
- Authority changes are scheduled events; no global scans.
- Resolution uses stable ordering keys and is deterministic.
- Batch vs step equivalence must hold.

## Executor authority (LIFE2 integration)
- Estate actions require explicit executor authority.
- If executor authority is missing or revoked, estate resolution must refuse deterministically.
- No implicit executor assignment is allowed.

## Epistemic boundary
- Control bindings do not grant knowledge.
- UI may only display authority status via capability snapshots.

## Prohibitions (absolute)
- Implicit control transfer without authority record.
- Authority resolution based on UI state or camera position.
- Global iteration over all persons for control matching.

## Integration points
- Continuation policies: `schema/life/SPEC_CONTINUATION_POLICIES.md`
- Contracts: `docs/specs/SPEC_CONTRACTS.md`
- Epistemic UI: `docs/specs/SPEC_EPISTEMIC_INTERFACE.md`
