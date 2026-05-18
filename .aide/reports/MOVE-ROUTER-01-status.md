Status: PASS_WITH_WARNINGS
Last Reviewed: 2026-05-18
Task: MOVE-ROUTER-01

# MOVE-ROUTER-01 Status

MOVE-ROUTER-01 applied the deterministic route table from MOVE-ROUTER-00 with
`git mv`. It did not edit moved file contents.

## Apply Summary

| Metric | Count |
| --- | ---: |
| Bad-root tracked files before | 1,765 |
| Bad-root tracked files after | 0 |
| Files moved | 1,765 |
| Semantic moves | 1,694 |
| Quarantine moves | 71 |
| Skipped moves | 0 |
| Target collisions | 0 |
| Roots emptied | 24 |
| Active root exceptions retired | 23 |
| Already-retired root exceptions confirmed | 1 |

## Validation Summary

- AIDE doctor/validate/test/selftest/tools/roots/repo passed; `validate` retained
  only the existing review-packet warning.
- Strict repo layout, root allowlist, distribution layout, and component matrix
  validators passed after exception retirement was recorded under the existing
  `retired_exceptions` ledger style.
- Bad-root absence validator passed with `tracked_bad_root_file_count = 0`.
- Docs sanity, build boundary, UI shell purity, ABI boundary, and `git diff
  --check` passed.

## Scope Guard

- No tracked files were deleted.
- No file contents were intentionally changed by the move pass.
- Only untracked `__pycache__/*.pyc` leftovers under empty former roots were
  cleaned so strict root-presence validators could see the final structure.
- No import, reference, CMake, build, product, projection, or release repair was
  performed.
- No feature work was performed.

## Next

`MOVE-ROUTER-02 - Repair References, Imports, Build, Projection, and Exceptions After Routing`.
