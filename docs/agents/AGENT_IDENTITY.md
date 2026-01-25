# Agent Identity (AGENT0)

Status: binding.
Scope: identity continuity, `agent_id` rules, and persistence across time.

## Identity invariants
- An `agent_id` MUST be globally unique and opaque.
- An `agent_id` MUST persist across save/load and replays.
- An `agent_id` MUST NOT be reused, even after termination or archival.
- Identity MUST NOT depend on embodiment, location, controller, or UI bindings.
- Identity MUST survive refinement, collapse, and capability/authority changes.

## Provenance and lineage
- Creation MUST record provenance from the creating process.
- Termination MUST record provenance from the terminating process.
- Forking or archival changes MUST mint a new `agent_id` with lineage references; it MUST NOT overwrite identity.

## Human/AI assumptions
- Agents MUST NOT be defined by human-centric assumptions or player-only traits.
- Agents MUST NOT rely on "AI magic" to establish identity.

## References
- `../arch/INVARIANTS.md`
- `../arch/REALITY_LAYER.md`
- `../arch/IDENTITY_ACROSS_TIME.md`
- `../arch/EXISTENCE_AND_REALITY.md`
