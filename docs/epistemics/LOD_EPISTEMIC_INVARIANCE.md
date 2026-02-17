Status: DERIVED
Version: 1.0.0
Last Reviewed: 2026-02-16
Compatibility: Bound to Observation Kernel, LawProfile, EpistemicPolicy, and deterministic collapse/expand transitions.

# LOD Epistemic Invariance

## Epistemic Invariance Principle

Let:
- `T` = TruthModel
- `P` = PerceivedModel projection under policy `E`
- `R` = deterministic refinement operator (macro -> micro)

For observers without additional entitlements:

`P(T) == P(R(T))`

Meaning:
- refinement may add internal simulation detail,
- but refinement must not add epistemic channels or precision beyond law/policy/lens limits.

## Information Categories Covered

1. Positional precision
2. Structural internal state
3. Hidden inventories/components
4. Internal stresses/failure internals
5. Unobserved population distributions

## Allowed Increases

New knowledge is allowed only when caused by lawful observation changes, for example:
- observer moved physically into sensory range,
- diegetic instrument measured new data in-range,
- law/policy changed to allow additional channels.

Solver tier change alone is never a lawful cause of new knowledge.

## Forbidden Increases

1. High-resolution terrain outside lawful observation range.
2. Exact internal structure details without inspection authority.
3. Internal stress/failure state without an allowed channel.
4. Hidden inventory disclosure caused only by refine/expand.

## Required Enforcement Points

1. Observation Kernel redaction/quantization pipeline.
2. Solver tier transition path (`collapse <-> expand`).
3. Macro capsule expand/collapse process enforcement.
4. PerceptionInterestPolicy selection and ordering.
5. Multiplayer perceived-delta generation paths (A/B/C policies).

## Refusal Semantics

When strict LOD invariance enforcement is enabled and a leak is detected:
- refuse deterministically with `refusal.ep.lod_information_gain`

In non-strict contexts:
- record deterministic invariant violation metadata for developer audit.

In multiplayer handshake/governance:
- server profile may advertise strict enforcement via
  `handshake.extensions.enforce_lod_invariance_strict=true`
- ranked governance can require strict refusal behavior.

## Memory Requirement On Collapse

Collapsing fidelity must not erase lawful memory:
- `Perceived.memory` remains policy-governed and tick-deterministic,
- collapse may reduce current perception precision,
- collapse must not delete previously lawful memory entries.
