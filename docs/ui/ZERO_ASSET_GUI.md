# Zero-Asset GUI

The zero-asset GUI is the PRIMARY GUI mode. It must function fully with:
- Zero packs installed.
- Zero textures or images.
- Zero external fonts.
- Zero themes or UI content packs.

The baseline GUI may use ONLY:
- Vector primitives (rectangles, lines, circles).
- Solid colors (hardcoded constants).
- Text rendered via built-in vector font or system default font.
- Layout rules.

## Non-negotiable requirements
- Must not load assets to render baseline UI.
- Must not block on missing packs.
- Must be deterministic and headless-capable.
- Must be parity-locked with CLI and TUI.

## Renderer expectations
- Null renderer and Software renderer MUST be supported.
- GPU renderers are optional and must not change behavior.

## References
- docs/arch/GUI_BASELINE.md
- docs/ui/UI_PHILOSOPHY.md
- docs/ui/CLI_TUI_GUI_PARITY.md
