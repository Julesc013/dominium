# CONTEXT TRANSFER PACKET — Domino Framework and Open-Source Provider Architecture

## 29. Context Transfer Packet for a Future Chat

### 29.1 Ultra-Condensed Bootstrap Brief

This retired-chat package preserves a conversation about how to build Dominium/Domino using open-source code without losing first-party architecture. The central conclusion is service-first/provider-backed/framework architecture. Domino should be a framework defining stable contracts, provider ABI, profiles, capability/refusal law, conformance tests, deterministic simulation boundaries, and artifact schemas. A Domino engine implementation satisfies those contracts. Dominium is a game implementation consuming the framework. Third-party code such as raylib, SDL2, Lua, raygui, raudio, rlgl, rlsw, ImGui, and other libraries should be providers, not law.

The user strongly liked raylib, SDL2, and Lua. The chat concluded that raylib should be used aggressively as the first visible provider suite: platform/input/render/draw/audio/asset/UI proof. `rlsw` is useful as a raylib software-render provider but should not become the canonical Dominium reference renderer. `rlgl` is useful as an OpenGL-family provider but should not be confused with a future direct `opengl33` provider. `raygui` can bootstrap Workbench/debug UI but should not define UI documents. `raudio` can provide early audio. `raymath` is only for render/editor math, not deterministic simulation. SDL2 remains a first-wave platform/input/audio provider. Lua should be pinned and exposed through `dominium.script.v1` rather than raw Lua ABI.

The chat also classified external projects. SpaceEngine, Celestia, PCGUniverse2, pgg, Luanti, OpenRA, Spring, Mindustry, Freeciv, Endless Sky, Pioneer, Godot, O3DE, and others are useful references by subsystem, but most should not be direct dependencies without license and architecture review.

The user’s larger game vision led to sparse deterministic delegated simulation: infinite address space, finite active set, deterministic cells/islands, event-sourced state, client-contributed work leases, host verification, and CAD-style arbitrary creations compiled into bounded runtime construct/machine/physics/render graphs.

The best next action is `DOMINO-FRAMEWORK-WEDGE-01`: define framework/provider headers, provider manifests, null providers, raylib providers, release profiles, and validators. Verify repo C17/C++17 status, dependency versions, OS floors, and licenses before implementation.

### 29.2 Source Hierarchy

1. Direct user statements in this chat: preference for framework approach, raylib, SDL2, Lua, deterministic sparse game vision, preservation task.
2. Explicit decisions accepted by the user: framework/provider direction, raylib-heavy use with boundaries, service-first model direction.
3. Current task register: sections 17–28 in this package.
4. Constraint register: third-party fencing, deterministic law, license caution.
5. Artifact ledger: uploaded preservation prompt, prior in-chat outputs, repo inspection snippets.
6. Inferences: exact priority of some tasks and design implications.
7. Assistant suggestions not accepted by explicit user action: exact directory trees, wedge names, proposed schemas.
8. General model knowledge and prior web/GitHub checks: must be verified before implementation.

### 29.3 Operating Rules for Future Assistants

- Preserve FACT / INFERENCE / UNCERTAIN / PROJECT-CONTEXT labels.
- Do not assume access to old chats behind pasted links.
- Do not re-ask answered questions unless the answer is materially missing.
- Verify stale facts before relying on them.
- Do not invent missing repo state, licenses, versions, or decisions.
- Do not treat tentative assistant suggestions as final user decisions.
- Do not repeat rejected options such as “make raylib the engine.”
- Preserve artifacts and cite the preservation prompt when relevant.
- Use structured outputs when continuing implementation/spec work.

### 29.4 Active Workstreams

Active workstreams are: open-source bootstrap strategy, Domino Framework split, service-first provider architecture, raylib provider suite, SDL2 provider, Lua provider, repo alignment, reference projects, sparse deterministic delegated simulation, CAD/machine/invention system, and preservation/export.

### 29.5 Current Priorities

1. Verify repo baseline and dependency/platform facts.
2. Define minimal Domino Framework/provider ABI.
3. Add validators and provider manifests.
4. Implement null and raylib provider wedges.
5. Add profile-selected client/server/workbench proofs.
6. Formalize deterministic sparse simulation and CAD graph specs.

### 29.6 Current Open Questions

Main unresolved issues: exact dependency versions, current C17/C++17 repo state, lua54 vs lua55, minimal framework ABI, first provider profile order, deterministic class, license policy for GPL/LGPL/unclear sources, first CAD graph scope, and client-work verification policy.

### 29.7 Recommended First Action

Draft `DOMINO-FRAMEWORK-WEDGE-01` as an implementation-ready PR plan: exact files, minimal C ABI headers, provider manifest schema, null provider, raylib render/input/platform proof, server.null profile, client.raylib profile, and CI boundary validators.
