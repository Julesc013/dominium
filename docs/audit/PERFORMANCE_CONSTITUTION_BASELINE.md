# Performance Constitution Baseline (RS-5)

Date: 2026-02-26  
Status: Baseline complete (deterministic performance envelope, arbitration, and inspection caching)

## 1) Budget Envelope Parameters

`UniversePhysicsProfile` now carries:
- `budget_envelope_id`
- `arbitration_policy_id`
- `inspection_cache_policy_id`

Registered envelope baselines:

1. `budget.null`
   - `max_micro_entities_per_shard=0`
   - `max_micro_regions_per_shard=0`
   - `max_solver_cost_units_per_tick=0`
   - `max_inspection_cost_units_per_tick=0`
2. `budget.default_realistic`
   - `max_micro_entities_per_shard=100000`
   - `max_micro_regions_per_shard=128`
   - `max_solver_cost_units_per_tick=250000`
   - `max_inspection_cost_units_per_tick=25000`
3. `budget.rank_strict`
   - `max_micro_entities_per_shard=50000`
   - `max_micro_regions_per_shard=64`
   - `max_solver_cost_units_per_tick=125000`
   - `max_inspection_cost_units_per_tick=10000`

Cost accounting is deterministic and wall-clock independent:
- `src/performance/cost_engine.py` computes per-tick cost snapshots from declared tier/entity cost classes.
- If envelope limits are exceeded, RS-4 transition planning is forced through deterministic degrade/cap behavior.

## 2) Arbitration Modes and Fairness

Arbitration policy registry baselines:

1. `arb.equal_share` (`mode=equal_share`)
2. `arb.server_weighted` (`mode=weighted`)
3. `arb.distance_priority` (`mode=server_authoritative_priority`)

Deterministic tie-break and ordering guarantees:
- Stable candidate ordering by quantized distance, priority, peer id, and region id.
- Equal-share and weighted arbitration allocate capacity deterministically across peers.
- Selection trace artifacts are emitted for deterministic auditability.

Ranked fairness constraint:
- Ranked handshakes refuse non-`arb.equal_share` arbitration policy selection.

## 3) Deterministic Degradation Strategy

When demand exceeds capacity, transition planning degrades deterministically:

1. degrade selected regions to lower tiers (`fine -> medium -> coarse`)
2. collapse capped regions when tier degradation is insufficient
3. reduce inspection resolution to inspection budget cap
4. refuse remaining expansions if still above envelope

This path is deterministic, policy-driven, and does not allow lag-spike substitution for degradation.

## 4) Inspection Snapshot Caching

Inspection is implemented as a derived artifact path:
- `src/performance/inspection_cache.py`
- `process.inspect_generate_snapshot` in runtime process execution

Guarantees:
- Snapshot key uses deterministic content hash over target + truth/policy/profile inputs.
- Cache is keyed by `H(target_id, truth_hash_anchor, policy_id, physics_profile_id, pack_lock_hash)`.
- Invalidated on truth/policy context change.
- Eviction is deterministic (`evict.deterministic_lru` order).
- Inspection path is non-authoritative truth mutation (`skip_state_log=True` for derived-only process handling).
- Budget-gated via deterministic inspection cost reservation with refusal `refusal.inspect.budget_exceeded`.

## 5) Multiplayer Integration Notes

Across lockstep / authoritative / SRZ hybrid:
- Physics profile performance ids are resolved server-side and propagated in runtime policy context.
- Handshake compatibility now includes:
  - `budget_envelope_id`
  - `arbitration_policy_id`
- Mismatch refusal paths enforce compatibility before session activation.
- Arbitration and transition decisions remain deterministic and traceable in transition event payloads.

## 6) Guardrails Added

### RepoX invariants

1. `INV-NO-WALLCLOCK-IN-PERFORMANCE`
2. `INV-INSPECTION-IS-DERIVED`

### AuditX analyzers

1. `E48_PERFORMANCE_NONDETERMINISM_SMELL`
2. `E49_UNBOUNDED_MICRO_EXPANSION_SMELL`

### TestX coverage

1. `testx.performance.cost_accounting_deterministic`
2. `testx.performance.arbitration_equal_share`
3. `testx.performance.budget_exceeded_triggers_degrade_not_lag`
4. `testx.performance.inspection_cache_reuse`
5. `testx.performance.inspection_invalidation_on_state_change`
6. `testx.performance.multiplayer_fairness_under_spread_players`

## 7) Gate Execution (RS-5 Final)

1. RepoX PASS
   - command: `py -3 -m tools.xstack.repox.check --profile STRICT`
   - result: `status=pass`, `findings=0`
2. AuditX run PASS
   - command: `py -3 -m tools.xstack.auditx.check --profile STRICT`
   - result: `status=pass` (warn findings present; no fail)
3. TestX PASS (RS-5 suite)
   - command: `py -3 tools/xstack/testx/runner.py --profile STRICT --subset testx.performance.cost_accounting_deterministic,testx.performance.arbitration_equal_share,testx.performance.budget_exceeded_triggers_degrade_not_lag,testx.performance.inspection_cache_reuse,testx.performance.inspection_invalidation_on_state_change,testx.performance.multiplayer_fairness_under_spread_players`
   - result: `status=pass`, `selected_tests=6`
4. strict build PASS
   - command: `py -3 tools/setup/build.py --repo-root . --bundle bundle.base.lab --out build/dist.strict.rs5 --cache on --format json`
   - result: `result=complete` (build + validation complete)
5. `ui_bind --check` PASS
   - command: `py -3 tools/xstack/ui_bind.py --repo-root . --check`
   - result: `result=complete`, `checked_windows=21`

## 8) Extension Points (MAT/DOM)

1. Cost classes can be refined per domain solver tier without changing deterministic envelope enforcement.
2. Transition arbitration weights can consume richer server profile metadata while preserving stable tie-break rules.
3. Inspection snapshots can incorporate richer derived domain views without truth mutation.
4. Cross-domain inspect invalidation can add contract-specific invalidation rules while preserving deterministic cache keys.
