# Audio / UI / Input stubs

Public headers live under `include/domino/` and are C89 friendly. Current implementations are NULL stubs that satisfy linkage without producing sound, windows, or real input mapping.

## Audio (`daudio_*`)
- Header: `include/domino/audio.h`, impl: `source/domino/audio/audio.c`.
- Opaque `daudio_context` from `daudio_init(const daudio_desc*)`; desc selects sample rate/channels/buffer_frames but the null backend ignores them.
- `daudio_get_caps` returns `{ name: "null", max_channels: 0, supports_streams: false, supports_3d: false }`.
- Buffers: `daudio_buffer_create` allocates a small struct (optionally copying interleaved float samples); destroy frees it.
- Playback: `daudio_play`, `daudio_play_stream`, and control calls (`stop`/`set_gain`/`set_pan`) are no-ops that return voice id `0`.

## Unified UI (`dom_ui_*`)
- Header: `include/domino/ui.h`, impl: `source/domino/ui/ui.c`.
- Enums cover mode/backends (`NONE/CLI/TUI/GUI`, bitmask backends), widget kinds (`ROOT/PANEL/LABEL/BUTTON/LIST/TREE/TABS/SPLIT/CANVAS`), and event types (`NONE/CLICK/CHANGE/ACTIVATE/CLOSE`).
- `dom_ui_app_create` builds an in-memory app with a linked list of windows/widgets; no native rendering or event generation occurs.
- Windows/widgets store bounds, text, and callbacks but never dispatch them; `dom_ui_app_pump` just returns `false` once a quit flag is set.
- Canvas helpers always return `NULL` handles and zeroed client rectangles.
- Legacy `domino_ui_*` definitions remain in the header for compatibility with the old stub in `source/domino/system/core/domino_ui_stub.c`.

## Input (`dom_input_*`)
- Header: `include/domino/input.h`, impl: `source/domino/input/input.c`.
- `dom_input_state` tracks key array, mouse buttons/position/wheel, and basic gamepad buttons/axes.
- `dom_input_reset` clears state; `dom_input_consume_event` folds `dsys_event` instances into that state (key down/up, mouse move/button/wheel, gamepad button/axis).
- High-level mapping is stubbed: `dom_input_axis` returns `0.0f` and `dom_input_action` returns `false`.
