# Signals Baseline (S0-LITE)

This guide documents the symbolic, event-driven signal baseline. Signals are deterministic, constant-cost, and explainable with zero content packs.

## Scope
- Digital boolean and bounded integer signals.
- Simple routing, thresholds, and visual indication.
- No physics, continuous waves, RF propagation, or surveillance.

## Data Pack
Baseline signals and components are defined in:
- `org.dominium.core.signals.baseline`
- Button, lever, wire, lamp, counter (no external assets).
- Data-only process families for emit/toggle/route/threshold/indicate.

## CLI Quickstart
Create a world and build a simple button → wire → lamp path:
```
dominium_client create-world template=world.template.exploration_baseline seed=42
dominium_client batch load path=data/saves/world.save; \
  object-select type=org.dominium.core.signal.button; \
  place pos=1,0,0; \
  object-select type=org.dominium.core.signal.wire; \
  place pos=2,0,0; \
  object-select type=org.dominium.core.signal.lamp; \
  place pos=3,0,0; \
  signal-connect from=1 to=2; \
  signal-connect from=2 to=3; \
  signal-toggle id=1; \
  signal-list; \
  save path=data/saves/signals.save; \
  replay-save path=data/replays/signals.replay
```

Threshold example (counter → lamp):
```
dominium_client batch load path=data/saves/world.save; \
  object-select type=org.dominium.core.signal.counter; \
  place pos=4,0,0; \
  object-select type=org.dominium.core.signal.lamp; \
  place pos=5,0,0; \
  signal-threshold from=1 to=2 threshold=2; \
  signal-set id=1 value=3
```

Notes:
- `signal-preview` is available for a non-committing link preview.
- `signal-set` emits an explicit value; `signal-toggle` flips boolean signals.

## Inspect & Explainability
`object-inspect` includes:
- signal value and last change tick
- inbound and outbound links
- provenance and data source

Refusals are explicit and should reference `docs/architecture/REFUSAL_SEMANTICS.md`.

## Save / Load / Replay
Signals are captured in artifacts:
- `signals_*` lines appear in `.save` files.
- `client.signal.*` events appear in `.replay` files.

## Tooling
Inspect signal networks and replay parity:
```
python tools/inspect/signal_inspector.py --save data/saves/signals.save --format text
python tools/inspect/signal_inspector.py --replay data/replays/signals.replay --format text
python tools/inspect/signal_inspector.py --diff data/replays/a.replay data/replays/b.replay --format text
```

## What This Does Not Include
- No analog waves, RF propagation, or encryption.
- No networking, surveillance, or continuous-time simulation.
- No UI-only behavior; CLI/TUI/GUI are identical.
