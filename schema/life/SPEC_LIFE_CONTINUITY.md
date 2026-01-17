--------------------------------
OWNERSHIP & RESPONSIBILITY
--------------------------------
ENGINE:
- Stable IDs, hashing, deterministic RNG, ACT time, event scheduling, ledger primitives.
GAME:
- LIFE semantics: identity rules, control authority policy, death/continuation triggers.
- Estate/inheritance orchestration via contracts and ledgers.
SCHEMA:
- Canonical LIFE record formats, versioning, and validation constraints.
TOOLS:
- Future inspectors/editors only (no runtime behavior).
FORBIDDEN:
- No runtime logic in schema specs.
- No respawn or lineage policy in engine code.
- No UI semantics or platform logic in game rules.
DEPENDENCIES:
- Engine -> (no dependencies outside engine/).
- Game -> engine public API only.
- Schema -> none (formats only).
- Tools -> schema + engine/game public APIs only.
--------------------------------
# SPEC_LIFE_CONTINUITY — Person/Body/Controller Canon

Status: draft
Version: 1

## Purpose
Define the canonical LIFE continuity model: Person identity, Body embodiment,
Controller agency, and deterministic continuity constraints. This spec defines
data formats and invariants only; no runtime logic is introduced.

## Core invariants (locked)
1) Person identity is persistent and never deleted.
2) Body embodiment is physical and may be alive, dead, or missing.
3) A body is bound to exactly one person at a time.
4) Controllers are sessions, not persons.
5) Continuity is deterministic and event-driven.
6) No global iteration over all persons or bodies is allowed.
7) Death creates an estate; assets move only via ledger/contract.
8) Knowledge of death is epistemic and must be observed or communicated.

## Canonical entities (schema-level)

### PERSON (Identity)
Persistent identity object; exists regardless of body.

Conceptual fields:
- person_id (stable)
- sex (baseline enum; may be UNKNOWN)
- lineage_links (parent_ids, descendant_ids, may be UNKNOWN)
- trait_carriers (references; may be cohort-aggregated)
- ownership_roles (references to control/authority records)
- provenance_id (origin record)

Notes:
- Person exists without an active body.
- Person may be represented as a cohort member at macro fidelity.

### BODY (Embodiment)
Physical embodiment bound to exactly one person.

Conceptual fields:
- body_id
- person_id
- alive_state (alive | dead | missing)
- location_ref (world coord or shard key)
- health_state_summary (placeholder reference)
- death_record_ref (optional)

### CONTROLLER (Player Agency)
Session binding for player agency; not a person.

Conceptual fields:
- controller_id (session)
- controlled_person_id (or NONE)
- ability_package_id
- authority_scope_id
- last_bind_tick (ACT)

### ABILITY PACKAGE (Mode Preset)
Data-defined capability bundle referenced by controllers.
See `schema/life/SPEC_CONTINUATION_POLICIES.md`.

## Defaults (mandatory)
- Default mode: HARDCORE lineage realism.
- Default world start: at least two humans (male + female) unless scenario selects
  "last human" explicitly.
- Default continuation: S1 (transfer to existing eligible person only).
- Any respawn that creates a new body requires a constructed causal pipeline
  (clone/vat, drone, backup) and is not default.

## Scalability and fidelity interaction
- Persons may exist as:
  - micro persons (instantiated)
  - cohort entries (macro aggregates)
- Bodies are micro in active regions; macro summaries are counts only.
- Continuation policy decisions must operate on bounded sets:
  - eligible persons are selected by authority scope + interest sets.
  - no global scan of all persons is permitted.

## Multiplayer parity requirements
Lockstep:
- Death and continuation decisions are explicit commands or deterministic events.
- All peers produce identical outcomes.

Server-auth:
- Server validates death and continuation.
- Clients receive updated controller bindings deterministically.

## Prohibitions (absolute)
- Deleting Person on death.
- Fabricating heirs or population.
- "Respawn at nearest spawn point" without a causal pipeline.
- UI displaying time-of-death without epistemic knowledge.
- Any design that requires global iteration over all persons.

## Integration points (mandatory)
- Provenance: `docs/SPEC_PROVENANCE.md`
- Ledger: `docs/SPEC_LEDGER.md`
- Time scheduling: `docs/SPEC_SCHEDULING.md` and `docs/SPEC_TIME_CORE.md`
- Epistemic model: `docs/SPEC_INFORMATION_MODEL.md` and `docs/SPEC_EPISTEMIC_INTERFACE.md`
