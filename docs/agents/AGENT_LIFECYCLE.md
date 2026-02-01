Status: CANONICAL
Last Reviewed: 2026-02-01
Supersedes: none
Superseded By: none

# Agent Lifecycle (AGENT0)

Status: binding.
Scope: creation, persistence, transformation, and termination contracts.

## Lifecycle contract
1) Creation
   - Agents MUST be created only via processes.
   - Creation MUST include provenance from the creating process.
2) Persistence
   - Agents MUST persist across save/load.
   - `agent_id` MUST remain stable across time and replays.
3) Transformation
   - Capabilities, authority, and epistemic state MAY change only via processes.
   - Identity MUST NOT change during transformation.
4) Termination
   - Agents MUST be terminated only via processes.
   - Termination MUST leave history.
   - Agent history MUST remain queryable after termination.

## No implicit existence
- Agents MUST NOT appear or disappear without explicit process effects.
- Existence transitions MUST be law-gated and auditable.

## Human/AI assumptions
- Agents MUST NOT depend on human-only lifecycle assumptions.
- Agents MUST NOT rely on "AI magic" or implicit resurrection.

## References
- `../arch/INVARIANTS.md`
- `../arch/REALITY_LAYER.md`
- `../arch/EXISTENCE_LIFECYCLE.md`
- `../arch/EXISTENCE_AND_REALITY.md`
