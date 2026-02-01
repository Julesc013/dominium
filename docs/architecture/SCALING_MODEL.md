Status: CANONICAL
Last Reviewed: 2026-02-01
Supersedes: none
Superseded By: none

# Scaling Model (SCALE0)





Status: binding.


Scope: authoritative scaling across space/time without breaking determinism or small-scale correctness.





## Purpose


Define the canonical scaling philosophy and the allowed representations of


simulation state across fidelity tiers.





## Core rule


> Small-scale simulation is the ground truth.  


> Large-scale simulation must be a semantics-preserving projection of it.





Scaling may:


- approximate


- aggregate


- defer


- collapse





Scaling MUST NOT:


- contradict micro truth


- invent resources or entities


- violate conservation


- change outcomes when expanded back





## Fidelity tiers (canonical)


1) LATENT / SYMBOLIC (Tier 0)


   - Aggregated fields


   - Statistical summaries


   - No instantiated entities


   - Time may advance in large steps





2) OPERATIONAL (Tier 1)


   - Entities exist


   - Coarse stepping


   - Bounded local interactions





3) CRITICAL / LOCAL (Tier 2)


   - High precision


   - Fine stepping


   - Structural, safety, and commit-critical checks





These are NOT different engines. They are scheduling and representation


policies over the same primitives:


- Same Work IR + Access IR.


- Same law gates and authority checks.


- Same deterministic reductions and commit ordering.





## Determinism and replay


- Scaling transitions only occur at commit boundaries.


- Collapse/expand is deterministic and replay-safe.


- Macro stepping uses ACT and event logs; no wall-clock coupling.





## Forbidden assumptions


- Macro state can override or rewrite micro outcomes.


- View/camera state may activate simulation.


- Non-deterministic sampling is acceptable without explicit seeds.





## See also


- `docs/architectureitecture/SCALE_AND_COMPLEXITY.md`


- `docs/architectureitecture/REFINEMENT_CONTRACTS.md`


- `docs/architectureitecture/EXECUTION_MODEL.md`


- `docs/architectureitecture/INTEREST_MODEL.md`


- `docs/architectureitecture/INVARIANTS_AND_TOLERANCES.md`


- `docs/architectureitecture/COLLAPSE_EXPAND_CONTRACT.md`


- `docs/architectureitecture/MACRO_TIME_MODEL.md`
