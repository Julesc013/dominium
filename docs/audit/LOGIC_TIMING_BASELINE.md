Status: BASELINE
Last Reviewed: 2026-03-08
Scope: LOGIC-5 timing, oscillation, watchdog, and deterministic micro-ROI preparation.
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: canon-aligned documentation set for convergence and release preparation

# LOGIC Timing Baseline

## Summary

LOGIC-5 completes the canonical timing layer for L1 logic evaluation without introducing a global clock subsystem.

The baseline is:
- TEMP-routed
- deterministic
- compute-budgeted
- explainable
- replay-verifiable
- ready to hand off to future LOGIC-6 compile/collapse work

## Delay Semantics

- `delay.none`
  - minimum latency; output becomes visible on the next canonical tick
- `delay.fixed_ticks`
  - output becomes visible at `t + k`
- `delay.temporal_domain`
  - TEMP resolves domain mapping and offset before scheduling delivery
- `delay.sig_delivery`
  - carrier `sig` delivery remains message-oriented and uses the SIG seam

LOGIC timing does not use wall-clock time and does not introduce a free-running clock.

## Oscillation Classification

- Oscillation is detected from repeated logical-state hashes within a bounded policy window.
- Classification is deterministic:
  - stable oscillator
    - repeated state pattern with positive period and stable intervening sequence
  - unstable oscillation
    - repeated churn that violates the declared policy window or timing contract
- Policy handling remains explicit:
  - `refuse`
  - `force_roi`
  - `allow_with_record`

Explain surfaces:
- `explain.logic_oscillation`
- `explain.logic_timing_violation`

## Watchdog And Synchronizer Patterns

- Watchdog and synchronizer support remain data-defined through LOGIC element/pattern registries.
- `logic.watchdog_basic`
  - monitors signal activity within a declared timeout window
  - emits canonical timeout events and derived explain artifacts
- Synchronizer staging remains deterministic and TEMP-driven; no special engine-side clocking was introduced.

Explain surface:
- `explain.watchdog_timeout`

## Timing Enforcement And L2 Hook

- Declared timing constraints measure propagation depth against delay policy outcomes.
- Violations emit canonical timing-violation events and derived explain artifacts.
- If the active logic policy allows `roi_micro_optional`, L1 marks the network as requiring future L2 timing rather than silently degrading.
- L1 timing gates remain deterministic and network-scoped.

## Proof And Replay

Proof/replay surfaces now include:
- `logic_oscillation_record_hash_chain`
- `logic_timing_violation_hash_chain`
- `logic_watchdog_timeout_hash_chain`

Supporting tools:
- `tools/logic/tool_replay_timing_window.py`
- `tools/logic/tool_run_logic_timing_stress.py`

## Stress Harness

Baseline stress lane:
- tool: `python tools/logic/tool_run_logic_timing_stress.py --repo-root . --oscillator-count 12 --tick-count 8 --out-json docs/audit/LOGIC5_TIMING_STRESS.json`
- target: oscillator-heavy network with watchdog coverage under `logic.lab_experimental`
- result:
  - `oscillation_record_count = 2`
  - `timing_violation_count = 0`
  - `watchdog_timeout_count = 12`
  - `logic_oscillation_record_hash_chain = 93ddea66669718d2656093482eaea9a1de25b5133befee67f94610935af59953`
  - `logic_timing_violation_hash_chain = 4f53cda18c2baa0c0354bb5f9a3ecbe5ed12ab4d8e11ba873c2f11161202b945`
  - `logic_watchdog_timeout_hash_chain = 11dcd57c3417d84618abf6a94e2240567f567209fe39e80a5e9d58d92198912c`
  - `deterministic_fingerprint = 1e6a03cb9a281fb81463f715c0b0e1ec4529d5deddc4d91c56d5d43d27a7ec3e`

## Validation Seal

- Topology map refreshed
  - fingerprint: `84e90dac519fd6bcc43b689a226166552ad061f4c952bc4a8a04f27f17c892cb`
  - size: `2277537` bytes
- `AuditX STRICT`
  - pass with `findings = 2222`, `promoted_blockers = 0`
- `TestX STRICT` targeted LOGIC-5/topology subset
  - pass with `selected_tests = 12`
- strict build
  - `canonical_content_hash = 9cdabc6762b207303ef749adddf995b3fe64fe1d0605241cf417330f1966e2b5`

## Readiness

Ready for LOGIC-6:
- compile/collapse proofs can consume timing hash chains without changing L1 semantics
- stable oscillators and timing-gated networks now have explicit proof surfaces
- ROI escalation seam exists without introducing mandatory micro simulation
