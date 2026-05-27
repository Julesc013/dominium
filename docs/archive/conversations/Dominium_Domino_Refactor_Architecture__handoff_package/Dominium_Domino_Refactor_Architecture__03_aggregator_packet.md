# Aggregator Packet — Dominium + Domino Refactor Architecture

## 1. Packet Metadata

- Chat label: Dominium + Domino Refactor Architecture
- Date anchor: 2026-05-27 Australia/Melbourne
- Source scope: THIS CHAT ONLY: visible transcript plus the Context Transfer Packet generated in this same chat; no external repo inspection performed.
- Coverage: Full for visible chat and previous transfer packet; no live repo verification.
- Confidence: 5/5 for chat content, 3/5 for actual codebase implementation state.
- Staleness risk: Medium.
- Merge priority: High.
- Main limitations: Codex application status unknown; exact versions unknown; UI/packs implementation mostly design-level.

## 2. Ultra-Condensed Carry-Forward Capsule

This chat finalized the Dominium + Domino refactor architecture and produced implementation prompts for Codex. Domino is the named deterministic engine under `source/domino`, not `source/engine`, and should not be installed as a separate player-facing runtime. It is linked/bundled into Dominium products, with a developer SDK only as a possible future separate artifact. Dominium is the suite built on Domino and is organized under `source/dominium`.

The final source layout decision is critical: remove `source/dominium/products` and place `common`, `game`, `launcher`, `setup`, and `tools` directly under `source/dominium`. Move existing `source/dominium/products/common` to `source/dominium/common`; move game/launcher/setup subtrees to their corresponding direct subdirs; move `source/dominium/rules` to `source/dominium/game/rules`; move `tools/dominium_modcheck` into `source/dominium/tools/modcheck` as the first DominiumTools tool. Existing Domino source under `source/domino` mostly remains as engine code.

The product model consists of four products: DominiumGame, DominiumLauncher, DominiumSetup, and DominiumTools. The user wants separate product binaries, but not separate demo/server products. Game is a single product/binary with modes: client, listen server, dedicated server, demo/full. Use flags such as `--mode=gui|tui|headless`, `--server=off|listen|dedicated`, `--instance=<id>`, and `--demo`. Demo is represented by demo content/base pack plus instance flag, not by a separate product.

Launcher is the main suite access point. It should enumerate instances, product builds, mods/packs, and actions. It should launch Game and Tools via `actions.json` descriptors from product builds, not hardcoded executable paths. Setup is responsible for portable/per-user/system-wide installation, non-destructive repo import, repair/uninstall, and garbage collection. Tools is an aggregated product; existing `dominium_modcheck` moves into it, while future tools may include world editor, pack editor, save inspector, profile viewer, and instance manager.

The versioning model is central. Core/engine, Game, Launcher, Setup, Tools, formats, protocols, mods, and packs all have independent identities. `SUITE_VERSION := GAME_VERSION`. Products expose `DomProductInfo` through `--introspect-json`, with a `DomCompatProfile` containing versioned capabilities for core, save format, pack format, replay format, net protocol, launcher-game protocol, and tools-game protocol. Compatibility decisions are FULL, LIMITED, READONLY, or INCOMPATIBLE/REFUSE. The base official modpack should match Game version as an official release convention, but the engine should not hardwire equality; compatibility ranges decide validity. DLCs, user mods, official packs, and user packs use independent SemVer.

The install/runtime model is `DOMINIUM_HOME`: a versioned repo of product builds, mods, and packs plus lightweight instances. Instances reference build IDs and mod/pack versions rather than storing copies. Suite installation imports missing builds/mods/packs non-destructively and never overwrites existing identical versions. GC scans instances and deletes only unreferenced repo entries after preview/confirmation.

The packaging model uses explicit OS family and architecture tags. Avoid `x64`; use `x86-64`, `x86-32`, `arm-64`, `wasm-32`, `z80-8`, etc. Suite artifact naming follows `Dominium-Suite-<GAME_VERSION>-<OSFam>-<Arch>.<ext>`. Wrapper scripts should default `dominium` to Launcher, `dom-client` to Game GUI mode, and `dom-server` to Game headless dedicated mode.

This chat also produced several Codex prompts: master refactor, consistency pass, starter-prompt generator, extended-starter generator. The prompts were generated but not confirmed as applied. Future aggregation must preserve that uncertainty.

## 3. Top Carry-Forward Items

| Priority | Item | Type | Related ID | Why it matters | Label | Confidence |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | Flatten source/dominium layout and remove products/ | decision | DECISION-03 | Core refactor target | FACT | 5 |
| 2 | Keep Domino under source/domino; no source/engine | decision | DECISION-01 | Preserves engine identity | FACT | 5 |
| 3 | Do not install Domino runtime globally | decision | DECISION-02 | Avoids version skew | FACT | 5 |
| 4 | Game is one product with modes | decision | DECISION-06 | Avoids client/server/demo fragmentation | FACT | 5 |
| 5 | Launcher is main access point and actions-driven | decision | DECISION-08/15 | Central suite hub | FACT | 5 |
| 6 | DOMINIUM_HOME repo/instances model | architecture | DECISION-11 | Enables multi-version instances | FACT | 5 |
| 7 | Suite version equals Game version | versioning | DECISION-14 | Package/user-facing identity | FACT | 5 |
| 8 | Base mod matching is convention not invariant | versioning | DECISION-18 | Avoids artificial constraints | FACT | 5 |
| 9 | Explicit arch tags like x86-64 | naming | DECISION-19 | Avoids ambiguity | FACT | 5 |
| 10 | Codex prompts generated but application unknown | process | QUESTION-01 | Prevents false assumptions | UNCERTAIN / UNVERIFIED | 5 |

## 4. Workstream Summaries

### WORKSTREAM-01 — Domino engine identity and source boundary

- Objective: Preserve Domino as the named deterministic engine under source/domino, not a generic source/engine directory.
- Current state: Existing repo tree includes source/domino with core, render, sim, system, mod, ui, audio, input and many d*.c modules.
- Desired end state: Domino remains source/domino and include/domino. New compat/platform headers may be added without changing sim semantics.
- Priority: high
- Decisions: DECISION-01, DECISION-02
- Tasks: TASK-03, TASK-04
- Constraints: CONSTRAINT-01, CONSTRAINT-02, CONSTRAINT-04
- Artifacts: ARTIFACT-01, ARTIFACT-09
- Risks: RISK-01, RISK-08
- Open questions: QUESTION-09
- Next action: When refactoring, add compat/platform headers under include/domino but keep existing engine behavior stable.

### WORKSTREAM-02 — Dominium source layout flattening

- Objective: Remove source/dominium/products and place common, game, launcher, setup, and tools directly under source/dominium.
- Current state: Existing repo tree contains source/dominium/products/common, game, launcher, setup and source/dominium/rules.
- Desired end state: source/dominium/common, source/dominium/game, source/dominium/launcher, source/dominium/setup, source/dominium/tools, with rules under source/dominium/game/rules.
- Priority: critical
- Decisions: DECISION-03, DECISION-04
- Tasks: TASK-01, TASK-02
- Constraints: CONSTRAINT-03
- Artifacts: ARTIFACT-09, ARTIFACT-10
- Risks: RISK-02, RISK-03
- Open questions: QUESTION-11
- Next action: Run master refactor prompt or apply equivalent moves manually.

### WORKSTREAM-03 — Dominium product model

- Objective: Maintain four top-level Dominium products: Game, Launcher, Setup, Tools.
- Current state: Existing build targets include dominium_game_cli, dominium_launcher_cli, dominium_setup_cli, dominium_modcheck, dominium_product_common.
- Desired end state: Four product targets: DominiumGame/dominium_game_cli, DominiumLauncher/dominium_launcher_cli, DominiumSetup/dominium_setup_cli, DominiumTools/dominium_tools.
- Priority: critical
- Decisions: DECISION-05
- Tasks: TASK-05, TASK-06
- Constraints: CONSTRAINT-05, CONSTRAINT-07
- Artifacts: ARTIFACT-03, ARTIFACT-09
- Risks: RISK-04
- Open questions: QUESTION-06
- Next action: Normalize target names and product metadata after moving directories.

### WORKSTREAM-04 — Game client/listen/dedicated/demo modes

- Objective: Use one Game product/binary with modes for client, listen server, dedicated server, and demo/full.
- Current state: Existing tree includes game cli, client main, server main, and runtime_display_* implementations.
- Desired end state: dominium_game_cli supports --mode=gui|tui|headless, --server=off|listen|dedicated, --instance, --demo, and routes all startup paths through a unified mode selector.
- Priority: high
- Decisions: DECISION-06, DECISION-07
- Tasks: TASK-07, TASK-08
- Constraints: CONSTRAINT-06, CONSTRAINT-08
- Artifacts: ARTIFACT-09, ARTIFACT-10
- Risks: RISK-05, RISK-06
- Open questions: none
- Next action: Implement/centralize g_runtime/g_modes or equivalent.

### WORKSTREAM-05 — Launcher as main suite hub

- Objective: Make Launcher the main point of access to the entire suite.
- Current state: Existing launcher tree includes CLI/core/gui/model/services/instances/tui and discovery/process-related files.
- Desired end state: Launcher enumerates instances, repo product builds, mods/packs, and actions; it launches Game/Tools/Setup through action descriptors rather than hardcoded paths.
- Priority: high
- Decisions: DECISION-08, DECISION-15
- Tasks: TASK-12, TASK-13
- Constraints: CONSTRAINT-09
- Artifacts: ARTIFACT-06, ARTIFACT-10, ARTIFACT-11
- Risks: RISK-07, RISK-09
- Open questions: none
- Next action: Implement dmn_actions and refactor launcher execution paths.

### WORKSTREAM-06 — Setup/install/package management

- Objective: Support portable, per-user, and system-wide install modes, with non-destructive repo import and GC.
- Current state: Existing setup product tree has CLI/core/model/os stubs and FORMAT_INSTALL_MANIFEST.md.
- Desired end state: Setup distinguishes InstallRoot from DOMINIUM_HOME, imports products/mods/packs non-destructively, registers shortcuts, repairs/uninstalls, and runs GC.
- Priority: high
- Decisions: DECISION-09, DECISION-10
- Tasks: TASK-14, TASK-15, TASK-16
- Constraints: CONSTRAINT-10, CONSTRAINT-11
- Artifacts: ARTIFACT-10, ARTIFACT-11
- Risks: RISK-10, RISK-11
- Open questions: QUESTION-05
- Next action: Codify setup import flow and update docs.

### WORKSTREAM-07 — DOMINIUM_HOME repository and instance system

- Objective: Store multiple versions of products/mods/packs once and let instances reference them.
- Current state: Concept fully specified in chat; current code status unverified.
- Desired end state: DOMINIUM_HOME/repo/products, repo/mods, repo/packs, and instances/<id>/instance.json are used across Launcher/Game/Setup/Tools.
- Priority: critical
- Decisions: DECISION-11, DECISION-12
- Tasks: TASK-09, TASK-10, TASK-11
- Constraints: CONSTRAINT-12, CONSTRAINT-13
- Artifacts: ARTIFACT-05, ARTIFACT-10, ARTIFACT-11
- Risks: RISK-12, RISK-13
- Open questions: QUESTION-03, QUESTION-04, QUESTION-05
- Next action: Implement dmn_paths, dmn_repo, dmn_instance.

### WORKSTREAM-08 — Versioning and compatibility metadata

- Objective: Allow products, formats, protocols, mods, and packs to negotiate compatibility and degrade safely.
- Current state: Concept and headers specified; implementation unverified.
- Desired end state: All products expose DomProductInfo via --introspect-json and build metadata; compatibility decisions use DomCompatProfile.
- Priority: critical
- Decisions: DECISION-13, DECISION-14, DECISION-16
- Tasks: TASK-03, TASK-04, TASK-17
- Constraints: CONSTRAINT-14, CONSTRAINT-15
- Artifacts: ARTIFACT-10, ARTIFACT-11
- Risks: RISK-14
- Open questions: QUESTION-02
- Next action: Add compat/platform headers and product info stubs.

### WORKSTREAM-09 — Mods, packs, base data, DLC, demo content

- Objective: Version and load content packs/mods independently while preserving base-game clarity.
- Current state: Existing data tree has mods/base, mods/examples, mods/space, mods/war, packs/graphics/music/sounds, versions/1.0.0.
- Desired end state: Base official modpack version conventionally matches GAME_VERSION; DLC/user mods/packs are independent and declare compatibility ranges; demo uses demo base pack and instance flag.
- Priority: high
- Decisions: DECISION-17, DECISION-18
- Tasks: TASK-18, TASK-19
- Constraints: CONSTRAINT-16
- Artifacts: ARTIFACT-09, ARTIFACT-11
- Risks: RISK-15
- Open questions: QUESTION-10
- Next action: Audit data manifests and update docs.

### WORKSTREAM-10 — OS family, architecture, packaging, wrappers

- Objective: Use explicit OS/architecture tags and package naming across all suites.
- Current state: Packaging scripts exist under scripts/packaging with wrapper templates.
- Desired end state: Suite artifacts named Dominium-Suite-<GAME_VERSION>-<OSFam>-<Arch>.<ext>; wrappers launch launcher/game modes; arch tags avoid x64 ambiguity.
- Priority: medium
- Decisions: DECISION-19, DECISION-20
- Tasks: TASK-20, TASK-21
- Constraints: CONSTRAINT-17
- Artifacts: ARTIFACT-10, ARTIFACT-11
- Risks: RISK-16
- Open questions: QUESTION-12
- Next action: Update scripts/packaging and docs.

### WORKSTREAM-11 — Backend selection via dsys/dgfx

- Objective: Allow products to choose valid platform and renderer backends through shared Domino APIs.
- Current state: Existing repo has many platform/render backends; unified registry/CLI status unverified.
- Desired end state: Products accept --platform and --renderer, and call Domino backend registries such as dom_sys_select_backend and dom_gfx_select_backend.
- Priority: medium
- Decisions: DECISION-21
- Tasks: TASK-22
- Constraints: CONSTRAINT-18, CONSTRAINT-19
- Artifacts: ARTIFACT-11
- Risks: RISK-17
- Open questions: QUESTION-08
- Next action: Add registries/CLI flags incrementally.

### WORKSTREAM-12 — UI/UX/packs presentation architecture

- Objective: Create a modular UI and packs stack on top of dsys/dgfx with vector-only fallback and optional raster/audio/music packs.
- Current state: Design proposed; implementation state unverified. Existing repo has UI/render files.
- Desired end state: Unified UI toolkit used by launcher, game menus/HUD, setup, and tools; vector baseline always works; raster/sound/music packs optional.
- Priority: medium
- Decisions: DECISION-22
- Tasks: TASK-23
- Constraints: CONSTRAINT-20
- Artifacts: ARTIFACT-02
- Risks: RISK-18
- Open questions: QUESTION-07
- Next action: Keep out of initial refactor except for docs/guardrails; later generate dedicated prompt.

### WORKSTREAM-13 — Codex refactor and consistency prompts

- Objective: Provide Codex with prompts to apply architecture changes and then normalize repo consistency.
- Current state: Multiple prompts have been generated in chat; application status unverified.
- Desired end state: Codex applies refactor, then consistency pass, producing buildable repo aligned with architecture.
- Priority: critical
- Decisions: none
- Tasks: TASK-24, TASK-25
- Constraints: CONSTRAINT-21
- Artifacts: ARTIFACT-10, ARTIFACT-11, ARTIFACT-12, ARTIFACT-13
- Risks: RISK-19
- Open questions: QUESTION-01, QUESTION-06
- Next action: Ask user whether Codex has run or generate a final cleaned prompt package.

### WORKSTREAM-14 — Starter prompts and future chat continuity

- Objective: Generate reusable starter prompts and transfer packets so future ChatGPT conversations can continue without re-explanation.
- Current state: Starter-prompt generator prompts and an initial Context Transfer Packet were produced; current task packages this chat into final downloadable files.
- Desired end state: A shareable per-chat report package plus future starter prompt material.
- Priority: high
- Decisions: none
- Tasks: TASK-26
- Constraints: CONSTRAINT-22, CONSTRAINT-23
- Artifacts: ARTIFACT-14, ARTIFACT-15
- Risks: RISK-20, RISK-21
- Open questions: none
- Next action: Save the ZIP and use it in future aggregation.

## 5. Registers for Merge

### Decision Register

| ID | Decision | Status | Evidence | Rationale | Implications | Workstream | Confidence | Label |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| DECISION-01 | Use `source/domino` as engine source root, not `source/engine`. | decided | User asked; assistant recommended; no later objection. | Domino is a named engine and matches include/domino. | Keeps naming explicit and avoids generic engine ambiguity. | WORKSTREAM-01 | 5 | FACT |
| DECISION-02 | Do not install Domino as a separate end-user runtime product. | decided | User asked bundle vs separate; assistant recommended bundling/static linking; user proceeded. | Avoids DLL/runtime version skew. | Domino is linked/bundled into Dominium products; SDK may be future dev artifact. | WORKSTREAM-01 | 5 | FACT |
| DECISION-03 | Remove `source/dominium/products`. | decided | User explicitly instructed removal. | Simplifies source layout. | Move common/game/launcher/setup/tools directly under source/dominium. | WORKSTREAM-02 | 5 | FACT |
| DECISION-04 | Move Dominium rules into `source/dominium/game/rules`. | decided | Assistant included this in Codex prompts based on existing `source/dominium/rules` and product layout. | Rules are game-specific content/runtime logic. | CMake and includes must update. | WORKSTREAM-02 | 4 | INFERENCE |
| DECISION-05 | Use four top-level Dominium products: Game, Launcher, Setup, Tools. | decided | User wanted separate set of binaries per product. | Clear product boundaries without monolithic executable. | Targets map to those products; Domino is not product. | WORKSTREAM-03 | 5 | FACT |
| DECISION-06 | Use one Game product/binary with client/listen/dedicated modes via flags. | decided | User asked; assistant recommended; prompts encode it. | Avoids version skew and duplicate products. | Existing client/server entrypoints route through central mode logic. | WORKSTREAM-04 | 5 | FACT |
| DECISION-07 | Demo is content/instance policy, not a separate product/binary. | decided | User asked; assistant recommended; later prompts enforce. | Avoids duplicate game binary and save/mod divergence. | Use demo base pack and instance flag. | WORKSTREAM-04 | 5 | FACT |
| DECISION-08 | Launcher is the main access point to the suite. | decided | User explicitly stated this. | Centralizes suite UX. | Wrappers should default to launcher; actions drive execution. | WORKSTREAM-05 | 5 | FACT |
| DECISION-09 | Downloads/installations should be portable out of the box. | decided | User explicitly requested portable by default. | Supports no-install use and movable installs. | Setup must support portable fallback DOMINIUM_HOME. | WORKSTREAM-06 | 5 | FACT |
| DECISION-10 | Support portable, per-user, and system-wide install modes. | decided | User explicitly requested these modes. | Flexible deployment. | Setup must distinguish install modes. | WORKSTREAM-06 | 5 | FACT |
| DECISION-11 | Use DOMINIUM_HOME repo plus lightweight instances. | decided | User asked how to store multiple versions; assistant proposed; no objection. | Dedupes product/mod/pack versions. | Instances reference builds rather than copying suites. | WORKSTREAM-07 | 5 | FACT |
| DECISION-12 | Suite install/import must be non-destructive and not overwrite existing versions. | decided | User explicitly: suite install should not overwrite if already installed. | Preserves multiple versions and old instances. | Setup imports only missing builds/mods/packs. | WORKSTREAM-07 | 5 | FACT |
| DECISION-13 | Use independent versions for core, game, launcher, setup, tools, and protocols. | decided | User explicitly wanted separate version numbers. | Allows arbitrary product combinations and compat negotiation. | Need DomProductInfo and compat metadata. | WORKSTREAM-08 | 5 | FACT |
| DECISION-14 | Suite version equals Game version. | decided | User explicitly corrected assistant: Suite version should be game version. | User-facing clarity. | Package names and suite manifests use GAME_VERSION. | WORKSTREAM-08 | 5 | FACT |
| DECISION-15 | Use actions descriptors for Launcher-to-product/tool execution. | decided | Assistant recommended; user continued with it in prompts. | Avoid hardcoded paths and supports many tools. | Product builds include actions.json; launcher enumerates. | WORKSTREAM-05 | 5 | FACT |
| DECISION-16 | Compatibility outcomes are FULL, LIMITED, READONLY, REFUSE/INCOMPATIBLE. | decided | Assistant proposed; carried into prompts. | Graceful degradation without crash/corruption. | Implement dom_decide_compat. | WORKSTREAM-08 | 4 | FACT |
| DECISION-17 | Base official modpack version should match Game/Suite version as release convention. | decided with nuance | User said base modpack should match game version; later accepted not hardwired. | Clarity for official releases. | Official suite ships matching base pack. | WORKSTREAM-09 | 5 | FACT |
| DECISION-18 | Do not hardwire base version equality into engine validity; use compatibility ranges. | decided | User asked if arbitrary link wise; assistant recommended convention not invariant. | Allows engine-only/data-only hotfixes. | Loader checks compat, not strict equality. | WORKSTREAM-09 | 5 | FACT |
| DECISION-19 | Avoid ambiguous `x64`; use explicit architecture tags like `x86-64`. | decided | User explicitly disliked x64. | Unambiguous multi-arch packages. | Update package names and docs. | WORKSTREAM-10 | 5 | FACT |
| DECISION-20 | Suite artifact naming pattern: Dominium-Suite-<GAME_VERSION>-<OSFam>-<Arch>.<ext>. | decided | Assistant proposed; prompts use it. | Consistent distribution naming. | Update packaging scripts. | WORKSTREAM-10 | 5 | FACT |
| DECISION-21 | All products must use shared dsys/dgfx platform/render APIs, not product-specific APIs. | decided | User asked; assistant answered 'only'. | Avoid duplicate rendering/platform paths. | Products accept backend selection flags and call Domino. | WORKSTREAM-11 | 5 | FACT |
| DECISION-22 | UI/packs stack must keep vector-only fallback and optional raster/audio/music packs. | decided as architecture | Initial user prompt required vector-only baseline and optional packs. | Cross-platform and no-asset baseline. | Future UI implementation must honor this. | WORKSTREAM-12 | 5 | FACT |

### Task Register

| ID | Task | Priority | Urgency | Owner | Dependencies | Inputs | Expected output | Next step | Workstream | Label |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| TASK-01 | Move source/dominium/products/common to source/dominium/common. | high | high | Codex/developer | WORKSTREAM-02 | Current repo tree | Common code in new path | Apply refactor and update CMake/includes | WORKSTREAM-02 | FACT |
| TASK-02 | Move game/launcher/setup directories and rules to new source/dominium layout. | high | high | Codex/developer | TASK-01 | Existing source tree | Flattened source/dominium layout | Run master refactor prompt | WORKSTREAM-02 | FACT |
| TASK-03 | Add include/domino/platform.h and include/domino/compat.h. | high | high | Codex/developer | WORKSTREAM-01 | Specified enum/struct definitions | Public compatibility/platform API | Add headers and adjust includes | WORKSTREAM-08 | FACT |
| TASK-04 | Implement source/domino/compat/compat_core.c. | high | high | Codex/developer | TASK-03 | DomCompatProfile definitions | Range-based compat helpers | Wire into CMake | WORKSTREAM-08 | FACT |
| TASK-05 | Create/normalize product info providers for Game, Launcher, Setup, Tools. | high | high | Codex/developer | TASK-03 | Version macros | dom_get_product_info_* functions | Add stubs and test | WORKSTREAM-03 | FACT |
| TASK-06 | Add --introspect-json to all products. | high | high | Codex/developer | TASK-05 | Product info structs | Valid JSON product metadata output | Implement in CLI mains | WORKSTREAM-08 | FACT |
| TASK-07 | Centralize Game mode parsing and options. | high | medium | Codex/developer | WORKSTREAM-04 | Existing game CLI files | Parsed --mode/--server/--instance/--demo | Add options struct | WORKSTREAM-04 | FACT |
| TASK-08 | Route client/server old entrypoints through unified Game mode selector. | high | medium | Codex/developer | TASK-07 | dom_client_main.c, dom_server_main.c | One startup pathway | Refactor carefully | WORKSTREAM-04 | FACT |
| TASK-09 | Implement dmn_get_dominium_home path discovery. | high | medium | Codex/developer | WORKSTREAM-07 | OS path policy | Central DOMINIUM_HOME API | Create dmn_paths module | WORKSTREAM-07 | FACT |
| TASK-10 | Implement repo API for products/mods/packs. | high | medium | Codex/developer | TASK-09 | Repo layout schema | dmn_repo helpers | Write tests with temp DOMINIUM_HOME | WORKSTREAM-07 | FACT |
| TASK-11 | Implement instance load/save/list API. | high | medium | Codex/developer | TASK-09 | instance.json schema | dmn_instance module | Refactor launcher instances service | WORKSTREAM-07 | FACT |
| TASK-12 | Implement product actions loader. | high | medium | Codex/developer | TASK-10 | actions.json schema | dmn_actions_list functions | Load actions from repo builds | WORKSTREAM-05 | FACT |
| TASK-13 | Refactor Launcher to invoke actions instead of hardcoded executables. | high | medium | Codex/developer | TASK-12 | Launcher process code | Action-driven Launcher | Search hardcoded calls | WORKSTREAM-05 | FACT |
| TASK-14 | Implement Setup non-destructive import into repo. | high | medium | Codex/developer | TASK-10 | InstallRoot model | Import builds/mods/packs if missing | Add dry-run/logging | WORKSTREAM-06 | FACT |
| TASK-15 | Implement Setup portable/per-user/system-wide mode handling. | medium | medium | Codex/developer | TASK-09 | Install mode policy | Setup CLI/model supports modes | Update docs/help | WORKSTREAM-06 | FACT |
| TASK-16 | Implement GC preview/confirm for unused repo entries. | medium | medium | Codex/developer | TASK-10, TASK-11 | Repo and instance APIs | Safe cleanup command | Add preview before deletion | WORKSTREAM-06 | FACT |
| TASK-17 | Centralize version macros in include/dominium/version.h and dominium_version.c. | high | high | Codex/developer | WORKSTREAM-08 | Existing version files | Single version source | Replace hardcoded versions | WORKSTREAM-08 | FACT |
| TASK-18 | Update base and demo content manifests. | medium | medium | Codex/developer | TASK-17 | data/mods and data/versions | Base/demo version/compat aligned | Inspect actual manifests | WORKSTREAM-09 | FACT |
| TASK-19 | Ensure DLC/user mods/packs keep independent versions and compatibility ranges. | medium | medium | Codex/developer | TASK-18 | data/mods/space/war/examples | Manifest consistency | Update docs and validation | WORKSTREAM-09 | FACT |
| TASK-20 | Update packaging artifact naming and arch tags. | medium | medium | Codex/developer | TASK-17 | scripts/packaging | Dominium-Suite-<GAME_VERSION>-<OSFam>-<Arch> names | Edit packaging scripts | WORKSTREAM-10 | FACT |
| TASK-21 | Update wrapper scripts to launch Launcher/client/server modes. | medium | medium | Codex/developer | TASK-07 | scripts/packaging/scripts | dominium/dom-client/dom-server wrappers aligned | Edit .cmd.in/.sh.in | WORKSTREAM-10 | FACT |
| TASK-22 | Add backend selection CLI flags and registry stubs. | medium | medium | Codex/developer | WORKSTREAM-11 | Existing dsys/dgfx init | --platform and --renderer work or fail clearly | Implement minimally | WORKSTREAM-11 | FACT |
| TASK-23 | Defer full UI/packs refactor into dedicated later prompt/spec. | medium | low | Developer/assistant | WORKSTREAM-12 | Initial UI architecture | Separate UI implementation plan | Do not mix into Phase 1 refactor | WORKSTREAM-12 | FACT |
| TASK-24 | Run master refactor prompt in Codex. | critical | high | User/Codex | All decisions | Master refactor prompt | Repo refactored | User should execute or ask assistant to refine prompt | WORKSTREAM-13 | FACT |
| TASK-25 | Run post-refactor consistency prompt after build. | high | high | User/Codex | TASK-24 | Consistency prompt | Stale references removed | Run grep/build/tests | WORKSTREAM-13 | FACT |
| TASK-26 | Save this report package and use it in future aggregation. | high | high | User | Current package | Generated files | Reusable chat-specific report package | Download ZIP | WORKSTREAM-14 | FACT |

### Constraint Register

| ID | Constraint | Type | Hard/soft | Basis | Implication | Risk | Confidence | Label |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| CONSTRAINT-01 | Domino engine code should remain C89-compatible where applicable. | technical | hard | User/project instructions and repeated prompts | Avoid modern C features in engine headers/sources. | medium | 5 | FACT |
| CONSTRAINT-02 | Do not change deterministic simulation semantics. | technical | hard | Repeated Codex guardrails | Refactor must not alter sim algorithms or save/replay semantics. | high | 5 | FACT |
| CONSTRAINT-03 | Use flattened source/dominium layout with no products subdirectory. | structural | hard | User explicit instruction | CMake/includes/docs must migrate. | high | 5 | FACT |
| CONSTRAINT-04 | Domino is not an end-user runtime product. | packaging | hard | Accepted recommendation | No global Domino runtime install tree. | medium | 5 | FACT |
| CONSTRAINT-05 | Dominium has separate product binaries by product. | product | hard | User preference | Do not collapse all products into one executable. | medium | 5 | FACT |
| CONSTRAINT-06 | Game is one product with modes by default. | product | hard | Accepted recommendation | No separate client/server/demo products in primary architecture. | medium | 5 | FACT |
| CONSTRAINT-07 | All products must expose shared version/compat metadata. | technical | hard | Versioning model | Implement DomProductInfo/--introspect-json. | medium | 5 | FACT |
| CONSTRAINT-08 | Demo must be content/instance policy, not separate product. | product/content | hard | Accepted recommendation | Use demo base pack and flags. | medium | 5 | FACT |
| CONSTRAINT-09 | Launcher must be main access point where feasible. | product/UX | hard | User explicit instruction | Wrapper/default desktop entry points to launcher. | medium | 5 | FACT |
| CONSTRAINT-10 | Downloads should be portable out of the box. | distribution | hard | User explicit instruction | Portable DOMINIUM_HOME fallback required. | medium | 5 | FACT |
| CONSTRAINT-11 | Install/import must not overwrite already installed identical versions. | distribution | hard | User explicit instruction | Setup must be non-destructive. | high | 5 | FACT |
| CONSTRAINT-12 | Instances must reference repo versions rather than copying suites. | storage | hard | Repo model discussion | Implement build IDs and mod/pack references. | medium | 5 | FACT |
| CONSTRAINT-13 | Repo supports multiple versions of products, mods, and packs. | storage | hard | User request | No single-current-version assumption. | medium | 5 | FACT |
| CONSTRAINT-14 | Suite version equals Game version. | versioning | hard | User explicit correction | Package names and suite metadata follow GAME_VERSION. | low | 5 | FACT |
| CONSTRAINT-15 | Do not conflate product/core/protocol/format versions. | versioning | hard | User versioning request | Separate macros and compat ranges. | medium | 5 | FACT |
| CONSTRAINT-16 | Base version matching game is convention, not engine validity invariant. | content/versioning | hard | Later decision refinement | Loader must use compat ranges. | medium | 5 | FACT |
| CONSTRAINT-17 | Do not use ambiguous x64 naming in architecture tags. | naming | hard | User explicit preference | Use x86-64 etc. | medium | 5 | FACT |
| CONSTRAINT-18 | All product platform/renderer access must go through dsys/dgfx. | architecture | hard | User prompt and assistant answer | No direct platform drawing/backend bypass. | high | 5 | FACT |
| CONSTRAINT-19 | Setup should use conservative renderer/backend choices by default. | robustness | soft | Assistant recommendation | Favor soft/TUI fallback. | low | 4 | INFERENCE |
| CONSTRAINT-20 | Vector-only UI fallback must remain functional. | UI | hard | Initial thread requirements | No raster asset dependency for functionality. | medium | 5 | FACT |
| CONSTRAINT-21 | Codex prompts must not introduce new external libraries. | implementation | hard | Codex guardrails | Use existing JSON/helpers/manual output. | medium | 5 | FACT |
| CONSTRAINT-22 | Context transfer outputs must label FACT/INFERENCE/UNCERTAIN/PROJECT-CONTEXT. | reporting | hard | User final transfer request | Future aggregation needs provenance labels. | low | 5 | FACT |
| CONSTRAINT-23 | This package is for this chat only. | reporting | hard | User current request | Do not summarize whole project beyond visible chat scope. | low | 5 | FACT |

### Open Questions Register

| ID | Question | Why | Known | Unknown | Resolution | Priority | Workstreams | Label |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| QUESTION-01 | Has Codex applied any generated prompt? | Determines whether next work is implementation, audit, or prompt refinement. | Prompts were generated. | No confirmation of repo changes. | User/repo check. | high | WORKSTREAM-13 | UNCERTAIN / UNVERIFIED |
| QUESTION-02 | What are the current actual version values? | Needed for macros, package names, base manifests. | Existing files include .dominium_build_number and data/versions/1.0.0. | Final GAME/CORE/product versions not established. | Inspect include/dominium/version.h and data manifests. | high | WORKSTREAM-08 | UNCERTAIN / UNVERIFIED |
| QUESTION-03 | Which JSON/TOML parser should repo/instance/actions use? | Implementation needs parser choice. | Existing repo has json.cpp and manifest_io.c. | TOML support unclear. | Inspect code/external libs. | medium | WORKSTREAM-07 | UNCERTAIN / UNVERIFIED |
| QUESTION-04 | Should include/domino/repo.h exist or should repo APIs be dominium-only? | Earlier assistant suggested both; repo seems product-suite specific. | Final prompts lean to dominium/common and include/dominium/instance.h. | Public API boundary unresolved. | User/architecture decision. | medium | WORKSTREAM-07 | UNCERTAIN / UNVERIFIED |
| QUESTION-05 | What exact default DOMINIUM_HOME paths should each OS use? | Affects setup/portable logic. | Examples were discussed. | Final per-OS defaults not confirmed. | User/platform policy decision. | medium | WORKSTREAM-07, WORKSTREAM-06 | UNCERTAIN / UNVERIFIED |
| QUESTION-06 | Which root-level tools should become DominiumTools? | Prevents misclassification of Domino dev tools. | dominium_modcheck should move. | domino_assetc/pack/replay/test status unclear. | User decision or code audit. | medium | WORKSTREAM-03, WORKSTREAM-13 | UNCERTAIN / UNVERIFIED |
| QUESTION-07 | How much UI/packs architecture should be implemented now? | Large scope could derail source refactor. | Architecture specified. | Timing not decided beyond deferral suggestion. | User prioritization. | medium | WORKSTREAM-12 | UNCERTAIN / UNVERIFIED |
| QUESTION-08 | What exact product capability masks by backend are final? | Needed for robust backend selection. | High-level recommendations exist. | Exact code matrix not fixed. | Spec and user review. | low | WORKSTREAM-11 | UNCERTAIN / UNVERIFIED |
| QUESTION-09 | Should private dynamic Domino libs ever be supported? | Affects packaging complexity. | Static linking recommended. | Future constraints unknown. | Reconsider only if concrete need arises. | low | WORKSTREAM-01 | UNCERTAIN / UNVERIFIED |
| QUESTION-10 | What is the final base mod compatibility range syntax? | Needed for manifests. | Suggested game_min/game_max etc. | Exact format may already exist in SPEC_DOMINO_MOD/SPEC_PACKAGES. | Inspect docs/data. | medium | WORKSTREAM-09 | UNCERTAIN / UNVERIFIED |
| QUESTION-11 | What exact current repo status after build artifacts? | Needed before moving files. | User pasted tree at one point. | Repo may have changed after chat. | Fresh file tree. | high | WORKSTREAM-02 | UNCERTAIN / UNVERIFIED |
| QUESTION-12 | Should package generation include ZIP and installer formats immediately? | Affects scripts scope. | Naming scheme decided. | Exact formats per OS not finalized in implementation. | Packaging plan. | low | WORKSTREAM-10 | UNCERTAIN / UNVERIFIED |

### Artifact Ledger

| ID | Artifact | Type | Purpose | Status | Origin | Carry | Notes | Label |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| ARTIFACT-01 | Initial Graphics/UI/UX/Packs Thread Prompt | user prompt | Defined presentation-layer scope and constraints. | source context | User first message in chat | yes | Includes dsys/dgfx/UI/packs requirements. | FACT |
| ARTIFACT-02 | Layered UI/packs architecture response | assistant output | Proposed UI core/style/render/events/fonts/packs design. | generated design | Assistant response | yes | Future UI implementation reference. | FACT |
| ARTIFACT-03 | Product binaries and CLI discussion outputs | assistant outputs | Established separate products and shared CLI patterns. | generated design | Assistant responses | yes | Some earlier one-binary suggestions superseded. | FACT |
| ARTIFACT-04 | Versioning/package scheme discussion outputs | assistant outputs | Established core/product/suite/format/protocol model. | generated design | Assistant responses | yes | Suite=Game correction by user is final. | FACT |
| ARTIFACT-05 | DOMINIUM_HOME repo/instances response | assistant output | Specified shared repo and instances. | generated design | Assistant response | yes | Core carry-forward artifact. | FACT |
| ARTIFACT-06 | Launcher-as-main-access response | assistant output | Defined launcher hub responsibilities. | generated design | Assistant response | yes | Actions/instances/tools integration. | FACT |
| ARTIFACT-07 | Domino runtime placement response | assistant output | Recommended static/internal link and SDK separation. | generated recommendation | Assistant response | yes | Avoid separate runtime. | FACT |
| ARTIFACT-08 | Source/domino vs source/engine response | assistant output | Recommended source/domino and source/dominium. | generated recommendation | Assistant response | yes | Source layout decision. | FACT |
| ARTIFACT-09 | Existing repo directory tree | user-provided file/tree listing | Source for path-specific refactor prompt. | input artifact | User pasted full tree | yes | Must not be treated as current after future changes. | FACT |
| ARTIFACT-10 | Master Refactor Prompt | Codex prompt | Instructed Codex to refactor layout/version/repo/actions/package model. | generated prompt | Assistant response | yes | May be reused/refined. | FACT |
| ARTIFACT-11 | Post-Refactor Consistency Pass Prompt | Codex prompt | Instructed Codex to remove stale refs and align docs/code. | generated prompt | Assistant response | yes | Run after master prompt. | FACT |
| ARTIFACT-12 | Prompt for Codex to generate ChatGPT starter prompt | Codex prompt | Generates concise starter prompt for future chats. | generated prompt | Assistant response | yes | Useful for continuity. | FACT |
| ARTIFACT-13 | Prompt for Codex to generate Extended Master Starter Prompt | Codex prompt | Generates maximal project-wide starter prompt. | generated prompt | Assistant response | yes | Useful for project-wide context. | FACT |
| ARTIFACT-14 | Initial Context Transfer Packet | handoff text | Maximum-fidelity state transfer before packaging. | generated report | Assistant response immediately before current request | yes | This package repairs/normalizes it. | FACT |
| ARTIFACT-15 | Final downloadable report package files | generated files | Current output package. | current artifact | This assistant response | yes | Markdown/YAML/ZIP files. | FACT |

### Risk Register

| ID | Risk | Consequence | Likelihood | Severity | Mitigation | Workstream | Label |
| --- | --- | --- | --- | --- | --- | --- | --- |
| RISK-01 | Accidental engine semantic changes | Breaks determinism/saves/tests | medium | critical | Guardrail: structural refactor only; review sim diffs. | WORKSTREAM-01 | FACT |
| RISK-02 | Old source/dominium/products references remain | Build/docs inconsistency | high | high | Run consistency grep/pass. | WORKSTREAM-02 | FACT |
| RISK-03 | CMake breakage after moves | Build fails | high | high | Update CMake incrementally and run tests. | WORKSTREAM-02 | FACT |
| RISK-04 | Domino treated as product or installed runtime | Version skew/DLL hell | medium | high | No domino runtime targets; link internally. | WORKSTREAM-03 | FACT |
| RISK-05 | Client/server startup paths diverge | Different behavior/version skew | medium | high | Route through shared mode selector. | WORKSTREAM-04 | FACT |
| RISK-06 | Demo becomes separate binary | Duplicate product surface | medium | medium | Enforce content/instance demo model. | WORKSTREAM-04 | FACT |
| RISK-07 | Launcher hardcodes paths | Actions/repo extensibility broken | high | medium | Search and replace with dmn_actions. | WORKSTREAM-05 | FACT |
| RISK-08 | Generic engine naming resurfaces | Docs/code ambiguity | low | medium | Preserve Domino name in source and docs. | WORKSTREAM-01 | FACT |
| RISK-09 | Tool integration becomes ad hoc | Launcher cannot scale to many tools | medium | medium | Actions system; tools registry. | WORKSTREAM-05 | FACT |
| RISK-10 | Setup overwrites existing versions | Breaks old instances | medium | high | Non-destructive import with hashes/build IDs. | WORKSTREAM-06 | FACT |
| RISK-11 | InstallRoot and DOMINIUM_HOME conflated | Portable/user/system modes break | medium | high | Central path APIs and docs. | WORKSTREAM-06 | FACT |
| RISK-12 | Instances copy suites/assets | Disk bloat and version inconsistency | medium | medium | Instances reference repo entries only. | WORKSTREAM-07 | FACT |
| RISK-13 | Repo GC deletes referenced data | Broken instances | low | critical | GC scans instances and requires preview/confirm. | WORKSTREAM-07 | FACT |
| RISK-14 | Compatibility model overpromises never-fail behavior | Unsafe operations may happen | medium | high | Use refuse/read-only when impossible; never corrupt. | WORKSTREAM-08 | FACT |
| RISK-15 | Base version equality treated as hard invariant | Artificial forced bumps and invalid mixes | medium | medium | Use compat ranges; convention only. | WORKSTREAM-09 | FACT |
| RISK-16 | Package names use inconsistent arch tags | User confusion and build matrix ambiguity | medium | medium | Use x86-64 etc.; update scripts. | WORKSTREAM-10 | FACT |
| RISK-17 | Products bypass dsys/dgfx | Duplicate platform/render code | medium | high | Shared backend registries; audit GUI code. | WORKSTREAM-11 | FACT |
| RISK-18 | UI/packs scope bloats initial refactor | Refactor becomes unmanageable | medium | medium | Defer full UI work to later phase. | WORKSTREAM-12 | INFERENCE |
| RISK-19 | Codex prompt too broad causes unsafe changes | Large diff with behavior changes | medium | high | Phase prompts or enforce guardrails/tests. | WORKSTREAM-13 | FACT |
| RISK-20 | Future assistant loses nuance from this chat | Repeated decisions or wrong architecture | medium | high | Use this package and bootstrap prompt. | WORKSTREAM-14 | FACT |
| RISK-21 | Future aggregation treats assistant suggestions as user decisions | Spec book becomes overcommitted | medium | high | Preserve labels and decision evidence. | WORKSTREAM-14 | FACT |

### Verification Queue

| ID | Item | Why | Source/type | Priority | Workstream | Label |
| --- | --- | --- | --- | --- | --- | --- |
| VERIFY-01 | Confirm source/domino still contains existing engine modules after refactor. | Ensure engine not accidentally moved/renamed. | Fresh repo tree/build check. | high | WORKSTREAM-01 | UNCERTAIN / UNVERIFIED |
| VERIFY-02 | Confirm no global Domino runtime target/install path was added. | Avoid rejected runtime model. | CMake/install script inspection. | medium | WORKSTREAM-01 | UNCERTAIN / UNVERIFIED |
| VERIFY-03 | Search for source/dominium/products references after refactor. | Ensure layout consistency. | grep/search. | high | WORKSTREAM-02 | UNCERTAIN / UNVERIFIED |
| VERIFY-04 | Build after directory moves. | Ensure CMake/includes correct. | CMake/Ninja/CTest. | high | WORKSTREAM-02 | UNCERTAIN / UNVERIFIED |
| VERIFY-05 | Confirm four product targets exist and build. | Product model sanity. | CMake target list. | high | WORKSTREAM-03 | UNCERTAIN / UNVERIFIED |
| VERIFY-06 | Confirm dominium_modcheck moved or wrapped under DominiumTools. | Tools product migration. | Tree/CMake check. | medium | WORKSTREAM-03 | UNCERTAIN / UNVERIFIED |
| VERIFY-07 | Run dominium_game_cli --help and check game mode flags. | Game mode CLI. | CLI run. | high | WORKSTREAM-04 | UNCERTAIN / UNVERIFIED |
| VERIFY-08 | Confirm dom_client_main/dom_server_main route through shared runtime mode. | Avoid divergent code paths. | Code review. | medium | WORKSTREAM-04 | UNCERTAIN / UNVERIFIED |
| VERIFY-09 | Search Launcher code for hardcoded executable invocations. | Actions compliance. | grep/code review. | medium | WORKSTREAM-05 | UNCERTAIN / UNVERIFIED |
| VERIFY-10 | Confirm launcher is default wrapper target in packaging scripts. | Main access point. | script inspection. | medium | WORKSTREAM-05 | UNCERTAIN / UNVERIFIED |
| VERIFY-11 | Confirm Setup distinguishes InstallRoot and DOMINIUM_HOME. | Install correctness. | Code/doc review. | medium | WORKSTREAM-06 | UNCERTAIN / UNVERIFIED |
| VERIFY-12 | Confirm setup import is non-destructive. | Old versions safety. | Tests/code review. | high | WORKSTREAM-06 | UNCERTAIN / UNVERIFIED |
| VERIFY-13 | Confirm dmn_get_dominium_home exists and all products use it. | Central paths. | grep/code review. | medium | WORKSTREAM-07 | UNCERTAIN / UNVERIFIED |
| VERIFY-14 | Validate instance.json schema in docs/code/tests. | Instance compatibility. | Schema/test fixture review. | medium | WORKSTREAM-07 | UNCERTAIN / UNVERIFIED |
| VERIFY-15 | Confirm include/domino/compat.h and platform.h compile in C/C++. | API health. | Build/test. | high | WORKSTREAM-08 | UNCERTAIN / UNVERIFIED |
| VERIFY-16 | Run --introspect-json for all products and validate JSON. | Metadata contract. | CLI + JSON validation. | high | WORKSTREAM-08 | UNCERTAIN / UNVERIFIED |
| VERIFY-17 | Inspect data/mods/base manifest for version and compat fields. | Base/game convention. | File review. | medium | WORKSTREAM-09 | UNCERTAIN / UNVERIFIED |
| VERIFY-18 | Confirm no demo product/target exists after refactor. | Demo model compliance. | CMake/tree search. | medium | WORKSTREAM-09 | UNCERTAIN / UNVERIFIED |
| VERIFY-19 | Check package scripts for x64 or old artifact names. | Naming consistency. | grep scripts/docs. | medium | WORKSTREAM-10 | UNCERTAIN / UNVERIFIED |
| VERIFY-20 | Confirm --platform and --renderer behavior is documented/implemented consistently. | Backend selection. | CLI/docs/code review. | medium | WORKSTREAM-11 | UNCERTAIN / UNVERIFIED |
| VERIFY-21 | Audit product GUI paths for direct OS drawing. | UI layering. | Code review. | low | WORKSTREAM-12 | UNCERTAIN / UNVERIFIED |
| VERIFY-22 | Confirm whether Codex prompts have been applied. | Avoid assuming completed work. | User report/repo check. | high | WORKSTREAM-13 | UNCERTAIN / UNVERIFIED |
| VERIFY-23 | Open generated package ZIP and confirm all seven files exist. | Report package integrity. | Manual download/open. | high | WORKSTREAM-14 | UNCERTAIN / UNVERIFIED |

## 6. Possible Cross-Chat Duplicates

- Detailed dsys/dgfx backend architecture.
- UI toolkit and packs system.
- Mod/package manifest formats.
- Deterministic simulation, worldgen, save/TLV formats.
- Launcher protocol and CLI details.
- Packaging/install details.

## 7. Possible Cross-Chat Conflicts

- Other chats may still refer to `source/dominium/products`.
- Other chats may use `source/engine`.
- Other chats may assume separate client/server/demo binaries.
- Other chats may bind Suite version to Core version.
- Other chats may hardwire base pack equality rather than compatibility ranges.
- Other chats may use `x64` naming.

## 8. Spec Book Integration Guidance

Use this chat as source material for chapters on source layout, product model, versioning, repo/instance model, launcher actions, setup/install/GC, package naming, and continuity prompts. Treat UI/packs content as architecture background unless another chat has implementation details. Do not merge illustrative version numbers as final. Confirm exact repo state before turning tasks into completed requirements.

## 9. Aggregator Warnings

Do not treat Codex prompts as executed. Do not treat assistant recommendations as user decisions unless accepted or built upon. Preserve the nuanced base mod decision. Do not erase rejected options. Preserve labels and uncertainty.
