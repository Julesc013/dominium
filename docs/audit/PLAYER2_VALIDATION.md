Status: DERIVED
Last Reviewed: 2026-02-01
Supersedes: none
Superseded By: none

# PLAYER-2 Validation

Scope: engine/ + game/ + docs/player for PLAYER-2 (player embodiment as agent).

Validation artifacts:
- `engine/tests/player_embodiment_tests.cpp` (headless, no assets)

Coverage matrix:
- Player agent cannot bypass authority: `test_player_authority_block`
- Player sees only subjective truth: `test_player_subjective_snapshot`
- Player intent refused cleanly: `test_player_intent_refusal_and_history`
- Player failure produces history: `test_player_intent_refusal_and_history`
- Multiplayer determinism: `test_multiplayer_determinism`

Notes:
- Tests are deterministic and avoid UI/render dependencies.