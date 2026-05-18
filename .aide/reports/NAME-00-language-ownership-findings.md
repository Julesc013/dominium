# NAME-00 Language Ownership Findings

Status: `PASS_WITH_WARNINGS`

NAME-00 records language placement law and current language-placement debt. It does not convert files, move files, rewrite imports, create shims, or change behavior.

## Final Law

- `engine/`: C89 by default; deterministic substrate only.
- `game/`: C89/C++98 unless isolated and explicitly approved.
- `runtime/`: C89/C++98 for shared runtime; isolated platform adapter language only where needed.
- `apps/`: thin product shell language only; no simulation truth.
- `contracts/`: machine-readable data only.
- `content/`: data only; no executable code.
- `tools/`: Python, shell wrappers, CMake helpers, codegen, validators, migration, build, and release tooling.
- `scripts/`: thin wrappers only.
- `archive/`: historical languages allowed, not active authority.

## Current Findings

| Scope | Finding | Disposition |
| --- | --- | --- |
| `engine/**/*.py` | 19 tracked Python files under engine | warning; existing debt |
| `game/**/*.py` | 299 tracked Python files under game | warning; existing debt |
| `runtime/**/*.py` | 37 tracked Python files under runtime | warning; existing debt |
| former bad roots | active Python remains under excepted roots such as `core/`, `control/`, `compat/`, `lib/`, `meta/`, `net/`, and `validation/` | warning; deferred to MOVE-BULK B-G gates |

## Blockers

Immediate NAME-00 blockers: none.

These findings are not accepted as final architecture. They are recorded so future language cleanup has a contract to enforce against.
