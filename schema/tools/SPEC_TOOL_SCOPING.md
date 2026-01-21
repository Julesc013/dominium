# SPEC_TOOL_SCOPING (OMNI1)

Schema ID: TOOL_SCOPING
Schema Version: 1.0.0
Status: binding.
Scope: scoping model for tool capabilities and ToolIntents.

## Purpose
Define how tool capabilities are scoped by domain, jurisdiction, time, subject,
and session without special-case tooling logic.

## Scope Dimensions
Tool capabilities and ToolIntents MAY declare:
- domain_ref: domain volume identifier
- jurisdiction_ref: law jurisdiction identifier
- time_window: [act_start, act_end] inclusive ACT ticks
- subject_type: entity, domain, tool, session category
- subject_ref: specific subject identifier
- session_ref: session identifier
- organization_ref: organization or operator group
- parameters: deterministic limits and quotas

Empty fields mean unbounded for that dimension.

## Scope Resolution
- Grants combine by union; denials combine by union.
- Denials override grants unless explicitly superseded by lawful override.
- Scope precedence is resolved by the law scope chain.

## Examples
- Freecam allowed only inside admin chamber volume for 100 ACT ticks.
- Spawn allowed only during maintenance window and only for test subjects.
- Inspect hidden state allowed only for own organization in a specific domain.

## Cross-References
- Capability domains: `schema/tools/SPEC_TOOL_CAPABILITIES.md`
- Authority scopes: `schema/authority/SPEC_CAPABILITY_DOMAINS.md`
- Law scopes: `schema/law/SPEC_LAW_SCOPES.md`
