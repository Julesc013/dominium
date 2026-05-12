# Content Root

Status: PROVISIONAL
Phase: POST-CONVERGE-03

`content/` owns authored content inputs that are meant to be source material for Dominium rather than runtime state or generated output.

This includes authored packs, profiles, datasets, fixtures-as-content, assets, templates, and domain data when those materials are not implementation code, schema authority, generated distribution output, or mutable runtime stores.

Content rules:

- Pack and profile IDs must be preserved during any move.
- Bundle/profile/package identity must not be rewritten by path cleanup.
- Runtime mutable stores belong to install, instance, save, or store projections, not this source root.
- Generated distribution output belongs under generated or release-output policy, not source content.
- Machine-readable schema and contract authority belongs under `contracts/`.
- Engine, game, runtime, AppShell, and tooling implementation code must stay in their owning source roots.

POST-CONVERGE-03 did not move identity-sensitive pack, profile, bundle, data, modding, model, or template material into `content/`; it recorded the current split and left protected roots for later review.
