# SPEC_JOBS — Jobs / Tasks (JOB)

This spec defines the deterministic job/task layer and its data model. Jobs are
engine-level task instances parameterized by content templates; the engine only
enforces generic feasibility/ordering constraints and does not embed product
gameplay semantics.

## Scope
Applies to:
- job record storage and persistence (`d_job_record`)
- deterministic job creation/cancellation/update APIs
- job template parameters consumed from content (requirements/rewards)

This repo also contains an older, tile-oriented job API (`djob_*`) in
`include/domino/djob.h`. That API is legacy compatibility and is not the
authoritative job representation.

## Authoritative representation (current)
Job records are stored as `d_job_record` (`source/domino/job/d_job.h`):
- Stable identity: `d_job_id id`, `d_job_template_id template_id`
- State: `d_job_state state`, `d_agent_id assigned_agent`, `progress` (Q16.16)
- Targets: `target_struct_eid`, `target_spline_id`, and/or `(target_x,y,z)` (Q32.32)

## Owns / Produces / Consumes

### Owns (authoritative)
JOB owns:
- the job record set for a world (stable IDs, deterministic ordering)
- authoritative job state transitions (pending/assigned/running/completed/cancelled)

### Produces (derived outputs)
- derived job/agent scheduling decisions (e.g. assignment plans)
- optional diagnostics (counts, reasons for refusal) that MUST NOT affect SIM

### Consumes
- content-defined job templates (`d_proto_job_template`) and their TLV blobs
  (`requirements`, `rewards`, `params`)
- policy constraints (if applied) and deterministic world queries required to
  validate targets

## Template TLVs (content-defined)
Shared tag IDs live in `source/domino/content/d_content_extra.h`.

Implemented consumption:
- `D_TLV_JOB_REQ_AGENT_TAGS` is used to filter eligible agents in the planner.
- `D_TLV_JOB_REWARD_PAYMENT` is consumed by reward application.

Reserved (defined in content tags but not enforced by JOB in this revision):
- `D_TLV_JOB_ENV_RANGE` (environment range requirements)

Any future enforcement MUST be deterministic, budgeted, and ordered canonically.

## Determinism + ordering
- Job IDs and agent IDs are stable integers; iteration MUST be in ascending ID
  order (no hash-table iteration, no pointer ordering).
- If selection/assignment requires tie-breaks, tie-break keys MUST be explicit
  and stable (IDs first, never pointer identity).
- Planner work MUST be bounded. Fixed caps (e.g. maximum jobs/agents per tick)
  MUST apply deterministic truncation (prefix by canonical order).

## Save/load framing
- Subsystem id: `D_SUBSYS_JOB` (`source/domino/core/d_subsystem.h`).
- Container tag: `TAG_SUBSYS_DJOB` (`source/domino/core/d_serialize_tags.h`).

## Forbidden behaviors
- UI-driven mutation: UI/tools emit intents only; they MUST NOT write job state
  directly.
- Platform-dependent behavior in deterministic paths (time, threads, IO).
- Unbounded per-tick allocation or scans without explicit caps/budgets.

## Source of truth vs derived cache
**Source of truth:**
- job record set and its committed state transitions
- content template IDs referenced by jobs

**Derived cache:**
- assignment plans and diagnostics

## Related specs
- `docs/SPEC_DETERMINISM.md`
- `docs/SPEC_ACTIONS.md`
- `docs/SPEC_SIM.md`
- `docs/SPEC_DOMINO_SUBSYSTEMS.md`
- `docs/SPEC_AGENT.md`
