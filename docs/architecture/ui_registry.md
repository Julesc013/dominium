Status: DERIVED
Last Reviewed: 2026-02-15
Supersedes: none
Superseded By: none
Version: 1.0.0
Compatibility: Bound to `schemas/ui_window.schema.json` v1.0.0, `schemas/ui_registry.schema.json` v1.0.0, and canon v1.0.0.

# UI Registry and Descriptor Contract v1

## Purpose
Define descriptor-driven tool windows as pack data, compiled into `ui.registry.json`, with PerceivedModel-only bindings and process-intent actions.

## Source of Truth
- Window schema: `schemas/ui_window.schema.json` (`version: 1.0.0`)
- Derived registry schema: `schemas/ui_registry.schema.json` (`version: 1.0.0`)
- Compiler path: `tools/xstack/registry_compile/compiler.py`
- Headless host path: `tools/xstack/sessionx/ui_host.py`

## Descriptor Fields (`ui_window` v1.0.0)
Required:
- `schema_version` (`"1.0.0"`)
- `window_id`
- `title`
- `required_entitlements[]`
- `widgets` (tree root)

Optional:
- `required_lenses[]`

### Supported Widget Types
- `container`
- `text`
- `button`
- `list`
- `tree`
- `input_text`
- `input_number`

Unknown widget types refuse at schema validation time.

## Binding Rules
Data binding:
- `data_binding.source` must be `perceived_model`
- `data_binding.selector` must use selector syntax:
  - dot path with optional index selectors
  - pattern: `token(.token)*` with optional `[n]` or `[*]`
  - example: `navigation.hierarchy`, `entities.entries[0].entity_id`

Action binding:
- `action_binding.intent_id`
- `action_binding.process_id`
- `action_binding.payload_template`

Template tokens in payloads:
- `${widget.<field>}`
- `${selection.<field>}`
- `${perceived.<selector>}`

Selector syntax violations refuse deterministically during registry compile.

## Gating Policy (Lab v1)
Policy: unavailable windows are hidden from available set and emitted in tool log with reason.

Gates:
- Entitlement gate: `required_entitlements[]` against `AuthorityContext.entitlements[]`
- Lens gate: `required_lenses[]` against active `PerceivedModel.lens_id`
- Law gate: `LawProfile.debug_allowances.allow_nondiegetic_overlays` must be true for non-diegetic overlays

On failure:
- Window excluded from `available_windows`
- Logged under `tool_log` with deterministic reason and IDs
- Refusal reason codes include `ENTITLEMENT_MISSING` and `LENS_FORBIDDEN`

## Determinism Invariants
- `ui.registry.json` windows sorted by `(window_id, pack_id)`
- Descriptor validation failures are deterministic and sorted
- Same descriptor + perceived snapshot + widget state + selection yields identical emitted intent payload
- UI host emits intents only; authoritative mutation occurs only through process runtime

## Example (Window Descriptor)
```json
{
  "schema_version": "1.0.0",
  "window_id": "window.tool.goto",
  "title": "Go-To",
  "required_entitlements": [
    "entitlement.teleport"
  ],
  "required_lenses": [
    "lens.diegetic.sensor",
    "lens.nondiegetic.debug"
  ],
  "widgets": {
    "widget_id": "goto.root",
    "type": "container",
    "layout": "vertical",
    "children": [
      {
        "widget_id": "goto.results",
        "type": "list",
        "data_binding": {
          "source": "perceived_model",
          "selector": "navigation.search_results"
        }
      },
      {
        "widget_id": "goto.teleport",
        "type": "button",
        "action_binding": {
          "intent_id": "intent.ui.goto.teleport",
          "process_id": "process.camera_teleport",
          "payload_template": {
            "target_object_id": "${selection.object_id}",
            "target_site_id": "${selection.site_id}"
          }
        }
      }
    ]
  }
}
```

## Add-a-Window Steps (Pack-Only)
1. Add descriptor JSON in `packs/tool/<pack_id>/ui/window.<name>.json`.
2. Add `ui_windows` contribution in that pack `pack.json`.
3. Validate schema with `tools/xstack/schema_validate ui_window <descriptor_path>`.
4. Rebuild registries with `tools/xstack/registry_compile`.
5. Verify deterministic output via `tools/xstack/run fast`.

## TODO
- Add optional descriptor-localization map contract.
- Add versioned selector grammar contract file.
- Add widget state persistence contract for future UI sessions.

## Cross-References
- `docs/canon/constitution_v1.md`
- `docs/canon/glossary_v1.md`
- `docs/architecture/truth_perceived_render.md`
- `docs/architecture/camera_and_navigation.md`
- `docs/architecture/registry_compile.md`
- `docs/contracts/authority_context.md`
- `docs/contracts/refusal_contract.md`
