Status: DERIVED
Last Reviewed: unknown
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: canon-aligned documentation set for convergence and release preparation

# SAFETY Pattern Baseline

Status: BASELINE
Scope: SAFETY-0
Updated: 2026-03-03

## Pattern Definitions

SAFETY-0 baseline patterns are registered in `data/registries/safety_pattern_registry.json`:

- `safety.interlock_block`
- `safety.fail_safe_stop`
- `safety.relief_pressure`
- `safety.breaker_trip`
- `safety.redundant_pair`
- `safety.deadman_basic`
- `safety.loto_basic`
- `safety.graceful_degrade_basic`

Authoritative doctrine:

- `docs/safety/SAFETY_PATTERN_LIBRARY.md`

Schema contracts:

- `schema/safety/safety_pattern.schema`
- `schema/safety/safety_instance.schema`

## Cross-Domain Usage

SAFETY-0 integration hooks are wired through process execution and event logging:

- MOB signaling interlock hook emits `safety.interlock_block` safety events.
- MOB derail process emits fail-safe safety hook events (`safety.fail_safe_stop`).
- MECH fracture process emits graceful degradation safety hook events (`safety.graceful_degrade_basic`).
- SIG jamming process emits watchdog/deadman safety hook events (`safety.deadman_basic`).

Safety actions execute through deterministic process mediation in `process.safety_tick`:

- constraint locking
- state transitions via state-machine transitions
- effect application
- flow disconnect
- refusal emission markers

## Determinism Guarantees

- Safety instance evaluation order is deterministic (`instance_id` sorted).
- Safety actions are ordered by `(instance_id, action_sequence, action_id)`.
- Budget degradation is deterministic through explicit defer sets.
- Safety events are deterministic artifacts with stable fingerprints.
- Heartbeat/watchdog state is preserved in runtime state (`heartbeat_rows`) and used deterministically for deadman checks.

## SAFETY-0 Validation Summary

Executed commands:

- `python tools/xstack/testx/runner.py --profile FAST --cache off --subset test_interlock_prevents_conflict,test_fail_safe_defaults,test_breaker_trip_disconnects_flow,test_deadman_timeout,test_safety_event_logged,test_deterministic_ordering_of_instances`
- `python tools/governance/tool_topology_generate.py --repo-root .`
- `python tools/xstack/repox/check.py --repo-root . --profile STRICT`
- `python tools/auditx/auditx.py verify --repo-root .`
- `python tools/xstack/run.py strict`

Observed results:

- Safety TestX subset: PASS (6/6).
- Topology map: regenerated (`docs/audit/TOPOLOGY_MAP.json`, fingerprint `aa2efd3e5e5d102e470294ccb95aee03aadf48a08a18dbdd523f4f25ef949f78`).
- AuditX: run completed and outputs refreshed under `docs/audit/auditx/`.
- RepoX STRICT: refusal remains due non-SAFETY pre-existing/global findings, including `INV-NO-RANKED-FLAGS` in `tools/signals/tool_run_sig_stress.py`.
- strict build (`tools/xstack/run.py strict`): global pipeline error/refusals outside SAFETY-0 scope (CompatX findings, RepoX refusal, TestX full-suite failures, packaging missing pack artifact).

## Extension Guidance (ELEC / LOGIC / DOM)

Future domains must:

- register protection semantics as `safety_pattern` templates, not inline runtime branches;
- instantiate via `safety_instance` and evaluate through `process.safety_tick`;
- declare and log all safety-triggered actions/effects/events;
- preserve deterministic ordering, budgeted degradation, and replayability.
