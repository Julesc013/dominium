# Dominium Game

Status: placeholder for M1.

This folder will host the standalone game runtime, frontends, and content wiring.
Specs:
- SPEC_RUNTIME.md
- SPEC_COMMANDS.md
- SPEC_SAVE.md
- SPEC_REPLAY.md
- SPEC_CONTENT.md

## Runtime determinism hash
The runtime exposes `dom_game_runtime_get_hash`, which uses Domino's authoritative
world hash (`d_sim_hash_world`) over serialized world/instance state to validate
determinism across ticks.
