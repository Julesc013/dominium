# Law And Meta-Law Split (LAWMETA0)

Status: binding.
Scope: the permanent separation between simulated in-world law and operational meta-law.

## In-world law
In-world law is part of the simulated reality. It is:
- data-driven
- simulated and historical
- enforced by institutions, jurisdictions, and processes
- able to affect outcomes and history

Examples of in-world law:
- who may enter or control a domain
- which contracts or obligations are enforceable
- which institutions may authorize specific actions

Non-examples:
- thread limits
- debug toggles
- operator maintenance windows

## Meta-law
Meta-law governs the operation of the engine and server boundary. It is:
- operational and extra-historical
- not part of the simulated timeline
- responsible for budgets, safety, determinism, and operability
- enforced at admission, scheduling, and commit boundaries

Examples of meta-law:
- budget enforcement and refusal semantics
- capability baselines and SKU gating
- determinism guards and anti-entropy rules
- debug and audit modes that do not change history

Non-examples:
- property disputes or rights inside the simulation
- historical changes to institutions or jurisdictions

## Interaction rules
- In-world law may refuse or transform in-world actions.
- Meta-law may refuse or defer work for operational reasons.
- Meta-law MUST NOT fabricate in-world outcomes.
- In-world law changes are historical events; meta-law changes are not.

## See also
- `docs/architecture/LAW_ENFORCEMENT_POINTS.md`
- `docs/architecture/BUDGET_POLICY.md`
- `docs/architecture/REFUSAL_SEMANTICS.md`
- `docs/architecture/ANTI_ENTROPY_RULES.md`
