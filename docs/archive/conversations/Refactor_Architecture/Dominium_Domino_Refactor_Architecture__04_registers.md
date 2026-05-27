# Registers — Dominium + Domino Refactor Architecture

## 1. Workstream Register

| ID | Name | Objective | Status | Priority | Label | Confidence |
| --- | --- | --- | --- | --- | --- | --- |
| WORKSTREAM-01 | Domino engine identity and source boundary | Preserve Domino as the named deterministic engine under source/domino, not a generic source/engine directory. | active | high | FACT | 5 |
| WORKSTREAM-02 | Dominium source layout flattening | Remove source/dominium/products and place common, game, launcher, setup, and tools directly under source/dominium. | active | critical | FACT | 5 |
| WORKSTREAM-03 | Dominium product model | Maintain four top-level Dominium products: Game, Launcher, Setup, Tools. | active | critical | FACT | 5 |
| WORKSTREAM-04 | Game client/listen/dedicated/demo modes | Use one Game product/binary with modes for client, listen server, dedicated server, and demo/full. | active | high | FACT | 5 |
| WORKSTREAM-05 | Launcher as main suite hub | Make Launcher the main point of access to the entire suite. | active | high | FACT | 5 |
| WORKSTREAM-06 | Setup/install/package management | Support portable, per-user, and system-wide install modes, with non-destructive repo import and GC. | active | high | FACT | 5 |
| WORKSTREAM-07 | DOMINIUM_HOME repository and instance system | Store multiple versions of products/mods/packs once and let instances reference them. | active | critical | FACT | 5 |
| WORKSTREAM-08 | Versioning and compatibility metadata | Allow products, formats, protocols, mods, and packs to negotiate compatibility and degrade safely. | active | critical | FACT | 5 |
| WORKSTREAM-09 | Mods, packs, base data, DLC, demo content | Version and load content packs/mods independently while preserving base-game clarity. | active | high | FACT | 5 |
| WORKSTREAM-10 | OS family, architecture, packaging, wrappers | Use explicit OS/architecture tags and package naming across all suites. | active | medium | FACT | 5 |
| WORKSTREAM-11 | Backend selection via dsys/dgfx | Allow products to choose valid platform and renderer backends through shared Domino APIs. | active | medium | FACT | 4 |
| WORKSTREAM-12 | UI/UX/packs presentation architecture | Create a modular UI and packs stack on top of dsys/dgfx with vector-only fallback and optional raster/audio/music packs. | active but later-phase | medium | FACT | 4 |
| WORKSTREAM-13 | Codex refactor and consistency prompts | Provide Codex with prompts to apply architecture changes and then normalize repo consistency. | active | critical | FACT | 5 |
| WORKSTREAM-14 | Starter prompts and future chat continuity | Generate reusable starter prompts and transfer packets so future ChatGPT conversations can continue without re-explanation. | active | high | FACT | 5 |

## 2. Decision Register

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

## 3. Task Register

| ID | Task | Priority | Urgency | Owner | Dependencies | Inputs needed | Expected output | Next step | Related workstream | Label | Confidence |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| TASK-01 | Move source/dominium/products/common to source/dominium/common. | high | high | Codex/developer | WORKSTREAM-02 | Current repo tree | Common code in new path | Apply refactor and update CMake/includes | WORKSTREAM-02 | FACT | 5 |
| TASK-02 | Move game/launcher/setup directories and rules to new source/dominium layout. | high | high | Codex/developer | TASK-01 | Existing source tree | Flattened source/dominium layout | Run master refactor prompt | WORKSTREAM-02 | FACT | 5 |
| TASK-03 | Add include/domino/platform.h and include/domino/compat.h. | high | high | Codex/developer | WORKSTREAM-01 | Specified enum/struct definitions | Public compatibility/platform API | Add headers and adjust includes | WORKSTREAM-08 | FACT | 5 |
| TASK-04 | Implement source/domino/compat/compat_core.c. | high | high | Codex/developer | TASK-03 | DomCompatProfile definitions | Range-based compat helpers | Wire into CMake | WORKSTREAM-08 | FACT | 5 |
| TASK-05 | Create/normalize product info providers for Game, Launcher, Setup, Tools. | high | high | Codex/developer | TASK-03 | Version macros | dom_get_product_info_* functions | Add stubs and test | WORKSTREAM-03 | FACT | 5 |
| TASK-06 | Add --introspect-json to all products. | high | high | Codex/developer | TASK-05 | Product info structs | Valid JSON product metadata output | Implement in CLI mains | WORKSTREAM-08 | FACT | 5 |
| TASK-07 | Centralize Game mode parsing and options. | high | medium | Codex/developer | WORKSTREAM-04 | Existing game CLI files | Parsed --mode/--server/--instance/--demo | Add options struct | WORKSTREAM-04 | FACT | 5 |
| TASK-08 | Route client/server old entrypoints through unified Game mode selector. | high | medium | Codex/developer | TASK-07 | dom_client_main.c, dom_server_main.c | One startup pathway | Refactor carefully | WORKSTREAM-04 | FACT | 5 |
| TASK-09 | Implement dmn_get_dominium_home path discovery. | high | medium | Codex/developer | WORKSTREAM-07 | OS path policy | Central DOMINIUM_HOME API | Create dmn_paths module | WORKSTREAM-07 | FACT | 5 |
| TASK-10 | Implement repo API for products/mods/packs. | high | medium | Codex/developer | TASK-09 | Repo layout schema | dmn_repo helpers | Write tests with temp DOMINIUM_HOME | WORKSTREAM-07 | FACT | 5 |
| TASK-11 | Implement instance load/save/list API. | high | medium | Codex/developer | TASK-09 | instance.json schema | dmn_instance module | Refactor launcher instances service | WORKSTREAM-07 | FACT | 5 |
| TASK-12 | Implement product actions loader. | high | medium | Codex/developer | TASK-10 | actions.json schema | dmn_actions_list functions | Load actions from repo builds | WORKSTREAM-05 | FACT | 5 |
| TASK-13 | Refactor Launcher to invoke actions instead of hardcoded executables. | high | medium | Codex/developer | TASK-12 | Launcher process code | Action-driven Launcher | Search hardcoded calls | WORKSTREAM-05 | FACT | 5 |
| TASK-14 | Implement Setup non-destructive import into repo. | high | medium | Codex/developer | TASK-10 | InstallRoot model | Import builds/mods/packs if missing | Add dry-run/logging | WORKSTREAM-06 | FACT | 5 |
| TASK-15 | Implement Setup portable/per-user/system-wide mode handling. | medium | medium | Codex/developer | TASK-09 | Install mode policy | Setup CLI/model supports modes | Update docs/help | WORKSTREAM-06 | FACT | 5 |
| TASK-16 | Implement GC preview/confirm for unused repo entries. | medium | medium | Codex/developer | TASK-10, TASK-11 | Repo and instance APIs | Safe cleanup command | Add preview before deletion | WORKSTREAM-06 | FACT | 5 |
| TASK-17 | Centralize version macros in include/dominium/version.h and dominium_version.c. | high | high | Codex/developer | WORKSTREAM-08 | Existing version files | Single version source | Replace hardcoded versions | WORKSTREAM-08 | FACT | 5 |
| TASK-18 | Update base and demo content manifests. | medium | medium | Codex/developer | TASK-17 | data/mods and data/versions | Base/demo version/compat aligned | Inspect actual manifests | WORKSTREAM-09 | FACT | 5 |
| TASK-19 | Ensure DLC/user mods/packs keep independent versions and compatibility ranges. | medium | medium | Codex/developer | TASK-18 | data/mods/space/war/examples | Manifest consistency | Update docs and validation | WORKSTREAM-09 | FACT | 5 |
| TASK-20 | Update packaging artifact naming and arch tags. | medium | medium | Codex/developer | TASK-17 | scripts/packaging | Dominium-Suite-<GAME_VERSION>-<OSFam>-<Arch> names | Edit packaging scripts | WORKSTREAM-10 | FACT | 5 |
| TASK-21 | Update wrapper scripts to launch Launcher/client/server modes. | medium | medium | Codex/developer | TASK-07 | scripts/packaging/scripts | dominium/dom-client/dom-server wrappers aligned | Edit .cmd.in/.sh.in | WORKSTREAM-10 | FACT | 5 |
| TASK-22 | Add backend selection CLI flags and registry stubs. | medium | medium | Codex/developer | WORKSTREAM-11 | Existing dsys/dgfx init | --platform and --renderer work or fail clearly | Implement minimally | WORKSTREAM-11 | FACT | 4 |
| TASK-23 | Defer full UI/packs refactor into dedicated later prompt/spec. | medium | low | Developer/assistant | WORKSTREAM-12 | Initial UI architecture | Separate UI implementation plan | Do not mix into Phase 1 refactor | WORKSTREAM-12 | FACT | 4 |
| TASK-24 | Run master refactor prompt in Codex. | critical | high | User/Codex | All decisions | Master refactor prompt | Repo refactored | User should execute or ask assistant to refine prompt | WORKSTREAM-13 | FACT | 5 |
| TASK-25 | Run post-refactor consistency prompt after build. | high | high | User/Codex | TASK-24 | Consistency prompt | Stale references removed | Run grep/build/tests | WORKSTREAM-13 | FACT | 5 |
| TASK-26 | Save this report package and use it in future aggregation. | high | high | User | Current package | Generated files | Reusable chat-specific report package | Download ZIP | WORKSTREAM-14 | FACT | 5 |

## 4. Constraint Register

| ID | Constraint | Type | Hard/soft | Source / basis | Implication | Violation risk | Confidence | Label |
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

## 5. User Preference Register

| ID | Preference | Kind | Source basis | Implication | Strength | Risk if misunderstood | Label |
| --- | --- | --- | --- | --- | --- | --- | --- |
| PREFERENCE-01 | Straightforward, strict technical language. | explicit | User instructions | Use concise, dense, direct responses. | high | Risk of user dissatisfaction and ambiguity. | FACT |
| PREFERENCE-02 | Correctly cited/fact-checked sources where current external facts are used. | explicit | User profile/instructions | Search web for current facts when needed; not relevant for this internal package. | high | Could violate trust if external claims made. | FACT |
| PREFERENCE-03 | Maximum-fidelity transfer and preservation of decisions, rejected options, prompts, files. | explicit | Current request | Do not compress aggressively. | high | Loss of context for future chats. | FACT |
| PREFERENCE-04 | Codex-ready prompts with concrete paths and constraints. | inferred | Repeated requests for Codex prompts | Generate implementation-oriented prompts. | high | Prompts too vague for Codex. | INFERENCE |
| PREFERENCE-05 | Long-lived modular architecture over quick hacks. | inferred | Repeated emphasis on extensibility/robustness | Avoid brittle hardcoded solutions. | high | Future refactors become harder. | INFERENCE |
| PREFERENCE-06 | Preserve source layout decisions exactly. | explicit | User corrected source layout | Do not reopen settled source directory choices. | high | Wasted discussion/repeated options. | FACT |
| PREFERENCE-07 | Use explicit architecture names, no x64 ambiguity. | explicit | User statement | Use x86-64 in examples and package names. | medium | Naming inconsistency. | FACT |
| PREFERENCE-08 | No normal summary for transfer tasks. | explicit | Current request | Produce registers/package, not generic prose summary. | high | Output fails task. | FACT |

## 6. Open Questions Register

| ID | Question | Why it matters | Known | Unknown | Resolution path | Priority | Related workstreams | Label |
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

## 7. Artifact Ledger

| ID | Artifact | Type | Purpose | Status | Origin | Carry forward | Notes | Label |
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

## 8. Rejected / Superseded Options Register

| ID | Option | Status | Reason | Final/tentative | Reconsider conditions | Related workstream | Label |
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

## 9. Risk Register

| ID | Risk | Consequence | Likelihood | Severity | Mitigation | Related workstream | Label |
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

## 10. Verification Queue

| ID | Item | Why verification is needed | Suggested source/type | Priority | Related workstream | Label |
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

## 11. Timeline Register

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

## 12. Spec Book Contribution Register

| ID | Spec book contribution | Type | Notes | Label |
| --- | --- | --- | --- | --- |
| SPEC-CONTRIB-01 | Domino vs Dominium identity and source boundaries | chapter/section | Use WORKSTREAM-01 and WORKSTREAM-02. | FACT |
| SPEC-CONTRIB-02 | Product model and binaries | chapter/section | Use WORKSTREAM-03 and WORKSTREAM-04. | FACT |
| SPEC-CONTRIB-03 | Launcher hub and actions model | chapter/section | Use WORKSTREAM-05. | FACT |
| SPEC-CONTRIB-04 | Setup and install model | chapter/section | Use WORKSTREAM-06. | FACT |
| SPEC-CONTRIB-05 | DOMINIUM_HOME repo/instances | chapter/section | Use WORKSTREAM-07. | FACT |
| SPEC-CONTRIB-06 | Versioning and compatibility | chapter/section | Use WORKSTREAM-08. | FACT |
| SPEC-CONTRIB-07 | Mods/packs/content versioning | chapter/section | Use WORKSTREAM-09. | FACT |
| SPEC-CONTRIB-08 | OS/architecture/package naming | chapter/section | Use WORKSTREAM-10. | FACT |
| SPEC-CONTRIB-09 | Backend selection | chapter/section | Use WORKSTREAM-11. | FACT |
| SPEC-CONTRIB-10 | UI/packs future architecture | chapter/section | Use WORKSTREAM-12, but verify against UI-specific chats. | FACT |
| SPEC-CONTRIB-11 | Codex prompt workflow | appendix/process | Use WORKSTREAM-13. | FACT |
| SPEC-CONTRIB-12 | Continuity and transfer process | appendix/process | Use WORKSTREAM-14. | FACT |