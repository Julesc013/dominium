Status: DERIVED
Last Reviewed: 2026-05-17
Supersedes: none
Superseded By: none

# MOVE-FAMILY-00C-PLAN Active Tool Boundaries

## Active Modules Found

| Root | Tracked Python Files | Package Init Files | Direct CLI Entrypoints | Decision |
| --- | ---: | ---: | ---: | --- |
| `validation/` | 2 | 1 | 0 | candidate only after shim contract |
| `meta/` | 26 | 11 | 0 | split identity/stability; preserve semantic/runtime modules |
| `governance/` | 2 | 1 | 0 | candidate only after release-control shim plan |
| `performance/` | 3 | 1 | 0 | preserve current |

## Proposed Owners

| Current Material | Proposed Owner | Migration Mode | Gate Ready? |
| --- | --- | --- | --- |
| `validation/**` | `tools/validators/unified_validation/**` | move with temporary shim | no |
| `meta/identity/**` | `tools/validators/identity/**` | move with temporary shim | no |
| `meta/stability/**` | `tools/validators/stability/**` | move with temporary shim | no |
| `governance/**` | `tools/governance/profile/**` | move with temporary shim | no |
| semantic/runtime `meta/**` | preserve current | preserve until wrapper/owner split | no |
| `performance/**` | preserve current | preserve until runtime/product ownership plan | no |

## Key Boundary Decisions

- `validation/**` is not purely tooling because runtime AppShell imports it.
- `meta/identity/**` is not merely a validator because release/security identity semantics depend on it.
- `meta/stability/**` is validator-like but is used by RepoX, AuditX, governance, release, security, and validation.
- `governance/**` has a natural neighbor in `tools/governance/**`, but release/update and setup imports make it a release-control migration.
- `performance/**` should not move to `tools/performance/**` in this wave because current consumers are product/client and game code.

## Result

The plan is blocked from direct gate review. It defines future batches, but no batch is apply-ready.
