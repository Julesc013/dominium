# MMO Safety Model (MMO0)

Status: binding.
Scope: abuse boundaries enforced via budgets, refusal semantics, and
authority roles only.

## Anarchy rule (clarified)

"Anarchy" means:

- minimal gameplay restrictions
- no content censorship as a primary system rule
- no artificial progression gates as a distribution mechanism

It does not mean:

- unlimited resource consumption
- denial-of-service tolerance
- unbounded intent spam

## Canonical enforcement mechanisms

All enforcement MUST be expressed through existing canon mechanisms:

- budgets and admission control
- refusal semantics and explicit deferrals
- authority roles and capability baselines

No hidden moderation logic is allowed in the authoritative simulation.

## Abuse boundaries as policy, not hacks

Abuse resistance is expressed as deterministic policy:

- budgets bound per-tick and per-commit work
- refusal and deferral outcomes are logged and replayable
- authority and capability checks are explicit

## Determinism under abuse pressure

Under abusive load, the system MUST:

- refuse or defer explicitly
- remain deterministic and auditable
- avoid silently dropping simulation work

## Related invariants

- SCALE3-BUDGET-009
- SCALE3-ADMISSION-010
- MMO0-UNIVERSE-012
- MMO0-COMPAT-018

## See also

- `docs/architecture/BUDGET_POLICY.md`
- `docs/architecture/REFUSAL_SEMANTICS.md`
- `docs/architecture/ANTI_CHEAT_AND_INTEGRITY.md`
