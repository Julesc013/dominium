Status: DERIVED
Last Reviewed: 2026-02-01
Supersedes: none
Superseded By: none

# FAB Interpreters (FAB-1)





Status: binding.


Scope: minimal, deterministic FAB interpreters in the engine/game stack.





## Purpose


Provide the smallest possible, content-agnostic execution layer for FAB-0 data.


Interpreters operate on schemas and fixed-point quantities, never on real-world


meaning.





## Responsibilities


- Material trait access, interpolation, and aggregation using fixed-point math.


- Interface compatibility checks by tag, directionality, and unit compatibility.


- Assembly graph validation and deterministic aggregation.


- Process-family execution adapter to the Process hooks.


- Quality and failure hooks as data-driven checks.


- Spatial placement and volume-claim validation (no geometry solvers).





## Non-responsibilities


- No gameplay rules or balance.


- No hardcoded domain semantics.


- No floating point in authoritative logic.


- No implicit content or pack requirements.





## Determinism guarantees


- All registry operations are deterministic for identical inputs.


- Aggregation order is independent of input ordering.


- Process outcomes use deterministic PRNG seeded by data-defined IDs.


- Unit and overflow enforcement is deterministic and refusal-based.





## Refusal semantics


All refusals map to canonical codes in `docs/architecture/REFUSAL_SEMANTICS.md`.


Refusals are explicit outcomes and do not mutate state.





## Code locations


- Public API: `game/include/dominium/fab/fab_interpreters.h`


- Implementation: `game/rules/fab/fab_interpreters.cpp`


- Shared enums: `engine/include/domino/fab.h`





## Extension points


- Add new schema fields via extensions and keep unknown fields round-trippable.


- Add new constraint types by extending data-driven constraint evaluation.


- Add new process families by data only; no code changes required.





## Common mistakes


- Missing unit annotations for numeric map fields.


- Using floating point in authoritative paths.


- Reusing IDs with new meanings.
