Status: DERIVED
Last Reviewed: 2026-05-17
Supersedes: none
Superseded By: none

# MOVE-FAMILY-00C Active Tool Namespace Plan

## Status

- Task: `MOVE-FAMILY-00C-PLAN`
- Result: BLOCKED
- Baseline: BASELINE-00 / RELEASE-00 structural regression baseline
- Ready for `MOVE-FAMILY-00C-GATE`: false
- Apply allowed: false

## Scope

This plan inspects active Python/tooling surfaces under:

- `validation/`
- `meta/`
- `governance/`
- `performance/`

It applies no moves, deletes, renames, import rewrites, reference rewrites, shims, path aliases, move maps, salvage maps, or exception updates.

## Baseline

MOVE-FAMILY-00B retired `ide/` as tracked source and moved projection manifest source metadata to `contracts/projections/ide/**`. The remaining MOVE-FAMILY-00 work is active Python/module ownership.

## Target Roots

| Root | Tracked Python Files | Package Init Files | Active Import Files | Decision |
| --- | ---: | ---: | ---: | --- |
| `validation/` | 2 | 1 | 8 | candidate after shim contract |
| `meta/` | 26 | 11 | 104 | split validator-like subpackages; preserve semantic/runtime modules |
| `governance/` | 2 | 1 | 9 | candidate after release-control shim plan |
| `performance/` | 3 | 1 | 4 | preserve current |

## Active Modules

The target roots contain 33 tracked Python files and no direct CLI entrypoints. Ignored local `__pycache__/` directories exist under target roots but remain untracked.

## Proposed Ownership

| Current Material | Proposed Owner | Mode |
| --- | --- | --- |
| `validation/**` | `tools/validators/unified_validation/**` | move with temporary shim |
| `meta/identity/**` | `tools/validators/identity/**` | move with temporary shim |
| `meta/stability/**` | `tools/validators/stability/**` | move with temporary shim |
| `governance/**` | `tools/governance/profile/**` | move with temporary shim |
| semantic/runtime `meta/**` | preserve current | defer |
| `performance/**` | preserve current | defer |

## Batch Plan

| Batch | Scope | Gate Ready? |
| --- | --- | --- |
| 00C-A | `validation/**`, `meta/identity/**`, `meta/stability/**` | no |
| 00C-B | `governance/**` | no |
| 00C-C | `performance/**` ownership review | no |
| 00C-D | semantic/runtime `meta/**` preserve/defer review | no |

## Import/Reference Rewrite Plan

This task rewrites nothing.

Future rewrites must handle:

- `validation` consumers in runtime AppShell, compat, tools, RepoX, AuditX, and TestX;
- `meta.identity` consumers in release, security, lib validators, tools, validation, and TestX;
- `meta.stability` consumers in validation, governance, AuditX, RepoX, release, review, security, and TestX;
- `governance` consumers in release/update, setup, dist, release tools, governance tools, and TestX.

Historical/AIDE/audit/generated references must remain historical unless a future task explicitly refreshes evidence.

## Shim Plan

Temporary shims are likely required for:

- `validation`
- `meta.identity`
- `meta.stability`
- `governance`

The shim plan is not approved and no shim was created.

## Validation Plan

Future apply tasks must run Tier 0, strict validators, docs/build/UI/ABI checks, focused RepoX, affected validator commands, py_compile and import smoke for moved modules and modified consumers, stale-import scans, generated-output staging checks, and smoke CTest if active validators or AppShell import paths are touched.

## Rollback Plan

Rollback for any future apply must reverse moves, imports, references, shims, and exception changes, then rerun the same validation suite.

## Exception Update Plan

No exception can retire from this plan. Future batches may narrow `validation`, `meta`, or `governance` only after the tracked state, shim lifecycle, and validators prove the narrowing. `performance` remains preserve-current.

## Readiness For MOVE-FAMILY-00C-GATE

Not ready.

The recommended next task is:

```text
MOVE-FAMILY-00C-A-PLAN - Validation, Identity, and Stability Shim Contract Plan
```

## No Moves/Deletes/Renames Confirmation

MOVE-FAMILY-00C-PLAN made no source-root moves, deletes, renames, import rewrites, reference rewrites, active aliases, compatibility shims, move-map applications, salvage-map applications, or exception retirements.
