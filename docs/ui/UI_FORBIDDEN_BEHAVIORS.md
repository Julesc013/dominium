# UI Forbidden Behaviors

The UI MUST NOT:
- Mutate simulation state or bypass authority checks.
- Access objective snapshots by default.
- Infer or reveal hidden truth.
- Auto-correct player intent or inject actions directly.
- Provide GUI-only or TUI-only features not present in the CLI.
- Hide failures, refusal reasons, or error codes.
- Expose gameplay difficulty or simulation rule toggles in Settings.
- Use assets, textures, images, external fonts, or content packs in baseline UI.

Any UI implementation violating the above is non-canonical.

## References
- docs/ui/UI_PHILOSOPHY.md
- docs/architecture/INVARIANTS.md
