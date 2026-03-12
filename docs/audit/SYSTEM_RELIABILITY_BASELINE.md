Status: BASELINE
Last Reviewed: 2026-03-06
Version: 1.0.0
Scope: SYS-6 System Reliability, Failure Budgeting, and Predictive Expand-on-Edge
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: canon-aligned documentation set for convergence and release preparation

# System Reliability Baseline

## Summary
SYS-6 introduces deterministic reliability evaluation for systems and macro capsules without changing domain semantics.

Delivered capabilities:
- deterministic per-system health aggregation (`process.system_health_tick`) with bounded update scheduling,
- deterministic reliability evaluation (`process.system_reliability_tick`) using registry-declared reliability profiles,
- warning, forced-expand, safe-fallback, and failure pathways with canonical logging,
- optional profile-gated stochastic branch using named RNG streams with proof logging,
- macro capsule integration for reliability-driven output degradation and safety shutdown behavior,
- explain and inspection integration for reliability warnings/failures,
- replay verification for reliability hash chains and event windows.

## Reliability Profiles
Registry:
- `data/registries/reliability_profile_registry.json`

Declared starter profiles:
- `reliability.engine_basic`
- `reliability.pump_basic`
- `reliability.pressure_system_basic`
- `reliability.power_system_basic`
- `reliability.reactor_stub`

Profile contracts include:
- failure mode declarations,
- deterministic warning/forced-expand/failure thresholds,
- optional stochastic controls (`stochastic_allowed`, `rng_stream_name`),
- safe fallback safety-pattern references.

## Execution Model
Health aggregation engine:
- `src/system/reliability/system_health_engine.py`
- aggregates bounded hazard and entropy inputs into canonical `system_health_state_rows`,
- deterministic ordering by `system_id`,
- deterministic budget degradation via tick-bucket stride controls.

Reliability engine:
- `src/system/reliability/reliability_engine.py`
- evaluates macro systems against trigger rules,
- emits warning rows, forced expand requests, safe fallback rows, and canonical failure events,
- logs deterministic decision/refusal evidence for denied expands.

Runtime/process integration:
- `tools/xstack/sessionx/process_runtime.py`
- process IDs:
  - `process.system_health_tick`
  - `process.system_reliability_tick`
- reliability outputs are integrated into macro execution pathways through process-governed effects/ledger rows only.

## Forced Expand and Safe Fallback
Expand-on-edge behavior:
- warning threshold exceeded: warning artifact/event pathway,
- forced-expand threshold exceeded: deterministic forced-expand request,
- expand denied: deterministic safe fallback action list applied and logged,
- failure threshold exceeded: canonical `failure_event` emitted with safety shutdown/isolation actions.

No silent transitions are allowed; all critical reliability transitions are logged and hash chained.

## Explain and Inspection Integration
Explain contracts:
- `explain.system_warning`
- `explain.system_forced_expand`
- `explain.system_failure`

Inspection sections:
- `section.system.health_summary`
- `section.system.failure_risks`

Diegetic indicators (policy/lens gated):
- warning light semantics,
- maintenance-required marker semantics,
- system quarantined marker semantics.

## Proof and Replay
Reliability proof chains:
- `system_health_hash_chain`
- `system_failure_event_hash_chain`
- `system_warning_hash_chain`
- `system_reliability_rng_hash_chain`
- existing `system_forced_expand_event_hash_chain`

Replay tool:
- `tools/system/tool_replay_system_failure_window.py`
- wrappers:
  - `tools/system/tool_replay_system_failure_window`
  - `tools/system/tool_replay_system_failure_window.cmd`

## Validation Snapshot (SYS-6)
- RepoX STRICT: PASS (validated on clean committed worktree).
- AuditX STRICT: PASS.
- TestX SYS-6 subset: PASS.
- Reliability stress run (many near-failure systems): PASS.
- strict build (`python tools/xstack/run.py strict --repo-root . --cache on`): REFUSAL due pre-existing global strict-lane blockers outside SYS-6 scope (CompatX/pack/session/bootstrap/full-lane TestX/packaging).
- topology map refresh: PASS.

## Readiness for SYS-7
SYS-6 outputs provide deterministic, replay-safe reliability substrate for SYS-7 system forensics:
- canonical failure/forced-expand/warning event streams exist and are hash chained,
- optional stochastic behavior is profile-gated and proof-logged,
- macro-tier reliability behavior remains process-only, safety-bound, and explain-ready.
