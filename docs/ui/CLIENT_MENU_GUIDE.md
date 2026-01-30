# Client Menu Guide (P3)

Status: binding for P3. Applies to CLI, TUI, and GUI.

## Menu Entries (Authoritative)

1. **New World**
   - Opens the world creation wizard.
   - Disabled with reason if no templates are available.

2. **Load World**
   - Lists saves under `{data_root}/saves/`.
   - Shows: name, created_at, required_caps, compat summary, file path.
   - Disabled with reason if no saves exist.

3. **Replay**
   - Lists replays under `{data_root}/replays/`.
   - Shows: source, duration (event count), determinism status.
   - Inspect-only playback with step/pause/rewind.
   - Disabled with reason if no replays exist.

4. **Tools**
   - Opens tools shell (handoff).
   - Always visible.

5. **Settings**
   - Opens settings screen.
   - Always visible.

6. **Exit**
   - Exits the client shell.

## Global Rules

- Disabled entries remain visible with explicit reasons.
- No placeholder actions.
- CLI is canonical; TUI/GUI wrap the same intents.
