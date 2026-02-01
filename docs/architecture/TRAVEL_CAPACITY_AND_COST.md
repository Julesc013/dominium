Status: CANONICAL
Last Reviewed: 2026-02-01
Supersedes: none
Superseded By: none

# Travel Capacity and Cost (TRAVEL1)

Status: draft.
Scope: movement scarcity, budgets, and deterministic denial.

## Capacity
Every travel edge declares capacity:
- FINITE, INFINITE, or BURST
- explicit capacity units
- deterministic refill rules

Capacity is consumed on travel begin and returned on arrival or cancellation.

## Cost
Travel cost is explicit and deterministic:
- time, energy, fuel, bandwidth, economic, risk
- prepaid, escrowed, or settled on arrival
- no resource fabrication

## Latency
Latency is ACT-based and explicit:
- constant or deterministic function
- zero-time edges allowed but scheduled

## Queueing
When capacity is unavailable:
- request is queued or deferred
- ordering is deterministic
- no implicit priority

## Denial Semantics
Travel outcomes include:
- ACCEPT, QUEUE, DEFER, REFUSE
- refusal reasons are explicit and auditable

## References
- `schema/travel/SPEC_TRAVEL_CAPACITY.md`
- `schema/travel/SPEC_TRAVEL_COST.md`
- `schema/travel/SPEC_TRAVEL_LATENCY.md`
- `schema/travel/SPEC_TRAVEL_QUEUEING.md`