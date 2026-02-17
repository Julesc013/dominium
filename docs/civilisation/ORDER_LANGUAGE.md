Status: AUTHORITATIVE
Last Reviewed: 2026-02-17
Version: 1.0.0

# Governance Order Language

## Scope
- Orders are canonical CIV intents that schedule deterministic processes.
- Orders target simulation subjects:
  - `agent_id`
  - `cohort_id`
  - `faction_id`
  - `territory_id` (where supported by order type)
- Orders are valid in worlds with:
  - no agents
  - cohorts only
  - micro agents only
  - mixed macro/micro populations

## Contract
- Orders are schema-defined artifacts, not ad hoc command payloads.
- Order execution is process-only mutation.
- Orders do not bypass:
  - `LawProfile`
  - `AuthorityContext`
  - epistemic filtering
  - shard routing rules
- Orders do not grant knowledge by creation alone.

## Lifecycle
- Canonical status sequence:
  - `created`
  - `queued`
  - `executing`
  - terminal: `completed|failed|refused`
- `accepted/refused` are deterministic outcomes of validation at creation/dispatch time.
- Cancellation is explicit (`process.order_cancel`) and policy-gated.

## Deterministic Queueing
- Queue order is deterministic:
  - sort key: `(priority desc, created_tick asc, order_id asc)`
- Conflict resolution is deterministic:
  - same-target conflicts resolve by queue order.
  - later conflicting orders either wait or fail with deterministic refusal.
- Execution budget is deterministic and policy-driven.

## Initial Order Families
- `order.move`
- `order.migrate`
- `order.assimilate`
- `order.patrol` (stub)
- `order.build_plan` (stub, plan artifact only)
- `order.communicate` (ED-2 message integration)

## Refusal Discipline
- Required refusal paths include:
  - unsupported pathing/transport
  - cross-shard unsupported route
  - missing entitlement
  - forbidden by active law/profile
  - invalid target or payload schema
- Refusals are deterministic and include remediation hints.

## Anti-Cheat Surfaces
- Order spam is evaluated by tick-based input integrity.
- Impossible orders are refused and logged.
- Authority escalation attempts through order issuance are refused and logged.

## Non-Goals (CIV-3)
- No crafting/inventory semantics.
- No combat/damage semantics.
- No deep economic solver integration.

