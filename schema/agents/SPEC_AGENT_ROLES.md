--------------------------------
OWNERSHIP & RESPONSIBILITY
--------------------------------
ENGINE:
- ACT time, deterministic scheduling primitives, and command envelopes.
GAME:
- Role binding logic and doctrine assignment policy.
SCHEMA:
- Role data formats, constraints, and versioning metadata.
TOOLS:
- Future editors/inspectors only (no runtime behavior).
FORBIDDEN:
- No runtime logic in schema specs.
- No hard-coded role behaviors.
DEPENDENCIES:
- Engine -> (no dependencies outside engine/).
- Game -> engine public API only.
- Schema -> none (formats only).
- Tools -> schema + engine/game public APIs only.
--------------------------------
# SPEC_AGENT_ROLES - Agent Roles (AGENT2)

Status: draft
Version: 1

## Purpose
Define roles as semantic labels that bind agents to doctrine and authority
requirements without embedding behavior.

## AgentRole schema
Required fields:
- role_id
- default_doctrine_ref
- authority_requirements
- capability_requirements
- provenance_ref

Recommended fields:
- scope_ref (org/jurisdiction)
- created_act

## Role binding rules
- Roles do not execute actions.
- Role requirements must be satisfied before doctrine applies.
- Role mismatch MUST refuse goal evaluation or planning.

## Determinism rules
- Roles are resolved deterministically by role_id.
- No per-tick scans or role-based hidden privileges.

## Prohibitions
- Roles MUST NOT hard-code behaviors.
- Roles MUST NOT bypass doctrine or command systems.

## Test plan (spec-level)
Required scenarios:
- Deterministic role resolution under conflicting inputs.
- Role mismatch refusal handling.
