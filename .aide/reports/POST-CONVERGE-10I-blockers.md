# POST-CONVERGE-10I Blockers

Status: PARTIAL

## Blocking Issues

- Focused tuple `inv_repox_rules` still fails with 71 failures and 5 warnings.
- POST-CONVERGE-11 remains blocked.
- Canonical `ctest --preset verify -N` still discovers 0 tests.

## Fixed Family

| Family | Before | After | Notes |
| --- | ---: | ---: | --- |
| `INV-CANON-NO-HIST-REF` | 81 | 0 | DERIVED quarantine/archive evidence references preserved; rule aligned to canonical-doc scope. |

## Remaining RepoX Families

| Family | Count |
| --- | ---: |
| `INV-DOC-STATUS-HEADER` | 12 |
| `INV-NEW-CONTRACT-REQUIRES-ENTRY` | 9 |
| `INV-ALL-PRODUCTS-EMIT-DESCRIPTOR` | 7 |
| `INV-NO-ADHOC-MAIN` | 5 |
| `INV-TOOLS-REQUIRE-ENTITLEMENT` | 5 |
| `INV-REPLAY-REFUSES-CONTRACT-MISMATCH` | 4 |
| `INV-CACHE-KEY-INCLUDES-CONTRACTS` | 2 |
| `INV-TOOL-VERSION-MISMATCH` | 2 |
| `INV-UNIVERSE-MUST-HAVE-CONTRACT-BUNDLE` | 2 |
| `INV-BODY-MOTION-PROCESS-ONLY` | 1 |
| `INV-CAMERA-SMOOTH-RENDER-ONLY` | 1 |
| `INV-CANON-NO-SUPERSEDED` | 1 |
| `INV-COLLISION-DETERMINISTIC` | 1 |
| `INV-CONFLICTS-NOT-SILENT-IN-STRICT` | 1 |
| `INV-IDENTITY-FINGERPRINT` | 1 |
| `INV-JUMP-PROFILE-GATED` | 1 |
| `INV-LENS-PROFILED` | 1 |
| `INV-NO-ASSET-DEPENDENCY-FOR-EMB` | 1 |
| `INV-NO-BLOCKING-WORLDGEN-IN-UI` | 1 |
| `INV-NO-EXTENSION-INTERPRETATION-WITHOUT-REGISTRY` | 1 |
| `INV-NO-FLOAT-SMOOTHING` | 1 |
| `INV-NO-IDENTITY-OVERRIDE` | 1 |
| `INV-NO-RANDOM-RETRY-LOOPS-IN-WORLDGEN` | 1 |
| `INV-NO-SILENT-DEGRADE` | 1 |
| `INV-NO-TRUTH-LEAK-IN-SCANS` | 1 |
| `INV-OVERLAY-CONFLICT-POLICY-DECLARED` | 1 |
| `INV-REFINEMENT-BUDGETED` | 1 |
| `INV-REPOX-RULESET-MISSING` | 1 |
| `INV-REPRO-BUNDLE-DETERMINISTIC` | 1 |
| `INV-REPRO-BUNDLE-NO-SECRETS` | 1 |
| `INV-SHADOW-BOUNDED` | 1 |
| `INV-TERRAIN-EDITS-PROCESS-ONLY` | 1 |

## Warnings

- RepoX still reports 5 warnings.
- Full CTest remains outside this task.

## Product Boot Readiness

POST-CONVERGE-11 is not ready because focused RepoX still has governance failures.
