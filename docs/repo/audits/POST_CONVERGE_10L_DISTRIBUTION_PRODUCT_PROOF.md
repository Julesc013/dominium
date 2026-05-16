Status: DERIVED
Last Reviewed: 2026-05-16
Supersedes: none
Superseded By: none

# POST-CONVERGE-10L Distribution Descriptor and Product Proof Blocker Classification

## Status

- Task ID: POST-CONVERGE-10L
- Result: PARTIAL
- Branch: `main`
- HEAD: `ac57200b86ac14253b3fb48070acf75c35514150`
- origin/main: `ac57200b86ac14253b3fb48070acf75c35514150`
- Worktree before: clean
- Worktree after: scoped evidence and status changes pending commit

## Scope

This was focused distribution/product proof blocker classification. It applied no root moves, no product proof, no portable projection proof, no package proof, no release generation, no product/runtime behavior changes, and no product ID or executable name changes.

## Prior State

POST-CONVERGE-10K reduced focused RepoX to 51 failures and 5 warnings by eliminating `INV-NEW-CONTRACT-REQUIRES-ENTRY`. The largest remaining target families were `INV-ALL-PRODUCTS-EMIT-DESCRIPTOR` with 7 failures and `INV-NO-ADHOC-MAIN` with 5 failures.

## Reproduction

| Command | Result | Failures | Warnings | Notes |
| --- | --- | ---: | ---: | --- |
| `ctest --preset verify -N` | PASS | 0 | 0 | Canonical verify discovery reports 493 tests. |
| `ctest --preset verify -R inv_repox_rules --output-on-failure` before | FAIL_EXPECTED | 52 | 5 | Included transient 10K audit status-header failure. |
| `ctest --preset verify -R inv_repox_rules --output-on-failure` after | FAIL_EXPECTED | 51 | 5 | Header fixed; distribution/product family remains real missing proof/projection surface. |

## Distribution/Product Findings

Checked target failures: 12.

| Rule | Count | Classification | Disposition |
| --- | ---: | --- | --- |
| `INV-ALL-PRODUCTS-EMIT-DESCRIPTOR` | 7 | `portable_projection_proof_missing` | Defer to POST-CONVERGE-12 or targeted dist wrapper proof. |
| `INV-NO-ADHOC-MAIN` | 5 | `portable_projection_proof_missing` | Defer to POST-CONVERGE-12 or targeted dist wrapper proof. |

The implicated paths are:

- `dist/bin/client`
- `dist/bin/engine`
- `dist/bin/game`
- `dist/bin/launcher`
- `dist/bin/server`
- `dist/bin/setup`
- `dist/bin/tool_attach_console_stub`

The authority basis is `data/registries/product_registry.json`, `docs/compat/ENDPOINT_DESCRIPTORS.md`, `scripts/ci/check_repox_rules.py`, and the existing partial product proof in `docs/release/PRODUCT_BOOT_PROOF.md`.

## Changes Made

- Added DERIVED status metadata to `docs/repo/audits/POST_CONVERGE_10K_CONTRACT_REGISTRY_ACCEPTANCE.md`.
- Added POST-CONVERGE-10L audit and AIDE evidence.
- Updated post-converge status docs to reflect that distribution/product proof failures are classified but not fixed.

No `dist/bin` wrapper, native binary, package, portable projection, or release artifact was created.

## Before/After

| Metric | Before | After |
| --- | ---: | ---: |
| Focused RepoX failures from 10K baseline | 51 | 51 |
| Focused RepoX warnings | 5 | 5 |
| Initial 10L reproduction failures | 52 | 51 |
| `INV-DOC-STATUS-HEADER` transient 10K audit failure | 1 | 0 |
| Distribution/product failures | 12 | 12 |

## Remaining Blockers

- Missing `dist/bin` wrapper/projection surfaces for descriptor emission and AppShell-owned delegation.
- Retired-domain path policy checks.
- Tool hash/audit staleness.
- Ruleset mapping gaps.
- Miscellaneous RepoX governance failures outside product proof scope.
- Full CTest remains a promotion gate and was not run.

## POST-CONVERGE-11 Readiness

POST-CONVERGE-11 is not ready yet. Product proof failures alone should not circularly block the product proof task, but the focused RepoX set still includes real non-proof governance failures. The next task should target retired-domain path policy and tool hash drift before product boot proof proceeds.

## Validation

- `ctest --preset verify -N`: PASS, 493 tests discovered.
- `ctest --preset verify -R inv_repox_rules --output-on-failure`: FAIL_EXPECTED, 51 failures / 5 warnings after the safe header fix.
- AIDE doctor/validate/test/selftest/tools/roots/repo validation: PASS.
- Strict repo/root/distribution/component validators: PASS.
- Docs/build/UI/ABI supplemental checks: PASS.
- JSON reports and JSONL ledger parse: PASS.
- Full CTest, build, product boot proof, portable projection proof, package proof, and release proof: NOT RUN by scope.
- Final command details are recorded in `.aide/reports/POST-CONVERGE-10L-validation.md`.
