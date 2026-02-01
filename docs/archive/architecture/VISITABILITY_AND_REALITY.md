Status: HISTORICAL
Last Reviewed: 2026-02-01
Supersedes: none
Superseded By: docs/architecture/VISITABILITY_AND_REFINEMENT.md

This document is archived.
Reason: Superseded by docs/architecture/VISITABILITY_AND_REFINEMENT.md.
Do not use for implementation.

This document is archived.
Reason: Superseded by docs/architecture/VISITABILITY_AND_REFINEMENT.md.
Do not use for implementation.

This document is archived.
Reason: Superseded by docs/architecture/VISITABILITY_AND_REFINEMENT.md.
Do not use for implementation.

# Visitability and Reality (DOMAIN4)





Status: deprecated.


Scope: historical summary of visitability and reachability.





Deprecated by `docs/architecture/VISITABILITY_AND_REFINEMENT.md`, which is the canonical


REALITY0 visitability contract. This document remains for context but is no


longer authoritative.





## Core Promise


If a location can be reached, it is real, consistent, and refinable.


If it cannot be refined, it must be unreachable.





## Definitions


Reachable:


- A valid travel path exists.


- All traversed domains permit entry.


- Law and capability checks pass.


- Time/capacity can be scheduled.





Visitable:


- Reachable, AND


- existence_state is REFINABLE or REALIZED, AND


- a refinement contract exists, AND


- refusal conditions are not met.





## Visitability Pipeline


1) Travel feasibility (TRAVEL graph + schedule)


2) Domain permission (DOMAIN volumes)


3) Existence state (EXIST0)


4) Refinement contract (EXIST1)


5) Budget gate (EXEC/HWCAPS)


6) Outcome (accept, defer, refuse)





## Budget and Degradation


Budget pressure can:


- defer a visit deterministically


- degrade refinement fidelity (meso vs micro)


Budget pressure must not:


- allow visits without refinement


- fabricate placeholder environments





## Admin Overrides


Admin capability may bypass visit checks, but:


- must emit explicit effects


- must log audit records


- must respect archival rules (fork before mutation)





## Why Fake Worlds Cannot Exist


- Declared/latent targets are unreachable by normal travel.


- Refinement contracts are mandatory for visitability.


- Archived/frozen states block entry unless forked.


- Uncertainty yields refusal or deferral, not optimistic acceptance.





## References


- `schema/domain/SPEC_REACHABILITY.md`


- `schema/domain/SPEC_VISITABILITY.md`


- `docs/architecture/EXISTENCE_AND_REALITY.md`


- `docs/architecture/VISITABILITY_AND_REFINEMENT.md`
