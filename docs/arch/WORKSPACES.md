# Workspaces (WS0)

Status: binding.
Scope: dev-only workspace overlays.

## Definition
Workspaces are pack-like overlays used for development and testing only.
They never ship in production builds.

## Layout
```
data/workspaces/<workspace_id>/
├── workspace.toml
├── data/
└── schema/
```

Rules:
- Workspace IDs are namespaced (reverse-DNS).
- Workspace removal must be safe and leave no residue outside data root.
- Workspaces are optional; absence must not break loads.

## See also
- `docs/arch/MODPACK_FORMAT.md`
- `docs/arch/INDEXING_POLICY.md`
