# DEPENDENCY-DIRECTION-01 Status

Status: PARTIAL

## Repo State

- branch: `main`
- starting HEAD: `5ee3d5b92e56ed16dd3c205fb453245851a054cb`
- origin/main at start: `ed7427c96b9857ab5b93b0fab127a16d436d83ae`
- local state at start: clean, local `main` ahead of `origin/main` by the README commit
- full CTest: not run; remains T4 full/release proof

## Created Surfaces

- `contracts/repo/dependency_directions.contract.toml`
- `contracts/repo/dependency_direction.schema.json`
- `contracts/repo/dependency_direction_exceptions.toml`
- `tools/validators/repo/check_dependency_directions.py`
- `docs/architecture/dependency_direction_law.md`
- `docs/development/dependency_direction_guidelines.md`
- `tests/contract/dependency_direction/**`
- `.aide/reports/DEPENDENCY-DIRECTION-01-*`
- `docs/repo/audits/DEPENDENCY_DIRECTION_01.md`

## Initial Scan

- roots scanned: 14
- files scanned: 16,104
- violations: 358
- warnings: 38
- active exceptions: 0
- broad exceptions added: 0

Violation groups:

- `game -> tools` imports: 250
- `runtime -> tools` imports: 79
- `apps -> tools` imports: 21
- `engine -> tools` imports: 6
- `runtime -> apps` imports: 2

Warning groups:

- `runtime -> game` imports: 19
- `game -> runtime` imports: 10
- `apps -> content` includes: 8
- `apps -> engine` imports: 1

## Result

The law and validator are implemented and surrounding governance proof passes,
but the dependency graph is not clean. The task is PARTIAL because strict
dependency-direction validation exposes real existing debt and no broad exception
was added to hide it.

Next task: `COMMAND-SURFACE-01`.
