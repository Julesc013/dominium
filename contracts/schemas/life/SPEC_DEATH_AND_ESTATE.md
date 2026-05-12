--------------------------------
OWNERSHIP & RESPONSIBILITY
--------------------------------
ENGINE:
- ACT time and deterministic event scheduling primitives.
- Ledger primitives for assets/obligations.
GAME:
- Death triggers, estate orchestration, and contract integration.
- Cause-of-death policies and jurisdictional rules.
SCHEMA:
- Death event records, estate records, and enum definitions.
TOOLS:
- Future inspectors/editors only (no runtime behavior).
FORBIDDEN:
- No runtime logic in schema specs.
- No automatic respawn or magic transfers.
- No UI truth leaks without epistemic knowledge.
DEPENDENCIES:
- Engine -> (no dependencies outside engine/).
- Game -> engine public API only.
- Schema -> none (formats only).
- Tools -> schema + engine/game public APIs only.
--------------------------------
# SPEC_DEATH_AND_ESTATE — Death Event & Estate Canon

Status: legacy (superseded by LIFE0+)
Version: 1

Note: LIFE0+ canonical specs live in `schema/life/SPEC_DEATH_CONTRACTS.md` and
`schema/life/SPEC_IDENTITY_AND_LINEAGE.md`. This document remains for legacy
context; if any statement conflicts with LIFE0+, LIFE0+ wins.

## Purpose
Define deterministic death events and estate creation. This is a schema and
invariant specification only; implementation is deferred.

## Death event model (mandatory)
Death is a deterministic event that transitions a body to dead and creates an
estate. The person identity persists.

Death pipeline (conceptual):
1) Body alive_state -> dead (or missing -> declared_dead).
2) Person persists unchanged.
3) Estate record created and linked.
4) Ledger obligations and contracts persist.
5) Provenance record emitted.
6) Epistemic knowledge of death is updated only via observation or comms.

### DeathEvent schema (conceptual)
Required fields:
- death_event_id (stable)
- person_id
- body_id
- act_tick
- cause_code (enum)
- location_ref (world coord or shard key)
- provenance_id
- estate_id (created by this event)

Optional fields:
- declared_by_authority_id
- declaration_tick (if missing -> declared_dead)
- notes_ref (non-sim metadata)

### Cause-of-death classification (minimal enum)
- NATURAL
- ACCIDENT
- VIOLENCE
- EXECUTION
- UNKNOWN
- MISSING_DECLARED

Cause-of-death is epistemic; it can be UNKNOWN even if death is known.

## Estate model (mandatory)
An estate is a deterministic record used to resolve assets, rights, and
obligations after death.

### Estate schema (conceptual)
Required fields:
- estate_id
- deceased_person_id
- ledger_account_ids (references)
- contract_refs (obligations, claims, liens)
- jurisdiction_id
- organization_id (if applicable)
- resolution_schedule (ACT ticks or recurrence reference)
- status (open | resolving | closed)

Optional fields:
- executor_authority_id
- audit_trail_ref

## Remains & salvage model (mandatory)
Remains persist deterministically after death and are the only lawful source
for post-death recovery. Remains are not globally known; discovery is
epistemic.

### Remains schema (conceptual)
Required fields:
- remains_id
- person_id (identity link)
- body_id (embodiment link)
- location_ref
- created_act
- state (fresh | decayed | skeletal | unknown | collapsed)
- ownership_rights_ref (post-death rights)
- next_due_tick (for decay scheduling)
- provenance_ref

Optional fields:
- inventory_account_id (ledger account for carried items)
- active_claim_id

### Post-death rights schema (conceptual)
Required fields:
- rights_id
- estate_id
- jurisdiction_id
- has_contract
- allow_finder
- jurisdiction_allows
- estate_locked

Rights resolution order (deterministic):
1) Explicit contract
2) Estate executor (if authorized)
3) Jurisdiction default
4) Finder policy (if allowed)
5) Refusal

### Salvage claims (conceptual)
Required fields:
- claim_id
- claimant_id
- claimant_account_id
- remains_id
- claim_basis (contract | executor | jurisdiction | finder)
- status (pending | accepted | refused)
- resolution_tick
- refusal_code

Salvage outcomes MUST produce ledger transactions and provenance entries.

### Decay & persistence
- Remains decay is event-driven using ACT ticks (no global scans).
- Decay stages are deterministic and batch/step invariant.
- Collapse/refine MUST preserve counts and provenance summary hashes.

## Epistemic knowledge of death
- The death event is authoritative; knowledge of death is not.
- Knowledge must be produced by sensors or communication (INF0/INF2).
- UI MUST NOT display death time or cause unless epistemically known.

## Event-driven requirements
- Estate resolution is scheduled via ACT ticks (no global scans).
- Resolution uses deterministic queues and stable ordering keys.
- Batch vs step invariance must hold for estate resolution events.

## Implementation notes (LIFE2)
- Runtime code lives under `game/include/dominium/life/*` and `game/core/life/*`.
- The death pipeline entrypoint is `life_handle_death(...)` and is deterministic.
- Estate creation copies and sorts account IDs and reassigns ownership to the estate.
- Inheritance scheduling uses the due-event scheduler and emits `InheritanceAction` records.
- Epistemic visibility is provided via an explicit death-notice callback; no implicit broadcasts exist.

## Implementation notes (LIFE4)
- Remains creation is part of the death pipeline and emits audit log entries.
- Remains decay is scheduled via the due-event scheduler (no global iteration).
- Post-death rights records are created alongside remains.
- Salvage claims resolve deterministically and use ledger transactions only.
- Remains discovery is emitted via explicit observation hooks (no omniscient broadcast).

## Prohibitions (absolute)
- Deleting Person on death.
- Fabricating heirs or assets.
- Implicit asset transfers without ledger transactions.
- UI showing time-of-death without epistemic knowledge.
- Global iteration over all estates or persons.

## Test plan (spec-level)
Implementations MUST provide tests for:
- deterministic death -> estate creation
- deterministic control transfer selection (when linked to policies)
- refusal when no eligible person exists (hardcore)
- replay equivalence for death and estate events
- batch vs step invariance for scheduled estate resolution
- epistemic correctness (death knowledge delayed via sensors/comms)
- deterministic remains creation and decay scheduling
- salvage rights resolution order determinism
- ledger conservation during salvage transfers
- epistemic gating for salvage attempts
- collapse/refine count and provenance hash preservation

## Integration points (mandatory)
- Provenance: `docs/specs/SPEC_PROVENANCE.md`
- Ledger: `docs/specs/SPEC_LEDGER.md`
- Time scheduling: `docs/specs/SPEC_SCHEDULING.md`
- Epistemic model: `docs/specs/SPEC_INFORMATION_MODEL.md` and `docs/specs/SPEC_COMMUNICATION.md`
