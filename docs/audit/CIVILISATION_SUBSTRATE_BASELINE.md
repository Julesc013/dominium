Status: DERIVED
Last Reviewed: 2026-02-16
Version: 1.0.0
Scope: CIV-1/4 structural baseline

# Civilisation Substrate Baseline

## Summary
CIV-1 establishes deterministic, process-driven foundations for factions, affiliations, territory claims, and diplomacy stubs without adding economy/combat/survival semantics.

## Faction Model
- Truth-side assembly: `assembly.faction.*` represented in `universe_state.faction_assemblies`.
- Deterministic create/dissolve process surface:
  - `process.faction_create`
  - `process.faction_dissolve`
- Deterministic faction ID path:
  - auto: `faction.{H(founder_agent_id, created_tick)[:16]}`
  - override: explicit `inputs.faction_id` (must be unique)
- Ownership authority:
  - faction extension `owner_peer_id` enforces mutation ownership in multiplayer paths.
  - admin override allowed via entitlement path (`entitlement.control.admin` or `entitlement.civ.admin`).

## Affiliation Model
- Field substrate in `universe_state.affiliations`.
- Deterministic mutation processes:
  - `process.affiliation_join`
  - `process.affiliation_leave`
- `subject_id` supports agent IDs now and cohort IDs structurally for CIV-2 expansion.
- Duplicate join rejected with deterministic refusal:
  - `refusal.civ.already_affiliated`

## Territory Claim Rules
- Territory substrate in `universe_state.territory_assemblies`.
- Deterministic mutation processes:
  - `process.territory_claim`
  - `process.territory_release`
- Claim behavior:
  - unclaimed -> owner set, status `claimed`
  - conflicting owner -> status `contested`, contested set tracked deterministically
- Deterministic conflict tie-break for owner field in contested state:
  - lexical faction ordering to keep order-invariant output

## Diplomacy Stub
- Relation substrate in `universe_state.diplomatic_relations`.
- Process surface:
  - `process.diplomacy_set_relation`
- CIV-1 relation behavior:
  - symmetric updates over canonical pair `(min(faction_a,faction_b), max(...))`
  - relation states constrained by `data/registries/diplomatic_state_registry.json`
- No gameplay effects (war/trade mechanics deferred).

## Refusal Codes
- `refusal.civ.entitlement_missing`
- `refusal.civ.law_forbidden`
- `refusal.civ.already_affiliated`
- `refusal.civ.territory_invalid`
- `refusal.civ.claim_forbidden`
- `refusal.civ.relation_invalid`
- `refusal.civ.ownership_violation`

## Multiplayer Integration Notes
- Lockstep: CIV intents are carried as deterministic process intents.
- Server-authoritative: server remains authoritative over faction/territory/diplomacy state mutation.
- SRZ hybrid: ownership checks enforce peer/faction authority; invalid ownership mutation paths refuse deterministically.
- CIV changes remain process-log anchored and hash-stable.

## Guardrails
- RepoX:
  - `INV-CIV-PROCESSES-ONLY-MUTATION`
  - `INV-NO-PLAYER-FACTION-SPECIALCASE`
  - `INV-FACTION-ID-STABLE`
- AuditX analyzers:
  - `E30_FACTION_ORPHAN_SMELL`
  - `E31_TERRITORY_OWNERSHIP_DRIFT_SMELL`
- TestX coverage:
  - `testx.civilisation.faction_create_deterministic`
  - `testx.civilisation.affiliation_join_leave_deterministic`
  - `testx.civilisation.territory_claim_conflict_order`
  - `testx.civilisation.diplomacy_update_deterministic`
  - `testx.civilisation.no_agents_world_runs_ok`
  - `testx.civilisation.single_agent_world_runs_ok`

## Extension Points (CIV-2+)
- Cohort/population affiliation and macro cohort abstractions.
- Governance policy behaviors (`governance_type_id`) as solver/domain modules.
- Treaty metadata and directional diplomacy.
- Claim-to-conflict escalation integration (war/trade systems).
- Cross-shard faction governance and explicit global civ coordinator patterns.

