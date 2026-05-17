# MOVE-FAMILY-00-REFINE Active Module Boundaries

Status: DERIVED
Last Reviewed: 2026-05-17

## Summary

The target Python roots contain active importable packages/modules, not passive cleanup material.

| Root | Files | Boundary Result | Target Owner |
| --- | ---: | --- | --- |
| `governance/` | 2 | release/tool helper package | `tools/repo` via `tools/governance/**`, with temporary shim/import plan |
| `meta/identity/**` | 2 | identity validator/helper surface | `tools/validators`, with temporary shim/import plan |
| `meta/stability/**` | 3 | registry stability validator surface | `tools/validators`, with temporary shim/import plan |
| `validation/**` | 2 | unified validation engine | `tools/validators`, with temporary shim/import plan |
| other `meta/**` | 21 | semantic/runtime/domain helper modules | preserve current until semantic owner split |
| `performance/**` | 3 | product/client/game runtime helpers | preserve current; do not force into `tools/performance` |

## Direct Import Evidence

- `governance`: 9 direct Python import references.
- `meta`: 123 direct Python import references.
- `performance`: 7 direct Python import references.
- `validation`: 9 direct Python import references.

Decision-bearing examples:

- `release/update_resolver.py` imports `governance` and `meta.identity`.
- `runtime/appshell/commands/command_engine.py` imports `validation`.
- `runtime/appshell/logging/log_engine.py` imports `meta.observability`.
- `apps/client/interaction/preview_generator.py` imports `performance.cost_engine` and `performance.inspection_cache`.
- `engine/time/time_mapping_engine.py` and game physics modules import `meta.numeric`.
- RepoX/AuditX/TestX surfaces import `validation`, `meta.stability`, `meta.identity`, and many semantic `meta` subpackages.

## Migration Modes

| Group | Migration Mode | Why |
| --- | --- | --- |
| `governance/**` | move_with_temporary_shim | Release/setup/dist/tools import the root package directly. |
| `meta/identity/**` | move_with_temporary_shim | Identity helpers are used by release, security, tools, and validation. |
| `meta/stability/**` | move_with_temporary_shim | Registry validators are used by validation, AuditX, RepoX, TestX, and repo tooling. |
| `validation/**` | move_with_temporary_shim | Runtime AppShell and many tools import `validation` directly. |
| semantic `meta/**` | preserve_until_tool_wrapping | These are active domain/runtime semantic helpers, not tool-only modules. |
| `performance/**` | block_unknown | Current consumers are product/client/game runtime paths; a tools destination is not correct yet. |

## Blockers

- No active Python group is apply-ready.
- Temporary shim policy is needed before moving validator-like roots.
- Runtime/product consumers block `performance/**` relocation.
- `meta/**` must be split by semantic owner rather than moved as one family.
