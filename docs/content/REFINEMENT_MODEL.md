Status: DERIVED
Last Reviewed: 2026-02-01
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: patched document aligned to current canon ownership and release scope

# Refinement and Representation Tiers

## Patch Notes

- Current status: partially aligned to the Constitutional Architecture and release-freeze documentation set.
- Required updates: documentation surface exists, but current canon ownership is not explicit
- Cross-check with: `docs/audit/CANON_MAP.md` and `docs/audit/DOC_DRIFT_MATRIX.md`.






This document defines how representation tiers describe content detail without


changing simulation truth. It MUST be read alongside


`docs/architectureitecture/TERMINOLOGY.md`.





## Tiers





- Explicit: stored facts at the declared LOD.


- Hybrid: explicit macro facts plus procedural refinement below the ceiling.


- Procedural: generated detail within declared constraints.





Tiers are metadata only. They MUST NOT change simulation logic.





## Refinement Ceiling





Each record MUST declare a `refinement_ceiling` in its extensions. This ceiling


defines the highest LOD for which the record provides authoritative detail.





## Explicit Absence of Detail





Each record MUST declare `detail_absence` in its extensions. This describes


what is intentionally NOT provided (for example: no geometry, no population,


no micro-scale physics).





## Combining Tiers





- Explicit data defines a floor, not a limit.


- Procedural refinement MAY fill in details below the ceiling, but MUST NOT


  contradict explicit facts.


- Hybrid data declares both the explicit floor and the procedural ceiling.





## Unknown and Latent Data





Unknown or latent state MUST remain explicit as missing or inferred data. It


MUST NOT be silently invented by representation metadata.
