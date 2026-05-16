# POST-CONVERGE-11 Product Boot Results

Status: DERIVED
Last Reviewed: 2026-05-17

## Overall

BLOCKED.

No product binaries were inspected or executed because the RepoX readiness gate failed.

## RepoX Gate

- Focused `inv_repox_rules`: FAIL_EXPECTED
- Failures: 20
- Warnings: 5
- Accepted-warning ledger: none

## Products

| Product | Status | Commands Run | Blocker |
| --- | --- | ---: | --- |
| setup | BLOCKED | 0 | RepoX semantic blocker |
| launcher | BLOCKED | 0 | RepoX semantic blocker |
| client | BLOCKED | 0 | RepoX semantic blocker |
| server | BLOCKED | 0 | RepoX semantic blocker |
| tools | BLOCKED | 0 | RepoX semantic blocker |

## POST-CONVERGE-12 Readiness

No. Portable projection proof cannot proceed because product boot proof did not run.
