--------------------------------
OWNERSHIP & RESPONSIBILITY
--------------------------------
ENGINE:
- None. This spec is implemented under `tools/`.

GAME:
- None. This spec is implemented under `tools/`.

TOOLS:
- Authoring/inspection utilities described here.
- Implementation lives under `tools/` (including shared tool runtime).

SCHEMA:
- None (no canonical schema formats defined here).

FORBIDDEN:
- No launcher/setup orchestration logic in engine or game.
- No engine internal headers exposed outside engine targets.
- No game rules or policy implemented inside engine primitives.
- No runtime authority or game rules inside tools.

DEPENDENCIES:
- Engine -> libs/ and schema/ only (never game/launcher/setup/tools).
- Game -> engine public API and schema/ only.
- Tools -> engine public API, game public API, and schema/ only.
- Launcher/Setup (if applicable) -> libs/contracts + schema (launcher may also use engine public API).
--------------------------------
# UI Action Codegen (Registry + Gen/User Split)

## Scope
- Defines the action registry format and deterministic codegen outputs.
- Documents `domui_codegen` CLI usage and outputs.
- Applies to UI docs that bind events to `action_key` strings.

## Action keys
- UI docs store `event_name -> action_key` bindings (strings).
- Action keys are stable, human-readable identifiers (e.g., `tool_editor.quit`).
- Canonical event ordering is lexicographic by event name.

## Registry (stable numeric IDs)
- Registry file is JSON, deterministic ordering by key.
- IDs are monotonic per registry and never reused.
- Removing and re-adding an action key preserves the same ID.

Example:
```json
{
  "next_id": 2,
  "actions": {
    "tool_editor.quit": 1
  }
}
```

## Codegen outputs (per document)
For doc name `tool_editor`, codegen emits:
- `ui_tool_editor_actions_gen.h/.cpp` (generated; safe to overwrite)
- `ui_tool_editor_actions_user.h/.cpp` (user; append-only inside markers)

Generated artifacts:
- `DOMUI_ACT_<SANITIZED_KEY>` numeric ID defines.
- `ui_tool_editor_get_action_table()` returns `{action_id, fn, key}` table.
- `ui_tool_editor_action_id_from_key()` resolves key → id.
- `ui_tool_editor_dispatch()` routes `domui_event` to the user handler.

User stubs:
- Signature:
  `void ui_tool_editor_act_<SANITIZED>(void* user_ctx, const domui_event* e);`
- Codegen only appends new stubs inside:
  `// BEGIN AUTO-GENERATED ACTION STUBS` ... `// END AUTO-GENERATED ACTION STUBS`

## CLI usage (`domui_codegen`)
Preferred mode:
```
domui_codegen --in <ui_doc.tlv> --out <dir> --registry <registry.json> [--docname <name>]
```
This writes to `<dir>/gen` and `<dir>/user`.

Legacy mode (still supported):
```
domui_codegen --input <ui_doc.tlv> --registry <registry.json> --out-gen <dir> --out-user <dir> [--doc-name <name>]
```

Output summary (deterministic):
- action count
- registry path
- output directories
- output file paths

## Build option
- `DOMUI_ENABLE_CODEGEN` (CMake, default ON) controls build-time codegen steps for tools.

## Determinism rules
- Registry output is byte-stable for identical inputs.
- Codegen output is stable across runs for identical inputs.
- No hashing, random IDs, or timestamps.
