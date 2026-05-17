Status: DERIVED
Last Reviewed: 2026-05-17
Supersedes: none
Superseded By: none

# MOVE-FAMILY-00C-A-PLAN Review

## Review Result

PASS_WITH_WARNINGS for gate readiness.

## Groups Planned

- `validation`
- `meta.identity`
- `meta.stability`

## Files Included

- `validation/__init__.py`
- `validation/validation_engine.py`
- `meta/identity/__init__.py`
- `meta/identity/identity_validator.py`
- `meta/stability/__init__.py`
- `meta/stability/stability_scope.py`
- `meta/stability/stability_validator.py`

## Target Namespaces

- `tools.validators.validation`
- `tools.validators.identity`
- `tools.validators.stability`

## Shim Requirements

All three groups require temporary old-path shims. Shims must be import/re-export only and must not mutate behavior.

## Import Rewrite Complexity

- 44 active Python import consumers found.
- 34 imports are planned for apply-phase rewrite.
- 10 old-import callers are temporarily allowlisted.

## Static Check Plan

A future static check must fail active old imports outside the shim files and temporary allowlist. Historical docs, AIDE evidence, and generated evidence remain warning-only.

## Validation Plan

Future apply requires Tier 0, strict validators, docs/build/UI/ABI checks, focused RepoX, py_compile, new and old import smoke checks, affected validator smoke, static stale-import scan, and smoke CTest if AppShell or active validator imports are changed.

## Readiness

Ready for `MOVE-FAMILY-00C-A-GATE`.

The plan does not authorize apply.
