# Sandbox Model (OPS0)

Status: binding.
Scope: meta-law sandbox constraints for ops, launcher, and tools.

## Canonical schema

Sandbox policy is defined by:

- `schema/sandbox.policy.schema`

Sandbox policy is operational meta-law only. It must not affect simulation
semantics, authority, or outcomes.

## Required fields (summary)

- allowed_paths / denied_paths
- network_policy (offline | lan | internet)
- pack_source_whitelist
- cpu_budget / memory_budget / io_budget
- extensions (open map)

## Rules

- Sandbox enforcement is required for ops actions.
- Sandbox violations MUST emit refusal semantics.
- Sandbox does not imply a single install or instance.

## See also

- `docs/architecture/REFUSAL_SEMANTICS.md`
- `docs/architecture/OPS_TRANSACTION_MODEL.md`
