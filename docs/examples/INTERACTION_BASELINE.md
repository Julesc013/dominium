Status: DERIVED
Last Reviewed: 2026-02-01
Supersedes: none
Superseded By: none

# Interaction Baseline (I0)

This guide documents the reversible, non-progressive interaction baseline. The client remains fully usable with zero content packs, and interactions are data-only, deterministic, and explainable.

## Scope
- Inspect, place, remove, measure, and toggle signal interactions.
- No progression, economy, AI, or irreversible state changes.
- CLI is canonical; TUI/GUI wrap the same commands.

## Data Pack
Baseline primitives are defined in the data-only pack:
- `org.dominium.core.interaction.baseline`
- Marker, beacon, and indicator parts (no external assets).
- Baseline measurement instrument for position/distance.

## Interaction Policies
Interaction permissions are enforced by law/meta-law via `policy.interaction.*`.

Common policies:
- `policy.interaction.place`
- `policy.interaction.remove`
- `policy.interaction.signal`
- `policy.interaction.measure`
- `policy.interaction.inspect`
- `policy.interaction.radius=<meters>` (optional distance limit from player position)

Refusals are explicit and should reference `docs/architecture/REFUSAL_SEMANTICS.md`.

## CLI Quickstart
Create a world and perform baseline interactions:
```
dominium_client create-world template=world.template.exploration_baseline seed=42
dominium_client batch load path=data/saves/world.save; \
  object-select type=org.dominium.core.interaction.beacon; \
  place pos=1,0,0; \
  signal-toggle id=1; \
  measure id=1; \
  object-inspect id=1; \
  remove id=1; \
  save path=data/saves/interaction.save; \
  replay-save path=data/replays/interaction.replay
```

Notes:
- `place-preview` and `place-confirm` are available when you want explicit two-step placement.
- `object-list` shows all placed objects and the current selection.

## Inspect & Explainability
`object-inspect` shows:
- object ID
- defining data source
- provenance ID
- current signal state (if applicable)

Refusals include a reason and the policy that blocked the action.

## Save / Load / Replay
Interactions are stored in saves and replays:
- `interaction_*` lines appear in `.save` files.
- `client.interaction.*` events appear in `.replay` files.

## Tooling
Inspect saved interactions or replay events:
```
python tools/inspect/interaction_inspector.py --save data/saves/interaction.save --format text
python tools/inspect/interaction_inspector.py --replay data/replays/interaction.replay --format text
python tools/inspect/interaction_inspector.py --diff data/replays/a.replay data/replays/b.replay --format text
```

## What This Does Not Include
- No progression, economy, activities, or AI systems.
- No asset requirements or hidden content assumptions.
- No UI-only behavior; CLI/TUI/GUI are identical.