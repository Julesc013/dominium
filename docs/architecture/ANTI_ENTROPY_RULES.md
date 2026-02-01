Status: CANONICAL
Last Reviewed: 2026-02-01
Supersedes: none
Superseded By: none

# Anti-Entropy Rules (ENTROPY0)





Status: binding.


Scope: anti-entropy guarantees that prevent drift and convenience shortcuts.





## Rules (non-negotiable)


- No shortcuts: never bypass law, audit, or capability gates for convenience.


- No UI authority: UI and presentation layers never mutate authoritative state.


- No era logic: do not hardcode "eras" or progression markers into core systems.


- No hardcoded world assumptions: do not assume Earth, Sol, gravity, or real-world defaults.





## Enforcement references


These rules MUST be referenced by:


- Code reviews (checklist includes ENTROPY0).


- TESTX (contract tests must verify presence and compliance).


- future prompts (prompts must cite ENTROPY0).





## See also


- `docs/architecture/ARCH0_CONSTITUTION.md`


- `docs/architecture/INVARIANTS.md`


- `docs/architecture/SEMANTIC_STABILITY_POLICY.md`
