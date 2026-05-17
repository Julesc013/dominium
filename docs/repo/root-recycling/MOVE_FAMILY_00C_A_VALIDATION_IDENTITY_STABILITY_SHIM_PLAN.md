Status: DERIVED
Last Reviewed: 2026-05-17
Supersedes: none
Superseded By: none

# MOVE-FAMILY-00C-A Validation, Identity, and Stability Shim Plan

## Status

- Task: `MOVE-FAMILY-00C-A-PLAN`
- Result: PASS_WITH_WARNINGS
- Baseline: BASELINE-00 / RELEASE-00 structural regression baseline
- Apply allowed: false
- Approval status: not_approved
- Ready for `MOVE-FAMILY-00C-A-GATE`: true

## Scope

This plan covers only:

- `validation/`
- `meta/identity/`
- `meta/stability/`

It excludes `governance/`, `performance/`, and broader semantic/runtime `meta/**`.

## Baseline

MOVE-FAMILY-00C-PLAN found that active root packages cannot move directly because current import paths are used by runtime, release/control-plane, compatibility, tools, RepoX, AuditX, TestX, and validators. This plan defines the shim and staged import migration contract needed before apply.

## Package Inventory

| Package | Files | Target Namespace | Shim Required |
| --- | ---: | --- | --- |
| `validation` | 2 | `tools.validators.validation` | yes |
| `meta.identity` | 2 | `tools.validators.identity` | yes |
| `meta.stability` | 3 | `tools.validators.stability` | yes |

## Import Consumers

| Group | Consumers | Apply Rewrites | Temporary Old-Import Callers |
| --- | ---: | ---: | ---: |
| `validation` | 8 | 6 | 2 |
| `meta.identity` | 20 | 14 | 6 |
| `meta.stability` | 16 | 14 | 2 |

## Target Namespaces

Active Python implementation code should move to `tools/validators/**`. It should not move to `contracts/**`, because contracts own machine-readable authority and policy, not active validator implementation.

Planned targets:

- `validation/**` -> `tools/validators/validation/**`
- `meta/identity/**` -> `tools/validators/identity/**`
- `meta/stability/**` -> `tools/validators/stability/**`

## Shim Contract

Temporary old-path shims are planned for:

- `validation`
- `meta.identity`
- `meta.stability`

Shim rules:

- import/re-export only;
- no file writes;
- no subprocess calls;
- no environment mutation;
- no runtime warning emission;
- no new semantics;
- no behavior mutation;
- explicit static check against new old-import use.

## Import Rewrite Plan

The future apply should rewrite active tool/test/validator imports to the new namespaces. Runtime, compatibility, release/security/lib, and deferred governance callers stay on the temporary old-import allowlist until owner-specific rewrites or wrappers exist.

## Static Check Plan

A future check should fail active old imports outside:

- shim files;
- the explicit temporary old-import allowlist;
- historical/audit/AIDE/generated evidence paths.

The check should scan AST imports for `validation`, `meta.identity`, and `meta.stability`.

## Validation Plan

Future apply must run:

- AIDE doctor/validate/test/selftest/tools/roots/repo validate;
- strict repo/root/distribution/component validators;
- docs sanity;
- build target boundaries;
- UI shell purity;
- ABI boundaries;
- focused RepoX;
- py_compile for moved modules and shim files;
- old and new import smoke checks;
- affected validator smoke checks;
- legacy-import static check;
- smoke CTest if active validator or AppShell import paths are changed.

## Rollback Plan

Rollback must reverse moves, reverse import rewrites, remove shims, restore any exception state changed by apply, and rerun the same validation set.

## Exception Update Plan

No root exception can retire after the first shim apply:

- `validation/` remains as a temporary shim root.
- `meta/` remains because broader semantic/runtime material remains.
- `meta/identity/` and `meta/stability/` may narrow to shim-only subtrees after apply.

## Readiness For Gate

Ready for:

```text
MOVE-FAMILY-00C-A-GATE - Validation, Identity, and Stability Shim Migration Gate
```

The gate may review this plan, but no apply is authorized by this document.

## No Moves/Deletes/Renames Confirmation

MOVE-FAMILY-00C-A-PLAN made no source-root moves, deletes, renames, import rewrites, reference rewrites, shims, path aliases, move-map applications, salvage-map applications, or exception retirements.
