# Debug and Inspect Access (P3)

Status: binding for P3. Applies to CLI, TUI, and GUI.

## Always-Available Access

- Debug/inspect is always reachable without content packs.
- Console exists in TUI/GUI and maps directly to CLI commands.
- No hidden or UI-only commands.

## Inspect Surface (World View)

Inspect overlays MUST expose:

- entity identity (world id)
- provenance (template + source)
- active policies (authority/mode/debug)
- refusal codes and details (when applicable)

## Replay Inspect (Read-Only)

- Replay playback is inspect-only.
- Supports step, pause, rewind.
- Missing or incompatible replays refuse explicitly.

## Logs and Explanations

- Refusals are visible and explainable.
- Logs remain deterministic across CLI/TUI/GUI.
- No stack traces are shown by default.
