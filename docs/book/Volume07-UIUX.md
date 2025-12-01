```markdown
// docs/book/Volume07-UIUX.md
# Dominium Design Book v3.0
## Volume 07 — UIUX

### Overview
The UI is deterministic, renderer-agnostic, and platform-neutral. It supports ortho/isometric/3D views, vector and texture renderers, canonical input streams, HUD overlays, text/localisation, notifications/logging/clipboard/undo, and a full accessibility layer. UI projects simulation snapshots; simulation remains authoritative.

### Requirements (MUST)
- Maintain renderer independence: single UI description usable across SDL1/SDL2/OpenGL 1.1/2.0/DX9/DX11/software; supports vector and bitmap modes.
- Support views: orthographic 2D, isometric 2D, 3D/FP/freecam, minimap, world/galaxy maps.
- Input pipeline: hardware → Dominium Input Layer → canonical ordered event stream → SIM_CMD/UI_EVT/SYS_EVT/LOG_EVT via Engine Message Bus; deterministic ordering (SIM_CMD > SYS_EVT > UI_EVT > LOG_EVT).
- HUD rules: deterministic state derived from simulation + canonical UI events; overlay layering for networks/logistics/climate; in-world anchors for entities; mode-unified across renderers.
- Text/localisation: UTF-8 everywhere; NFC normalisation; multi-tier font pipeline (bitmap fallback, vector fallback, Unicode TTF/OTF engine fonts, mod fonts). Deterministic shaping, bidi support, kerning; no platform-dependent layout.
- Notifications/logging/clipboard/undo: command-based undo/redo; internal clipboard fallback; deterministic log ordering (tick/sequence/subsystem); notifications UI-only.
- Accessibility (Volume 7.22): UI scale 0.5–4.0, text size override, colorblind/high-contrast modes, readability options; subtitles/visual sound indicators; reduced cognitive load; input assistance; presets.
- Deterministic snapshots: UI reads tick snapshots, never queries simulation mid-tick; interpolation only for visuals.

### Recommendations (SHOULD)
- Batch UI events (tooltips ≤15 Hz, notifications ≤10 Hz, logs ≤5 Hz) to protect UPS/FPS.
- Provide mod-extensible panels/markers/themes within deterministic layout constraints.
- Use deterministic word-wrapping and line heights; avoid fractional jitter in texture mode.
- Offer minimal modes for retro/low-end paths while preserving information.

### Prohibitions (MUST NOT)
- UI must not mutate simulation directly; only via SIM_CMD through EMB.
- No nondeterministic rendering or platform font shaping; no HUD repositioning outside defined grids/docking.
- Mods cannot hide essential HUD data or bypass deterministic ordering.
- No clipboard or OS integration that alters simulation outcome; presentation-only.

### Detailed Sections
#### 7.1 — UI Architecture and Views
- Layers: renderer primitives → UI core (panels/widgets/layout/fonts) → game UI (HUD/toolbars/inspectors/overlays) → view layer (ortho/iso/3D/minimap/world/galaxy) → input/interaction.
- Works on Win2000+/macOS 10.6+/Linux; retro modes for Win98/SDL1 and future DOS/Win3.x.

#### 7.2 — Input and Interaction (Volume 9H)
- Canonical Input Event Stream ensures deterministic ordering; supports keyboard/mouse/gamepad.
- Simulation sees only canonical events; hardware polling differences are abstracted.
- Supports hotkeys, accessibility input rules, and platform-neutral bindings.

#### 7.3 — HUD and Overlays (Volume 9J)
- Deterministic HUD surfaces loads/flows/alerts; supports hiding/minimal/expert/guided modes.
- Overlay layers for networks, logistics, climate, markers; in-world anchors for entity billboards.
- Same HUD semantics in vector, texture, and 3D screen-space.

#### 7.4 — Text, Fonts, and Localisation (Volume 9K)
- UTF-8, NFC; Tiered fonts (bitmap fallback, vector fallback, Dominium Sans/Serif/Mono, mod fonts).
- Deterministic shaping (ligatures, bidi, kerning), deterministic wrapping and scaling; RTL support.
- Localisation files in `/locale/<lang>/strings.json` with fallback `<lang> → English → placeholder`; mod locale overrides allowed with validation.

#### 7.5 — Notifications, Logging, Clipboard, Undo (Volume 9L)
- EMB classes: SIM_CMD/UI_EVT/SYS_EVT/LOG_EVT with ordered timestamps/sequence IDs.
- Notifications are UI-only representations of SIM_NOTICE; expiry deterministic; critical persist until acknowledgment.
- Logging levels ERROR/WARN/INFO/DEBUG/TRACE; includes tick/sequence/subsystem; deterministic replay.
- Clipboard: engine clipboard always available; OS clipboard optional; blueprint copies carry commands not state.
- Undo/redo via command journal (type/args/reverse args/tick/sequence); physics/network packets not undoable.

#### 7.6 — Accessibility (Volume 7.22)
- Vision: UI scale 0.5–4.0, font overrides, colorblind modes, high contrast, readability aids.
- Hearing: subtitles (basic/full), scale/background, visual sound indicators; STT/TTS on capable OS.
- Cognitive: reduced load simplifies UI/hides redundancy/reduces animation; enhanced tooltips.
- Input assistance and motion reduction; presets (Vision-Friendly, Hearing-Friendly, Cognitive Simplification, Motor Assistance, Full Accessibility, Minimal Mode).

### Cross-References
- Volume 02 — Simulation (snapshots feeding UI)
- Volume 03 — World (map layers, entity anchors)
- Volume 04 — Networks (overlay data)
- Volume 05 — Economy (market UI, finance panels)
- Volume 06 — Climate (weather overlays)
- Volume 08 — Engine (EMB, logging, command stack)
- Volume 09 — Modding (UI extensions, fonts, localisation packs)
```
