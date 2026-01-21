# Tools as Capabilities (OMNI1)

Status: binding.
Scope: tooling, dev features, and debug utilities as law-gated capabilities.

## Purpose
Ensure all tools and dev features are first-class, explicit, and auditable.
No special-case dev hooks or admin bypass paths are allowed.

## Model
- Tools are CommandIntents (ToolIntents).
- ToolIntents are capability-gated and law-gated.
- ToolIntents resolve to explicit effects only.
- Tool powers are scoped by domain, jurisdiction, session, and time window.

## Tool Intent Examples
- console command
- freecam enable/disable
- teleport
- spawn entity
- edit terrain
- inspect hidden state
- profiler view

## Scope Controls
Tools can be enabled or revoked per:
- domain volume,
- jurisdiction,
- session,
- ACT time window,
- subject type.

## Cross-References
- Tool authority: `schema/authority/SPEC_TOOL_AUTHORITY.md`
- Tool intents: `schema/tools/SPEC_TOOL_INTENTS.md`
- Tool capabilities: `schema/tools/SPEC_TOOL_CAPABILITIES.md`
