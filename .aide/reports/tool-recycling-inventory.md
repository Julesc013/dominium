# Tool Recycling Inventory

## Status

- Task: AIDE-STRUCTURE-01
- Status: INVENTORY_CREATED
- Scope: metadata inventory and classification only
- Tools executed from inventory: false
- Moves/deletes/renames: false
- Wrappers applied: false

## Evidence Inputs

- `.aide/reports/AIDE-STRUCTURE-00-status.md`
- `.aide/reports/AIDE-STRUCTURE-00-validation.md`
- `.aide/reports/AIDE-STRUCTURE-00-blockers.md`
- `.aide/tools/latest-tool-inventory.json`
- `.aide/tools/latest-tool-inventory.md`
- `.aide/tools/latest-tool-wrap-plan.json`
- `.aide/tools/latest-tool-wrap-plan.md`
- `.aide/reports/DOM-AIDE-02-wrapper-selection.md`
- `.aide/reports/DOM-AIDE-02-validation.md`
- `.aide/reports/DOM-AIDE-02-blockers.md`
- `.aide/context/dominium-doctrine-refs.md`
- `docs/aide/AIDE_REFACTOR_FRAMEWORK.md`
- `docs/aide/XSTACK_RECYCLING_PLAN.md`

Missing expected aliases:

- `.aide/tools/latest-wrap-plan.json`
- `.aide/tools/latest-wrap-plan.md`
- `.aide/reports/latest-dominium-status.md`
- `.aide/reports/latest-warning-disposition.md`

The current baseline uses `.aide/tools/latest-tool-wrap-plan.*`,
`.aide/reports/dominium-aide-operating-baseline.md`, and
`.aide/reports/dominium-aide-warning-disposition.md` instead.

## Summary Counts

- Total classified items: 2831
- Wrapper candidates: 37
- Execution allowed now: 0

By family:

- aide: 174
- appshell: 13
- audit: 608
- build: 31
- ci: 6
- migration: 3
- repo_policy: 11
- test: 3
- ui_bind: 2
- ui_index: 2
- unknown: 18
- validator: 22
- xstack: 1938

By fate:

- adapt: 2616
- convert: 1
- keep: 196
- preserve_unknown: 18

By risk:

- high: 361
- low: 16
- medium: 2436
- unknown: 18

## Tool Families

The inventory confirms that Dominium has active AIDE, XStack, AuditX,
RepoX-like, TestX-like, build, validator, migration, AppShell, UI bind/index,
CI, and script surfaces. XStack/AuditX/RepoX/TestX-style material dominates the
inventory and should be recycled through wrapper contracts rather than renamed
or deleted first.

## Candidate Wrapper Families

Highest-priority candidates for AIDE-STRUCTURE-02:

1. AIDE Lite validation command family through `.aide/scripts/aide_lite.py`.
2. Build contract validator: `tools/build/validate_build_contract.py`.
3. Component matrix and distribution layout validators.
4. Repo layout/root allowlist validators only after the local `build/` and
   `out/` generated-root blocker is resolved or explicitly classified.
5. Supplemental docs/build/UI/ABI validators after wrapper side effects are
   documented.

Execution should remain disabled by default in the next wrapper contract unless
the specific command is already proven safe and bounded by existing evidence.

## High-Risk/Unknown Tools

High or unknown records remain preserved and execution-disabled. Counts by
family for high/unknown risk:

- aide: 94
- appshell: 1
- audit: 46
- build: 4
- ci: 3
- migration: 2
- repo_policy: 2
- test: 1
- unknown: 18
- validator: 2
- xstack: 206

These include broad legacy validation surfaces, build/test/package-like tools,
CI/GitHub surfaces, and unknown developer scripts. They require classification,
side-effect proof, and wrapper contracts before execution or renaming.

## Preserve / Adapt / Extract / Convert / Archive / Drop Summary

- `keep`: stable AIDE and validator surfaces that are useful as-is for now.
- `adapt`: most legacy tool surfaces; useful behavior should be wrapped through
  AIDE before naming migration.
- `extract`: protected high-risk families may contain useful logic that later
  needs splitting from broad tools.
- `convert`: CI/policy-like configuration can later become contract-backed
  validator inputs.
- `archive`: no active archive recommendation was applied in this task.
- `drop`: no deletion recommendation is actionable in this task.
- `preserve_unknown`: 18 items lack enough evidence and must not be executed.

## Why Nothing Was Moved Or Renamed

This task is inventory and classification only. Bad long-term names are not a
reason to delete or rename tools. The safe sequence remains:

```text
inventory -> classify -> wrap through AIDE -> adapt useful logic -> rename only after adapters exist -> archive/drop only with evidence
```

## Next Steps

- AIDE-STRUCTURE-02: create wrapper contracts for the first low-risk existing
  check family.
- AIDE-ROOT-00: expand root recycling and salvage-map work.
- POST-CONVERGE-10F: address unit annotation and RepoX drift through
  AIDE-controlled evidence.
