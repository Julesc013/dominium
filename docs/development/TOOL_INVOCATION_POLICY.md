Status: DERIVED
Last Reviewed: 2026-02-10
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: patched document aligned to current canon ownership and release scope

# Tool Invocation Policy

## Patch Notes

- Current status: partially aligned to the Constitutional Architecture and release-freeze documentation set.
- Required updates: documentation surface exists, but current canon ownership is not explicit
- Cross-check with: `docs/archive/audit/CANON_MAP.md` and `docs/archive/audit/DOC_DRIFT_MATRIX.md`.


Canonical tool invocation is PATH-based and name-only.

## Canonical Tool Root

- Canonical runtime tools directory: `archive/generated/dist/sys/<platform>/<arch>/bin/tools/`
- Examples:
- Windows: `archive/generated/dist/sys/winnt/x64/bin/tools/`
- Linux: `archive/generated/dist/sys/linux/x64/bin/tools/`

Only this directory is sanctioned for canonical tool discovery.

## Canonical Adapter Family

Adapter utilities under `scripts/dev/`:

- `scripts/dev/env_tools.py`
- `scripts/dev/env_tools.cmd`
- `scripts/dev/env_tools.ps1`
- `scripts/dev/env_tools.sh`

Adapter responsibilities:

- resolving host platform/arch to canonical tool root
- prepending canonical tool root to `PATH` deterministically
- validating canonical tools are discoverable by name
- failing with refusal diagnostics when discovery is invalid

Repo-root command shims are provided for zero-setup interactive use:

- `scripts/dev/shims/tool_ui_bind.cmd`
- `scripts/dev/shims/tool_ui_validate.cmd`
- `scripts/dev/shims/tool_ui_doc_annotate.cmd`

These shims resolve and execute the canonical binary from
`archive/generated/dist/sys/<platform>/<arch>/bin/tools/` and do not change policy.

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

## Execution Policy

- RepoX and TestX must canonicalize PATH internally before any tool discoverability checks.
- Manual shell preparation via `env_tools` is optional convenience only.
- Preferred gate entrypoint: `python scripts/dev/gate.py verify`.
