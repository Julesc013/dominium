Status: DERIVED
Last Reviewed: 2026-05-16
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: POST-CONVERGE
Replacement Target: none

# POST-CONVERGE-10F Unit Annotation and RepoX Rule Remediation

## Status

- Task ID: POST-CONVERGE-10F
- Result: PARTIAL
- Branch: `main`
- HEAD before: `28602fabe9a0759c542e7c6f202eb1df2f703a73`
- origin/main: `28602fabe9a0759c542e7c6f202eb1df2f703a73`
- Worktree before: clean
- Worktree after: scoped task changes only

## Scope

This task targeted the remaining post-native-build governance and test blockers from POST-CONVERGE-10E: `invariant_units_present`, `inv_repox_rules`, and full CTest wall-time classification.

No root moves, deletes, renames, reference rewrites, feature work, product proof, package proof, move maps, salvage maps, path aliases, or layout exception retirements were performed.

## Prior Blockers

| Blocker | Prior status | POST-CONVERGE-10F result |
| --- | --- | --- |
| `invariant_units_present` | failing on `unit.mass_energy.stub` and `unit.schema` | fixed |
| `inv_repox_rules` | failing on broad RepoX drift | still failing; classified |
| full CTest wall-time | timeout/long-running | still not clean; semantic RepoX failure remains primary |

## Focused Test Reproduction

| Test | Command | Result | First Failure | Notes |
| --- | --- | --- | --- | --- |
| canonical discovery | `ctest --preset verify -N` | pass, but 0 tests | none | `out/build/vs2026/verify` currently has no discoverable CTest tests |
| canonical unit filter | `ctest --preset verify -R invariant_units_present --output-on-failure` | pass, but no tests found | none | canonical preset discovery gap |
| canonical RepoX filter | `ctest --preset verify -R inv_repox_rules --output-on-failure` | pass, but no tests found | none | canonical preset discovery gap |
| tuple discovery | `ctest --test-dir .dominium.local/build/tuple.verify.winnt10.x64.msvc143.mt.debug -C Debug -N` | pass | none | 493 tests discovered |
| tuple unit gate before | `ctest --test-dir .dominium.local/build/tuple.verify.winnt10.x64.msvc143.mt.debug -C Debug -R invariant_units_present --output-on-failure` | fail | undeclared `unit.mass_energy.stub`; false-positive `unit.schema` | reproduced from 10E |
| tuple unit gate after | same command | pass | none | 1/1 passed |
| tuple RepoX gate after | `ctest --test-dir .dominium.local/build/tuple.verify.winnt10.x64.msvc143.mt.debug -C Debug -R inv_repox_rules --output-on-failure` | fail | broad RepoX drift | 1,844 failures and 5 warnings in local proof manifest |

## Unit Invariant Findings

| Unit/token | Source | Classification | Change |
| --- | --- | --- | --- |
| `unit.mass_energy.stub` | `contracts/schema/quantity.schema.json`, `data/registries/quantity_registry.json`, `tools/xstack/sessionx/universe_physics.py` | valid provisional unit missing from machine-readable unit registry | added to `data/registries/unit_registry.json` |
| `unit.schema` | path fragment `contracts/schema/materials/unit.schema` | stale tokenization / false-positive path fragment | `tests/contract/unit_annotation_validation.py` now ignores unit-like tokens preceded by `/` or `\` |

The unit validator now accepts declared units from the canonical policy table and the machine-readable unit registry. No fake units were added, and no invariant was weakened.

## RepoX Findings

`inv_repox_rules` still fails after the unit remediation. The current failure is not a single stale path. The local RepoX proof manifest reports:

| Category | Count |
| --- | ---: |
| `INV-DOC-STATUS-HEADER` | 1545 |
| `INV-CANON-INDEX` | 84 |
| `INV-CANON-NO-HIST-REF` | 81 |
| `INV-OFFLINE-BOOT-OK` | 22 |
| `INV-REPOX-STRUCTURE` | 22 |
| `INV-NEW-CONTRACT-REQUIRES-ENTRY` | 9 |
| `INV-ALL-PRODUCTS-EMIT-DESCRIPTOR` | 7 |

The focused RepoX CTest wrapper was updated to write generated proof/profile output under ignored `.dominium.local/ctest/repox/` instead of dirtying tracked audit outputs. This does not weaken RepoX; it preserves the same failing result while avoiding generated tracked side effects.

## CTest Wall-Time Classification

- semantic_failures_remaining: yes, due `inv_repox_rules`
- wall_time_blocker: yes, but secondary until RepoX semantic failures are remediated
- canonical CTest discovery issue: yes, `ctest --preset verify -N` currently reports 0 tests
- tuple CTest discovery: yes, 493 tests discovered
- full CTest run in this task: not run, because focused RepoX still fails and full run would not produce a clean proof
- TEST-PERF-00 recommended: yes, after RepoX semantic drift is addressed

## Files Changed

| File | Why |
| --- | --- |
| `data/registries/unit_registry.json` | Added valid missing provisional unit `unit.mass_energy.stub` |
| `tests/contract/unit_annotation_validation.py` | Reads machine-readable unit registry and avoids false-positive `unit.schema` path fragments |
| `tests/invariant/repox_rules_tests.py` | Redirects RepoX generated CTest output to ignored local state |
| `.aide/**` and docs reports | Records evidence and blocker classification |

## Validation

Validation was run through focused CTest, AIDE, strict repo/root/distribution/component validators, docs sanity, build boundary, UI shell purity, ABI checks, JSON parsing, and git diff checks.

The focused unit invariant now passes. The focused RepoX invariant remains red by design because its failures are broad governance drift, not a safe narrow 10F fix.

## Readiness Decision

- ready_for_POST_CONVERGE_11: no
- reason: product boot proof should not proceed while `inv_repox_rules` remains a real semantic governance failure and the canonical CTest preset discovery is not coherent.

Recommended next task: `POST-CONVERGE-10G - RepoX Rule and Canonical Evidence Drift Remediation`.

## POST-CONVERGE-10G Follow-Up

POST-CONVERGE-10G reduced the RepoX blocker from 1844 failures and 5 warnings to 1769 failures and 5 warnings. Safe remediation covered stale top-level root handling, retired root-level AppShell path assumptions, and RepoX group-cache invalidation. The remaining blockers are broad canonical documentation/status/index and policy evidence drift, so POST-CONVERGE-11 remains blocked.
