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
- Render/UI thread IO ban (runtime trace + watchdog)
- Stall watchdog thresholds

### Stall watchdog thresholds

Any of the following is a failure:
- Render-thread stall > 2 ms caused by IO/compile/decode
- UI-thread stall > 1 ms caused by IO/compile/decode
- Any blocking file or network call on render/UI threads regardless of duration

## Failure artifacts

On violation, emit a structured report under `run_root/perf/no_modal_loading/`:
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
