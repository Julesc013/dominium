Status: DERIVED
Last Reviewed: 2026-05-22
Task: AIDE-WORKFLOW-LAW-01
Stability: provisional
Binding Sources: `docs/repo/audits/PRODUCT_SPINE_REVIEW_01.md`, `.aide/queue/current.toml`, `contracts/aide/aide_workflow_law.v1.json`

# AIDE Parallel Execution Law

## Doctrine

Limited parallelism is allowed only when development remains non-blocking and
promotion remains evidence-blocked.

Large parallelism remains unauthorized until follow-up schema and promotion
policy tasks land.

## Limited Parallelism

Limited parallelism may be allowed after product-spine review when:

- fast strict passes
- dependency-direction strict has `0` violations
- AIDE validate/doctor passes or warnings are known
- queue/current is current
- task branches do not overlap unsafe paths
- coordinator ownership is explicit for queue/status/latest packet files

Before `AIDE-WORKUNIT-SCHEMA-01` and `AIDE-DEV-MAIN-POLICY-01`, the recommended
limit is 2 concurrent tasks and the hard maximum is 4.

## Large Parallelism

Large parallelism requires:

- `AIDE-WORKFLOW-LAW-01`
- `AIDE-WORKUNIT-SCHEMA-01`
- `AIDE-DEV-MAIN-POLICY-01`
- checkpoint/review policy
- repair/resume policy

Large parallel execution is not authorized by this task.

## Path Conflict Rules

- Only one coordinator task may edit `.aide/queue/current.toml` at a time.
- Only one task may update latest task/review/status packets at a time unless
  explicitly assigned.
- Structure-moving tasks must not run concurrently with broad dependency
  validators unless coordinated.
- CMake/global build files require explicit lane ownership.
- Root contracts require explicit lane ownership.
- Broad generated-output refreshes must not overlap semantic schema changes
  unless planned.
- Product/runtime, Workbench, renderer, native GUI, gameplay, release, and
  provider lanes remain blocked unless a future task explicitly authorizes them.

## Current Closeout

- `large_parallel_execution_authorized = false`
- `limited_parallel_prompt_generation_authorized = true`
- `limited_parallel_task_execution_authorized = false` until the next tasks
  declare non-overlapping paths and coordinator ownership.
- `recommended_parallel_candidate = PRESENTATION-CONTRACT-01`
