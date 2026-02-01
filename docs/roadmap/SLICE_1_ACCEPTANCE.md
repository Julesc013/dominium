Status: DERIVED
Last Reviewed: 2026-02-01
Supersedes: none
Superseded By: none

# SLICE-1 Acceptance

SLICE-1 is complete when all items below are satisfied:

Local fields:
- Field system extended with support_capacity, surface_gradient, local_moisture,
  accessibility_cost (generic, unitful, LOD-aware, unknown-by-default).

Survey and processes:
- survey_local_area refines subjective knowledge with confidence/uncertainty.
- collect_local_material, assemble_simple_structure, connect_energy_source,
  inspect_structure, repair_structure are implemented and deterministic.
- Each process declares required fields, capabilities, authority, and failures.

Failure and history:
- Failures occur for insufficient support, steep gradients, insufficient resources,
  energy overload, inspection failure, and epistemic gaps.
- Failures emit events, alter state, and persist across save/load.

Movement and interaction:
- Movement respects policy layers and accessibility_cost.
- No teleportation without lawful authority.

Observability:
- CLI/TUI/GUI expose local topology context, known vs unknown fields,
  agent intent and plan, event log, and refusal/failure reasons.

Save/load/replay:
- Saves embed WorldDefinition and preserve unknown fields.
- Replays reproduce failures deterministically.
- Missing fields/capabilities cause explicit refusal.

Tests:
- Headless SLICE-1 flow works with zero packs.
- Survey refines subjective knowledge only.
- Acting without survey increases failure probability.
- Failures are deterministic and explainable via events.
- Replay reproduces failures exactly.
- Lint/static test ensures no hardcoded physical assumptions.