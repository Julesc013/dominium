Status: DERIVED
Last Reviewed: 2026-03-10
Supersedes: none
Superseded By: none

# MVP Toolbelt Baseline

## Scope

This report records the EMB-1 MVP toolbelt baseline delivered for Dominium v0.0.0.

## Available Tools

The baseline toolbelt exposes the following capability affordances:

- `tool.terrain_edit`
- `tool.scanner_basic`
- `tool.logic_probe`
- `tool.logic_analyzer`
- `tool.teleport`

These are capability surfaces only.
No inventory ownership or crafting dependency was introduced.

## Entitlements And Gating

The canonical EMB-1 entitlements are:

- `ent.tool.terrain_edit`
- `ent.tool.scan`
- `ent.tool.logic_probe`
- `ent.tool.logic_trace`
- `ent.tool.teleport`

Tool use remains constrained by:

- `AuthorityContext`
- `LawProfile`
- access-policy registry rows
- existing process-level law gates

Terrain edits still require the underlying geometry-edit process gates.
Logic probe and trace remain bounded and epistemic-gated.

## Deterministic Behavior

Implemented deterministic behavior:

- terrain tool plans only lawful geometry-edit process sequences
- scanner output is derived from inspection, field, and provenance inputs
- logic probe and analyzer plans are deterministic and bounded
- teleport reuses the MW-4 refinement-aware deterministic planner
- CLI and viewer surfaces expose the same stable command vocabulary

The canonical EMB-1 replay probe is `tools/embodiment/tool_replay_tool_session.py`.

## UI And Command Exposure

The viewer shell now emits:

- `toolbelt_surface`
- scanner and logic tool panels through inspection surfaces
- tool command ids:
  - `tool mine`
  - `tool fill`
  - `tool cut`
  - `tool scan`
  - `tool probe`
  - `tool trace`
  - `tool tp`

The runtime bundle publishes matching command bindings for MVP bootstrap.

## Forward Readiness

EMB-1 is ready for:

- server-authoritative tool invocation loops
- AppShell command hosting
- future itemization of tools without changing command semantics
- richer diegetic measurement and authority profiles layered on the same capability registry
