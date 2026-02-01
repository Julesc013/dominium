Status: DERIVED
Last Reviewed: 2026-02-01
Supersedes: none
Superseded By: none

# JOB ENGINE (RESUMABLE JOBS)

This document defines the resumable job model used by launcher and setup.

## Overview
- Jobs are deterministic DAGs of steps with explicit dependencies.
- Progress is journaled in TLV files and can be resumed after interruption.
- Every job ends with a recorded outcome (OK/FAILED/REFUSED/CANCELLED/PARTIAL).

## Core Model
Core structures live in `include/dominium/core_job.h`.
- `core_job_def`: static job definition (type + steps + dependencies).
- `core_job_state`: runtime progress (current step, completed bitset, retries, outcome, last_error).

Step flags:
- `CORE_JOB_STEP_IDEMPOTENT`: safe to re-run.
- `CORE_JOB_STEP_RETRYABLE`: safe to retry on failure.
- `CORE_JOB_STEP_REVERSIBLE`: has rollback.
- `CORE_JOB_STEP_HAS_CHECKPOINT`: uses persisted checkpoint.

## Journal Layout (TLV)
Job journals are TLV-only and skip-unknown.

Setup job journals live under the install root:
```
<install_root>/.dsu_txn/jobs/<job_id>/
  job_def.tlv
  job_state.tlv
  job_input.tlv
  job_events.tlv
```

Launcher job journals follow the launcher instance staging layout (see launcher core docs).

## Resume Semantics
- On start, the frontend scans for incomplete jobs (outcome = NONE).
- Resume uses `job_def.tlv` + `job_state.tlv` + `job_input.tlv`.
- If a job definition is incompatible, return a refusal (`ERRF_NOT_SUPPORTED`).
- Steps are executed only when dependencies are satisfied; completed steps are not re-run.

## Adding a Job Type
1) Append a new `core_job_type` value in `include/dominium/core_job.h` (never renumber).
2) Define a static job def (steps + dependencies) in the module owning the job.
3) Implement each step deterministically; mark idempotent/retryable.
4) Persist progress after each step and emit structured events.
5) Add tests that simulate interruption and resume.

## Determinism & Safety
- Jobs must not depend on wall-clock time or OS locale.
- Journals are written atomically (temp + rename).
- No silent failures: every job has a final outcome and `err_t` (if failed/refused).