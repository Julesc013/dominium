# UI Editor Ops Script Format (ops.json)

This document defines the deterministic edit script format consumed by
`dominium-ui-editor --headless-apply`.

## Top-Level Schema (v1)

```json
{
  "version": 1,
  "docname": "launcher_ui",
  "defaults": {
    "root_name": "root"
  },
  "strict": true,
  "validate": true,
  "ops": [
    { "op": "ensure_root", "name": "root", "type": "CONTAINER" }
  ]
}
```

- `version` (required, int): Must be `1`.
- `ops` (required, array): Applied in file order.
- `docname` (optional, string): Updates doc meta name.
- `defaults.root_name` (optional, string): Default root name for helpers.
- `strict` (optional, bool, default `true`): Unknown fields error unless `false`.
- `validate` (optional, bool, default `true`): Run final validation after ops.

## Selectors

Selectors address widgets deterministically:

- `id`: numeric widget id or a variable reference (`"$var"`).
- `path`: slash-separated names from root, e.g. `"root/main/sidebar"`.
- `query`: `{ "name": "...", "type": "BUTTON" }` (must be unique).

Resolution rules: prefer `id` if present, otherwise `path`, otherwise `query`.
Missing targets or ambiguous matches are errors.

## Variables

Use `out` to capture widget IDs for later ops:

- `out: "$play_id"` stores the widget id under `play_id`.
- Any selector can use `id: "$play_id"` to reference it.

Captured IDs are reported in the `created_ids` map.

## Operations (v1)

### ensure_root

Create a root if missing; verify type if present.

```json
{ "op": "ensure_root", "name": "root", "type": "CONTAINER", "out": "$root" }
```

### create_widget

Create a widget under a parent selector. `if_exists` controls idempotency.

```json
{
  "op": "create_widget",
  "parent": { "path": "root/main" },
  "type": "BUTTON",
  "name": "play_button",
  "if_exists": "reuse",
  "out": "$play_id"
}
```

`if_exists` values:
- `error` (default): fail if name already exists under the parent.
- `reuse`: reuse existing widget of the same type.
- `replace`: delete existing subtree, then recreate.

### delete_widget

```json
{ "op": "delete_widget", "target": { "id": 123 } }
```

### rename_widget

```json
{ "op": "rename_widget", "target": { "id": 123 }, "name": "new_name" }
```

### reparent_widget

```json
{
  "op": "reparent_widget",
  "target": { "id": 123 },
  "new_parent": { "path": "root/sidebar" },
  "z_order": 10
}
```

### set_rect

```json
{ "op": "set_rect", "target": { "id": 123 }, "x": 10, "y": 20, "w": 200, "h": 40 }
```

### set_layout

```json
{
  "op": "set_layout",
  "target": { "id": 123 },
  "dock": "LEFT",
  "anchors": ["L", "T"],
  "margins": { "l": 8, "r": 8, "t": 4, "b": 4 },
  "constraints": { "min_w": 0, "min_h": 0, "max_w": -1, "max_h": -1 }
}
```

### set_container_layout

```json
{
  "op": "set_container_layout",
  "target": { "id": 55 },
  "mode": "STACK_COL",
  "params": {}
}
```

`params` is accepted but ignored in v1 (non-empty params emit a warning).

### set_prop

```json
{
  "op": "set_prop",
  "target": { "id": 123 },
  "key": "text",
  "value": { "type": "string", "v": "Play" }
}
```

Supported types: `int`, `uint`, `bool`, `string`, `vec2i`, `recti`.

### bind_event

```json
{ "op": "bind_event", "target": { "id": 123 }, "event": "on_click", "action": "launcher.nav.play" }
```

### validate

```json
{ "op": "validate", "targets": ["win32", "win32_t1"], "fail_on_warning": false }
```

### save

Explicit save hook (only works when a save callback is provided by the caller).

```json
{ "op": "save" }
```

## Determinism Rules

- Ops are applied in file order.
- Widget IDs are allocated monotonically.
- Diagnostics are emitted in a stable order.
- For idempotent scripts, use `if_exists: "reuse"` and captured IDs.

## Example: Sidebar With Buttons

```json
{
  "version": 1,
  "docname": "launcher_ui",
  "defaults": { "root_name": "root" },
  "ops": [
    { "op": "ensure_root", "name": "root", "type": "CONTAINER" },
    { "op": "create_widget", "parent": { "path": "root" }, "type": "CONTAINER", "name": "sidebar", "if_exists": "reuse", "out": "$sidebar" },
    { "op": "set_rect", "target": { "id": "$sidebar" }, "x": 0, "y": 0, "w": 200, "h": 600 },
    { "op": "create_widget", "parent": { "id": "$sidebar" }, "type": "BUTTON", "name": "play", "if_exists": "reuse", "out": "$play" },
    { "op": "set_rect", "target": { "id": "$play" }, "x": 16, "y": 24, "w": 168, "h": 32 },
    { "op": "set_prop", "target": { "id": "$play" }, "key": "text", "value": { "type": "string", "v": "Play" } }
  ]
}
```
