Status: DERIVED
Version: 1.0.0
Last Reviewed: 2026-02-15
Compatibility: Bound to Truth/Perceived/Render separation, Observation Kernel contracts, and LawProfile lens gating.

# Epistemics Over Network

## Purpose
Define non-leak network epistemics: transport conveys Perceived artifacts only.

## Core Rule

1. Network transport must not serialize raw TruthModel state for client consumption.
2. Approved transport payloads:
   - perceived deltas
   - snapshot/delta artifact references and hashes
   - hash anchor frames
3. Truth payload exceptions:
   - server-internal deterministic snapshot artifacts by reference/hash only, not unrestricted client projection.

## Filtering Path

1. Truth -> Observation Kernel -> Perceived
2. Perceived filtered by:
   - `Lens`
   - `LawProfile`
   - `AuthorityContext`
3. Network output emits only filtered Perceived channels.

## Perception Interest Management vs Simulation ROI

1. Simulation ROI:
   - determines where micro/macro simulation detail activates.
2. Perception Interest Management:
   - determines what each peer may observe/receive.
3. These are separate policy surfaces and must not be conflated.

## Non-Leak Guarantees

1. No direct truth serialization in network-facing modules.
2. No bypass around Observation Kernel for peer-visible state.
3. Deterministic refusal for authority/lens/epistemic violations.

## Test Expectations

1. Static guardrails detect truth-over-net smells.
2. Strict tests verify observation redaction under restrictive law profiles.
3. Hash anchors remain deterministic regardless of network message timing.

## Cross-References

- `docs/architecture/truth_perceived_render.md`
- `docs/architecture/observation_kernel.md`
- `docs/net/MULTIPLAYER_MODEL_OVERVIEW.md`
- `docs/net/REPLICATION_POLICIES.md`

## TODO

- Add concrete Perceived channel whitelist matrix per replication policy family.
