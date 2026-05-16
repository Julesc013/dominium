# AIDE Latest Task Packet

## PHASE

POST-CONVERGE-10L - Distribution Descriptor and Product Proof Blocker Classification

## GOAL

Classify remaining focused RepoX distribution/product proof failures without fabricating product boot proof, portable projection proof, package output, release output, or distribution wrapper artifacts.

## WHY

RepoX now distinguishes documentation and contract registry drift from proof-dependent distribution surfaces. Missing product/projection proof must not be treated as source readiness, but it also must not circularly block the tasks meant to produce that proof.

## CURRENT RESULT

PARTIAL. Focused `inv_repox_rules` remains 51 failures / 5 warnings after a safe audit status-header fix. The 12 target distribution/product failures are classified as missing distribution wrapper/projection proof. POST-CONVERGE-11 remains blocked by non-proof RepoX failures.

## CONTEXT_REFS

- `docs/repo/audits/POST_CONVERGE_10L_DISTRIBUTION_PRODUCT_PROOF.md`
- `.aide/reports/POST-CONVERGE-10L-distribution-product-findings.json`
- `.aide/reports/POST-CONVERGE-10L-repox-before-after.json`
- `.aide/reports/POST-CONVERGE-10L-post-converge-11-readiness.md`
- `data/registries/product_registry.json`
- `docs/compat/ENDPOINT_DESCRIPTORS.md`
- `docs/release/PRODUCT_BOOT_PROOF.md`

## IMPLEMENTATION

POST-CONVERGE-10L adds evidence reports and status notes, fixes only the transient missing status header on the 10K audit report, and preserves all missing `dist/bin` wrapper surfaces as blockers.

## EVIDENCE

- `ctest --preset verify -N` reports 493 tests.
- Focused `ctest --preset verify -R inv_repox_rules --output-on-failure` reports 51 failures / 5 warnings after the metadata fix.
- Product registry declares the missing distribution wrapper names.
- Product boot proof remains partial and does not prove the missing projection wrappers.

## NON_GOALS

- no product boot proof
- no portable projection proof
- no package or release generation
- no dummy wrapper files
- no product ID, executable name, install root, pack/profile/bundle ID, semantic contract ID, or distribution contract change
- no RepoX weakening

## ACCEPTANCE

- distribution/product failures are classified by rule and path
- no proof is fabricated
- focused RepoX before/after counts are recorded
- POST-CONVERGE-11 readiness is explicit
- next family is recommended

## OUTPUT_SCHEMA

Human-readable reports plus JSON evidence:

- `.aide/reports/POST-CONVERGE-10L-distribution-product-findings.json`
- `.aide/reports/POST-CONVERGE-10L-repox-before-after.json`

## TOKEN_ESTIMATE

Latest packet is intended to stay below the AIDE compact-context budget.

## ALLOWED_PATHS

- AIDE reports/context/ledger
- post-converge and release status docs
- direct audit evidence
- narrow descriptor/proof metadata only where authority is clear

## FORBIDDEN_PATHS

- generated product/projection/package/release artifacts
- product/runtime/source behavior
- root moves, deletes, renames, aliases, or move maps
- RepoX/AuditX/TestX weakening

## VALIDATION

Focused RepoX was rerun after the safe header fix and remains an expected failure at 51 failures / 5 warnings. Final command details are recorded in `.aide/reports/POST-CONVERGE-10L-validation.md`.

## NEXT

Recommended semantic task: `POST-CONVERGE-10M - Retired-Domain Path Policy and Tool Hash Drift Remediation`.
