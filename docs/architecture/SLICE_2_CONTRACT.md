# SLICE-2 Contract

Purpose: prove coordination via delegation, shared infrastructure, and
institutional authority without hardcoded agent roles or world assumptions.

Scope (binding for SLICE-2):
- engine/, game/, data/, client/, tools/, docs/arch/, docs/examples/, tests/
- Documentation and tests may be added/updated.

Non-goals (binding for SLICE-2):
- No trade between settlements, diplomacy, or civilization-scale politics.
- No role classes, XP/levels, or manager AI shortcuts.
- No hardcoded infrastructure types or world-specific assumptions.

Required behaviors:
1) Multiple agents:
   - Multiple agents act concurrently with independent epistemic states.
   - Player possession is an authority/policy overlay, not a special agent type.
2) Delegation:
   - Goals can be delegated and refused deterministically.
   - Delegation consumes planning budget and never bypasses law/physics.
3) Shared infrastructure:
   - Network system supports power/material/logistics flows with capacity,
     loss, and explicit failure modes.
   - Storage/buffering is modeled as network nodes.
4) Systemic failure:
   - Overloads, insufficient storage, and delayed maintenance cause failure.
   - Cascades are deterministic and local-first.
5) Institutional constraint:
   - A minimal institution can grant/revoke authority and impose constraints.
   - All actions are logged and replayable.
6) Observability:
   - CLI/TUI/GUI expose agents, delegations, networks, storage, bottlenecks,
     and event logs with refusal/failure reasons.
7) Save/load/replay:
   - Delegation, authority, constraints, and network state persist.
   - Replays reproduce systemic failure deterministically.

Replaceability rules:
- All behavior is routed through agents, processes, fields, networks,
  law/policy/capability, and WorldDefinition.
- All SLICE-2 logic must be safe to replace or extend later.

SLICE-2 completion is defined by the acceptance checklist in
`docs/roadmap/SLICE_2_ACCEPTANCE.md`.
