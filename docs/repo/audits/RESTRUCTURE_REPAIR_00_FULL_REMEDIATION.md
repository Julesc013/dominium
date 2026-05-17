Status: DERIVED
Last Reviewed: 2026-05-18
Supersedes: none
Superseded By: none

# RESTRUCTURE-REPAIR-00 Full Remediation

## Status

Result: PARTIAL.

The repair pass fixed safe stale-path, test-contract, and proof-output issues discovered during post-restructure validation. It did not force unsafe root moves, policy renewals, frozen-hash refreshes, or replay-hash acceptance.

## Scope

This was structural repair and proof only. No feature, gameplay, renderer, GUI, worldgen expansion, release publication, tag, installer, or GitHub release work was performed.

## Repairs Applied

- App/client path expectations were updated to current `apps/client/core/**` and `runtime/app/**` homes.
- RepoX helper test calls were updated for the current helper signature.
- Ops compatibility JSON output no longer receives a Python 3.14 deprecation warning on stdout.
- TestX host-path fixtures no longer trip source path hygiene while preserving leak-test semantics.
- Archive presence fixtures now point to `archive/legacy/` and `archive/generated/` instead of retired top-level roots.
- The focused RepoX archive allowlist now matches the repaired archive fixture roots.
- Narrow current contract references were added to pack, lockfile, and budget docs.
- The hardcoded-identifier lint now prints deterministic diagnostics on Windows codepages.

## Validation Summary

Passing: AIDE, strict repo/root/distribution/component validators, docs/build/UI/ABI checks, focused RepoX, smoke CTest, CMake configure, build-only `ALL_BUILD`, product boot proof, portable projection proof, and internal pilot proof.

Partial/failing: full CTest remains failing and incomplete due hardcoded-id findings, hardcoded-constant findings, frozen hash drift, expired overrides, replay hash mismatches, and AuditX timeouts.

## Root State

`ide/` is retired. The other 23 formerly bad roots remain tracked and excepted, totaling 1,764 tracked files. No unexcepted bad roots were reported by strict validators.

## Generated Output Policy

`.aide.local/**`, `.dominium.local/**`, `build/`, `out/`, `dist/`, and `tmp/` remain ignored local output and were not staged.

## Readiness

DOE-00 is not authorized. Feature implementation remains blocked.

Next task: `MOVE-BULK-A-SKIPPED-REFERENCE-REFINEMENT`.
