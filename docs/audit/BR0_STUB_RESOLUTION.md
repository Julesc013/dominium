Status: DERIVED
Last Reviewed: 2026-02-07
Supersedes: none
Superseded By: none

# BR-0 Forbidden Stub Resolution

This note documents the resolution of forbidden authoritative runtime stubs.

## Resolved stubs

- `game/rules/city/city_services_stub.cpp`
  - Behavior: Explicit refusal (`CIV1_REFUSAL_NOT_IMPLEMENTED`) via
    `city_services_available_ex`. No state mutation.
- `game/rules/logistics/routing_stub.cpp`
  - Behavior: Explicit refusal (`CIV1_REFUSAL_NOT_IMPLEMENTED`) via
    `logistics_route_estimate_ex`. Outputs zeroed; no state mutation.
- `game/rules/life/life_events_stub.cpp`
  - Behavior: Explicit refusal (`LIFE_REFUSAL_NOT_IMPLEMENTED`) via
    `life_cmd_continuation_apply_ex`. No state mutation.

## Rationale

These areas are not implemented in authoritative runtime and must refuse
deterministically rather than perform placeholder logic. The refusal paths are
explicit, stable, and covered by TestX.
