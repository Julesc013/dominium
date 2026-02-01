Status: DERIVED
Last Reviewed: 2026-02-01
Supersedes: none
Superseded By: none

# Streaming Budgets Policy (PERF0)

This document defines enforceable streaming budgets and cache policy.
Streaming MUST be interest-set driven, budgeted, and non-blocking.

## Scope

Applies to all streamed systems:
- WSS tiles
- meshes
- textures
- shader variants

## Per-frame budgets (measurable)

Budgets are per frame and MUST be enforced by schedulers.

### Baseline tier (2010 hardware)
- Derived jobs: <= 2.0 ms/frame
- IO: <= 256 KB/frame
- Decode ops: <= 2/frame
- Shader variant prepares: <= 0/frame (precompile only)

### Modern tier (2020 hardware)
- Derived jobs: <= 4.0 ms/frame
- IO: <= 1 MB/frame
- Decode ops: <= 6/frame
- Shader variant prepares: <= 1/frame (preload only)

### Server tier
- Derived jobs: <= 1.0 ms/tick
- IO: <= 128 KB/tick
- Decode ops: <= 0/tick

## Interest-set driven prefetching

- Prefetching MUST be driven by interest sets, not global scans.
- Interest sets MUST be bounded and deterministic.
- Prefetch requests MUST be coalesced per frame to avoid bursts.

## Cache policies

- LRU is required for streamed assets.
- Pinned assets MUST be explicitly declared and budgeted.
- Eviction MUST be deterministic and independent of wall-clock time.

## Violations

Any budget breach is a failure:
- Derived job over budget
- IO over budget
- Decode op count over budget
- Shader variant work outside preload phase

## Failure artifacts

On violation, emit a report under `run_root/perf/streaming/`:
- budget type and threshold
- observed value
- asset identifiers
- frame/tick identifiers