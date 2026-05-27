# Reader Brief — Dominium Launcher Setup Architecture

## What This Chat Was About

This chat designed the Dominium launcher, setup system, runtime-launcher contract, and related modular architecture. It began from the user’s broad Dominium philosophy: deterministic C89 engine core, stable APIs, versioned/TLV file formats, data-first content/mods, optional plugins, and migration rather than silent breakage. The conversation then narrowed into how the launcher should behave for users: install the game, run the launcher, create profiles, choose versions/mods/settings, and launch one or more client/server/tool instances.

The launcher became an optional all-in-one Dominium control center, not a hard dependency. The game must still run directly without launcher involvement. The setup system became a separate canonical install/repair/uninstall authority. The user then fixed the built-in launcher tabs as News, Changes, Mods, Instances, and Settings, and required these tabs to be fully interactive.

The final major direction change was the user’s requirement that the launcher be designed and implemented using the Domino platform/rendering layers: `dsys` for platform services and `dgfx` for rendering, with strict C89 APIs and retro/modern support. This latest dsys/dgfx direction supersedes earlier C++98/ncurses/SDL/ImGui launcher frontend prompts.

## Most Important Things to Know

- Latest active launcher implementation direction: C89 + dsys + dgfx.
- Game/runtime must run standalone with no launcher.
- Launcher supervision is optional and disableable.
- Instance display modes are NONE, CLI, TUI, GUI.
- Setup, launcher, and game should remain separate binaries unless user revises this.
- Setup must support portable, per-user, and system-wide installs.
- Setup must support defaults and full customization.
- Launcher tabs are News, Changes, Mods, Instances, Settings.
- Tabs must be fully interactive.
- Mods tab is a full mod manager.
- Instances tab manages instances and installations.
- Settings tab must be intuitive and powerful.
- Launcher/setup/instances should be modular and extensible.
- Plugins should be ABI-versioned.
- Earlier JSON schemas conflict with later TLV/dmeta direction.
- Actual repo, build system, dsys/dgfx APIs were not inspected.

## Active Plans or Workstreams

- WORKSTREAM-01: Global Dominium architecture and repo strategy.
- WORKSTREAM-03: Runtime/game executable integration.
- WORKSTREAM-04: Setup system.
- WORKSTREAM-05: Launcher all-in-one hub.
- WORKSTREAM-06: Launcher tabs and interaction model.
- WORKSTREAM-07: Plugin/extensibility.
- WORKSTREAM-08: dsys/dgfx C89 launcher implementation.

## Decisions Already Made

- Use one codebase / monorepo.
- Prefer separate setup, launcher, and game binaries.
- Engine remains deterministic C89.
- Game runs without launcher.
- Display modes: NONE, CLI, TUI, GUI.
- Setup is canonical install/repair/uninstall authority.
- Tabs are News, Changes, Mods, Instances, Settings.
- Latest launcher uses dsys and dgfx.

## Pending Tasks

- Inspect repo.
- Resolve JSON vs TLV/dmeta.
- Verify dsys/dgfx API names.
- Generate dsys/dgfx Work-order 1.
- Implement launcher data layer.
- Implement UI widgets/layout/events.
- Implement dgfx renderer.
- Implement process supervision.
- Implement tabs.
- Implement harness.
- Verify runtime capabilities.

## Open Questions

- JSON or TLV/dmeta?
- Is setup also C89/dsys?
- What are real dsys/dgfx API names?
- What is actual runtime binary structure?
- How much retro support is first-class now?
- Does dsys provide dynamic plugin loading?
- How to handle News/Changes open/browse on retro platforms?

## Files / Artifacts / Prompts to Preserve

- Global architecture philosophy.
- Runtime CLI contract.
- Setup system prompt/spec.
- Launcher tabs spec.
- dsys/dgfx launcher architecture.
- C89 header sketches.
- Codex work-order sequence.
- Context Transfer Packet.
- This report package.

## What to Verify Before Acting

- Repo layout/build system.
- dsys/dgfx APIs.
- TLV/metadata implementation.
- Runtime capabilities.
- Setup language/system-layer requirements.
- Plugin loading APIs.

## Best Next Step

Generate dsys/dgfx Work-order 1: core launcher config/install/profile/mods data layer in C89 using dsys filesystem and versioned metadata, after resolving or explicitly flagging the JSON-vs-TLV/dmeta format question.
