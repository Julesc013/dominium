# Reader Brief — Dominium + Domino Refactor Architecture

## What This Chat Was About

This chat was a detailed architecture and refactor planning session for the Dominium + Domino project. The central result is a stable separation between **Domino**, the deterministic engine under `source/domino`, and **Dominium**, the product suite under `source/dominium`. The user explicitly chose to flatten the Dominium product source layout by removing `source/dominium/products` and placing `common`, `game`, `launcher`, `setup`, and `tools` directly under `source/dominium`. The chat also established that Domino should not be installed as a separate end-user runtime; it should be linked/bundled into Dominium products, with a separate developer SDK only as a future possibility.

The product model is four products: Game, Launcher, Setup, and Tools. Game is a single product with startup modes for client, listen server, dedicated server, and demo/full. Launcher is the main access point to the suite. Setup handles portable/per-user/system-wide install, import, repair, uninstall, and GC. Tools is an aggregated product beginning with existing `dominium_modcheck`.

The chat also defined the `DOMINIUM_HOME` model for multi-version installs. Product builds, mods, and packs live in a shared versioned repo; instances reference versions instead of copying whole suites. Versioning is split across core, products, formats, protocols, mods, and packs, with Suite version equal to Game version. The base official modpack should match Game version by release convention, but engine validity should use compatibility ranges.

Several Codex prompts were generated, including a master refactor prompt and a post-refactor consistency prompt. It is not verified that any prompt was applied.

## Most Important Things to Know

- Domino stays under `source/domino`; do not rename to `source/engine`.
- Dominium source is flattened under `source/dominium/common`, `game`, `launcher`, `setup`, `tools`.
- Do not keep `source/dominium/products` in the final layout.
- Domino is not a separate end-user runtime product.
- Dominium has four products: Game, Launcher, Setup, Tools.
- Game is one binary/product with modes, not separate client/server/demo products.
- Demo is content/instance policy, not a separate product.
- Launcher is the main suite hub.
- Launcher should use actions, not hardcoded executable paths.
- Setup supports portable, per-user, and system-wide install modes.
- DOMINIUM_HOME stores repo/products, repo/mods, repo/packs, and instances.
- Instances reference versions; they do not copy full suites.
- Suite version equals Game version.
- Core/product/protocol/format versions are separate.
- Base mod version matching Game version is a convention, not engine invariant.
- DLC/user mods/packs use independent versions and compatibility ranges.
- Use explicit architecture tags such as `x86-64`, not `x64`.
- All product UI/rendering must go through Domino dsys/dgfx/canvas.
- Codex prompts were generated; application status is unknown.

## Active Plans or Workstreams

- Apply source layout refactor.
- Add compat/platform headers and product introspection.
- Unify Game client/server/demo modes.
- Implement DOMINIUM_HOME repo/instance APIs.
- Implement actions loader and Launcher integration.
- Implement Setup import/install/GC.
- Update content manifests and packaging scripts.
- Run post-refactor consistency sweep.

## Decisions Already Made

See DECISION-01 through DECISION-22 in the registers. Highest impact: DECISION-01, DECISION-02, DECISION-03, DECISION-06, DECISION-08, DECISION-11, DECISION-13, DECISION-14, DECISION-18, DECISION-19.

## Pending Tasks

Highest priority tasks are TASK-24, TASK-01, TASK-02, TASK-03, TASK-04, TASK-05, TASK-06, TASK-07, TASK-08, TASK-09, TASK-10, TASK-11, TASK-12, and TASK-13.

## Open Questions

- Has Codex applied the generated prompts?
- What are the current actual version numbers?
- Which parser should repo/instance/actions manifests use?
- What exact DOMINIUM_HOME defaults should each OS use?
- Which root-level tools should become DominiumTools?
- How much UI/packs work should be included in the next implementation phase?

## Files / Artifacts / Prompts to Preserve

- User-provided existing repo directory tree.
- Master Refactor Prompt.
- Post-Refactor Consistency Pass Prompt.
- Starter Prompt Generator Prompt.
- Extended Master Starter Prompt Generator Prompt.
- Initial Context Transfer Packet.
- This report package.

## What to Verify Before Acting

- Repo state after any Codex run.
- Current version macros and data versions.
- Whether new headers/targets exist.
- Whether `source/dominium/products` remains.
- Whether product introspection works.
- Whether CMake/tests build.
- Whether docs/scripts still contain stale paths or `x64`.

## Best Next Step

Ask the user whether Codex has already applied the master refactor prompt. If not, run or refine the master refactor prompt. If yes, run the post-refactor consistency prompt and then verify the build/test results.
