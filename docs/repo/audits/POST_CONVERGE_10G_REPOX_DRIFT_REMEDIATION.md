Status: DERIVED
Last Reviewed: 2026-05-16
Supersedes: none
Superseded By: none

# POST-CONVERGE-10G RepoX Rule and Canonical Evidence Drift Remediation

Status: PARTIAL

## Status

- Task ID: POST-CONVERGE-10G
- Result: PARTIAL
- Branch: main
- HEAD: `ae0ded5997b8c496ea992166913e8857ca9a8372`
- origin/main: `ae0ded5997b8c496ea992166913e8857ca9a8372`
- Worktree before: clean at task start
- Worktree after: scoped 10G report/rule edits before commit

## Scope

This task performed focused RepoX remediation only. It did not move roots, delete files, rename files, apply move maps, apply salvage maps, run product boot proof, run package proof, or implement features.

## Prior State

POST-CONVERGE-10F fixed `invariant_units_present` and left focused tuple `inv_repox_rules` failing with 1844 failures and 5 warnings. The failure was classified as broad RepoX/canonical-evidence drift.

## Reproduction

| Command | Result | Failures | Warnings | Notes |
| --- | --- | ---: | ---: | --- |
| `ctest --preset verify -N` | pass with warning | n/a | n/a | Canonical verify discovery reports 0 tests. |
| `ctest --preset verify -R inv_repox_rules --output-on-failure` | pass with warning | n/a | n/a | No tests found in canonical verify discovery. |
| `python scripts/ci/check_repox_rules.py --repo-root . --proof-manifest-out .dominium.local/ctest/repox/proof_manifest.json --profile-out .dominium.local/ctest/repox/REPOX_PROFILE.json` | fail expected | 1769 | 5 | Direct RepoX after safe fixes. |
| `ctest --test-dir .dominium.local/build/tuple.verify.winnt10.x64.msvc143.mt.debug -C Debug -R inv_repox_rules --output-on-failure` | fail expected | 1769 | 5 | Focused tuple CTest after safe fixes. |

## Failure Families

| Family | Classification | Before | After | Safe now? | Action | Notes |
| --- | --- | ---: | ---: | --- | --- | --- |
| `safe_stale_root_and_appshell_paths` | stale_path | 75 | 0 | true | fix_now | RepoX now uses runtime/appshell for AppShell source checks and consumes the current root allowlist plus active layout exceptions for top-level structure checks. |
| `repox_rule_cache_dependency` | stale_canonical_evidence | 0 | 0 | true | fix_now | The rule implementation path is now included in every group cache dependency hash. |
| `doc_status_header_backlog` | stale_canonical_evidence | 1545 | 1545 | false | defer | Classified as broad documentation status migration, not safe to mass-edit under 10G. |
| `canon_index_backlog` | missing_canonical_acceptance | 84 | 84 | false | needs_generator | Classified as canonical-index migration work requiring a source-of-truth review or generator path. |
| `historical_reference_backlog` | duplicate_cascade | 81 | 81 | false | defer | Preserved as historical/generated-reference debt pending a quarantine/archive policy task. |
| `contract_registry_acceptance_backlog` | missing_canonical_acceptance | 9 | 9 | false | document_blocker | Deferred because adding semantic contract entries is authority-sensitive. |
| `distribution_descriptor_backlog` | real_policy_violation | 12 | 12 | false | document_blocker | Kept blocking; product/distribution proof is outside 10G. |
| `retired_domain_path_backlog` | stale_path | None | 23 | false | defer | Classified but not remapped broadly; requires domain-owner path review. |
| `tool_hash_and_audit_staleness` | stale_canonical_evidence | None | 3 | false | needs_generator | Deferred until a tool-version/audit-output refresh task can identify the canonical generator and acceptance rule. |
| `other_policy_backlog` | real_policy_violation | None | 31 | false | document_blocker | Kept blocking until a narrower owner-specific remediation task can prove each rule family. |

## Changes Made

- `scripts/ci/check_repox_rules.py` now reads the root allowlist and active layout exceptions for top-level structure checks instead of depending only on the legacy prose intent doc.
- RepoX top-level scanning ignores generated/local roots that are not source authority.
- AppShell checks now use `runtime/shell/` instead of the retired root-level `appshell/` path.
- RepoX group cache dependency hashes now include `scripts/ci/check_repox_rules.py` so rule implementation edits invalidate stale cached group results.

## Before/After

| Metric | Before | After |
| --- | ---: | ---: |
| RepoX failures | 1844 | 1769 |
| RepoX warnings | 5 | 5 |
| RepoX cache hits in direct rerun | n/a | 16 |
| RepoX cache misses in direct rerun | n/a | 0 |

## Remaining Blockers

The dominant remaining blockers are `INV-DOC-STATUS-HEADER`, `INV-CANON-INDEX`, `INV-CANON-NO-HIST-REF`, contract acceptance, distribution descriptor proof, and retired-domain runtime policy checks. These were not safe to mass-edit in 10G because they require canonical documentation policy, contract registry acceptance, distribution proof, or domain-owner review.

## Product Boot Readiness

POST-CONVERGE-11 is not ready. Focused RepoX still has semantic failures, so product boot proof must wait.

## Validation

| Command | Result | Notes |
| --- | --- | --- |
| `git status --short --branch` | pass | Initial state clean; final state dirty only from scoped 10G edits before commit. |
| `git fetch --all --prune` | pass | origin/main matched local HEAD at task start. |
| `git merge-base ancestry checks` | pass | HEAD and origin/main were equal at ae0ded5997b8c496ea992166913e8857ca9a8372. |
| `ctest --preset verify -N` | pass_with_warning | Canonical verify preset discovers 0 tests. |
| `ctest --preset verify -R inv_repox_rules --output-on-failure` | pass_with_warning | No matching tests in canonical verify discovery; exit 0 with no tests found. |
| `python scripts/ci/check_repox_rules.py --repo-root . --proof-manifest-out .dominium.local/ctest/repox/proof_manifest.json --profile-out .dominium.local/ctest/repox/REPOX_PROFILE.json` | fail_expected | RepoX reduced from 1844 failures to 1769; warnings remain 5. |
| `ctest --test-dir .dominium.local/build/tuple.verify.winnt10.x64.msvc143.mt.debug -C Debug -R inv_repox_rules --output-on-failure` | fail_expected | Focused tuple CTest still fails with 1769 RepoX failures and 5 warnings. |
| `python -m py_compile scripts/ci/check_repox_rules.py` | pass | RepoX rule implementation compiles. |

Final AIDE, strict validator, supplemental validator, JSON parse, and git diff checks are recorded in `.aide/reports/POST-CONVERGE-10G-validation.md` after final validation.

## POST-CONVERGE-10H Follow-Up

POST-CONVERGE-10H reduced the RepoX blocker from 1769 failures and 5 warnings to 153 failures and 5 warnings. It cleared the `INV-CANON-INDEX` family and reduced `INV-DOC-STATUS-HEADER` from 1545 to 12 by applying metadata-only DERIVED headers to evidence/reference docs. POST-CONVERGE-11 remains blocked.
