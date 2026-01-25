# Worldgen Offline Tools

Offline-only utilities for refinement planning, validation, epistemic simulation,
and pack overlay inspection. These tools read data packs and emit disposable
artifacts under `build/cache/assets/`. They do not modify engine or game code.

Tools:
- `refinement_runner.py` - materializes refinement requests and metadata.
- `validation_checker.py` - compares expected vs actual tool outputs.
- `epistemic_simulator.py` - builds subjective snapshot metadata from knowledge.
- `pack_diff_visualizer.py` - reports capability overlaps and refinement conflicts.
- `world_definition_cli.py` - generates, validates, and diffs WorldDefinitions.

All outputs are optional and reproducible. Delete `build/cache/assets/` at any
time without affecting packs or saves.
