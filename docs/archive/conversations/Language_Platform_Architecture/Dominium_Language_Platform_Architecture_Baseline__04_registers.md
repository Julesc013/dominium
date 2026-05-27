# STRUCTURED REGISTERS — Dominium Language, Platform, and Architecture Baseline

## 17. Workstream Register

| ID | Name | Objective | Current state | Desired end state | Status | Priority | Confidence | Label |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| WORKSTREAM-01 | Language and architecture baseline | Set the active implementation language and machine baseline for the mainline project. | C17/C++17 and 64-bit source-native direction accepted in the discussion; repo CMake now reflects C17/C++17. | Clear mainline baseline: C17/C++17, x86_64/arm64, little-endian, C-compatible ABI. | active | P0 | 4 | FACT/INFERENCE |
| WORKSTREAM-02 | C/C++ responsibility split | Define what belongs in C and what belongs in C++. | Repeatedly refined from engine=C/game=C++ to law=C and machinery=C++. | C17 owns stable law and ABI; C++17 owns orchestration, providers, apps, Workbench, and tools. | active | P0 | 4 | FACT/INFERENCE |
| WORKSTREAM-03 | ABI and public surface governance | Prevent C++ implementation details from becoming permanent binary/data contracts. | Existing ABI header is POD/extern-C/return-code oriented but old wording remains. | C-compatible ABI, POD-only, versioned, no STL/classes/exceptions/RTTI across stable boundaries. | active | P0 | 5 | FACT |
| WORKSTREAM-04 | Determinism and scheduler law | Preserve replayable, platform-independent simulation behavior. | Specs already define stable IDs, canonical order, fixed-point, no OS time/thread timing as truth. | Language migration does not weaken determinism; rules remain enforced by tests/contracts. | active | P0 | 5 | FACT |
| WORKSTREAM-05 | Repository boundaries and Foundation Lock | Clean dependency direction and prove the foundation before product work. | Foundation Lock is blocked by dependency-direction strict failures: 358 violations and 38 warnings. | Dependency-direction validator green; Foundation Lock closed; Workbench slice authorized. | blocked | P0 | 5 | FACT |
| WORKSTREAM-06 | Provider/capability runtime model | Make render/platform/storage/network/audio/input backends replaceable and explicit. | Component matrices exist; many backends are available/stub/planned/research. | Providers declare capabilities, refusals, fallback, conformance tests, and determinism impact. | active | P1 | 4 | FACT/INFERENCE |
| WORKSTREAM-07 | Composition resolver and lockfiles | Make modular packs/modules/providers/apps reproducible instead of manually wired. | Identified as the major missing integration layer. | One resolver selects packs/modules/providers and emits lockfiles/evidence/refusals. | missing | P1 | 4 | INFERENCE |
| WORKSTREAM-08 | Packs/modules/content/trust | Support extensible authored data and modules without unsafe plugin sprawl. | Vocabulary clarified: pack, module, provider, service, component, workspace, app, artifact. | Packs and modules have descriptors, trust/permission rules, validation fixtures, and overlay/conflict law. | active | P1 | 4 | INFERENCE |
| WORKSTREAM-09 | Workbench and AIDE operating model | Use Workbench as command/evidence surface and AIDE as repo control-plane. | Plan says Workbench is not authority and must use same command/service/result/refusal spine as CLI/tests. | Workbench validates via registered commands; AIDE governs with task/evidence packets and validators. | active | P1 | 4 | FACT/INFERENCE |
| WORKSTREAM-10 | Legacy and platform support tiers | Support older systems without letting them govern mainline architecture. | Windows 98/Mac OS 9/old 32-bit systems moved to projection/constrained/archive tiers. | Source-native 64-bit mainline; legacy systems use thin clients, replay viewers, snapshots, or generated subsets. | active | P1 | 4 | FACT/INFERENCE |
| WORKSTREAM-11 | Performance and efficiency contracts | Make optimization measurable and compatible with determinism. | Performance discussed as data layout, arenas, command buffers, batching, budgets, provider conformance. | Benchmarks and budgets for tick, replay, rendering, load, allocation, Workbench latency. | planned | P1 | 4 | INFERENCE |

## 18. Decision Register

| ID | Decision | Status | Evidence / basis | Rationale | Implications | Related workstream | Confidence | Label |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| DECISION-01 | Mainline should use C17 and C++17 rather than C89/C++98, pure C99, or pure C++11. | accepted direction | User repeatedly moved toward C17/C++17; repo CMake now requires C17/C++17. | Keeps modern implementation leverage while staying conservative enough for Windows 7/Mavericks-era planning. | Affects all source/build policy, docs, validators, and toolchain matrices. | WORKSTREAM-01 | 4 | FACT/INFERENCE |
| DECISION-02 | Full source-native products should be 64-bit-first/64-bit-only: x86_64 and arm64. | accepted direction | User asked about dropping 32-bit; answer recommended 64-bit full-native and 32-bit only as constrained/projection. | Reduces matrix complexity and matches modern desktop/mobile/console direction. | Requires pointer-width audit and fixed-width save/replay/network formats. | WORKSTREAM-10 | 4 | FACT/INFERENCE |
| DECISION-03 | Keep little-endian mainline and explicit little-endian data formats. | accepted direction | Determinism spec already says supported runtime targets are little-endian and prefers explicit little-endian routines. | Avoids large portability burden while retaining cross-platform determinism across chosen targets. | Big-endian becomes unsupported unless a future projection lane appears. | WORKSTREAM-04 | 5 | FACT |
| DECISION-04 | Public boundary remains C-compatible, POD-only, versioned, and no C++ ABI leakage. | accepted direction | Existing ABI design and repeated answers converge on this. | Enables C/C++/tools/projections/plugins without binding to compiler-specific C++ ABI. | All public headers and provider interfaces must avoid STL/classes/exceptions/allocator ownership. | WORKSTREAM-03 | 5 | FACT |
| DECISION-05 | C17 owns deterministic law and stable formats; C++17 owns machinery and orchestration. | accepted direction | The conversation corrected engine=C/game=C++ into law=C/machinery=C++. | Gives determinism and stable contracts while using C++ where it provides real value. | Requires target split and boundary validators. | WORKSTREAM-02 | 4 | FACT/INFERENCE |
| DECISION-06 | Raylib and SDL2 should be providers/backends, not architectural identity. | accepted direction | User asked if C APIs imply pure C; answer rejected that. | Allows direct C API integration without forcing the whole engine/game to C99. | Provider facade must remain C-compatible. | WORKSTREAM-06 | 4 | INFERENCE |
| DECISION-07 | Do not pursue a universal primitive binary for all systems. | accepted direction | Conversation clarified native binaries are tied to ISA, object format, loader, ABI, runtime, and OS APIs. | Prevents false portability assumptions for Windows 98/Mac OS 9/consoles. | Legacy support uses projections/constrained builds/archive runners. | WORKSTREAM-10 | 4 | FACT/INFERENCE |
| DECISION-08 | Foundation Lock must not close while dependency-direction strict validation is red. | accepted/current blocker | Latest task and review packets record 358 violations and 38 warnings and block Workbench slice. | Prevents product/UI work before dependency law is enforceable. | Next work is dependency-direction repair. | WORKSTREAM-05 | 5 | FACT |
| DECISION-09 | Workbench is not authority; it is a command/evidence surface over contracts/services/providers. | accepted direction | User pasted unified plan and assistant refined it. | Prevents Workbench from bypassing CLI/tests/AIDE and fragmenting behavior. | First Workbench slice must use registered command/result/refusal/evidence path. | WORKSTREAM-09 | 4 | FACT/INFERENCE |
| DECISION-10 | Composition resolver and lockfiles are missing central pieces. | recommended, not yet implemented | Assistant identified them as missing in response to user’s “what are we missing?” question. | Needed to make modules/packs/providers/apps reproducible and extensible. | Should become near-term design work after Foundation repair. | WORKSTREAM-07 | 4 | INFERENCE |

## 19. Task Register

| ID | Task | Priority | Urgency | Owner | Dependencies | Inputs needed | Expected output | Next step | Related workstream | Label |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| TASK-01 | Run FOUNDATION-REPAIR-DEPENDENCY-DIRECTION-01 and classify/fix dependency violations. | P0 | U0 | repo maintainer / future assistant | Latest closeout evidence; dependency validator output | Violation list, architecture law, allowed exception policy | Green dependency-direction strict validator or truthful remaining blocker report | Inspect violations, distinguish real leaks from needed narrow exceptions | WORKSTREAM-05 | FACT |
| TASK-02 | Update ABI wording from C89/C++98-visible to C-compatible ABI. | P1 | U1 | repo maintainer / future assistant | Current abi.h wording; language baseline decision | ABI header and related docs | Docs/header terminology aligned with C17/C++17 mainline while preserving ABI law | Patch header comments and spec references | WORKSTREAM-03 | FACT/INFERENCE |
| TASK-03 | Update determinism spec wording that still assumes C89/C90 deterministic modules. | P1 | U1 | repo maintainer / future assistant | SPEC_DETERMINISM; C17/C++17 decision | Spec patch | C17 source allowed; fixed-width/little-endian/no-float/no-pointer-order law preserved | Patch spec and add validator if useful | WORKSTREAM-04 | FACT/INFERENCE |
| TASK-04 | Add explicit architecture profile contract for 64-bit/little-endian/source-native tiers. | P1 | U1 | repo maintainer / future assistant | Platform/support matrices; 64-bit decision | contracts/arch or platform profile files | x86_64/arm64 mainline; 32-bit constrained/projection; no serialized pointer-size types | Draft contract and validation rules | WORKSTREAM-01 | INFERENCE |
| TASK-05 | Split broad domino_engine target into layered targets. | P1 | U1 | repo maintainer / future assistant | engine/CMakeLists currently aggregates engine/game/runtime/render/platform/UI/network/package code | CMake target split plan and incremental patches | Ownership boundaries reflected in build graph | After dependency repair, split targets without breaking tests | WORKSTREAM-05 | FACT/INFERENCE |
| TASK-06 | Design composition resolver contract. | P1 | U1 | architecture owner / future assistant | Module/pack/provider/app vocabulary | contracts/composition draft | Resolver selects packs/modules/providers, emits lockfile/refusals/evidence | Create minimal schema and one vertical slice | WORKSTREAM-07 | INFERENCE |
| TASK-07 | Define lockfile formats for pack/module/provider/profile/toolchain/release composition. | P1 | U1 | architecture owner / future assistant | Composition resolver design | Lockfile schemas and golden examples | Reproducible modular configuration | Draft lockfile taxonomy | WORKSTREAM-07 | INFERENCE |
| TASK-08 | Build compatibility corpus for saves, replays, packs, commands, diagnostics, provider descriptors. | P1 | U1 | test/validation owner | Stable artifact decisions | tests/compat fixtures | Compatibility proof over time | Start with one pack/profile validation fixture | WORKSTREAM-04 | INFERENCE |
| TASK-09 | Define trust and permission model for packs/modules/native code/scripts/tools. | P1 | U1 | security/trust owner | Pack/module extensibility plan | contracts/trust extensions | Unsafe native/plugin behavior gated by policy and diagnostics | Draft trust levels and permissions | WORKSTREAM-08 | INFERENCE |
| TASK-10 | Implement WORKBENCH-VALIDATION-SLICE-01 after Foundation Lock closes. | P1 | U1 after TASK-01 | Workbench owner / future assistant | Foundation green; command/diagnostic/evidence contracts | CLI + Workbench validation of one artifact | Same command/result/refusal/evidence path across CLI and Workbench | Wait until dependency-direction repair passes | WORKSTREAM-09 | FACT/INFERENCE |
| TASK-11 | Add performance budgets and benchmark gates. | P1 | U2 | performance owner | Determinism scheduler, renderer IR, runtime providers | Benchmark suite and budget contracts | Measured tick/replay/render/load/allocation performance | Define first five budget metrics | WORKSTREAM-11 | INFERENCE |
| TASK-12 | Verify external toolchain/deployment claims before baking support floors into requirements. | P1 | U1 | future assistant / build owner | Windows 7, macOS 10.9, Linux, raylib/SDL2 claims | Verification report with primary sources | Support matrix based on current official docs/toolchain tests | Research with official sources and local smoke builds | WORKSTREAM-10 | UNCERTAIN |

## 20. Constraint Register

| ID | Constraint | Type | Hard/soft | Source / basis | Practical implication | Violation risk | Confidence | Label |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| CONSTRAINT-01 | Mainline uses C17 and C++17 with extensions off. | technical | hard | Current CMake root and target settings | Code should compile under standards-conforming C17/C++17 modes. | Toolchain drift or nonstandard extensions enter core. | 5 | FACT |
| CONSTRAINT-02 | Full source-native products target 64-bit x86_64/arm64 only. | architecture | hard for mainline | User accepted 64-bit direction in chat | Do not let 32-bit memory limits govern mainline design. | Legacy support could silently re-expand matrix. | 4 | INFERENCE |
| CONSTRAINT-03 | Stable data formats use fixed-width values and explicit little-endian encoding. | data/determinism | hard | Determinism spec | No size_t, long, uintptr_t, native padding, or raw pointers in save/replay/network formats. | Cross-platform replay/save breakage. | 5 | FACT |
| CONSTRAINT-04 | Public ABI is C-compatible, POD-only, versioned, no exceptions. | ABI | hard | ABI header and repeated decisions | No STL/classes/templates/RTTI/exceptions/allocator ownership across ABI. | Compiler/runtime coupling and plugin breakage. | 5 | FACT |
| CONSTRAINT-05 | Authoritative simulation cannot depend on OS time, thread timing, async completion, pointer order, hash iteration, or floats. | determinism | hard | Determinism and scheduler specs | Parallelism is allowed only with canonical commit and stable ordering. | Replay/lockstep nondeterminism. | 5 | FACT |
| CONSTRAINT-06 | Repository must use canonical roots and not reintroduce arbitrary top-level roots. | repo layout | hard | layout.contract.toml | New concepts belong under apps/ engine/ game/ runtime/ contracts/ tools/ etc. | Future cleanup cycles and fractured ownership. | 5 | FACT |
| CONSTRAINT-07 | Workbench cannot bypass command/service/result/refusal/evidence spine. | architecture | hard | Unified plan discussion | Workbench is a client of contracts and services, not a private-tool shortcut. | Different UI paths produce inconsistent behavior. | 4 | INFERENCE |
| CONSTRAINT-08 | Support claims require evidence, not just tier labels. | release/support | hard | support tiers and component matrix docs | Stubs/planned/research are not support claims. | False portability/release claims. | 5 | FACT |
| CONSTRAINT-09 | Legacy targets consume constrained builds/projections; they do not define mainline architecture. | portability | hard for mainline | Cross-platform discussion | Windows 98/Mac OS 9/old 32-bit targets remain projection/archive unless justified. | Mainline dragged back to obsolete constraints. | 4 | INFERENCE |
| CONSTRAINT-10 | No new product/Workbench feature work before Foundation dependency-direction blocker is handled. | process | hard until green | latest task/review packets | Do repair work first. | Unstable foundation hidden by UI/product progress. | 5 | FACT |

## 21. User Preference Register

| ID | Preference | Area | Explicit/inferred/uncertain | Strength | Practical implication | Risk if wrong | Label |
| --- | --- | --- | --- | --- | --- | --- | --- |
| PREF-01 | User wants direct, audit-ready, source-grounded answers. | communication | explicit | high | Use labels, citations, uncertainty, and concrete next actions. | User may distrust vague or overconfident answers. | FACT |
| PREF-02 | User prefers human-readable narrative before machine-readable registers. | handoff/reporting | explicit | high | Start preservation reports with prose explanation, then registers/spec sheets. | Machine-only output misses the stated goal. | FACT |
| PREF-03 | User values preserving rejected/superseded options and contradictions. | knowledge preservation | explicit | high | Do not flatten the history into only final decisions. | Future assistants may repeat rejected paths. | FACT |
| PREF-04 | User wants not to re-explain everything when moving chats. | workflow | explicit | high | Create context transfer packets, aggregators, and bootstrap prompts. | Loss of continuity and repeated prompting. | FACT |
| PREF-05 | User wants strong modularity but not arbitrary folder proliferation. | architecture | explicit/inferred | high | Use canonical roots and ownership/category names, not platform-specific top-level roots. | Repo rot or bad abstractions. | FACT/INFERENCE |
| PREF-06 | User is sensitive to assistant suggestions being mistaken for accepted decisions. | epistemic | explicit | high | Label decisions vs recommendations vs inferences. | Incorrect spec book aggregation. | FACT |

## 22. Open Questions Register

| ID | Question / issue | Why it matters | Known information | Unknown information | Resolution path | Priority | Related workstream | Label |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| QUESTION-01 | What exact platform floors should be formalized: Windows 7 SP1, macOS 10.9.5, which Linux baseline, Android/iOS min versions? | Support floors determine toolchain, standard library, SDK, packaging, and testing. | Windows 7/Mavericks/Linux were discussed; mobile/consoles future. | Exact versions and support tiers remain to be locked and verified. | Create platform profile contracts after verifying official/toolchain facts. | P1 | WORKSTREAM-10 | UNCERTAIN |
| QUESTION-02 | How should the 358 dependency-direction violations be classified? | Foundation Lock is blocked until repaired. | Counts and blocker status known. | Specific files/causes not in this preservation prompt. | Run validator, classify real boundary leaks vs justified exceptions. | P0 | WORKSTREAM-05 | FACT/UNCERTAIN |
| QUESTION-03 | What is the first minimal composition resolver slice? | Resolver is central but can be overbuilt. | Need resolver for packs/modules/providers/apps. | Smallest useful schema and runtime path not yet specified. | Start with one pack/profile validation command and one provider. | P1 | WORKSTREAM-07 | INFERENCE |
| QUESTION-04 | How permissive should C++17 be internally? | Too strict wastes C++; too loose risks ABI/determinism leaks. | Broad policy exists; restricted subset discussed. | Exact exceptions/RTTI/stdlib policy per target not finalized. | Draft C++17 subset policy by layer. | P1 | WORKSTREAM-01 | UNCERTAIN |
| QUESTION-05 | Should raylib be a serious provider, a prototyping provider, or excluded in favor of SDL2/native backends? | It affects render/platform/audio/input provider shape. | Raylib/SDL2 treated as providers, not identity. | Priority and long-term role of raylib are unsettled. | Research support matrix and decide provider tier. | P2 | WORKSTREAM-06 | UNCERTAIN |
| QUESTION-06 | What exact trust/permission model should native modules, scripts, packs, and Workbench tools use? | Unsafe extensibility can compromise users and saves. | Need trust levels and permissions. | Concrete policy/schema absent. | Draft trust contract before native plugin implementation. | P1 | WORKSTREAM-08 | INFERENCE |
| QUESTION-07 | What are the first performance budgets? | Optimization needs measurable gates. | Tick/replay/render/load/allocation budgets proposed. | Specific thresholds absent. | Add baseline benchmarks, then set budget thresholds from measurements. | P1 | WORKSTREAM-11 | INFERENCE |

## 23. Artifact Ledger

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

## 24. Rejected / Superseded Options Register

| ID | Option | Status | Reason | Final or tentative? | Reconsider conditions | Related workstream | Label |
| --- | --- | --- | --- | --- | --- | --- | --- |
| REJECTED-01 | Stay permanently on C89/C++98 as mainline. | superseded | Good for old compiler reach, but too constraining once platform floor moved to Windows 7/Mavericks/Linux and repo already moved to C17/C++17. | mostly final for mainline | May remain relevant for retro projection/archive lanes. | WORKSTREAM-01 | FACT/INFERENCE |
| REJECTED-02 | Pure C99 for entire engine and game. | rejected | Suitable for small raylib/SDL games but poor fit for Dominium-scale providers, Workbench, resource ownership, composition, and modularity. | tentative but strong | Could be reconsidered for tiny projection clients or isolated C providers. | WORKSTREAM-02 | INFERENCE |
| REJECTED-03 | Pure C++11 for entire engine and game. | rejected | Viable but unnecessarily conservative; loses useful C++17 features and does not solve ABI/data-contract issues. | tentative but strong | Could be used for constrained native targets if toolchains require it. | WORKSTREAM-01 | INFERENCE |
| REJECTED-04 | Expose C++17 ABI/classes/STL across module boundaries. | rejected | Compiler/runtime ABI instability and ownership/lifetime hazards. | final | Never for stable public ABI; private in-process internals allowed. | WORKSTREAM-03 | FACT |
| REJECTED-05 | Universal primitive binary that runs on any OS/era. | rejected | Native binaries depend on ISA, binary format, loader, imports, runtime, and OS APIs. | final | Bytecode or generated projections could serve a different purpose. | WORKSTREAM-10 | FACT/INFERENCE |
| REJECTED-06 | Top-level platform folders such as windows/, mac/, android/. | rejected | Violates ownership-based canonical root model and creates platform-owned source identity. | final unless repo contract changes | Platform profiles/adapters belong under runtime/contracts/cmake/release as appropriate. | WORKSTREAM-05 | FACT/INFERENCE |
| REJECTED-07 | Let Workbench call private tools directly. | rejected | Would bypass command/evidence spine and create inconsistent behavior. | final | Debug-only internal panels may need explicit experimental status. | WORKSTREAM-09 | INFERENCE |

## 25. Risk Register

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

## 26. Verification Queue

| ID | Item requiring verification | Why verification is needed | Suggested source/type | Priority | Related workstream | Label |
| --- | --- | --- | --- | --- | --- | --- |
| VERIFY-01 | Current official Windows 7 targeting status for MSVC/VS toolchains. | Toolchain support is time-sensitive and affects release floors. | Official Microsoft docs plus smoke build on Windows 7/VM. | P1 | WORKSTREAM-10 | UNCERTAIN |
| VERIFY-02 | macOS 10.9.5 viability for C++17 language and restricted libc++ subset. | Deployment target and library features determine what can be used. | Apple/Xcode/libc++ docs plus smoke build on Mavericks target. | P1 | WORKSTREAM-10 | UNCERTAIN |
| VERIFY-03 | Linux glibc/musl baseline for distributed binaries. | Building on too-new glibc can break older distros. | Distro/toolchain build container tests. | P1 | WORKSTREAM-10 | UNCERTAIN |
| VERIFY-04 | SDL2/raylib support for chosen platform floors and 64-bit-only policy. | Backend provider choices depend on library support. | Official SDL2/raylib docs and build tests. | P2 | WORKSTREAM-06 | UNCERTAIN |
| VERIFY-05 | Exact dependency-direction violation categories. | Foundation repair needs targeted fixes, not broad exceptions. | Run check_dependency_directions.py --strict and inspect output. | P0 | WORKSTREAM-05 | FACT/UNCERTAIN |
| VERIFY-06 | Current repo HEAD still matches cited state when future work begins. | Repo may change after this report. | Git status / fetch latest / inspect CMake and task packets. | P1 | all | UNCERTAIN |
| VERIFY-07 | Console SDK constraints for PS5/Xbox/Switch. | Console support depends on private partner SDKs and license terms. | Official partner docs after enrollment; avoid public speculation. | P3 | WORKSTREAM-10 | UNCERTAIN |

## 27. Chronological Timeline Register

| Sequence | Event / topic | What changed or was decided | Why it mattered | Current relevance | Confidence |
| --- | --- | --- | --- | --- | --- |
| 1 | Initial language question | User asked whether switching from C89/C++98 to newer C/C++ gives performance or feature gains. | Started the architecture/language baseline review. | Historical basis for why language choice became central. | 5 |
| 2 | Major C/C++ standard comparisons | Runtime performance and capability gains by C/C++ version were compared. | Distinguished compiler improvements from language-level guarantees. | Supports final C17/C++17 policy. | 4 |
| 3 | Versioned plan C89/C++98 then C11/C++17 | User proposed v0/v1 old standards, v2+ modern standards. | Established staged migration thinking. | Superseded by mainline C17/C++17 decision. | 4 |
| 4 | Mix-and-match question | C11 engine + C++98 game and reverse combinations were examined. | Clarified ABI/memory-model boundaries. | Still relevant to provider/substrate separation. | 4 |
| 5 | What should be C vs C++ | Conversation corrected folder-based split into semantic split: law vs machinery. | Most important conceptual clarification. | Core design rule. | 5 |
| 6 | Current repo and language research | Repo files were inspected and language choices compared against actual source roles. | Grounded advice in codebase instead of abstract language preference. | Needs re-verification as repo changes. | 4 |
| 7 | Mainline C17/C++17 pivot | User wanted to abandon old plans and move to C17/C++17. | Became the active baseline. | Current repo reflects it. | 5 |
| 8 | Future platforms and monorepo support | XP/98/OS X 10.6/Mac OS 9/mobile/consoles discussed. | Led to support modes: source_native, constrained, projection, archive. | Feeds platform/support matrix. | 4 |
| 9 | 32-bit support question | User asked whether to drop 32-bit. | Led to 64-bit source-native policy and fixed-width data warnings. | Feeds architecture profile. | 4 |
| 10 | Best performance/modularity portability pass | Repo source checked again; recommendations included 64-bit, little-endian, C ABI, split targets, matrices. | Integrated language/platform choices with repo architecture. | High relevance. | 4 |
| 11 | Unified future plan review | User pasted a consolidated plan and asked if best/future-proof. | Missing pieces identified: composition resolver, lockfiles, compatibility corpus, trust, virtual roots, performance budgets. | Direct input to spec book. | 4 |
| 12 | C99/C++11/raylib/SDL advice challenged | User pasted external-style advice favoring C99/C++11 and asked whether to pivot. | Conclusion: do not pivot; C17+C++17 remains best; raylib/SDL are providers. | Prevents regression to simpler but weaker architecture. | 4 |
| 13 | Preservation prompt uploaded | User uploaded the maximum-fidelity preservation/export prompt. | Current task became report and handoff package creation. | This generated package. | 5 |

## 28. Spec Book Contribution Register

| Spec-book area | Contribution from this chat | Source IDs | Should become requirement/context/open issue? | Confidence | Notes |
| --- | --- | --- | --- | --- | --- |
| Language baseline | C17 + C++17 mainline, with C-compatible public ABI. | DECISION-01, DECISION-04 | requirement | 4 | Needs stale docs updated. |
| Architecture baseline | 64-bit source-native, little-endian, fixed-width data formats. | DECISION-02, DECISION-03 | requirement | 4 | Needs architecture profile contract. |
| C/C++ layering | C17 law; C++17 machinery. | DECISION-05 | requirement | 4 | Core design rule. |
| Determinism | Stable IDs, canonical ordering, fixed-point, no floats/pointer order/thread timing. | CONSTRAINT-05 | requirement | 5 | Existing specs remain canonical with language wording update. |
| ABI/public surfaces | No C++ ABI leakage, POD-only, versioned, no exceptions. | DECISION-04, CONSTRAINT-04 | requirement | 5 | Important for providers/projections/tools. |
| Modularity/composition | Composition resolver, lockfiles, modules, providers, packs, services. | WORKSTREAM-07, DECISION-10 | open issue / requirement candidate | 4 | Needs first minimal slice. |
| Workbench/AIDE | Workbench command/evidence client; AIDE control-plane harness. | WORKSTREAM-09 | context + requirement | 4 | Workbench slice blocked until Foundation green. |
| Portability/support tiers | Legacy via constrained/projection/archive; no universal binary. | WORKSTREAM-10, DECISION-07 | requirement/context | 4 | External support floors require verification. |
