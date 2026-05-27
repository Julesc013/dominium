## 29. Context Transfer Packet for a Future Chat

### 29.1 Ultra-Condensed Bootstrap Brief

This prior chat developed Dominium’s architecture from GUI/binary planning into a broader deterministic simulation operating environment and Interface Operating Layer. The user wanted to know whether the proposed repository, GUI, binary, Workbench, and UI/UX plans were the best possible version, with emphasis on modularity, extensibility, robustness, reliability, future-proofing, data-driven behavior, modding, compatibility, and usefulness.

The key carry-forward idea is that Dominium should not be treated as merely a game or one editor. It should be a deterministic operating environment: engine as kernel-like substrate, contracts as law, runtime services and drivers, game domains as lawful modules, apps as userland product shells, content/packs as mounted data, and proof/replay/release infrastructure around all state changes. The current repo’s post-CONVERGE layout already supports this if interpreted correctly: apps, engine, game, runtime, contracts, content, docs, tests, tools, scripts, cmake, external, release, archive.

The UI/UX conclusion was that the old UI Editor / Tool Editor idea should be superseded by a reusable Interface Operating Layer and a modular Dominium Workbench. The interface layer must provide one command/result/refusal/document/event spine with multiple projections: CLI, TUI, rendered GUI, headless JSON/report mode, and native wrappers later. Workbench is not the platform; Workbench is the largest host/proof surface for that platform. Every serious module should expose the same command through CLI/TUI/rendered/headless projections.

Important caveats: current code is not yet fully data-driven or deeply moddable. Product boot and portable projection proof were partial/blocked in inspected docs. Runtime command graph adoption is partial. Current client code has hard-coded command/help/session/UI/interaction slices. AppShell docs currently say rendered mode is client-only, so rendered Workbench requires a formal law update: rendered mode should be allowed only for products/modules declaring `cap.ui.rendered` and a rendered-shell contract.

### 29.2 Source Hierarchy

1. Direct user statements in this chat.
2. Explicit decisions accepted or strongly endorsed by the user.
3. Current task/register items in this preservation package.
4. Constraint and artifact ledgers.
5. Inferences marked as INFERENCE.
6. Assistant suggestions not yet accepted.
7. General model knowledge only after verification where stale.

### 29.3 Operating Rules for Future Assistants

Preserve FACT / INFERENCE / UNCERTAIN / PROJECT-CONTEXT labels. Do not assume access to this old chat. Do not re-ask answered questions. Verify stale repo/platform/toolchain facts before relying on them. Do not invent missing details. Do not treat tentative suggestions as final decisions. Do not repeat rejected options as if new. Keep artifacts and stable IDs. Use structured outputs when continuing.

### 29.4 Active Workstreams

Active workstreams: repo convergence/ownership, proof spine/build boot, operating environment doctrine, Interface Operating Layer, command dispatch unification, Workbench, no-assets UI floor, packaging/release, platform/render lanes, and domain/modding evolution.

### 29.5 Current Priorities

1. Resolve proof spine blockers.
2. Draft operating environment doctrine.
3. Draft INTERFACE-LAW-00.
4. Update rendered-mode capability law.
5. Unify command dispatch.
6. Define module/document/result/refusal schemas.
7. Build minimal Workbench shell with Validation Dashboard.

### 29.6 Current Open Questions

Rendered-mode law wording, canonical command registry, module descriptor schema, first Workbench module, current repo build/test status, and how other old-chat reports may conflict.

### 29.7 Recommended First Action

Draft `INTERFACE-LAW-00` and `DOMINIUM_OPERATING_ENVIRONMENT.md` as doctrine/spec stubs, then turn them into PR-sized tasks after verifying current repo state.
