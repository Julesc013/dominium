# Tool Classification

Status: needs_review

## Summary

- Tool candidates classified: 2,995.
- Unknown candidates: 854.
- High-risk candidates: 171.
- Every Dominium-specific classification has `execution_allowed: false` and `apply_allowed: false`.

## Fate Counts

- `wrap`: 2,140.
- `unknown`: 854.
- `keep`: 1.

## Capability Counts

- `audit`: 1,040
- `build`: 225
- `context`: 204
- `docs`: 465
- `format`: 42
- `generate`: 126
- `install`: 170
- `lint`: 3
- `migrate`: 6
- `package`: 206
- `release`: 158
- `repo_policy`: 251
- `security`: 18
- `test`: 234
- `unknown`: 854
- `validate`: 206

## Risk Summary

- Most candidates are low/medium or unknown.
- High-risk candidates include release-sensitive, security-sensitive, destructive-candidate, build-sensitive, and authority-sensitive tool surfaces.
- Unknown classifications are preservation/manual-review cases, not deletion candidates.

## Owner / Status Summary

The current AIDE inventory records many owners as unknown. Q51 treats unknown ownership as a reason to preserve and review later, not a reason to delete or execute.

## High-Risk Areas

- Release/package surfaces.
- Repo policy and security checks.
- Build/native CMake wrappers.
- Doctrine-adjacent docs/audit tooling.
- Any command that might clean, build, package, publish, migrate, or rewrite repository state.

## No-Delete / No-Rename Statement

No tool is approved for deletion, rename, move, migration, or retirement by Q51. `drop_candidate` semantics, if produced by future classifiers, would still require a separate reviewed evidence phase before any file operation.
