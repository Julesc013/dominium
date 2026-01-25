# Agent Model (AGENT0)

Status: binding.
Scope: defines agents as simulation participants and sets mandatory contracts.

## Definition
An AGENT is:
> A persistent simulation entity capable of holding intent, executing processes under authority, and perceiving the world through an epistemically bounded projection.

Agents MUST NOT be assumed human, intelligent, biological, singular, mobile, or conscious.
Agents MUST NOT rely on "AI magic" or implicit intelligence.

## Non-negotiable properties
1) Stable identity
   - An agent MUST have a globally unique `agent_id`.
   - An `agent_id` MUST persist across save/load and replays.
   - An `agent_id` MUST NOT be reused.
2) Authority scope
   - An agent MUST hold explicit authority token(s).
   - An agent MUST NOT mutate state without authority.
3) Capability set
   - Capabilities MUST be declared, not inferred.
   - Capabilities MUST be composable and may change only via processes.
4) Epistemic state
   - Agents MUST hold a subjective view of reality.
   - Agents MUST preserve uncertainty and ignorance.
5) Persistence semantics
   - Agents MUST be created only via processes.
   - Agents MUST be terminated only via processes.

## What an agent can be (non-exhaustive)
- Individuals (human, animal, alien, synthetic)
- Collectives (tribes, states, corporations)
- Institutions (courts, guilds, religions)
- Autonomous systems (factories, drones, AIs)
- Abstract coordinators (planners, schedulers)
- Mythic or fictional constructs (if content defines them)

The engine MUST NOT special-case any of these categories.

## What an agent is not
- Agents MUST NOT be behavior trees.
- Agents MUST NOT be scripts or quest givers.
- Agents MUST NOT be UI avatars or hardcoded AI archetypes.
- Agents MUST NOT be physics objects (though they may own or inhabit one).

## Agent <-> process relationship
- Agents MUST NOT mutate authoritative state directly.
- Agents MUST select or initiate processes; all effects occur through process execution.
- Agents MUST consume time and resources; refusal and failure are valid outcomes.

## Agent <-> knowledge relationship
- Agents MUST perceive the world via subjective snapshots and epistemic filters.
- Agents MUST NOT see objective truth by default.
- Agents MUST be allowed to hold false or outdated beliefs.

## Agent <-> authority relationship
- Agents MUST NOT possess implicit god mode.
- Authority escalation MUST be explicit and process-mediated.
- Agents MAY hold multiple authority tokens and MAY lose authority via processes.

## Memory (declarative only)
- Agents MUST support memory acquisition, decay, loss, and distortion.
- Memory MUST be epistemic data and lossy by default.
- Memory MUST be institutionally mediated (archives, records, testimony).
- Agents MUST NOT have infinite or perfect memory.

## Multiple agent types, one contract
- The system MUST NOT create separate agent systems for NPCs, AIs, players, or institutions.
- Differences MUST be expressed via capabilities, authority, perception, and interfaces only.

## Forbidden assumptions
- Agents MUST NOT be defined by human-centric defaults or player-only assumptions.
- Agents MUST NOT rely on "AI magic" or hidden planners.

## References
- `../arch/INVARIANTS.md`
- `../arch/REALITY_LAYER.md`
- `../arch/AUTHORITY_MODEL.md`
- `../arch/EXISTENCE_AND_REALITY.md`
