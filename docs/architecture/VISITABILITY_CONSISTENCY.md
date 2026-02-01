Status: CANONICAL
Last Reviewed: 2026-02-01
Supersedes: none
Superseded By: none

# Visitability Consistency (EXIST1)





Status: deprecated.


Scope: historical definition of visitability and "alive" without global micro simulation.





Deprecated by `docs/architecture/VISITABILITY_AND_REFINEMENT.md`, which is the canonical


REALITY0 visitability contract. This document remains for context but is no


longer authoritative.





## Definition: Visitable


A subject is VISITABLE if:


- it is reachable, AND


- it is REFINABLE with a valid contract, AND


- refusal conditions are not met.





If a subject is not visitable:


- it may still exist as DECLARED/LATENT macro systems.


- travel/interaction must not allow physical reachability.





## Definition: Alive


An "alive" subject satisfies:


- conservation and provenance invariants at macro level.


- refinement contracts that can realize micro detail deterministically.


- no contradictions with observed history.





## Consistency Rules


- Refinement does not fabricate history or state.


- Denial/deferral is explicit and auditable.


- Collapses preserve pinned and visible entities.


- Budget limits affect performance, not truth.





## Integration Points


- Domain volumes: reachability defines visitability.


- Law kernel: refinement and collapse are gated.


- Work IR: refinement/collapse are explicit effects.


- Sharding: ownership respects existence and visitability.





## References


- `schema/existence/SPEC_REFINEMENT_CONTRACTS.md`


- `schema/existence/SPEC_REFINEMENT_DENIAL.md`


- `docs/architecture/VISITABILITY_AND_REFINEMENT.md`
