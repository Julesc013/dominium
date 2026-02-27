Status: DERIVED
Last Reviewed: 2026-02-27
Supersedes: none
Superseded By: none
Version: 1.0.0
Compatibility: Bound to MAT-10 constitutional scope and canon.

# MAT-10 Performance And Scale Baseline

## Stress Scenario Parameters
- generator: `tools/materials/tool_generate_factory_planet_scenario.py`
- baseline seed: `202610`
- complexes: `18`
- logistics nodes: `96`
- active projects: `72`
- players: `48`
- ticks: `12`
- envelope:
  - `max_solver_cost_units_per_tick=9000`
  - `max_inspection_cost_units_per_tick=600`
  - `max_micro_parts_per_roi=96`

## Cost Envelope Results
- deterministic MAT subsystem cost model declared and integrated:
  - logistics (`manifest`, `routing`)
  - construction (`active_step`, `ag_node`)
  - decay (`tracked_asset`, bounded time-warp factor)
  - materialization (`micro_part_instance`)
  - inspection (`section`, `history_window`)
  - reenactment (`event`, `fidelity_multiplier`)
  - maintenance (`low_priority_asset`)
- stress harness reports per-tick solver and inspection cost units.
- deterministic degradation keeps per-tick costs bounded under envelope.

## Deterministic Degradation Statistics
- deterministic order:
  1. `inspection_fidelity_reduce`
  2. `materialization_cap`
  3. `construction_parallel_reduce`
  4. `logistics_batching`
  5. `maintenance_deferral`
  6. `creation_refusal`
- baseline degradation order fingerprint:
  - `6faa5279f8bba04bda7e28f24de43a2c9004705c08e6faea0d8d95234470c293`
- degradation sequence fingerprint:
  - `2492470714aec63c1888bdb1402386403c188e32b810a439ad7455b610071022`

## Cache Effectiveness
- inspection cache summary baseline:
  - hits: `528`
  - misses: `48`
  - hit_rate_permille: `916`
  - max_cache_entries: `48`
- constant inspection reuses cached artifacts and avoids recomputation thrash.

## Hash Stability
- short-run per-tick hash anchor stream recorded in:
  - `data/regression/mat_scale_baseline.json`
- final deterministic fingerprint (baseline run):
  - `b15aa3efcf3b07e4a7287a4596eca444493f3f1411b61ed8a60e32223995088e`

## Multiplayer Fairness Notes
- equal-share inspection arbitration is deterministic and policy-invariant across:
  - `policy.net.lockstep`
  - `policy.net.server_authoritative`
  - `policy.net.srz_hybrid`
- shares are sorted-player deterministic and bounded by +/-1 unit when remainder exists.

## Known Limits
- Stress harness is cost-unit based; it does not model hardware wall-clock throughput.
- Material/logistics/construction fidelity is intentionally macro/meso-first and degrades before correctness.
- Deeper solver realism remains deferred to future domain-specific packs/solvers.

## Extension Points
- MAT-11+ can add richer routing/priority heuristics while preserving deterministic ordering.
- Additional scenario generators can target shard-heavy multiplayer or long-range time-warp campaigns.
- Regression locks can expand to per-policy hash streams and shard-level fairness proofs.

## Gate Snapshot (2026-02-27)
1. RepoX PASS
   - command: `py -3 tools/xstack/repox/check.py --repo-root . --profile STRICT`
   - result: `status=pass`, findings=0
2. AuditX run
   - command: `py -3 tools/xstack/auditx/check.py --repo-root . --profile STRICT`
   - result: `status=pass`, findings=870 (warn-level findings)
3. TestX PASS (MAT-10 required subset + guard presence)
   - command: `py -3 tools/xstack/testx/runner.py --repo-root . --profile FAST --cache off --subset testx.materials.stress_scenario_deterministic,testx.materials.cost_usage_bounded_per_tick,testx.materials.degradation_order_deterministic,testx.materials.inspection_cache_prevents_thrashing,testx.materials.micro_materialization_bounded,testx.materials.hash_anchors_stable_under_stress,testx.materials.multiplayer_equal_share_arbitration,testx.materials.guardrail_declarations_present`
   - result: `status=pass`, selected_tests=8
4. strict build PASS
   - command: `cmake --build out/build/vs2026/verify --config Debug --target domino_engine dominium_game dominium_client`
   - result: build completed successfully
5. ui_bind --check PASS
   - command: `py -3 tools/xstack/ui_bind.py --repo-root . --check`
   - result: `result=complete`, checked_windows=21
