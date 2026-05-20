Status: DERIVED
Last Reviewed: 2026-05-21
Supersedes: none
Superseded By: none
Stability: provisional

# Workbench Module Guidelines

Workbench modules are user-facing projections over command, service, document,
view, diagnostic, refusal, and evidence surfaces. They are not authority over
truth or product semantics.

## Boundaries

- Put reusable UI primitives in `runtime/ui/`.
- Keep Workbench shell/workspace orchestration separate from modules.
- Bind behavior to command IDs and service IDs.
- Present result documents and evidence packets without inventing meanings.
- Use typed refusals and diagnostics for unsupported or unavailable behavior.

## Workspace Composition

A workspace composes modules, panels, views, commands, and evidence surfaces.
It should be declared with `contracts/workbench/workspace.schema.json` and
validated with:

```text
python tools/validators/contracts/check_workbench_workspaces.py --repo-root . --strict
```

No private tool calls are allowed in workspace or view-binding descriptors.
