Status: DRAFT
Last Reviewed: 2026-05-17
Approval Status: not_approved
Apply Allowed: false

# MOVE-FAMILY-00 Active Module Boundary Refinement

## Status

- Task: `MOVE-FAMILY-00-REFINE-ACTIVE-MODULE-BOUNDARIES`
- Result: `PASS_WITH_WARNINGS`
- Baseline: `BASELINE-00`
- Prior plan: `MOVE-FAMILY-00-PLAN`
- Ready for `MOVE-FAMILY-00-GATE`: false

## Scope

This refinement inspects the remaining material under:

- `governance/`
- `meta/`
- `performance/`
- `validation/`
- `ide/`

It creates ownership maps and a revised cleanup strategy only. It does not move, delete, rename, rewrite imports, rewrite references, create shims, apply maps, or retire exceptions.

## Why MOVE-FAMILY-00 Was Blocked

MOVE-FAMILY-00-PLAN found no safe family-level apply set because `ide/README.md` had already moved and the remaining files were not passive docs. The remaining root-family material is active Python import surface or machine-readable projection metadata.

## Active Module Findings

The refinement found 33 tracked Python files:

- 14 package/export files with `__init__.py` semantics.
- 4 validator implementation files.
- 0 direct executable tool entrypoints in the target roots.
- many active imports from release, runtime, product/client, game domains, tools, AuditX, RepoX, TestX, and tests.

The direct import scan found:

- `governance`: 9 direct Python imports.
- `meta`: 123 direct Python imports.
- `performance`: 7 direct Python imports.
- `validation`: 9 direct Python imports.

## IDE Manifest Findings

The remaining `ide/` files are three machine-readable projection manifest files:

- `ide/manifests/projection_manifest.schema.json`
- `ide/manifests/projection_manifest_examples/example_linux_clang_modern_client_gui.projection.json`
- `ide/manifests/projection_manifest_examples/example_win_vc6_win9x_client_gui.projection.json`

They are source metadata, not generated evidence. Their preferred future owner is `contracts/projections`.

## Ownership Destinations

| Material | Target Owner | Migration Mode |
| --- | --- | --- |
| `ide/manifests/**` | `contracts/projections` | preserve_until_manifest_contract |
| `validation/**` | `tools/validators` | move_with_temporary_shim |
| `meta/identity/**` | `tools/validators` | move_with_temporary_shim |
| `meta/stability/**` | `tools/validators` | move_with_temporary_shim |
| `governance/**` | `tools/repo` via `tools/governance/**` | move_with_temporary_shim |
| semantic/runtime `meta/**` | preserve_current | preserve_until_tool_wrapping |
| `performance/**` | preserve_current | block_unknown |

## Recommended Next Task

```text
MOVE-FAMILY-00B-PLAN - IDE Manifest Contract/Projection Ownership Plan
```

This is the smallest refined group and has the clearest target owner. It should define the projection contract path, validator, reference rewrite list, rollback plan, and exception update conditions for `ide/manifests/**`.

## No Moves/Deletes/Renames Confirmation

This refinement made no source-root moves, deletes, renames, import rewrites, reference rewrites, active aliases, compatibility shims, move-map applications, salvage-map applications, or exception retirements.
