Status: DERIVED
Last Reviewed: 2026-02-15
Supersedes: none
Superseded By: none
Version: 1.0.0
Compatibility: Bound to `schema/session/session_stage.schema` v1.0.0, `schema/session/session_pipeline.schema` v1.0.0, and registries under `data/registries/`.
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: canon-aligned documentation set for convergence and release preparation

# Session Pipeline Contract Report

## Scope
Audit proof for Prompt 14 session pipeline formalization and enforcement:
- canonical stage and pipeline schemas
- registry-driven stage execution
- abort/resume/re-entry discipline
- server-side stage/authority gate
- launcher/setup integration and RepoX invariants
- CLI/TUI/GUI parity adapters
- strict validation gates including `ui_bind --check`

## Stage Definitions
Canonical stage registry source:
- `data/registries/session_stage_registry.json`

Declared deterministic stages:
1. `stage.resolve_session`
2. `stage.acquire_world`
3. `stage.verify_world`
4. `stage.warmup_simulation`
5. `stage.warmup_presentation`
6. `stage.session_ready`
7. `stage.session_running`
8. `stage.suspend_session`
9. `stage.resume_session`
10. `stage.teardown_session`

All canonical rows declare `deterministic=true`.
`stage.session_ready` enforces `extensions.ready_time_must_equal_tick = 0`.

## Transition Map
Pipeline source:
- `data/registries/session_pipeline_registry.json`

Canonical ordered path:
`stage.resolve_session -> stage.acquire_world -> stage.verify_world -> stage.warmup_simulation -> stage.warmup_presentation -> stage.session_ready -> stage.session_running -> stage.suspend_session -> stage.resume_session -> stage.teardown_session`

Transition enforcement:
- client boot path: `tools/xstack/sessionx/runner.py`
- stage/abort/resume controls: `tools/xstack/sessionx/session_control.py`
- server authority gate: `tools/xstack/sessionx/server_gate.py`

Refusal codes:
- `refusal.stage_invalid_transition`
- `refusal.session_ready_time_nonzero`
- `refusal.resume_incompatible`
- `refusal.resume_hash_mismatch`
- `refusal.resume_identity_violation`
- `refusal.server_stage_mismatch`
- `refusal.server_authority_violation`

## Enforcement Summary
1. Schema contracts
- `schemas/session_stage.schema.json`
- `schemas/session_pipeline.schema.json`
- `schemas/session_artifacts.schema.json`
- `schemas/session_spec.schema.json` (includes `pipeline_id`)

2. Registry loading and validation
- `tools/xstack/sessionx/pipeline_contract.py` validates stage and pipeline registries deterministically.

3. Stage execution discipline
- Runner derives stage log from registry order only.
- Illegal stage edges refuse deterministically.
- SessionReady requires `simulation_time.tick == 0` and no pre-begin tick execution.

4. Abort/resume/re-entry
- `client.session.abort` writes deterministic snapshot run-meta.
- `client.session.resume` validates lockfile hash, registry hash map, identity hash, and authority compatibility.
- Re-entry starts from declared pipeline and revalidates artifacts.

5. Server gate
- `tools/xstack/session_server` enforces declared transitions and authority binding prior to running transitions.

6. Launcher/setup guardrails
- Launcher supports deterministic SessionSpec creation with explicit `pipeline_id`.
- Launcher run path validates server gate before running-stage requests.
- Setup refuses stage-driving args (`REFUSE_SETUP_PIPELINE_FORBIDDEN`).

7. RepoX invariants
- `INV-SESSION-PIPELINE-DECLARED`
- `INV-NO-STAGE-SKIP`
- `INV-SESSION-READY-TIME-ZERO`

8. CLI/TUI/GUI parity
- `tools/xstack/session_surface` routes `stage/abort/resume` via shared control logic.
- Workspace payload parity includes `stage_id`, `stage_log`, `refusal_codes`.

9. UI binding gate
- `tools/xstack/ui_bind --check` validates ui registry descriptor bindings and file/schema consistency.

## Validation Evidence
Commands executed:
1. `python tools/xstack/repox/check.py --profile STRICT`
2. `python tools/xstack/testx/runner.py --profile STRICT --cache off`
3. `python tools/xstack/ui_bind.py --check`
4. `python tools/xstack/run.py strict --cache off`

Observed result:
- all commands completed without refusal/failure.

## Known Extensibility Points
- Additional pipelines can be added in `session_pipeline_registry.json` without code path forks.
- New stage rows can be introduced if schema-valid and transition-consistent.
- `run_meta_only` stage rows are supported for non-canonical observability stages.
- Server gate can add shard-aware checks later without changing client command contracts.
- Parity adapter can be bound to concrete TUI/GUI frontends while preserving shared stage control semantics.

## Cross-References
- `docs/client/CLIENT_LIFECYCLE_PIPELINE.md`
- `docs/client/SESSION_READY_AND_RUNNING.md`
- `docs/client/CLI_TUI_GUI_PARITY.md`
- `docs/contracts/refusal_contract.md`
- `docs/testing/xstack_profiles.md`
