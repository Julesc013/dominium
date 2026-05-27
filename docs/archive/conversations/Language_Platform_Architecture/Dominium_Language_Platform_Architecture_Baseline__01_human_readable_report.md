# COMPLETE CHAT PRESERVATION REPORT — Dominium Language, Platform, and Architecture Baseline

## 0. Coverage and Reliability Assessment

| Field | Assessment |
| --- | --- |
| Chat label | Dominium Language, Platform, and Architecture Baseline |
| Date anchor | 2026-05-27 Australia/Melbourne |
| Source scope | This chat only, with PROJECT-CONTEXT/repo citations where used |
| Apparent access | Partial-to-high for visible/current chat; not full independent access to all other old chats |
| Previously generated files available? | No prior generated downloadable files visible in this chat; this response creates files |
| Uploaded files or artifacts present? | Yes: Pasted text.txt preservation prompt; tool also noted some earlier uploaded files may have expired |
| Contains future plans? | Yes |
| Contains decisions? | Yes, with some recommendations still not implemented |
| Contains pending tasks? | Yes |
| Contains unresolved questions? | Yes |
| Staleness risk | Medium: toolchain/platform/library facts are time-sensitive |
| Extraction confidence | 4/5 for this visible chat; 3/5 for claims relying on external repo/toolchain state |
| Safe for later aggregation? | Yes, with caveats and labels |
| Main limitations | Cannot guarantee full contents of “other chats”; repo may change; external platform claims require verification; some uploaded files outside current prompt may have expired |

This report covers the visible/current chat and the attached preservation prompt. The prompt itself requests a maximum-fidelity human-readable and structured export package for this chat. The file is available as `Pasted text.txt` and is treated as an artifact to preserve. Some repo/source facts were already fetched in this chat and are carried forward with citations where available. The main caveat is that the first user message asked to scan “other chats in this repo,” but this preservation report cannot independently reconstruct all other chats beyond project context and the visible transcript. External toolchain/platform claims are treated as verification items, not permanently settled facts.

## 1. One-Page Orientation

This chat was a design-decision and architecture-baseline discussion for Dominium, focused on language standards, platform floors, binary architecture, portability strategy, and the project’s long-term modular structure. The user began by asking whether Dominium would gain performance or features by moving beyond the earlier C89 engine and C++98 game plan. Over the conversation, the topic expanded into a full re-evaluation of what should be written in C versus C++, what standards should define the mainline, which operating systems should still count as full native targets, and how old or exotic systems should be supported without distorting the modern architecture.

The most important evolution was away from the crude split “engine = C, game = C++.” The better rule that emerged was semantic: C should own stable law, ABI, fixed-width data, serialization, replay, packets, renderer command IR, and deterministic primitives; C++ should own resource-heavy machinery, runtime services, providers, apps, game orchestration, tools, Workbench, and composition. This is the central idea to preserve. The project does not need pure C, pure C++, or a language ideology. It needs stable contracts at the boundaries and modern implementation power internally.

The user initially considered staged old-to-new plans: versions 0.x/1.x using C89/C++98 and later versions moving to C11/C++17. That plan was superseded as the user accepted a more decisive baseline: C17 and C++17 across the mainline, with 64-bit source-native builds and little-endian assumptions. The old C89/C++98 goal moved from active mainline law into retro/projection/archive thinking. The current repo state discussed in the chat supports this: root and engine CMake were observed as already requiring C17/C++17, while the repository still contains documentation and comments that should be updated to match the new doctrine.

The chat also clarified portability. The user wanted future support for Windows XP, Windows 98, Mac OS X 10.6, Mac OS 9.2, Android, iOS, PS5, Xbox, and Switch. The answer was not to pretend one primitive binary can execute everywhere. The correct model is one canonical project with contracts, content, tests, deterministic law, C-compatible ABI, and renderer/platform/provider interfaces, then multiple products or projections: full 64-bit source-native builds for modern supported systems, constrained native builds for some older environments, contract projections for extreme legacy systems, and archive/emulator lanes for museum targets.

Another major thread was modularity. The user wanted code, data, modules, packs, tools, apps, and Workbench to integrate cleanly and be reusable. The answer became a contract-centered composition model: apps compose modules; modules require services; services are implemented by providers; providers declare capabilities; packs provide data/modules/content; profiles select packs/settings; contracts define compatibility; lockfiles make composition reproducible; commands invoke behavior; artifacts record results; tests prove it; Workbench operates it; AIDE governs it. This is the most future-proof part of the design, but it also revealed missing pieces: a composition resolver, lockfiles, compatibility corpus, trust/permission model, virtual filesystem/root model, performance budgets, and a public-surface promotion protocol.

The final state of the chat was not “done.” It reached a coherent architecture direction, but the latest project state said Foundation Lock was blocked by dependency-direction strict validation failures: 358 violations and 38 warnings. Therefore, the immediate next step is not more Workbench UI, renderer work, or gameplay expansion. It is FOUNDATION-REPAIR-DEPENDENCY-DIRECTION-01: classify and repair those dependency-direction violations, then rerun Foundation Closeout. Only after that should WORKBENCH-VALIDATION-SLICE-01 begin.

## 2. The Story of the Conversation

The conversation began with a practical question: whether Dominium would gain runtime performance or features by abandoning the older C89/C++98 split. Early answers distinguished compiler improvements from language-standard effects. A newer compiler can optimize old C and C++ code, but newer standards allow the programmer to express ownership, atomics, alignment, move semantics, copy elision, and compile-time policies in ways that reduce implementation risk and can improve runtime behavior in targeted places.

The user then asked for separate C and C++ standard comparisons. That framed C99/C11/C17/C23 and C++98/C++11/C++17/C++20+ as capability choices, not just syntax choices. C99 was identified as a meaningful step up from C89 for C ergonomics and some optimization opportunities, but not sufficient for the overall Dominium architecture. C11/C17 provide useful modern C features but cannot be trusted as the cross-platform threading/atomic layer under MSVC. C++11 provides a major leap over C++98, but C++17 is the better current target if the project is already using modern toolchains and carefully restricting standard-library deployment assumptions.

The user proposed an early staged plan: v0/v1 in C89/C++98 and v2+ in C11/C++17. That was coherent for maximum retro reach, but later became obsolete when the project floor moved toward Windows 7 SP1, macOS 10.9.5, and Linux. The conversation then explored whether the engine and game could mix standards, such as a C11 engine with a C++98 game. The answer was yes in principle, as long as the ABI boundary was C-compatible and semantic assumptions did not leak across the boundary.

The discussion then corrected the conceptual split. The user asked what actually needs C++, whether everything should be converted to C89, whether everything should be C++98, and whether there is any reason to keep regular C. The answer that matters is that folders should not determine language. Deterministic law, ABI, packets, saves, replays, stable IDs, renderer command IR, and low-level facades should be C-compatible. Resource ownership, high-level orchestration, providers, apps, Workbench, and tools should use C++ where it helps.

The user then asked for repo-specific advice based on julesc013/dominium. The assistant inspected repo files across the conversation. Earlier, the repo still carried C89/C++98 assumptions. Later, the live CMake state showed root and engine target settings had moved to C17/C++17. The repo also showed a broad domino_engine target that aggregates engine, game, runtime, renderer, platform, UI, network, packaging, ECS, scheduler, SIMD/GPU, and legacy C sources. That is useful as a convergence artifact but not the final modular target graph.

The user then shifted decisively: abandon the old plan and move to C17/C++17. That became the mainline recommendation. The plan was then expanded to support old and future platforms. The answer was that Windows 98, Mac OS 9.2, and similar targets should not govern mainline code. They can consume projections, replay streams, snapshot clients, or generated subsets. Full source-native builds should be modern and eventually 64-bit.

The 32-bit question followed. The answer was to make full native products 64-bit and keep 32-bit as constrained or projection support only. The key caveat was not to make native pointer size part of game law. Save, replay, network, IDs, and renderer IR must use fixed-width types and never serialize size_t, long, uintptr_t, or raw pointers.

The user then consolidated a broad future plan around Domino, Dominium, Workbench, AIDE, contracts, tests, replay, and evidence. The answer agreed that the plan was strong, but identified missing central pieces: composition resolver, lockfiles, compatibility corpus, trust/permissions, virtual filesystem roots, performance budgets, and stable public-surface promotion rules.

Finally, the user pasted advice favoring C99 or C++11 due to raylib/SDL and legacy targets. The answer rejected a pivot. Raylib and SDL2 being C APIs only means provider boundaries should be C-callable; it does not force the whole engine or game to C99. The final recommendation remained C17 + C++17, with raylib/SDL2 treated as providers and with external deployment claims placed into the verification queue.

## 3. Main Topics Discussed

### Topic 1 — Language baseline
The chat repeatedly compared C89, C99, C11/C17, C23, C++98, C++11, C++17, and newer C++ standards. The final working direction is C17 + C++17 for the mainline. C99 and C++11 were considered but not adopted as the project-wide baseline. Newer C23/C++20/C++23/C++26 were treated as future provider/tool lanes, not current mainline law.

### Topic 2 — C versus C++ responsibility split
The major conclusion was not “engine C, game C++,” but “stable law C-compatible, machinery C++17.” C17 should own deterministic primitives, ABI, fixed-point math, save/replay/wire formats, renderer command IR, stable IDs, and low-level facades. C++17 should own game orchestration, runtime services, providers, apps, Workbench, resource ownership, and tools.

### Topic 3 — ABI and data contracts
The project must retain a C-compatible ABI. The public boundary should remain POD-only, versioned, return-code/refusal based, and free of exceptions, STL containers, classes, templates, allocator ownership, and C++ ABI assumptions. This allows providers, plugins, tools, projections, and future bindings to survive implementation changes.

### Topic 4 — Determinism and parallelism
The deterministic simulation law remains more important than the language standard. Authoritative simulation must use stable IDs, canonical ordering, fixed-width values, fixed-point math, explicit little-endian encoding, and deterministic scheduler phases. Threads may accelerate derived work, but final authoritative commit must be canonical and not depend on OS timing or thread completion.

### Topic 5 — Platform and legacy support
The mainline should be 64-bit source-native for x86_64 and arm64. Windows 7 SP1, macOS 10.9.5, and Linux were discussed as the practical active floor, subject to verification. Windows XP, Windows 98, Mac OS X 10.6, Mac OS 9.2, and similar systems should be constrained native, projection, or archive lanes rather than mainline constraints.

### Topic 6 — Modularity, providers, packs, and modules
The design moved toward contracts and composition. Apps compose modules; modules require services; services are implemented by providers; packs provide data/modules/content; profiles select packs; lockfiles make composition reproducible; Workbench operates through commands; AIDE governs and validates.

### Topic 7 — Repo state and Foundation blocker
The live repo was discussed as already having C17/C++17 CMake settings, but also retaining a broad domino_engine target and old wording in docs/headers. The immediate blocker is Foundation Lock: dependency-direction strict validation reports 358 violations and 38 warnings, so Workbench/product work is not authorized until repair.

## 4. What We Were Trying to Achieve

### 4.1 Explicit Goals
- Determine whether Dominium should move beyond C89/C++98.
- Decide whether to use C, C++, or both, and which language versions.
- Support Windows 7, macOS Mavericks, Linux, and possibly older/future systems.
- Preserve modularity, performance, extensibility, distributed simulation, and long-term portability.
- Understand how code, data, modules, packs, providers, apps, Workbench, and AIDE integrate.
- Preserve this chat in a human-readable and aggregator-ready form.

### 4.2 Inferred Goals
- Avoid another cleanup cycle by locking hard-to-change decisions early.
- Prevent old retro ambitions from governing the modern mainline.
- Keep future assistants from repeating rejected advice such as pure C99 or pure C++11.
- Prepare material for a future Project Spec Book.

### 4.3 Goals That Changed Over Time
The goal changed from “should old C/C++ standards be upgraded?” to “what is the full future architecture baseline?” The user initially entertained C89/C++98 staging, then accepted C17/C++17 as mainline. The user also moved from “maybe support old systems directly” to “support old systems through constrained/projection/archive lanes.”

### 4.4 Goals Still Unresolved
The exact platform floors, C++17 subset policy, composition resolver schema, lockfile taxonomy, trust model, performance budgets, and dependency-direction repair remain open.

## 5. Decisions Made and Why

| ID | Decision | Status | Why it mattered | Confidence | Label |
| --- | --- | --- | --- | --- | --- |
| DECISION-01 | Mainline should use C17 and C++17 rather than C89/C++98, pure C99, or pure C++11. | accepted direction | Keeps modern implementation leverage while staying conservative enough for Windows 7/Mavericks-era planning. | 4 | FACT/INFERENCE |
| DECISION-02 | Full source-native products should be 64-bit-first/64-bit-only: x86_64 and arm64. | accepted direction | Reduces matrix complexity and matches modern desktop/mobile/console direction. | 4 | FACT/INFERENCE |
| DECISION-03 | Keep little-endian mainline and explicit little-endian data formats. | accepted direction | Avoids large portability burden while retaining cross-platform determinism across chosen targets. | 5 | FACT |
| DECISION-04 | Public boundary remains C-compatible, POD-only, versioned, and no C++ ABI leakage. | accepted direction | Enables C/C++/tools/projections/plugins without binding to compiler-specific C++ ABI. | 5 | FACT |
| DECISION-05 | C17 owns deterministic law and stable formats; C++17 owns machinery and orchestration. | accepted direction | Gives determinism and stable contracts while using C++ where it provides real value. | 4 | FACT/INFERENCE |
| DECISION-06 | Raylib and SDL2 should be providers/backends, not architectural identity. | accepted direction | Allows direct C API integration without forcing the whole engine/game to C99. | 4 | INFERENCE |
| DECISION-07 | Do not pursue a universal primitive binary for all systems. | accepted direction | Prevents false portability assumptions for Windows 98/Mac OS 9/consoles. | 4 | FACT/INFERENCE |
| DECISION-08 | Foundation Lock must not close while dependency-direction strict validation is red. | accepted/current blocker | Prevents product/UI work before dependency law is enforceable. | 5 | FACT |
| DECISION-09 | Workbench is not authority; it is a command/evidence surface over contracts/services/providers. | accepted direction | Prevents Workbench from bypassing CLI/tests/AIDE and fragmenting behavior. | 4 | FACT/INFERENCE |
| DECISION-10 | Composition resolver and lockfiles are missing central pieces. | recommended, not yet implemented | Needed to make modules/packs/providers/apps reproducible and extensible. | 4 | INFERENCE |

### Decision explanations

- **DECISION-01:** The accepted direction is C17 + C++17 mainline. This superseded the old C89/C++98 plan and the later temptations to pivot to pure C99 or pure C++11. It depends on restricted deployment/library policy for legacy floors.
- **DECISION-02:** Full source-native builds should be 64-bit. This simplifies the release matrix and avoids old memory constraints, while fixed-width data keeps saves/replays portable.
- **DECISION-03:** Little-endian is accepted as a mainline invariant. Explicit little-endian serialization remains necessary so that files are stable and auditable.
- **DECISION-04:** The public ABI remains C-compatible. This is the key decision that lets modern C++ implementation coexist with tools, providers, projections, and future bindings.
- **DECISION-05:** C and C++ are separated by semantic role, not by folder name.
- **DECISION-06:** Raylib and SDL2 can be useful providers but should not determine the whole architecture.
- **DECISION-07:** Universal primitive binaries were rejected; projections or generated subsets are the correct extreme-legacy strategy.
- **DECISION-08:** Foundation Lock remains blocked while dependency-direction strict validation is red.
- **DECISION-09:** Workbench must operate through the same command/evidence system as CLI/tests.
- **DECISION-10:** Composition resolver and lockfiles are recommended as missing pieces; they are not yet implemented.

## 6. Ideas Considered but Rejected, Superseded, or Deprioritised

| ID | Option | Status | Reason | Final or tentative? | Reconsider conditions | Related workstream | Label |
| --- | --- | --- | --- | --- | --- | --- | --- |
| REJECTED-01 | Stay permanently on C89/C++98 as mainline. | superseded | Good for old compiler reach, but too constraining once platform floor moved to Windows 7/Mavericks/Linux and repo already moved to C17/C++17. | mostly final for mainline | May remain relevant for retro projection/archive lanes. | WORKSTREAM-01 | FACT/INFERENCE |
| REJECTED-02 | Pure C99 for entire engine and game. | rejected | Suitable for small raylib/SDL games but poor fit for Dominium-scale providers, Workbench, resource ownership, composition, and modularity. | tentative but strong | Could be reconsidered for tiny projection clients or isolated C providers. | WORKSTREAM-02 | INFERENCE |
| REJECTED-03 | Pure C++11 for entire engine and game. | rejected | Viable but unnecessarily conservative; loses useful C++17 features and does not solve ABI/data-contract issues. | tentative but strong | Could be used for constrained native targets if toolchains require it. | WORKSTREAM-01 | INFERENCE |
| REJECTED-04 | Expose C++17 ABI/classes/STL across module boundaries. | rejected | Compiler/runtime ABI instability and ownership/lifetime hazards. | final | Never for stable public ABI; private in-process internals allowed. | WORKSTREAM-03 | FACT |
| REJECTED-05 | Universal primitive binary that runs on any OS/era. | rejected | Native binaries depend on ISA, binary format, loader, imports, runtime, and OS APIs. | final | Bytecode or generated projections could serve a different purpose. | WORKSTREAM-10 | FACT/INFERENCE |
| REJECTED-06 | Top-level platform folders such as windows/, mac/, android/. | rejected | Violates ownership-based canonical root model and creates platform-owned source identity. | final unless repo contract changes | Platform profiles/adapters belong under runtime/contracts/cmake/release as appropriate. | WORKSTREAM-05 | FACT/INFERENCE |
| REJECTED-07 | Let Workbench call private tools directly. | rejected | Would bypass command/evidence spine and create inconsistent behavior. | final | Debug-only internal panels may need explicit experimental status. | WORKSTREAM-09 | INFERENCE |

The most important rejected idea is pure C99. It is attractive for small raylib/SDL projects, but Dominium’s scope includes deterministic simulation, distributed zones, provider replacement, Workbench, packs/modules, AIDE governance, and long-lived artifacts. A hand-written C object system would not actually be simpler at this scale. Pure C++11 was also rejected as unnecessarily conservative. Unrestricted C++17 across ABI/data boundaries was rejected even though C++17 remains the internal implementation standard.

## 7. Important Reasoning, Rationale, and Tradeoffs

The visible rationale repeatedly balanced three forces: modern implementation leverage, long-term compatibility, and deterministic auditability. C17/C++17 gives enough modern power without depending on the latest unstable library/runtime ecosystems. A C-compatible ABI prevents compiler-specific C++ details from becoming public law. Fixed-width, little-endian formats prevent native architecture details from corrupting saves, replays, packets, or renderer commands. Provider/capability contracts prevent a backend such as SDL2, raylib, D3D11, or Metal from becoming the identity of the product. Support tiers prevent old systems from distorting mainline architecture while still leaving room for projections or archive builds.

The largest tradeoff is that this architecture needs more governance and proof than a simple game. The mitigation is to require vertical slices: one command, one provider, one pack/profile artifact, one diagnostic/refusal path, and one evidence packet before broad Workbench or plugin work.

## 8. Plans, Future Work, and Next Steps

The immediate plan is not more doctrine. The next active task is **FOUNDATION-REPAIR-DEPENDENCY-DIRECTION-01**. It should classify the 358 dependency-direction violations and 38 warnings, repair real boundary leaks, add only narrow justified exceptions, and rerun Foundation Closeout. After that, the next authorized product slice is **WORKBENCH-VALIDATION-SLICE-01**: validate one pack/profile/content artifact through a registered command, show the same result in CLI and Workbench, and emit diagnostics/evidence.

Recommended sequence:

1. Repair dependency-direction blocker.
2. Close Foundation Lock.
3. Update stale C89/C++98 wording in ABI and determinism specs.
4. Add architecture/source-native profiles for 64-bit/little-endian policy.
5. Design the smallest composition resolver and lockfile slice.
6. Run the first Workbench validation slice.
7. Build compatibility corpus and performance budgets.

## 9. Constraints, Preferences, and Non-Negotiables

### 9.1 Explicit Constraints and Preferences
| ID | Preference | Area | Explicit/inferred/uncertain | Strength | Practical implication | Risk if wrong | Label |
| --- | --- | --- | --- | --- | --- | --- | --- |
| PREF-01 | User wants direct, audit-ready, source-grounded answers. | communication | explicit | high | Use labels, citations, uncertainty, and concrete next actions. | User may distrust vague or overconfident answers. | FACT |
| PREF-02 | User prefers human-readable narrative before machine-readable registers. | handoff/reporting | explicit | high | Start preservation reports with prose explanation, then registers/spec sheets. | Machine-only output misses the stated goal. | FACT |
| PREF-03 | User values preserving rejected/superseded options and contradictions. | knowledge preservation | explicit | high | Do not flatten the history into only final decisions. | Future assistants may repeat rejected paths. | FACT |
| PREF-04 | User wants not to re-explain everything when moving chats. | workflow | explicit | high | Create context transfer packets, aggregators, and bootstrap prompts. | Loss of continuity and repeated prompting. | FACT |
| PREF-05 | User wants strong modularity but not arbitrary folder proliferation. | architecture | explicit/inferred | high | Use canonical roots and ownership/category names, not platform-specific top-level roots. | Repo rot or bad abstractions. | FACT/INFERENCE |
| PREF-06 | User is sensitive to assistant suggestions being mistaken for accepted decisions. | epistemic | explicit | high | Label decisions vs recommendations vs inferences. | Incorrect spec book aggregation. | FACT |

### 9.2 Inferred Constraints and Preferences
The user wants architectural clarity more than fashionable language choices. The user also wants future assistants to preserve tradeoffs, not collapse everything into an oversimplified final answer.

### 9.3 Uncertain or Unestablished Preferences
Exact tolerance for exceptions/RTTI inside private C++17 code remains unsettled. Exact platform floors and raylib/SDL2 priority remain unresolved.

## 10. Files, Artifacts, Outputs, and Prompts

| ID | Artifact / file / prompt / output | Type | Purpose | Status | Origin | Carry forward? | Notes | Label |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| ARTIFACT-01 | Pasted text.txt preservation prompt | uploaded prompt | Defines this preservation task and required output package. | available | User upload in current turn | yes | This file is the direct task source for the preservation package. | FACT |
| ARTIFACT-02 | CMakeLists.txt root C17/C++17 settings | repo file | Evidence that repo mainline currently sets C17 and C++17. | referenced | GitHub repo | yes | Cited in report; also indicates language migration already occurred. | FACT |
| ARTIFACT-03 | engine/CMakeLists.txt broad domino_engine target | repo file | Evidence of current aggregation of engine/game/runtime/render/platform/UI/network sources. | referenced | GitHub repo | yes | Important for target split and dependency repair. | FACT |
| ARTIFACT-04 | contracts/repo/layout.contract.toml | repo contract | Defines canonical root model and strict unknown-root policy. | referenced | GitHub repo | yes | Central to avoiding bad folder structures. | FACT |
| ARTIFACT-05 | engine/include/domino/abi.h | repo header | Current ABI helper design and stale C89/C++98 wording. | referenced | GitHub repo | yes | Needs terminology update but design should be preserved. | FACT |
| ARTIFACT-06 | SPEC_DETERMINISM.md | repo spec | Defines deterministic law: stable IDs, fixed-point, no pointers/floats, little-endian. | referenced | GitHub repo | yes | Needs language wording update but remains canonical law. | FACT |
| ARTIFACT-07 | SPEC_SIM_SCHEDULER.md | repo spec | Defines tick/phase/budget/ordering law and forbids OS time/thread timing as truth. | referenced | GitHub repo | yes | Core to distributed/parallel simulation. | FACT |
| ARTIFACT-08 | component/support/platform matrices | repo docs/contracts | Define backend status vocabulary, support tiers, and evidence requirements. | referenced | GitHub repo | yes | Need expansion for architecture/source-native tiers. | FACT |
| ARTIFACT-09 | latest task/review packets | AIDE context files | Record Foundation Lock blocked by dependency-direction strict failures. | referenced | GitHub repo | yes | Current immediate blocker and next action. | FACT |
| ARTIFACT-10 | Current preservation package files | generated files | Human-readable report, registers, context packet, spec sheet, aggregator packet, reader brief, audit, bootstrap prompt, in-chat reader, ZIP. | created now | This response | yes | Use these to continue or aggregate this chat. | FACT |

## 11. Open Questions and Unresolved Issues

| ID | Question / issue | Why it matters | Known information | Unknown information | Resolution path | Priority | Related workstream | Label |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| QUESTION-01 | What exact platform floors should be formalized: Windows 7 SP1, macOS 10.9.5, which Linux baseline, Android/iOS min versions? | Support floors determine toolchain, standard library, SDK, packaging, and testing. | Windows 7/Mavericks/Linux were discussed; mobile/consoles future. | Exact versions and support tiers remain to be locked and verified. | Create platform profile contracts after verifying official/toolchain facts. | P1 | WORKSTREAM-10 | UNCERTAIN |
| QUESTION-02 | How should the 358 dependency-direction violations be classified? | Foundation Lock is blocked until repaired. | Counts and blocker status known. | Specific files/causes not in this preservation prompt. | Run validator, classify real boundary leaks vs justified exceptions. | P0 | WORKSTREAM-05 | FACT/UNCERTAIN |
| QUESTION-03 | What is the first minimal composition resolver slice? | Resolver is central but can be overbuilt. | Need resolver for packs/modules/providers/apps. | Smallest useful schema and runtime path not yet specified. | Start with one pack/profile validation command and one provider. | P1 | WORKSTREAM-07 | INFERENCE |
| QUESTION-04 | How permissive should C++17 be internally? | Too strict wastes C++; too loose risks ABI/determinism leaks. | Broad policy exists; restricted subset discussed. | Exact exceptions/RTTI/stdlib policy per target not finalized. | Draft C++17 subset policy by layer. | P1 | WORKSTREAM-01 | UNCERTAIN |
| QUESTION-05 | Should raylib be a serious provider, a prototyping provider, or excluded in favor of SDL2/native backends? | It affects render/platform/audio/input provider shape. | Raylib/SDL2 treated as providers, not identity. | Priority and long-term role of raylib are unsettled. | Research support matrix and decide provider tier. | P2 | WORKSTREAM-06 | UNCERTAIN |
| QUESTION-06 | What exact trust/permission model should native modules, scripts, packs, and Workbench tools use? | Unsafe extensibility can compromise users and saves. | Need trust levels and permissions. | Concrete policy/schema absent. | Draft trust contract before native plugin implementation. | P1 | WORKSTREAM-08 | INFERENCE |
| QUESTION-07 | What are the first performance budgets? | Optimization needs measurable gates. | Tick/replay/render/load/allocation budgets proposed. | Specific thresholds absent. | Add baseline benchmarks, then set budget thresholds from measurements. | P1 | WORKSTREAM-11 | INFERENCE |

## 12. Risks, Failure Modes, and What Future Chats Might Get Wrong

| ID | Risk / failure mode | Consequence | Likelihood | Severity | Mitigation | Related workstream | Label |
| --- | --- | --- | --- | --- | --- | --- | --- |
| RISK-01 | Dependency-direction blocker is ignored while product work continues. | Foundation rot and false green status. | medium | high | Repair validator failures before Workbench/product slices. | WORKSTREAM-05 | FACT |
| RISK-02 | Assistant/future spec treats tentative recommendations as accepted user decisions. | Incorrect master spec and repeated bad advice. | medium | high | Use decision status labels and cite direct user acceptance. | all | FACT |
| RISK-03 | C++17 leaks into ABI/data formats. | Compiler lock-in, plugin breakage, save/replay incompatibility. | medium | high | C-compatible ABI validators and public header checks. | WORKSTREAM-03 | FACT |
| RISK-04 | Determinism breaks through thread timing, unordered iteration, pointer identity, or floats. | Replay/lockstep failures. | medium | critical | Keep scheduler/determinism validators and golden replay hashes. | WORKSTREAM-04 | FACT |
| RISK-05 | False support claims for Windows 7/Mavericks/Linux/legacy/mobile/consoles. | Users/builds fail; credibility loss. | medium | high | Support claims require toolchain/preset/smoke/package/release evidence. | WORKSTREAM-10 | FACT |
| RISK-06 | Over-architecture delays useful vertical slices. | Lots of contracts but no working product proof. | medium | medium | Use one pack/profile validation slice after Foundation green. | WORKSTREAM-09 | INFERENCE |
| RISK-07 | Raylib/SDL provider choice becomes product identity. | Backend lock-in and architecture distortion. | low | medium | Keep backends behind provider facades. | WORKSTREAM-06 | INFERENCE |
| RISK-08 | Generated files or stale context are mistaken for canonical source. | Aggregation and repo decisions use wrong authority. | medium | medium | Respect source hierarchy and label PROJECT-CONTEXT/UNCERTAIN. | all | FACT |

The biggest future-chat failure would be to answer the language question as if this were a small raylib project. It is not. Another failure would be to treat the final architecture as permission to build every layer immediately. The current red gate is still dependency direction.

## 13. What This Chat Contributes to the Larger Project or Future Spec Book

This chat should feed the Project Spec Book chapters on language baseline, ABI/data contracts, deterministic simulation, platform support tiers, provider/capability architecture, modular composition, Workbench/AIDE operating model, and release/support evidence. It should not be merged as a final implementation spec until the dependency-direction repair and platform/toolchain verification are done.

## 14. What I Should Remember

- The mainline is C17 + C++17, but stable boundaries remain C-compatible.
- 64-bit source-native and little-endian mainline are the intended architecture assumptions.
- C is for law; C++ is for machinery.
- Raylib/SDL2 are providers, not the product identity.
- Workbench is not authority; contracts/commands/evidence are authority.
- Extreme legacy support uses constrained builds or projections, not one universal binary.
- The immediate blocker is dependency-direction strict validation.
- The missing architectural center is composition resolver + lockfiles.

## 15. Best Questions I Can Ask Next in This Chat

### 15.1 Understanding the Chat
- Explain the difference between “C for law” and “C++ for machinery” using Dominium examples.
- Which parts of the old C89/C++98 plan are fully superseded and which survive as projection/archive ideas?

### 15.2 Decisions
- Which decisions in this chat are user-accepted versus assistant recommendations?
- What would cause us to revisit the C17/C++17 decision?

### 15.3 Tasks and Next Actions
- Draft the task packet for FOUNDATION-REPAIR-DEPENDENCY-DIRECTION-01.
- Draft the acceptance criteria for WORKBENCH-VALIDATION-SLICE-01.

### 15.4 Artifacts and Files
- Which repo docs need wording updates after the C17/C++17 decision?
- What should go into the architecture profile contract?

### 15.5 Risks and Verification
- Verify the Windows 7 and macOS 10.9 toolchain/library assumptions using official sources.
- List ways C++17 could accidentally break deterministic replay.

### 15.6 Future Spec Book / Aggregation
- Convert this chat’s decisions into formal spec-book requirements.
- Merge this chat with other Dominium platform/renderer chats and identify conflicts.

### 15.7 Deep-Dive Questions Specific to This Chat
- Design the composition resolver’s first minimal schema.
- Define trust levels for packs, modules, scripts, and native providers.
- Propose a CMake target split from the current broad domino_engine target.

## 16. Compact Human Summary

This chat is the point where Dominium’s mainline architecture moved from the old C89 engine + C++98 game idea into a modern but still conservative C17 + C++17 baseline. The user repeatedly tested alternative language strategies: old C/C++, pure C99, pure C11/C17, pure C++11, pure C++17, and newer C++ standards. The final position is not a language ideology. It is a layered architecture: C-compatible stable law at the boundaries and C++17 implementation machinery inside.

The key rule is that C should own deterministic law and stable formats: ABI structs, fixed-width types, stable IDs, packets, saves, replays, fixed-point math, renderer command IR, capability/refusal structs, and provider facades. C++17 should own game orchestration, domain systems, runtime services, providers, renderer/platform backends, apps, tools, Workbench, jobs, resource ownership, and composition. This lets Dominium benefit from RAII, move semantics, variants/optionals internally, templates, constexpr, and safer orchestration, without exporting C++ ABI or native object layouts into long-term contracts.

The chat also established a 64-bit source-native direction. Full native products should target x86_64 and arm64. 32-bit is not deleted from imagination, but it is downgraded to constrained-native or projection support. Old systems such as Windows 98 and Mac OS 9 should consume replay viewers, snapshots, thin clients, or generated subsets rather than forcing the mainline to remain old-standard or 32-bit. The project should also remain little-endian mainline and use explicit little-endian serialization for stable data.

The repo context matters. The current CMake state discussed in this chat already reflects C17 and C++17, but the repo still has stale C89/C++98 wording in some docs/headers and a broad domino_engine target that aggregates many ownership domains. That target should eventually be split into layered targets once dependency-direction repairs are complete. The layout contract is already directionally right: keep canonical roots and avoid top-level platform folders or arbitrary module roots.

The user’s broader future plan around Domino, Dominium, Workbench, AIDE, contracts, tests, replay, and evidence was mostly accepted. The missing pieces identified were composition resolver, lockfiles, compatibility corpus, trust/permission model, virtual roots, performance budgets, and public-surface promotion protocol. These are necessary to make code, data, modules, packs, providers, apps, Workbench, and AIDE actually compose rather than becoming manually wired subsystems.

The immediate next action is not more architecture brainstorming. The latest project task/review packets say Foundation Lock is blocked because dependency-direction strict validation reports 358 violations and 38 warnings. The next task is FOUNDATION-REPAIR-DEPENDENCY-DIRECTION-01. Only after that should Workbench validation or product-facing module work proceed.
