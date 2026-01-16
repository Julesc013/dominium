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
# UI Actions and Events (UI IR + DUI Runtime)

## Scope
- Defines action keys, numeric action IDs, the registry format, and deterministic codegen outputs.
- Describes how DUI backends emit `domui_event` and how dispatch is wired.
- UI Editor GUI is out of scope.

## Action keys (UI IR)
- UI documents store event bindings as `event_name -> action_key` (string).
- Action keys are stable, human-readable identifiers (e.g., `tool_editor.quit`).
- Canonical ordering for events is lexicographic by `event_name`.

## Numeric action IDs (registry)
- Codegen assigns a stable numeric ID to each action key.
- IDs are monotonic per registry file and never reused.
- Registry is JSON, deterministic ordering by key:
```
{
  "next_id": 2,
  "actions": {
    "tool_editor.quit": 1
  }
}
```
- If a key is removed from the doc and later re-added, it keeps the same ID.

## Codegen outputs (gen/user split)
For a document name `tool_editor`, codegen emits:
- `ui_tool_editor_actions_gen.h/.cpp` (generated; safe to overwrite).
- `ui_tool_editor_actions_user.h/.cpp` (user; append-only inside markers).

Generated artifacts:
- `DOMUI_ACT_<SANITIZED_KEY>` numeric ID defines.
- `ui_tool_editor_get_action_table()` returns a sorted table `{action_id, fn, key}`.
- `ui_tool_editor_action_id_from_key()` resolves key -> id deterministically.
- `ui_tool_editor_dispatch()` finds the action function and invokes it.

User stubs:
- Function signature:
  `void ui_tool_editor_act_<SANITIZED>(void* user_ctx, const domui_event* e);`
- Codegen only appends new stubs inside:
  `// BEGIN AUTO-GENERATED ACTION STUBS` ... `// END AUTO-GENERATED ACTION STUBS`

## DUI runtime dispatch (win32/dgfx/null)
- Backends may emit legacy `dui_event_v1` (queue) and also call action dispatch.
- Dispatch uses `domui_event` (see `include/dui/domui_event.h`).
- Optional ABI: `dui_action_api_v1` via `query_interface` (`DUI_IID_ACTION_API_V1`).
- Backends map events to `domui_event_type`:
  - `CLICK` for button activation.
  - `CHANGE` for value changes (text, checkbox, list selection, slider, splitter drag).
  - `SUBMIT` for list activation (double-click/enter).
  - `TAB_CHANGE` for tab selection change (`a` = selected index).

## Determinism rules
- Registry output is byte-stable for identical inputs.
- Codegen output is stable across runs for identical inputs.
- No hashing; no random IDs; no timestamps.

## Non-goals
- No UI editor GUI.
- No TLV schema changes for launcher UI yet.
- No layout engine changes.
