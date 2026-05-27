# Accompanying Detailed Conversation Summary Report — Dominium Language, Platform, and Architecture Baseline

**Date anchor:** 2026-05-27 Australia/Melbourne  
**Scope:** This visible chat and the files generated from it.  
**Purpose:** Human-readable companion report for the full preservation package.  
**Primary caveat:** This report reconstructs the visible conversation and the prior preservation package. It does not claim complete access to every other old chat in the wider project. Some external platform/toolchain facts discussed in the chat should be re-verified before being converted into final project law.

---

## 1. Executive summary

This conversation was an extended architectural decision session for **Dominium**, focused on the project’s long-term language, platform, ABI, modularity, portability, performance, and repo-governance baseline. The original question was narrow: whether the project would gain performance or features by moving from **C89 and C++98** to newer C/C++ versions. Over the course of the chat, the discussion expanded into a broader architectural doctrine for the whole project: what should be C, what should be C++, what platforms should be first-class, how legacy systems should be handled, whether 32-bit support should remain, how C APIs like SDL2/raylib should fit, how modules/packs/providers/apps should compose, and what must happen before Workbench or product features proceed.

The biggest evolution was this: the initial plan treated **C89 engine + C++98 game** as a deliberate portability baseline. That was later superseded after the target floor narrowed to **Windows 7 SP1, macOS 10.9.5 Mavericks, and Linux**. Under that floor, the mainline direction became **C17 + C++17**, with a **64-bit**, **little-endian**, **C-compatible ABI** baseline. The chat repeatedly emphasized that “C vs C++” should not be decided by folder name. The stronger doctrine became: **C17 owns law; C++17 owns machinery**.

In practical terms, C17 should own deterministic substrate, ABI-facing structures, fixed-width types, stable IDs, save/replay/wire formats, canonical hashing, fixed-point math, renderer command IR, and low-level facades. C++17 should own game orchestration, domain systems, runtime services, platform/render providers, apps, Workbench, tools, job systems, resource ownership, and higher-level composition. The public boundary should remain C-compatible and POD-only. C++17 can be used internally, but C++ ABI, STL types, exceptions, RTTI, allocator ownership, raw platform handles, pointer-sized serialization, and native object layout must not cross stable ABI/data-format boundaries.

Another major conclusion was that **full native mainline builds should be 64-bit only**, targeting x86_64 and arm64. Supporting 32-bit as a first-class native product was judged to impose too much cost: two ABI families, smaller address space, dependency duplication, platform/toolchain gravity, more testing, more installer/runtime variants, and higher risk of pointer-size bugs. However, the code should remain 32/64-clean where practical. Legacy 32-bit or retro systems can remain as **constrained native**, **contract projection**, or **archive runner** lanes, not as mainline constraints.

The conversation also rejected the idea of a universal “primitive binary” that could execute across arbitrary old and modern systems. Native binaries remain bound to CPU ISA, executable format, dynamic loader, ABI, runtime libraries, kernel/API imports, and OS version. The clean model is: one canonical source/project with contracts, content, deterministic law, public ABI, tests, replay/save formats, and renderer IR; many target products that are built natively, constrained, or projected depending on platform.

A later prompt challenged the C17/C++17 direction by proposing pure C99 or C++11, especially because raylib and SDL2 expose C APIs. The conclusion remained unchanged: raylib/SDL2 should be treated as **providers**, not as architectural identity. Their C APIs do not require the entire game/engine to be pure C. C++17 can call C APIs directly, while the project keeps C-compatible provider facades.

The final architecture direction included more than language/platform choices. The chat converged on a contract-governed modular project model: **Domino** as reusable deterministic/runtime substrate; **Dominium** as game/product family; **Workbench** as production, validation, editing, inspection, packaging, and evidence environment; **AIDE** as repo/control-plane harness; and **contracts/tests/evidence** as authority. A key warning emerged: do not build Workbench UI, runtime module loaders, native plugin systems, or product features before Foundation Lock is green. The latest task packet recorded Foundation Lock as blocked because dependency-direction strict validation reports **358 violations and 38 warnings**. The immediate next action was therefore **FOUNDATION-REPAIR-DEPENDENCY-DIRECTION-01**.

A preservation task was then uploaded in `Pasted text.txt`, asking for a maximum-fidelity preservation package. In response, a full handoff package was generated with manifest, human report, context transfer packet, spec sheet, registers, aggregator packet, reader brief, verification/audit, future-chat bootstrap prompt, in-chat reader, and zip package. This current companion report adds an additional human-readable explanation of the entire visible conversation and bundles it with those files into one updated complete package.

---

## 2. Chronological narrative of the conversation

### 2.1 The first framing: old standards versus newer standards

The chat began with the user asking the assistant to inspect the broader project context and answer whether Dominium would see performance or feature gains by switching from **C89 and C++98** to newer versions of C or C++. The initial answer was that newer standards can provide real gains, but not by magic. Modern compilers already optimize old-standard code well. The gains come from language features that let the compiler and programmer express stronger guarantees: aliasing hints, atomics, move semantics, constexpr, copy elision, typed ownership, and cleaner concurrency.

At this stage, the assistant treated **C89/C++98** as a compatibility-oriented baseline. C89 was framed as good for old compilers, stable ABI, and deterministic substrate. C++98 was framed as usable for app/game layers but missing modern ownership and concurrency tools.

### 2.2 Runtime-performance comparison by C and C++ standard

The user then asked for a more systematic comparison of major C and C++ versions, specifically runtime performance rather than compile time. This produced separate tables for C and C++.

For C, the main conclusions were:

- **C89/C90** was baseline.
- **C99** gives the most meaningful C-side performance/capability gain through `restrict`, better `inline`, flexible array members, mixed declarations, and cleaner data-oriented code.
- **C11** adds atomics and a memory model, useful for concurrency, but only where supported and used carefully.
- **C17/C18** is effectively a corrected C11 baseline rather than a new performance standard.
- **C23** was considered interesting but not a mainline fit for legacy-compatible targets.

For C++, the main conclusions were:

- **C++11** is a major step beyond C++98 because of move semantics, `std::atomic`, a standard memory model, `std::thread`, lambdas, `unique_ptr`, and better RAII patterns.
- **C++17** is a strong modern baseline because of guaranteed copy elision, `std::optional`, `std::variant`, `string_view`, `if constexpr`, stronger constexpr patterns, and better internal architecture support.
- **C++20/23/26** add powerful features, but were treated as too risky as project baselines for Windows 7/Mavericks-era compatibility and library/runtime constraints.

### 2.3 A staged old-to-modern plan: C89/C++98 first, C11/C++17 later

The user proposed a staged version policy: versions 0.x and 1.x would use **C89 for the engine and C++98 for the game**, while versions 2.x and later would use **C11 for the engine and C++17 for the game**. The assistant initially judged that wise for a project trying to preserve broad historical compiler reach early and then unlock modern concurrency and renderer/runtime capabilities later.

This was an important intermediate stage. It preserved the old dream of broad vintage portability while allowing a future modern track. The rationale was that C89/C++98 support maximum old-compiler reach and deterministic simplicity, while C11/C++17 unlock atomics, better memory/lifetime tools, and cleaner large-scale implementation.

### 2.4 Mixing and matching C and C++ standards

The user then asked whether engine and game standards could be mixed, such as a **C11 engine with a C++98 game**. The answer was yes, if the boundary is a pure C ABI and the stricter/modern memory/concurrency semantics do not leak across it. A C11 engine can own threads/atomics internally while presenting a single-threaded or externally synchronized C ABI to a C++98 game. The reverse direction, C89 engine plus C++17 game, was treated as riskier because modern game code might assume stronger threading/lifetime guarantees than the engine can actually provide.

The key rule from that phase was: language mixing is possible; semantic leakage is the danger. The ABI and threading contract matter more than file extension.

### 2.5 Reframing what should be C and what should be C++

The user then challenged whether the split was arbitrary and asked what truly needs C++. This produced one of the central doctrines of the chat: **C should define deterministic law and stable boundaries; C++ should implement machinery around that law**.

The assistant recommended:

- C for public ABI, deterministic kernel, fixed-point math, RNG, stable IDs, save/replay/wire formats, canonical hashing, renderer command IR, and low-level facades.
- C++ for app/runtime orchestration, resource ownership, platform/render backends, UI, tools, Workbench, job systems, and higher-level composition.

At this stage the assistant warned against making all “game” code C++ by default. Deterministic game law that affects save/replay/network lockstep should remain C-compatible or at least follow the same strict deterministic rules. C++ is useful, but not necessary for authoritative stepping, fixed-point math, canonical serialization, or stable packets.

### 2.6 Repo-aware language comparison

The user asked to look at the actual source repository `julesc013/dominium` and compare what would happen if the engine moved from C89 to C++98, C99, C11, C++11, C17, C++17, C23, C++23, C++26, or C++29. The assistant used repo evidence from GitHub in that earlier exchange. The repo was described as already more mixed than the C89/C++98 slogan: CMake was then pinned to C90/C++98, but the engine target pulled in C and C++ files from engine, game, runtime, platform, scheduler, ECS, SIMD/GPU, and renderer layers. The public ABI header used C89/C++98-visible POD/vtable conventions.

The answer concluded that moving the whole engine to C++98 would not be worthwhile, C99 would be the best small C upgrade for deterministic/data-heavy code, C11/C17 would be useful for private runtime/provider internals, and C++17 would be the best modern C++ implementation lane for providers/tools/apps. C23/C++23/C++26 were treated as experimental/future lanes rather than baselines.

### 2.7 Abandoning the old plan: C17 + C++17 mainline

The user then pasted an argument that if the target floor is narrowed to **Windows 7 SP1, Mac OS X 10.9.5 Mavericks, and Linux**, C17/C++17 becomes a plausible upper baseline. The user said: “Okay, let’s completely abandon the old plans... I think we should completely and entirely transition our entire project across the board to C17 and C++17.”

This was the clearest user-accepted pivot in the chat. The assistant affirmed it, with caveats: C++17 is not necessarily a hard OS upper limit; the actual constraints are runtime libraries, deployment target, standard-library features, toolchain support, and platform SDKs. Still, the policy became:

```text
Primary source baseline: C17 + C++17
Public ABI: C-compatible, POD-only, no C++ ABI leakage
C++17 library subset: restricted for macOS 10.9.5 compatibility
Vintage/retro lanes: archived, optional, not governing mainline
```

### 2.8 Future platform support and the “thin shell / modern module” idea

The user asked how future demand for Windows XP, Windows 98, Mac OS X 10.6, Mac OS 9.2, Android, iOS, PS5, Xbox, and Switch could be supported cleanly in one monorepo with C17/C++17 source. The user also floated the idea of compiling C17/C++17 into primitive binaries that could be loaded by period-correct thin apps.

The assistant corrected this sharply: there is no universal primitive native binary that can run everywhere. Native binaries are bound to CPU architecture, executable format, loader, ABI/calling convention, runtime libraries, kernel/API imports, and OS minimum versions. A C89 shell cannot magically load a C++17 module on Windows 95 or Mac OS 9 if the module’s binary format/imports/runtime are incompatible.

The clean model became:

- Full native C17/C++17 builds for modern mainline targets.
- Constrained native builds for some older targets if worth the cost.
- Contract projections for very old targets: replay viewers, snapshot clients, thin clients, generated subsets, or software-rendered museum clients.
- Console/mobile adapters behind private SDK interfaces.

The assistant also rejected bad platform-top-level folder names and reinforced the repo’s canonical roots. Platform specificity should live under runtime/platform profiles and contract matrices, not in new top-level `windows/`, `mac/`, `android/`, etc.

### 2.9 Dropping 32-bit support

The user asked whether to drop 32-bit support and refactor for 64-bit. The assistant recommended making mainline full-native builds **64-bit-first and probably 64-bit-only**, while keeping code 32/64-clean where cheap. The mainline should target x86_64 and arm64. Stable ABI, save, replay, network, and renderer IR must never depend on native pointer width. Legacy 32-bit targets can be constrained native or projection lanes.

The advantages identified were larger address space, simpler release matrix, better modern CPU/ABI baseline, fewer old-toolchain constraints, better fit for modern desktop/mobile/consoles, and fewer plugin/module incompatibilities. The main losses were old 32-bit machines, 32-bit Windows 7/XP/98, older 32-bit Mac/Linux/Android devices, and some pointer-size memory density.

### 2.10 “C17, C++17, 64-bit — what else?”

The user then asked what else should be locked in and whether the project could “eat our cake and have it too.” The assistant checked latest repo source. It found that the root CMake now sets C17/C++17 with extensions off, and the engine target does too. It also observed that `domino_engine` remains broad, pulling in engine, game, runtime, render, platform, UI, network, package, scheduler, ECS, and legacy kernel sources. That was treated as a convergence artifact, not final modular form.

The assistant recommended locking these additional baselines:

- 64-bit source-native x86_64/arm64.
- Little-endian mainline only.
- C-compatible, POD-only, versioned ABI.
- Fixed-width explicit data formats with no padding or pointer-sized serialized fields.
- Deterministic fixed-point simulation, stable IDs, canonical ordering.
- Provider/capability/refusal model.
- Null + software renderer baseline, GPU backends replaceable.
- CLI/headless always available; TUI/rendered/native shells capability layers.
- Legacy targets as constrained/projection/archive lanes.

The assistant also identified hard-to-change decisions: save/replay/network formats, ID widths/namespaces, endian policy, ABI style, allocator/ownership model, threading/commit model, renderer command IR, platform capability model, package/install roots, and repo roots.

### 2.11 The unified project identity and missing pieces

The user pasted a proposed unified future plan: Domino as substrate, Dominium as game/product family, Workbench as production/validation/editing/inspection environment, AIDE as repo/control-plane harness, contracts as law, tests/replay/evidence as proof. The assistant endorsed it but corrected the scope: Dominium should not become a vague everything-platform. Domino is the substrate; Dominium is the product family; Workbench operates; AIDE governs.

The assistant identified missing pillars:

1. **Composition resolver** — resolves app/profile/packs/modules/providers/platform/renderers/trust into selected providers/modules/packs/capabilities/refusals/lockfile/evidence.
2. **Lockfile model** — pack graph, module graph, provider selections, toolchain/platform profile, schema versions, content hashes, save/replay compatibility, Workbench workspace state.
3. **Compatibility corpus** — old saves, replays, packs, profiles, commands, diagnostics, provider descriptors, manifests.
4. **Security/trust model** — trust levels and permissions for packs, native modules, scripts, remote services, etc.
5. **Stable virtual filesystem/root model** — install/content/packs/profiles/saves/replays/exports/cache/logs/temp/tools roots.
6. **Performance budgets as contracts** — tick, replay, save/load, pack validation, renderer command, software renderer, memory, allocation, startup, and Workbench latency budgets.
7. **Public-surface promotion protocol** — no stable surface without contract, owner, version, compatibility rule, diagnostics, fixture, consumer test, and migration/refusal behavior.

The assistant also noted the current blocker: Foundation Lock is blocked because dependency-direction strict validation reports 358 violations and 38 warnings. Workbench validation slice should not proceed until `FOUNDATION-REPAIR-DEPENDENCY-DIRECTION-01` is completed.

### 2.12 C99 / C++11 / raylib / SDL2 challenge

The user later pasted another argument suggesting C99 or C++11 might be better because raylib and SDL2 are C APIs and C++17 may be risky for legacy OS targets. The assistant rejected a pivot to pure C99 or pure C++11.

Key corrections:

- C99 is not “universally supported” in MSVC in the clean way the pasted advice implied. MSVC historically defaulted to C89-ish mode with Microsoft extensions, and strict modern C modes arrive later.
- C11/C17 atomics/threads are not portable through MSVC C in the way the argument claimed; MSVC C11/C17 lacks conforming C atomics/threads.
- C++17 does not inherently break Windows 7 or Mavericks; the real risks are toolchain/runtime/library/deployment-target constraints.
- Raylib and SDL2 should be providers, not architectural identity. C++ can call C APIs directly with no binding penalty.

Final answer remained: C17 + C++17 is best for Dominium; C17 for law, C++17 for machinery, C ABI between worlds, providers for raylib/SDL2/platform/render/audio/input.

### 2.13 Preservation package generation

The user uploaded a large preservation prompt in `Pasted text.txt`, requiring a maximum-fidelity chat preservation report, structured registers, context transfer packet, spec sheet, aggregator packet, self-audit, file export, and ZIP package. The assistant produced the package with the following files:

- `__00_manifest.md`
- `__01_human_readable_report.md`
- `__02_context_transfer_packet.md`
- `__03_spec_sheet.yaml`
- `__04_registers.md`
- `__05_aggregator_packet.md`
- `__06_reader_brief.md`
- `__07_verification_and_audit.md`
- `__08_future_chat_bootstrap_prompt.md`
- `__09_in_chat_reader.md`
- `__handoff_package.zip`

This current task adds an accompanying detailed conversation report and a new complete bundle including all those files plus this report.

---

## 3. Decisions made and their rationale

### DECISION-01 — Use C17 + C++17 as the mainline

**Status:** Accepted user direction.  
**Why:** Once the target floor narrowed to Windows 7 SP1, macOS 10.9.5, and Linux, the old C89/C++98 plan imposed too much cost for too little mainline benefit. C17/C++17 gives stronger internal implementation tools while still allowing a C-compatible ABI and stable data contracts.

**Alternatives considered:** C89/C++98, staged C89/C++98 then C11/C++17, pure C99, pure C++11, C23/C++26.  
**Why alternatives were not adopted:** C89/C++98 became too restrictive; pure C99 lacks ergonomic large-system machinery; pure C++11 is unnecessarily conservative; very latest standards are too risky for legacy-compatible baselines.

### DECISION-02 — Full native mainline is 64-bit

**Status:** Accepted direction.  
**Why:** 64-bit simplifies memory, release matrices, modern platforms, tools, and future console/mobile fit. 32-bit remains useful as an optional audit/constrained/projection target but should not govern architecture.

**Caveat:** Stable data formats must not depend on pointer width. 64-bit process model does not mean 64-bit everything. Domain handles can remain compact fixed-width integers where appropriate.

### DECISION-03 — Mainline is little-endian

**Status:** Accepted direction.  
**Why:** The repo determinism doctrine already assumes little-endian runtime targets and explicit little-endian encodings. Supporting big-endian would introduce serialization, hashing, replay, asset, and test complexity without an identified target.

### DECISION-04 — Public ABI remains C-compatible

**Status:** Accepted direction.  
**Why:** C-compatible ABI enables bindings, plugin/provider boundaries, stable public surfaces, older projections, and tool reuse. C++ ABI is compiler/toolchain/platform-fragile.

**Concrete bans at stable boundaries:** C++ classes, STL containers, templates, exceptions, RTTI, allocator ownership, raw native layout, raw pointers in serialized data, `size_t`/`uintptr_t` in save/replay/network formats.

### DECISION-05 — C17 law, C++17 machinery

**Status:** Accepted architectural doctrine.  
**Why:** It allows the deterministic, auditable, serializable substrate to remain boring and stable while using C++17’s RAII, move semantics, `optional`/`variant`, templates, and stronger type modelling for complex runtime and app code.

### DECISION-06 — Raylib/SDL2 are providers, not identity

**Status:** Accepted direction.  
**Why:** Raylib/SDL2 being C APIs does not require pure C. Dominium can call them through provider facades while preserving a higher-level C++17 runtime/app architecture.

### DECISION-07 — No universal primitive binary

**Status:** Accepted correction.  
**Why:** Native binaries are constrained by CPU ISA, ABI, object format, loader, runtime, and OS imports. Legacy platforms need projections or constrained builds, not magical dynamic loading of modern modules.

### DECISION-08 — Foundation Lock is currently blocked

**Status:** Current project fact from latest task packet.  
**Why:** Dependency-direction strict validation reports 358 violations and 38 warnings. Product/Workbench work should not proceed until this is repaired.

### DECISION-09 — Workbench is not authority

**Status:** Accepted doctrine.  
**Why:** Workbench should operate through registered commands/services/results/refusals/evidence. It should not bypass validators or private tools.

### DECISION-10 — Composition resolver and lockfiles are missing central pieces

**Status:** Assistant recommendation; not yet implemented.  
**Why:** True modularity requires deterministic composition of apps, profiles, packs, modules, providers, capabilities, trust, and evidence. Lockfiles make composition reproducible.

---

## 4. What was put off for later

The chat deliberately deferred several categories of work:

1. **Legacy native ports** such as Windows 98, Mac OS 9.2, Mac OS X 10.6, Windows XP, old Linux, or 32-bit Android. These are not abandoned, but they are not mainline. They belong in constrained native, contract projection, or archive runner lanes.

2. **C23/C++20/C++23/C++26 baselines.** These may be useful for modern-only tools/providers later, but they are not suitable as the mainline baseline for the chosen legacy-compatible floor.

3. **Native plugin/module loader.** The chat repeatedly warned that native code extension requires trust/permission/refusal law first. Do not build native plugins before security/trust policy.

4. **Workbench UI and product features.** Workbench is important, but it is not authorized until Foundation Lock is green. The first Workbench slice should validate one artifact through the command/service/result/refusal/evidence spine, not build a full UI.

5. **Renderer expansion.** Null and software renderer baselines are sufficient for correctness. D3D11, Metal, Vulkan, GL, raylib, SDL2, etc. are providers to add behind contracts and conformance tests.

6. **Full release/public support claims.** The component/support matrix remains a planning/evidence tool. Stub/planned/research rows are not support claims.

7. **Full CTest / full gate debt.** The latest task packet says full CTest was not run and remains full-gate debt.

8. **Exact platform/toolchain verification.** Windows 7, macOS 10.9.5, Linux glibc, MSVC, Xcode, SDL2/raylib, and standard-library deployment facts need current verification before formal release commitments.

---

## 5. Integration model preserved from the chat

The final integration model is:

```text
contracts define what exists
content provides authored data
packs distribute authored payloads
modules declare functional extension units
providers implement runtime capabilities
services expose callable behavior
commands invoke services consistently
apps compose commands, modules, providers, and packs
Workbench presents and edits the system
AIDE validates and governs the repo
tests prove behavior
artifacts preserve results
```

A more operational version:

```text
Content / Packs / Profiles
        ↓
Composition Resolver
        ↓
Capability + Trust + Version Negotiation
        ↓
Commands
        ↓
Services
        ↓
Providers
        ↓
Artifacts / Views / Diagnostics / Evidence
        ↓
CLI / TUI / Rendered Client / Native Shell / Workbench / AIDE
```

This model matters because it keeps implementation replaceable. A module is not a DLL, not a folder, and not necessarily native code. A module is a declared functional extension unit. A provider is a replaceable implementation. A pack is distributable authored payload. An app composes modules, providers, services, and packs. A workspace is a Workbench composition. An artifact is a persisted versioned thing such as save, replay, pack, bundle, diagnostic, or release.

---

## 6. Major risks and failure modes

### Risk 1 — Treating assistant recommendations as final user decisions

Some items were clearly accepted by the user, especially the pivot to C17/C++17 and later 64-bit. Other items, such as exact names for lockfiles or composition resolver folder names, were assistant recommendations. Future aggregation should label these correctly.

### Risk 2 — Overcorrecting into pure C99 or C++11

The final chat explicitly rejected a pivot to pure C99 or pure C++11. Those options may be reasonable for smaller projects, but not for Dominium’s scale and goals.

### Risk 3 — C++17 ABI leakage

C++17 is beneficial internally but dangerous at stable boundaries. Future implementation must audit against STL/classes/templates/exceptions/RTTI/allocator ownership leaking into ABI or serialized formats.

### Risk 4 — Letting Workbench bypass architecture

Workbench must use command/service/result/refusal/evidence paths. If it directly invokes private validators or runtime internals, it will become a second authority and undermine the contract model.

### Risk 5 — False platform support claims

Support tiers, stubs, research rows, and planned backends must not be presented as real support without toolchain, preset, smoke-test, package, and release evidence.

### Risk 6 — Not repairing dependency direction first

The latest task packet states Foundation Lock is blocked. Starting product work before repairing dependency-direction violations risks building on a structurally invalid graph.

### Risk 7 — Treating raylib/SDL2 as the architecture

Raylib/SDL2 can be useful providers, but they should not determine Dominium’s internal architecture, ABI, or data contracts.

### Risk 8 — Stale platform/toolchain facts

External facts about MSVC, Windows 7, Xcode, macOS deployment, C++ library availability, Linux glibc, SDL2, and raylib can change or have nuance. They need verification before formal release policy.

---

## 7. Recommended next-action sequence

1. **Run `FOUNDATION-REPAIR-DEPENDENCY-DIRECTION-01`.**  
   Classify the 358 dependency-direction violations and 38 warnings. Repair real boundary leaks. Add narrow fixture/archive/generated exceptions only where justified. Do not weaken dependency law broadly.

2. **Rerun Foundation Closeout.**  
   Confirm dependency-direction strict is green. Confirm fast strict remains green. Record honest closeout evidence.

3. **Update doctrine/docs for C17/C++17.**  
   Replace stale wording such as “C89/C++98 visible” with “C-compatible ABI.” Update determinism language from “C89/C90 compilation” to the new C17 source baseline while preserving fixed-width/little-endian/no-float/no-pointer-identity rules.

4. **Add architecture/platform contracts.**  
   Define source-native 64-bit, constrained native, contract projection, archive runner. Add x86_64/arm64, little-endian, no serialized pointer-sized fields.

5. **Design the smallest composition resolver slice.**  
   It should resolve one app/profile/pack/provider set and produce capability selection, refusals/degradations, lockfile, and evidence.

6. **Define lockfiles.**  
   Start with profile/pack/provider/toolchain lockfiles. Keep them deterministic, explicit, and auditable.

7. **Define trust/permission model before native plugins.**  
   Native modules should be a high-trust extension type, not the default modding mechanism.

8. **Implement `WORKBENCH-VALIDATION-SLICE-01` only after Foundation Lock.**  
   The slice should validate one pack/profile/content artifact through a registered command, with same result shown in CLI and Workbench, same diagnostics/refusals, and an evidence packet.

9. **Create performance budget contracts.**  
   Track tick, replay, load/save, pack validation, renderer command, software renderer, allocations, memory, startup, and Workbench command latency.

10. **Verify external platform/toolchain facts.**  
   Treat Windows 7, macOS 10.9.5, Linux, C++17 library subset, SDL2/raylib, MSVC, and Xcode claims as verification queue items.

---

## 8. What to preserve for future chats

Preserve these exact ideas:

- **C17 + C++17 is the accepted mainline direction.**
- **C17 owns law; C++17 owns machinery.**
- **Full native products are 64-bit, little-endian, x86_64/arm64.**
- **Public ABI is C-compatible, POD-only, versioned, and no C++ ABI leaks.**
- **Determinism law outranks language preference.**
- **Legacy systems consume constrained builds or projections, not mainline constraints.**
- **Raylib/SDL2 are providers, not architectural identity.**
- **Workbench is not authority; it must use command/service/result/refusal/evidence spine.**
- **Composition resolver and lockfiles are missing central pieces.**
- **Foundation Lock is blocked until dependency-direction strict validation is repaired.**
- **Do not build product features or Workbench UI before Foundation Lock is green.**
- **Do not treat all assistant suggestions as user decisions.**

---

## 9. Verification queue

These items require external/current verification before becoming formal release policy:

1. Windows 7 SP1 targeting status for selected MSVC/Windows SDK/toolset.
2. Whether the project should pin VS 2022/v143 or another exact Windows toolchain.
3. macOS 10.9.5 deployment viability for chosen Xcode/Clang/libc++ combination.
4. C++17 library feature subset safe for macOS 10.9.5.
5. Linux glibc/musl baseline and packaging policy.
6. SDL2 support status for chosen desktop/mobile/legacy targets.
7. Raylib support status for chosen desktop/mobile/legacy targets.
8. Android NDK C++17/64-bit policy for selected API floor.
9. iOS native C++17/static-library policy for selected deployment target.
10. Console SDK language/runtime constraints for PS5/Xbox/Switch under licensed access.
11. Repo current state after future commits: CMake, component matrix, support tiers, dependency-direction output, Foundation Lock status.

---

## 10. Package check performed for this companion report

The following previously generated files were present in `/mnt/data` before this new bundle was created:

- `Dominium_Language_Platform_Architecture_Baseline__00_manifest.md`
- `Dominium_Language_Platform_Architecture_Baseline__01_human_readable_report.md`
- `Dominium_Language_Platform_Architecture_Baseline__02_context_transfer_packet.md`
- `Dominium_Language_Platform_Architecture_Baseline__03_spec_sheet.yaml`
- `Dominium_Language_Platform_Architecture_Baseline__04_registers.md`
- `Dominium_Language_Platform_Architecture_Baseline__05_aggregator_packet.md`
- `Dominium_Language_Platform_Architecture_Baseline__06_reader_brief.md`
- `Dominium_Language_Platform_Architecture_Baseline__07_verification_and_audit.md`
- `Dominium_Language_Platform_Architecture_Baseline__08_future_chat_bootstrap_prompt.md`
- `Dominium_Language_Platform_Architecture_Baseline__09_in_chat_reader.md`
- `Dominium_Language_Platform_Architecture_Baseline__handoff_package.zip`
- `Pasted text.txt`

This task added:

- `Dominium_Language_Platform_Architecture_Baseline__10_accompanying_detailed_conversation_report.md`
- `Dominium_Language_Platform_Architecture_Baseline__11_complete_bundle_manifest.md`
- `Dominium_Language_Platform_Architecture_Baseline__complete_conversation_package.zip`

---

## 11. Final compact conclusion

This conversation’s final state is not “use C++ because it is modern” or “use C because SDL2/raylib are C.” The final state is a more durable architecture:

```text
Dominium mainline: C17 + C++17 + 64-bit + little-endian.
C17 defines law and stable data.
C++17 implements complex machinery.
C-compatible ABI protects long-term portability.
Contracts define identity.
Providers implement capability.
Packs and modules compose through descriptors.
Workbench operates; AIDE governs.
Tests, replay, and evidence prove.
Legacy targets are projections or constrained builds.
Foundation dependency direction must be repaired before product work.
```

The most important next action is still:

```text
FOUNDATION-REPAIR-DEPENDENCY-DIRECTION-01
```
