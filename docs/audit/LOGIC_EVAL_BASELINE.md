Status: BASELINE
Last Reviewed: 2026-03-08
Scope: LOGIC-4 deterministic L1 evaluation engine baseline.
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: canon-aligned documentation set for convergence and release preparation

# LOGIC Evaluation Baseline

## Summary

LOGIC-4 completes the canonical L1 controller runtime:

1. `SENSE`
2. `COMPUTE`
3. `COMMIT`
4. `PROPAGATE`

The baseline is:
- deterministic
- process-mediated
- STATEVEC-compliant
- compute-budgeted
- loop-policy-gated
- replay-verifiable

## Phase Rules

- `SENSE`
  - builds an immutable snapshot from validated network inputs and current STATEVEC snapshots
  - orders work by `network_id`, `element_instance_id`, and `port_id`
- `COMPUTE`
  - evaluates behavior models as pure functions over the snapshot and explicit state
  - requests compute through META-COMPUTE per element
  - stops deterministically on throttle/refusal
- `COMMIT`
  - writes only explicit state-vector snapshots through `process.statevec_update`
  - emits canonical logic state-update records
- `PROPAGATE`
  - schedules downstream signal writes through canonical signal processes
  - never exposes same-tick visibility, including `delay.none`

## Throttle Behavior

- Per-element compute is metered through `request_logic_element_compute`.
- Per-network caps are read from declared logic policy extensions.
- Throttle order is stable:
  - policy/priority first
  - lexical element/network identity as tie-break
- Behavioral throttles emit:
  - `logic_throttle_event`
  - `explain.logic_compute_throttle`
  - `logic_eval_record`

## Delay Semantics

- `delay.none`
  - delivery scheduled for `t + 1`
- `delay.fixed_ticks`
  - delivery scheduled for `t + k`
- `delay.temporal_domain`
  - delivery scheduled from TEMP-mapped tick offset
- `delay.sig_delivery`
  - delivery scheduled through the SIG-oriented message seam

Propagation traces are derived, compactable artifacts:
- `trace.logic.propagation_scheduled`
- `trace.logic.propagation_delivered`

## Loop And Validation Gates

- LOGIC-4 refuses L1 execution unless LOGIC-3 validation marked the network `validated`.
- Combinational loops are refused by default with `explain.logic_loop_detected`.
- `force_roi` and `allow_compiled_only` loop resolutions are explicitly refused at L1 until LOGIC-5/6 paths exist.

## Proof And Replay

Replay/proof surfaces now include:
- `logic_throttle_event_hash_chain`
- `logic_state_update_hash_chain`
- `logic_output_signal_hash_chain`

Supporting tools:
- `tools/logic/tool_replay_logic_window.py`
- `tools/logic/tool_run_logic_eval_stress.py`

## Stress Harness

Baseline stress lane:
- tool: `python tools/logic/tool_run_logic_eval_stress.py --repo-root . --element-pairs 36 --tick-count 10 --out-json build/logic/logic4_stress_report.json`
- target: large, validated, uncompiled network with 72 elements
- expected outcome: deterministic completion without loop-policy bypass or direct signal/state mutation

## Readiness

Ready for LOGIC-5:
- timing-pattern and oscillation diagnostics can consume deterministic eval/proof traces

Ready for LOGIC-6:
- compiled/collapsed controllers can prove equivalence against the L1 hash surfaces and state update chain
