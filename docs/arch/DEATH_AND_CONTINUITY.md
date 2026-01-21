# Death and Continuity (LIFE0+)

Status: binding.
Scope: death, estate, continuation, and reincarnation rules.

Death is an explicit effect. Identity does not silently disappear, and all
post-death actions are audited.

## Invariants
- No death without a DeathContract effect.
- Identity does not disappear; it is archived or continued by contract.
- Refusal or deferral is valid and auditable.

## Death is explicit
Death requires a DeathContract and produces:
- a death event record,
- audit and provenance entries,
- estate and remains records when applicable.

Outcomes are deterministic:
- DEATH_ACCEPT
- DEATH_DEFER (e.g., dying state)
- DEATH_REFUSE (rare, protected entities)

## Continuity is configuration
Continuation and reincarnation are configuration, not modes:
- Hardcore: no reincarnation; identity ends in-place.
- Softcore: reincarnation allowed only via contract.
- Spectator: no life entity bound to the controller.

All continuation requires explicit authority and audit.

## Estates, remains, and audit
- Estates preserve assets and obligations; transfers occur only via ledger.
- Remains persist deterministically and decay via ACT scheduling.
- Knowledge of death is epistemic; UI is gated by observation or comms.

## Dependencies
- Reality flow: `docs/arch/REALITY_FLOW.md`
- Identity and lineage: `schema/life/SPEC_IDENTITY_AND_LINEAGE.md`
- Death contracts: `schema/life/SPEC_DEATH_CONTRACTS.md`
- Reincarnation: `schema/life/SPEC_REINCARNATION.md`
- Death/estate legacy guide: `schema/life/SPEC_DEATH_AND_ESTATE.md`

## Forbidden assumptions
- Death can be silent or implicit.
- Reincarnation is default or free.

## See also
- `docs/arch/IDENTITY_ACROSS_TIME.md`
- `docs/arch/LIFE_AND_POPULATION.md`
