Status: DERIVED
Last Reviewed: 2026-02-09
Supersedes: none
Superseded By: none

# RepoX Tool Rules

This document defines RepoX invariants for canonical tool discoverability and invocation.

## INV-TOOL-NAME-ONLY

- Intent: canonical tools must be invoked by name only.
- Fails when scripts/tests/CMake/CI use canonical tool paths directly.
- Fails when CMake uses target-file path indirection for canonical tool execution.
- Allowed form: `tool_<name> ...` after `env_tools` canonical PATH setup.

## INV-TOOLS-PATH-SET

- Intent: RepoX execution environment must include canonical tools directory in `PATH`.
- Fails when canonical tool root is missing from process `PATH`.
- Canonical root is resolved from `dist/sys/<platform>/<arch>/bin/tools/`.

## INV-TOOL-UNRESOLVABLE

- Intent: canonical tools must be executable by name once PATH is canonicalized.
- RepoX validates discoverability at run start.
- Fails when any required canonical tool is missing or not resolvable by name.

## Canonical Required Tools

- `tool_ui_bind`
- `tool_ui_validate`
- `tool_ui_doc_annotate`

## Operational Rule

Before RepoX/TestX/CI execution, apply `scripts/dev/env_tools` for the current shell:

- `scripts/dev/env_tools.cmd`
- `scripts/dev/env_tools.ps1`
- `scripts/dev/env_tools.sh`
- `python scripts/dev/env_tools.py ...`
