# Context Transfer Packet for a Future Chat — Dominium Architecture, UI, Providers, and Robot OS Strategy

## 29.1 Ultra-Condensed Bootstrap Brief

This chat converged a large part of Dominium/Domino’s technical and design direction. The project should be treated as a long-lived platform, not a one-off game. The strongest architecture phrase is: service-first, provider-backed, profile-selected, contract-governed, third-party-fenced, and evidence-tested. Dominium owns contracts, commands, actions, views, documents, saves, replays, packs, profiles, provider law, simulation law, asset identity, diagnostics, and Workbench semantics. Third-party libraries such as raylib, rlgl, rlsw, raygui, SDL2, Lua, raudio, rtextures, and rmodels may be used aggressively, but only as replaceable providers behind first-party service contracts.

The user stated that Dominium has transitioned to C17/C++17 and now targets Windows 7 SP1+, Mac OS X 10.9.5+, and Linux. This deprioritises old first-wave targets such as OpenGL 1.1/2.1 and Direct3D 5/7/8/9. The first direct hardware renderer should be OpenGL 3.3, then Direct3D 11, then Metal/Vulkan/DX12 later. raylib/rlgl/rlsw are seed providers, not architecture. `vector2d` should not be a renderer backend; drawing/canvas is a renderer-independent layer.

The game design direction shifted decisively: Dominium should become a robotic seed-civilisation game, not a labour-management game. Players are robot avatars or machine consciousnesses. A mothership provides knowledge, starter resources, spawn fabrication, and AI planning but is constrained by feedstock, heat, throughput, energy, rare materials, and safety protocols. Gameplay focuses on exploration, surveying, mining, refining, fabrication, logistics, power, sensors, permissions, spawn labs, machine graphs, cities, terraforming, and megaprojects. Human worker NPCs are not core.

The UI/UX should feel like a customizable robot operating system. CLI, TUI, rendered GUI, native GUI, headless, and future immersive/VR shells are projections of the same command/action/view/document system. Workbench authors UI artifacts, not provider-specific objects. Menus, HUD, Workbench, node console, body link, and boot shell should share code and documents. UI customization is allowed only over known/permitted information and cannot hide protected warnings or bypass authority.

## 29.2 Source Hierarchy

1. Direct user statements in this chat.
2. Explicit decisions accepted by the user.
3. Current task register.
4. Constraint register.
5. Artifact ledger.
6. Inferences from repeated user acceptance and synthesis.
7. Assistant suggestions not explicitly accepted.
8. General model knowledge.

## 29.3 Operating Rules for Future Assistants

Preserve FACT / INFERENCE / UNCERTAIN / UNVERIFIED / PROJECT-CONTEXT labels. Do not assume access to the old chat. Do not re-ask answered questions. Verify stale facts before relying on them. Flag contradictions. Use the task register and open questions to choose next actions. Do not treat tentative items as final. Do not repeat rejected options such as one universal GUI framework, vector2d as backend, raylib as architecture, or human labour as core. Preserve artifacts and use structured outputs when continuing.

## 29.4 Active Workstreams

- WORKSTREAM-01: Repository and directory architecture.
- WORKSTREAM-02: Service/provider/profile architecture.
- WORKSTREAM-03: C17/C++17 and platform floor.
- WORKSTREAM-04: Renderer/drawing plan.
- WORKSTREAM-05: Workbench and shared UI platform.
- WORKSTREAM-06: Robot OS UI/UX.
- WORKSTREAM-07: Robotic seed-civilisation game design.
- WORKSTREAM-08: Setup/launcher user-selectable components.
- WORKSTREAM-09: Data/schema/pack/save compatibility.
- WORKSTREAM-10: Preservation and aggregation.

## 29.5 Current Priorities

1. PROVIDER-WEDGE-01.
2. ROBOT-OS-WEDGE-01.
3. Game design spec extraction.
4. Matrix cleanup and verification.
5. UI customization/security spec.

## 29.6 Current Open Questions

Top open questions: Lua version pin; exact Linux baseline; current repo tree truth; first gameplay vertical slice; Unreal’s role after raylib-first; official-server UI customization policy; consciousness backup/disconnect/body persistence rules.

## 29.7 Recommended First Action

Create a Codex-ready PROVIDER-WEDGE-01 task: provider manifest schema, third-party manifest, forbidden include validator, null providers, raylib/rlgl/rlsw/raygui/raudio providers, client/workbench/server profiles, and conformance smoke tests.
