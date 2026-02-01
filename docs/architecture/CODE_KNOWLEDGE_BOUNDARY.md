Status: CANONICAL
Last Reviewed: 2026-02-01
Supersedes: none
Superseded By: none

# Code Knowledge Boundary (CODEKNOW0)





Status: binding.


Scope: what authoritative code is allowed to know versus what must remain data-owned meaning.





This document complements:


- `docs/architecture/CODE_DATA_BOUNDARY.md`


- `docs/architecture/EXTEND_VS_CREATE.md`


- `docs/architecture/WORLDDEFINITION_CONTRACT.md`





## Code may know (mechanisms only)


Authoritative code MAY know and implement:


- how to evaluate constraints and invariants


- how to execute processes and schedule work


- how to aggregate and sample deterministically


- how to enforce authority, budgets, and refusal semantics


- how to serialize and deserialize stable formats





These are mechanism concerns and are part of the engine and game substrate.





## Code must not know (meaning and content)


Authoritative code MUST NOT embed:


- real-world domain semantics such as "steel", "engine", or "gun"


- era, progression, or tech-tree assumptions


- balance expectations such as "this should be strong" or "cheap"


- content-specific meaning such as fixed resource or item taxonomies





These are data concerns. They belong in packs, schemas, and registries.





## Explicit violation examples


These are architectural violations even if they "work":


- `if material_id == "steel": hardness = 5`


- `if era >= 3: unlock_feature("rifle")`


- `damage *= 1.10  # because swords need a buff`


- `if item_type == "food": decay_rate = 0.01`





The correct pattern is to read data-owned parameters by stable identifiers.





## Enforcement expectations


- Prefer registry lookups over string comparisons in hot paths.


- Reject or preserve unknown identifiers; do not guess meaning.


- Keep public APIs content-agnostic and capability-gated.





## See also


- `docs/architecture/REGISTRY_PATTERN.md`


- `docs/architecture/ID_AND_NAMESPACE_RULES.md`


- `docs/architecture/PROCESS_ONLY_MUTATION.md`
