Status: DERIVED
Last Reviewed: 2026-05-22
Supersedes: none
Superseded By: none
Stability: provisional

# Package Mount Slice Development Notes

Use this slice to validate package/profile mount planning fixtures without
starting package runtime work.

## Commands

```text
python -m py_compile tools/validators/package/check_package_mount_slice.py
python tools/validators/package/check_package_mount_slice.py --repo-root . --strict
python tools/validators/package/check_package_mount_slice.py --repo-root . --json
python tools/validators/package/check_package_mount_slice.py --repo-root . --fixtures
python tools/validators/package/check_package_mount_slice.py --repo-root . --inventory
python tests/app/package_mount_slice_tests.py
```

Strict mode validates the package mount command, input/result schemas, public
surface entries, positive fixture chain, and required negative fixtures.
Inventory mode is descriptive only.

## Fixture Contract

The positive fixture chain starts at:

```text
tests/contract/package/fixtures/valid_package_mount_input.json
tests/contract/package/fixtures/valid_package_mount_result.json
```

The result references package mount plan, decision, lock, capability report,
trust report, compatibility report, and refusal report fixtures. Those artifacts
are derived evidence. They are not runtime state.

Negative fixtures cover:

- unknown package ref
- path-as-identity
- silent overlay overwrite
- missing required capability
- unsupported trust level
- lockfile marked as source truth
- degraded fallback without fallback trace

## Boundaries

Do not extend this validator into a runtime package resolver. It may inspect
fixtures, registries, and contract files. Product/runtime code must not depend
on this validator, and Workbench must not bind to its private path.
