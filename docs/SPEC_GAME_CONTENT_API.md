# Game Content API

- Header: `include/dominium/game_content_api.h`; implementation in `source/dominium/product/common/game_content_api.c`.
- Purpose: thin Dominium-facing wrappers over Domino registries so game code/mods can register content without touching internal registries directly.
- Functions:
  - `dom_game_register_machine_type(const MachineType*)`
  - `dom_game_register_recipe(const Recipe*)`
  - `dom_game_register_tech(const Tech*)`
  - Blueprint helpers: `dom_game_create_blueprint(name, capacity)`, `dom_game_blueprint_add_elem`, `dom_game_blueprint_generate_jobs`
- Behaviour: deterministic, direct pass-through to Domino registries; IDs are sequential/stable for a session/build.
