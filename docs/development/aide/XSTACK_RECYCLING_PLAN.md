Status: DERIVED
Last Reviewed: 2026-05-16
Supersedes: none
Superseded By: none

# XStack Recycling Plan

## Status

- Status: PROVISIONAL
- Phase: AIDE-STRUCTURE-00

## Why XStack/AuditX/RepoX/TestX Are Preserved

XStack, AuditX, RepoX, and TestX contain useful validation knowledge, historical
assumptions, project-specific checks, and operator workflows. Their names and
paths are transitional, but the evidence they encode is valuable.

Deleting them first would lose validation memory. Renaming them first would
break references before adapters exist. Executing unknown commands first could
write caches, build outputs, generated reports, package artifacts, release
metadata, or runtime state.

## Why Old Names Are Transitional

The old names are not Dominium product architecture. They are current tool
surfaces and historical control-plane language. Future architecture should use
stable capability names behind AIDE command contracts, not accidental names
from earlier tooling waves.

## Wrap-Before-Rename Plan

1. Inventory existing tools without execution.
2. Classify capabilities, risks, inputs, outputs, and side effects.
3. Create wrapper contracts with execution disabled by default.
4. Implement adapters only for proven read-only/report-only checks.
5. Migrate names after references and behavior are protected by adapters.
6. Retire shims only after validation and ledger evidence prove no consumer
   still depends on them.

## Tool Fate Categories

- `keep`: preserve the tool or command as-is.
- `adapt`: keep behavior behind an AIDE wrapper or new command contract.
- `extract`: split useful checks from a mixed or risky tool.
- `convert`: convert reports or policy data into AIDE-native evidence.
- `archive`: preserve historical material outside active execution paths.
- `drop`: remove only after explicit evidence and approval.

## Phases

- `inventory`: list tools, references, capabilities, and risk.
- `wrapper contracts`: define stable AIDE command contracts.
- `adapter implementation`: create report-only adapters for proven-safe tools.
- `naming migration`: update consumers after adapters are stable.
- `shim retirement`: retire legacy names only after validation and ledger proof.

## AIDE-STRUCTURE-01 Inventory

AIDE-STRUCTURE-01 records the first tool recycling inventory under
`.aide/reports/tool-recycling-inventory.*` and summarizes it in
`docs/development/aide/TOOL_RECYCLING_INVENTORY.md`. It does not execute, rename, move, or
delete legacy tools.

## AIDE-STRUCTURE-02 Initial Wrappers

AIDE-STRUCTURE-02 creates the first stable wrapper command surface documented
in `docs/development/aide/AIDE_WRAPPER_COMMANDS.md` and planned in
`.aide/tools/wrapper-plans/AIDE-STRUCTURE-02.md`. It wraps AIDE-native
validation commands first and leaves XStack/AuditX/RepoX/TestX names preserved
behind future adapters.

## Forbidden Actions

- delete first
- rename first
- execute unknown tools
- let product/runtime naming leak from XStack/AuditX/RepoX/TestX
- treat old tool names as durable architecture
