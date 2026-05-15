# Review Packet Repair

Status: repaired

## Root Cause

AIDE `test` and `selftest` previously failed when temporary selftest repositories were created under a path inside the Dominium working tree. Git discovery climbed from the temporary directory into the outer Dominium `.git`, so generated review-packet changed-file summaries contained out-of-repo relative paths.

## Repair

`.aide/scripts/aide_lite.py` now sets `GIT_CEILING_DIRECTORIES` inside `git_status_short()` to the parent of the requested repo root before running `git -C <repo_root> status --short`.

This constrains Git discovery to the intended repository boundary and prevents nested temporary selftest directories from inheriting the outer Dominium repository.

## Validation

- `python -m py_compile .aide/scripts/aide_lite.py`: PASS
- `aide_lite.py test`: PASS
- `aide_lite.py selftest`: PASS

## Preservation

- Product/source files modified: no
- Doctrine files modified: no
- Legacy tools modified: no
- Unknown legacy tools executed: no
