Status: CANONICAL
Last Reviewed: 2026-02-01
Supersedes: none
Superseded By: none

# Scaling Compatibility (SCALE0)





Status: binding.


Scope: mandatory vs optional scaling features and legacy behavior.





## Mandatory (all SKUs)


- The three-tier model exists (Tier 0/1/2 as policy, not engine forks).


- Interest-driven activation rules are honored.


- Macro capsules obey the collapse/expand contract.


- Invariants and tolerances are enforced.


- Deterministic execution and replay guarantees hold.


- Budget/refusal behavior is explicit and auditable.





## Optional variants (per SKU/capability)


- Macro model implementations (economy, logistics, population).


- Statistical encoding formats for sufficient statistics.


- Interest prioritization heuristics within budget.


- Scheduling backends (single-thread vs parallel) that preserve determinism.





All variants MUST preserve invariants, determinism, and replay equivalence.





## Legacy SKU behavior


Legacy SKUs MUST be explicit about supported tiers and expansion capability.





### Symbolic-only macro simulation


- Supports Tier 0 only.


- Any request that requires Tier 1/2 expansion MUST refuse explicitly.





### Frozen inspect mode


- Allows read-only inspection of macro capsules.


- No expansion or authoritative mutation is permitted.





### Unsupported expansion


- MUST refuse with REFUSE_CAPABILITY_MISSING when capability is absent.


- MUST refuse with REFUSE_BUDGET_EXCEEDED when budget is the limiting factor.


- MUST log refusal/deferral events for replay.





## Capability baselines


Scaling support is expressed as capabilities and may be constrained by baseline


profiles (`docs/architecture/CAPABILITY_BASELINES.md`). Baselines may restrict tiers,


expansion, or macro stepping but MUST still obey this contract.





## UPS compatibility


Macro capsules are serializable artifacts and MUST be UPS-compatible. Any


packaged capsule data MUST follow pack rules and namespacing.





## See also


- `docs/architecture/CAPABILITY_BASELINES.md`


- `docs/architecture/REFUSAL_SEMANTICS.md`


- `docs/architecture/PACK_FORMAT.md`


- `docs/architecture/SCALING_MODEL.md`
