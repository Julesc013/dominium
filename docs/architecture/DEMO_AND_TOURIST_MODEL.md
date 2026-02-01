Status: CANONICAL
Last Reviewed: 2026-02-01
Supersedes: none
Superseded By: none

# Demo and Tourist Model (TESTX3)





Status: binding.


Scope: base_free and tourist authority behavior.





## Core invariants


- INVARIANT: AUTH3-DEMO-003 — Demo is an authority profile, not a build.


- INVARIANT: AUTH3-TOURIST-004 — Tourists never mutate authoritative state.


- INVARIANT: AUTH3-SAVE-008 — base_free/tourist saves are non-authoritative.





## Base_free authority


Allows:


- offline sandbox play


- limited singleplayer


- full renderer/UI


- replay viewing


- content inspection





Disallows:


- persistent progression


- authoritative saves


- economic impact


- competitive multiplayer


- mod/tool export





## Tourist authority


Allows:


- connect to real servers


- observe real worlds and players


- move within server-defined limits





Disallows:


- authoritative mutation


- progression or economic value extraction





## Refusal semantics


Tourist/base_free attempts to perform disallowed actions:


- must be refused explicitly


- must be logged


- must not alter authoritative state





## Cross-references


- `docs/architecture/AUTHORITY_AND_ENTITLEMENTS.md`


- `docs/architecture/PIRACY_CONTAINMENT.md`
