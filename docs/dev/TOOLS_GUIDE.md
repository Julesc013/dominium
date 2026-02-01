Status: DERIVED
Last Reviewed: 2026-02-01
Supersedes: none
Superseded By: none

# Tools Guide (DEV-Tools)

Status: EVOLVING.
Scope: read-only and operational tooling entrypoints.

## Read-only inspection
- `dominium-tools inspect`  
  Read-only topology + metadata (JSON or text via `--format`).
- `dominium-tools validate`  
  Compatibility check output for the current build/runtime.

## Replay inspection
- `dominium-tools replay <path>`  
  Summary and event scan of a replay file.
- `tools/playtest/replay_diff.py`  
  Diff two replay files or runs (read-only).

## Refusal explanation
- `tools/inspect/refusal_explain.py`  
  Parse refusal payloads into a readable explanation.

## Validation & schema tooling
- `tools/validate/*`  
  Dataset and schema validation (read-only by default).
- `tools/worldgen_offline/world_definition_cli.py`  
  WorldDefinition validation and diffs.

## Sandbox and mutation rules
- Tools must default to read-only behavior.
- Any mutation requires explicit, user-initiated intent.
- Tools must be headless-friendly and scriptable.