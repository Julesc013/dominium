Status: DERIVED
Last Reviewed: unknown
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: canon-aligned documentation set for convergence and release preparation

# LOGIC-8 Fault / Noise / Security Baseline

Status: final baseline for LOGIC-8

## Constitutional Summary

LOGIC-8 extends the existing typed-signal substrate with deterministic fault overlays, declared noise policies, EMI field stubs, and protocol-security hooks without changing LOGIC semantics, bypassing process-only mutation, or introducing wall-clock dependence.

Authoritative mutation paths:

- `process.logic_fault_set`
- `process.logic_fault_clear`

Behavioral placement:

- faults and noise are applied during LOGIC SENSE
- COMPUTE remains pure
- security gating occurs before a protocol-linked sample becomes visible to element evaluation

## Fault Semantics

Supported fault kinds:

- `fault.open`
- `fault.short`
- `fault.stuck_at_0`
- `fault.stuck_at_1`
- `fault.threshold_drift`
- `fault.bounce`

Baseline behavior:

- open faults block transmission on the affected edge during SENSE
- short faults force a declared value or refuse under policy
- stuck-at faults override the sampled port value deterministically
- threshold drift shifts comparison inputs or thresholds deterministically
- bounce remains ROI-only and never activates in default L1 without explicit policy

## Noise Policies

Registered policies:

- `noise.none`
- `noise.quantize_default`
- `noise.named_rng_optional`

Baseline behavior:

- the default is deterministic quantization at the sampling boundary
- named-RNG noise requires explicit policy gating and a declared `rng_stream_name`
- behavior-affecting noise decisions are captured in `logic_noise_decision_rows`
- replay/proof surfaces include `logic_noise_decision_hash_chain`

## EMI Coupling Stubs

LOGIC-8 does not add analog EMI simulation. Instead it accepts deterministic field modifiers through:

- `field.magnetic_flux_stub`
- `field.radiation_intensity`

Stub effects:

- magnetic flux can increase quantization magnitude or threshold drift
- radiation intensity can activate predeclared fault thresholds
- all effects remain model/policy driven and replayable

## Security Hooks

- protocol-link security is enforced from LOGIC SENSE using `security_policy_id` on incoming `protocol_link` edges
- `sec.none`, `sec.auth_required_stub`, and `sec.encrypted_required_stub` are the declared baseline policies
- failed verification records deterministic `logic_security_fail_rows` and emits `explain.logic_spoof_detected`
- replay/proof surfaces include `logic_security_fail_hash_chain`

## Explainability And Instrumentation

Registered explain surfaces:

- `explain.logic_fault_open`
- `explain.logic_fault_short`
- `explain.logic_stuck_at`
- `explain.logic_noise_effect`
- `explain.logic_spoof_detected`

Registered instrumentation surfaces:

- `measure.logic.fault_state`
- `forensics.logic.fault_open`
- `forensics.logic.fault_short`
- `forensics.logic.noise_effect`
- `forensics.logic.spoof_detected`

Fault-state reads remain instrumentation-gated; no truth-to-render bypass was added.

## Safety Integration

- fault application can emit deterministic `safety_event_rows` during SENSE when a fault policy declares isolation or shutdown behavior
- session-runtime integration merges those rows into the authoritative safety event stream instead of bypassing SYS or watchdog governance

## Proof, Replay, And Stress

Proof bundle additions:

- `logic_fault_state_hash_chain`
- `logic_noise_decision_hash_chain`
- `logic_security_fail_hash_chain`

Replay/stress tools:

- `tools/logic/tool_replay_fault_window.py`
- `tools/logic/tool_run_logic_fault_stress.py`

Stress artifact:

- `docs/audit/LOGIC8_FAULT_STRESS.json`
- deterministic fingerprint: `cb945cf6904a3dd7fbb9e55c5d087db6ef4cff1251614e75a5bc8daaeb440280`

## Validation Snapshot

- TestX STRICT targeted subset passed with `selected_tests=9`
- AuditX STRICT passed with `findings=2234` and `promoted_blockers=0`
- strict build passed with canonical content hash `9cdabc6762b207303ef749adddf995b3fe64fe1d0605241cf417330f1966e2b5`
- topology map refreshed with fingerprint `8b43fd2f5a96d4240abd273239a8b6d245a36a2b0cdc42ed2b28480e48213d6b`
- fault stress passed with `fault_state_count=2`, `noise_decision_count=30`, and `security_fail_count=6`

## Readiness

Ready for LOGIC-9:

- protocol-security hooks exist on protocol-linked buses
- spoof detection is explainable and replay-safe
- fault/noise behavior is policy-declared rather than inline randomness

Ready for LOGIC-10:

- fault-heavy controller windows can be replayed deterministically
- proof chains cover injected faults, behavior-affecting noise, and blocked secure links
- debug surfaces can observe authorized fault state without widening epistemic scope
