Status: DERIVED
Last Reviewed: 2026-02-01
Supersedes: none
Superseded By: none

# Refinement Lattice





Status: canonical.


Scope: definition of refinement layers and collapse.


Authority: canonical. All refinement behavior MUST follow this contract.





## Formal lattice definition


The refinement lattice is the ordered set of truth-preserving layers applied to


a target. Each layer MUST add detail without contradicting existing truth.





## Base procedural truth


- Base procedural truth MUST provide the minimum coherent state required by


  invariants and declared content.


- Base truth MUST be deterministic for the same seeds and inputs.


- Base truth MUST NOT encode realism or domain-specific laws.





## Refinement layers


- Each refinement layer MUST declare its applicable target, fields, and LOD


  bounds.


- A refinement layer MUST NOT contradict any parent invariant or previously


  established truth.


- A refinement layer MUST NOT remove truth. It MAY clarify unknowns but SHALL


  NOT negate prior truth.


- Refinement order MUST be deterministic and explicitly declared.





## Domain-scoped overrides


- Overrides MUST be scoped to explicit domains or topology nodes.


- Overrides MUST NOT leak outside declared scope.


- Overrides MUST be additive or constraining; they MUST NOT rewrite unrelated


  truth.





## LOD-bounded refinement


- Every refinement MUST declare an LOD_min..LOD_max band.


- Refinement outputs MUST be limited to that band and MUST NOT imply precision


  outside it.


- Refinement ceilings MUST be explicit and enforced.





## Collapse rules


- Collapse is a deterministic reduction to a coarser representation.


- Collapse MUST NOT change objective truth; it only reduces representation


  detail.


- Collapse MUST preserve provenance and auditability.


- Collapse MUST be achievable through the same refinement contract used for


  refinement.





## References


- `docs/worldgen/REFINEMENT_CONTRACT.md`


- `docs/architectureitecture/INVARIANTS.md`
