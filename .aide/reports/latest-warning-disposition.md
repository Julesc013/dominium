
# Latest Warning Disposition

Status: DERIVED
Last Reviewed: 2026-05-16
Supersedes: none
Superseded By: none

## TEST-PERF-00

- Focused tuple RepoX still fails with 51 failures and 5 warnings.
- Canonical `ctest --preset verify -N` discovered 0 tests before configure refresh, then 493 tests after `cmake --preset verify`.
- CTest smoke labels now discover 57 tests after `dom_add_testx` label repair and reconfigure.
- Full CTest, product boot proof, package proof, and portable projection proof remain not run by scope.
- Full CTest remains a promotion gate rather than the normal post-change feedback path.
- The first TEST-PERF-00 commit has a classified AIDE commit-message policy issue in its changelog category prefixes; amend is avoided and the issue is recorded by a follow-up evidence commit.
