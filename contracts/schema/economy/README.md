# Economy Schema Specs (CIV0+)





Status: draft


Version: 1





This directory contains canonical CIV0+ economy schema specifications for


economic actors, production chains, markets, logistics, and conservation.


These documents define authoritative data formats and invariants only; no


runtime logic is introduced here.





Scope: economy actor, production, market, logistics, and conservation formats.





## Invariants


- No goods without production inputs and contracts.


- Logistics uses travel edges and schedules only.


- Schemas do not encode runtime logic.





## Forbidden assumptions


- Markets create goods or value.


- Schema defaults imply free resources.





## Dependencies


- `docs/architecture/ECONOMY_AND_LOGISTICS.md`


- `schema/domain/civilization/README.md`





## Canonical CIV0+ economy index


- `schema/economy/SPEC_ECONOMIC_ACTORS.md`


- `schema/economy/SPEC_PRODUCTION_CHAINS.md`


- `schema/economy/SPEC_MARKETS_AND_EXCHANGE.md`


- `schema/economy/SPEC_LOGISTICS.md`


- `schema/economy/SPEC_RESOURCE_CONSERVATION.md`





## Related civilization specs (CIV0+)


- `schema/domain/civilization/SPEC_SETTLEMENTS.md`


- `schema/domain/civilization/SPEC_INFRASTRUCTURE.md`


- `schema/domain/civilization/SPEC_INSTITUTIONS.md`


- `schema/domain/civilization/SPEC_ORGANIZATIONS.md`


- `schema/domain/civilization/SPEC_GOVERNANCE.md`


- `schema/domain/civilization/SPEC_LEGITIMACY.md`





## Versioning policy


All economy schemas follow `schema/SCHEMA_VERSIONING.md` and


`schema/SCHEMA_MIGRATION.md`:


- Every schema has `schema_id`, semantic version, and stability level.


- MAJOR bumps require explicit migration or refusal.


- MINOR bumps must be skip-unknown safe (unknown fields preserved).


- PATCH changes must not alter simulation behavior.





Schemas in this directory are authoritative for data formats and validation


rules. Runtime behavior lives in `game/` and must not be encoded here.





Reality and civilization integration:


- `docs/architecture/REALITY_LAYER.md`


- `docs/architecture/CIVILIZATION_MODEL.md`
