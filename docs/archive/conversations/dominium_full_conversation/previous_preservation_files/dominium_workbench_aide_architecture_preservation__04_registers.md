# STRUCTURED REGISTERS

## 17. Workstream Register

| ID | Name | Objective | Current state | Desired end state | Status | Priority | Confidence | Label |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| WORKSTREAM-01 | Dominium/Domino architectural identity | Preserve the distinction between Domino as reusable deterministic substrate and Dominium as game/product family. | Conceptually settled in this chat; repo-current status requires verification. | Contract-governed reusable substrate supporting Dominium and other games/apps. | Active | P0 | 4 | FACT/INFERENCE |
| WORKSTREAM-02 | AIDE control-plane workflow | Make AIDE the scheduler/ledger/checkpoint/repair system for bounded Codex work. | Workflow, WorkUnit, dev/main, checkpoint, and capability reality prompts were generated or discussed. | Parallel task execution with evidence-blocked main promotion. | Active | P0 | 4 | FACT |
| WORKSTREAM-03 | Product spine and queue sequencing | Continue narrow product-spine tasks while broad features remain blocked. | Package mount, replay proof, barebones shell, product spine review, presentation contract and full-gate tasks were discussed; latest execution state is user-reported, not independently verified here. | Proven command/result/view/replay/client shell leading to presentation/projection and Workbench read-only shell. | Active | P0 | 3 | UNCERTAIN / UNVERIFIED |
| WORKSTREAM-04 | Unified presentation architecture | Unify CLI, TUI/text, rendered GUI, native GUI, and headless as projections of commands/results/views. | Presentation contract completed per user report; projection conformance remains next. | One view/action/projection model shared by products and Workbench. | Active | P0 | 4 | FACT/UNVERIFIED |
| WORKSTREAM-05 | Workbench production environment | Make Workbench the visual/agentic production environment, not the authority. | Strong conceptual plan; implementation deferred until contracts/projections/read-only shell. | Progressive self-hosting Workbench that edits artifacts through document patches and evidence. | Planned | P1 | 4 | FACT/INFERENCE |
| WORKSTREAM-06 | Renderer/provider strategy | Use raylib/SDL/Lua as fenced providers under Dominium service contracts. | Detailed provider doctrine decided conceptually; implementation not yet started. | Service-first provider system with manifests, profiles, conformance tests, and third-party fences. | Planned | P1 | 4 | FACT/INFERENCE |
| WORKSTREAM-07 | Structure stabilization and full-gate cleanup | Stop broad structure cleanup; run targeted maintenance such as full-gate legacy test routing. | User requested FULL-GATE-LEGACY-TEST-ROUTE-01 next; prompt generated. | Canonical active structure with full-gate tests no longer expecting retired roots. | Active | P0 | 4 | FACT |
| WORKSTREAM-08 | Universe Explorer north-star | Build read-only Universe Explorer as first meaningful inspection product slice after presentation/projection. | Discussed as future path, not yet implementation. | Headless and then visual no-modal-loading universe inspection proving reference frames, streaming, materialization, and projection. | Planned | P2 | 3 | INFERENCE |
| WORKSTREAM-09 | Modular theme/UI/TUI/rendered system | Support modular layouts, controls, widgets, themes, OEM+ mimic styles, TUI profiles, and code-only primitive themes. | Discussed with screenshots and mockups; mostly conceptual. | Theme/control/layout/view system packable and testable across CLI/TUI/rendered/native. | Planned | P1 | 4 | FACT/INFERENCE |
| WORKSTREAM-10 | Long-range simulation/game doctrine | Preserve deep primitives, materialization, representation ladders, formalization, civilization, and failure ontology as future domain doctrine. | Discussed repeatedly but deferred. | Domain constitutions and slices after product spine and Workbench foundations. | Future | P3 | 3 | INFERENCE |

## 18. Decision Register

| ID | Decision | Status | Evidence / basis | Rationale | Implications | Related workstream | Confidence | Label |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| DECISION-01 | Domino is the reusable deterministic substrate; Dominium is one product/game family on it. | Accepted/active | Repeated user acceptance and later handoffs. | Allows reuse for other games and prevents Dominium-specific systems from contaminating the engine substrate. | Affects roots, APIs, provider boundaries, Workbench, packs, and future game projects. | WORKSTREAM-01 | 4 | FACT |
| DECISION-02 | Workbench is not authority; it is a production environment over contracts, commands, services, documents, patches, evidence, modules, packs, and providers. | Accepted/active | User accepted replacement of old UI/Tool Editor with Workbench platform. | Prevents a second GUI framework and keeps CLI/TUI/GUI/headless parity. | Workbench must call command/service/document/patch flows, not mutate truth privately. | WORKSTREAM-05 | 4 | FACT |
| DECISION-03 | Abandon old UI Editor / Tool Editor as final products; recycle their ideas into Workbench modules. | Accepted/active | User explicitly said old UI editor/tool editor were good general ideas but bad final products, to abandon and recycle them. | Avoids Windows-first one-off tooling and moves to cross-platform rendered tools. | Old concepts become Interface Studio, UI/HUD Sandbox, Theme Lab, Module/Pack Foundry, App Composer. | WORKSTREAM-05 | 5 | FACT |
| DECISION-04 | CLI, TUI/text, rendered GUI, OS-native GUI, and headless are projections of the same semantic command/result/view system. | Accepted/active | Repeatedly discussed and accepted. | Prevents separate implementations and enables reuse across client, server, setup, launcher, and Workbench. | Requires presentation contracts and projection conformance before rich UI. | WORKSTREAM-04 | 4 | FACT |
| DECISION-05 | Use progressive self-hosting: seed substrate first, then Workbench edits safe artifacts, then its own presentation, then products. | Accepted/active | User accepted progressive self-hosting model. | Avoids circular dependency and unsafe self-modifying Workbench. | Defines Workbench maturity ladder S0-S6. | WORKSTREAM-05 | 4 | FACT |
| DECISION-06 | Stop broad structure cleanup once canonical active structure is clean enough; use targeted maintenance lanes. | Accepted/latest plan | User shifted to full-gate legacy test routing and targeted cleanup. | Avoids cleanup spiral. | Maintenance tasks include full-gate legacy test route, pack layout canon, residual taxonomy, public ABI promotion. | WORKSTREAM-07 | 4 | FACT |
| DECISION-07 | Use AIDE as governor/ledger/checkpoint/repair system and Codex as bounded patch executor. | Accepted/active | Explicit in multiple handoff plans. | Supports parallel development without corrupting main. | Requires workflow law, WorkUnit schema, dev/main policy, checkpoint loop, capability reality ledger. | WORKSTREAM-02 | 4 | FACT |
| DECISION-08 | Development is non-blocking; promotion is evidence-blocked. | Accepted/active | Repeated as doctrine in user and assistant handoffs. | Allows progress on dev while protecting main. | Shapes branch model and testing policy. | WORKSTREAM-02 | 5 | FACT |
| DECISION-09 | Use task branches/worktrees; do not let multiple agents mutate shared dev directly. | Accepted/active | Discussed as required before larger parallelism. | Prevents conflicts and stale AIDE state. | Requires branch role policy and checkpoint loop. | WORKSTREAM-02 | 4 | FACT |
| DECISION-10 | Current mainline language doctrine moved from C89/C++98 ideas to C17 + C++17 with C-compatible ABI boundaries. | Accepted but verify live repo | User pasted synthesis stating this; earlier chat had C89/C++98 assumptions. | Improves maintainability while preserving ABI portability. | Needs live verification in CMake/build policy before final spec merge. | WORKSTREAM-01 | 3 | UNCERTAIN / UNVERIFIED |
| DECISION-11 | Use raylib/rlgl/rlsw/raygui/raudio/SDL2/Lua aggressively only as replaceable providers behind Dominium service contracts. | Accepted/conceptual | User asked what I thought; assistant agreed and refined. | Gives fast visible progress without architectural lock-in. | Provider work should follow AIDE/presentation and manifest/fence/service contract wedges. | WORKSTREAM-06 | 4 | FACT/INFERENCE |
| DECISION-12 | Do not make raylib, SDL2, Lua, or app variants define the architecture. | Accepted/conceptual | Explicitly discussed as service-first/provider-backed doctrine. | Prevents vendor-shaped directory and API lock-in. | Requires forbidden include validator and provider manifests. | WORKSTREAM-06 | 4 | FACT/INFERENCE |
| DECISION-13 | Raylib rlsw is a raylib software-provider, not the canonical Dominium software renderer. | Accepted/conceptual | Discussed and accepted in provider doctrine. | Preserves first-party reference renderer slot. | Directory split: runtime/render/providers/software vs runtime/render/providers/rlsw. | WORKSTREAM-06 | 4 | FACT/INFERENCE |
| DECISION-14 | Universe Explorer is a north-star read-only inspection product, not gameplay. | Tentative/accepted as plan | Discussed after structure cleanup as first meaningful product identity. | Proves no-modal-loading, reference frames, streaming, materialization, projection before embodiment. | Implementation should start with contracts/headless proof, not renderer/gameplay. | WORKSTREAM-08 | 3 | INFERENCE |
| DECISION-15 | Workbench should begin read-only before editing artifacts. | Accepted/active | Repeated in self-hosting safety stages. | Reduces risk and proves projection/evidence first. | First Workbench shell should inspect commands, diagnostics, artifacts, graphs, packs, status. | WORKSTREAM-05 | 4 | FACT/INFERENCE |
| DECISION-16 | Full CTest remains full-gate/T4 debt, not every-prompt gate. | Accepted/latest plan | Repeated; user wants speed on dev with full suite at main/checkpoints. | Supports parallel productivity. | Requires targeted validators, fast strict, and checkpoint policy. | WORKSTREAM-02 | 4 | FACT/UNVERIFIED |

## 19. Task Register

| ID | Task | Priority | Urgency | Owner | Dependencies | Inputs needed | Expected output | Next step | Related workstream | Label |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| TASK-01 | FULL-GATE-LEGACY-TEST-ROUTE-01 | P0 | U0 | Codex/AIDE | PRESENTATION-CONTRACT-01 complete; canonical structure clean enough | Full-gate tests still expecting retired roots; generated prompt | Audit + targeted test/validator fixes; no retired root expectations | Run/execute generated prompt | WORKSTREAM-07 | FACT |
| TASK-02 | PACK-INTERNAL-LAYOUT-CANON-01 | P1 | U1 | Codex/AIDE | Current pack layout warnings | Audit current pack-internal content layout | Decision and targeted migration/validator update | Generate prompt after or alongside full-gate cleanup | WORKSTREAM-07 | FACT/INFERENCE |
| TASK-03 | RUNTIME-ENGINE-RESIDUAL-TAXONOMY-01 | P1 | U1 | Codex/AIDE | Structure audit warning buckets | Inspect engine/runtime residual paths such as session/serialization/foundation | Classification or targeted moves | Generate maintenance prompt | WORKSTREAM-07 | FACT/INFERENCE |
| TASK-04 | PUBLIC-HEADER-ABI-PROMOTION-01 | P1 | U1 | Codex/AIDE | Public ABI warning debt | Public surface/header promotion warnings | Classify public vs internal/provisional; reduce warnings | Generate prompt | WORKSTREAM-01 | FACT/INFERENCE |
| TASK-05 | STORAGE-PACKAGE-PROVIDER-SPLIT-01 | P1 | U1 | Codex/AIDE | Provider/package structure warnings | Current storage/package provider split uncertainty | Targeted taxonomy/contract clarification | Generate prompt | WORKSTREAM-06 | FACT/INFERENCE |
| TASK-06 | POINTER-WIDTH-SERIALIZATION-AUDIT-01 | P1 | U1 | Codex/AIDE | C17/C++17 + 64-bit policy; serialization law | Code/search audit for pointer-width serialization risks | Audit and repair tasks | Generate prompt | WORKSTREAM-01 | FACT |
| TASK-07 | PROJECTION-CONFORMANCE-01 | P0 | U1 | Codex/AIDE | PRESENTATION-CONTRACT-01 complete | Projection conformance task | Fixtures/tests proving CLI/text/rendered-placeholder/native/headless projections consume same views | Generate next mainline prompt after maintenance set or now if chosen | WORKSTREAM-04 | FACT |
| TASK-08 | ACCESSIBILITY-CONTRACT-01 | P1 | U1 | Codex/AIDE | Presentation contracts | Accessibility labels/focus/keyboard/contrast/reduced-motion law | Contracts/fixtures/validators | Generate after projection conformance | WORKSTREAM-04 | FACT |
| TASK-09 | TEXT-LOCALIZATION-CONTRACT-01 | P1 | U1 | Codex/AIDE | Presentation contracts | Text/message catalog/localization fallback law | Contracts/fixtures/validators | Generate after accessibility contract or parallel | WORKSTREAM-04 | FACT |
| TASK-10 | WORKBENCH-SHELL-READONLY-01 | P1 | U2 | Codex/AIDE | Presentation/projection conformance | Read-only Workbench shell | Command palette/status/validation/evidence/project graph surfaces, no editing | Generate once projection conformance is stable | WORKSTREAM-05 | FACT/INFERENCE |
| TASK-11 | UNIVERSE-EXPLORER-CONTRACT-01 | P1 | U2 | Codex/AIDE | Presentation/projection; read-only shell preferably | Contract for read-only universe inspection/explorer | Observer/ref frames/streaming/materialization/fidelity/provenance contracts | Generate after Workbench/read-only or as contract-only lane | WORKSTREAM-08 | INFERENCE |
| TASK-12 | UNIVERSE-EXPLORER-HEADLESS-01 | P1 | U2 | Codex/AIDE | Universe Explorer contract | Headless/null-render proof | Typed traversal/inspection/materialization/refusal evidence without renderer | Generate after contract | WORKSTREAM-08 | INFERENCE |
| TASK-13 | PROVIDER-MANIFEST-WEDGE-01 | P1 | U2 | Codex/AIDE | AIDE governance/presentation; provider doctrine | Provider descriptor law | Provider schema, examples, status vocab, relation to capability ledger | Generate after presentation/projection or as parallel low-risk lane | WORKSTREAM-06 | INFERENCE |
| TASK-14 | SERVICE-CONTRACT-WEDGE-01 | P1 | U2 | Codex/AIDE | Provider manifest wedge | Service slots for platform/input/render/draw/audio/assets/script | Service contracts and null-provider contract fixtures | Generate after provider manifest | WORKSTREAM-06 | INFERENCE |
| TASK-15 | THIRD-PARTY-FENCE-01 | P1 | U2 | Codex/AIDE | Provider manifest/service contract | Forbidden include and license/third-party validator | Boundary validator and third-party manifest policy | Generate before concrete raylib wedge | WORKSTREAM-06 | INFERENCE |
| TASK-16 | RAYLIB-PROVIDER-WEDGE-01 | P2 | U2 | Codex/AIDE | Manifest/service/fence tasks | Raylib ecosystem seed provider proof | Raylib/rlgl/rlsw/raygui/raudio provider proofs; no leakage | Generate after fences | WORKSTREAM-06 | INFERENCE |
| TASK-17 | PRODUCT-SPINE/STATUS verification before future prompts | P0 | U0 | Future assistant/user | Current chat state may be stale | Live repo status from queue/audits/log | Correct next prompt and prevent stale work | Verify before execution | WORKSTREAM-03 | UNCERTAIN / UNVERIFIED |

## 20. Constraint Register

| ID | Constraint | Type | Hard/soft | Source / basis | Practical implication | Violation risk | Confidence | Label |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| CONSTRAINT-01 | Do not turn Workbench into authority. | Architecture | Hard | Direct repeated doctrine | Workbench must use commands/services/documents/patches/evidence. | High | 5 | FACT |
| CONSTRAINT-02 | Broad Workbench UI, provider runtime, package runtime, module loader, renderer/native GUI, gameplay, release publication remain blocked until gates authorize. | Execution | Hard | Repeated queue/foundation summaries in chat | Future prompts must preserve non-goals. | High | 4 | FACT/UNVERIFIED |
| CONSTRAINT-03 | No broad structure cleanup unless validator/audit blocks next slice. | Execution | Hard/soft | Latest plan | Use targeted maintenance lanes. | Medium | 4 | FACT |
| CONSTRAINT-04 | CLI/TUI/rendered/native/headless must be projections of same command/result/view spine. | Architecture | Hard | Repeated accepted doctrine | Presentation work must avoid separate semantics per UI mode. | High | 4 | FACT |
| CONSTRAINT-05 | Third-party types must not leak into engine/game/contracts/content/saves/replays/public SDK. | Architecture | Hard | Provider doctrine | Provider code must translate to Dominium types. | High | 4 | FACT/INFERENCE |
| CONSTRAINT-06 | Full CTest is full-gate/T4 debt, not ordinary prompt gate. | Testing | Soft but important | Repeated latest plans | Dev tasks run targeted validators/fast strict; main/checkpoint more stringent. | Medium | 4 | FACT/UNVERIFIED |
| CONSTRAINT-07 | Stable identity is contractual, not path-based. | Architecture | Hard | Repeated doctrine | Use IDs/manifests/registries, not folder names, as identity. | High | 5 | FACT |
| CONSTRAINT-08 | Apps compose; runtime implements; contracts define law; content supplies authored payloads; tools validate/generate/migrate. | Architecture | Hard | Repeated doctrine | Prevents apps/tools becoming runtime or truth owners. | High | 4 | FACT |
| CONSTRAINT-09 | Development non-blocking; promotion evidence-blocked. | Process | Hard | Repeated AIDE doctrine | Dev may accept classified warnings; main requires checkpoint/evidence. | High | 4 | FACT |
| CONSTRAINT-10 | The preservation report itself is for THIS CHAT ONLY unless labelled PROJECT-CONTEXT. | Reporting | Hard | Uploaded preservation prompt | Do not merge other chat facts unlabelled. | Medium | 5 | FACT |

## 21. User Preference Register

| ID | Preference | Area | Explicit/inferred/uncertain | Strength | Practical implication | Risk if wrong | Label |
| --- | --- | --- | --- | --- | --- | --- | --- |
| PREF-01 | Direct, source-grounded, audit-ready answers with explicit uncertainty. | Response style | Explicit | Strong | Use FACT/INFERENCE/UNCERTAIN labels and cite uploaded/current files when used. | High | FACT |
| PREF-02 | Generate copyable Codex/AIDE prompts in one fenced block. | Prompt generation | Explicit | Strong | Future prompts should be single-block, status/context/goals/non-goals/validation/final format. | Medium | FACT |
| PREF-03 | Do not re-ask answered questions; proceed with assumptions when safe. | Interaction | Explicit/inferred | Strong | Ask only if materially blocking. | Medium | FACT/INFERENCE |
| PREF-04 | Do not restart settled doctrine. | Continuity | Explicit | Strong | Future chats should verify state but not re-litigate architecture. | High | FACT |
| PREF-05 | Preserve rejected/superseded options. | Memory | Explicit in preservation prompt | Strong | Report rejected UI Editor, native-widget-first editor, monolithic editor, broad cleanup. | Medium | FACT |
| PREF-06 | Prefer professional/OS-like engineering over one-off indie architecture. | Technical philosophy | Explicit | Strong | Design for portability, modularity, compatibility, evidence, replaceability. | High | FACT |

## 22. Open Questions Register

| ID | Question / issue | Why it matters | Known information | Unknown information | Resolution path | Priority | Related workstream | Label |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| QUESTION-01 | What is the live repo status at the time of continuation? | The chat includes changing queue and commit state. | User reported latest tasks and statuses. | Whether subsequent Codex runs changed queue/audits after this preservation. | Verify `.aide/queue/current.toml`, latest commits, relevant audits. | P0 | WORKSTREAM-03 | UNCERTAIN / UNVERIFIED |
| QUESTION-02 | Should the next executable task be FULL-GATE-LEGACY-TEST-ROUTE-01 or PROJECTION-CONFORMANCE-01? | User said first generate maintenance prompts, then replan. | FULL-GATE prompt was generated immediately before preservation request. | Whether user will run maintenance lane first or mainline projection. | Ask user or check queue after files. | P0 | WORKSTREAM-07 | FACT/UNCERTAIN |
| QUESTION-03 | Is C17/C++17 fully implemented in CMake or partially doctrinal? | Language baseline changed during chat. | Later handoffs state C17/C++17 baseline. | Live CMake/toolchain details. | Verify repo files before spec lock. | P1 | WORKSTREAM-01 | UNCERTAIN / UNVERIFIED |
| QUESTION-04 | How aggressively should provider/raylib work start relative to presentation/projection and Workbench read-only shell? | Provider strategy was accepted conceptually but timing deferred. | Recommended after AIDE/presentation/fence/manifest tasks. | Exact queue timing after maintenance tasks. | Replan after projection conformance and maintenance status. | P1 | WORKSTREAM-06 | INFERENCE |
| QUESTION-05 | What is the final target for Universe Explorer as first product identity? | It is a north-star but not implemented. | Headless/read-only first, visual later, embodiment after. | How soon to schedule after read-only Workbench/presentation. | Formalize UNIVERSE-EXPLORER-CONTRACT-01 when gates allow. | P2 | WORKSTREAM-08 | INFERENCE |

## 23. Artifact Ledger

| ID | Artifact / file / prompt / output | Type | Purpose | Status | Origin | Carry forward? | Notes | Label |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| ARTIFACT-01 | Prompt UU1–UU6 plan for UI Editor import/CLI/ops/Minecraft launcher/setup tests | Prompt plan | Earlier plan for old UI Editor toolchain. | Superseded/recycled | This chat | Yes, as rejected/superseded context | Ideas became Workbench modules and CLI/presentation concepts. | FACT |
| ARTIFACT-02 | Final UI Editor implementation prompt with import/CLI/Minecraft tests | Codex prompt | Implementation prompt for old Phase A UI Editor. | Superseded | This chat | Yes, as historical artifact | Shows why old approach was abandoned. | FACT |
| ARTIFACT-03 | Screenshots/mockups of Workbench themes/modules | Images | Visual references for OEM+ themes, modules, TUI, Workbench surfaces. | Reference only | Uploaded in chat | Yes | Used to derive modular theme/workspace concepts, not exact design requirements. | FACT |
| ARTIFACT-04 | AIDE/Workbench/product-spine handoff prompt | Handoff text | Long carry-forward prompt summarizing repo state and next tasks. | Important | This chat | Yes | Should inform future chat bootstrap; live repo must still be verified. | FACT |
| ARTIFACT-05 | Codex prompts: STATUS-RECONCILE-02, AIDE-WORKFLOW-LAW-01, AIDE-WORKUNIT-SCHEMA-01, AIDE-DEV-MAIN-POLICY-01, AIDE-CHECKPOINT-LOOP-01, AIDE-CAPABILITY-REALITY-LEDGER-01 | Codex prompts | Detailed prompts for AIDE workflow layer. | Generated | This chat | Yes | Some reportedly executed later; verify live repo. | FACT |
| ARTIFACT-06 | Codex prompt: FULL-GATE-LEGACY-TEST-ROUTE-01 | Codex prompt | Targeted full-gate stale-root cleanup prompt. | Generated immediately before preservation request | This chat | Yes | Potential next execution depending on user plan. | FACT |
| ARTIFACT-07 | User-uploaded Pasted text.txt preservation instruction | Uploaded file | Maximum-fidelity preservation package instructions. | Active input | Uploaded file | Yes | Primary instruction for this response. | FACT |
| ARTIFACT-08 | This preservation package files and zip | Generated export | Downloadable report/register/spec/handoff files created by this response. | Created now | This response | Yes | Use for aggregation and future chat transfer. | FACT |

## 24. Rejected / Superseded Options Register

| ID | Option | Status | Reason | Final or tentative? | Reconsider conditions | Related workstream | Label |
| --- | --- | --- | --- | --- | --- | --- | --- |
| REJECTED-01 | Old Windows-only UI Editor as final product | Superseded | Too narrow, native-widget-first, not cross-platform/reusable; replaced by Workbench modules. | Final for final product; ideas recycled | Temporary for bootstrap only if ever needed. | WORKSTREAM-05 | FACT |
| REJECTED-02 | Tool Editor as monolithic editor | Superseded | Would become separate architecture; replaced by modular Workbench Platform. | Final as monolithic product | Could reappear as workspace/module concept only. | WORKSTREAM-05 | FACT |
| REJECTED-03 | Workbench as authority/center of architecture | Rejected | Contracts/commands/services/providers/packs/artifacts/proof are center; Workbench is surface. | Final | Reconsider only as UX language, not architecture. | WORKSTREAM-05 | FACT |
| REJECTED-04 | Broad root/directory rewrites after structure became clean enough | Deprioritized | Risk of cleanup spiral; remaining work targeted. | Current plan, not forever | If validators show blockers. | WORKSTREAM-07 | FACT |
| REJECTED-05 | Raylib-shaped architecture or apps/client/rendered/raylib variants | Rejected | Vendor/provider must not define architecture. | Final | Temporary proof folders allowed with retirement notes. | WORKSTREAM-06 | FACT/INFERENCE |
| REJECTED-06 | Pure C99 or pure C++11 as mainline baseline | Rejected/superseded | C17+C++17 with C-compatible ABI deemed better fit. | Tentative until live build verified | If platform/toolchain evidence contradicts. | WORKSTREAM-01 | UNCERTAIN / UNVERIFIED |

## 25. Risk Register

| ID | Risk / failure mode | Consequence | Likelihood | Severity | Mitigation | Related workstream | Label |
| --- | --- | --- | --- | --- | --- | --- | --- |
| RISK-01 | Future assistant treats stale repo status as current. | Wrong prompts, duplicate tasks, stale queues. | Medium | High | Always verify live repo before current-status decisions. | WORKSTREAM-03 | UNCERTAIN / UNVERIFIED |
| RISK-02 | Workbench implementation starts before projection conformance. | Separate UI semantics, later rewrite. | Medium | High | Require presentation/projection contracts first. | WORKSTREAM-04 | FACT/INFERENCE |
| RISK-03 | Raylib/SDL/Lua provider types leak into stable contracts or game state. | Vendor lock-in, replay/save instability. | Medium | High | Forbidden include/type validator and provider fences. | WORKSTREAM-06 | FACT/INFERENCE |
| RISK-04 | Full CTest debt remains ignored too long. | Release gate remains blocked. | Medium | Medium | Targeted full-gate legacy test routing and debt ledger. | WORKSTREAM-07 | FACT/UNVERIFIED |
| RISK-05 | Capability status overclaimed. | Docs/Workbench say implemented when only fixture/stub exists. | High | High | Capability Reality Ledger. | WORKSTREAM-02 | FACT |
| RISK-06 | Parallel Codex tasks conflict on coordinator files. | Queue/status corruption. | Medium | High | Coordinator ownership rules and checkpoint loop. | WORKSTREAM-02 | FACT |
| RISK-07 | Universe Explorer free-camera becomes implicit gameplay movement. | Wrong gameplay model and authority leakage. | Low-Medium | High | Separate observer inspection authority from embodied actor authority. | WORKSTREAM-08 | INFERENCE |
| RISK-08 | Preservation report overstates decisions from assistant suggestions. | Bad spec aggregation. | Medium | High | Label decisions accepted by user vs assistant suggestions. | WORKSTREAM-01 | FACT |

## 26. Verification Queue

| ID | Item requiring verification | Why verification is needed | Suggested source/type | Priority | Related workstream | Label |
| --- | --- | --- | --- | --- | --- | --- |
| VERIFY-01 | Live repo task queue and audit status. | Many user-pasted statuses changed over time. | GitHub/repo files: .aide/queue/current.toml, audits, log. | P0 | WORKSTREAM-03 | UNCERTAIN / UNVERIFIED |
| VERIFY-02 | C17/C++17 baseline in current CMake/toolchain docs. | Earlier chat had C89/C++98; later says C17/C++17. | CMakeLists, toolchain docs, foundation audit. | P1 | WORKSTREAM-01 | UNCERTAIN / UNVERIFIED |
| VERIFY-03 | Whether FULL-GATE-LEGACY-TEST-ROUTE-01 has been run. | It was generated, but execution unknown. | Repo commit/audit search. | P0 | WORKSTREAM-07 | UNCERTAIN / UNVERIFIED |
| VERIFY-04 | Whether AIDE workflow layer prompts have all landed. | Some reportedly passed in pasted summaries; may be stale. | AIDE audits and queue. | P1 | WORKSTREAM-02 | UNCERTAIN / UNVERIFIED |
| VERIFY-05 | Third-party current facts for raylib, SDL, Lua. | External software versions/support/licensing may change. | Official project docs/releases before implementation. | P2 | WORKSTREAM-06 | UNCERTAIN / UNVERIFIED |

## 27. Chronological Timeline Register

| Sequence | Event / topic | What changed or was decided | Why it mattered | Current relevance | Confidence |
| --- | --- | --- | --- | --- | --- |
| 01 | Launcher/UI Editor start | User sought graphical UI editor for mangled/flickering launcher UI. | Initial problem and early requirements. | Historical/superseded but concepts reused. | 4 |
| 02 | Phase A/B UI Editor/Tool Editor prompt plan | Generated multi-prompt implementation plan for UI Editor and Tool Editor. | Provided concrete early approach. | Superseded; artifact context. | 4 |
| 03 | Import/CLI/ops and Minecraft-style tests | UI Editor plan expanded to import existing tools, CLI scripting, and launcher/setup layout tests. | Introduced automation and structural UI testing. | Recycled into Workbench/presentation ideas. | 4 |
| 04 | Abandon old editor as final product | User stated old UI/tool editor should be abandoned/recycled. | Major pivot. | Active doctrine. | 5 |
| 05 | Dominium Workbench Platform | Workbench becomes production/validation/editing/agent environment. | Core architecture. | Active. | 5 |
| 06 | Unified CLI/TUI/rendered/native/headless projections | All UIs become projections of same semantic spine. | Prevents drift. | Presentation contract completed per user report. | 4 |
| 07 | AIDE/Codex workflow | AIDE as governor, Codex as bounded executor; task branches/checkpoints. | Enables parallel dev safely. | Active. | 4 |
| 08 | Provider/raylib strategy | Use raylib/SDL/Lua as fenced providers. | Accelerates visible progress without lock-in. | Planned. | 4 |
| 09 | Structure stabilization and full-gate debt | Stop broad cleanup; run targeted maintenance. | Keeps moving without cleanup spiral. | Current maintenance lane. | 4 |
| 10 | Preservation request | User requested maximum-fidelity preservation package. | This output. | Active. | 5 |

## 28. Spec Book Contribution Register

| Spec-book area | Contribution from this chat | Source IDs | Should become requirement/context/open issue? | Confidence | Notes |
| --- | --- | --- | --- | --- | --- |
| Architecture doctrine | Domino/Dominium/Workbench/AIDE roles and stable identity law. | DECISION-01, DECISION-02, DECISION-07 | Requirement | 4 | Core spec chapter. |
| Workbench product strategy | Workbench as modular production environment and progressive self-hosting ladder. | WORKSTREAM-05, DECISION-05 | Requirement/context | 4 | Implementation later. |
| Presentation/UI system | Unified CLI/TUI/rendered/native/headless projection doctrine. | WORKSTREAM-04, DECISION-04 | Requirement | 4 | Needs projection conformance. |
| Provider strategy | Raylib/SDL/Lua fenced provider doctrine. | WORKSTREAM-06, DECISION-11-13 | Requirement/context | 4 | External facts verify before implementation. |
| AIDE process | Development non-blocking, promotion evidence-blocked, WorkUnit/checkpoint model. | WORKSTREAM-02, DECISION-07-09 | Requirement | 4 | Partly implemented per user reports. |
| Maintenance queue | Targeted full-gate/pack/taxonomy/ABI/storage/pointer audits. | TASK-01-06 | Open issue/tasks | 4 | Current next execution. |
| Long-range game doctrine | Deep primitives, materialization, representation ladders, formalization, civilization. | WORKSTREAM-10 | Background/context | 3 | Future domain spec. |