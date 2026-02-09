Status: DERIVED
Last Reviewed: 2026-02-09
Supersedes: none
Superseded By: none

# Tool Invocation Policy

Canonical tool invocation is PATH-based and name-only.

## Canonical Tool Root

- Canonical runtime tools directory: `dist/sys/<platform>/<arch>/bin/tools/`
- Examples:
- Windows: `dist/sys/winnt/x64/bin/tools/`
- Linux: `dist/sys/linux/x64/bin/tools/`

Only this directory is sanctioned for canonical tool discovery.

## Required Adapter

Use the single adapter family under `scripts/dev/`:

- `scripts/dev/env_tools.py`
- `scripts/dev/env_tools.cmd`
- `scripts/dev/env_tools.ps1`
- `scripts/dev/env_tools.sh`

The adapter is responsible for:

- resolving host platform/arch to canonical tool root
- prepending canonical tool root to `PATH` deterministically
- validating canonical tools are discoverable by name
- failing with refusal diagnostics when discovery is invalid

## Canonical Invocation Form

Invoke canonical tools by executable name only:

- `tool_ui_bind --repo-root . --check`
- `tool_ui_validate --help`
- `tool_ui_doc_annotate --help`

Forbidden invocation forms:

- absolute paths
- repo-relative paths
- build-tree-relative paths

## Scope

This policy applies to:

- RepoX
- TestX
- CI scripts
- developer shells
- wrapper scripts and mega-prompt execution instructions
