Status: CANONICAL
Last Reviewed: 2026-03-14
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: ENGINE/CONCURRENCY
Replacement Target: release-pinned shard-merge execution contract and target-specific worker policy envelopes

# Concurrency Determinism Contract

## Determinism Principle

Canonical state mutation order must be identical regardless of:

- thread count
- scheduler interleaving
- host CPU differences
- OS thread wake order

Truth execution remains lawful only when identical inputs produce identical authoritative hashes under all allowed worker counts.

## Allowed Parallelism

- Derived artifact generation may be parallelized when each task is a pure function and the merged output is canonicalized before hashing, serialization, or persistence.
- Validation and audit pipelines may be parallelized when result rows are canonicalized before status reduction, report writing, or cache storage.
- Canonical truth execution may be single-threaded or sharded only when the merge contract is deterministic and independent of completion order.

## Task Scheduling Contract

When a task system is used:

- tasks must be keyed by stable ids
- task completion order must not affect outcome
- merges must be stable-sorted by canonical key before hashing or persistence
- scheduler metadata may report requested worker counts, but authoritative commit ordering may not vary by those counts

## Locks And Atomics

- lock timing must never determine a canonical outcome
- atomics are allowed only for non-authoritative counters or derived contexts
- “first writer wins” behavior is forbidden in truth paths unless expressed through deterministic shard merge law
- any threaded truth write path without deterministic shard merge must refuse in strict governance

## Refusal

- `refusal.determinism.threading_violation`

## Current MVP Policy

- default authoritative policy: `concurrency.single_thread`
- allowed derived policy: `concurrency.parallel_derived`
- allowed validation policy: `concurrency.parallel_validation`
- `allow_parallel_truth` remains `false` for all declared MVP policies
