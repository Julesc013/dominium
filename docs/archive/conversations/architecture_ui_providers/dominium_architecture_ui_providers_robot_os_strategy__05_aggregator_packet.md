# Aggregator Packet — Dominium Architecture, UI, Providers, and Robot OS Strategy

## Packet Metadata

* Chat label: Dominium Architecture, UI, Providers, and Robot OS Strategy
* Date anchor: 2026-05-27 Australia/Melbourne
* Source scope: This chat only unless labelled PROJECT-CONTEXT.
* Coverage: Partial with caveats.
* Confidence: 4/5.
* Staleness risk: Medium.
* Merge priority: High.
* Main limitations: visible chat plus pasted prior-chat material, not guaranteed raw older transcripts; external facts require verification.

## Ultra-Condensed Carry-Forward Capsule

This chat converged Dominium/Domino around two major axes: a technical platform architecture and a game/UI identity. Technically, the strongest doctrine is service-first, provider-backed, profile-selected, contract-governed, third-party-fenced, and evidence-tested. Dominium owns services, contracts, commands, actions, views, documents, saves, replays, packs, profiles, provider law, asset identities, diagnostics, and Workbench semantics. Third-party libraries such as raylib, rlgl, rlsw, raygui, raudio, rtextures, rmodels, SDL2, and Lua may be used aggressively, but only as replaceable providers behind first-party contracts. Apps remain generic and compose services; provider choices belong in profiles. Third-party types must not leak into engine, game, contracts, content, saves, replays, packs, public SDK, or game law.

The language baseline changed from older C89/C++98 framing to C17/C++17. The user stated first-wave minimum systems as Windows 7 SP1+, Mac OS X 10.9.5+, and Linux. This makes old fixed-function/old-DirectX lanes non-primary. OpenGL 1.1/2.1 and Direct3D 5/7/8/9 are deferred to research/back-port. OpenGL 3.3 is the first direct hardware renderer target, Direct3D 11 follows for Windows, and Metal/Vulkan/DX12 are later. Software renderer remains valuable for CPU framebuffer, evidence, tests, fallback, and reference behavior. rlsw may be a raylib software provider but not the canonical Dominium reference renderer. `vector2d` should not be a renderer backend; drawing/canvas is a renderer-independent layer.

The UI platform direction is that CLI, TUI, rendered GUI, native GUI, headless, and later immersive/VR shells are projections of the same command/action/view/document model. Workbench is the authoring environment for UI artifacts: views, widgets, layouts, themes, HUDs, TUI panels, rendered screens, workspaces, preview fixtures, and UI packs. It edits Dominium documents and patches, not raylib/raygui/native UI objects.

The biggest game-design contribution is that Dominium should be a robotic seed-civilisation game, not a labour-management game. Players are robots or machine consciousnesses. A mothership provides human knowledge, starter resources, spawn fabrication, and AI planning, but is constrained by feedstock, throughput, heat, energy, rare materials, safety protocols, reserves, and scale. Gameplay focuses on exploration, surveying, mining, refining, fabrication, logistics, power, sensors, permissions, machine graphs, spawn labs, cities, terraforming, and megaprojects. Nanotech gives precise manipulation, not free matter/energy/logistics. Human worker NPCs are not core.

The final UX identity is a customizable robot operating system. The player boots into an OS, connects to a universe/node, downloads consciousness into a manufactured body, and uses the same OS shell as menu, Workbench, CLI/TUI, HUD, and future VR interface. UI should respect diegetic epistemics: sensor source, confidence, staleness, permission, network path, and speed-of-light/latency. Customization is allowed but cannot reveal hidden data, hide critical warnings, bypass permissions, or automate illegal actions.

## Top Carry-Forward Items

| Priority | Item | Type | Related ID | Why it matters | Label | Confidence |
| --- | --- | --- | --- | --- | --- | --- |
| P0 | Service-first/provider-backed/profile-selected architecture | decision | DECISION-01 | Core technical doctrine | FACT | 4 |
| P0 | Robotic seed-civilisation game identity | decision | DECISION-10 | Core game direction | FACT | 5 |
| P0 | Robot OS customizable UI/UX | decision | DECISION-11 | Core UX/diegetics direction | FACT/INFERENCE | 4 |
| P0 | PROVIDER-WEDGE-01 | task | TASK-04 | First implementation slice | INFERENCE | 4 |
| P0 | ROBOT-OS-WEDGE-01 | task | TASK-07 | Proof of shared UI shell | INFERENCE | 4 |
| P1 | Verify external facts | verification | VERIFY-01..09 | Prevents stale support claims | VERIFY | 4 |

## Workstream Summaries

See registers in file 04. Main workstreams: repo layout; provider architecture; language/platform floor; renderer plan; Workbench/UI; Robot OS; robotic seed-civilisation; setup/launcher profile selection; data/schema/pack compatibility; preservation.

## Compact Registers for Merge

Decision IDs: DECISION-01, DECISION-02, DECISION-03, DECISION-04, DECISION-05, DECISION-06, DECISION-07, DECISION-08, DECISION-09, DECISION-10, DECISION-11, DECISION-12.
Task IDs: TASK-01, TASK-02, TASK-03, TASK-04, TASK-05, TASK-06, TASK-07, TASK-08, TASK-09, TASK-10, TASK-11, TASK-12, TASK-13, TASK-14.
Constraint IDs: CONSTRAINT-01, CONSTRAINT-02, CONSTRAINT-03, CONSTRAINT-04, CONSTRAINT-05, CONSTRAINT-06, CONSTRAINT-07, CONSTRAINT-08, CONSTRAINT-09, CONSTRAINT-10.
Open question IDs: QUESTION-01, QUESTION-02, QUESTION-03, QUESTION-04, QUESTION-05, QUESTION-06, QUESTION-07, QUESTION-08, QUESTION-09.
Artifact IDs: ARTIFACT-01, ARTIFACT-02, ARTIFACT-03, ARTIFACT-04, ARTIFACT-05, ARTIFACT-06, ARTIFACT-07, ARTIFACT-08, ARTIFACT-09, ARTIFACT-10.
Risk IDs: RISK-01, RISK-02, RISK-03, RISK-04, RISK-05, RISK-06, RISK-07, RISK-08, RISK-09, RISK-10.
Verification IDs: VERIFY-01, VERIFY-02, VERIFY-03, VERIFY-04, VERIFY-05, VERIFY-06, VERIFY-07, VERIFY-08, VERIFY-09.

## Possible Cross-Chat Duplicates

GUI/binary rebuild; AppShell doctrine; repo layout convergence; component matrices; provider architecture; Workbench UI; game design pillars; planet generation; raylib/SDL/Lua usage.

## Possible Cross-Chat Conflicts

Older C89/C++98 baseline; old OpenGL/D3D priority; one universal GUI framework; native GUI-first client; Unreal-first visual architecture; human worker/labour-management MMO framing; vector2d as renderer backend.

## Spec Book Integration Guidance

Feed this chat into chapters on architecture doctrine, source layout, provider/service profiles, rendering, Workbench/UI, Robot OS, game premise, seed-civilisation mechanics, fog-of-war/epistemics, and build/release matrices. External version/support claims must be verified before becoming requirements. Do not merge assistant-only suggestions as final decisions unless user acceptance is clear.

## Aggregator Warnings

Do not reduce this to “use raylib.” Do not reduce Robot OS to a theme. Do not treat old pasted repo reports as current truth without verification. Do not make Workbench a raygui editor. Do not make UI customization unconstrained on official servers.
