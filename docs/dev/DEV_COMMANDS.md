Status: DERIVED
Last Reviewed: 2026-02-10
Supersedes: none
Superseded By: none

# Dev Commands

Developer wrappers are convenience surfaces only. RepoX/TestX/CI must continue using canonical adapter and tool policies.

## Tool Wrappers

Wrapper entrypoint:

- `python scripts/dev/dev.py`
- `scripts/dev/dev.cmd` (Windows convenience)

Supported commands:

- `python scripts/dev/dev.py tools list`
- `python scripts/dev/dev.py tools doctor`
- `python scripts/dev/dev.py tools ui_bind -- --repo-root . --check`
- direct repo-root shims: `tool_ui_bind`, `tool_ui_validate`, `tool_ui_doc_annotate`

Workspace pinning (optional):

- `python scripts/dev/dev.py --workspace-id <ws_id> tools doctor`

Behavior:

- wrappers call canonical tools by name only
- wrappers apply canonical tool PATH via `scripts/dev/env_tools.py`
- wrappers do not bypass RepoX/TestX invariants

## Gate Wrappers

Canonical autonomous gate entrypoint:

- `python scripts/dev/gate.py precheck`
- `python scripts/dev/gate.py taskcheck`
- `python scripts/dev/gate.py exitcheck`
- `python scripts/dev/gate.py verify`
- `python scripts/dev/gate.py strict`
- `python scripts/dev/gate.py full`
- `python scripts/dev/gate.py snapshot`
- `python scripts/dev/gate.py dist`
- `python scripts/dev/gate.py doctor`
- `python scripts/dev/gate.py dev`
- `python scripts/dev/gate.py remediate`
- optional workspace pinning: `python scripts/dev/gate.py verify --workspace-id <ws_id>`

Equivalent dev wrapper commands:

- `python scripts/dev/dev.py gate precheck`
- `python scripts/dev/dev.py gate taskcheck`
- `python scripts/dev/dev.py gate exitcheck`
- `python scripts/dev/dev.py gate verify`
- `python scripts/dev/dev.py gate strict`
- `python scripts/dev/dev.py gate full`
- `python scripts/dev/dev.py gate snapshot`
- `python scripts/dev/dev.py gate dist`
- `python scripts/dev/dev.py gate doctor`
- `python scripts/dev/dev.py gate dev`
- `python scripts/dev/dev.py gate remediate`

Behavior:

- canonicalizes tool PATH in-process
- runs gate policy classes deterministically (minimal precheck and strict exitcheck)
- supports targeted execution with `--only-gate <gate_id>` for dependency gate diagnostics
- emits remediation artifacts to `docs/audit/remediation/...`
- emits remediation artifacts to `docs/audit/remediation/<workspace_id>/...`
- verify/strict/full are tracked-read-only and write diagnostics under `.xstack_cache/`
- snapshot is the only mode allowed to write `SNAPSHOT_ONLY` artifacts to `docs/audit/`

Sanctioned legacy wrappers:

- `python scripts/dev/gate_shim.py verify`
- `python scripts/dev/run_repox.py`
- `python scripts/dev/run_testx.py`

## Notes

- These wrappers are optional quality-of-life helpers.
- They are not used as authority paths by RepoX/TestX.
