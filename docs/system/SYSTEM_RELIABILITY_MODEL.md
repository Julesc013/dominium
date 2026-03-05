Status: AUTHORITATIVE
Last Reviewed: 2026-03-06
Version: 1.0.0
Scope: SYS-6 system reliability and predictive failure budgeting for macro capsules.

# System Reliability Model

## A) Failure Modes
Canonical system-level failure mode IDs:
- `failure.mode.overheat`
- `failure.mode.overpressure`
- `failure.mode.electrical_fault`
- `failure.mode.corrosion_breach`
- `failure.mode.control_loss`
- `failure.mode.structural_fracture`
- `failure.mode.pollution_violation` (reserved/future)

Failure mode IDs are data-declared by reliability profiles and evaluated deterministically.

## B) ReliabilityProfile
A `ReliabilityProfile` defines deterministic reliability behavior for a system/capsule:
- failure mode declarations,
- hazard-to-failure trigger rules,
- warning thresholds,
- forced-expand thresholds,
- failure thresholds,
- optional profile-gated stochastic branch,
- safe fallback actions for macro operation when expand is denied.

Profiles are pack/registry driven. No hardcoded per-object failure logic is allowed.

## C) Deterministic Failure Policy
Default behavior is deterministic threshold evaluation:
- health state aggregation is deterministic and bounded,
- trigger evaluation is deterministic and ordered by `(system_id, failure_mode_id)`,
- outcomes are logged and replayable.

Optional stochastic mode is permitted only when profile allows it:
- uses a named RNG stream from profile (`rng_stream_name`),
- deterministic seed source is `(system_id, tick, reliability_profile_id, failure_mode_id)`,
- RNG outcome is proof-logged and replay-stable.

## D) Expand-on-Edge
When reliability indicates near-failure:
1. Emit warning state/event output.
2. Trigger forced expand request through SYS-3/CTRL pathway.
3. If expand approved: transition to higher fidelity.
4. If expand denied: apply declared safety fallback actions and log decision.

If failure threshold is exceeded:
- emit canonical system failure event,
- apply fail-safe safety actions,
- emit explain artifact linkage for forensic pathways.

## Determinism and Budget Discipline
- No wall-clock input.
- Fixed canonical tick integration.
- Deterministic degrade order under budget pressure:
  - lower-frequency health updates for low-priority systems,
  - deterministic bucket scheduling by `(system_id, tick)`,
  - explicit DecisionLog rows for degraded/denied actions.
- Canonical emissions, invariants, and safety constraints remain authoritative.
