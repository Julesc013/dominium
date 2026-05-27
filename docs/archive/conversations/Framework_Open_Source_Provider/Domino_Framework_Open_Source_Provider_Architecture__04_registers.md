# STRUCTURED REGISTERS — Domino Framework and Open-Source Provider Architecture

## 17. Workstream Register

| ID | Name | Objective | Current state | Desired end state | Status | Priority | Confidence | Label |
|---|---|---|---|---|---|---|---|---|
| WORKSTREAM-01 | Open-source bootstrap strategy | Use existing open-source libraries/projects to accelerate Dominium without losing first-party architecture. | Direction accepted; no code changes made in this chat. | A governed dependency/provider strategy with manifests, boundaries, and tests. | Active | P0 | 4 | FACT/INFERENCE |
| WORKSTREAM-02 | Domino Framework / Engine / Game split | Define Domino Framework as stable contracts; allow multiple Domino engine implementations; run Dominium as one game implementation. | Concept introduced and accepted directionally by user. | Framework ABI, reference engine implementation, Dominium game implementation, profiles, providers. | Active | P0 | 4 | FACT/INFERENCE |
| WORKSTREAM-03 | Service-first provider architecture | Organize runtime by service and provider, not by vendor or app variant. | Strong recurring conclusion. | runtime/<service>/providers/<provider> plus contracts/provider and release/content profiles. | Active | P0 | 5 | FACT |
| WORKSTREAM-04 | raylib provider suite | Use raylib ecosystem as first visible provider suite. | Discussed extensively; proposed directories and boundaries. | raylib/rlgl/rlsw/raygui/raudio providers integrated behind Dominium contracts. | Active | P0 | 5 | FACT/INFERENCE |
| WORKSTREAM-05 | SDL2 and platform/input/audio providers | Keep SDL2 as first-wave platform/input/audio provider alongside raylib. | Direction accepted; no implementation. | SDL2 provider can be selected by profile and coexist with raylib rendering. | Active | P1 | 4 | FACT/INFERENCE |
| WORKSTREAM-06 | Lua scripting provider | Use Lua for packs/mods/CLI/Workbench automation, pinned behind Dominium script API. | Direction repeatedly affirmed. | runtime/script/providers/lua54 or lua55 with dominium.script.v1 API. | Active | P1 | 4 | FACT/INFERENCE |
| WORKSTREAM-07 | Dominium repo alignment | Compare proposed architecture to julesc013/dominium current repo structure. | Repo was inspected via GitHub in chat; findings may be stale. | C17/C++17 baseline and provider directories aligned with actual repo. | Active | P1 | 3 | UNCERTAIN/UNVERIFIED |
| WORKSTREAM-08 | Reference projects and research lane | Use SpaceEngine, Celestia, PCGUniverse2, pgg, and other open-source games as references. | Classified by reuse risk and value. | Research notes and clean-room pattern extraction, not direct unreviewed code reuse. | Active | P2 | 4 | FACT/INFERENCE |
| WORKSTREAM-09 | Sparse deterministic delegated simulation | Design architecture for infinite sparse universe with client-contributed compute. | Conceptual architecture proposed; not implemented. | Work leases, cell authority, sparse materialization, deterministic event logs. | Active | P0 | 4 | INFERENCE |
| WORKSTREAM-10 | CAD / machine / arbitrary invention system | Support arbitrary player/agent/NPC creations by compiling CAD documents into bounded runtime graphs. | Discussed conceptually. | CAD documents, validation, compiled construct graphs, physics/render proxies, machine graphs. | Active | P1 | 4 | INFERENCE |
| WORKSTREAM-11 | Preservation/export package | Preserve this chat into human-readable, structured, and downloadable handoff files. | This output creates the package. | Full report, registers, spec sheet, aggregator packet, ZIP. | Active | P0 | 5 | FACT |

## 18. Decision Register

| ID | Decision | Status | Evidence / basis | Rationale | Implications | Related workstream | Confidence | Label |
|---|---|---|---|---|---|---|---|---|
| DECISION-01 | Use open-source code primarily through a framework/provider approach, not by mutating one large fork. | Accepted direction | User liked framework approach; earlier conversation preferred modular libraries over full engine fork. | Preserves Dominium law and allows replaceability. | Creates Domino Framework/provider architecture. | WORKSTREAM-01 | 4 | FACT/INFERENCE |
| DECISION-02 | raylib should be used heavily as the first visible provider suite. | Accepted direction | User repeatedly agreed with using raylib and asked how to use all of raylib ecosystem. | Fast client, Workbench, rendering, audio, import preview. | Add raylib/rlgl/rlsw/raygui/raudio providers; keep fenced. | WORKSTREAM-04 | 5 | FACT |
| DECISION-03 | Dominium/Domino contracts, simulation, replay, saves, packs, commands, UI documents, provider law remain first-party. | Accepted doctrine | Repeated across assistant outputs and accepted by user refinement. | Avoids lock-in and supports deterministic/replayable game law. | Third-party types forbidden in contracts/game/content/saves/replays. | WORKSTREAM-03 | 5 | FACT/INFERENCE |
| DECISION-04 | Use service-first runtime layout: runtime/<service>/providers/<provider>. | Accepted direction | User moved from raylib-shaped directories to provider/service model. | Avoids vendor-shaped architecture. | Directories should be organized by platform/input/render/audio/etc. | WORKSTREAM-03 | 5 | FACT/INFERENCE |
| DECISION-05 | Profiles select provider combinations; apps should remain generic. | Accepted direction | Transcript repeatedly rejected app variants like apps/client/rendered/raylib as architecture. | Avoids product forks per backend. | Use release/profiles or content/profiles. | WORKSTREAM-03 | 4 | FACT/INFERENCE |
| DECISION-06 | Keep SDL2 as a first-wave provider, not a fallback afterthought. | Accepted direction | User liked SDL; assistant explained SDL2/raylib coexistence. | Gives stable platform/input/audio substrate. | Implement runtime/platform/input/audio/providers/sdl2. | WORKSTREAM-05 | 4 | FACT/INFERENCE |
| DECISION-07 | Use Lua, but pin the Lua provider and expose Dominium script API separately. | Accepted direction | User explicitly said Lua support is wise; transcript refined to pin version. | Prevents raw Lua ABI from becoming mod law. | runtime/script/providers/lua54 or lua55, dominium.script.v1. | WORKSTREAM-06 | 4 | FACT/INFERENCE |
| DECISION-08 | rlsw can be used as a raylib software-render provider, but not as Dominium canonical reference renderer. | Recommended; likely accepted direction | User asked if rlsw could be used; answer differentiated provider vs reference renderer. | Maintains first-party deterministic evidence path. | software/ remains Dominium-owned; rlsw/ is provider. | WORKSTREAM-04 | 4 | FACT/INFERENCE |
| DECISION-09 | rlgl can be used as OpenGL-family provider, but should not be named as final opengl33 law. | Recommended; likely accepted direction | User asked if rlgl could be opengl; answer clarified naming. | Preserves future direct OpenGL provider. | runtime/render/providers/rlgl and later opengl33. | WORKSTREAM-04 | 4 | FACT/INFERENCE |
| DECISION-10 | SpaceEngine, Celestia, PCGUniverse2, and pgg should mainly be reference material, not direct code dependencies. | Recommended | Discussed license/proprietary/GPL/unclear-license issues. | Avoids legal and architectural contamination. | Create research notes and clean-room pattern extraction. | WORKSTREAM-08 | 4 | FACT/INFERENCE |
| DECISION-11 | For sparse/infinite game design, use infinite address space with finite active set and deterministic cells. | Recommended design doctrine | Discussion of deterministic sparse delegated simulation. | Makes infinite/arbitrary world computationally feasible. | world/cell/authority/work/construct subsystems. | WORKSTREAM-09 | 4 | INFERENCE |
| DECISION-12 | Clients may contribute compute but should not be blindly trusted as authoritative. | Recommended doctrine | User asked about clients dynamically taking load; response set host verification model. | Prevents cheating/desync in distributed compute. | Use work leases, verification, state hashes, quorum/spot checks. | WORKSTREAM-09 | 4 | INFERENCE |
| DECISION-13 | Arbitrary CAD creations should compile into bounded runtime representations. | Recommended doctrine | User wants arbitrary infinite building/machines/inventions. | Separates design-time freedom from runtime tractability. | CAD document -> validation -> construct/machine/physics/render graphs. | WORKSTREAM-10 | 4 | INFERENCE |
| DECISION-14 | Create a full preservation package for this chat. | Explicit user instruction | User uploaded preservation prompt and requested files/ZIP. | Allows aggregation and future continuation. | This response creates files and report. | WORKSTREAM-11 | 5 | FACT |

## 19. Task Register

| ID | Task | Priority | Urgency | Owner | Dependencies | Inputs needed | Expected output | Next step | Related workstream | Label |
|---|---|---|---|---|---|---|---|---|---|---|
| TASK-01 | Create DOMINO-FRAMEWORK-WEDGE-01 with framework headers, provider ABI, null providers, raylib providers, profiles, validators. | P0 | U1 | Project implementer | DECISION-01..05 | Repo access, target branch, build policy | Compilable skeleton with client.raylib and server.null profiles. | Draft exact file tree and first PR plan. | WORKSTREAM-02 | INFERENCE |
| TASK-02 | Update or verify C17/C++17 baseline in the actual repo. | P0 | U0 | Project implementer | Repo branch confirmation | Current CMake state | CMake/toolchain policy aligned with target. | Inspect latest branch and update standards or provider target isolation. | WORKSTREAM-07 | UNCERTAIN/UNVERIFIED |
| TASK-03 | Add forbidden include validator. | P0 | U1 | Project implementer | Provider path policy | Allowed/forbidden roots | CI check blocking raylib/SDL/Lua headers in contracts/game/content. | Implement tools/validators/boundary/check_forbidden_includes.py. | WORKSTREAM-03 | FACT/INFERENCE |
| TASK-04 | Add provider manifest schema and validator. | P0 | U1 | Project implementer | Contracts/provider design | Provider fields and paths | Validated manifests for raylib/SDL2/Lua/null providers. | Create contracts/provider/provider.schema.json. | WORKSTREAM-03 | FACT/INFERENCE |
| TASK-05 | Vendor/pin raylib, raygui, SDL2, Lua, and license manifests. | P1 | U1 | Project implementer | License policy, repo dependency policy | Chosen versions | external/upstream contents and manifests. | Select exact versions and confirm platform floors. | WORKSTREAM-04 | UNCERTAIN/UNVERIFIED |
| TASK-06 | Implement raylib platform/input/render/audio/UI/asset providers. | P1 | U2 | Project implementer | TASK-01..05 | Provider ABI, raylib version | Visible client/workbench proof. | Start with rect/text/input/audio/image smoke. | WORKSTREAM-04 | INFERENCE |
| TASK-07 | Implement SDL2 platform/input/audio provider. | P1 | U2 | Project implementer | TASK-01..05 | SDL2 version | client.sdl2_raylib profile. | Start platform/input events and optional audio. | WORKSTREAM-05 | INFERENCE |
| TASK-08 | Implement pinned Lua script provider behind dominium.script.v1. | P1 | U2 | Project implementer | Script API contract | Lua version choice | CLI/pack/workbench automation script provider. | Choose lua54 vs lua55 and define API. | WORKSTREAM-06 | INFERENCE |
| TASK-09 | Create reference notes for external projects. | P2 | U2 | Researcher/assistant | Project links | Research source review | docs/research/references/*.md. | Prioritize SpaceEngine addon model, Celestia architecture, Luanti/OpenRA/Mindustry. | WORKSTREAM-08 | FACT/INFERENCE |
| TASK-10 | Design worldgen/universegen contracts. | P1 | U2 | Project architect | Reference notes, sparse sim doctrine | Scope decisions | contracts/schema/runtime/worldgen/*.schema.json. | Define universe_seed, star_system_packet, planet_packet. | WORKSTREAM-09 | INFERENCE |
| TASK-11 | Design sparse deterministic delegated simulation work-lease packet. | P0 | U2 | Project architect | Determinism doctrine | Network/authority assumptions | work_lease, work_result, verification schemas. | Draft minimal host/client lease smoke. | WORKSTREAM-09 | INFERENCE |
| TASK-12 | Design CAD/construct compile pipeline. | P1 | U2 | Project architect | CAD goals, machine graph model | Scope of first components | CAD document and compiled construct schemas. | Start with components, ports, power graph. | WORKSTREAM-10 | INFERENCE |
| TASK-13 | Manually review this preservation package before merging into a master spec book. | P1 | U1 | User/project curator | This package | Human review | Approved carry-forward items and corrections. | Read sections 1, 5, 17-31 first. | WORKSTREAM-11 | FACT |

Priority: P0 = critical/immediate; P1 = important; P2 = useful; P3 = optional; PX = unclear. Urgency: U0 = now/blocking; U1 = soon; U2 = later; U3 = no timeline; UX = unclear.

## 20. Constraint Register

| ID | Constraint | Type | Hard/soft | Source / basis | Practical implication | Violation risk | Confidence | Label |
|---|---|---|---|---|---|---|---|---|
| CONSTRAINT-01 | Third-party types must not cross framework/contracts/game/content/saves/replays/public SDK boundaries. | Architecture | Hard | Repeated doctrine in chat | All raylib/SDL/Lua/ImGui usage must be fenced in providers or proof tools. | Lock-in, ABI contamination, replay/save instability. | 5 | FACT/INFERENCE |
| CONSTRAINT-02 | Dominium simulation, commands, replay, saves, packs, provider law, UI documents remain first-party. | Architecture | Hard | Repeated doctrine accepted in conversation | Provider implementations cannot define canonical game law. | Third-party engine becomes architecture. | 5 | FACT/INFERENCE |
| CONSTRAINT-03 | Use provider profiles rather than app variants as architecture. | Architecture | Hard-ish | Repeated corrected directory design | apps/client and apps/workbench remain generic. | Backend-specific product forks. | 4 | FACT/INFERENCE |
| CONSTRAINT-04 | C ABI boundaries should be POD/fixed-width/versioned/opaque, no STL/exceptions/third-party handles. | ABI | Hard | Framework design recommendation | Multiple engine/game implementations can interoperate. | ABI instability and plugin breakage. | 4 | INFERENCE |
| CONSTRAINT-05 | Current target includes Windows 7 SP1+, macOS 10.9.5+, Linux, C17/C++17, Win32/Cocoa/SDL2/OpenGL 3.3. | Platform | Hard if user confirms | User stated target earlier in chat | Dependency/version choices must respect floors. | Selected libraries may not support old floors. | 4 | FACT |
| CONSTRAINT-06 | External facts and license/version claims must be verified before implementation. | Evidence | Hard | User preferences and preservation prompt | Create verification queue for software status/licenses/APIs. | Stale or legally unsafe decisions. | 5 | FACT |
| CONSTRAINT-07 | No direct code reuse from proprietary/GPL/unclear-license projects unless license strategy is explicit. | Legal/architecture | Hard | SpaceEngine/Celestia/PCGUniverse/pgg discussion | Use reference-only clean-room notes unless GPL/permissions accepted. | License contamination or infringement. | 4 | FACT/INFERENCE |
| CONSTRAINT-08 | Authoritative client-contributed compute must be verified by host/server. | Networking/security | Hard | Sparse delegated simulation discussion | Clients produce work results, host verifies before commit. | Cheat/desync/state corruption. | 4 | INFERENCE |
| CONSTRAINT-09 | Arbitrary CAD creations must compile to bounded runtime graphs/proxies. | Simulation/performance | Hard | CAD/machine discussion | Runtime sim works on machine graphs/physics proxies, not raw arbitrary geometry. | Infinite/unbounded compute and impossible physics. | 4 | INFERENCE |
| CONSTRAINT-10 | This preservation report is for this chat only unless labelled PROJECT-CONTEXT. | Reporting | Hard | Uploaded preservation prompt | Do not merge unseen past chats or project memory silently. | False completeness or invented context. | 5 | FACT |

## 21. User Preference Register

| ID | Preference | Area | Explicit/inferred/uncertain | Strength | Practical implication | Risk if wrong | Label |
|---|---|---|---|---|---|---|---|
| PREF-01 | Direct, audit-ready, source-grounded answers with uncertainty labels. | Communication | Explicit | High | Use FACT/INFERENCE/UNCERTAIN labels and verification queues. | User may distrust unsupported conclusions. | FACT |
| PREF-02 | Human-readable explanation first, not just machine registers. | Preservation | Explicit | High | Lead with narrative sections before YAML/registers. | Report fails main user goal. | FACT |
| PREF-03 | Do not ask whether to proceed; proceed with best effort. | Workflow | Explicit | High | Create files and report now. | Unwanted clarification delays. | FACT |
| PREF-04 | Do not treat brainstorms as decisions. | Epistemic discipline | Explicit | High | Mark suggestions vs accepted direction. | Overstated spec decisions. | FACT |
| PREF-05 | Preserve rejected/superseded options and contradictions. | Aggregation | Explicit | High | Registers include rejected/superseded options. | Future chat repeats old mistakes. | FACT |
| PREF-06 | Use modular framework/provider approach rather than monolithic fork. | Architecture | Explicit/inferred | High | Prioritize libraries/providers and contracts. | Forked engine may overwrite Dominium law. | FACT/INFERENCE |
| PREF-07 | Keep responses structured with headings/tables where useful. | Communication | Explicit/inferred | Medium-high | Use tables for registers, prose for narrative. | Hard to audit later. | FACT/INFERENCE |

## 22. Open Questions Register

| ID | Question / issue | Why it matters | Known information | Unknown information | Resolution path | Priority | Related workstream | Label |
|---|---|---|---|---|---|---|---|---|
| QUESTION-01 | Which exact versions of raylib, SDL2, Lua, raygui, ImGui, and related libraries should be pinned? | Platform floors and API stability depend on versions. | The conversation recommended using them. | Exact versions and compatibility with Win7/macOS 10.9.5. | Verify upstream release notes and build tests. | P0 | WORKSTREAM-04 | UNCERTAIN/UNVERIFIED |
| QUESTION-02 | Is Dominium repo main branch actually C17/C++17 or still C90/C++98? | Build baseline affects raylib and framework. | Earlier assistant inspection found possible C90/C++98 contradiction; later transcript claimed C17/C++17. | Current branch truth. | Inspect current repo branch before implementation. | P0 | WORKSTREAM-07 | UNCERTAIN/UNVERIFIED |
| QUESTION-03 | Should the canonical Lua provider be lua54 or lua55? | Script ABI and mod compatibility. | Lua should be pinned and hidden behind dominium.script.v1. | Specific series choice. | Compare maturity, compatibility, platform support. | P1 | WORKSTREAM-06 | UNCERTAIN |
| QUESTION-04 | What is the first minimal Domino Framework ABI? | Blocks implementation. | Concept defined but not specified fully. | Exact structs/functions/services. | Draft DOMINO-FRAMEWORK-WEDGE-01 header. | P0 | WORKSTREAM-02 | INFERENCE |
| QUESTION-05 | What first provider profile should be implemented: client.raylib, client.sdl2_raylib, or server.null? | Implementation order. | All were proposed. | Priority/order and acceptance tests. | Choose wedge scope. | P0 | WORKSTREAM-02 | INFERENCE |
| QUESTION-06 | How strict must deterministic simulation be across platforms? | Affects math, threads, providers. | Determinism required at sim/command layer, not render/audio/UI. | Exact determinism class and tolerated divergence. | Define determinism spec. | P0 | WORKSTREAM-09 | INFERENCE |
| QUESTION-07 | What license policy will Dominium adopt for GPL/LGPL/unclear-license references? | Code reuse boundaries. | Reference-only default recommended. | Formal project legal policy. | Write license/provenance policy. | P1 | WORKSTREAM-08 | UNCERTAIN |
| QUESTION-08 | What is the minimal CAD construct graph for first implementation? | Arbitrary invention system is broad. | Graph/ports/machine model proposed. | First component set and compile pipeline. | Define CAD-WEDGE-01. | P1 | WORKSTREAM-10 | INFERENCE |
| QUESTION-09 | How will client-contributed work be verified and what trust tiers exist? | Distributed compute feasibility and security. | Work lease/quorum/spot-check model proposed. | Exact verification policy. | Prototype host/client lease smoke. | P0 | WORKSTREAM-09 | INFERENCE |

## 23. Artifact Ledger

| ID | Artifact / file / prompt / output | Type | Purpose | Status | Origin | Carry forward? | Notes | Label |
|---|---|---|---|---|---|---|---|---|
| ARTIFACT-01 | Pasted text.txt preservation prompt | Uploaded file / prompt | Defines required preservation package, sections, files, and labels. | Available in this chat | User upload | Yes | Primary instruction artifact for this task. fileciteturn29file0 | FACT |
| ARTIFACT-02 | Prior assistant raylib/provider architecture messages | In-chat outputs | Developed service-first provider doctrine, raylib/SDL/Lua role, directory structures. | Visible in chat context | This chat | Yes | Substantive source for report. | FACT |
| ARTIFACT-03 | GitHub inspection snippets for julesc013/dominium | Tool results in chat | Compared current repo dsys/dgfx stubs and possible CMake baseline. | Visible in chat context; freshness uncertain | GitHub connector during chat | Yes, with verification | Use as historical inspection, not current truth. | UNCERTAIN/UNVERIFIED |
| ARTIFACT-04 | Lists of external projects and reference links | In-chat lists | SpaceEngine, Celestia, PCGUniverse2, pgg, open-source engines/games. | Visible in chat | User and assistant messages | Yes | Feed research/reference lane. | FACT |
| ARTIFACT-05 | DOMINO-FRAMEWORK-WEDGE-01 proposal | Plan/output | First implementation wedge for framework/provider architecture. | Proposed, not implemented | Assistant suggestion accepted directionally | Yes | Should become task/epic. | INFERENCE |
| ARTIFACT-06 | PROVIDER-WEDGE / RENDER-WEDGE / SCRIPT-WEDGE naming | Plan/output | Staged implementation plan. | Proposed, not implemented | Assistant outputs | Yes | Useful for backlog. | INFERENCE |
| ARTIFACT-07 | This preservation package files | Generated files | Markdown/YAML/ZIP handoff package. | Created by current response | Assistant file export | Yes | Use for aggregation and future continuation. | FACT |

## 24. Rejected / Superseded Options Register

| ID | Option | Status | Reason | Final or tentative? | Reconsider conditions | Related workstream | Label |
|---|---|---|---|---|---|---|---|
| REJECTED-01 | Forking a full engine as the main architecture. | Deprioritised | Would overwrite Dominium law and create lock-in. | Tentative but strong | Reconsider only for isolated prototype or tool, not canonical core. | WORKSTREAM-01 | FACT/INFERENCE |
| REJECTED-02 | Letting raylib define game architecture. | Rejected | raylib should be provider, not law. | Strong | Never reconsider unless project goal changes. | WORKSTREAM-04 | FACT |
| REJECTED-03 | Placing provider identity into app folder names such as apps/client/rendered/raylib. | Superseded | Profiles should select providers; apps remain generic. | Strong | Temporary proof apps may exist under proof/experiments. | WORKSTREAM-03 | FACT/INFERENCE |
| REJECTED-04 | Top-level labs/ or profiles/ roots as main architecture. | Deprioritised | Could reopen top-level-root sprawl; prefer content/profiles or release/profiles and tools/experiments. | Tentative | Reconsider if repo governance adopts those roots deliberately. | WORKSTREAM-03 | INFERENCE |
| REJECTED-05 | Using rlsw as canonical Dominium software renderer. | Rejected | rlsw is raylib ecosystem provider; Dominium reference should be first-party. | Strong | Could be temporary fallback but not proof law. | WORKSTREAM-04 | FACT/INFERENCE |
| REJECTED-06 | Using rlgl as the final direct opengl33 provider. | Rejected/superseded | rlgl is raylib abstraction; direct opengl33 should be separate. | Strong | rlgl can implement first OpenGL-family provider. | WORKSTREAM-04 | FACT/INFERENCE |
| REJECTED-07 | Trusting client-contributed simulation results without verification. | Rejected | Cheating/desync risk. | Strong | Only in local trusted sandbox/co-op if explicitly chosen. | WORKSTREAM-09 | INFERENCE |
| REJECTED-08 | Simulating every arbitrary object everywhere continuously. | Rejected | Impossible/unbounded; sparse activation required. | Strong | Local dense simulation can exist in bounded active cells. | WORKSTREAM-09 | INFERENCE |
| REJECTED-09 | Copying code from proprietary/GPL/unclear-license projects by default. | Rejected | License and architecture risk. | Strong | Reconsider only with explicit license strategy/quarantine. | WORKSTREAM-08 | FACT/INFERENCE |

## 25. Risk Register

| ID | Risk / failure mode | Consequence | Likelihood | Severity | Mitigation | Related workstream | Label |
|---|---|---|---|---|---|---|---|
| RISK-01 | Future assistant treats recommendations as final decisions. | Spec may overcommit. | Medium | High | Use status labels: accepted direction vs proposed vs unresolved. | All | FACT/INFERENCE |
| RISK-02 | Third-party libraries leak into public contracts. | Long-term lock-in, save/replay breakage. | Medium | High | Forbidden include validator and provider manifests. | WORKSTREAM-03 | FACT/INFERENCE |
| RISK-03 | C17/C++17 baseline assumed without repo verification. | Build failures or wrong plan. | Medium | High | Verify current branch before implementation. | WORKSTREAM-07 | UNCERTAIN/UNVERIFIED |
| RISK-04 | raylib/SDL/Lua current versions may not support stated old OS floors. | Platform target failure. | Medium | High | Pin/test exact versions on Win7/macOS 10.9.5/Linux. | WORKSTREAM-04 | UNCERTAIN/UNVERIFIED |
| RISK-05 | GPL/unclear-license project code copied accidentally. | Legal contamination. | Low-medium | High | Research-only lane, license validator, provenance policy. | WORKSTREAM-08 | FACT/INFERENCE |
| RISK-06 | Distributed client compute becomes cheat vector. | Invalid world state/economy/combat. | High if unmitigated | High | Host verification, work leases, state hashes, trust tiers. | WORKSTREAM-09 | INFERENCE |
| RISK-07 | Arbitrary CAD runtime becomes computationally unbounded. | Performance collapse/desync. | High if raw CAD simulated | High | Compile to bounded graphs/proxies and enforce budgets. | WORKSTREAM-10 | INFERENCE |
| RISK-08 | Report overstates access to full chat or past-chat links. | Bad aggregation. | Medium | Medium | State source limitation; use this chat only. | WORKSTREAM-11 | FACT |
| RISK-09 | External facts go stale. | Wrong dependency/legal choices. | High over time | Medium-high | Verification queue before implementation. | All | FACT |

## 26. Verification Queue

| ID | Item requiring verification | Why verification is needed | Suggested source/type | Priority | Related workstream | Label |
|---|---|---|---|---|---|---|
| VERIFY-01 | Current julesc013/dominium CMake language standards and branch state. | Prior chat had contradictory statements. | GitHub repo current branch / local clone. | P0 | WORKSTREAM-07 | UNCERTAIN/UNVERIFIED |
| VERIFY-02 | raylib current version, license, OS floors, and exact support for Win7/macOS 10.9.5. | Provider viability depends on it. | Official raylib repo/release notes/build tests. | P0 | WORKSTREAM-04 | UNCERTAIN/UNVERIFIED |
| VERIFY-03 | SDL2 exact version and OS floor support. | Platform/input/audio provider viability. | SDL release notes/docs/build tests. | P0 | WORKSTREAM-05 | UNCERTAIN/UNVERIFIED |
| VERIFY-04 | Lua 5.4 vs 5.5 stability and embedding implications. | Script ABI and mod lifecycle. | Official Lua docs/release notes. | P1 | WORKSTREAM-06 | UNCERTAIN |
| VERIFY-05 | Licenses for PCGUniverse2 and Valian/pgg. | Direct code reuse currently unsafe. | Repository license files/author clarification. | P2 | WORKSTREAM-08 | UNCERTAIN/UNVERIFIED |
| VERIFY-06 | Celestia GPL implications for any code reuse. | Avoid license contamination. | GPL counsel/project license policy. | P1 | WORKSTREAM-08 | UNCERTAIN/UNVERIFIED |
| VERIFY-07 | Whether SpaceEngine assets/code can be used at all. | Likely proprietary; must not copy. | SpaceEngine EULA/licensing pages. | P1 | WORKSTREAM-08 | UNCERTAIN/UNVERIFIED |
| VERIFY-08 | Dear ImGui, Nuklear, SQLite, Jolt, Box2D, bgfx license/platform fit before adoption. | Second-wave dependencies may carry constraints. | Official repos/licenses/releases. | P2 | WORKSTREAM-01 | UNCERTAIN/UNVERIFIED |

## 27. Chronological Timeline Register

| Sequence | Event / topic | What changed or was decided | Why it mattered | Current relevance | Confidence |
|---|---|---|---|---|---|
| 1 | User asked whether the project could use existing open-source systems instead of starting from nothing. | Bootstrap strategy became the initial frame. | Established modular/fork tradeoff. | Foundation of entire chat. | 5 |
| 2 | Assistant recommended using open-source code as scaffolding/providers while keeping Dominium contracts first-party. | Doctrine: fork for speed, wrap for control, test for proof, replace by boundary. | Set anti-lock-in strategy. | Still core. | 5 |
| 3 | User listed target platforms/language goals and expressed support for Lua, SDL, and raylib. | Discussion narrowed to raylib/SDL/Lua provider strategy. | Established first-wave dependency candidates. | Core. | 5 |
| 4 | Assistant proposed raylib-heavy backend use with strict boundaries. | Initial directory structure used runtime/render/raylib etc. | Useful but later refined. | Superseded by service-first layout. | 4 |
| 5 | User requested deep dive on raylib and comparison to julesc013/dominium. | GitHub repo was inspected. | Connected theory to current codebase. | Needs verification due staleness. | 4 |
| 6 | Assistant found current repo had dsys/dgfx abstractions and some stubs/soft-backed paths. | raylib could fill missing concrete provider layer. | Showed repo already has seams. | Important but verify. | 3 |
| 7 | User pasted/compared prior syntheses and asked about rlsw, rlgl, raymath, raygui, raudio. | Architecture refined into service-first/provider-first model. | Final raylib ecosystem classification. | Core. | 5 |
| 8 | Assistant concluded rlsw is provider not canonical renderer; rlgl is provider not final opengl33; raygui/raudio/raymath/rtextures/rmodels are usable with fences. | Clarified specific subcomponent roles. | Avoids naming/ownership confusion. | Core. | 5 |
| 9 | User asked whether SpaceEngine, Celestia, PCGUniverse2, pgg can help. | Projects classified as reference-only or license-constrained. | Created research lane. | Important context. | 4 |
| 10 | User asked about other projects and deterministic sparse distributed arbitrary game design. | Architecture expanded to sparse deterministic delegated simulation. | Defined world/cell/work/authority/CAD/machine directions. | Core future work. | 4 |
| 11 | User asked if open-source engines/games could be used. | Assistant classified engines/games into dependency/reference lanes. | Added Luanti/OpenRA/Mindustry/etc. as references. | Useful for research backlog. | 4 |
| 12 | User asked whether framework approach could create a Domino framework provided by any engine implementation and any Dominium game implementation. | Domino Framework / Domino Engine Implementation / Dominium Game Implementation split was articulated. | Most important conceptual convergence. | Core. | 5 |
| 13 | User uploaded preservation prompt. | Current task became full chat preservation and export. | Creates handoff for aggregation. | Current output. | 5 |

## 28. Spec Book Contribution Register

| Spec-book area | Contribution from this chat | Source IDs | Should become requirement/context/open issue? | Confidence | Notes |
|---|---|---|---|---|---|
| Framework architecture | Domino Framework API, engine implementation, game implementation split. | DECISION-01, DECISION-14, WORKSTREAM-02 | Requirement | 5 | Central spec chapter. |
| Provider system | Service-first runtime providers, manifests, profiles, conformance tests. | DECISION-03..05, WORKSTREAM-03 | Requirement | 5 | Core architecture. |
| First-wave dependencies | raylib, rlgl, rlsw, raygui, raudio, SDL2, Lua. | DECISION-02, DECISION-06..09 | Requirement/context with verification | 4 | Needs version/platform checks. |
| License/provenance | Reference-only lane for GPL/proprietary/unclear projects. | DECISION-10, CONSTRAINT-07 | Requirement | 4 | Should become legal/provenance policy. |
| Sparse deterministic simulation | Infinite address space, finite active set, work leases, host verification. | DECISION-11..13, WORKSTREAM-09 | Requirement/open issue | 4 | Needs formal protocols. |
| CAD/invention system | CAD documents compile into bounded construct/machine graphs. | DECISION-13, WORKSTREAM-10 | Requirement/open issue | 4 | Needs first component model. |
| Workbench direction | Workbench edits Dominium documents, not raygui objects; uses providers. | WORKSTREAM-04, WORKSTREAM-10 | Requirement/context | 4 | Ties UI documents to tooling. |
| Preservation/aggregation | This chat is converted into report, registers, spec sheet, ZIP. | WORKSTREAM-11 | Context | 5 | Feeds master spec book. |
