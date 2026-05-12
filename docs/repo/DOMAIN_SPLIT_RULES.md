Status: PROVISIONAL
Phase: CONVERGE-01
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
