# SPEC_TOOL_AUTHORITY (OMNI1)

Schema ID: TOOL_AUTHORITY
Schema Version: 1.0.0
Status: binding.
Scope: authority integration for tools and dev features.

## Purpose
Define how ToolIntents integrate with authority layers, law gating, and audit
so tools are governed like any other action.

## Tool Authority Rules
- ToolIntents are CommandIntents and must use the command pipeline.
- ToolIntents are capability-gated and law-gated at every enforcement point.
- ToolIntents resolve to explicit effects; no direct mutation is allowed.
- Tool authority is data-defined and revocable via capability sets.

## Layer Integration
Tool capabilities map to authority layers:
- TOOL.SPATIAL -> SPATIAL
- TOOL.SIMULATION -> SIMULATION
- TOOL.EPISTEMIC -> EPISTEMIC
- TOOL.TEMPORAL -> TEMPORAL
- TOOL.EXECUTION -> EXECUTION
- TOOL.GOVERNANCE -> GOVERNANCE

## Audit Requirements
Every ToolIntent MUST emit:
- actor and tool identity,
- domain and jurisdiction context,
- ACT timestamp and scope window,
- capability evidence and denials,
- law targets evaluated,
- effect tokens committed or refusal codes.

## Anti-Cheat as Law
Anti-cheat is expressed as law that denies tool capabilities for most actors.
No tool-specific bypasses are allowed outside law evaluation.

## Cross-References
- Tool intents: `schema/tools/SPEC_TOOL_INTENTS.md`
- Tool capabilities: `schema/tools/SPEC_TOOL_CAPABILITIES.md`
- Law kernel: `schema/law/SPEC_LAW_KERNEL.md`
