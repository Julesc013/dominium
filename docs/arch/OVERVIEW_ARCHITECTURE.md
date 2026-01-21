# Dominium Architecture Overview

- **Domino engine** (`engine/`): C90 deterministic core with modules under
  `engine/modules/` and render backends under `engine/render/`. Public headers
  live under `engine/include/domino/`.
- **Dominium game** (`game/`): C++98 rules and domain logic that depend only on
  the engine public API. Public headers live under `game/include/dominium/`.
- **Products**:
  - `client/` and `server/` are entrypoints that link the engine + game libraries.
  - `launcher/` provides orchestration frontends and links `engine::domino` +
    `libs::contracts`.
  - `setup/` provides installer frontends and links `libs::contracts`.
- **Tools** (`tools/`): offline validators and editors; some tools link
  `engine::domino` and others are contract-only.
- **Shared contracts** (`libs/contracts`): cross-product headers used by
  launcher/setup/tools.
- **Schemas** (`schema/`): data schemas and validation docs (no build targets).

## See also
- `docs/arch/CANONICAL_SYSTEM_MAP.md`
- `docs/arch/ARCHITECTURE.md`
- `docs/arch/ARCHITECTURE_LAYERS.md`
