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

- `apps/workbench/shell/` may later own shell and workspace manager code.
- `apps/workbench/module/` may later own user-facing Workbench modules.
- `apps/workbench/workspace/` may later own large user-facing compositions.
- Reusable UI primitives belong under `runtime/ui/`, not Workbench app code.

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
