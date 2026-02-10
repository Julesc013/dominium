Status: DERIVED
Last Reviewed: 2026-02-10
Supersedes: none
Superseded By: none

# RepoX Tool Rules

This document defines RepoX invariants for canonical tool discoverability and invocation.

## INV-TOOL-NAME-ONLY

- Intent: canonical tools must be invoked by name only.
- Fails when scripts/tests/CMake/CI use canonical tool paths directly.
- Fails when CMake uses target-file path indirection for canonical tool execution.
- Allowed form: `tool_<name> ...` after `env_tools` canonical PATH setup.

## INV-TOOLS-DIR-EXISTS

- Intent: RepoX must canonicalize tool discovery in-process.
- Fails when canonical tool root is not active in RepoX process `PATH` after canonicalization.
- Canonical root prefers `dist/ws/<workspace_id>/sys/<platform>/<arch>/bin/tools/` and falls back to `dist/sys/<platform>/<arch>/bin/tools/`.

## INV-TOOLS-DIR-MISSING

- Intent: fail explicitly when canonical tools output does not exist yet.
- Fails when `dist/sys/<platform>/<arch>/bin/tools/` is missing.
- Remediation hint is mandatory: build tools via `ui_bind_phase` or canonical tools target.

## INV-TOOL-UNRESOLVABLE

- Intent: canonical tools must be executable by name once PATH is canonicalized.
- RepoX validates discoverability at run start.
- Fails when any required canonical tool is missing or not resolvable by name.

## Canonical Required Tools

- `tool_ui_bind`
- `tool_ui_validate`
- `tool_ui_doc_annotate`

## Operational Rule

- RepoX/TestX self-canonicalize internally; manual shell PATH setup is not required.
- Workspace selection is deterministic unless explicitly pinned via `DOM_WS_ID`.
- Repo-root shim commands (`tool_ui_bind.cmd`, `tool_ui_validate.cmd`, `tool_ui_doc_annotate.cmd`)
  are allowed for interactive use and resolve canonical binaries only.
- `scripts/dev/env_tools.*` remains optional convenience for interactive shells.
- Preferred entrypoints are:
  - `python scripts/dev/gate.py precheck`
  - `python scripts/dev/gate.py exitcheck`
  - `python scripts/dev/gate.py verify`

Prompt and queue automation must use the gate contract in `docs/governance/PROMPT_GATE_CONTRACT.md`.

See `docs/governance/GATE_AUTONOMY_POLICY.md` for autonomous gate flow.
