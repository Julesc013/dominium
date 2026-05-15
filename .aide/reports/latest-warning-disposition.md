# Latest Warning Disposition

## Accepted Warnings

- `py -3 .aide/scripts/aide_lite.py repo validate` still reports advisory
  unknown file classifications.
- Full eval, full CTest, build, package, release generation, CMake
  configure/build, and product binaries were not run.
- The draft first move-planning candidate has high reference complexity and
  requires `AIDE-MOVE-01-PLAN` review before any application task.
- `git diff --check` reports CRLF normalization warnings only.

## Cleared Warnings

- Strict repo layout and root allowlist validators now pass by excluding
  ignored, untracked local output roots from source-root enforcement.
