Status: CANONICAL
Last Reviewed: 2026-02-14
Supersedes: none
Superseded By: none

# XStack Production Criteria

## Purpose

This document defines production-readiness criteria for XStack hardening without changing FAST/STRICT/FULL semantics, canonical artifact contracts, or runtime removability.

## Required Criteria

- [x] Deterministic plan hashing
- [x] Deterministic runner ordering
- [x] Cold STRICT bounded
- [x] Warm STRICT near-instant
- [x] FULL sharded + deterministic aggregation
- [x] Zero tracked writes outside snapshot policy
- [x] Removability proven
- [x] Failure classification implemented
- [x] Execution ledger enabled
- [x] Workspace isolation
- [x] Cache corruption detection
- [x] Performance ceiling detection
- [x] Extension hooks stable
- [x] Portability documented

## Validation Sources

- planner and scheduler invariants in `tools/xstack/core/`
- gate write-policy enforcement in `scripts/dev/gate.py`
- portable environment/workspace rules in `scripts/dev/env_tools_lib.py`
- integration and invariant coverage in `tests/invariant/` and `tests/integration/`
- portability governance in `docs/governance/XSTACK_PORTABILITY.md`

## Acceptance Notes

- Determinism requirements are evaluated on canonical payloads and canonical ordering.
- Run-meta artifacts remain non-canonical and must not influence plan hash, cache key semantics for canonical outputs, or canonical artifact hashing.
- Workspace isolation applies to XStack run-meta and cache surfaces.
