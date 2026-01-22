# Engine/Game Diagnostics

Engine and game modules remain platform-agnostic and do not host UI layers.
APR3 does not add new engine/game CLI tools.

Diagnostics live in the application layer:
- `client`, `server`, `launcher`, `setup`, and `tools` provide CLI-only smoke
  paths and build-info output.
- Engine/game tests run via `ctest` (see `engine/tests` and `game/tests`).

If additional diagnostics are needed, prefer app-layer tools that call into
existing engine/game interfaces without changing engine/game behavior.
