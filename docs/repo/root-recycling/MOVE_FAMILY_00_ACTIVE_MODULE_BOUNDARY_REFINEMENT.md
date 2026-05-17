Status: DERIVED
Last Reviewed: 2026-05-17
Supersedes: none
Superseded By: none
Plan Status: DRAFT
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

## MOVE-FAMILY-00B Plan Follow-up

`MOVE-FAMILY-00B-PLAN` completed the IDE manifest contract/projection planning step.

- Planned moves: 3 tracked manifest source files.
- Target owner: `contracts/projections/ide/**`.
- Ready for `MOVE-FAMILY-00B-GATE`: true.
- Apply allowed: false.
- Generated `ide/manifests/*.projection.json` output may remain under `ide/` as ignored generated output.
- The `ide` source-layout exception may retire only after an approved apply moves all tracked files and `git ls-files ide` is empty.

## MOVE-FAMILY-00B Apply Follow-up

`MOVE-FAMILY-00B-APPLY` moved the three tracked IDE manifest source files to `contracts/projections/ide/**` and retired the `ide` source-layout exception after `git ls-files ide` became empty.

The remaining active-module ownership work is unchanged:

- `validation/**`, `meta/identity/**`, and `meta/stability/**` still need shim-aware validator namespace planning.
- `governance/**` still needs release/tool import proof before relocation.
- semantic/runtime `meta/**` and product/runtime `performance/**` remain preserve-current.

## MOVE-FAMILY-00B Proof Follow-up

`MOVE-FAMILY-00B-PROOF` proved the `ide/` root retirement state:

- tracked `ide/` files: none;
- filesystem `ide/` path: absent;
- retired `ide_root` exception: accepted by strict validators;
- active stale references to old tracked schema/example paths: none.

The next family-00 task should now focus on active tooling/module ownership rather than IDE manifests:

```text
MOVE-FAMILY-00C-PLAN - Active Validation/Meta/Governance Tool Namespace Plan
```

## MOVE-FAMILY-00C Plan Follow-up

`MOVE-FAMILY-00C-PLAN` inspected the remaining active Python/tooling roots after `ide/` retirement.

- Tracked Python files inspected: 33.
- Direct CLI entrypoints under target roots: 0.
- Candidate validator/governance files: 9, but none are gate-ready.
- `validation/**`, `meta/identity/**`, `meta/stability/**`, and `governance/**` require temporary shim policy and consumer proof before any apply.
- semantic/runtime `meta/**` and product/runtime `performance/**` remain preserve-current.
- Recommended next task: `MOVE-FAMILY-00C-A-PLAN - Validation, Identity, and Stability Shim Contract Plan`.
