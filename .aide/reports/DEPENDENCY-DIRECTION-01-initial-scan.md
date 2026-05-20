# DEPENDENCY-DIRECTION-01 Initial Scan

Command:

```powershell
python tools/validators/repo/check_dependency_directions.py --repo-root . --json
```

Machine-readable evidence:

```text
.aide/reports/DEPENDENCY-DIRECTION-01-initial-scan.json
```

## Summary

- status: fail
- roots scanned: 14
- tracked files considered: 17,710
- text/source files scanned: 16,104
- high-confidence violations: 358
- warnings: 38
- active exceptions: 0
- exceptions used: 0
- unused exceptions: 0

## Violation Groups

| Edge | Count |
| --- | ---: |
| `apps -> tools` import | 21 |
| `engine -> tools` import | 6 |
| `game -> tools` import | 250 |
| `runtime -> apps` import | 2 |
| `runtime -> tools` import | 79 |

## Warning Groups

| Edge | Count |
| --- | ---: |
| `apps -> content` include | 8 |
| `apps -> engine` import | 1 |
| `game -> runtime` import | 10 |
| `runtime -> game` import | 19 |

## Disposition

These findings are recorded as dependency-direction debt. They are not hidden by
broad exceptions and are not marked passing. A future repair task must either
remove each dependency, move code to the correct owner, add a proper contract or
service boundary, or add precise temporary exceptions with owner and retirement
task.
