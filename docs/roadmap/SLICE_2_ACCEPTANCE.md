# SLICE-2 Acceptance

SLICE-2 is complete when all items below are satisfied:

Multiple agents:
- Multiple agents act concurrently with independent epistemic states.
- Player possession is an authority/policy overlay (no special agent type).

Delegation:
- Delegated goals are accepted or refused deterministically.
- Delegation does not bypass law, authority, or physics.

Shared infrastructure:
- Networks support capacity, loss, and explicit failure modes.
- Storage/buffering is modeled as network nodes.

Systemic failure:
- Overload, insufficient storage, and delayed maintenance can fail networks.
- Cascading failures are deterministic and local-first.

Institutional constraint:
- A minimal institution grants/revokes authority and imposes constraints.
- All actions are logged and replayable.

Observability:
- CLI/TUI/GUI expose agents, delegations, network summaries, storage levels,
  bottlenecks, and event logs with refusal/failure reasons.

Save/load/replay:
- Delegation, authority, constraints, and network state persist.
- Replay reproduces systemic failure exactly.

Tests:
- Multiple agents act concurrently.
- Delegation works without micromanagement.
- Infrastructure bottlenecks cause failure.
- Authority enforcement affects outcomes.
- Cascading failure is deterministic.
- Replay reproduces systemic collapse.
- Lint/static test ensures no hardcoded agent roles exist.
