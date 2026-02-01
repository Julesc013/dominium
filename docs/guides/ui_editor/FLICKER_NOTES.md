Status: DERIVED
Last Reviewed: 2026-02-01
Supersedes: none
Superseded By: none

Win32 DUI batching and relayout checks

Manual verification checklist

- Launcher: resize rapidly; window should remain stable with reduced flicker.
- Launcher: refresh lists or toggle sections that hide/show; avoid visible redraw storms.
- UI Editor: resize preview pane; layout should update smoothly.
- Tool Editor: resize main window; tabs and preview should not thrash redraws.

Optional debug counters

- Define `DUI_WIN32_DEBUG_COUNTERS` and call `dui_win32_debug_dump_counters()` to log paint/erase/relayout/invalidations.