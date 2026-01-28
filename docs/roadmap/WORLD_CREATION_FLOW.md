# World Creation Flow (WD-0)

Status: binding.
Scope: canonical world creation and load flow.

## Canonical flow
1) User selects a template.
2) User sets parameters (seed, policies).
3) Template generates a WorldDefinition.
4) WorldDefinition is written into the save.
5) Engine loads the WorldDefinition.
6) Simulation begins.

At no point may the engine infer world structure outside the WorldDefinition.

## Save / load / replay integration
- Saves embed the full WorldDefinition.
- Replays reference the WorldDefinition by value or hash.
- Loading a save does not re-run templates.
- Missing capabilities cause explicit refusal or degraded/frozen modes.

## Refusal integration
Refusals are surfaced identically across CLI/TUI/GUI and must include stable
codes and structured payloads.

## References
- `docs/architecture/WORLDDEFINITION.md`
- `docs/worldgen/TEMPLATE_REGISTRY.md`
