Status: CANONICAL
Last Reviewed: 2026-02-01
Supersedes: none
Superseded By: none

# Services and Products (TESTX3)





Status: binding.


Scope: optional services and product boundaries.





## Core invariants


- INVARIANT: AUTH3-SERVICE-005 — Services affect access only.


- INVARIANT: AUTH3-UPGRADE-007 — Authority changes do not mutate world state.





## Service rules


Services MAY:


- grant temporary authority


- unlock premium universes


- provide hosted servers


- provide compute-heavy features


- provide events/seasons





Services MUST:


- affect access only


- never rewrite history


- never invalidate replays


- never alter past state





Services MAY expire.


Expired services MUST degrade authority cleanly and explicitly.





## Product boundaries


- Engine/game are authority consumers only.


- Launcher/platform/cloud handle entitlements and service issuance.


- No secrets live in engine/game.





## Required response prompts


Each team MUST respond to TESTX3 with:


- Accept/Reject for each section.


- Frozen interfaces (what cannot change).


- Tests to add.


- Expectations of other teams.





Teams:


1) Engine/Game team


2) Application/Platform team


3) Services/Backend team


4) Tools/Modding team





## Cross-references


- `docs/architecture/AUTHORITY_AND_ENTITLEMENTS.md`


- `docs/architecture/DISTRIBUTION_AND_STOREFRONTS.md`
