Debug UI
--------
- The in-game debug panel is built with the DUI widget toolkit and can be toggled via the “Toggle Debug Panel” button (or `--devmode` to start visible).
- The panel shows current world hash, chunk count/coordinates, a resource sample at the camera focus, structure counts, loaded packs/mods, content registry counts, and determinism mode status.
- Debug widgets respect DUI visibility flags; when hidden they do not participate in layout or rendering.
- Dev mode marks the session as deterministic-by-default and keeps the panel visible to surface engine state during development.
