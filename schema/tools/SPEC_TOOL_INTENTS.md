# SPEC_TOOL_INTENTS (OMNI1)

Schema ID: TOOL_INTENTS
Schema Version: 1.0.0
Status: binding.
Scope: ToolIntent format and command admission requirements.

## Purpose
Define ToolIntent as a CommandIntent subtype so all tools and cheats are
explicit, scoped, law-gated, and auditable.

## ToolIntent Definition
ToolIntent is a CommandIntent with additional fields:
- tool_id: stable tool identifier (console, editor, profiler, debug_ui)
- intent_type: tool action token (TOOL_FREECAM_ENABLE, TOOL_TELEPORT, etc.)
- target_scope: declared scope (domain, jurisdiction, subject, session)
- parameters: deterministic payload (validated, bounded)

ToolIntent MUST declare law_targets and capability requirements.

## Admission Rules
- ToolIntent MUST enter the command pipeline.
- ToolIntent MUST be evaluated by the law kernel before scheduling.
- ToolIntent MUST resolve to explicit effects (no direct mutation).
- ToolIntent MUST emit an audit entry on accept or refuse.

## Determinism Requirements
- parameters MUST be deterministic, validated, and schema-bound.
- wall-clock time and randomness are forbidden.

## Examples (Intent Types)
- TOOL_FREECAM_ENABLE
- TOOL_TELEPORT
- TOOL_SPAWN_ENTITY
- TOOL_EDIT_TERRAIN
- TOOL_INSPECT_STATE
- TOOL_PROFILER_VIEW

## Cross-References
- Tool capabilities: `schema/tools/SPEC_TOOL_CAPABILITIES.md`
- Tool scoping: `schema/tools/SPEC_TOOL_SCOPING.md`
- Authority integration: `schema/authority/SPEC_TOOL_AUTHORITY.md`
