Status: PROVISIONAL
Phase: CONVERGE-07
Supersedes: none
Superseded By: none
Stability: provisional

# Domain Split Rules

Current root-level domain folders are likely mixed. CONVERGE-01 records this with `split_required_domain_root` classifications rather than moving them.

For any domain such as geology, chemistry, ecology, hydrology, materials, fluid, thermal, electricity, economy, logistics, civilization, or worldgen, split by ownership:

- schemas, registries, capabilities, protocols, compatibility, and stability rules go to `contracts/`.
- implementation and process logic go to `game/domains/<domain>/`.
- content, datasets, authored fixtures, and pack data go to `content/domain-data/<domain>/` or `content/packs/`.
- human-readable design, doctrine, and explanatory notes go to `docs/domains/<domain>/`.
- determinism tests, fixtures, and proof inputs go to `tests/determinism/<domain>/` or `tests/fixtures/<domain>/`.

Do not move a root domain folder wholesale unless it is proven pure. Most current domain roots are probably mixed across contract, game, content, docs, and tests ownership.

Domain split work must happen after the contract, inventory, and move-map phases. Later moves must preserve process-only mutation, truth/perceived/render separation, pack-driven integration, deterministic ordering, named RNG discipline, and explicit compatibility/refusal obligations.

CONVERGE-06 moved shared schema roots into `contracts/schemas/`. It did not perform a full domain split. Domain-specific schemas and registries found during later domain inspection should ultimately live under `contracts/schemas/<domain>/` or `contracts/registries/<domain>/`, but domain implementation, content, docs, and tests remain separate ownership surfaces.

CONVERGE-07 moved only safe runtime-facing roots into `runtime/`. It did not perform a domain split. Runtime adapters may observe, present, route, and diagnose domain state, but they must not absorb domain law or Process mutation authority during CONVERGE-09.

## CONVERGE-03 Planning Basis

CONVERGE-09 depends on `tools/migration/root_inventory.json` and `tools/migration/root_move_map.json`. Roots classified as `split_required_domain_root` are not move-ready directories; they are inspection scopes.

Before splitting a domain root, inspect at least:

- schema, registry, protocol, capability, compatibility, stability, and ABI material
- implementation and Process logic
- fixtures, authored datasets, packs, profiles, assets, and generated material
- docs, design notes, planning mirrors, and legacy references
- tests, determinism proofs, replay fixtures, and verification inputs

Examples:

- `geo/`: likely splits into geology schemas/registries, game domain implementation, terrain or geologic datasets, docs, and determinism fixtures.
- `chem/`: likely splits into reaction/material contracts, game process logic, authored chemistry data, docs, and validation fixtures.
- `materials/`: likely crosses contracts, game rules, content data, pack descriptors, docs, and tests.
- `worldgen/`: likely crosses generation contracts, deterministic implementation, content seeds/datasets, docs, and tests.
- `process/`: ownership-sensitive because authoritative truth mutation must stay lawful and deterministic.
- `field/` and `fields/`: must respect the existing semantic ownership review; `fields/` is the stronger semantic substrate while `field/` is transitional compatibility.

CONVERGE-09 examples after contract convergence:

- `geo/` schema material -> `contracts/schemas/geology/` or `contracts/registries/geology/`; implementation remains under a game/domain owner.
- `materials/` registry definitions -> `contracts/registries/materials/`; authored material datasets remain content.
- `worldgen/` schemas -> `contracts/schemas/worldgen/`; deterministic generation logic remains game/domain implementation.
- `field/` and `fields/` schema contracts -> `contracts/schemas/fields/` or `contracts/registries/fields/` depending on file role.
