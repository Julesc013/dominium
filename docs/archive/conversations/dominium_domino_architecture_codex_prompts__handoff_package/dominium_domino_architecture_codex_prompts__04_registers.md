# Registers — Dominium/Domino Architecture and Codex Prompts

## 1. Workstream Register

| ID | Name | Label | Objective | Current state | Status | Priority |
| --- | --- | --- | --- | --- | --- | --- |
| WORKSTREAM-01 | Domino Engine Core Infrastructure | FACT | Define deterministic C89 engine core with subsystem/model/schema registries, TLV save/load, fixed-point foundations, and strict platform/render abstractions. | Architecture and Codex prompts defined; implementation not verified. | active | critical |
| WORKSTREAM-02 | Dominium Product Suite | FACT | Define C++98 products on top of Domino: game, launcher, setup, and tools. | Architecture and prompts defined; implementation not verified. | active | high |
| WORKSTREAM-03 | Repository, Instance, and Compatibility Model | FACT | Maintain multi-version products, packs, mods, blueprints, and instances under DOMINIUM_HOME. | Canonical layout and compatibility concepts defined. | active | high |
| WORKSTREAM-04 | Content, Packs, Mods, TLV, and Base Pack | FACT | Keep all gameplay data in packs/mods using TLV schemas and registries. | Content model, base pack, base_demo mod prompts defined. | active | critical |
| WORKSTREAM-05 | DRES Resource System | FACT | Generic channel-based resource system with model vtables and data-defined deposits. | Baseline architecture accepted; implementation prompts generated. | active | high |
| WORKSTREAM-06 | Environment, Hydrology, Atmosphere, and Lithology | FACT | Zone/field-based environmental systems for enclosed spaces, water, gases, heat, light, pollution, radiation, and terrain layers. | Architecture developed; Prompt 13 generated. | active | high |
| WORKSTREAM-07 | Buildings, Construction, Placement, and Sloped Terrain | FACT | Support Sims-style buildings, interior zones, machine placement, off-grid anchors, yaw rotation, and realistic terrain foundations. | Design defined; prompts generated. | active | high |
| WORKSTREAM-08 | Transport and Logistics Splines | FACT | Unified spline infrastructure for arbitrary transport modes with endpoints/midpoints, profiles, movers, ports, and low-CPU simulation. | Design defined; Prompt 14 generated. | active | high |
| WORKSTREAM-09 | Packaging and Containers | FACT | Aggregate items into crates/bags/pallets/containers to reduce simulation cost while respecting mass/volume/density. | Design defined; integrated into Prompt 14. | active | medium-high |
| WORKSTREAM-10 | Structures, Machines, and Generic Process Runner | FACT | Generic structures/machines run data-defined processes via ports, inventories, resources, and networks. | Prompts 10 and 15 define minimal and expanded loops. | active | high |
| WORKSTREAM-11 | Vehicles and Weapons as Compiled Runtime Objects | FACT | Allow player-designed vehicles/weapons compiled from module graphs into single runtime protos. | Design defined; prompt scaffolding generated. | active | medium-high |
| WORKSTREAM-12 | Jobs, Agents, AI, and Factory Orchestration | FACT | Generic job templates, deterministic planner, agent capabilities, and production/logistics orchestration. | Prompt 15 generated. | active | high |
| WORKSTREAM-13 | Research, Organizations, Economy, and Policies | FACT | Generic research/tech, org ownership, accounts, macro metrics, and policy constraints. | Prompt 16 generated. | active | medium-high |
| WORKSTREAM-14 | Multiplayer, Netcode, Replay, and Determinism | FACT | Deterministic input/command lockstep, TLV net protocol, replay capture, hash-based desync detection. | Prompts 12 and 17 generated. | active | high |
| WORKSTREAM-15 | GUI, Renderer, View, and UI Framework | FACT | GUI-first minimal smoke path through dsys -> dgfx soft renderer -> dview -> dui -> Dominium game/launcher. | Prompts 8 and 11 generated after user rejected CLI-only testing. | active | critical |
| WORKSTREAM-16 | Toolchain, Editors, and Authoring Pipeline | FACT | World/editor/blueprint/tech/policy/process/transport/structure/item/pack/save/replay/net tools. | Prompt 18 generated. | planned | medium |
| WORKSTREAM-17 | Advanced Simulation Path D | FACT | Dedicated future focus on heat, power grids, fluids, atmosphere, vehicles, structural loads/destruction, and mod-extensible physics. | New-chat starter prompt generated at user request. | active-next | critical |
| WORKSTREAM-18 | Codex Prompt Roadmap and Chat Handoff | FACT | Sequence implementation prompts and produce reusable context/report packages for future chats. | Prompts 1-18 and previous transfer packet generated; current request creates final package. | active | critical |

## 2. Decision Register

| ID | Decision | Status | Evidence / basis | Rationale | Implications | Related workstreams | Confidence | Label |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| DECISION-01 | Domino engine code uses ISO C89. | decided | User starter prompt. | Retro/modern portability and stable ABI. | All engine prompts/code must avoid C99/C++ features. | WORKSTREAM-01 | high | FACT |
| DECISION-02 | Dominium products/tools/UI use portable C++98 subset. | decided | User starter prompt. | Thin portable product layer on top of Domino. | No C++11+, no exceptions/RTTI unless explicitly allowed. | WORKSTREAM-02 | high | FACT |
| DECISION-03 | Simulation must be deterministic and fixed-point. | decided | User starter prompt and repeated design constraints. | Replay, multiplayer lockstep, cross-platform reproducibility. | Use Q formats, deterministic tick order, no platform RNG/floats where determinism matters. | WORKSTREAM-01, WORKSTREAM-14, WORKSTREAM-17 | high | FACT |
| DECISION-04 | All platform services go through dsys. | decided | User starter prompt. | Portability and layering. | No OS headers/API calls in engine except dsys backend layer. | WORKSTREAM-01, WORKSTREAM-02 | high | FACT |
| DECISION-05 | All drawing goes through dgfx/DVIEW/DUI; no OS-native drawing. | decided | User starter prompt. | Renderer abstraction and vector fallback. | GUI/TUI/products must render via engine pipelines. | WORKSTREAM-15 | high | FACT |
| DECISION-06 | Engine/core must not know actual gameplay data definitions. | decided | User explicitly reminded before Prompt 8+ plan. | Modularity and content-driven design. | Actual items/machines/recipes/resources live in packs/mods/TLV, not engine code. | WORKSTREAM-04, WORKSTREAM-10 | high | FACT |
| DECISION-07 | Use Core + Model + Proto + Instance + Registry + TLV pattern across subsystems. | adopted design | Assistant proposal repeatedly used and carried through prompts. | Extensibility without hardcoded systems. | Each subsystem should expose model/registry/proto/save APIs. | WORKSTREAM-01 | medium-high | INFERENCE |
| DECISION-08 | Use subsystem registry for init/tick/save/load orchestration. | planned | Prompt 1. | Plug-in subsystems and subsystem-scoped TLVs. | Core serializer iterates registered descriptors. | WORKSTREAM-01 | medium-high | FACT |
| DECISION-09 | Use unified model registry with model families. | planned | Prompt 1 and extensibility discussion. | Consistent registration for RES/ENV/BUILD/TRANS/VEH/JOB/NET/REPLAY. | Subsystem-specific vtables registered behind generic model descriptors. | WORKSTREAM-01 | medium-high | FACT |
| DECISION-10 | Use TLV schema registry and versioned schemas. | planned | Prompt 1/2/9. | Forward/backward compatibility and validation. | Content/save schemas must register and validate versions. | WORKSTREAM-04 | high | FACT |
| DECISION-11 | Prefer GUI-first validation over CLI-only testing. | decided | User said: 'I want a minimal GUI, I don't want to test in CLI.' | User workflow preference and product visibility. | Prompt 8 establishes GUI smoke path before deep content testing. | WORKSTREAM-15 | high | FACT |
| DECISION-12 | Use a base pack and base_demo mod for data definitions/testing. | planned | Prompts 9-11. | Avoid engine data leakage while enabling demo. | DomPackSet autoloads base if present; demo content in mod TLV. | WORKSTREAM-04, WORKSTREAM-10 | high | FACT |
| DECISION-13 | Transport infrastructure uses arbitrary splines with profiles. | adopted design | User asked for arbitrary endpoints/midpoints; assistant designed spline system. | Unified roads/rails/belts/pipes/chutes/etc.; low CPU. | Profiles define speed/gauge/capacity/max grade; engine remains generic. | WORKSTREAM-08 | high | FACT |
| DECISION-14 | Belts/conveyors should use packets/containers, not per-item tick simulation. | adopted design | User wanted realistic lower-processing belts; assistant proposed packet model. | Performance and realism. | Transport cost O(splines+movers), not O(tiles*items). | WORKSTREAM-08, WORKSTREAM-09 | high | FACT |
| DECISION-15 | Inserters become generic programmable robot manipulators. | adopted design | User asked if inserters may be generic robot arms. | Realistic and general automation. | Job-driven pick/place, deterministic kinematics; no tile-locked tick spam. | WORKSTREAM-08, WORKSTREAM-12 | medium-high | FACT |
| DECISION-16 | Buildings use a local shell/grid initially, placed in world with arbitrary yaw and generated foundations. | adopted design | Building/sloped terrain discussion. | Sims-style construction with manageable path/env computation. | Interior zones and terrain foundations can be derived and saved. | WORKSTREAM-07 | medium-high | INFERENCE |
| DECISION-17 | Vehicles/weapons are designed as blueprints/modules then compiled into single runtime objects. | adopted design | Vehicle/weapon construction discussion. | Player design with runtime performance. | Runtime vehicle is aggregate rigid body with module state. | WORKSTREAM-11 | high | FACT |
| DECISION-18 | Dropped items should be aggregated piles/containers, not thousands of entities. | adopted design | Dropped item discussion. | Performance and deterministic scalability. | World spills are aggregate content states. | WORKSTREAM-09 | high | FACT |
| DECISION-19 | Worldgen providers should be modular and DAG/dependency ordered. | planned | Extensibility discussion and prompts. | Flexible geology/climate/built-env pipelines. | Providers declare dependencies; deterministic chunk populate. | WORKSTREAM-03, WORKSTREAM-06 | medium-high | FACT |
| DECISION-20 | Multiplayer uses deterministic command/input lockstep with TLV protocol. | planned | Prompt 17. | No continuous state replication; replay/debug alignment. | Host/client share initial save and command stream; desync via hashes. | WORKSTREAM-14 | medium-high | FACT |
| DECISION-21 | Toolchain should become full editor/authoring ecosystem. | planned | Prompt 18. | Content expansion requires authoring tools. | Editor suite under Dominium tools, deterministic TLV export. | WORKSTREAM-16 | medium | FACT |
| DECISION-22 | Path D advanced simulation is the next new-chat focus. | decided | User said they will branch into another conversation and focus on D. | Next conversation should not restart base architecture. | Start with advanced simulation architecture or prompt generation. | WORKSTREAM-17 | high | FACT |
| DECISION-23 | Existing code may be stale and must be reconciled, not duplicated. | decided guidance | User said major components may already exist but be out of date before Prompt 8. | Avoid parallel incompatible systems. | Codex prompts should instruct search/update/refactor first. | WORKSTREAM-18 | high | FACT |

## 3. Task Register

| ID | Task | Priority | Urgency | Owner | Dependencies | Inputs needed | Expected output | Next step | Related workstreams | Label |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| TASK-01 | Inspect actual repository before applying any prompt. | critical | immediate | Developer/Codex | None | Repo access/build files | Verified implementation baseline | Run source tree and build inspection. | WORKSTREAM-18 | FACT |
| TASK-02 | If not implemented, apply Prompt 1 core infrastructure. | high | near-term | Codex | Repo inspection | Prompt 1 and existing core code | Subsystem/model/schema/registry scaffolding | Apply/refactor with C89 compliance. | WORKSTREAM-01 | FACT |
| TASK-03 | Implement or reconcile GUI smoke path from Prompt 8. | high | near-term | Codex | Core/render/system code | Available platform backend | Minimal GUI window via dsys/dgfx/dview/dui | Apply Prompt 8; prefer real backend over stub. | WORKSTREAM-15 | FACT |
| TASK-04 | Finalize content model and base pack autoload. | critical | near-term | Codex | Prompt 9 | Existing content/TLV code | Data-only base pack schema and loader | Apply Prompt 9 after core/TLV infra. | WORKSTREAM-04 | FACT |
| TASK-05 | Build data-driven demo loop from packs/mods. | high | near-term | Codex/content author | Prompts 9-10 | TLV content generator/loader | Demo deposit/process/machine/container extraction loop | Apply Prompt 10. | WORKSTREAM-10 | FACT |
| TASK-06 | Add GUI gameplay menu/HUD/blueprint placement. | high | after TASK-05 | Codex | Prompt 11 | GUI smoke path and demo content | GUI-first demo world flow | Apply Prompt 11. | WORKSTREAM-15 | FACT |
| TASK-07 | Add determinism validation and world hash. | high | after demo loop | Codex | Prompt 12 | World/resource/struct state | Hash/replay/debug validators | Apply Prompt 12. | WORKSTREAM-14 | FACT |
| TASK-08 | Start Path D advanced simulation architecture in new chat. | critical | next chat | New assistant | This report/bootstrap prompt | User confirmation only if necessary | Top-level advanced sim architecture | Use Section 15 bootstrap prompt. | WORKSTREAM-17 | FACT |
| TASK-09 | Design fixed-point solvers for heat/power/fluids/atmosphere. | high | Path D phase 1 | New assistant/architect | TASK-08 | Simulation ranges and constraints | Solver plan with tick dependencies | Produce design before coding. | WORKSTREAM-17 | INFERENCE |
| TASK-10 | Reconcile Prompt 13 with Path D architecture. | high | Path D phase 1 | New assistant | Prompt 13 and new design | Existing env/hydro prompts | No duplicate physical systems | Map systems to subsystems/models. | WORKSTREAM-17 | FACT |
| TASK-11 | Generate Codex prompt(s) for Path D implementation if requested. | medium-high | after architecture | Assistant | Path D architecture | Implementation sequencing choice | Prompt 19+ or split prompt series | Ask user if wants architecture-to-Codex conversion. | WORKSTREAM-17 | INFERENCE |
| TASK-12 | Audit engine for domain leakage. | critical | continuous | Developer/Codex | Implemented code | Search terms/list of reserved concepts | Report/remediation PR | Use prompt 12 style validation/audit. | WORKSTREAM-04 | FACT |
| TASK-13 | Prepare future master Project Spec Book aggregation. | medium | later | Aggregator assistant | Per-chat report packages | All old chat packages | Cross-chat spec book and state file | Use aggregator prompt from previous assistant output. | WORKSTREAM-18 | FACT |
| TASK-14 | Preserve this report package with all files and ZIP. | critical | immediate | User | Current output | Download links | Saved per-chat archive | Download and store in chat-specific folder. | WORKSTREAM-18 | FACT |
| TASK-15 | Verify stale external/tool facts before future use. | medium | as needed | Future assistant | Any current API/dependency/law/pricing claim | Web/official docs | Verified current facts | Do not rely on memory for current external data. | WORKSTREAM-18 | FACT |
| TASK-16 | Define exact TLV schema field tables before coding content tools. | high | before content/tooling | Architect/Codex | Prompt 9 and docs | Schema ID conventions | Canonical DATA_FORMATS section | Generate/confirm with user. | WORKSTREAM-04, WORKSTREAM-16 | UNCERTAIN / UNVERIFIED |
| TASK-17 | Decide container nesting policy. | medium | before packaging scale-up | Architect/user | Packaging design | Performance/UX needs | Concrete nesting/packing rules | Resolve during Prompt 14 implementation. | WORKSTREAM-09 | INFERENCE |
| TASK-18 | Select or implement at least one real GUI platform backend. | high | before visual testing | Developer/Codex | Build system/platform targets | SDL2/win32/x11/etc. availability | Renderable soft framebuffer window | Implement under dsys. | WORKSTREAM-15 | UNCERTAIN / UNVERIFIED |

## 4. Constraint Register

| ID | Constraint | Type | Hard/soft | Source / basis | Practical implication | Violation risk | Confidence | Label |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| CONSTRAINT-01 | Domino engine code must be ISO C89. | language | hard | User starter prompt | No C99/C++ constructs in source/domino/**. | high | high | FACT |
| CONSTRAINT-02 | Dominium code must use portable C++98 subset. | language | hard | User starter prompt | Avoid C++11+, exceptions/RTTI unless explicitly approved. | medium | high | FACT |
| CONSTRAINT-03 | Simulation must be deterministic across platforms. | simulation | hard | User starter prompt | Fixed-point math, deterministic tick/order/randomness. | high | high | FACT |
| CONSTRAINT-04 | Use fixed-point Q formats where determinism matters. | math | hard | Starter prompt | Avoid nondeterministic floats in sim/network/replay. | high | high | FACT |
| CONSTRAINT-05 | Platform-specific behavior must be abstracted through dsys. | architecture | hard | Starter prompt | No direct OS APIs in engine core/sim/products where prohibited. | high | high | FACT |
| CONSTRAINT-06 | Rendering must go through dgfx/DVIEW/DUI. | architecture | hard | Starter prompt | No OS-native drawing; soft renderer baseline required. | medium | high | FACT |
| CONSTRAINT-07 | Engine/core must not contain actual content definitions. | content | hard | User explicit reminder | Materials/items/machines/recipes/resources in packs/mods/TLV only. | critical | high | FACT |
| CONSTRAINT-08 | All content formats must be versioned and backward-compatible. | data | hard | Starter prompt | TLV schemas, unknown field handling, migration/version checks. | high | high | FACT |
| CONSTRAINT-09 | Old saves/packs/mods/tools should not be broken. | compatibility | hard | Starter prompt | Stable IDs/ABI, compat profiles, read-only/limited modes. | high | high | FACT |
| CONSTRAINT-10 | GUI/TUI should share logic/pipelines. | ui | hard | Starter prompt | Single widget tree/core; render backend differences only. | medium | high | FACT |
| CONSTRAINT-11 | GUI-first testing is preferred for this workflow. | workflow | soft-to-hard | User explicit before Prompt 8 | Do not only provide CLI/headless tests. | medium | high | FACT |
| CONSTRAINT-12 | World is toroidal 2^24 m surface with ±2 km vertical. | world | hard | Starter prompt | Coords/worldgen/save must respect topology. | medium | high | FACT |
| CONSTRAINT-13 | Target platforms include retro and modern systems. | portability | hard | Starter prompt | Avoid assuming modern GPU/64-bit/threads/filesystem APIs. | high | high | FACT |
| CONSTRAINT-14 | Use vector-only fallback; raster packs optional. | render/content | hard | Starter prompt | Game must function with zero raster packs installed. | medium | high | FACT |
| CONSTRAINT-15 | Packs/mods must be data-driven and registry-based. | content | hard | Conversation decisions | Engine looks up IDs/tags/protos; no hardwired paths. | high | high | FACT |
| CONSTRAINT-16 | Worldgen randomness must be seed/coordinate/tick derived. | determinism | hard | Prompts 10/13/17 | No wall-clock/random platform source in worldgen/sim. | high | high | FACT |
| CONSTRAINT-17 | Network messages must be TLV-encoded/versioned. | net | hard | Prompt 17 | No raw struct dumps over wire. | high | medium-high | FACT |
| CONSTRAINT-18 | Tool outputs must be deterministic. | tools | hard | Prompt 18 | Stable sorted TLVs/assets for identical inputs. | medium | medium-high | FACT |
| CONSTRAINT-19 | No treating assistant proposals as final if user did not accept them. | reporting | hard | User’s current request | Preserve tentative statuses. | high | high | FACT |
| CONSTRAINT-20 | Important items must be labeled FACT/INFERENCE/UNCERTAIN/PROJECT-CONTEXT. | reporting | hard | User’s current request | All reports/registers must include labels. | medium | high | FACT |
| CONSTRAINT-21 | Date anchor is 2026-05-27 Australia/Melbourne. | reporting | hard | User’s current request | Use in report metadata. | low | high | FACT |
| CONSTRAINT-22 | Report scope is this chat only. | reporting | hard | User’s current request | Project-level context must be labeled if used. | medium | high | FACT |
| CONSTRAINT-23 | Generated final package should include specific seven files and ZIP if possible. | artifact | hard | User’s current request | Create downloadable files, no false claims. | low | high | FACT |
| CONSTRAINT-24 | If facts could change externally, verify before future use. | evidence | hard | User’s current request/system instructions | APIs/laws/prices/current products need future verification. | medium | high | FACT |
| CONSTRAINT-25 | Avoid over-engineering past diminishing returns. | architecture | soft | User asked for modular/future-proof without diminishing returns | Prefer stable minimal interfaces over reflection/VM-everything. | medium | medium-high | FACT |

## 5. User Preference Register

| ID | Preference | Source basis | Strength | Implication | Risk if misunderstood | Label |
| --- | --- | --- | --- | --- | --- | --- |
| PREF-01 | Direct, technical, concise style. | explicit | User profile/instructions | high | Future assistants should avoid fluff and focus on engineering detail. | Medium if ignored. |
| PREF-02 | Fact-check and cite when using external facts. | explicit | User profile/instructions | high | Search/verify current external info before relying on it. | High if ignored. |
| PREF-03 | Critical rigor over agreement. | explicit | User profile/instructions | medium-high | Do not rubber-stamp flawed architecture; identify risks. | Medium. |
| PREF-04 | GUI-first minimal testing for this project stage. | explicit | User said they do not want CLI testing only. | high | Prioritize a visible minimal GUI path. | Medium. |
| PREF-05 | Maximum-fidelity handoff/reporting. | explicit | Current request and prior transfer packet request. | high | Preserve details, uncertainty, artifacts, registers. | High. |
| PREF-06 | Long-horizon modular architecture. | inferred | Repeated acceptance of future-proof modular prompts. | medium-high | Design extensible systems but avoid gratuitous abstraction. | Medium. |
| PREF-07 | Codex-ready implementation prompts. | inferred | User repeatedly requested next prompts. | high | Provide explicit work orders when asked. | Low. |
| PREF-08 | No re-explaining base architecture in new chats. | inferred | User asks transfer packet and bootstrap prompt. | medium-high | Use packet as state and continue from focused path. | Medium. |
| PREF-09 | Explicit labels for uncertainty. | explicit | Current request. | high | Mark FACT/INFERENCE/UNCERTAIN/PROJECT-CONTEXT. | High. |
| PREF-10 | Stable IDs and structured reports for aggregation. | explicit | Current request. | high | Use normalized IDs/registers/YAML. | High. |

## 6. Open Questions Register

| ID | Question | Why it matters | Known | Unknown | Resolution path | Priority | Related workstreams | Label |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| QUESTION-01 | Has any Codex prompt been applied to the actual repository? | Determines whether next step is implementation, audit, or architecture. | Prompts were generated in chat. | No repo inspection occurred. | Inspect repository and build logs. | critical | WORKSTREAM-18 | UNCERTAIN / UNVERIFIED |
| QUESTION-02 | Which GUI/backend dependencies are available? | Prompt 8 depends on a real or stubbed window path. | User wants GUI-first. | Actual build/dependency state unknown. | Inspect build system/deps; choose SDL2/win32/x11/etc. | high | WORKSTREAM-15 | UNCERTAIN / UNVERIFIED |
| QUESTION-03 | Should the new chat produce architecture or Codex prompts for Path D first? | User said focus on D but may want design or implementation prompt. | Path D starter prompt asks for architecture first. | Exact desired output in next chat unknown. | Ask only if ambiguous; default to architecture. | high | WORKSTREAM-17 | INFERENCE |
| QUESTION-04 | How strict is the ban on domain words in engine comments/docs? | Prompts evolved from examples to strict no domain leakage. | Engine runtime should be generic. | Whether comments/examples in engine docs are allowed. | Ask user or enforce strict code-only ban. | medium | WORKSTREAM-04 | UNCERTAIN / UNVERIFIED |
| QUESTION-05 | What fixed-point formats should each advanced simulation domain use? | Heat/power/fluids need ranges/scales. | Q16.16/Q24.8 are global defaults. | Domain-specific numeric ranges not designed. | Path D architecture should define them. | high | WORKSTREAM-17 | UNCERTAIN / UNVERIFIED |
| QUESTION-06 | How detailed should initial advanced physics solvers be? | Avoid over-engineering and instability. | Coarse deterministic models preferred. | Accuracy/performance target unknown. | Define minimal stable solver ladder in Path D. | high | WORKSTREAM-17 | UNCERTAIN / UNVERIFIED |
| QUESTION-07 | Should deterministic scripting/DSL be implemented before plugin ABI? | Affects mod-extensibility roadmap. | A deterministic DSL was proposed. | Implementation priority unknown. | Future architecture decision. | medium | WORKSTREAM-04 | UNCERTAIN / UNVERIFIED |
| QUESTION-08 | What build system should Codex modify? | Implementation prompts did not know actual build system. | Desired source dirs known. | CMake/make/custom unknown. | Inspect repo. | high | WORKSTREAM-01 | UNCERTAIN / UNVERIFIED |
| QUESTION-09 | What exact TLV field tags should become canonical? | Prompts include examples, not complete final schema tables. | Versioned TLV required. | Precise tags need consolidation. | Generate DATA_FORMATS spec from prompt sequence and confirm. | medium-high | WORKSTREAM-04 | UNCERTAIN / UNVERIFIED |
| QUESTION-10 | How will retro targets handle GUI smoke tests? | Platform matrix includes DOS/CPM/retro. | GUI-first desired. | Backend feasibility varies. | Design backend-specific fallbacks. | medium | WORKSTREAM-15 | UNCERTAIN / UNVERIFIED |
| QUESTION-11 | What is acceptable nesting depth for containers? | Performance risk. | Limit nesting depth suggested. | Exact policy unknown. | Decide during packaging implementation. | medium | WORKSTREAM-09 | INFERENCE |
| QUESTION-12 | How should existing obsolete code be migrated? | User warned old code may exist. | Prompts say reconcile, not duplicate. | Actual obsolete code unknown. | Repo audit before implementation. | high | WORKSTREAM-18 | UNCERTAIN / UNVERIFIED |

## 7. Artifact Ledger

| ID | Artifact | Type | Purpose | Status | Origin | Carry forward | Notes | Label |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| ARTIFACT-01 | Extended Master Starter Prompt — Dominium + Domino | user prompt | Governing architecture and constraints. | active | User first message | yes | Contains role/tone, platform matrix, subsystem list, repo layout, product model. | FACT |
| ARTIFACT-02 | dres modular resource proposal from another chat | user-provided design | Baseline for resource system. | accepted as baseline in discussion | User pasted long proposal | yes | Four layers: core, models, content protos, interaction systems. | FACT |
| ARTIFACT-03 | Complete integrated system summary | assistant output | Summarized world/resources/env/build/trans/etc. | generated | Assistant response to summary request | yes | Useful for high-level spec book. | FACT |
| ARTIFACT-04 | Data/type hierarchy output | assistant output | Defined IDs, protos, models, instances, systems. | generated | Assistant response | yes | Useful for API/spec sections. | FACT |
| ARTIFACT-05 | Engine-wide hierarchy output | assistant output | Extended pattern to all Domino modules. | generated | Assistant response | yes | Covers dcore/dsys/dgfx/dinput/daudio/dsim/dworld etc. | FACT |
| ARTIFACT-06 | Full stack engine+game+launcher+setup+tools+mods hierarchy | assistant output | Defined product suite and content interactions. | generated | Assistant response | yes | Useful for Dominium spec. | FACT |
| ARTIFACT-07 | Extensibility refinement pass | assistant output | Proposed universal subsystem/model/registry/event/policy extensions. | generated | Assistant response | yes | Captured future-proofing decisions. | FACT |
| ARTIFACT-08 | Codex prompt split plan (7 prompts) | assistant output | Implementation roadmap split under 10 prompts. | generated | Assistant response | yes | Superseded one huge prompt plan. | FACT |
| ARTIFACT-09 | Prompt 1 — Core Infrastructure & Registries | Codex prompt | Subsystem/model/TLV/dynamic registries and docs. | generated | Assistant | yes | First implementation prompt. | FACT |
| ARTIFACT-10 | Prompt 2 — Content & Proto Layer | Codex prompt | Pack/mod manifests, protos, blueprint registry. | generated | Assistant | yes | Defines content scaffolding. | FACT |
| ARTIFACT-11 | Prompt 3 — World/Res/Env/Build/Trans/Struct/Vehicle/Job | Codex prompt | Major world subsystems. | generated | Assistant | yes | Heavy subsystem prompt. | FACT |
| ARTIFACT-12 | Prompt 4 — DSIM/ECS, Net, Replay, View, UI | Codex prompt | Tick/replay/net/view/ui infrastructure. | generated | Assistant | yes | Completes engine scaffolding. | FACT |
| ARTIFACT-13 | Prompt 5 — Dominium Common Layer | Codex prompt | DomSession, paths, instances, compat, packset. | generated | Assistant | yes | Product glue. | FACT |
| ARTIFACT-14 | Prompt 6 — Game Product | Codex prompt | DomGameApp, modes, states, UI, save/load. | generated | Assistant | yes | Game runtime. | FACT |
| ARTIFACT-15 | Prompt 7 — Launcher, Setup, Tools | Codex prompt | Launcher/setup/modcheck/docs. | generated | Assistant | yes | Product suite completion. | FACT |
| ARTIFACT-16 | Prompt 8 — Minimal GUI Vertical Slice | Codex prompt | Soft renderer, dsys window, DVIEW/DUI, game/launcher GUI. | generated | Assistant | yes | Reflects user GUI-first preference. | FACT |
| ARTIFACT-17 | Prompt 9 — Base Pack Structure, TLV Schemas, Autoload | Codex prompt | Base pack and data-only schemas. | generated | Assistant | yes | Important for data/code separation. | FACT |
| ARTIFACT-18 | Prompt 10 — Data-Driven Playable Minimal Slice | Codex prompt | Demo deposit/process/machine/container loop. | generated | Assistant | yes | First gameplay loop. | FACT |
| ARTIFACT-19 | Prompt 11 — Minimal GUI Gameplay Loop | Codex prompt | Menu, camera, HUD, blueprint placement. | generated | Assistant | yes | GUI-driven demo. | FACT |
| ARTIFACT-20 | Prompt 12 — Determinism, Validation, Boundaries | Codex prompt | World hash, replay, validation, debug UI. | generated | Assistant | yes | Architecture hardening. | FACT |
| ARTIFACT-21 | Prompt 13 — World-Scale Physical Systems | Codex prompt | Hydrology/atmosphere/lithosphere/interior volumes. | generated | Assistant | yes | Relevant to Path D. | FACT |
| ARTIFACT-22 | Prompt 14 — Logistics Splines, Construction, Packaging | Codex prompt | Spline/mover/build/packaging framework. | generated | Assistant | yes | Logistics layer. | FACT |
| ARTIFACT-23 | Prompt 15 — Production Chains, Jobs/AI, Economy | Codex prompt | Production, jobs, agents, accounts. | generated | Assistant | yes | Factory orchestration. | FACT |
| ARTIFACT-24 | Prompt 16 — Research, Orgs, Macro-Econ, Policies | Codex prompt | Research/org/econ/policy systems. | generated | Assistant | yes | Progression layer. | FACT |
| ARTIFACT-25 | Prompt 17 — Multiplayer, Netcode, Sessions | Codex prompt | Deterministic lockstep netcode. | generated | Assistant | yes | Multiplayer layer. | FACT |
| ARTIFACT-26 | Prompt 18 — Toolchain & Editors | Codex prompt | Editor/tool suite architecture. | generated | Assistant | yes | Authoring ecosystem. | FACT |
| ARTIFACT-27 | New Chat Advanced Simulation Starter Prompt | bootstrap prompt | Standalone prompt for Path D continuation. | generated | Assistant | yes | Primary bootstrap for next chat if focusing on D. | FACT |
| ARTIFACT-28 | Maximum-fidelity Context Transfer Packet | handoff document | State transfer for retired chat. | generated | Assistant previous answer | yes | Used as source for this package. | FACT |
| ARTIFACT-29 | Final report package request and generated files | report package | Current task output. | in progress | Current user request | yes | This package normalizes IDs and creates files. | FACT |

## 8. Rejected / Superseded Options Register

| ID | Option | Status | Reason | Final/tentative | Reconsider conditions | Related workstreams | Label |
| --- | --- | --- | --- | --- | --- | --- | --- |
| REJECTED-01 | Factorio-style tile/tick belts. | rejected | Too CPU-heavy and arcade-like; user wants realistic low-processing transport. | mostly final | Reconsider only for optional arcade/content pack. | WORKSTREAM-08 | FACT |
| REJECTED-02 | Per-item simulation for bulk logistics. | rejected | Too expensive; containers/packets reduce state count. | final | Use only for rare visible objects. | WORKSTREAM-09 | FACT |
| REJECTED-03 | Hardcoded ore/oil/tree logic in resource core. | rejected | Violates data-driven dres architecture. | final | Never in engine core. | WORKSTREAM-05 | FACT |
| REJECTED-04 | Machine code checking specific resource names. | rejected | Violates generic process/profile model. | final | Never; use tags/protos/TLV. | WORKSTREAM-10 | FACT |
| REJECTED-05 | OS-native drawing in product/UI code. | rejected | Violates dgfx abstraction. | final | Never. | WORKSTREAM-15 | FACT |
| REJECTED-06 | CLI-only validation workflow. | rejected by user | User explicitly wanted minimal GUI. | final for this workflow | Headless remains useful for server/tests, not as only test. | WORKSTREAM-15 | FACT |
| REJECTED-07 | Full per-object general rigid-body simulation for everything. | deprioritised | Too expensive and deterministic-risk; aggregate/simple models preferred. | tentative | Reconsider for limited dynamic subset or editor preview. | WORKSTREAM-17 | INFERENCE |
| REJECTED-08 | Full per-voxel CFD for atmosphere/hydrology. | deprioritised | Too expensive; zone/field/network models preferred. | tentative | Reconsider for localized high-fidelity modules. | WORKSTREAM-06, WORKSTREAM-17 | INFERENCE |
| REJECTED-09 | Forced flat block foundations or terrain leveling. | rejected | User said they do not want ugly foundation blocks/forced leveling. | mostly final | Manual foundation editing may be optional. | WORKSTREAM-07 | FACT |
| REJECTED-10 | Runtime simulation of every vehicle bolt/part. | rejected | Compiled aggregate runtime object preferred for performance. | final | Use detailed graph in designer/editor only. | WORKSTREAM-11 | FACT |
| REJECTED-11 | One huge Codex prompt for entire system. | superseded | User asked split under 10; seven prompts were produced. | final | Only use as reference. | WORKSTREAM-18 | FACT |
| REJECTED-12 | Blindly preserving stale existing code. | rejected | User warned existing components may be out of date. | final | Inspect and reconcile/refactor. | WORKSTREAM-18 | FACT |

## 9. Risk Register

| ID | Risk | Consequence | Likelihood | Severity | Mitigation | Related workstreams | Label |
| --- | --- | --- | --- | --- | --- | --- | --- |
| RISK-01 | Generated prompts may be mistaken for implemented code. | Future assistants may assume nonexistent repo state. | medium | high | Treat all implementation state as UNVERIFIED until repo inspection. | WORKSTREAM-18 | FACT |
| RISK-02 | Domain data leaks into engine code. | Breaks modding/layering and contradicts user instruction. | medium | critical | Audit engine C for domain strings/IDs; move examples to packs/mods/docs. | WORKSTREAM-04 | FACT |
| RISK-03 | Codex uses non-C89/non-C++98 features. | Build/portability failure. | high | high | Explicit prompt constraints and code review. | WORKSTREAM-01, WORKSTREAM-02 | FACT |
| RISK-04 | Existing repo code conflicts with generated architecture. | Duplicate/parallel systems and build breakage. | medium | high | Search/reconcile/update rather than duplicate. | WORKSTREAM-18 | FACT |
| RISK-05 | Advanced simulation becomes too detailed and unstable. | Performance and determinism problems. | medium | high | Use coarse bounded solvers and fixed-point stability analysis. | WORKSTREAM-17 | INFERENCE |
| RISK-06 | TLV schemas fragment into incompatible versions. | Content/save incompatibility. | medium | high | Central schema registry and DATA_FORMATS spec. | WORKSTREAM-04 | FACT |
| RISK-07 | World hash includes pointers/padding. | False desyncs across platforms. | medium | high | Hash logical sorted values only. | WORKSTREAM-14 | FACT |
| RISK-08 | GUI-first path blocked by missing platform backend. | User cannot visually test. | medium | medium-high | Implement soft renderer + at least one dsys backend; stub only temporarily. | WORKSTREAM-15 | UNCERTAIN / UNVERIFIED |
| RISK-09 | Assistant proposals treated as user-decided final specs. | Overwrites tentative design. | medium | medium | Preserve labels and request confirmation when needed. | WORKSTREAM-18 | FACT |
| RISK-10 | Over-abstraction slows implementation. | Architecture may exceed useful modularity. | medium | medium | Follow minimum stable interfaces and avoid reflection/VM-everything unless needed. | WORKSTREAM-01 | INFERENCE |
| RISK-11 | Future aggregator merges conflicting chats prematurely. | Spec book contradictions. | medium | medium-high | Preserve provenance, labels, and conflict registers. | WORKSTREAM-18 | FACT |
| RISK-12 | Retro platform constraints ignored in advanced systems. | Portability failure. | medium | high | Keep memory/fixed-point/backends minimal and feature-scalable. | WORKSTREAM-17 | FACT |
| RISK-13 | Network protocol becomes ad-hoc binary structs. | Endianness/ABI/version failure. | medium | high | Use TLV message schemas only. | WORKSTREAM-14 | FACT |
| RISK-14 | Containers allow unbounded nesting/state explosion. | Performance and save bloat. | medium | medium | Set nesting limits and O(1) bulk defaults. | WORKSTREAM-09 | INFERENCE |
| RISK-15 | Tool outputs non-deterministic packages. | Reproducibility failures. | medium | medium | Sort keys/files/IDs and stable serialize. | WORKSTREAM-16 | FACT |
| RISK-16 | Advanced sim cross-coupling creates circular tick dependencies. | Nondeterministic or unstable tick order. | medium | high | Define dependency graph and fixed solver phases. | WORKSTREAM-17 | INFERENCE |

## 10. Verification Queue

| ID | Item | Why verification is needed | Suggested source/type | Priority | Related workstreams | Label |
| --- | --- | --- | --- | --- | --- | --- |
| VERIFY-01 | Actual repository state and whether any prompts were applied. | Implementation status is unknown. | Repo inspection/build run. | critical | WORKSTREAM-18 | UNCERTAIN / UNVERIFIED |
| VERIFY-02 | Available build system and target configuration. | Prompts need wiring into real build. | Inspect repo build files. | high | WORKSTREAM-01 | UNCERTAIN / UNVERIFIED |
| VERIFY-03 | Availability of GUI backend dependency such as SDL2. | Prompt 8 may depend on it. | Inspect dependencies/build scripts. | high | WORKSTREAM-15 | UNCERTAIN / UNVERIFIED |
| VERIFY-04 | Existing content/TLV code compatibility. | User warned code may be stale. | Search source/domino/content and docs. | high | WORKSTREAM-04 | UNCERTAIN / UNVERIFIED |
| VERIFY-05 | Exact TLV schema IDs and field tags before formal spec. | Examples are not fully canonical. | Generate/validate DATA_FORMATS spec with user. | medium-high | WORKSTREAM-04 | UNCERTAIN / UNVERIFIED |
| VERIFY-06 | Fixed-point numeric ranges for heat/power/fluid solvers. | Advanced simulation stability requires scaling. | Path D design review/tests. | high | WORKSTREAM-17 | UNCERTAIN / UNVERIFIED |
| VERIFY-07 | Whether engine comments/docs may use domain examples. | Domain-neutral rule evolved. | User confirmation or stricter code audit. | medium | WORKSTREAM-04 | UNCERTAIN / UNVERIFIED |
| VERIFY-08 | World hash determinism across platforms. | Replay/net correctness depends on it. | Cross-platform deterministic test suite. | high | WORKSTREAM-14 | UNCERTAIN / UNVERIFIED |
| VERIFY-09 | Retro-target feasibility for memory-heavy systems. | Platform matrix includes constrained targets. | Memory/performance budgets per target. | medium | WORKSTREAM-17 | UNCERTAIN / UNVERIFIED |
| VERIFY-10 | Content validation can catch all references/dependencies. | Mod safety depends on it. | Run modcheck/validators on base/base_demo. | medium-high | WORKSTREAM-04 | UNCERTAIN / UNVERIFIED |
| VERIFY-11 | Dominium Common path/FS wrappers obey dsys abstraction. | Layering risk. | Code review. | medium | WORKSTREAM-02 | UNCERTAIN / UNVERIFIED |
| VERIFY-12 | Networking transport callbacks cover target platforms. | Multiplayer support depends on backend. | Prototype host/client smoke test. | medium | WORKSTREAM-14 | UNCERTAIN / UNVERIFIED |
| VERIFY-13 | Toolchain deterministic output guarantees. | Future SDK quality. | Byte-identical rebuild tests. | medium | WORKSTREAM-16 | UNCERTAIN / UNVERIFIED |
| VERIFY-14 | Whether user wants next chat to generate architecture or prompt for Path D. | Next output alignment. | Ask only if necessary; default architecture. | medium-high | WORKSTREAM-17 | INFERENCE |

## 11. Timeline Register

| Sequence | Event / topic | What changed or was decided | Why it mattered | Current relevance | Confidence |
| --- | --- | --- | --- | --- | --- |
| 01 | User supplied the Extended Master Starter Prompt for Dominium + Domino. | Established global architecture, constraints, directory layout, product model, platforms. | Provided governing context. | Still authoritative. | high |
| 02 | User provided another chat's dres proposal and asked about entities/items/recipes/resource mechanics. | Resource system became first concrete subsystem focus. | Established dres baseline. | Active. | high |
| 03 | Assistant accepted dres as baseline and expanded materials/items/deposits/processes/structures/jobs. | Initial content/resource taxonomy formed. | Useful for content spec but examples must remain data-side. | Active with caveats. | high |
| 04 | User asked how player builds a complete machine workshop. | Assistant described extraction -> processing -> components -> power/logistics/control -> machine assembly. | Defined gameplay progression conceptually. | Background. | high |
| 05 | User requested realistic lower-CPU belts and inserters. | Assistant proposed spline packet belts and robot manipulators. | Set logistics direction. | Active. | high |
| 06 | User expanded to arbitrary spline endpoints/midpoints and packaging. | Assistant proposed unified spline transport and realistic container system. | Established transport+packaging pillars. | Active. | high |
| 07 | User asked about arbitrary buildings, machines inside, off-grid placement, vehicles/weapons, gravity, destruction, dropped items. | Assistant proposed building shells, hybrid placement, compiled vehicles/weapons, constrained gravity/destruction, aggregate piles. | Established construction/physics boundaries. | Active. | high |
| 08 | User asked about hydrology/atmology/lithology with buildings and enclosed spaces plus blueprints/templates/sloped terrain. | Assistant proposed zone graph, env state, portals/materials, blueprint system, realistic foundations. | Established env/building/blueprint terrain model. | Active. | high |
| 09 | User asked integration with previous worldgen/save system. | Assistant mapped new systems into worldgen providers and TLV saves. | Established save/worldgen integration. | Active. | high |
| 10 | User asked if system can be more modular/extensible. | Assistant proposed system-wide registries/models/schema/worldgen DAG. | Set extensibility doctrine. | Active. | high |
| 11 | User asked for whole-system summary and data/type hierarchy. | Assistant produced major summary and hierarchy. | Created source material for spec. | Active. | high |
| 12 | User asked to extend hierarchy to entire engine and product stack. | Assistant mapped Domino modules and Dominium suite. | Full stack architecture defined. | Active. | high |
| 13 | User asked to make whole system more future-proof without diminishing returns. | Assistant refined universal subsystem model, registries, scripting, spatial graph, event bus/policies. | Set extensibility boundaries. | Active. | high |
| 14 | User asked for Codex plan and split under 10 prompts. | Assistant produced large plan then seven-prompt split. | Implementation roadmap created. | Active. | high |
| 15 | User requested Prompt 1 through Prompt 7 sequentially. | Assistant generated detailed Codex prompts 1-7. | Core/product implementation prompts created. | Active artifacts. | high |
| 16 | User corrected direction: minimal GUI desired; engine/core must not know actual data definitions. | Assistant generated Prompt 8+ plan emphasizing GUI-first and base/mod data separation. | Important refinement. | Active. | high |
| 17 | User requested Prompt 8 maximal and then Next repeatedly. | Assistant generated Prompts 8-12. | GUI/content/demo/determinism prompts created. | Active artifacts. | high |
| 18 | User said Yes to Prompt 13. | Assistant generated world-scale physical systems integration prompt. | Advanced env/physical systems prompt created. | Active. | high |
| 19 | User asked what's next and proceeded through prompts 14-17. | Assistant generated logistics, production/jobs, research/org/econ, multiplayer prompts. | Mid/late system prompts created. | Active. | high |
| 20 | User asked what's next after Prompt 17. | Assistant generated Prompt 18 toolchain/editors. | Authoring ecosystem prompt created. | Active. | high |
| 21 | User said they will branch into another conversation focusing on D. | Assistant generated standalone advanced simulation starter prompt. | Set next-chat focus. | Critical. | high |
| 22 | User requested maximum-fidelity Context Transfer Packet. | Assistant produced packet with registers, decisions, tasks, and bootstrap prompt. | Initial handoff created. | Source for current package. | high |
| 23 | User requested final downloadable/shareable report package for this chat. | Current assistant creates normalized files and ZIP. | Transforms CTP into reusable package. | Current. | high |

## 12. Spec Book Contribution Register

| ID | Contribution | Likely spec section | Status | Needs verification? | Label |
| --- | --- | --- | --- | --- | --- |
| SPEC-CONTRIB-01 | C89/C++98 deterministic engine/product split | Project Philosophy / Core Requirements | candidate formal requirement | no | FACT |
| SPEC-CONTRIB-02 | Core+Model+Proto+Instance+Registry+TLV pattern | Architecture Pattern | candidate formal requirement | user confirmation optional | INFERENCE |
| SPEC-CONTRIB-03 | Content in packs/mods, no engine data semantics | Content and Modding | candidate formal requirement | no | FACT |
| SPEC-CONTRIB-04 | GUI-first smoke testing path | Development Workflow | candidate formal requirement | no | FACT |
| SPEC-CONTRIB-05 | Prompt sequence 1-18 | Implementation Roadmap | background/reference | repo state verification needed | FACT |
| SPEC-CONTRIB-06 | Path D advanced simulation focus | Advanced Simulation | active next-workstream | yes, before detailed implementation | FACT |
| SPEC-CONTRIB-07 | Toolchain/editor suite | Authoring Pipeline | planned future chapter | yes | FACT |
