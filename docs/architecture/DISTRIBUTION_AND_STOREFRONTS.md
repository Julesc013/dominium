Status: CANONICAL
Last Reviewed: 2026-02-01
Supersedes: none
Superseded By: none

# Distribution and Storefronts (TESTX3)





Status: binding.


Scope: single distribution model and storefront rules.





## Core invariants


- INVARIANT: AUTH3-DEMO-003 — Demo is an authority profile, not a build.


- INVARIANT: AUTH3-ENT-002 — Entitlements gate issuance only.





## Single distribution rule


There is exactly one distribution:


- same executables


- same content packs


- same code paths





Storefront purchase grants an entitlement.


Entitlement upgrades authority only.





## Storefront rules


- No reinstall required.


- No forked code paths.


- No surprise paywalls.


- No bait-and-switch.





## Refusal semantics


When entitlements are missing:


- authority issuance is refused


- refusal reason is explicit


- base_free remains available





## Cross-references


- `docs/architecture/DEMO_AND_TOURIST_MODEL.md`


- `docs/architecture/UPGRADE_AND_CONVERSION.md`
