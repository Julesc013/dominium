# THERM5 Retro-Consistency Audit

Date: 2026-03-04  
Scope: THERM-5 stress/proof/replay hardening for thermal envelope.

## Findings

1. Unbudgeted thermal evaluation loops
- `src/thermal/network/thermal_network_engine.py` already enforces deterministic caps (`max_processed_edges`, `max_cost_units`) and T1->T0 downgrade.
- No standalone thermal stress harness existed to enforce envelope behavior across many graphs/ticks.

2. Fire/runaway boundedness
- THERM-4 spread is bounded by `max_fire_spread_per_tick` and `fire_iteration_limit`.
- No cross-network envelope verifier existed to assert cap-hit behavior remains logged under scale.

3. Heat-loss input logging coverage
- Heat inputs are consumed via deterministic `heat_input_rows` (`heat_loss`/`heat_input` keys).
- Proof surface lacked an explicit dedicated heat-input hash chain for ranked-style audit.

4. Replay envelope gap
- No THERM-specific replay-window verification tool existed for hash-stable temperature/event/degradation sequences.

## Fix Plan

1. Add deterministic THERM stress scenario generator and stress harness tools.
2. Encode deterministic degradation order in the harness:
- tick-bucket T1 frequency reduction
- deterministic T1->T0 network downgrade
- deferred non-critical model work via constrained model budget
- bounded fire spread cap with explicit cap-hit logs
3. Extend control proof bundle surface with thermal heat-input hash chain.
4. Add THERM replay-window verification tool and regression lock baseline (`THERM-REGRESSION-UPDATE`).
5. Add RepoX/AuditX/TestX envelope checks for budgeting, degradation logging, and heat-input logging.
