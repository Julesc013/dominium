# Reader Brief — Dominium Architecture IV

## What This Chat Was About

This chat defined and refined the architecture and implementation roadmap for the Dominium game and the reusable Domino engine. It moved from earlier platform/render/launcher/setup/game planning into a more rigorous ABIs-first roadmap. The current plan is to implement all ABIs/APIs first, then all platform backends, all renderer backends, then setup, launcher, tools/SDKs/editors, and finally the game.

The chat also established core architecture: Domino is the reusable engine layer; Dominium is the game/product layer. Products should be described once and presented through arbitrary UI/backend combinations using product contracts, capability descriptors, command/query APIs, data models, views, and canvases. The launcher/setup/tools can run headless/CLI/TUI/native GUI without a renderer; the game requires gfx.

Major game-system design also emerged: deterministic fixed-point numeric policy, integer item storage, world origin at center/sea level, sparse 3D surface grid, Keplerian on-rails space, seamless surface/space transitions via reference frames and sim tiers, and arbitrary constructions as graphs of parts/materials for vehicles/buildings/machines.

## Most Important Things to Know

- Current roadmap: ABIs/APIs → platforms → renderers → setup → launcher → tools → game.
- Actual repository state is unverified.
- Domino and Dominium must stay separate.
- Platform is mandatory; renderer optional for non-game products.
- UI mode and UI backend are separate.
- Product contracts control fallback/failure.
- Renderers consume command-buffer IR.
- Softref renderer is planned as canonical CPU reference.
- Numeric policy: Q4.12, Q16.16, Q48.16 plus integers.
- Inventory/material counts are whole integers.
- `0,0,0` is world center and sea level.
- Space uses Cartesian positions plus Keplerian on-rails orbits.
- Construction is unified across vehicles/buildings/machines.
- Blueprints are operations/plans, not world copies.
- Manual and queued work both flow through jobs.
- Setup should use native OS installer style where possible.
- Tools/SDKs/editors are first-class products.

## Active Plans or Workstreams

Domino engine, Dominium product/game layer, Repository structure, ABI/API spine, Platform API and backends, Renderer API and backends, Audio API and backends, Unified UI system, Product contracts and runtime selection, Packages, instances, mods, packs, Setup product, Launcher product, Tools and SDKs, Game product

## Decisions Already Made

See Decision Register in full report. Highest priority: DECISION-03, DECISION-05, DECISION-07, DECISION-08, DECISION-12, DECISION-19, DECISION-28.

## Pending Tasks

First: verify repo state. Then apply Phase 1 prompts in order.

## Open Questions

Key unresolved issues: schema format, scripting VM, default UPS, actual repo state, Carbon OS APIs, retro backend acceptance criteria, save/replay format, construction graph storage.

## Files / Artifacts / Prompts to Preserve

Phase 1 prompts, platform prompt template, renderer prompt template/vtable/softref, setup prompts, launcher prompts, tools prompts, Phase 7+ roadmap, numeric/construction/seamless transition specs.

## What to Verify Before Acting

Repo tree/build state, README scale, schema format, external packaging/render/platform tools, dependency licenses.

## Best Next Step

Verify the actual repository state, then begin Phase 1 with the Domino ABI/API prompt or ask for detailed Phase 7 prompts only if intentionally skipping implementation order.
