# LOGIC Fault, Noise, and Security Model

## Scope

LOGIC-8 adds deterministic fault, noise, EMI-stub, and protocol-security behavior for logic networks. It does not add wall-clock timing, RF simulation, or a full cyber-security stack.

## Fault Model

Faults are explicit rows attached to logic targets and consumed during authoritative evaluation.

Supported fault kinds:

- `fault.open`
- `fault.short`
- `fault.stuck_at_0`
- `fault.stuck_at_1`
- `fault.threshold_drift`
- `fault.bounce`

Fault targets:

- edges
- nodes or ports
- elements

Default semantics:

- open:
  - the affected edge contributes no transmitted signal to SENSE
- short:
  - the affected path forces a declared fault value or refuses the network under policy
- stuck-at:
  - the affected port snapshot is overridden to `0` or `1`
- threshold drift:
  - threshold comparison input or threshold extension is shifted deterministically
- bounce:
  - ROI-only pulse perturbation; never active in default L1 unless policy explicitly allows it

Fault state changes are canonical and process-only:

- `process.logic_fault_set`
- `process.logic_fault_clear`

## Noise Model

Default noise behavior is deterministic and policy-driven.

The default is deterministic quantization at the sampling boundary.

Kinds:

- `none`
- `quantize`
- `named_rng`

Semantics:

- quantize:
  - deterministic rounding/thresholding at sampling boundaries
- named RNG:
  - only allowed when profile/policy explicitly permits it
  - must declare `rng_stream_name`
  - must be replayable and proof-visible when behavior changes

Noise affects:

- signal sampling
- threshold comparisons
- derived bus/protocol interpretation if the sampling surface is policy-bound

Noise does not redefine logic semantics or gate truth by carrier-specific hacks.

## EMI Stub

LOGIC does not simulate RF or analog EM fields directly.

Instead, EMI is represented as deterministic field-driven modifiers:

- `field.magnetic_flux_stub`
- `field.radiation_intensity`

These modifiers can:

- increase noise magnitude
- increase threshold drift
- activate deterministic fault thresholds
- feed named-RNG probability envelopes only when explicitly allowed

All such effects must route through models, field samples, or policy surfaces. No direct inline “EMI if high then glitch” hacks are allowed.

## Security Hook

Protocol links may declare `security_policy_id`.

Supported requirements:

- credential verification
- signature or verification-state checks
- encryption requirement stubs

If a protocol-link payload fails verification:

- propagation is refused
- a deterministic security failure row is recorded
- `explain.logic_spoof_detected` is emitted

Security failure is a protocol/carrier control result, not a hidden render/debug behavior.

## Evaluation Placement

Fault and noise application occurs during SENSE:

1. read stable source signal
2. apply fault overrides
3. apply deterministic noise policy
4. expose the resulting snapshot to COMPUTE

This preserves the LOGIC-0 rule that COMPUTE remains pure with respect to authoritative writes.

## Safety Integration

Logic fault visibility can feed safety patterns such as:

- watchdog isolation
- fail-safe actuator shutdown
- interlock refusal

Safety responses remain profile- and pattern-driven. LOGIC faults do not bypass SAFETY or SYS governance.

## Explainability

LOGIC-8 standard explain kinds:

- `explain.logic_fault_open`
- `explain.logic_fault_short`
- `explain.logic_stuck_at`
- `explain.logic_noise_effect`
- `explain.logic_spoof_detected`

These explains must identify:

- affected network or target
- relevant fault/noise/security policy
- refusal/degradation behavior where applicable

## Non-Goals

- no free-running clock
- no full EMI solver
- no full cyber-security stack
- no nondeterministic randomness without named-RNG policy and proof surface
