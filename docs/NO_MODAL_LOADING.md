# No-Modal-Loading Policy (PERF0)

This document defines non-negotiable rules that forbid modal loading and blocking work
on render or UI threads. Violations are merge-blocking.

## Scope

Applies to all runtime code paths in:
- engine
- client
- server (for derived/preview systems)

## Non-negotiable rules

Render/UI threads MUST NOT:
- perform file IO
- decompress or decode assets
- compile shaders
- block on network
- wait on long-running jobs

All heavy work MUST be:
- asynchronous
- derived-only (never mutates authoritative state)
- budgeted per frame

## Violation detection

The following checks are mandatory:
- Render/UI thread IO ban (runtime guard + report)
- Stall watchdog thresholds

### Enforcement mechanisms (PERF1)

- UI/render threads MUST be tagged as no-block via `dsys_thread_tag_current(..., DSYS_THREAD_FLAG_NO_BLOCK)`.
- File IO MUST go through `dsys_file_*` wrappers (no direct `fopen`/platform IO in UI code); UI thread calls are blocked and reported (PERF-IOBAN-001).
- Stall watchdog uses `dsys_stall_watchdog_frame_begin/end` on no-block threads (PERF-STALL-001).
- Derived work MUST be enqueued via `dsys_derived_job_submit` and executed off the UI thread.
- ACT and sim tick values used in reports MUST be injected via `dsys_guard_set_act_time_us` and `dsys_guard_set_sim_tick`.

### Stall watchdog thresholds

Any of the following is a failure:
- Render-thread stall > 2 ms caused by IO/compile/decode
- UI-thread stall > 1 ms caused by IO/compile/decode
- Any blocking file or network call on render/UI threads regardless of duration

## Failure artifacts

On violation, emit a structured report under `run_root/perf/no_modal_loading/` with deterministic filenames:
- `PERF-IOBAN-001_####.log`
- `PERF-STALL-001_####.log`

Each report MUST include:
- thread name/id
- call site (file:line)
- blocking operation type (IO/decode/compile/network/wait)
- duration
- frame/tick identifiers

## Prohibitions (absolute)

- “Loading screens” are FORBIDDEN as a requirement for correctness.
- Synchronous IO on UI/render threads is FORBIDDEN.
- Per-frame asset decoding is FORBIDDEN.
- Blocking on long jobs from UI/render threads is FORBIDDEN.
