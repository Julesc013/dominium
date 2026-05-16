
# Latest Warning Disposition

Status: DERIVED
Last Reviewed: 2026-05-16
Supersedes: none
Superseded By: none

## POST-CONVERGE-10K

- Focused tuple RepoX still fails with 51 failures and 5 warnings.
- `INV-NEW-CONTRACT-REQUIRES-ENTRY` is no longer a failing family after semantic contract registry acceptance metadata was added for four current architecture contracts.
- The 10J `INV-LOCKLIST-FROZEN` local acceptance failure was absent at 10K start because `origin/main` equaled local HEAD.
- The first 10K commit has a classified AIDE commit-message policy issue in its changelog category prefixes; amend is forbidden, so the latest follow-up commit records the issue instead of rewriting history.
- Canonical `ctest --preset verify` still discovers 0 tests in this checkout.
- Full CTest, product boot proof, package proof, and portable projection proof remain not run by scope.
