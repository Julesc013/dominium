Status: DERIVED
Last Reviewed: 2026-05-21
Supersedes: none
Superseded By: none
Stability: provisional

# Workbench Workspace Model

Workbench is a production environment and presentation shell over registered
commands, services, modules, diagnostics, evidence, documents, and views. It is
not authority over product semantics.

## Structure

- `apps/workbench/shell/` owns Workbench shell and workspace-manager code when
  that runtime exists.
- `apps/workbench/module/` owns Workbench presentation modules only: editors,
  inspectors, panels, previews, dashboards, validation projections, and UI glue.
- `apps/workbench/workspace/` owns large user-facing Workbench compositions.
- Reusable UI primitives belong under `runtime/ui/`, not Workbench app code.
- Reusable domain, generation, validation, service, provider, package, and
  command behavior stays under its owning `game/`, `runtime/`, `engine/`,
  `tools/`, or contract root.

This task defines only contracts and validators. It does not create or migrate
those runtime directories.

## Workspaces

A workspace declares `workspace_id`, modules, panels, views, commands, layouts,
capabilities, and evidence surfaces. Planned workspace IDs include:

- `dominium.workbench.workspace.project_graph`
- `dominium.workbench.workspace.interface_studio`
- `dominium.workbench.workspace.module_foundry`
- `dominium.workbench.workspace.app_composer`
- `dominium.workbench.workspace.release_forge`

## Panels And Views

Panels bind to view bindings. View bindings project command results, documents,
and evidence into UI forms. They must not call private tools. A validation
table view should bind to `dominium.validation.run` and result/evidence schemas,
not to a Python validator file path.

## Rule

Workbench modules and workspaces consume typed results, diagnostics, refusals,
and evidence. They do not invent meanings for diagnostics and do not mutate
truth directly.

Workbench modules may present and edit module descriptors, pack payloads, world
blueprints, seeds, previews, and evidence. They must not own reusable
world-creation law, worldgen engines, provider backends, pack/profile
resolution, or server/client runtime behavior.
