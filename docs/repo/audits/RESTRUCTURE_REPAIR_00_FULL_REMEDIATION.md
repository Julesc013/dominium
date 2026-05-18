Status: DERIVED
Last Reviewed: 2026-05-18
Supersedes: none
Superseded By: none

# RESTRUCTURE-REPAIR-00 Full Remediation

## Status

Result: PARTIAL.

The repair pass fixed safe stale-path, test-contract, proof-output, frozen-hash, override-policy, replay-fixture, and AuditX scan-scope issues discovered during post-restructure validation. It did not force unsafe root moves, weaken semantic lint gates, or mark full CTest green.

## Scope

This was structural repair and proof only. No feature, gameplay, renderer, GUI, worldgen expansion, release publication, tag, installer, or GitHub release work was performed.

## Repairs Applied

- App/client path expectations were updated to current `apps/apps/client/session/**` and `runtime/shell/lifecycle/**` homes.
- RepoX helper test calls were updated for the current helper signature.
- Ops compatibility JSON output no longer receives a Python 3.14 deprecation warning on stdout.
- TestX host-path fixtures no longer trip source path hygiene while preserving leak-test semantics.
- Archive presence fixtures now point to `archive/legacy/` and `archive/generated/` instead of retired top-level roots.
- Focused RepoX archive allowlist now matches the repaired archive fixture roots.
- Narrow current contract references were added to pack, lockfile, and budget docs.
- Hardcoded-identifier lint prints deterministic diagnostics on Windows codepages.
- Frozen contract hashes were refreshed from current frozen surfaces without editing the frozen source text.
- Expired locklist overrides were removed rather than extended.
- Performance replay fixture hashes were refreshed from current replay stubs.
- AuditX graph/cache scans skip generated evidence and local proof roots.
- AuditX archive-policy analyzers use existing archive-policy evidence in static scan mode.

## Validation Summary

Passing: AIDE, strict repo/root/distribution/component validators, docs/build/UI/ABI checks, focused RepoX, smoke CTest, CMake configure, build-only `ALL_BUILD`, product boot proof, portable projection proof, internal pilot proof, frozen contract guard, override policy tests, and replay hash invariance.

Partial/failing: full CTest remains not green due hardcoded-id findings, hardcoded-constant findings, and AuditX wall-time.

## Root State

`ide/` is retired. The other 23 formerly bad roots remain tracked and excepted, totaling 1,764 tracked files. No unexcepted bad roots were reported by strict validators.

## Generated Output Policy

`.aide.local/**`, `.dominium.local/**`, `build/`, `out/`, `archive/generated/dist/`, and `tmp/` remain ignored local output and were not staged. Incomplete generated AuditX JSON from timed runs was not committed.

## Readiness

DOE-00 is not authorized. Feature implementation remains blocked.

Next task: `TEST-PERF-01 - CTest Sharding and AuditX Wall-Time Baseline`.
