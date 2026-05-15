# AIDE Wrapper Commands

## Status

- Phase: AIDE-STRUCTURE-02
- Status: provisional

## Purpose

AIDE wrapper commands provide stable command names for Dominium validation
work. The wrapper surface is allowed to mature while existing tool paths and
legacy names remain preserved behind it.

## Why Wrap Before Rename

Dominium already has useful checks, but some names and paths are transitional.
Wrappers decouple future AIDE command names from current tool locations. No
legacy validator should be deleted, renamed, or moved until an adapter proves
the same behavior and downstream references have evidence-backed migration
plans.

## Command Contract Model

Command contracts live under `.aide/tools/command-contracts/`. The registry at
`.aide/tools/command-registry.toml` points stable command names at those
contracts. The runner in `tools/aide/run_task.py` loads the registry, describes
commands, performs dry-runs, and executes only commands whose contracts allow
execution.

## Current Commands

| AIDE command | Underlying tool | Execution status | Side effects | Notes |
| --- | --- | --- | --- | --- |
| `aide.tools` | `py -3 .aide/scripts/aide_lite.py tools validate` | enabled | no apply, no network, no writes | Validates AIDE tool evidence without executing unknown legacy tools. |
| `aide.roots` | `py -3 .aide/scripts/aide_lite.py roots validate` | enabled | no apply, no network, no writes | Validates AIDE root evidence in no-apply mode. |
| `aide.repo` | `py -3 .aide/scripts/aide_lite.py repo validate` | enabled | no apply, no network, no writes | May report known unknown-classification warnings. |

## Safety Rules

- Do not execute unknown tools.
- Do not allow network access unless the command contract allows it.
- Do not allow writes unless the command contract allows them.
- Keep wrappers no-apply by default.
- Dry-run before execution.
- Preserve underlying exit codes.
- Preserve old tools behind adapters until migration evidence exists.

## Next Work

- Expand wrapper coverage to more proven read-only validators.
- Add structured result evidence capture if future tasks approve output paths.
- Migrate old names behind adapters only after wrapper behavior is proven.
- Retire shims only after validation, reference migration, and ledger evidence.
