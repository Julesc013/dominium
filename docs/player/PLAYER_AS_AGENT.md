# PLAYER AS AGENT

Players MUST be represented as normal agents with stable agent_id, capabilities, authority, and epistemic state.
The simulation layer MUST NOT distinguish player agents from AI agents.
Player agents MUST be created and terminated only via processes with provenance.

Player embodiment MUST NOT assume UI, control schemes, or human privilege.
Player embodiment MUST NOT grant implicit authority or omniscience.

References:
- docs/arch/INVARIANTS.md
- docs/arch/REALITY_LAYER.md
