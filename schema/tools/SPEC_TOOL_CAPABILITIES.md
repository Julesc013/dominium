# SPEC_TOOL_CAPABILITIES (OMNI1)

Schema ID: TOOL_CAPABILITIES
Schema Version: 1.0.0
Status: binding.
Scope: tool capability domains, grants, and explicit denials.

## Purpose
Define tool capabilities as first-class authority grants so all tools and
cheats are capability-gated and revocable.

## Tool Capability Domains
Tool capabilities are grouped by domain for clarity. Domains do not imply
authority layers; each capability declares its layer coverage.

- TOOL.SPATIAL (freecam, teleport)
- TOOL.SIMULATION (spawn, edit, mutate)
- TOOL.EPISTEMIC (inspect hidden state)
- TOOL.TEMPORAL (fast-forward view, time view)
- TOOL.EXECUTION (profiling, backend override)
- TOOL.GOVERNANCE (edit laws/jurisdictions)

## Canonical Tool Capabilities (Initial)
TOOL.SPATIAL
- CAN_TOOL_FREECAM
- CAN_TOOL_TELEPORT

TOOL.SIMULATION
- CAN_TOOL_SPAWN_ENTITY
- CAN_TOOL_EDIT_TERRAIN
- CAN_TOOL_MUTATE_STATE

TOOL.EPISTEMIC
- CAN_TOOL_INSPECT_STATE
- CAN_TOOL_INSPECT_HIDDEN

TOOL.TEMPORAL
- CAN_TOOL_TIME_VIEW
- CAN_TOOL_TIME_VIEW_FAST_FORWARD

TOOL.EXECUTION
- CAN_TOOL_PROFILER_VIEW
- CAN_TOOL_BACKEND_OVERRIDE

TOOL.GOVERNANCE
- CAN_TOOL_MODIFY_LAW
- CAN_TOOL_EDIT_JURISDICTION

## Negative Tool Capabilities (Explicit Denials)
Negative capabilities override grants unless explicitly superseded.

- DENY_TOOL_ALL
- DENY_TOOL_SPAWN
- DENY_TOOL_TELEPORT
- DENY_TOOL_INSPECT
- DENY_TOOL_MODIFY_LAW

## Requirement Rules
- Every ToolIntent MUST declare required tool capabilities.
- Denials MUST be explicit; absence is not a denial.
- Overrides MUST be explicit effects and auditable.

## Cross-References
- Tool intents: `schema/tools/SPEC_TOOL_INTENTS.md`
- Tool scoping: `schema/tools/SPEC_TOOL_SCOPING.md`
- Authority layers: `schema/authority/SPEC_AUTHORITY_LAYERS.md`
