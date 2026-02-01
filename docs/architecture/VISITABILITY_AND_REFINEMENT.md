Status: CANONICAL
Last Reviewed: 2026-02-01
Supersedes: none
Superseded By: none

# Visitability and Refinement (REALITY0)





Status: binding.


Scope: definitive contract for visitability and refinement.





Reachable is not visitable. Visitability is the extra contract that turns


reachability into a lawful, refinable arrival.





## Visitability contract (canonical)


A location is VISITABLE iff:


1) It is reachable via the Travel Graph.


2) The destination domain permits entry.


3) Law and capability allow the visit.


4) Existence state is REFINABLE or REALIZED.


5) A valid refinement contract exists.


6) Budget allows refinement, or defers deterministically.





If any condition fails, the outcome is explicit refusal or deferral.





## Invariants


- If a location cannot be refined, it must be unreachable.


- Placeholder or fake micro worlds are forbidden.


- Refinement is contract-driven; collapse preserves conservation and provenance.


- Admin or tool overrides still require law-gated effects and audit.





## Refinement and collapse summary


Refinement:


- deterministic realization from macro state,


- uses declared seeds and invariants,


- produces auditable outputs.





Collapse:


- deterministic aggregation back to macro state,


- preserves pinned/observed entities and history,


- never erases provenance.





## Forbidden assumptions


- Reachability implies visitability without contracts.


- Refinement can fabricate micro state without provenance.





## Dependencies


- Travel graph: `schema/travel/README.md`


- Domain visitability: `schema/domain/README.md`


- Refinement contracts: `schema/existence/SPEC_REFINEMENT_CONTRACTS.md`





## See also


- `docs/architecture/REALITY_LAYER.md`


- `docs/architecture/REFINEMENT_CONTRACTS.md`


- `docs/architecture/VISITABILITY_AND_REALITY.md`


- `docs/architecture/VISITABILITY_CONSISTENCY.md`


- `schema/existence/SPEC_REFINEMENT_CONTRACTS.md`
