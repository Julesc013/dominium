Status: DERIVED
Last Reviewed: 2026-03-10
Supersedes: none
Superseded By: none

# EMB-1 Retro Audit

## Scope

This audit records the existing embodiment, interaction, and viewer surfaces available before EMB-1 toolbelt integration.

## Existing Interaction Commands And Inspect Surfaces

Existing viewer and inspection surfaces already provide:

- teleport planning through `src/client/ui/teleport_controller.py`
- inspection panels through `src/client/ui/inspect_panels.py`
- overlay provenance through `tool.geo.explain_property_origin`
- field and terrain debug overlays through the viewer shell

These surfaces are already derived-view only and do not need a new truth path for EMB-1.

## Existing Geometry Edit Processes

The process runtime already exposes deterministic geometry edit processes:

- `process.geometry_remove`
- `process.geometry_add`
- `process.geometry_replace`
- `process.geometry_cut`

These remain the only lawful mutation path for terrain edits.

## Existing Logic Probe And Analyzer Processes

The process runtime and LOGIC debug surface already expose:

- `process.logic_probe`
- `process.logic_trace_start`
- `process.logic_trace_tick`
- `process.logic_trace_end`

EMB-1 can wire these through tool affordances without inventing new logic mutation or observation semantics.

## UI Exposure Readiness

Existing host surfaces already support command/button-style exposure without OS-specific work:

- CLI tooling under `tools/`
- TUI-friendly viewer shell payloads in `src/client/ui/viewer_shell.py`
- rendered client panels and control payloads

No inventory system or platform-native launcher widget is required for EMB-1.

## Findings

- Toolbelt work can be implemented as capability wrappers over existing processes.
- Terrain editing must remain process-only and continue using GEO-7 geometry edit processes.
- Scanner output must be assembled from inspection snapshots, field summaries, and explain/provenance results only.
- Logic probe and trace affordances can remain thin planners around existing LOGIC-7 processes.
- Teleport should reuse the existing MW-4 refinement-aware teleport plan rather than adding a separate transport path.
