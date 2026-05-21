Status: DERIVED
Last Reviewed: 2026-05-21
Task: FOUNDATION-REPAIR-DEPENDENCY-DIRECTION-01

# Input Summary

Current HEAD at repair continuation start: `b79ff549d2f64663d3d141e93abab9cb9c439522`.

`origin/main` after fetch: `b79ff549d2f64663d3d141e93abab9cb9c439522`.

Closeout blocker from `FOUNDATION-CLOSEOUT-01`: dependency-direction strict reported `358` violations and `38` warnings.

Expected validator command:

```powershell
py -3 tools/validators/repo/check_dependency_directions.py --repo-root . --strict
```

Foundation Lock state entering this task: blocked by dependency direction. Workbench validation slice and broad feature work remained unauthorized.

Known warning classes:

- `exception_applied`: narrow provisional transitional runtime/app adapter exceptions.
- `unlisted_active_dependency`: non-failing dependency review warnings that require later boundary promotion or extraction.
- ABI stable-promotion warnings remain unrelated full promotion debt.
- Full CTest remains T4/full-gate debt and was not required for this repair.
