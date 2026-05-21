Status: DERIVED
Last Reviewed: 2026-05-21
Task: FOUNDATION-REPAIR-DEPENDENCY-DIRECTION-01

# Validator Repairs

The dependency-direction validator already distinguished active source, docs, tests, tools, archive, release, scripts, CMake metadata, and generated/local roots sufficiently for this task.

No validator code change was required.

Validation:

```powershell
py -3 -m py_compile tools/validators/repo/check_dependency_directions.py
py -3 tools/validators/repo/check_dependency_directions.py --repo-root . --strict
```

Result: PASS, `0` violations, `68` warnings.
