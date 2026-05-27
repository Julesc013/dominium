# Reader Brief — Dominium/Domino Architecture and Codex Prompts

## What This Chat Was About

This chat developed the architecture and implementation roadmap for the Dominium/Domino project. The user provided a master starter prompt defining Domino as a deterministic, fixed-point, ISO C89 engine and Dominium as a portable C++98 product suite. The chat expanded from resources, items, entities, recipes, belts, buildings, vehicles, hydrology, atmosphere, blueprints, and saves into a full engine/product/content/tooling architecture.

The main outcome is a layered, data-driven design: Domino provides generic deterministic systems; Dominium provides products, GUI, launcher/setup/tools; content packs/mods define all actual gameplay data through TLV schemas. The user explicitly corrected the direction to require GUI-first testing and to keep actual data definitions out of engine/core. A sequence of Codex prompts was generated from Prompt 1 through Prompt 18, covering core infrastructure, content, world subsystems, GUI, demo slice, determinism, advanced simulation, logistics, production, research/economy/policies, multiplayer, and tools/editors.

The latest strategic direction is to retire this chat and start a new conversation focused on Path D: advanced simulation, including heat, power grids, fluids, atmosphere, vehicle physics, structural loads/destruction, and mod-extensible deterministic physics.

## Most Important Things to Know

- Domino Engine = ISO C89.
- Dominium products/tools/UI = portable C++98 subset.
- Simulation must be deterministic and fixed-point.
- Engine/core must not know actual gameplay data definitions.
- All real materials/items/machines/recipes/resources live in packs/mods/TLV.
- GUI-first minimal testing is preferred; do not rely only on CLI.
- Rendering goes through dgfx/DVIEW/DUI; no OS-native drawing.
- Platform operations go through dsys.
- The main architecture pattern is Core + Model + Proto + Instance + Registry + TLV.
- Prompts 1-18 are artifacts, not proof of implementation.
- Existing code may already exist and be stale; inspect and reconcile before coding.
- Path D advanced simulation is the next-chat focus.

## Active Plans or Workstreams

- WORKSTREAM-01: Domino engine core infrastructure.
- WORKSTREAM-04: Content/TLV/packs/mods/base pack.
- WORKSTREAM-15: GUI/render/view/UI.
- WORKSTREAM-17: Advanced simulation Path D.
- WORKSTREAM-18: Prompt roadmap and handoff/report packaging.

## Decisions Already Made

- Use C89 for engine and C++98 for products.
- Use fixed-point deterministic simulation.
- Keep platform/rendering behind dsys/dgfx.
- Keep actual content out of engine/core.
- Use GUI-first smoke testing.
- Use base/base_demo packs for data-driven demos.
- Use spline/packet/container logistics.
- Compile vehicles/weapons from blueprints into runtime aggregate objects.
- Focus next chat on Path D.

## Pending Tasks

- Save this report package.
- Inspect actual repository state.
- Start Path D new chat using the bootstrap prompt.
- Verify whether prompts have been implemented.
- Choose/verify GUI backend.
- Define Path D solver architecture and fixed-point ranges.
- Avoid duplicate systems if old code exists.

## Open Questions

- Has any Codex prompt been applied to the repo?
- Which GUI backend is available?
- Should new Path D chat produce architecture or Codex prompts first?
- What exact fixed-point ranges should advanced solvers use?
- How strict should domain-neutrality be in engine comments/docs?
- What exact TLV schema tags are canonical?

## Files / Artifacts / Prompts to Preserve

- ARTIFACT-01: Extended Master Starter Prompt.
- ARTIFACT-02: dres proposal.
- ARTIFACT-09 through ARTIFACT-26: Prompts 1-18.
- ARTIFACT-27: New Chat Advanced Simulation Starter Prompt.
- ARTIFACT-28: Prior Context Transfer Packet.
- ARTIFACT-29: This final report package.

## What to Verify Before Acting

- Actual repo state.
- Build system.
- Existing stale components.
- GUI backend availability.
- Content/TLV schema code.
- Whether user wants architecture or implementation prompt next.
- Any external/current dependency facts.

## Best Next Step

Start the new Path D chat with the bootstrap prompt from the full report or prior transfer packet, then produce the advanced simulation top-level architecture before requesting implementation prompts.
