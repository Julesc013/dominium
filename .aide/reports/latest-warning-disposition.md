# Latest Warning Disposition

Status: DERIVED
Last Reviewed: 2026-05-16
Supersedes: none
Superseded By: none

## POST-CONVERGE-10J

- Focused RepoX still fails with 60 failures and 5 warnings.
- `INV-DOC-STATUS-HEADER` is no longer a failing family after authority-sensitive status remediation.
- `INV-LOCKLIST-FROZEN` remains as a local baseline acceptance effect because `docs/architecture/CANON_INDEX.md` changed against `origin/main`.
- Canonical `ctest --preset verify` still discovers 0 tests in this checkout.
- Full CTest and product boot proof remain not run by scope.
