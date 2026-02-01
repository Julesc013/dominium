Status: CANONICAL
Last Reviewed: 2026-02-01
Supersedes: none
Superseded By: none

# Control Non-Interference (TESTX2)





Status: binding.


Scope: control layers must never modify authoritative outcomes.





## Invariant


Control layers may gate access, connectivity, or execution. They must never:


- alter authoritative simulation results


- alter ordering or timing


- alter state transitions


- introduce nondeterminism


- invalidate replays or archival verification





## Allowed effects


- Refusal before execution (deny access, disconnect, or halt launch).


- Logging, reporting, and audit trails.


- External policy enforcement outside engine/game.





## Forbidden effects


- Performance degradation or hidden penalties.


- Probability skewing or deterministic drift.


- Silent fallback paths that mask enforcement.


- Any mutation of authoritative state driven by control policy.





## Enforcement


- Tests in `tests/control/interference/`


- Invariant definitions in `docs/architecture/INVARIANTS.md`


- Disclosure rules in `docs/architecture/AUDITABILITY_AND_DISCLOSURE.md`
