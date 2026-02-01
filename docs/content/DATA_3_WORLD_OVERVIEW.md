Status: DERIVED
Last Reviewed: 2026-02-01
Supersedes: none
Superseded By: none

# DATA-3 World Overview

Purpose: Provide data-only world anchors, ecology, population, settlements, trade, and civilization stress so richer worlds can be described without code or era logic.

Packs and maturity:
- org.dominium.worldgen.anchors.planetary — STRUCTURAL
- org.dominium.worldgen.anchors.system — BOUNDED
- org.dominium.core.ecology.basic — PARAMETRIC
- org.dominium.core.population.basic — PARAMETRIC
- org.dominium.core.settlements.basic — STRUCTURAL
- org.dominium.core.infrastructure.basic — STRUCTURAL
- org.dominium.core.trade.basic — STRUCTURAL
- org.dominium.core.civ_stress.basic — BOUNDED

How emergence works (data-only):
- World anchors define topology nodes and base fields, nothing more.
- Ecology uses field-driven growth/decay/reproduction processes.
- Population uses field-driven birth/death/migration/role-shift processes.
- Settlements and infrastructure are anchors with capacity, loss, and maintenance processes.
- Trade is modeled via exchange, price adjustment, and transport cost processes.
- Civilization stress uses field indicators, shock/recovery processes, and parameterized institutional failure.

Known limitations and extension paths:
- No solver logic is included; anchors are intentionally abstract.
- Field semantics are not encoded in code; only tags and unit annotations exist.
- If a new interaction cannot be expressed, add new data fields/processes or document gaps for CODE-2.

Notes on law and regulation:
- Anarchy vs regulation remains data-driven via pack selection and policies (see DATA-2).
- DATA-3 does not add or alter law mechanisms.