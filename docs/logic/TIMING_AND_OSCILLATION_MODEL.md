Status: DERIVED
Last Reviewed: unknown
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: canon-aligned documentation set for convergence and release preparation

## LOGIC Timing And Oscillation Model

LOGIC timing is canonical cybernetic timing. It is expressed through canonical ticks, TEMP mappings, declared delay policies, explicit state, and deterministic evaluation order. It is not a wall-clock subsystem and it is not an electrical-frequency subsystem.

### A. Delay Semantics

- `delay.none`
  - Minimum latency path.
  - A value computed during tick `t` becomes visible no earlier than tick `t + 1`.
  - This preserves the LOGIC-4 no-intra-tick-race rule.
- `delay.fixed_ticks(k)`
  - Value becomes visible at tick `t + max(1, k)`.
  - `k` is declared data, never inferred from wall clock.
- `delay.temporal_domain(domain_id, offset)`
  - Delay resolution must pass through TEMP mapping and declared domain policy.
  - The offset remains explicit and deterministic.
  - LOGIC consumes TEMP as a timing oracle; it does not create a parallel timing model.
- `delay.sig_delivery`
  - Delay is mapped through SIG delivery semantics and receipt timing.
  - LOGIC only observes the declared delivery result; transport trust, encryption, and delivery policy remain in SIG.

### B. Oscillation Definition

Oscillation is a cyclic signal and state evolution with non-zero period.

- Detection basis:
  - repeat of a network timing-state hash inside a bounded policy window
- Period:
  - `current_tick - prior_tick`
- Stable oscillator:
  - repeated period pattern is consistent across consecutive windows
  - allowed unless a stricter policy refuses it
- Unstable oscillation:
  - repeat exists but period/stability cannot be established deterministically inside the bounded window
  - produces `explain.logic_oscillation`

LOGIC does not hardcode oscillator parts. Oscillation is emergent from feedback, delay, and explicit state.

### C. Watchdog Pattern

A watchdog is a pack-defined logic element or assembly pattern that:

- monitors a declared signal or signal slot
- tracks elapsed quiet ticks deterministically
- triggers a declared timeout action when no qualifying change is observed within a threshold

Allowed timeout actions:

- emit a deterministic signal update through LOGIC signal processes
- refuse or escalate through declared policy

Watchdogs do not use wall-clock timers. They advance only through canonical evaluation and TEMP-backed delay policy.

### D. Synchronizer Pattern

A synchronizer is a pack-defined logic element or assembly pattern for deterministic cross-domain stabilization.

- canonical form:
  - two or more sequential stages
- purpose:
  - absorb domain transition latency and expose only stage-stable output
- timing:
  - realized through explicit delay/state transitions, not hidden metastability simulation

Synchronizers are deterministic abstractions, not analog metastability solvers.

### E. Timing Violation

A timing violation occurs when declared timing intent cannot be met under the active policy.

Examples:

- propagation depth exceeds `max_propagation_ticks`
- repeated cycle exceeds `max_cycle_ticks`
- L1 evaluation encounters a network that must move to ROI timing

Required outputs:

- `explain.logic_timing_violation`
- canonical timing event if behavior is degraded, throttled, or refused

Policy actions may include:

- throttle
- force ROI micro
- refuse evaluation
- request expand before future evaluation

### F. Deterministic Micro-ROI

LOGIC reserves L2 for deterministic micro timing only when policy requires it.

- L1 never silently becomes L2.
- If `logic_policy.timing_mode == roi_micro_optional` and timing analysis requires micro detail:
  - L1 records the requirement explicitly
  - future evaluation may route to L2
- If policy does not allow ROI micro:
  - L1 refuses with explain artifacts

### G. Budgeting

- Oscillation detection, timing-constraint checks, and watchdog timeout analysis are budgeted work.
- Timing analysis must request META-COMPUTE units explicitly.
- Timing checks must remain bounded by:
  - fixed history windows
  - stable ordering
  - declared policy limits

### H. Explainability

The timing layer must surface:

- `explain.logic_oscillation`
- `explain.logic_timing_violation`
- `explain.watchdog_timeout`

All timing traces are derived and compactable. Canonical timing events are retained when they affect behavior, refusal, or degradation.

### I. Non-Goals

- No wall-clock time
- No global free-running clock
- No hardcoded oscillator element behavior in engine code
- No hidden jitter
- No nondeterministic timing noise unless a named policy explicitly allows it and logs it
