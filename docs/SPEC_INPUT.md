# Dominium — INPUT SPECIFICATION (V1)

Authoritative contract for how Dominium collects, maps, and consumes player input. Aligns with `docs/SPEC_CORE.md`, `docs/DIRECTORY_CONTEXT.md`, `docs/DATA_FORMATS.md`, and `docs/BUILDING.md`.

---

## 0. LAYERS AND RESPONSIBILITIES
- **Platform layer (`/engine/platform`)**
  - Collects raw OS input (keys, mouse, gamepad) into a deterministic, timestamped frame/queue.
  - Normalizes to canonical keycodes (`dom_keycode`) and mouse buttons; no knowledge of gameplay actions.
  - The only place that may include OS headers.
- **Client/game layer (`/game/client`)**
  - Maps raw input → actions via data-driven bindings (JSON).
  - Supports multiple contexts: `global`, `gameplay`, `ui`, `map`, `editor`, `launcher`. `global` is always active; others are enabled per state.
  - Emits deterministic action events used by UI, tools, and sim bridge. No direct OS dependencies.
- **Sim/core**
  - Never sees platform input directly. Only consumes action/command streams provided by the client pipeline.

Input that affects simulation must be deterministic: identical input streams → identical action/event sequences.

---

## 1. FUNCTION KEYS (F1–F12, CANONICAL AND RESERVED)
Function keys are globally reserved and must retain their semantics across contexts. Only remap with explicit warning gates.

| Key | Action ID | Default Behaviour |
|-----|-----------|-------------------|
| F1  | ACTION_HELP_OVERLAY             | Toggle help overlay (keybindings, controls, basic debug). |
| F2  | ACTION_SCREENSHOT_CAPTURE       | Deterministic screenshot / frame capture (client-side). |
| F3  | ACTION_DEBUG_OVERLAY_CYCLE      | Cycle debug overlays (off → basic → full). |
| F4  | ACTION_VIEW_DIMENSION_TOGGLE    | Toggle 2D ↔ 3D view. |
| Shift+F4 | ACTION_VIEW_RENDER_MODE_CYCLE | Cycle render flavour (vector ↔ textured/graphics) within the current dimension. |
| F5  | ACTION_QUICK_SAVE               | Quick save (single-slot, SP only). |
| F6  | ACTION_QUICK_LOAD               | Quick load last quicksave (SP only). |
| F7  | ACTION_REPLAY_PANEL             | Open/cycle replay and time-step controls. |
| F8  | ACTION_TOOLS_PANEL              | Mods/tools/editor/map-editor panel. |
| F9  | ACTION_WORLD_MAP                | Open world map / strategic view. |
| F10 | ACTION_SETTINGS_MENU            | Settings/system menu. |
| F11 | ACTION_FULLSCREEN_TOGGLE        | Fullscreen/borderless/clean-UI cycle. |
| F12 | ACTION_DEV_CONSOLE              | Developer/script console. |

Notes:
- **Launcher**: uses only `F1`, `F3`, `F11`, and optionally `F10` (settings). Other function keys are inert in launcher context.
- **Multiplayer**: `ACTION_QUICK_LOAD` must be disabled or routed to a server-side admin request; client cannot unilaterally load.

---

## 2. DEFAULT GAMEPLAY/UI BINDINGS (CANONICAL MAP)
These defaults are data-driven and loaded from `game/client/input/default_bindings.json`. Mods/user configs may override or extend bindings, but the F1–F12 semantics above remain reserved and should warn before remap.

### Core movement (shared 2D/3D)
- W / A / S / D — Move or pan camera.
- Q / E — Rotate camera (3D) or rotate blueprint (2D build mode).
- R / F — Raise/lower camera altitude (3D) or zoom to cursor (2D).
- Mouse wheel — Zoom in/out (client-side visual only).
- Right mouse drag — Rotate (3D) or pan (2D).
- Middle mouse drag — Pan (CAD style).
- Shift (held) — Fast pan / move.
- Ctrl (held) — Precision / snap mode.

### Selection & construction
- Left click — Select / place.
- Right click — Cancel / remove / context.
- Number keys 1–9 — Quick bar / tool slots.
- Ctrl + mouse wheel — Cycle entities/layers under cursor.
- Tab — Cycle layers or camera targets.

### UI / global
- Esc — Pause / main menu.
- Alt — Highlight interactive elements (tooltips, overlays).
- Ctrl + P — Profiler / performance overlay.

---

## 3. DATA-DRIVEN DEFAULTS
- File: `game/client/input/default_bindings.json`
- Schema (hand-parseable, deterministic):
```json
{
  "version": 1,
  "contexts": {
    "global": [ /* F1–F12 and global overlays */ ],
    "gameplay": [ /* camera, selection, quickbar */ ],
    "ui": [ /* UI back / menu */ ],
    "launcher": [ /* launcher subset */ ]
  }
}
```
- Contexts are additive: `global` is always active; others are enabled/disabled by the client state machine.
- Mods/user configs may override or extend bindings, but the reserved F1–F12 meanings must stay consistent (remap only behind an explicit warning/toggle).

---

## 4. LAUNCHER INPUT
- Launcher uses the shared mapping infrastructure with a dedicated `launcher` context:
  - `ACTION_HELP_OVERLAY` → F1
  - `ACTION_DEBUG_OVERLAY_CYCLE` → F3
  - `ACTION_FULLSCREEN_TOGGLE` → F11
  - `ACTION_SETTINGS_MENU` → F10 (optional)
  - `ACTION_UI_BACK` → Esc
- Other actions remain unbound/inert while the launcher context is active.

---

## 5. INTEGRATION NOTES
- Platform backends normalize raw events to `dom_keycode` (see `/engine/platform/dom_keys.h`) and feed deterministic per-frame queues.
- Client input mapping (`/game/client/input`) converts those events into action events, honoring active contexts and modifiers.
- Action events are then consumed by UI, tools, and the sim bridge; the sim never reads platform input directly.
- Debug logging (compile-time gated) should confirm default bindings loaded and print the bound keys for key system actions (help overlay, debug overlay, view mode, quick save/load, fullscreen, dev console).

End of SPEC_INPUT.md (V1).
