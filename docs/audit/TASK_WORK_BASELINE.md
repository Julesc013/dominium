Status: DERIVED
Last Reviewed: 2026-03-16
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: canon-aligned documentation set for convergence and release preparation

# TASK_WORK Baseline

Status: ACT-3 baseline complete
Version: 1.0.0

## Scope
ACT-3 introduces deterministic task/work primitives for ActionSurface-driven interactions. Tasks are commitment-aware, budgeted, interruptible progress containers that hand off mutation via process intents at completion.

## Schemas
Source schemas:
- `schema/interaction/task.schema`
- `schema/interaction/task_type.schema`
- `schema/interaction/progress_model.schema`

Compiled schemas:
- `schemas/task.schema.json`
- `schemas/task_type.schema.json`
- `schemas/progress_model.schema.json`
- `schemas/task_type_registry.schema.json`
- `schemas/progress_model_registry.schema.json`

## Registries
- `data/registries/task_type_registry.json`
- `data/registries/progress_model_registry.json`

Baseline task types:
- `task.cut_tree`
- `task.saw_plank`
- `task.tighten_fastener`
- `task.loosen_fastener`
- `task.repair_basic`
- `task.machine_adjust`

Baseline progress models:
- `progress.linear_default`
- `progress.heavy_work_default`

## Runtime Behavior
- Processes:
  - `process.task_create`
  - `process.task_tick`
  - `process.task_pause`
  - `process.task_resume`
  - `process.task_cancel`
- Deterministic ordering: `(status, -priority, task_id)` for active ticking.
- Fixed-point progress math with deterministic quantization.
- Completion emits deterministic pending process intents (process-only mutation handoff).

## Commitments And Reenactment
- Task creation may create linked commitments when strictness requires.
- Task lifecycle events are stored and linkable in event stream indexing.
- Timeline exporter:
  - `tools/interaction/tool_task_timeline_export.py`

## Diegetic Integration
- Added channels:
  - `ch.diegetic.task.progress`
  - `ch.diegetic.task.status`
- Observation redaction retains diegetic coarse defaults.

## Guardrails
RepoX invariants:
- `INV-TASKS-PROCESS-ONLY-MUTATION`
- `INV-NO-WALLCLOCK-IN-TASKS`

AuditX analyzers:
- `TaskNonDeterminismSmell`
- `TaskBypassSmell`

TestX:
- `test_task_progress_deterministic`
- `test_task_pause_resume_deterministic`
- `test_task_budget_degrade_deterministic`
- `test_task_completion_triggers_process_intent`
- `test_task_commitment_created_when_required`
- `test_mp_task_authoritative_validation`

## Gate Snapshot
- Run date: 2026-02-28
- RepoX (`python tools/xstack/repox/check.py --profile STRICT`): PASS (`findings=0`)
- AuditX (`python tools/auditx/auditx.py verify --repo-root . --format both`): run complete (`findings_count=994`, existing repo baseline)
- TestX ACT-3 required subset (`python tools/xstack/testx_all.py --repo-root . --profile STRICT --subset ...`): PASS (`selected_tests=6`)
- strict build (`python tools/xstack/run.py strict`): REFUSAL due existing repo-baseline CompatX findings (`schemas=265, findings=127`) and full-suite TestX findings (`selected_tests=336, findings=25`)
- ui_bind --check (`python tools/xstack/ui_bind.py --check`): PASS (`checked_windows=21`)

## Extension Points
- Completion-process stubs can target tree cutting, fasteners, machine operations.
- Actor execution can extend to NPC/robot/cohort machine controllers.
- MAT-5 construction steps can be unified into shared Task progression contracts.
