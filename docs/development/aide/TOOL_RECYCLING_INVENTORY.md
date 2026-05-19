Status: DERIVED
Last Reviewed: 2026-05-16
Supersedes: none
Superseded By: none

# Tool Recycling Inventory

## Status

- Status: PROVISIONAL
- Phase: AIDE-STRUCTURE-01
- Machine-readable inventory: `.aide/reports/tool-recycling-inventory.json`
- Human report: `.aide/reports/tool-recycling-inventory.md`

## Purpose

Dominium contains useful validation, audit, repo-policy, test, build,
migration, CI, and AIDE-adjacent systems. Some names are temporary or too
specific to old tooling eras. This inventory records what exists so future
work can recycle useful behavior through AIDE instead of deleting tools,
renaming blindly, or letting transitional names become permanent architecture.

## Why Old Tools Are Preserved

Old tools encode validation knowledge, operator workflows, and project history.
Removing them before wrappers exist would lose evidence and make future
regression analysis harder. Every existing tool remains preserved unless a
later evidence-backed task proves adaptation, archival, or deletion.

## Why Old Names Are Transitional

XStack, AuditX, RepoX, and TestX are current tooling names, not Dominium
product architecture. Their useful checks should move behind stable AIDE
command contracts before any naming migration or shim retirement.

## Inventory Summary

- Total classified items: 2831
- Wrapper candidates: 37
- Execution allowed now: 0
- High-risk items: 361
- Unknown-risk items: 18

Largest families:

- xstack: 1938
- audit: 608
- aide: 174
- build: 31
- validator: 22

## Fate Categories

- `keep`: useful and stable enough to preserve as-is for now.
- `adapt`: useful but should later be wrapped, renamed, or API-stabilized
  through AIDE.
- `extract`: useful logic exists in a protected or mixed tool and may need
  future splitting.
- `convert`: useful config/prose should later become a contract, schema, or
  validator input.
- `archive`: historically useful but not active; no archive action is approved
  here.
- `drop`: possible future deletion only after evidence; no deletion is approved
  here.
- `preserve_unknown`: insufficient evidence; preserve and do not execute.

## Wrapper Candidates

The recommended first wrapper family for AIDE-STRUCTURE-02 is the AIDE Lite
validation family:

- `tools validate`
- `roots validate`
- `repo validate`
- `xstack validate`

Execution should remain disabled by default in the wrapper contract unless the
specific command is already proven safe and bounded by evidence.

AIDE-STRUCTURE-02 begins that implementation with
`docs/development/aide/AIDE_WRAPPER_COMMANDS.md`,
`.aide/tools/command-contracts/dom-aide-structure-02.commands.toml`, and
`.aide/tools/wrapper-plans/AIDE-STRUCTURE-02.md`.

## High-Risk Tools

High-risk surfaces include broad XStack/AuditX/RepoX/TestX material, build and
package-like tools, CI/GitHub surfaces, migration tools, and unknown developer
scripts. They remain preserved but execution-disabled until side effects,
inputs, outputs, timeouts, and failure behavior are known.

## Next Phases

- AIDE-STRUCTURE-02: wrapper contracts/runner planning for the first safe
  existing checks.
- Later ontology rename: migrate old names only after adapters and references
  are proven.
- Later shim retirement: retire compatibility names only after validation and
  ledger evidence.

## Agent Rules

- Do not execute unknown tools.
- Do not rename first.
- Do not delete first.
- Wrap before rename.
- AIDE controls migration.
- Preserve XStack/AuditX/RepoX/TestX until adapters and retirement evidence
  exist.
