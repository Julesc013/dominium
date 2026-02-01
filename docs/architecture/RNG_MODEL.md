Status: CANONICAL
Last Reviewed: 2026-02-01
Supersedes: none
Superseded By: none

# RNG Model (DETER-0)

Status: binding.
Scope: deterministic RNG streams for all authoritative code paths.

## Core rule: no anonymous RNG
All randomness MUST originate from a named RNG stream. There is no global RNG
and no time-based seeding in authoritative code.

## Named stream format
Stream IDs are ASCII and follow this exact pattern:

`noise.stream.<domain>.<subsystem>.<purpose>`

Rules:
- The prefix `noise.stream.` is mandatory.
- At least three dot-separated segments must follow the prefix.
- IDs are stable and must not be repurposed.

Examples:
- `noise.stream.ai.planning.choice`
- `noise.stream.infrastructure.failure`
- `noise.stream.ecology.mutation`
- `noise.stream.market.shock`

## Derivation rule (canonical)
The deterministic seed is derived from:

- world seed
- domain_id
- process_id
- tick_index
- stream name

Canonical combination:

`seed = fold(world_seed) XOR fold(domain_id) XOR fold(process_id) XOR fold(tick_index) XOR hash(stream_name)`

Where:
- `fold(x)` is a deterministic 64→32 fold.
- `hash(stream_name)` is a deterministic 32-bit hash (FNV-1a).

If a component is not applicable for a given subsystem, it MUST be encoded
into the provided base seed so that the final derived seed still matches the
canonical rule.

## Required APIs
Authoritative code MUST use the named-stream helpers:
- `d_rng_seed_from_context`
- `d_rng_state_from_context`
- `d_rng_state_from_seed` (only for pre-mixed legacy seeds)
- `d_rng_stream_name_valid` + `D_DET_GUARD_RNG_STREAM_NAME`

## RNG cursor continuity (collapse/expand)
RNG stream state MUST be recorded in macro capsules and restored on expand.
This prevents reseeding and preserves micro↔macro equivalence.

Canonical extension key shape:
`rng.state.<stream_name>`

## Forbidden
- `rand()`, `srand()`, or any OS entropy source
- time-based seeds
- implicit global RNG state

## See also
- `docs/architecture/DETERMINISTIC_ORDERING_POLICY.md`
- `docs/architecture/DETERMINISTIC_REDUCTION_RULES.md`
- `docs/architecture/REDUCTION_MODEL.md`