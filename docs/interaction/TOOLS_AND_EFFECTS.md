Status: DERIVED
Last Reviewed: unknown
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-ARCHIVE
Replacement Target: legacy reference surface retained without current binding authority

# Tools And Effects

Status: Constitutional (ACT-2)
Version: 1.0.0

## Purpose
ToolEffect defines deterministic, data-driven tool capability metadata for ActionSurface interaction. Tools are assemblies or attachable components that influence process inputs. Tools never mutate TruthModel directly.

## Tool Model
- A tool is an assembly with:
  - `tool_tags`
  - `effect_model_id`
  - `tool_type_id`
  - optional bind state (`equipped_by_agent_id`, `tool.bound_subject_id`)
- Tool possession is represented minimally for ACT-2 as:
  - `controller.active_tool_id` (policy/session context supported)
  - `agent.equipped_tool_id` or runtime tool binding row
- Inventory/crafting is explicitly out of scope. Tools may be:
  - scenario spawned
  - lab/admin granted
  - future inventory managed

## ToolEffect Parameters
ToolEffect metadata is explicit and deterministic. Baseline parameters:
- `efficiency_multiplier`
- `precision_level`
- `torque_limit` (optional)
- `rate_limit` (optional)
- `durability_cost` (stub extension-ready)

These values are passed to process intents as parameters. Process code decides semantics.

## Process-Only Mutation
- Tool interactions are affordance/intents + deterministic process execution.
- UI and RenderModel do not mutate authoritative state.
- Tool bind/unbind/readout changes occur only through process runtime.

## Capability Gating
Tool usability requires all gates:
- LawProfile process allowlist
- AuthorityContext entitlements/privilege
- tool type capability:
  - allowed surface types
  - allowed process IDs
  - compatible tool tags

If capability fails, affordance remains disabled with refusal reason (for example `refusal.tool.incompatible`).

## Determinism
- Tool binds are deterministic and canonicalized.
- Single active tool per subject by default.
- Deterministic tie-break for active replacement:
  - deactivate prior active binds for subject
  - activate target bind with stable ordering by `bind_id`
- Tool readouts are derived deterministically from Perceived data + tool state at tick.

## Diegetic Outputs
Tools can emit diegetic instrument channels:
- `ch.diegetic.tool.torque`
- `ch.diegetic.tool.measurement`
- `ch.diegetic.tool.health`

Readouts:
- must not access hidden Truth data from client UX
- should use inspection/perceived channels where allowed
- must quantize/redact as required by epistemic policy

## Multiplayer And Anti-Cheat
- Bind/unbind/use is server-authoritative under B/C policies.
- Lockstep includes tool actions in deterministic tick intent list.
- Anti-cheat:
  - reject tool spoof (tool use without active bind)
  - detect tool spam patterns
  - log forbidden attempts deterministically

## Non-Goals
- No inventory system.
- No crafting.
- No skill trees.
- No nondeterministic success probability in tool semantics.
