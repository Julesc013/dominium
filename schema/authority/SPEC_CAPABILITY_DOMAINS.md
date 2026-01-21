# SPEC_CAPABILITY_DOMAINS (OMNI0)

Schema ID: CAPABILITY_DOMAINS
Schema Version: 1.0.0
Status: binding.
Scope: capability scoping across domain, time, and subject types.

## Purpose
Define how capabilities and denials are scoped without modes or hard-coded
admin flags. Scopes are deterministic and law-gated.

## Capability Scope Fields (Deterministic)
Each capability MAY declare any of the following scope dimensions:
- domain_ref: domain volume identifier (see `schema/domain/README.md`)
- domain_path_ref: path or corridor identifier (travel graph)
- travel_edge_ref: travel edge identifier
- time_window: [act_start, act_end] inclusive ACT ticks
- subject_type: entity/domain/tool/session category
- subject_ref: specific subject identifier
- actor_type: player, tool, service, server, or system actor class
- jurisdiction_ref: jurisdiction binding (law scopes)
- parameters: deterministic limits (ranges, quotas, budgets)

Empty fields mean unbounded for that dimension.

## Scope Resolution Rules
- Capability scope is matched by intersection across dimensions.
- Multiple grants produce a union of allowed scopes.
- Multiple denials produce a union of forbidden scopes.
- Denials take precedence over grants unless an explicit override effect is
  authorized and recorded.

Scope precedence is resolved via the law scope chain in
`schema/law/SPEC_LAW_SCOPES.md`.

## Domain and Travel Integration
- Domain scoping uses domain volumes and jurisdiction resolution.
- Travel scoping uses travel edges and declared paths only.
- Spatial capability checks MUST use domain APIs, not hard-coded bounds.

## Time Integration
- Time windows are ACT-based; wall-clock time is forbidden.
- Observer clocks may narrow perception but must not change authority scope.

## Parameterization
Capabilities may include deterministic parameters, for example:
- max_radius (spatial reach)
- max_entities (spawn limits)
- quota_per_act (rate limits)
- max_history_depth (archival visibility)

## Examples
- Freecam allowed only inside admin chamber volume and only for 100 ACT ticks.
- Spectator-only zones with denials for mutation in specific domains.

## Cross-References
- Authority layers: `schema/authority/SPEC_AUTHORITY_LAYERS.md`
- Law scopes: `schema/law/SPEC_LAW_SCOPES.md`
- Travel graph: `schema/travel/README.md`
- Domain volumes: `schema/domain/README.md`
