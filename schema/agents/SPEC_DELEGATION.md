--------------------------------
OWNERSHIP & RESPONSIBILITY
--------------------------------
ENGINE:
- ACT time, deterministic scheduling primitives, and command envelopes.
GAME:
- Delegation enforcement and command authorization checks.
SCHEMA:
- Delegation data formats, constraints, and versioning metadata.
TOOLS:
- Future editors/inspectors only (no runtime behavior).
FORBIDDEN:
- No runtime logic in schema specs.
- No implicit delegation or hidden authority.
DEPENDENCIES:
- Engine -> (no dependencies outside engine/).
- Game -> engine public API only.
- Schema -> none (formats only).
- Tools -> schema + engine/game public APIs only.
--------------------------------
# SPEC_DELEGATION - Delegated Authority (AGENT2)

Status: draft
Version: 1

## Purpose
Define explicit delegation records that allow agents to issue commands
within a bounded authority scope.

## Delegation schema
Required fields:
- delegation_id
- delegator_ref
- delegatee_ref
- allowed_commands
- expiry_act
- provenance_ref

Recommended fields:
- scope_ref
- created_act

## Delegation rules
- Delegation is explicit only; no implicit authority.
- Expired delegations MUST refuse command attempts.
- Delegation does not grant new mechanics; it gates CommandIntents only.

## Determinism rules
- Delegation resolution is deterministic by delegation_id.
- No per-tick polling of delegations.

## Prohibitions
- Delegation MUST NOT bypass doctrine or legitimacy rules.
- Delegation MUST NOT fabricate authority.

## Test plan (spec-level)
Required scenarios:
- Deterministic delegation resolution with multiple records.
- Expired delegation refusal handling.
