Status: DERIVED
Last Reviewed: 2026-05-16
Supersedes: none
Superseded By: none

# POST-CONVERGE-10I Historical Reference and Archive Citation Remediation

## Status

- Task ID: POST-CONVERGE-10I
- Result: PARTIAL
- Branch: main
- HEAD: `978818004c435ad2ca53355e065a888800fe2a94`
- origin/main: `978818004c435ad2ca53355e065a888800fe2a94`
- Worktree before: clean at task start
- Worktree after: scoped historical-reference rule/evidence/docs edits before commit

## Scope

Focused historical reference remediation only. No root moves, feature work, product proof, package proof, source behavior changes, evidence deletion, historical rewrite, or broad docs rewrite were performed.

## Prior State

POST-CONVERGE-10H reduced focused RepoX from 1769 failures to 153 failures and left `INV-CANON-NO-HIST-REF` as the largest remaining family with 81 failures.

## Reproduction

| Command | Result | Failures | Warnings | Notes |
| --- | --- | ---: | ---: | --- |
| `ctest --preset verify -N` | pass with warning | n/a | n/a | Canonical verify discovery still reports 0 tests. |
| `ctest --preset verify -R inv_repox_rules --output-on-failure` | pass with warning | n/a | n/a | No matching tests in canonical verify discovery. |
| `ctest --test-dir .dominium.local/build/tuple.verify.winnt10.x64.msvc143.mt.debug -C Debug -R inv_repox_rules --output-on-failure` | fail expected | 71 | 5 | Focused tuple RepoX after 10I. |
| `python scripts/ci/check_repox_rules.py --repo-root .` | fail expected | 71 | 5 | Uncached direct RepoX after 10I. |

## Historical Reference Findings

- Checked `INV-CANON-NO-HIST-REF` failures: 81
- Legitimate generated/DERIVED quarantine evidence references: 81
- Stale current references found: 0
- Root-recycling/migration references rewritten: 0
- Historical/audit references deleted: 0

The failures were all `docs/refactor/QUARANTINE_*` DERIVED evidence packets that cite `docs/archive/**` as part of duplicate/quarantine audit evidence. Those citations should remain.

## Changes Made

- Updated `scripts/ci/check_repox_rules.py` so `INV-CANON-NO-HIST-REF` applies to documents that are canonical by status header or `CANON_INDEX` membership.
- Added POST-CONVERGE-10I AIDE findings, before/after, validation, blocker, and next-family reports.
- Updated post-converge status/readiness docs with the new focused RepoX counts.

## Before/After

| Metric | Before | After |
| --- | ---: | ---: |
| RepoX failures | 153 | 71 |
| RepoX warnings | 5 | 5 |
| `INV-CANON-NO-HIST-REF` | 81 | 0 |

## Remaining Blockers

- `INV-DOC-STATUS-HEADER`: 12
- `INV-NEW-CONTRACT-REQUIRES-ENTRY`: 9
- `INV-ALL-PRODUCTS-EMIT-DESCRIPTOR`: 7
- `INV-NO-ADHOC-MAIN`: 5
- `INV-TOOLS-REQUIRE-ENTITLEMENT`: 5
- `INV-REPLAY-REFUSES-CONTRACT-MISMATCH`: 4
- `INV-CACHE-KEY-INCLUDES-CONTRACTS`: 2
- `INV-TOOL-VERSION-MISMATCH`: 2
- `INV-UNIVERSE-MUST-HAVE-CONTRACT-BUNDLE`: 2
- `INV-BODY-MOTION-PROCESS-ONLY`: 1
- `INV-CAMERA-SMOOTH-RENDER-ONLY`: 1
- `INV-CANON-NO-SUPERSEDED`: 1
- `INV-COLLISION-DETERMINISTIC`: 1
- `INV-CONFLICTS-NOT-SILENT-IN-STRICT`: 1
- `INV-IDENTITY-FINGERPRINT`: 1
- `INV-JUMP-PROFILE-GATED`: 1
- `INV-LENS-PROFILED`: 1
- `INV-NO-ASSET-DEPENDENCY-FOR-EMB`: 1
- `INV-NO-BLOCKING-WORLDGEN-IN-UI`: 1
- `INV-NO-EXTENSION-INTERPRETATION-WITHOUT-REGISTRY`: 1
- `INV-NO-FLOAT-SMOOTHING`: 1
- `INV-NO-IDENTITY-OVERRIDE`: 1
- `INV-NO-RANDOM-RETRY-LOOPS-IN-WORLDGEN`: 1
- `INV-NO-SILENT-DEGRADE`: 1
- `INV-NO-TRUTH-LEAK-IN-SCANS`: 1
- `INV-OVERLAY-CONFLICT-POLICY-DECLARED`: 1
- `INV-REFINEMENT-BUDGETED`: 1
- `INV-REPOX-RULESET-MISSING`: 1
- `INV-REPRO-BUNDLE-DETERMINISTIC`: 1
- `INV-REPRO-BUNDLE-NO-SECRETS`: 1
- `INV-SHADOW-BOUNDED`: 1
- `INV-TERRAIN-EDITS-PROCESS-ONLY`: 1

## Product Boot Readiness

POST-CONVERGE-11 is not ready. Focused RepoX still has real governance failures.

## Validation

Final validation results are recorded in `.aide/reports/POST-CONVERGE-10I-validation.md` and the commit message.

## POST-CONVERGE-10J Follow-up

POST-CONVERGE-10J reduced the authority-sensitive doc status backlog from 12 to 0 and reduced focused RepoX from 71 failures / 5 warnings to 60 failures / 5 warnings. Historical reference debt remains cleared; POST-CONVERGE-11 remains blocked by other RepoX families.
