# Civilization Model (CIV0+)

Status: binding.
Scope: canonical civilization model for settlements, infrastructure,
institutions, governance, and macro-only societies.

Civilization exists because it is constructed, maintained, and governed.
Nothing appears for balance or convenience. Macro civilizations can persist
indefinitely without micro simulation; when refined, micro details must be
consistent with macro history.

## Core model (canonical)
- Settlements are constructed aggregations of infrastructure.
- Infrastructure provides capacity, not free output.
- Institutions enforce rules via resources and legitimacy.
- Governance is law layered on institutions and scoped to domains.
- Economy is conserved flow of goods and services.
- Logistics is scheduled movement along Travel edges.

## Macro and micro consistency
Macro layers track population totals, production rates, and trade balances.
When refined, micro details must satisfy macro totals, shortages, and debt.
Refinement cannot invent goods, people, or institutions. Micro detail is
realized only under refinement; there are no global per-citizen loops.

## Construction and maintenance
Every settlement or infrastructure unit must be created through explicit
construction effects and must be maintained. Neglect triggers decay and
capacity loss, not silent deletion.

## Anti-fabrication invariants
- No settlement without a construction contract.
- No infrastructure without construction and maintenance.
- No goods without production inputs.
- No governance without institutions and legitimacy.
- No logistics without Travel edges.

## Integration points
- Life and population: `docs/arch/LIFE_AND_POPULATION.md`
- Reality layer: `docs/arch/REALITY_LAYER.md`
- Economy and logistics: `docs/arch/ECONOMY_AND_LOGISTICS.md`
- Governance: `docs/arch/GOVERNANCE_AND_INSTITUTIONS.md`
- Collapse and decay: `docs/arch/COLLAPSE_AND_DECAY.md`

## See also
- `schema/civ/README.md`
- `schema/economy/README.md`
