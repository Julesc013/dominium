# Full Chat Report — Dominium + Domino Refactor Architecture

## 0. Report Metadata

| Field | Value |
|---|---|
| Chat label | Dominium + Domino Refactor Architecture |
| Filesystem label | Dominium_Domino_Refactor_Architecture |
| Generated date anchor | 2026-05-27 Australia/Melbourne |
| Source scope | THIS CHAT ONLY: visible transcript plus the Context Transfer Packet generated in this same chat; no external repo inspection performed. |
| Apparent coverage | Full for the visible chat and the previous Context Transfer Packet; not a live repo audit |
| Extraction confidence | 5/5 for visible chat decisions; 3/5 for actual repo implementation state |
| Staleness risk | Medium |
| Future plans present | Yes |
| Pending tasks present | Yes |
| Artifacts/files/prompts present | Yes |
| Safe for aggregation | Yes, with caveats |
| Main limitations | No repository changes were performed or verified in this chat; Codex application status is unknown; exact current version numbers are not established; some UI/packs architecture is design-level and later-phase |


## 1. Executive Summary

This chat centered on the long-term architecture and implementation plan for the Dominium + Domino project, especially the source-layout refactor, product model, version/package system, launcher/setup/game/tools roles, DOMINIUM_HOME repository model, and continuity prompts for Codex and future ChatGPT sessions. The most important settled point is the division between **Domino** and **Dominium**: Domino is the named deterministic cross-platform engine under `source/domino`, while Dominium is the product suite under `source/dominium`. The user explicitly rejected the `source/dominium/products` intermediate directory and chose the flattened product layout: `source/dominium/common`, `source/dominium/game`, `source/dominium/launcher`, `source/dominium/tools`, and `source/dominium/setup`. Domino should not be renamed to `source/engine`, and it should not be installed as a separate end-user runtime. The accepted direction is that Domino is linked/bundled into Dominium products; a separate Domino SDK may exist later for developers only.

The product model was also clarified. Dominium has four products: Game, Launcher, Setup, and Tools. The user wants separate product binaries rather than one monolithic suite binary. Game is a single product/binary with startup modes for client, listen server, dedicated server, and demo/full. The default recommendation is not to create separate client/server/demo products; instead, use flags such as `--mode=gui|tui|headless`, `--server=off|listen|dedicated`, `--instance=<id>`, and `--demo`. Demo is not a separate product; it is represented by instance flags and demo content/base packs. Launcher is the main user entrypoint for the suite. It should enumerate product builds, instances, mods/packs, and actions, then launch Game and Tools through an actions layer rather than hardcoded executable paths.

A major theme was long-lived versioned installation. The user wanted multiple versions of chosen products, mods, and packs to coexist for many instances without storing full duplicate suites. The resulting model uses `DOMINIUM_HOME`, containing `repo/products`, `repo/mods`, `repo/packs`, and `instances`. Suite installation imports product builds/mods/packs into the repo non-destructively and instances reference those versions. Setup supports portable, per-user, and system-wide modes. Every download should be portable out of the box. Garbage collection must scan instances and only delete unreferenced repo entries.

Versioning decisions are critical. Core/engine, Game, Launcher, Setup, Tools, protocols, formats, mods, and packs all have independent version identities. `SUITE_VERSION` equals `GAME_VERSION`. The base official modpack should conventionally match the Game/Suite version for user clarity, but this should not be hardwired into engine validity; compatibility ranges determine loadability. DLCs, user mods, official packs, and user packs use independent SemVer with compatibility metadata. Products expose `DomProductInfo` via `--introspect-json`, and compatibility uses `DomCompatProfile` with versioned capabilities for core, save format, pack format, replay format, net protocol, launcher-game protocol, and tools-game protocol.

The chat produced several Codex prompts and plans: a master refactor prompt, a post-refactor consistency prompt, a phase plan, a prompt for Codex to generate a concise starter prompt, a prompt for an extended master starter prompt, and then a maximum-fidelity Context Transfer Packet. The current package turns that transfer packet and visible chat context into downloadable reports. The future assistant must not lose the final source layout, one-game-product mode model, Launcher-as-hub model, DOMINIUM_HOME repo/instance architecture, separate versioning model, non-destructive suite import, explicit architecture naming such as `x86-64`, and the fact that none of the generated Codex prompts have been confirmed as applied.


## 2. How to Use This Report

This report covers **only this old chat** and the Context Transfer Packet produced inside it. It is not a live repository audit and not a whole-project source of truth. It preserves decisions, plans, generated prompts, and visible rationale from this chat so that future assistants or aggregators can continue without asking the user to re-explain.

Interpretation rules:

1. Items labelled **FACT** were explicitly stated in the visible chat or directly present in the pasted repo tree.
2. Items labelled **INFERENCE** are reasonable conclusions from the chat but were not explicitly confirmed as final by the user.
3. Items labelled **UNCERTAIN / UNVERIFIED** require repo inspection, user confirmation, or later Codex results.
4. Items labelled **PROJECT-CONTEXT** would come from project-level context outside this transcript. This report primarily uses visible chat context.
5. Direct user statements outrank assistant suggestions.
6. Assistant suggestions become decisions only when the user accepted, incorporated, or did not object after asking for the plan to proceed.
7. Tentative implementation ideas must not be treated as completed repo changes.
8. External-world facts, tool versions, APIs, laws, current platform support, and package formats should be verified before future operational use.
9. This report is designed for later master-spec aggregation; preserve IDs when merging.


## 3. User Preferences Visible in This Chat

### 3.1 Explicit Preferences

| ID | Preference | Source basis | Strength | Implication for future assistants | Risk if misunderstood | Label |
| --- | --- | --- | --- | --- | --- | --- |
| PREFERENCE-01 | Straightforward, strict technical language. | User instructions | high | Use concise, dense, direct responses. | Risk of user dissatisfaction and ambiguity. | FACT |
| PREFERENCE-02 | Correctly cited/fact-checked sources where current external facts are used. | User profile/instructions | high | Search web for current facts when needed; not relevant for this internal package. | Could violate trust if external claims made. | FACT |
| PREFERENCE-03 | Maximum-fidelity transfer and preservation of decisions, rejected options, prompts, files. | Current request | high | Do not compress aggressively. | Loss of context for future chats. | FACT |
| PREFERENCE-06 | Preserve source layout decisions exactly. | User corrected source layout | high | Do not reopen settled source directory choices. | Wasted discussion/repeated options. | FACT |
| PREFERENCE-07 | Use explicit architecture names, no x64 ambiguity. | User statement | medium | Use x86-64 in examples and package names. | Naming inconsistency. | FACT |
| PREFERENCE-08 | No normal summary for transfer tasks. | Current request | high | Produce registers/package, not generic prose summary. | Output fails task. | FACT |

### 3.2 Inferred Preferences

| ID | Preference | Source basis | Strength | Implication for future assistants | Risk if misunderstood | Label |
| --- | --- | --- | --- | --- | --- | --- |
| PREFERENCE-04 | Codex-ready prompts with concrete paths and constraints. | Repeated requests for Codex prompts | high | Generate implementation-oriented prompts. | Prompts too vague for Codex. | INFERENCE |
| PREFERENCE-05 | Long-lived modular architecture over quick hacks. | Repeated emphasis on extensibility/robustness | high | Avoid brittle hardcoded solutions. | Future refactors become harder. | INFERENCE |

### 3.3 Preferences Not Established by This Chat

| Item | Status | Notes |
|---|---|---|
| Exact preferred final UI visual style | Not established | The chat specified architecture, vector/raster fallback, and packability, not final art direction. |
| Exact current version numbers | Not established | Examples such as 2.5.0 and 3.2.1 were illustrative unless found in actual files. |
| Exact OS-specific DOMINIUM_HOME paths | Partially established | Candidate paths were discussed; final path policy needs confirmation or repo inspection. |
| Whether Codex has applied any prompt | Not established | This report assumes prompts were generated, not executed. |


## 4. Complete Topic and Workstream Inventory

| Stable ID | Name | Objective | Current state | Desired end state | Status | Priority | Confidence | Label |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| WORKSTREAM-01 | Domino engine identity and source boundary | Preserve Domino as the named deterministic engine under source/domino, not a generic source/engine directory. | Existing repo tree includes source/domino with core, render, sim, system, mod, ui, audio, input and many d*.c modules. | Domino remains source/domino and include/domino. New compat/platform headers may be added without changing sim semantics. | active | high | 5 | FACT |
| WORKSTREAM-02 | Dominium source layout flattening | Remove source/dominium/products and place common, game, launcher, setup, and tools directly under source/dominium. | Existing repo tree contains source/dominium/products/common, game, launcher, setup and source/dominium/rules. | source/dominium/common, source/dominium/game, source/dominium/launcher, source/dominium/setup, source/dominium/tools, with rules under source/dominium/game/rules. | active | critical | 5 | FACT |
| WORKSTREAM-03 | Dominium product model | Maintain four top-level Dominium products: Game, Launcher, Setup, Tools. | Existing build targets include dominium_game_cli, dominium_launcher_cli, dominium_setup_cli, dominium_modcheck, dominium_product_common. | Four product targets: DominiumGame/dominium_game_cli, DominiumLauncher/dominium_launcher_cli, DominiumSetup/dominium_setup_cli, DominiumTools/dominium_tools. | active | critical | 5 | FACT |
| WORKSTREAM-04 | Game client/listen/dedicated/demo modes | Use one Game product/binary with modes for client, listen server, dedicated server, and demo/full. | Existing tree includes game cli, client main, server main, and runtime_display_* implementations. | dominium_game_cli supports --mode=gui\|tui\|headless, --server=off\|listen\|dedicated, --instance, --demo, and routes all startup paths through a unified mode selector. | active | high | 5 | FACT |
| WORKSTREAM-05 | Launcher as main suite hub | Make Launcher the main point of access to the entire suite. | Existing launcher tree includes CLI/core/gui/model/services/instances/tui and discovery/process-related files. | Launcher enumerates instances, repo product builds, mods/packs, and actions; it launches Game/Tools/Setup through action descriptors rather than hardcoded paths. | active | high | 5 | FACT |
| WORKSTREAM-06 | Setup/install/package management | Support portable, per-user, and system-wide install modes, with non-destructive repo import and GC. | Existing setup product tree has CLI/core/model/os stubs and FORMAT_INSTALL_MANIFEST.md. | Setup distinguishes InstallRoot from DOMINIUM_HOME, imports products/mods/packs non-destructively, registers shortcuts, repairs/uninstalls, and runs GC. | active | high | 5 | FACT |
| WORKSTREAM-07 | DOMINIUM_HOME repository and instance system | Store multiple versions of products/mods/packs once and let instances reference them. | Concept fully specified in chat; current code status unverified. | DOMINIUM_HOME/repo/products, repo/mods, repo/packs, and instances/<id>/instance.json are used across Launcher/Game/Setup/Tools. | active | critical | 5 | FACT |
| WORKSTREAM-08 | Versioning and compatibility metadata | Allow products, formats, protocols, mods, and packs to negotiate compatibility and degrade safely. | Concept and headers specified; implementation unverified. | All products expose DomProductInfo via --introspect-json and build metadata; compatibility decisions use DomCompatProfile. | active | critical | 5 | FACT |
| WORKSTREAM-09 | Mods, packs, base data, DLC, demo content | Version and load content packs/mods independently while preserving base-game clarity. | Existing data tree has mods/base, mods/examples, mods/space, mods/war, packs/graphics/music/sounds, versions/1.0.0. | Base official modpack version conventionally matches GAME_VERSION; DLC/user mods/packs are independent and declare compatibility ranges; demo uses demo base pack and instance flag. | active | high | 5 | FACT |
| WORKSTREAM-10 | OS family, architecture, packaging, wrappers | Use explicit OS/architecture tags and package naming across all suites. | Packaging scripts exist under scripts/packaging with wrapper templates. | Suite artifacts named Dominium-Suite-<GAME_VERSION>-<OSFam>-<Arch>.<ext>; wrappers launch launcher/game modes; arch tags avoid x64 ambiguity. | active | medium | 5 | FACT |
| WORKSTREAM-11 | Backend selection via dsys/dgfx | Allow products to choose valid platform and renderer backends through shared Domino APIs. | Existing repo has many platform/render backends; unified registry/CLI status unverified. | Products accept --platform and --renderer, and call Domino backend registries such as dom_sys_select_backend and dom_gfx_select_backend. | active | medium | 4 | FACT |
| WORKSTREAM-12 | UI/UX/packs presentation architecture | Create a modular UI and packs stack on top of dsys/dgfx with vector-only fallback and optional raster/audio/music packs. | Design proposed; implementation state unverified. Existing repo has UI/render files. | Unified UI toolkit used by launcher, game menus/HUD, setup, and tools; vector baseline always works; raster/sound/music packs optional. | active but later-phase | medium | 4 | FACT |
| WORKSTREAM-13 | Codex refactor and consistency prompts | Provide Codex with prompts to apply architecture changes and then normalize repo consistency. | Multiple prompts have been generated in chat; application status unverified. | Codex applies refactor, then consistency pass, producing buildable repo aligned with architecture. | active | critical | 5 | FACT |
| WORKSTREAM-14 | Starter prompts and future chat continuity | Generate reusable starter prompts and transfer packets so future ChatGPT conversations can continue without re-explanation. | Starter-prompt generator prompts and an initial Context Transfer Packet were produced; current task packages this chat into final downloadable files. | A shareable per-chat report package plus future starter prompt material. | active | high | 5 | FACT |

## 5. Detailed Workstream State

### WORKSTREAM-01 — Domino engine identity and source boundary

- Label: FACT
- Objective: Preserve Domino as the named deterministic engine under source/domino, not a generic source/engine directory.
- Background: User asked whether to use source/Domino and source/dominium or source/engine for Domino; assistant recommended source/domino and user did not object.
- Current state: Existing repo tree includes source/domino with core, render, sim, system, mod, ui, audio, input and many d*.c modules.
- Desired end state: Domino remains source/domino and include/domino. New compat/platform headers may be added without changing sim semantics.
- Importance: Prevents ambiguous engine naming and aligns source tree with include/domino.
- Decisions made: DECISION-01, DECISION-02
- Decisions pending: see open questions linked to this workstream
- Pending tasks: TASK-03, TASK-04
- Constraints: CONSTRAINT-01, CONSTRAINT-02, CONSTRAINT-04
- Dependencies: none recorded
- Timeline / sequencing: Settled after discussion of runtime bundling and source naming.
- Blockers: none recorded
- Risks: RISK-01, RISK-08
- Artifacts: ARTIFACT-01, ARTIFACT-09
- Success criteria: source/domino remains engine root, include/domino remains public engine header root, No global runtime Domino install is introduced
- Recommended next action: When refactoring, add compat/platform headers under include/domino but keep existing engine behavior stable.
- Verification needed: VERIFY-01, VERIFY-02
- Confidence: 5/5
- Carry-forward priority: critical

### WORKSTREAM-02 — Dominium source layout flattening

- Label: FACT
- Objective: Remove source/dominium/products and place common, game, launcher, setup, and tools directly under source/dominium.
- Background: User explicitly stated: 'Remove the products subdirectory under dominium, and just put game, launcher, setup, and tools subdirectories in dominium.'
- Current state: Existing repo tree contains source/dominium/products/common, game, launcher, setup and source/dominium/rules.
- Desired end state: source/dominium/common, source/dominium/game, source/dominium/launcher, source/dominium/setup, source/dominium/tools, with rules under source/dominium/game/rules.
- Importance: Simplifies product layout and avoids artificial product nesting.
- Decisions made: DECISION-03, DECISION-04
- Decisions pending: see open questions linked to this workstream
- Pending tasks: TASK-01, TASK-02
- Constraints: CONSTRAINT-03
- Dependencies: Existing repo tree
- Timeline / sequencing: Chosen after several earlier product-layout proposals.
- Blockers: Need Codex/refactor to update CMake and includes.
- Risks: RISK-02, RISK-03
- Artifacts: ARTIFACT-09, ARTIFACT-10
- Success criteria: No source/dominium/products references remain in primary build, CMake targets build from new paths, Docs use new layout
- Recommended next action: Run master refactor prompt or apply equivalent moves manually.
- Verification needed: VERIFY-03, VERIFY-04
- Confidence: 5/5
- Carry-forward priority: critical

### WORKSTREAM-03 — Dominium product model

- Label: FACT
- Objective: Maintain four top-level Dominium products: Game, Launcher, Setup, Tools.
- Background: User wanted separate binaries per product rather than one monolithic suite executable.
- Current state: Existing build targets include dominium_game_cli, dominium_launcher_cli, dominium_setup_cli, dominium_modcheck, dominium_product_common.
- Desired end state: Four product targets: DominiumGame/dominium_game_cli, DominiumLauncher/dominium_launcher_cli, DominiumSetup/dominium_setup_cli, DominiumTools/dominium_tools.
- Importance: Preserves product boundaries while sharing Domino engine and Dominium common code.
- Decisions made: DECISION-05
- Decisions pending: see open questions linked to this workstream
- Pending tasks: TASK-05, TASK-06
- Constraints: CONSTRAINT-05, CONSTRAINT-07
- Dependencies: WORKSTREAM-02
- Timeline / sequencing: Evolved from initial one-binary-per-platform discussion to user preference for separate product binaries.
- Blockers: none recorded
- Risks: RISK-04
- Artifacts: ARTIFACT-03, ARTIFACT-09
- Success criteria: Products are separate build targets, All products expose product info, Domino is not treated as product
- Recommended next action: Normalize target names and product metadata after moving directories.
- Verification needed: VERIFY-05, VERIFY-06
- Confidence: 5/5
- Carry-forward priority: critical

### WORKSTREAM-04 — Game client/listen/dedicated/demo modes

- Label: FACT
- Objective: Use one Game product/binary with modes for client, listen server, dedicated server, and demo/full.
- Background: User asked whether client/server should be separate binaries or startup flags; assistant recommended startup flags.
- Current state: Existing tree includes game cli, client main, server main, and runtime_display_* implementations.
- Desired end state: dominium_game_cli supports --mode=gui|tui|headless, --server=off|listen|dedicated, --instance, --demo, and routes all startup paths through a unified mode selector.
- Importance: Avoids client/server version skew and duplicate product surfaces.
- Decisions made: DECISION-06, DECISION-07
- Decisions pending: see open questions linked to this workstream
- Pending tasks: TASK-07, TASK-08
- Constraints: CONSTRAINT-06, CONSTRAINT-08
- Dependencies: WORKSTREAM-02, WORKSTREAM-03
- Timeline / sequencing: Settled after source layout discussion.
- Blockers: Need inspect existing main functions to route without breaking behavior.
- Risks: RISK-05, RISK-06
- Artifacts: ARTIFACT-09, ARTIFACT-10
- Success criteria: No separate demo product, No separate server product by default, Old client/server mains route through shared mode code
- Recommended next action: Implement/centralize g_runtime/g_modes or equivalent.
- Verification needed: VERIFY-07, VERIFY-08
- Confidence: 5/5
- Carry-forward priority: critical

### WORKSTREAM-05 — Launcher as main suite hub

- Label: FACT
- Objective: Make Launcher the main point of access to the entire suite.
- Background: User explicitly stated the launcher should be the main point of access to the entire suite.
- Current state: Existing launcher tree includes CLI/core/gui/model/services/instances/tui and discovery/process-related files.
- Desired end state: Launcher enumerates instances, repo product builds, mods/packs, and actions; it launches Game/Tools/Setup through action descriptors rather than hardcoded paths.
- Importance: Centralizes product/version/instance/mod/tool workflow.
- Decisions made: DECISION-08, DECISION-15
- Decisions pending: see open questions linked to this workstream
- Pending tasks: TASK-12, TASK-13
- Constraints: CONSTRAINT-09
- Dependencies: WORKSTREAM-07, WORKSTREAM-08
- Timeline / sequencing: Added after architecture naming and suite extension discussion.
- Blockers: Actions and repo/instance model need implementation.
- Risks: RISK-07, RISK-09
- Artifacts: ARTIFACT-06, ARTIFACT-10, ARTIFACT-11
- Success criteria: Launcher starts by default from wrapper scripts, Launcher menus are action-driven, Launcher can diagnose broken instances
- Recommended next action: Implement dmn_actions and refactor launcher execution paths.
- Verification needed: VERIFY-09, VERIFY-10
- Confidence: 5/5
- Carry-forward priority: critical

### WORKSTREAM-06 — Setup/install/package management

- Label: FACT
- Objective: Support portable, per-user, and system-wide install modes, with non-destructive repo import and GC.
- Background: User wanted all downloads portable out of the box and optional install to portable/per-user/system-wide.
- Current state: Existing setup product tree has CLI/core/model/os stubs and FORMAT_INSTALL_MANIFEST.md.
- Desired end state: Setup distinguishes InstallRoot from DOMINIUM_HOME, imports products/mods/packs non-destructively, registers shortcuts, repairs/uninstalls, and runs GC.
- Importance: Enables multi-version instances without duplicate suite installs.
- Decisions made: DECISION-09, DECISION-10
- Decisions pending: see open questions linked to this workstream
- Pending tasks: TASK-14, TASK-15, TASK-16
- Constraints: CONSTRAINT-10, CONSTRAINT-11
- Dependencies: WORKSTREAM-07, WORKSTREAM-11
- Timeline / sequencing: Discussed before and after repo/instances.
- Blockers: Need repo API and install manifest schema.
- Risks: RISK-10, RISK-11
- Artifacts: ARTIFACT-10, ARTIFACT-11
- Success criteria: InstallRoot/DOMINIUM_HOME separated, Import does not overwrite identical builds, GC preview/confirm available
- Recommended next action: Codify setup import flow and update docs.
- Verification needed: VERIFY-11, VERIFY-12
- Confidence: 5/5
- Carry-forward priority: high

### WORKSTREAM-07 — DOMINIUM_HOME repository and instance system

- Label: FACT
- Objective: Store multiple versions of products/mods/packs once and let instances reference them.
- Background: User asked how to store multiple different versions of chosen products for many instances without storing whole suites.
- Current state: Concept fully specified in chat; current code status unverified.
- Desired end state: DOMINIUM_HOME/repo/products, repo/mods, repo/packs, and instances/<id>/instance.json are used across Launcher/Game/Setup/Tools.
- Importance: Core mechanism for long-lived versioned installs and safe arbitrary combinations.
- Decisions made: DECISION-11, DECISION-12
- Decisions pending: see open questions linked to this workstream
- Pending tasks: TASK-09, TASK-10, TASK-11
- Constraints: CONSTRAINT-12, CONSTRAINT-13
- Dependencies: WORKSTREAM-08
- Timeline / sequencing: Introduced after suite/install discussion.
- Blockers: Need code implementation and JSON schema parsing.
- Risks: RISK-12, RISK-13
- Artifacts: ARTIFACT-05, ARTIFACT-10, ARTIFACT-11
- Success criteria: Instances reference build IDs and mod/pack versions, No full suite copies per instance, Repo GC safe
- Recommended next action: Implement dmn_paths, dmn_repo, dmn_instance.
- Verification needed: VERIFY-13, VERIFY-14
- Confidence: 5/5
- Carry-forward priority: critical

### WORKSTREAM-08 — Versioning and compatibility metadata

- Label: FACT
- Objective: Allow products, formats, protocols, mods, and packs to negotiate compatibility and degrade safely.
- Background: User wanted separate version numbers for core/game/launcher/setup/tools/protocols and arbitrary combinations that gracefully degrade.
- Current state: Concept and headers specified; implementation unverified.
- Desired end state: All products expose DomProductInfo via --introspect-json and build metadata; compatibility decisions use DomCompatProfile.
- Importance: Prevents crashes/corruption across mixed product versions.
- Decisions made: DECISION-13, DECISION-14, DECISION-16
- Decisions pending: see open questions linked to this workstream
- Pending tasks: TASK-03, TASK-04, TASK-17
- Constraints: CONSTRAINT-14, CONSTRAINT-15
- Dependencies: WORKSTREAM-01, WORKSTREAM-03
- Timeline / sequencing: Developed through product/package/version discussions.
- Blockers: Need actual version constants and format/protocol values from repo.
- Risks: RISK-14
- Artifacts: ARTIFACT-10, ARTIFACT-11
- Success criteria: Product info valid JSON, Compat ranges defined, Incompatibilities refuse safely
- Recommended next action: Add compat/platform headers and product info stubs.
- Verification needed: VERIFY-15, VERIFY-16
- Confidence: 5/5
- Carry-forward priority: critical

### WORKSTREAM-09 — Mods, packs, base data, DLC, demo content

- Label: FACT
- Objective: Version and load content packs/mods independently while preserving base-game clarity.
- Background: User discussed base modpack matching game version but not DLC/user mods/packs; later asked whether to hardwire the link.
- Current state: Existing data tree has mods/base, mods/examples, mods/space, mods/war, packs/graphics/music/sounds, versions/1.0.0.
- Desired end state: Base official modpack version conventionally matches GAME_VERSION; DLC/user mods/packs are independent and declare compatibility ranges; demo uses demo base pack and instance flag.
- Importance: Balances user-facing clarity with long-term content flexibility.
- Decisions made: DECISION-17, DECISION-18
- Decisions pending: see open questions linked to this workstream
- Pending tasks: TASK-18, TASK-19
- Constraints: CONSTRAINT-16
- Dependencies: WORKSTREAM-07, WORKSTREAM-08
- Timeline / sequencing: Settled after versioning and repo discussions.
- Blockers: Need inspect actual data manifests.
- Risks: RISK-15
- Artifacts: ARTIFACT-09, ARTIFACT-11
- Success criteria: Base manifest version aligned, DLC/user mods independent, Demo represented as content
- Recommended next action: Audit data manifests and update docs.
- Verification needed: VERIFY-17, VERIFY-18
- Confidence: 5/5
- Carry-forward priority: high

### WORKSTREAM-10 — OS family, architecture, packaging, wrappers

- Label: FACT
- Objective: Use explicit OS/architecture tags and package naming across all suites.
- Background: User asked to define names for each architecture and disliked x64 ambiguity.
- Current state: Packaging scripts exist under scripts/packaging with wrapper templates.
- Desired end state: Suite artifacts named Dominium-Suite-<GAME_VERSION>-<OSFam>-<Arch>.<ext>; wrappers launch launcher/game modes; arch tags avoid x64 ambiguity.
- Importance: Prevents package ambiguity and improves cross-platform matrix clarity.
- Decisions made: DECISION-19, DECISION-20
- Decisions pending: see open questions linked to this workstream
- Pending tasks: TASK-20, TASK-21
- Constraints: CONSTRAINT-17
- Dependencies: WORKSTREAM-08
- Timeline / sequencing: After OS suite extension and launcher access discussions.
- Blockers: Need update packaging scripts.
- Risks: RISK-16
- Artifacts: ARTIFACT-10, ARTIFACT-11
- Success criteria: No x64 in package names, Wrapper scripts call correct product/actions
- Recommended next action: Update scripts/packaging and docs.
- Verification needed: VERIFY-19
- Confidence: 5/5
- Carry-forward priority: medium

### WORKSTREAM-11 — Backend selection via dsys/dgfx

- Label: FACT
- Objective: Allow products to choose valid platform and renderer backends through shared Domino APIs.
- Background: User asked whether binaries can use shared platform/renderer APIs and support variety of combinations.
- Current state: Existing repo has many platform/render backends; unified registry/CLI status unverified.
- Desired end state: Products accept --platform and --renderer, and call Domino backend registries such as dom_sys_select_backend and dom_gfx_select_backend.
- Importance: Avoids product-specific platform/render code and maximizes backend flexibility.
- Decisions made: DECISION-21
- Decisions pending: see open questions linked to this workstream
- Pending tasks: TASK-22
- Constraints: CONSTRAINT-18, CONSTRAINT-19
- Dependencies: WORKSTREAM-01
- Timeline / sequencing: Discussed before product/version packaging.
- Blockers: Need inspect existing backend init APIs.
- Risks: RISK-17
- Artifacts: ARTIFACT-11
- Success criteria: No product bypasses dsys/dgfx, CLI backend flags documented
- Recommended next action: Add registries/CLI flags incrementally.
- Verification needed: VERIFY-20
- Confidence: 4/5
- Carry-forward priority: medium

### WORKSTREAM-12 — UI/UX/packs presentation architecture

- Label: FACT
- Objective: Create a modular UI and packs stack on top of dsys/dgfx with vector-only fallback and optional raster/audio/music packs.
- Background: Initial thread prompt was explicitly graphics/UI/UX/packs architecture.
- Current state: Design proposed; implementation state unverified. Existing repo has UI/render files.
- Desired end state: Unified UI toolkit used by launcher, game menus/HUD, setup, and tools; vector baseline always works; raster/sound/music packs optional.
- Importance: Prevents duplicate product UI systems and supports cross-era hardware.
- Decisions made: DECISION-22
- Decisions pending: see open questions linked to this workstream
- Pending tasks: TASK-23
- Constraints: CONSTRAINT-20
- Dependencies: WORKSTREAM-01, WORKSTREAM-11
- Timeline / sequencing: First major topic, then deferred from source refactor.
- Blockers: Large scope; needs separate implementation phase.
- Risks: RISK-18
- Artifacts: ARTIFACT-02
- Success criteria: All UI through dgfx, vector fallback, packs optional
- Recommended next action: Keep out of initial refactor except for docs/guardrails; later generate dedicated prompt.
- Verification needed: VERIFY-21
- Confidence: 4/5
- Carry-forward priority: medium

### WORKSTREAM-13 — Codex refactor and consistency prompts

- Label: FACT
- Objective: Provide Codex with prompts to apply architecture changes and then normalize repo consistency.
- Background: User repeatedly asked for Codex prompts, including master refactor, consistency pass, and starter prompt generation.
- Current state: Multiple prompts have been generated in chat; application status unverified.
- Desired end state: Codex applies refactor, then consistency pass, producing buildable repo aligned with architecture.
- Importance: Codex is intended implementation partner while ChatGPT continues architecture/spec work.
- Decisions made: none recorded
- Decisions pending: see open questions linked to this workstream
- Pending tasks: TASK-24, TASK-25
- Constraints: CONSTRAINT-21
- Dependencies: All architecture decisions
- Timeline / sequencing: Late thread outputs.
- Blockers: Need user to run Codex and report results.
- Risks: RISK-19
- Artifacts: ARTIFACT-10, ARTIFACT-11, ARTIFACT-12, ARTIFACT-13
- Success criteria: Prompts produce actual repo changes, Build passes, Docs consistent
- Recommended next action: Ask user whether Codex has run or generate a final cleaned prompt package.
- Verification needed: VERIFY-22
- Confidence: 5/5
- Carry-forward priority: critical

### WORKSTREAM-14 — Starter prompts and future chat continuity

- Label: FACT
- Objective: Generate reusable starter prompts and transfer packets so future ChatGPT conversations can continue without re-explanation.
- Background: User asked for maximum-fidelity transfer and now asks to convert it into a downloadable report package.
- Current state: Starter-prompt generator prompts and an initial Context Transfer Packet were produced; current task packages this chat into final downloadable files.
- Desired end state: A shareable per-chat report package plus future starter prompt material.
- Importance: Prevents loss of decisions, prompts, artifacts, and rationale across chats.
- Decisions made: none recorded
- Decisions pending: see open questions linked to this workstream
- Pending tasks: TASK-26
- Constraints: CONSTRAINT-22, CONSTRAINT-23
- Dependencies: Prior transfer packet
- Timeline / sequencing: Final part of retired chat.
- Blockers: none recorded
- Risks: RISK-20, RISK-21
- Artifacts: ARTIFACT-14, ARTIFACT-15
- Success criteria: Markdown/YAML/ZIP files created, Safe for aggregation with caveats
- Recommended next action: Save the ZIP and use it in future aggregation.
- Verification needed: VERIFY-23
- Confidence: 5/5
- Carry-forward priority: critical


## 6. Chronological Timeline

| Sequence | Event / topic | What changed or was decided | Why it mattered | Current relevance | Confidence |
| --- | --- | --- | --- | --- | --- |
| SEQ-01 | User opened thread as Dominium Graphics/UI/UX/Packs Architecture Thread. | Established presentation-layer scope and assumptions. | Set constraints for UI/packs and dsys/dgfx layering. | historical foundation | 5 |
| SEQ-02 | Assistant proposed layered presentation stack. | Introduced dsys→dgfx→ui_core/style/fonts/events/render/packs→domain UIs. | Became future UI/packs reference. | future phase | 5 |
| SEQ-03 | User asked about merging headless/CLI/TUI/GUI modes. | Assistant recommended unified mode model with backend flags. | Informed later product CLI design. | active | 5 |
| SEQ-04 | User asked what binaries to compile. | Assistant initially recommended minimal binaries and wrappers. | Later superseded by separate product binaries. | superseded | 5 |
| SEQ-05 | User wanted separate set of binaries per product. | Established Game/Launcher/Setup/Tools products. | Core product model. | active | 5 |
| SEQ-06 | User asked whether all binaries should use shared platform/renderer APIs. | Decision: all products use dsys/dgfx only; per-product capability masks. | Backend architecture. | active | 5 |
| SEQ-07 | User asked about packaging/version naming. | Assistant proposed support tiers, install layout, config, diagnostics, versions. | Foundation for later version/package decisions. | active | 5 |
| SEQ-08 | User wanted separate versions for core/product/protocols. | DomProductInfo/compat model developed. | Major compatibility model. | active | 5 |
| SEQ-09 | User corrected Suite version to Game version. | Suite version final decision changed from Core to Game. | High-impact naming decision. | active | 5 |
| SEQ-10 | User discussed base modpack version matching game but not DLC/packs. | Base/content versioning model refined. | Content model. | active | 5 |
| SEQ-11 | User asked if hard link between game and base data was wise. | Assistant recommended release convention not engine invariant. | Preserved flexibility. | active | 5 |
| SEQ-12 | User asked what else to nail down. | Assistant listed install manifest, paths, config, ABI policy, update, logging, backend tiers, localization, mod IDs, security, determinism. | Roadmap broadened. | background | 5 |
| SEQ-13 | User asked storing many product versions without whole suite copies. | DOMINIUM_HOME repo/instances model introduced. | Core install/runtime model. | active | 5 |
| SEQ-14 | User asked to extend suites to OS families. | OS family and DOMINIUM_HOME per OS discussed. | Cross-platform packaging model. | active | 5 |
| SEQ-15 | User wanted architecture names and Launcher main access point. | Explicit architecture tags and Launcher hub model defined. | Naming and UX model. | active | 5 |
| SEQ-16 | User asked about more tools/products/demo. | Assistant recommended Tools as action subtools and demo as Game content/mode. | Tool/demo model. | active | 5 |
| SEQ-17 | User asked to review whole system for extensibility. | Assistant recommended component roles, build IDs, actions-first, schema versions, atomic updates/tests. | Robustness improvements. | background/active | 5 |
| SEQ-18 | User asked proposed directory/executables. | Assistant summarized source/disk layout and product binaries. | Pre-final layout. | superseded partially | 5 |
| SEQ-19 | User chose flattened source/dominium layout and asked client/server recommendation. | Final source layout and one Game binary recommendation. | Critical final choices. | active | 5 |
| SEQ-20 | User asked Domino bundling/install placement. | Assistant recommended static/internal link and SDK separation. | Runtime/SDK decision. | active | 5 |
| SEQ-21 | User asked source/domino vs source/engine. | Assistant recommended source/domino and source/dominium. | Source naming final. | active | 5 |
| SEQ-22 | User asked final directory/package/version systems. | Assistant consolidated final spec. | Set stage for Codex prompt. | active | 5 |
| SEQ-23 | User said they would provide existing repo tree and asked plan for prompt. | Assistant planned Codex prompt contents. | Implementation preparation. | active | 5 |
| SEQ-24 | User pasted full repo tree. | Provided concrete existing files/dirs for refactor prompt. | Vital source artifact. | active | 5 |
| SEQ-25 | Assistant generated Codex master refactor prompt. | Created implementation prompt. | Artifact to carry forward. | active | 5 |
| SEQ-26 | User asked what Codex wasn't aware of. | Assistant audited missing architecture pieces. | Gap list for prompt extension. | active | 5 |
| SEQ-27 | User asked phase plan from scratch. | Assistant produced phased roadmap. | Implementation sequencing. | active | 5 |
| SEQ-28 | User asked to merge into one big refactoring prompt. | Assistant generated combined master prompt. | Codex implementation artifact. | active | 5 |
| SEQ-29 | User asked Codex consistency pass prompt. | Assistant generated post-refactor consistency prompt. | Quality-control artifact. | active | 5 |
| SEQ-30 | User asked prompt for Codex to generate starter prompt. | Assistant generated starter-prompt generator prompt. | Continuity artifact. | active | 5 |
| SEQ-31 | User asked extended starter prompt generator. | Assistant generated extended master starter prompt generator prompt. | Continuity artifact. | active | 5 |
| SEQ-32 | User requested Context Transfer Packet. | Assistant produced maximum-fidelity packet. | Precursor to current package. | active | 5 |
| SEQ-33 | User requested final downloadable report package. | Current task creates Markdown/YAML/ZIP package. | Final packaging step. | active | 5 |

## 7. Decisions

| ID | Decision | Status | Evidence / basis | Rationale | Implications | Related workstream | Confidence | Label |
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

### Highest-impact decisions

The highest-impact decisions are DECISION-03 (flatten `source/dominium`), DECISION-06 (one Game product with modes), DECISION-08 (Launcher as main suite hub), DECISION-11 (DOMINIUM_HOME repo/instances), DECISION-13/14 (separate versions and Suite=Game), and DECISION-02 (no separate Domino runtime). These decisions define the refactor shape and should not be reopened unless the user explicitly requests a redesign.


## 8. Pending Tasks and Next Actions

| ID | Task | Priority | Urgency | Owner | Dependencies | Inputs needed | Expected output | Recommended next step | Related workstream | Label |
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

### 8.1 Recommended Task Order

1. TASK-24 — Run or finalize the master Codex refactor prompt.
2. TASK-01/TASK-02 — Move the source layout and update CMake/includes.
3. TASK-03/TASK-04/TASK-17 — Add platform/compat/version foundations.
4. TASK-05/TASK-06 — Add product metadata and `--introspect-json`.
5. TASK-07/TASK-08 — Unify Game modes.
6. TASK-09/TASK-10/TASK-11 — Implement DOMINIUM_HOME/repo/instances.
7. TASK-12/TASK-13 — Implement actions and refactor Launcher.
8. TASK-14/TASK-15/TASK-16 — Implement Setup import/install modes/GC.
9. TASK-18/TASK-19 — Update content manifests.
10. TASK-20/TASK-21/TASK-22 — Update packaging/backend selection.
11. TASK-25 — Run consistency pass.

### 8.2 Blocked Tasks

Tasks depending on actual repo state are blocked until Codex is run or the repo is inspected: TASK-01 through TASK-22.

### 8.3 Quick Wins

- Add `include/domino/platform.h` and `include/domino/compat.h`.
- Add `--introspect-json` stubs.
- Update docs to remove `source/dominium/products` references.
- Move `dominium_modcheck` into `source/dominium/tools/modcheck`.

### 8.4 Tasks Requiring Verification

TASK-17 through TASK-22 require inspection of existing version files, data manifests, packaging scripts, and backend init code.


## 9. Constraints and Requirements

### 9.1 Hard Requirements

| ID | Constraint | Type | Hard/soft | Source / basis | Practical implication | Violation risk | Confidence | Label |
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
| CONSTRAINT-20 | Vector-only UI fallback must remain functional. | UI | hard | Initial thread requirements | No raster asset dependency for functionality. | medium | 5 | FACT |
| CONSTRAINT-21 | Codex prompts must not introduce new external libraries. | implementation | hard | Codex guardrails | Use existing JSON/helpers/manual output. | medium | 5 | FACT |
| CONSTRAINT-22 | Context transfer outputs must label FACT/INFERENCE/UNCERTAIN/PROJECT-CONTEXT. | reporting | hard | User final transfer request | Future aggregation needs provenance labels. | low | 5 | FACT |
| CONSTRAINT-23 | This package is for this chat only. | reporting | hard | User current request | Do not summarize whole project beyond visible chat scope. | low | 5 | FACT |

### 9.2 Soft Preferences

| ID | Constraint | Type | Hard/soft | Source / basis | Practical implication | Violation risk | Confidence | Label |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| CONSTRAINT-19 | Setup should use conservative renderer/backend choices by default. | robustness | soft | Assistant recommendation | Favor soft/TUI fallback. | low | 4 | INFERENCE |

### 9.3 Technical Constraints

See CONSTRAINT-01, CONSTRAINT-02, CONSTRAINT-18, CONSTRAINT-20, and CONSTRAINT-21.

### 9.4 Time / Resource Constraints

No explicit time or resource budget was established in this chat. The phased plan implies staged implementation to reduce refactor risk.

### 9.5 Legal / Ethical / Safety Constraints

No legal/ethical constraints specific to this project were established in this chat. General safety: do not corrupt saves, do not silently load incompatible mods, and do not misrepresent unverified implementation status.

### 9.6 Evidence / Citation Requirements

The user profile requests correctly cited, fact-checked sources for factual/external claims. This report uses visible chat context only; external platform facts should be verified before operational decisions.

### 9.7 Formatting / Output Requirements

The current user request required stable IDs, labels, multiple report files, and a ZIP package if possible.

### 9.8 Things to Avoid

Avoid reopening settled source-layout decisions, suggesting a global Domino runtime, creating separate demo/server products by default, using ambiguous `x64`, or treating generated prompts as applied repo changes.


## 10. Open Questions and Unresolved Issues

| ID | Question / issue | Why it matters | Known information | Unknown information | What would resolve it | Priority | Related workstream | Label |
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

## 11. Rejected, Superseded, or Deprioritised Options

| ID | Option | Status | Reason rejected/superseded/deprioritised | Is rejection final? | Reconsider conditions | Related workstream | Label |
| --- | --- | --- | --- | --- | --- | --- | --- |
| REJECTED-01 | Use `source/engine` for Domino. | rejected | Domino is a named engine and include path is include/domino. | final | Only reconsider if project renames Domino. | WORKSTREAM-01 | FACT |
| REJECTED-02 | Install Domino as a separate global runtime beside Dominium. | rejected | Avoid DLL/runtime version skew. | final for end-user runtime | Reconsider only as developer SDK or private per-suite dynamic lib. | WORKSTREAM-01 | FACT |
| REJECTED-03 | Keep source/dominium/products. | rejected | User explicitly requested flattened layout. | final | None likely. | WORKSTREAM-02 | FACT |
| REJECTED-04 | One monolithic binary for all products. | rejected | User wanted separate binaries per product. | final | Constrained targets may have special combined builds. | WORKSTREAM-03 | FACT |
| REJECTED-05 | Separate demo product/binary. | rejected | Demo should be content/instance policy. | final unless legal/commercial need | Commercial/legal demo packaging requirement. | WORKSTREAM-04 | FACT |
| REJECTED-06 | Separate server product/binary by default. | rejected | One game binary with flags avoids skew. | tentatively final | Minimal dedicated server distro requiring lean binary. | WORKSTREAM-04 | FACT |
| REJECTED-07 | Hardcode launcher execution paths to game/tools. | superseded | Actions system chosen for extensibility. | final direction | Temporary migration scaffolding only. | WORKSTREAM-05 | FACT |
| REJECTED-08 | Make Suite version equal Core version. | rejected | User corrected Suite=Game. | final | None. | WORKSTREAM-08 | FACT |
| REJECTED-09 | Force all product versions to match. | rejected | User requested separate versions. | final | None. | WORKSTREAM-08 | FACT |
| REJECTED-10 | Hardwire base mod version equality in engine. | rejected | Too rigid for engine-only/data-only patches. | final | Use as release convention only. | WORKSTREAM-09 | FACT |
| REJECTED-11 | Use ambiguous `x64` package arch naming. | rejected | User disliked ambiguity. | final | None. | WORKSTREAM-10 | FACT |
| REJECTED-12 | Full UI/packs rewrite in first source refactor. | deprioritized | Too large; initial refactor should be structural. | tentative | After layout/version/repo foundations are stable. | WORKSTREAM-12 | INFERENCE |

Preserving rejected and superseded options prevents future assistants from repeatedly proposing source/engine, global Domino runtime, separate demo binaries, default separate server products, hardcoded launcher paths, or `x64` naming.


## 12. Artifact Ledger

| ID | Artifact / file / prompt / output | Type | Purpose | Status | Where it came from | Carry forward? | Notes | Label |
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

## 13. Rationale and Assumptions

Major visible rationales:

- `source/domino` is retained because Domino is a named engine with matching public headers. Using `source/engine` would obscure identity.
- Domino is bundled/linked into Dominium products because a global runtime would create version skew across suites and old instances.
- Game remains one product with modes to avoid client/server/demo version skew and duplicated product surfaces.
- Launcher is the main suite hub because it can centralize instances, actions, tools, mods/packs, diagnostics, and product builds.
- DOMINIUM_HOME repo/instances exist because the user wants many product/mod/pack versions available to many instances without storing full suites repeatedly.
- Suite version equals Game version because the user explicitly corrected the scheme for user-facing clarity.
- Base official modpack version matching Game version is a release convention because strict equality would force unnecessary bumps and reduce flexibility.
- Actions descriptors are preferred because they allow Game and Tools to expose capabilities to Launcher without hardcoded product paths.
- Explicit architecture tags such as `x86-64` are used because the user rejected ambiguous `x64`.

Important assumptions:

- The repo has not yet been refactored unless the user later reports Codex applied prompts.
- Examples like `2.5.0` and `3.2.1` are illustrative unless found in current files.
- Existing C++ files may remain in Dominium product layers; Domino engine code should remain C89-compatible where applicable.
- The full UI/packs architecture is design-level and likely later-phase, not necessarily part of the immediate source refactor.


## 14. Risks and Failure Modes

| ID | Risk / failure mode | Consequence | Likelihood | Severity | Mitigation | Related workstream | Label |
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

## 15. Verification Queue

| ID | Item requiring verification | Why verification is needed | Suggested verification source/type | Priority | Related workstream | Label |
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

## 16. Spec Book Contribution Notes

Likely future Project Spec Book chapters or sections fed by this chat:

- Project identity: Domino vs Dominium.
- Source layout and build target structure.
- Product model: Game, Launcher, Setup, Tools.
- Game modes: client/listen/dedicated/demo.
- DOMINIUM_HOME repository and instance architecture.
- Versioning and compatibility: core, products, formats, protocols, mods/packs.
- Installer/setup model: portable, per-user, system-wide, non-destructive import.
- Launcher actions model.
- OS/architecture naming and package naming.
- UI/packs architecture overview.
- Codex refactor workflow and quality gates.

Unique contributions from this chat:

- Final source layout decision removing `source/dominium/products`.
- Decision that Domino remains `source/domino` and not `source/engine`.
- Decision that Domino is not a separate end-user runtime.
- Repo/instance model for multi-version product/mod/pack management.
- Actions-based launcher model.
- Suite version equals Game version with separate product/core versions.
- Base official modpack version convention rather than engine invariant.
- Explicit architecture tag scheme avoiding `x64`.

Likely overlaps with other chats:

- Detailed simulation/worldgen specs.
- Low-level dsys/dgfx implementation.
- Full UI toolkit/packs implementation.
- Mod/package manifest details.
- Save/TLV/replay formats.

Conflicts to watch for:

- Other chats may use `source/dominium/products` or old product names.
- Other chats may assume separate client/server/demo binaries.
- Other chats may hardwire base version equality.
- Other chats may use `x64` naming.

Formal requirement candidates:

- Flattened source layout.
- One Game product with modes.
- Launcher actions system.
- DOMINIUM_HOME repo/instance model.
- Product introspection with compatibility metadata.
- Non-destructive Setup import.
- No global Domino runtime.

Background-only candidates:

- Some illustrative version numbers.
- Earlier one-binary-per-platform proposal.
- Full UI/packs subsystem details until implemented.

Needs user confirmation before spec finalization:

- Exact current version numbers.
- Exact default DOMINIUM_HOME per OS.
- Scope of DominiumTools versus Domino dev tools.
- Timing of full UI/packs implementation.


## 17. What Future Assistants Must Preserve

| Priority | Item | Type | Why it matters | Risk if lost | Label | Confidence |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | Final source layout: source/domino plus source/dominium/common/game/launcher/setup/tools. | decision | Defines refactor target. | Wrong directory prompts/code. | FACT | 5 |
| 2 | Do not use source/engine for Domino. | decision | Preserves named engine identity. | Repeated rejected option. | FACT | 5 |
| 3 | No separate end-user Domino runtime. | decision | Avoids runtime version skew. | DLL hell / bad packaging. | FACT | 5 |
| 4 | Four Dominium products: Game, Launcher, Setup, Tools. | decision | Defines build/product model. | Monolithic or fragmented binaries. | FACT | 5 |
| 5 | Game is one product with client/listen/dedicated/demo modes. | decision | Avoids version skew. | Separate products by accident. | FACT | 5 |
| 6 | Launcher is main access point. | decision | Central UX/workflow. | Hardcoded fragmented launches. | FACT | 5 |
| 7 | DOMINIUM_HOME repo/instances model. | architecture | Core multi-version install model. | Duplicate suites and broken instances. | FACT | 5 |
| 8 | Suite version equals Game version. | versioning | Package naming and user-facing identity. | Wrong suite names. | FACT | 5 |
| 9 | Core/product/protocol/format versions remain separate. | versioning | Compatibility. | Unsafe mixed versions. | FACT | 5 |
| 10 | Base mod version matching game is convention, not engine invariant. | versioning/content | Flexibility. | Forced artificial content bumps. | FACT | 5 |
| 11 | DLC/user mods/packs have independent versions and compat ranges. | content | Modding extensibility. | Overconstrained content. | FACT | 5 |
| 12 | Actions system controls launcher execution. | architecture | Tool/product extensibility. | Hardcoded launcher paths. | FACT | 5 |
| 13 | Use explicit arch tags like x86-64, not x64. | naming | Avoid ambiguity. | Bad package names. | FACT | 5 |
| 14 | All UI/platform/rendering through Domino dsys/dgfx/canvas. | architecture | Cross-platform consistency. | OS-native bypasses. | FACT | 5 |
| 15 | Codex prompts were generated but not confirmed applied. | process | Avoid false implementation assumptions. | Misleading next steps. | FACT | 5 |

## 18. What Future Assistants Must Not Assume

- Do not assume the master refactor prompt was applied.
- Do not assume CMake already builds the new layout.
- Do not assume `source/dominium/products` is already gone.
- Do not assume `include/domino/compat.h` or `platform.h` already exist.
- Do not assume `dominium_tools` target exists.
- Do not assume exact version numbers from examples are real.
- Do not assume data manifests already contain the desired compat fields.
- Do not assume backend registry functions already exist.
- Do not assume the full UI/packs architecture is implemented.
- Do not assume root-level `tools/domino_*` should all move into DominiumTools.
- Do not assume all OS/architecture package formats are implemented.
- Do not assume external platform details are current without verification.


## 19. Recommended Next Action

If continuing this chat’s work alone: ask the user whether Codex has already applied any of the generated prompts. If not, use the master refactor prompt or create a slightly narrower Phase 1 prompt covering source layout, CMake, compat/platform headers, product info, and introspection.

If aggregating this chat with other reports: ingest `*_02_spec_sheet.yaml` and `*_03_aggregator_packet.md` first, preserve IDs, and compare against other chats for conflicts around source layout, product model, versioning, and UI/packs scope.

User verification needed before acting:

1. Confirm actual current repo state.
2. Confirm current version numbers.
3. Confirm whether Codex has applied any prompt.
4. Confirm exact scope of the next implementation phase.


## 20. Appendix: Possibly Relevant Details

The user-provided repo tree included a build directory with CMake API replies listing current targets. This is useful but should not be treated as current after future changes. Existing targets included `dominium_game_cli`, `dominium_launcher_cli`, `dominium_setup_cli`, `dominium_modcheck`, `dominium_product_common`, `dominium_rules`, `domino_core`, `domino_engine`, `domino_gfx`, `domino_mod`, `domino_sim`, `domino_sys`, and multiple tests.

Existing `include/dominium` contains product/content headers and some platform/render-like headers such as `dom_plat.h`, `dom_plat_sys.h`, `dom_plat_term.h`, `dom_plat_ui.h`, and `dom_rend.h`. These may need review during compat/platform header work so that responsibility is clear between Domino and Dominium.

Existing `source/domino/system/plat` contains many duplicate or parallel platform directories (`windows/win32`, `win32`, `unix/posix`, `posix`, `sdl/sdl2`, `sdl2`, etc.). This report does not resolve that lower-level cleanup; it only preserves the desired product-level architecture.

Existing `docs/dev` contains many large planning files (`dominium_new_*`) that may overlap with this chat’s architecture. Future aggregation should compare them rather than blindly overwrite.

The user’s final task requested a downloadable report package. This file is one part of that package and should be stored with the generated YAML, aggregator packet, registers, reader brief, audit file, manifest, and ZIP.
