# Registers — Dominium Codex Platform Renderer API Plan

## 1. Workstream Register

| ID | Name | Status | Priority | Label | Objective | Next action | Confidence |
| --- | --- | --- | --- | --- | --- | --- | --- |
| WORKSTREAM-01 | Master deterministic engine-core refactor prompts 1-14 | assumed prerequisite / historical active plan | high | FACT | Establish deterministic core primitives: packets, scheduler, fields/events, LOD, arbitrary placement, TRANS, STRUCT, DECOR, agents, graph toolkit, domains/frames/propagators, knowledge/fog/comms, and regression hardening. | Verify repository state if implementation-specific actions are needed. | 4 |
| WORKSTREAM-02 | Post-master platforms/renderers/APIs/product completion prompt pack | active | critical | FACT | Produce and preserve a ready-to-run Codex prompt pack to complete platforms, renderers, APIs, build/test infrastructure, and basic launcher/game GUI smoke tests. | Run Prompt 1 in Codex or, if already run, continue with the next unexecuted prompt. | 5 |
| WORKSTREAM-03 | API architecture: stable ABI, facades, backends, capabilities, determinism | active design requirement | critical | FACT | Make DSYS/DGFX and other evolvable systems modular, versioned, extensible, deterministic, and C89/C++98-compliant. | Execute Prompt 1 and Prompt 2. | 5 |
| WORKSTREAM-04 | AAA future readiness roadmap | future roadmap / not current implementation scope | medium-high | FACT | Reserve clean architectural slots for advanced future game/engine features beyond the current prompt pack. | Do not implement now; preserve as future Project Spec Book material. | 4 |
| WORKSTREAM-05 | Chat-specific handoff/report packaging | active in current response | high | FACT | Produce a downloadable, shareable, reusable report package for this old chat, suitable for future aggregation and Project Spec Book construction. | Download and store the ZIP and individual files. | 5 |

## 2. Decision Register

| ID | Decision | Status | Evidence / basis | Rationale | Implications | Related workstream | Confidence | Label |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| DECISION-01 | Use C89 for Domino core forever. | decided | User mandatory constraint. | Old-platform compatibility and ABI stability. | All Domino public/core code must be C89-clean. | WORKSTREAM-03 | 5 | FACT |
| DECISION-02 | Use C++98 for Dominium layer forever. | decided | User mandatory constraint. | Long-term compatibility. | No C++11 baseline leakage. | WORKSTREAM-03 | 5 | FACT |
| DECISION-03 | C99/C11/C++11+ are optional acceleration layers only. | decided | User mandatory constraint. | Correctness cannot require newer standards. | Modern preset cannot remove baseline paths. | WORKSTREAM-03 | 5 | FACT |
| DECISION-04 | Reject runtime language-standard switching. | decided | User explicitly required rejecting runtime C89 vs C11 switching. | Language standard is compile-time concern. | Launcher profiles select features/backends only. | WORKSTREAM-03 | 5 | FACT |
| DECISION-05 | All ABI-relevant boundaries use C ABI, POD structs, explicit function tables. | decided | User mandatory stable ABI requirement. | Avoid compiler/RTTI/STL incompatibility. | No C++ types/templates/exceptions across ABI boundaries. | WORKSTREAM-03 | 5 | FACT |
| DECISION-06 | Every interface struct begins with u32 abi_version and u32 struct_size. | decided | User mandatory stable ABI rule. | Versioned compatibility and size negotiation. | All vtables/interfaces must follow template. | WORKSTREAM-03 | 5 | FACT |
| DECISION-07 | Use facade + backend architecture for all evolvable subsystems. | decided | User mandatory rule. | Allows baseline/stub/optimized backends. | Platform facets, renderer, jobs, SIMD, IO streaming follow this pattern. | WORKSTREAM-03 | 5 | FACT |
| DECISION-08 | Use a centralized capability registry for backend selection. | decided | User mandatory rule and Prompt 2. | Selection must be deterministic and inspectable. | All backends declare OS/ISA, determinism, perf class. | WORKSTREAM-03 | 5 | FACT |
| DECISION-09 | Use determinism grades D0/D1/D2. | decided | User mandatory rule. | Prevents silent downgrade. | Lockstep refuses non-D0 for lockstep-relevant backends. | WORKSTREAM-03 | 5 | FACT |
| DECISION-10 | Lockstep strict requires D0 only. | decided | User mandatory rule. | Guarantees bit-exact authoritative simulation. | D1/D2 backends presentation-only or rejected. | WORKSTREAM-03 | 5 | FACT |
| DECISION-11 | Treat serialization/assets/saves/replays as public ABI. | decided | User mandatory rule. | Long-term compatibility. | One TLV container, skip-unknown, migrations. | WORKSTREAM-02 | 5 | FACT |
| DECISION-12 | Networking handshake must include build/schema/determinism/content hashes. | decided | User mandatory rule. | Avoid mixed-version undefined behavior. | Mixed sessions rejected unless compatibility table allows. | WORKSTREAM-02 | 5 | FACT |
| DECISION-13 | Launcher profiles select feature profiles/backends, not language standards. | decided | User mandatory and Prompt 2. | User-facing configurability without correctness changes. | --profile and --lockstep-strict become selection inputs. | WORKSTREAM-02 | 5 | FACT |
| DECISION-14 | Final active plan is the 9-prompt post-master pack. | decided | Latest user asked to start with prompt 1; assistant generated prompts 1-9. | Fewer larger prompts preferred. | Supersedes earlier 15-24 and 15-28 plans. | WORKSTREAM-02 | 5 | FACT |
| DECISION-15 | Codex must make detailed commits throughout. | decided | User requested commits for changelog later. | Changelog extraction. | Every prompt includes commit discipline. | WORKSTREAM-02 | 5 | FACT |
| DECISION-16 | Tier-1 platform completion focuses on Win32 and Win32 headless. | decided | User platform tier and final Prompt 4. | MVP validation on Windows Codex runtime. | System smoke tests required. | WORKSTREAM-02 | 5 | FACT |
| DECISION-17 | Software renderer is D0 reference backend. | decided | User renderer tier and final Prompt 5. | Deterministic pixel-hash reference. | Soft renderer required for lockstep-safe tests. | WORKSTREAM-02 | 5 | FACT |
| DECISION-18 | DX9 is Tier-1 runtime-present backend. | decided | User renderer tier and final Prompt 5. | Early Windows graphics MVP. | DX9 demo required, likely D2. | WORKSTREAM-02 | 5 | FACT |
| DECISION-19 | Tier-2 platforms/renderers are gated and compile-correct in current pack. | decided with caveat | Final Prompt 6. | Windows Codex cannot run native POSIX/macOS. | May need later runtime prompts if user wants full Tier-2 runtime. | WORKSTREAM-02 | 4 | FACT |
| DECISION-20 | Launcher and game need basic GUI smoke tests. | decided | User request and final Prompt 8. | Product done must prove integration. | --smoke-gui flags required. | WORKSTREAM-02 | 5 | FACT |
| DECISION-21 | Future AAA features are extension/capability slots, not immediate implementation scope. | decided for current plan | Assistant recommendation accepted implicitly by moving to prompt pack; no user objected. | Avoid bloating current pack. | Graphics/audio/AI/etc remain future spec material. | WORKSTREAM-04 | 4 | INFERENCE |
| DECISION-22 | This report package chat label is inferred as Dominium Codex Platform Renderer API Plan. | decided for packaging | User did not provide chat label; prompt says infer one. | Consistent filenames. | Can be renamed later if desired. | WORKSTREAM-05 | 5 | INFERENCE |

## 3. Task Register

| ID | Task | Priority | Urgency | Owner | Dependencies | Inputs needed | Expected output | Recommended next step | Related workstream | Label |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| TASK-01 | Verify whether MASTER prompts 1-14 were implemented in the repository. | high | before implementation-specific assumptions | future assistant/Codex | WORKSTREAM-01 | Repo access, Build logs | Verified status of prerequisite engine-core work. | Inspect repo; run searches/builds. | WORKSTREAM-01 | UNCERTAIN / UNVERIFIED |
| TASK-02 | Run or hand off final Prompt 1. | critical | first implementation step | Codex | WORKSTREAM-02 | Final Prompt 1 text, Repo | Baseline enforcement, abi.h, DSYS/DGFX facades, docs, commits. | Execute in Codex at repo path. | WORKSTREAM-02, WORKSTREAM-03 | FACT |
| TASK-03 | Run final Prompt 2. | critical | after Prompt 1 | Codex | TASK-02 | Prompt 2 | Capability registry, determinism grades, launcher profiles. | Execute after Prompt 1 passes. | WORKSTREAM-02, WORKSTREAM-03 | FACT |
| TASK-04 | Run final Prompt 3. | high | after Prompt 2 | Codex | TASK-03 | Prompt 3 | Presets, null backends, config header, build metadata, verify skeleton. | Execute after Prompt 2 passes. | WORKSTREAM-02 | FACT |
| TASK-05 | Run final Prompt 4. | high | after Prompt 3 | Codex | TASK-04 | Prompt 4 | Win32/win32_headless DSYS complete; domino_sys_smoke. | Execute and verify both platforms. | WORKSTREAM-02 | FACT |
| TASK-06 | Run final Prompt 5. | high | after Prompt 4 | Codex | TASK-05 | Prompt 5 | Soft D0 renderer, DX9 present, dgfx_demo. | Execute and verify soft hash + DX9 demo. | WORKSTREAM-02 | FACT |
| TASK-07 | Run final Prompt 6. | medium-high | after Prompt 5 | Codex | TASK-06 | Prompt 6 | Tier-2 gating and compile correctness. | Execute gating and optional backend compile checks. | WORKSTREAM-02 | FACT |
| TASK-08 | Run final Prompt 7. | high | after Prompt 6 | Codex | TASK-07 | Prompt 7 | TLV container, net handshake, schema IDs, tests. | Execute and run regression tests. | WORKSTREAM-02 | FACT |
| TASK-09 | Run final Prompt 8. | critical | after Prompt 7 | Codex | TASK-08 | Prompt 8 | Launcher/game GUI smokes and end-to-end verify script. | Execute; scripts\build_codex_verify.bat must pass. | WORKSTREAM-02 | FACT |
| TASK-10 | Run final Prompt 9. | medium | after Prompt 8 | Codex | TASK-09 | Prompt 9 | Changelog pipeline and release-note process. | Execute after done gates pass. | WORKSTREAM-02 | FACT |
| TASK-11 | Preserve AAA future feature roadmap for later Project Spec Book. | medium | after current foundation | future assistant/user | WORKSTREAM-04 | Roadmap items from this chat | Future-phase requirements/background material. | Do not implement now unless user asks. | WORKSTREAM-04 | FACT |
| TASK-12 | Create final downloadable chat report package. | high | now | assistant | Previous transfer packet, Visible chat context | This chat context | Markdown/YAML files plus ZIP. | Generate files and links. | WORKSTREAM-05 | FACT |
| TASK-13 | Resolve DSYS vs domino_sys policy if repo conflict occurs. | high | only if blocker appears | user/Codex | Prompt 1 repo discovery | Callsite/header scan | Policy decision: shim indefinitely vs migrate. | Use Prompt 1 stop-and-ask. | WORKSTREAM-03 | FACT |
| TASK-14 | Resolve smoke UI text strategy if needed. | medium | Prompt 5 or 8 | user/Codex | IR/UI scan | Existing text/font code | Bitmap font, rectangles only, or UI toolkit path. | Use stop-and-ask. | WORKSTREAM-02 | FACT |
| TASK-15 | Confirm exact launcher/game target names. | high | Prompt 8 | Codex/user | CMake target list | cmake --build --target help | Correct smoke executable invocation. | Use Prompt 8 stop-and-ask if unknown. | WORKSTREAM-02 | FACT |

## 4. Constraint Register

| ID | Constraint | Type | Hard/soft | Source / basis | Practical implication | Violation risk | Confidence | Label |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| CONSTRAINT-01 | Codex runtime OS is Windows. | runtime | hard | User | Validation commands target Windows; POSIX/macOS backends must be gated. | medium | 5 | FACT |
| CONSTRAINT-02 | Repo path is c:\Inbox\Git Repos\dominium. | runtime | hard | User | All prompts use this path. | low | 5 | FACT |
| CONSTRAINT-03 | Approval policy is NEVER. | process | hard | User | Prompts cannot require interactive approvals. | medium | 5 | FACT |
| CONSTRAINT-04 | Network enabled but no dependency downloads unless explicitly approved. | dependency | hard | User | CMake must not fetch deps. | high | 5 | FACT |
| CONSTRAINT-05 | Repo must remain buildable after each prompt. | build | hard | User | No big-bang broken states. | high | 5 | FACT |
| CONSTRAINT-06 | Domino core ISO C89 baseline forever. | language | hard | User | Core/public C headers must remain C89-clean. | high | 5 | FACT |
| CONSTRAINT-07 | Dominium layer C++98 baseline forever. | language | hard | User | No C++11 baseline constructs. | high | 5 | FACT |
| CONSTRAINT-08 | Modern standards are optional acceleration only. | language | hard | User | Correctness cannot depend on C11/C++11. | medium | 5 | FACT |
| CONSTRAINT-09 | No runtime language-standard switching. | compatibility | hard | User | Launcher profiles cannot select C89/C11. | low | 5 | FACT |
| CONSTRAINT-10 | Stable ABI uses C ABI, POD, no C++ boundary types. | ABI | hard | User | All plugin/cross-DLL interfaces use function tables. | high | 5 | FACT |
| CONSTRAINT-11 | Every interface begins with u32 abi_version and u32 struct_size. | ABI | hard | User | Vtables/interfaces must follow template. | medium | 5 | FACT |
| CONSTRAINT-12 | No floating point in deterministic core. | determinism | hard | User/master plan | Use fixed-point/integers in sim. | high | 5 | FACT |
| CONSTRAINT-13 | No grid assumptions in core placement/world systems. | simulation | hard | User/master plan | Pose/anchor systems must be arbitrary/quantized. | high | 5 | FACT |
| CONSTRAINT-14 | No tolerance solvers in deterministic core. | determinism | hard | User/master plan | Avoid non-deterministic numeric solvers. | high | 5 | FACT |
| CONSTRAINT-15 | Lockstep strict requires D0 bit-exact backends for lockstep-relevant subsystems. | determinism | hard | User | Registry must refuse non-D0. | high | 5 | FACT |
| CONSTRAINT-16 | Serialization formats are public ABI. | compatibility | hard | User | TLV/version/migration/skip-unknown required. | high | 5 | FACT |
| CONSTRAINT-17 | This report covers this chat only. | reporting | hard | User | Do not summarize whole Project except labelled project context. | medium | 5 | FACT |
| CONSTRAINT-18 | Important items must be labelled FACT/INFERENCE/UNCERTAIN/PROJECT-CONTEXT. | reporting | hard | User | Avoid unlabelled inference. | medium | 5 | FACT |
| CONSTRAINT-19 | Create downloadable files and ZIP if tools available. | reporting | hard | User | Must not claim files saved unless created. | low | 5 | FACT |
| CONSTRAINT-20 | Preserve superseded/rejected/deprioritised options. | reporting | hard | User | Future aggregators need lineage. | medium | 5 | FACT |
| CONSTRAINT-21 | Direct user statements outrank assistant suggestions. | evidence | hard | User | Assistant proposals are not decisions unless accepted. | medium | 5 | FACT |
| CONSTRAINT-22 | No new third-party dependencies in prompts unless approved. | dependency | hard | User | Use existing vendored/system deps only. | high | 5 | FACT |
| CONSTRAINT-23 | Prefer fewer larger Codex prompts. | process | soft/hard for plan | User | Final plan consolidated to 9 prompts. | low | 5 | FACT |
| CONSTRAINT-24 | Codex commits throughout with detailed bodies. | process | hard | User | Every prompt includes commit discipline. | medium | 5 | FACT |

## 5. User Preference Register

| ID | Preference | Source basis | Strength | Implication | Risk if misunderstood | Label |
| --- | --- | --- | --- | --- | --- | --- |
| PREFERENCE-01 | Direct, dense, no-filler assistance. | User profile/instructions | explicit | Use concise, structured responses. | If misunderstood, assistant may waste user time. | FACT |
| PREFERENCE-02 | Rigorously tested facts and correctly cited sources when factual/current. | User profile | explicit | Verify unstable facts; cite if using web/files. | Overconfident claims reduce trust. | FACT |
| PREFERENCE-03 | Prefer fewer larger Codex prompts. | User statement | explicit | Do not split final pack into many small prompts unless needed. | Too many prompts slow workflow. | FACT |
| PREFERENCE-04 | Codex prompts must be ready-to-run and self-contained. | Initial request | explicit | Each prompt restates context, commands, tasks, acceptance. | Codex may fail or ask questions unnecessarily. | FACT |
| PREFERENCE-05 | Repo must remain buildable after each prompt. | Initial request | explicit | Incremental implementation and verification. | Broken intermediate states unacceptable. | FACT |
| PREFERENCE-06 | Git commits throughout with detailed bodies. | User request | explicit | Prompts require commit discipline. | Changelog generation harder. | FACT |
| PREFERENCE-07 | Long-term extensibility and AAA readiness. | Repeated user requests | explicit | Reserve extension slots and avoid core bloat. | Future rewrite risk. | FACT |
| PREFERENCE-08 | Avoid re-asking already answered questions. | System/user style and this handoff request | explicit/inferred | Use this packet as continuity source. | User frustration and lost continuity. | INFERENCE |
| PREFERENCE-09 | Preserve uncertainty and rejected options. | Current packaging prompt | explicit | Use labels and registers. | Bad aggregation/spec errors. | FACT |
| PREFERENCE-10 | Start messages with model version/build date. | User profile instruction | explicit | Future assistant should comply unless system conflicts. | Style mismatch. | FACT |

## 6. Open Questions Register

| ID | Question / issue | Why it matters | Known information | Unknown information | What would resolve it | Priority | Related workstream | Label |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| QUESTION-01 | Were MASTER prompts 1-14 actually implemented in the repo? | Post-14 plan assumes them. | User says a prior prompt plan exists. | Actual repo state. | Inspect repo/build/history. | high | WORKSTREAM-01 | UNCERTAIN / UNVERIFIED |
| QUESTION-02 | Which DSYS API is authoritative if dsys_* and domino_sys_* conflict? | Prompt 1 refactor depends on it. | User said both surfaces exist. | Actual callsite distribution and desired compatibility policy. | Repo search; stop-and-ask. | high | WORKSTREAM-03 | FACT |
| QUESTION-03 | Which headers are baseline-visible? | Header checker scope. | Likely include/ public headers. | Exact exclusions/generated/vendor handling. | Repo inspection. | high | WORKSTREAM-03 | UNCERTAIN / UNVERIFIED |
| QUESTION-04 | Do public headers currently contain C99/C++11 constructs? | Prompt 1 may fail if violations exist. | Baseline rules are required. | Actual code. | Run checker/grep. | high | WORKSTREAM-03 | UNCERTAIN / UNVERIFIED |
| QUESTION-05 | What are exact launcher and game target/executable names? | Prompt 8 needs correct commands. | User listed likely targets including dominium-launcher and dominium_game. | Actual generated target names. | cmake --build --target help. | high | WORKSTREAM-02 | UNCERTAIN / UNVERIFIED |
| QUESTION-06 | Is there an existing UI toolkit? | Determines smoke GUI implementation. | Prompts allow immediate-mode dgfx primitives. | Actual UI layer status. | Search repo. | medium | WORKSTREAM-02 | UNCERTAIN / UNVERIFIED |
| QUESTION-07 | What is Tier-1 UI text strategy? | Smoke UI may need text. | Prompt allows optional title text or rectangles. | Existing font/text support. | Search repo; stop-and-ask. | medium | WORKSTREAM-02 | FACT |
| QUESTION-08 | Win32 path encoding policy: UTF-8 or UTF-16 internally? | Filesystem correctness. | Win32 platform facet must implement paths. | Project policy. | Inspect docs; ask if absent. | medium | WORKSTREAM-02 | FACT |
| QUESTION-09 | Minimum process feature: spawn+wait or stdout/stderr capture now? | Prompt 4 process scope. | Prompt handles unsupported if not declared. | User preference if API declares capture. | Inspect sys header; ask if complex. | medium | WORKSTREAM-02 | FACT |
| QUESTION-10 | Minimum networking facet: TCP only or TCP+UDP? | Prompt 4 net scope. | Sockets planned. | Exact Tier-1 required API. | Inspect headers/specs; ask. | medium | WORKSTREAM-02 | FACT |
| QUESTION-11 | Which legacy file formats must remain readable immediately? | Prompt 7 migrations. | TLV-as-ABI required. | Existing format list. | Search repo/docs; ask if complex. | high | WORKSTREAM-02 | FACT |
| QUESTION-12 | Does an existing networking join path exist? | Prompt 7 handshake integration. | Handshake required. | Where to wire it. | Search net code; create demo if absent. | medium | WORKSTREAM-02 | UNCERTAIN / UNVERIFIED |
| QUESTION-13 | Is full Tier-2 runtime completion required now or is compile-gated coverage acceptable? | User said fully complete; Prompt 6 gates compile correctness. | Current final pack chooses gated compile correctness. | User acceptance for runtime full Tier-2. | Clarify only if user reopens scope. | medium | WORKSTREAM-02 | INFERENCE |
| QUESTION-14 | Should D3D12 be added in a later prompt phase? | User mentioned future advanced graphics; current dgfx excludes D3D12. | D3D12 planned in docs per user statement. | Whether/when to implement. | Future planning. | low | WORKSTREAM-04 | FACT |
| QUESTION-15 | Does existing changelog format need preservation? | Prompt 9 generator output format. | Prompt creates CHANGELOG_DRAFT. | Existing CHANGELOG policy. | Inspect repo; ask if needed. | low | WORKSTREAM-02 | FACT |

## 7. Artifact Ledger

| ID | Artifact / file / prompt / output | Type | Purpose | Status | Where it came from | Carry forward? | Notes | Label |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| ARTIFACT-01 | Previous maximum-fidelity Context Transfer Packet | report | Base handoff for this package | consumed and repaired | Assistant response in this chat | yes | Contained sections 0-18; used as primary source. | FACT |
| ARTIFACT-02 | MASTER CODEX PROMPT PLAN prompts 1-14 | prompt plan | Prior deterministic engine-core refactor | assumed prerequisite; implementation unverified | User pasted | yes | Covers invariants, packets, scheduler, fields, LOD, pose, TRANS, STRUCT, DECOR, AI, graphs, domains, knowledge, determinism. | FACT |
| ARTIFACT-03 | /mnt/data/dominium.zip | uploaded repo archive | Repo copy provided by user | uploaded; contents unverified in this chat | User upload | yes | File ID file-5jr5EtLr5Sj6Wz5g5WcbuX. | FACT |
| ARTIFACT-04 | Initial questionnaire and user answers | planning input | Defined platforms/renderers/APIs/done/build context | used | User/assistant exchange | yes | User gave detailed platform tiers and render tiers. | FACT |
| ARTIFACT-05 | Initial assistant platform/render prompt pack 1-14 | prompt plan | Early platforms/renderers/APIs implementation plan | superseded | Assistant | historical | Replaced by later final pack. | FACT |
| ARTIFACT-06 | Post-engine plan prompts 15-24 | prompt plan | First post-master API/platform/render continuation | superseded | Assistant | historical | Replaced by injected constraints and final pack. | FACT |
| ARTIFACT-07 | User injected mandatory constraints | requirements text | Hard constraints for language/ABI/facades/caps/determinism/TLV/CI | integrated | User | yes | Dated in pasted text as GPT-5.2 Thinking — Build 2025-12-15. | FACT |
| ARTIFACT-08 | Revised post-14 prompts 15-28 | prompt plan | Expanded plan with injected constraints | superseded | Assistant | historical | Consolidated into final 9-prompt pack. | FACT |
| ARTIFACT-09 | Final Prompt 1 — Baseline enforcement + ABI/vtable + facades + commits | Codex prompt | First active implementation prompt | active | Assistant | yes | Includes docs, config headers, abi.h, DSYS/DGFX facades, jobs/SIMD/IO templates. | FACT |
| ARTIFACT-10 | Final Prompt 2 — Capability registry + determinism grades + launcher profiles | Codex prompt | Second active implementation prompt | active | Assistant | yes | Central registry, D0/D1/D2, profiles, backend registration. | FACT |
| ARTIFACT-11 | Final Prompt 3 — CMake switchboard + presets + null backends + build metadata | Codex prompt | Third active implementation prompt | active | Assistant | yes | Baseline/modern presets, null platform/renderer, build metadata, verify skeleton. | FACT |
| ARTIFACT-12 | Final Prompt 4 — Tier-1 platform Win32/win32_headless + system smoke | Codex prompt | Fourth active implementation prompt | active | Assistant | yes | Completes DSYS facets and domino_sys_smoke. | FACT |
| ARTIFACT-13 | Final Prompt 5 — Tier-1 renderer soft + DX9 + dgfx_demo | Codex prompt | Fifth active implementation prompt | active | Assistant | yes | Soft D0 hash test, DX9 present, demo harness. | FACT |
| ARTIFACT-14 | Final Prompt 6 — Tier-2 platform/render gating + compile correctness | Codex prompt | Sixth active implementation prompt | active | Assistant | yes | POSIX/X11/Wayland/Cocoa and DX11/GL2/VK1/Metal gating. | FACT |
| ARTIFACT-15 | Final Prompt 7 — TLV-as-ABI + net handshake + schema IDs + tests | Codex prompt | Seventh active implementation prompt | active | Assistant | yes | Container/TLV library, migrations, handshake, tests. | FACT |
| ARTIFACT-16 | Final Prompt 8 — Launcher/game GUI smoke + verify script | Codex prompt | Eighth active implementation prompt | active | Assistant | yes | Product done gates and end-to-end verification. | FACT |
| ARTIFACT-17 | Final Prompt 9 — Changelog pipeline + release notes automation | Codex prompt | Ninth active implementation prompt | active | Assistant | yes | Commit conventions, changelog generator, release process. | FACT |
| ARTIFACT-18 | README-style bootstrap prompt for new chat | prompt | New chat continuation instructions | created in transfer packet | Assistant | yes | Contains active plan and constraints. | FACT |
| ARTIFACT-19 | Manual verification checklist | checklist | Before relying on handoff | created in transfer packet | Assistant | yes | Includes repo inspection/build steps. | FACT |
| ARTIFACT-20 | AAA future feature roadmap | brainstorm/architecture notes | Future Project Spec Book material | not current implementation scope | User questions + assistant answers | yes | Graphics/audio/input/AI/nav/terrain/vehicles/economy/combat/weather/tools/modding. | FACT |
| ARTIFACT-21 | dominium_codex_platform_renderer_api_plan__01_full_chat_report.md | generated report file | Main human-readable report | created now | This response | yes | Downloadable file. | FACT |
| ARTIFACT-22 | dominium_codex_platform_renderer_api_plan__02_spec_sheet.yaml | generated YAML file | Structured data for future spec book | created now | This response | yes | Downloadable file. | FACT |
| ARTIFACT-23 | dominium_codex_platform_renderer_api_plan__03_aggregator_packet.md | generated report file | Compact cross-chat aggregation packet | created now | This response | yes | Downloadable file. | FACT |
| ARTIFACT-24 | dominium_codex_platform_renderer_api_plan__04_registers.md | generated registers file | All normalized tables | created now | This response | yes | Downloadable file. | FACT |
| ARTIFACT-25 | dominium_codex_platform_renderer_api_plan__05_reader_brief.md | generated brief | Short human-readable version | created now | This response | yes | Downloadable file. | FACT |
| ARTIFACT-26 | dominium_codex_platform_renderer_api_plan__06_verification_and_audit.md | generated audit file | Quality-control record | created now | This response | yes | Downloadable file. | FACT |
| ARTIFACT-27 | dominium_codex_platform_renderer_api_plan__manifest.md | generated manifest | Package inventory and counts | created now | This response | yes | Downloadable file. | FACT |
| ARTIFACT-28 | dominium_codex_platform_renderer_api_plan__handoff_package.zip | generated zip | Downloadable package archive | created now | This response | yes | ZIP bundle. | FACT |

## 8. Rejected / Superseded Options Register

| ID | Option | Status | Reason rejected/superseded/deprioritised | Is rejection final? | Reconsider conditions | Related workstream | Label |
| --- | --- | --- | --- | --- | --- | --- | --- |
| REJECTED-01 | Runtime C89 vs C11/C++ standard switching. | rejected | User explicitly rejected; standards are compile-time. | final | Only if user reverses mandatory rule. | WORKSTREAM-03 | FACT |
| REJECTED-02 | CMake dependency downloads. | rejected | User forbids downloads unless approved. | final | With explicit user approval. | WORKSTREAM-02 | FACT |
| REJECTED-03 | C++ ABI boundaries. | rejected | User requires C ABI/POD/function tables. | final | Not for cross-module/plugin ABI. | WORKSTREAM-03 | FACT |
| REJECTED-04 | Monolithic platform API as long-term architecture. | superseded | User requires facade/backend and platform facets. | final for new architecture | Only as legacy shim. | WORKSTREAM-03 | FACT |
| REJECTED-05 | Single fast path only. | rejected | User explicitly prohibited. | final | Never for correctness-critical paths. | WORKSTREAM-03 | FACT |
| REJECTED-06 | Silent determinism downgrade. | rejected | User explicitly prohibited. | final | Never. | WORKSTREAM-03 | FACT |
| REJECTED-07 | Unversioned serialization formats. | rejected | User required TLV/versioning. | final | Never. | WORKSTREAM-02 | FACT |
| REJECTED-08 | Advanced graphics/audio directly in core API. | superseded | Extension/caps model chosen. | final for current architecture | If future user explicitly changes API philosophy. | WORKSTREAM-04 | INFERENCE |
| REJECTED-09 | Renderer/audio output feeding simulation. | rejected | Would violate deterministic sim. | final | Never for authoritative lockstep. | WORKSTREAM-04 | INFERENCE |
| REJECTED-10 | Full Vulkan implementation in current pack. | deprioritised | Prompt 6 only gates/compile-fixes VK1. | tentative | Later advanced renderer phase. | WORKSTREAM-02, WORKSTREAM-04 | FACT |
| REJECTED-11 | D3D12 as current pack backend. | deprioritised | User said D3D12 planned but not current dgfx contract. | tentative | Future renderer phase. | WORKSTREAM-04 | FACT |
| REJECTED-12 | Runtime validation of Linux/macOS backends on Windows Codex. | deprioritised | Not possible in Windows runtime. | final for current Codex environment | Native CI or later platform-specific sessions. | WORKSTREAM-02 | FACT |
| REJECTED-13 | Initial assistant platform/render prompt pack as active plan. | superseded | Later final 9-prompt pack replaced it. | final | Historical only. | WORKSTREAM-02 | FACT |
| REJECTED-14 | Post-engine prompts 15-24 as active plan. | superseded | Injected constraints and optimized pack replaced it. | final | Historical only. | WORKSTREAM-02 | FACT |
| REJECTED-15 | Revised prompts 15-28 as active plan. | superseded | Consolidated into fewer larger prompts 1-9. | final | Re-expand only if Codex needs smaller prompts. | WORKSTREAM-02 | FACT |

## 9. Risk Register

| ID | Risk / failure mode | Consequence | Likelihood | Severity | Mitigation | Related workstream | Label |
| --- | --- | --- | --- | --- | --- | --- | --- |
| RISK-01 | Repo-specific claims may be wrong because uploaded zip was not inspected. | Future assistant may implement against wrong file paths/API assumptions. | medium | high | Verify repo/archive before implementation-specific claims. | WORKSTREAM-01, WORKSTREAM-02 | UNCERTAIN / UNVERIFIED |
| RISK-02 | MASTER prompts 1-14 may not actually be implemented. | Post-14 prompts may fail due missing prerequisites. | medium | high | Run verification searches/builds before execution. | WORKSTREAM-01 | UNCERTAIN / UNVERIFIED |
| RISK-03 | Final pack may not satisfy 'fully complete' for Tier-2 runtime backends. | User may expect runtime X11/Wayland/Cocoa/DX11/GL2/VK/Metal completion rather than compile-gated coverage. | medium | medium-high | Clarify if user reopens scope; add future runtime prompts. | WORKSTREAM-02 | INFERENCE |
| RISK-04 | Baseline header checker may flag many existing violations. | Prompt 1 could become larger than expected. | medium | high | Use stop-and-ask if rewriting/moving/deleting declarations needs policy. | WORKSTREAM-03 | INFERENCE |
| RISK-05 | Legacy DSYS vs new DSYS surface conflict. | Facade refactor may break callers. | medium | high | Keep legacy shim or ask policy per Prompt 1. | WORKSTREAM-03 | FACT |
| RISK-06 | Backend determinism grades may be hard to prove. | Incorrect D0 claims could break lockstep. | medium | high | Default uncertain optimized/platform-specific backends to D2 until proven. | WORKSTREAM-03 | INFERENCE |
| RISK-07 | AAA brainstorm could be mistaken as current scope. | Scope creep, implementation overload. | medium | medium | Label future features as roadmap/spec candidates only. | WORKSTREAM-04 | FACT |
| RISK-08 | Advanced presentation features could contaminate deterministic sim. | Replay/network desync. | low-medium | high | Keep presentation non-authoritative; use caps/extensions. | WORKSTREAM-04 | INFERENCE |
| RISK-09 | Report package may over-compress exact prompt text. | Future assistant may need original prompt wording. | low-medium | medium | Preserve active prompt IDs and key requirements; refer to chat context for exact text if needed. | WORKSTREAM-05 | INFERENCE |
| RISK-10 | Generated report may treat assistant suggestions as accepted decisions. | Spec book could overstate commitment. | low-medium | medium | Labels distinguish FACT/INFERENCE; future aggregator must preserve uncertainty. | WORKSTREAM-05 | FACT |
| RISK-11 | DX9 availability/toolchain mismatch. | Prompt 5 may fail to compile/link. | medium | medium | CMake detection and clear errors; system SDK only. | WORKSTREAM-02 | INFERENCE |
| RISK-12 | Smoke UI text requirement may exceed renderer IR subset. | Launcher/game smoke blocked. | medium | medium | Use rectangles or ask text strategy. | WORKSTREAM-02 | FACT |
| RISK-13 | TLV migration scope unknown. | Prompt 7 may miss legacy formats. | medium | high | Inventory formats before conversion. | WORKSTREAM-02 | FACT |
| RISK-14 | Verify script may be Windows-only. | Cross-platform CI needs later scripts. | low | medium | Accept for current Windows Codex; add POSIX scripts later if needed. | WORKSTREAM-02 | INFERENCE |
| RISK-15 | Stale external software/toolchain facts. | Build assumptions may age. | medium | medium | Reverify CMake/toolchain/SDK status before future use. | WORKSTREAM-02 | UNCERTAIN / UNVERIFIED |
| RISK-16 | Future aggregation may merge superseded plans incorrectly. | Project spec may include obsolete prompt packs. | medium | high | Use rejected/superseded register. | WORKSTREAM-05 | FACT |

## 10. Verification Queue

| ID | Item requiring verification | Why verification is needed | Suggested verification source/type | Priority | Related workstream | Label |
| --- | --- | --- | --- | --- | --- | --- |
| VERIFY-01 | Inspect repo/archive to confirm MASTER prompts 1-14 implementation. | Prerequisite state unverified. | Repo search/build/history. | high | WORKSTREAM-01 | UNCERTAIN / UNVERIFIED |
| VERIFY-02 | Run initial CMake configure/build in repo. | Need actual build baseline. | cmake -S . -B build\verify_initial -G Ninja; build target help. | high | WORKSTREAM-02 | FACT |
| VERIFY-03 | Search DSYS/DGFX callsites. | API refactor depends on actual usage. | ripgrep dsys/domino_sys/dgfx. | high | WORKSTREAM-02, WORKSTREAM-03 | FACT |
| VERIFY-04 | Confirm exact launcher/game target names. | Prompt 8 command lines require exact names. | CMake target help. | high | WORKSTREAM-02 | FACT |
| VERIFY-05 | Run baseline header checker once implemented. | Validate C89/C++98 visibility. | CMake configure with checker. | high | WORKSTREAM-03 | FACT |
| VERIFY-06 | Print capability registry selection audit. | Ensure backend selection is deterministic/inspectable. | --print-selection output. | high | WORKSTREAM-03 | FACT |
| VERIFY-07 | Run domino_sys_smoke for win32 and win32_headless. | Tier-1 platform completion. | Prompt 4 commands. | high | WORKSTREAM-02 | FACT |
| VERIFY-08 | Run soft renderer hash test and dgfx_demo. | Tier-1 renderer completion. | Prompt 5 commands. | high | WORKSTREAM-02 | FACT |
| VERIFY-09 | Run Tier-2 incompatible-selection configure tests. | Gating correctness. | Prompt 6 bad platform/backend cmake calls. | medium-high | WORKSTREAM-02 | FACT |
| VERIFY-10 | Run TLV/handshake regression tests. | Serialization/network ABI correctness. | ctest or direct test exes. | high | WORKSTREAM-02 | FACT |
| VERIFY-11 | Run scripts\build_codex_verify.bat after Prompt 8. | Final done gate. | Verify script. | critical | WORKSTREAM-02 | FACT |
| VERIFY-12 | Confirm which AAA roadmap items become formal future requirements. | Brainstorm vs spec separation. | User review in future spec aggregation. | medium | WORKSTREAM-04 | INFERENCE |
| VERIFY-13 | Verify generated report files and ZIP are downloadable/readable. | Package quality. | Open files; check ZIP contents. | high | WORKSTREAM-05 | FACT |
| VERIFY-14 | Check whether existing CHANGELOG format exists. | Prompt 9 format compatibility. | Repo inspection. | low-medium | WORKSTREAM-02 | FACT |

## 11. Timeline Register

| Sequence | Event / topic | What changed or was decided | Why it mattered | Current relevance | Confidence |
| --- | --- | --- | --- | --- | --- |
| 01 | User requested Codex prompt pack and mandated initial questionnaire. | Established process and output requirements. | Prevented assumptions. | historical foundation | 5 |
| 02 | Assistant asked questionnaire. | Collected categories: platforms, renderers, APIs, completion, build context. | Matched user process. | historical | 5 |
| 03 | User answered platform/render/API/build questions in detail. | Defined Tier-1/2/3 platforms and renderers, dsys/dgfx context, C89/C++98, build targets. | Primary source for architecture/prompt scope. | still relevant | 5 |
| 04 | User uploaded dominium.zip and asked assistant to analyze it. | Repo archive became artifact. | Should have verified repo facts. | still relevant; unverified | 4 |
| 05 | Assistant generated initial platform/render/API prompt pack. | First implementation plan existed. | Later superseded. | historical only | 4 |
| 06 | User pasted pre-existing MASTER prompts 1-14 and asked for new plan assuming them implemented. | Shifted scope to post-master continuation. | Important sequencing assumption. | still relevant | 5 |
| 07 | Assistant generated new post-master plan. | Started platforms/render/API continuation after engine core. | Later revised. | historical | 4 |
| 08 | User asked how APIs can be extensible/modular. | Architecture discussion introduced vtables, extensions, caps, registry, handles. | Became core design. | still relevant | 5 |
| 09 | User asked for C89/C++98 maintainability. | Stabilized ABI and two-tier renderer model. | Became mandatory later. | still relevant | 5 |
| 10 | User asked for new prompt plan after prior prompt 14. | Assistant generated prompts 15-24. | Later superseded. | historical | 4 |
| 11 | User asked whether plan supports GUI launcher/game and future bloom/ray tracing/spatial audio/proximity chat. | Extended graphics/audio/input roadmap. | Future roadmap material. | still relevant as roadmap | 5 |
| 12 | User asked about broader AAA features. | Expanded roadmap: AI, nav, terrain, vehicles, economy, combat, weather, tools, modding. | Spec book material. | still relevant as roadmap | 5 |
| 13 | User injected mandatory constraints. | Hard requirements for language baseline, ABI, facades, caps, determinism, TLV, CI. | Rewrote plan constraints. | critical | 5 |
| 14 | Assistant integrated constraints into revised prompts 15-28. | Expanded detailed plan. | Superseded by consolidated pack. | historical | 4 |
| 15 | User asked whether plan covered absolutely everything and preferred fewer larger prompts. | Assistant produced optimized 8-prompt pack. | Precursor to final pack. | historical/near-final | 5 |
| 16 | User requested Codex commits and 'start with prompt 1'. | Commit discipline added. | Final pack generation began. | critical | 5 |
| 17 | Assistant generated final Prompt 1. | Active pack prompt 1. | still relevant | 5 |  |
| 18 | User said 'next' repeatedly; assistant generated Prompts 2-9. | Final active 9-prompt pack completed. | critical | 5 |  |
| 19 | User requested maximum-fidelity Context Transfer Packet. | Assistant produced detailed handoff. | Base for current report package. | critical | 5 |
| 20 | User requested final downloadable report package. | Current task. | Package generated now. | current | 5 |

## 12. Spec Book Contribution Register

| ID | Contribution | Destination section | Status | Needs confirmation | Label |
| --- | --- | --- | --- | --- | --- |
| SPECBOOK-01 | C89/C++98 baseline and no runtime language switching | Language Baselines | formal requirement candidate | no | FACT |
| SPECBOOK-02 | C ABI/POD/vtable/interface header ABI template | ABI and Plugin Boundaries | formal requirement candidate | no | FACT |
| SPECBOOK-03 | Facade/backend architecture and platform facets | Engine Architecture | formal requirement candidate | repo mapping needs verification | FACT |
| SPECBOOK-04 | Capability registry and launcher profiles | Runtime Configuration | formal requirement candidate | implementation pending | FACT |
| SPECBOOK-05 | D0/D1/D2 determinism grades | Determinism | formal requirement candidate | per-backend grade verification needed | FACT |
| SPECBOOK-06 | TLV-as-ABI container and migrations | Serialization | formal requirement candidate | existing format inventory needed | FACT |
| SPECBOOK-07 | Final 9-prompt Codex pack | Implementation Roadmap | active plan | confirm still active before execution | FACT |
| SPECBOOK-08 | Future AAA feature roadmap | Long-Term Roadmap | background/spec candidate | user prioritization needed | FACT |
