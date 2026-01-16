# Architecture Enforcement Law (ENF0)

This document defines non-negotiable architectural law for the Dominium / Domino repository.
All code, build rules, tools, and CI checks MUST comply.
Violations are merge-blocking.

## Scope

This law applies to all source, build, and tooling content in this repository.
It does not describe gameplay systems and MUST NOT be used to justify gameplay changes.

## A. Ownership Law

Each top-level directory has exclusive ownership and responsibility boundaries.
Cross-boundary behavior is FORBIDDEN unless explicitly allowed by the Dependency Law.

### ENGINE (engine/)

**Allowed responsibilities**
- Core runtime systems, platform abstraction, memory, logging, threading.
- Deterministic simulation primitives, core data structures, and engine modules.
- Render backends and render-facing API surfaces.

**Forbidden responsibilities**
- Game rules, content policy, or gameplay tuning.
- Product UI, launcher behavior, installer behavior.
- Distribution, packaging, or update policy.

**MUST NOT**
- Contain game rules, economy, or domain logic.
- Ship product UI flows or launcher/setup logic.
- Embed product-specific data packs or gameplay tuning tables.

**Rationale**
Keeping engine responsibilities isolated preserves deterministic simulation, enables backend replacement,
and prevents product coupling.

### GAME (game/)

**Allowed responsibilities**
- Authoritative game rules, economy, and domain logic.
- Simulation-specific data tables, tuning, and rule configuration.
- Game-facing APIs that consume engine public interfaces.

**Forbidden responsibilities**
- Engine subsystems, platform abstraction, or renderer backends.
- Product installation or distribution logic.
- Client-only presentation logic and UI frameworks.

**MUST NOT**
- Implement or fork engine modules.
- Branch on graphics APIs or render backends.
- Include engine internal headers from `engine/modules/**`.

**Rationale**
Game logic must be portable across platforms and renderers and must not erode engine boundaries.

### CLIENT (client/)

**Allowed responsibilities**
- Client application assembly, input capture, presentation orchestration.
- Session management and client-side IO that consumes engine/game APIs.
- UI composition that does NOT read authoritative world state.

**Forbidden responsibilities**
- Authoritative simulation ownership.
- Render backend implementations.
- Server-only policy, matchmaking authority, or trust boundaries.

**MUST NOT**
- Implement or host render backends.
- Read authoritative world state directly.
- Include engine internal headers from `engine/modules/**`.

**Rationale**
Client code must remain a thin presentation shell to preserve determinism and server authority.

### SERVER (server/)

**Allowed responsibilities**
- Server runtime assembly and authoritative session orchestration.
- Networking, authoritative simulation hosting, and state replication.
- Server-side services and persistence interfaces.

**Forbidden responsibilities**
- Rendering logic or UI composition.
- Installer, launcher, or setup behavior.
- Client-only interaction flows.

**MUST NOT**
- Include engine internal headers from `engine/modules/**`.
- Implement render backends.
- Embed client-only UI components.

**Rationale**
Server code must be authoritative, deterministic, and independent from client presentation.

### LAUNCHER (launcher/)

**Allowed responsibilities**
- Product discovery, installation, update, launch configuration.
- User-facing UI for product management.
- Integration with schema-driven data for installed state and manifests.

**Forbidden responsibilities**
- Engine or game runtime code.
- Authoritative simulation logic.
- Rendering backend code.

**MUST NOT**
- Depend on `engine/` or `game/` or their internal headers.
- Read or modify authoritative world state.
- Embed runtime simulation code.

**Rationale**
Launcher concerns are operational and must not bind to runtime architecture or determinism rules.

### SETUP (setup/)

**Allowed responsibilities**
- Installation, packaging, system integration, repair, and removal.
- Schema-driven install plans and deterministic setup state.

**Forbidden responsibilities**
- Engine or game runtime code.
- Client or server runtime assembly.
- Rendering backends or UI frameworks beyond setup UI.

**MUST NOT**
- Depend on `engine/` or `game/` or their internal headers.
- Execute or embed authoritative simulation logic.
- Access runtime world state.

**Rationale**
Setup must remain isolated to installation and system policy to keep runtime architecture pure.

### TOOLS (tools/)

**Allowed responsibilities**
- Offline tooling, validators, editors, compilers, and asset pipelines.
- Developer productivity tools that consume engine/game public APIs.

**Forbidden responsibilities**
- Runtime shipping code paths.
- Authoritative simulation ownership in production builds.
- Launcher/setup responsibilities.

**MUST NOT**
- Be a runtime dependency of shipped client/server executables.
- Include engine internal headers from `engine/modules/**`.
- Bypass deterministic data pipelines.

**Rationale**
Tooling must be isolated from runtime to avoid leakage of dev-only behavior into production.

### LIBS (libs/)

**Allowed responsibilities**
- Standalone shared libraries and third-party dependencies.
- Libraries consumed by launcher/setup or tooling where explicitly allowed.

**Forbidden responsibilities**
- Engine runtime or simulation modules.
- Game rules or authoritative logic.
- Renderer backend implementations.

**MUST NOT**
- Become a dependency of `engine/`, `game/`, `client/`, or `server/`.
- Contain game rules or deterministic simulation logic.
- Host build system logic that alters architecture boundaries.

**Rationale**
Shared libraries are leaf dependencies to avoid architectural back-edges and coupling.

### SCHEMA (schema/)

**Allowed responsibilities**
- Data schemas, versioned formats, and validation definitions.
- Canonical data contracts for tools, launcher, and setup.

**Forbidden responsibilities**
- Runtime code, gameplay logic, or engine systems.
- Rendering, platform, or networking implementations.

**MUST NOT**
- Contain compiled runtime code.
- Embed authoritative simulation logic.
- Depend on `engine/` or `game/`.

**Rationale**
Schemas are contracts, not behavior; they must remain stable and tooling-friendly.

## B. Dependency Law

Allowed dependency directions are strict and exclusive:

- `engine/` → (nothing)
- `game/` → `engine/`
- `client/` → `engine/`, `game/`
- `server/` → `engine/`, `game/`
- `tools/` → `engine/`, `game/`
- `launcher/` and `setup/` → `libs/`, `schema/` only

**Forbidden edges**
- Any dependency from `engine/` to any other top-level directory.
- Any dependency from `game/` to `client/`, `server/`, `tools/`, `launcher/`, `setup/`, `libs/`, or `schema/`.
- Any dependency from `client/` or `server/` to `tools/`, `launcher/`, `setup/`, `libs/`, or `schema/`.
- Any dependency from `tools/` to `client/`, `server/`, `launcher/`, `setup/`, `libs/`, or `schema/`.
- Any dependency from `launcher/` or `setup/` to `engine/` or `game/`.
- Any circular dependency between top-level directories.

**Rationale**
Strict dependency direction prevents architectural drift and enforces layering for determinism,
performance, and portability.

## C. Include Path Law

- Only `engine/include/**` is public.
- `engine/modules/**` is internal and FORBIDDEN outside `engine/`.
- `game/` MUST NOT include `engine/modules/**`.
- `client/`, `server/`, and `tools/` MUST NOT include `engine/modules/**`.

**Rationale**
Public include boundaries are the enforcement mechanism for stable APIs and isolation.

## D. Renderer Ownership Law

- All render backends MUST live in `engine/render/**`.
- `client/` MUST NOT own rendering logic or renderer backends.
- `game/` MUST NOT branch on graphics APIs or backend selection.

**Rationale**
Renderer ownership in engine isolates platform variance and keeps game logic renderer-agnostic.

## E. Permanent Prohibitions (FORBIDDEN FOREVER)

The following actions are permanently FORBIDDEN:

- Reintroducing generic `source/` directories at repo root or within top-level domains.
- Collapsing `engine/` into `game/` or merging their responsibilities.
- Making `launcher/` or `setup/` depend on engine internals.
- Adding "temporary exceptions" to determinism rules.
- Adding renderer-specific code outside `engine/render/**`.
- Adding UI code that reads authoritative world state.
