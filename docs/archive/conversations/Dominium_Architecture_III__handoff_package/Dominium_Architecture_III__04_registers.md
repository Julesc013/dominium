# Registers — Dominium Architecture III

## 1. Workstream Register

| ID | Project / workstream | Objective | Current state | Desired end state | Future relevance | Priority | Confidence | Label |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| WORKSTREAM-01 | Deterministic Dominium core and repository contract | Preserve the deterministic fixed-step simulation model and repo layering while launcher/platform/render work proceeds. | Project contract was explicitly supplied by the user in the chat: C89/C++98-era constraints, deterministic tick model, strict directories, no floats in core/sim, stable serialization. | All new launcher/render/platform/input code obeys deterministic and layering rules. | active | P0 | High | FACT |
| WORKSTREAM-02 | System-agnostic launcher architecture | Design the launcher as portable, modular, extensible C89 core logic plus thin frontends. | Architecture designed conceptually; implementation is not confirmed. | A C89 launch core/model/config/capability/launch-plan layer, platform process adapters, and multiple frontend skins over a shared view model. | active | P0 | High | FACT |
| WORKSTREAM-03 | Launcher backend/frontend language split | Keep backend launcher logic C89 and allow frontend code for each binary to use C++98. | Explicit user decision. | C89 backend compiles independently of OS/UI; C++98 max frontends handle platform-specific shells. | active | P0 | High | FACT |
| WORKSTREAM-04 | Launcher-to-client/server process execution | Launcher settings resolve to external client/server binary execution. | Explicit user decision. | A DomLaunchPlan-like structure resolves role, account, instance, platform, renderer, headless mode, executable, args, environment, and working directory. | active | P0 | High | FACT |
| WORKSTREAM-05 | Unified user-facing entrypoint scripts | Provide scripts/commands for dominium, setup, dom-client, and dom-server. | Script templates and CMake configure/install plans were generated, but implementation is unverified. | Consistent commands across OSes dispatch to correct launcher/setup/client/server binaries. | active | P0 | High | FACT |
| WORKSTREAM-06 | Setup / installer / repair / uninstaller wrapper | Implement setup entrypoint for install, repair, and uninstall modes. | Script behavior was specified; real setup binaries may not exist yet. | setup [install\|repair\|uninstall] calls dom_setup-* with --mode=<mode>. | active | P1 | High | FACT |
| WORKSTREAM-07 | Platform backend taxonomy and capability model | Normalize platform backend categories and encode allowed/conditional combinations. | Latest user categories are POSIX, SDL1, SDL2, Native. Earlier chat also discussed win32, macosx, X11, Wayland, and POSIX headless. | A single documented platform taxonomy used by CMake, launcher capabilities, scripts, and docs. | active | P0 | Medium | FACT / UNCERTAIN |
| WORKSTREAM-08 | Renderer backend taxonomy and capability model | Normalize render backends and expose vector/full graphics capability across all. | Latest user renderer list is DX9.0c, DX11, GL1.1, GL2, VK1, software. DX12 appeared earlier but was omitted later. | Renderer enum/docs/CMake/scripts use the final list and mark DX12 as deferred/unconfirmed unless the user confirms it. | active | P0 | Medium | FACT / UNCERTAIN |
| WORKSTREAM-09 | Universal all-platform software renderer | Replace vector_soft with one software renderer capable of vector and textured graphics on all platforms. | User-finalized design goal; implementation unverified. | engine/render/software supports vector-only mode, full graphics mode, textured primitives, missing-texture placeholders, and platform present callbacks. | active | P0 | High | FACT |
| WORKSTREAM-10 | Vector/full graphics render modes | Every renderer supports vector-only and graphics modes. | Design accepted; not confirmed implemented. | Runtime view/render mode can switch between CAD/vector and full textured graphics without backend replacement. | active | P0 | High | FACT |
| WORKSTREAM-11 | Instant zoom and 2D/3D view switching | Support seamless zoom at any scale and instant switching between top-down 2D and first-person 3D, each in vector or graphics. | Architecture designed conceptually; implementation unverified. | View type and mode are runtime view state; command generation changes without renderer reinitialization. | active | P1 | High | FACT |
| WORKSTREAM-12 | Arbitrary cameras, multi-view, overlays, and offscreen targets | Support free cam, maps, HUD cameras, CCTV, content creation cameras, overlays, windows, and offscreen views. | Architecture proposed with camera/view/target registries. | Render core supports arbitrary camera IDs, view IDs, target IDs, and per-frame view instances. | active | P1 | High | FACT |
| WORKSTREAM-13 | Launcher UI tabs and bottom selectors | Define launcher UI structure. | User specified UI; uploaded code may differ. | Tabs: News, Changes, Mods, Instances, Accounts, Settings. Bottom: Account, Instance, Platform, Renderer, Graphical/Headless, Client/Server. | active | P1 | High | FACT |
| WORKSTREAM-14 | Input and keybinding specification | Document and implement canonical F1–F12 and core controls. | F-key map and Codex prompt generated; implementation unverified. | docs/SPEC_INPUT.md, default_bindings.json, action enum, and mapping layer consistent with launcher/game contexts. | active | P1 | High | FACT |
| WORKSTREAM-15 | Platform support tiers | Formalize Tier 1/2/3 OS support ranges. | User finalized tier ranges. | Docs, build tooling, and capability matrix reflect final support tiers, with feasibility verified. | active | P0 | High for user decision; Medium for feasibility | FACT |
| WORKSTREAM-16 | Capability matrix | Map supported and conditional platform/renderer combinations per OS/tier. | Draft matrix generated; external facts and taxonomy require verification. | Launcher filters invalid choices through static support matrix plus runtime probes. | active | P0 | Medium | FACT / UNCERTAIN |
| WORKSTREAM-17 | Launcher build/test flow | Build and test launcher binaries and scripts. | Build/test plan and Codex prompt generated. | CMake targets, scripts, setup stubs, direct/script smoke tests, spawn dry-run tests. | active | P1 | High | FACT |
| WORKSTREAM-18 | Uploaded launcher code refactor | Reconcile uploaded launcher code with intended architecture. | Files uploaded; prior assistant summary says native Win32 launcher and engine-rendered view are mixed; exact contents unverified. | Engine-based launcher canonical, Win32 native launcher as separate frontend/tool if retained. | active | P0 | Medium | FACT / UNCERTAIN |
| WORKSTREAM-19 | Documentation and Codex implementation prompts | Generate prompts and docs updates for implementation. | Multiple prompts generated, but not confirmed applied. | Use consolidated final decisions to update docs/code, not stale prompt fragments. | historical/active artifact | P1 | High | FACT |
| WORKSTREAM-20 | Chat handoff and report packaging | Produce downloadable per-chat report package for future aggregation. | This file package is being created from prior CTP and visible chat. | Markdown/YAML/ZIP package preserving state with labels and stable IDs. | active | P0 | High | FACT |

## 2. Decision Register

| ID | Decision | Status | Source / evidence cue | Rationale | Implications | Related project | Confidence | Label |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| DECISION-01 | Dominium deterministic core and layering contract remains binding. | final | User supplied project identity and docs summary. | Preserve deterministic sim and architecture. | All code/docs must obey no-floats core/sim, C89/C++98 limits, and layering. | WORKSTREAM-01 | High | FACT |
| DECISION-02 | Launcher settings execute separate client/server binaries. | final | User: settings selected in launcher will execute client or server binaries. | Simplifies platform/render/client/server separation. | Requires launch plan and spawn API. | WORKSTREAM-04 | High | FACT |
| DECISION-03 | Launcher backend/core must use C89. | final | User explicit statement. | Portability and legacy support. | Launcher core cannot rely on C++. | WORKSTREAM-03 | High | FACT |
| DECISION-04 | Launcher frontends may use C++98. | final | User explicit statement. | Permits system-specific UI shell code while staying inside project era constraints. | Frontend code should not exceed C++98. | WORKSTREAM-03 | High | FACT |
| DECISION-05 | Client/server binaries can be single-system builds. | final | User explicit statement. | Avoids universal binary complexity. | Launcher/scripts choose correct binary. | WORKSTREAM-04, WORKSTREAM-05 | High | FACT |
| DECISION-06 | Use unified entrypoints for launcher/client/server/setup. | final | User requested scripts. | Consistent UX across OSes. | Packaging scripts needed. | WORKSTREAM-05 | High | FACT |
| DECISION-07 | Use dominium as the main launcher command. | final | User requested “dominium” to launch launcher. | Product-facing command name. | dom-launcher becomes optional alias only. | WORKSTREAM-05 | High | FACT |
| DECISION-08 | Use setup as installer/repair/uninstaller command. | final | User requested “setup”. | Simple lifecycle command. | setup dispatches install/repair/uninstall. | WORKSTREAM-06 | High | FACT |
| DECISION-09 | Remove minimal/full backend split and use full single implementations. | final | User: remove minimal versions, use full single implementation. | Avoid duplicated backend code. | Launcher and game share platform/render implementations. | WORKSTREAM-07 | High | FACT |
| DECISION-10 | Replace vector_soft with a universal software renderer. | final | User explicitly requested software renderer instead of vector_soft. | One fallback renderer handles vector and textures. | Public backend is software, not vector_soft. | WORKSTREAM-09 | High | FACT |
| DECISION-11 | All renderers must support vector-only and graphics modes. | final | User explicit statement. | CAD, performance, and missing file fallback. | Every backend must implement or emulate both modes. | WORKSTREAM-10 | High | FACT |
| DECISION-12 | Software renderer must work on all platforms. | final | User explicit statement. | Universal fallback. | Renderer must be OS-independent with platform present callbacks. | WORKSTREAM-09 | High | FACT |
| DECISION-13 | Support instant seamless zoom to any scale. | final | User explicit request. | CAD-style viewing. | Camera transforms must be view-layer state. | WORKSTREAM-11 | High | FACT |
| DECISION-14 | Support instant switching between top-down 2D and first-person 3D. | final | User explicit request. | View flexibility. | View type/mode should not require renderer reinit. | WORKSTREAM-11 | High | FACT |
| DECISION-15 | Support arbitrary cameras for free cam, map, HUD, CCTV, content creation, windows, overlays. | final | User explicit request. | Extensible UI/game/tooling. | Need camera/view/target registries. | WORKSTREAM-12 | High | FACT |
| DECISION-16 | Use final Tier 1 support: Windows NT 2000 SP4-latest, Mac OS X 10.6-10.14, Linux 3.2-current. | final | User final tier list. | Main support target. | Docs and matrix must include. | WORKSTREAM-15 | High | FACT |
| DECISION-17 | Use final Tier 2 support: Win98SE-Me, NT 2000 SP4-latest, Mac OS 9-9.2, Mac OS X 10.6-15.0, Linux 2.6.18-current. | final | User final tier list. | Extended legacy support. | Docs and matrix must include. | WORKSTREAM-15 | High | FACT |
| DECISION-18 | Use final Tier 3 support: MS-DOS 3.3-6.2, Windows 3, Windows 95-Me, NT 2000 SP4-latest, Mac OS 8.5-9.2, Mac OS X 10.0-latest, Linux 2.4-current. | final | User final tier list. | Retro/heritage support. | Docs and matrix must include with feasibility caveats. | WORKSTREAM-15 | High | FACT |
| DECISION-19 | Latest renderer implementation set is DX9.0c, DX11, GL1.1, GL2, VK1, and software. | final latest / with caveat | User capability matrix request. | Defines current renderer scope. | DX12 must not be assumed final. | WORKSTREAM-08, WORKSTREAM-16 | Medium | FACT |
| DECISION-20 | Latest platform implementation categories are POSIX, SDL1, SDL2, and Native. | final latest / unresolved taxonomy | User capability matrix request. | Defines current platform scope. | X11/Wayland mapping must be resolved. | WORKSTREAM-07, WORKSTREAM-16 | Medium | FACT / UNCERTAIN |
| DECISION-21 | F1-F12 keybinding map is accepted enough to generate implementation prompt. | accepted plan | User asked for Codex prompt after keybinding proposal. | Stabilizes input semantics. | Implement SPEC_INPUT/default bindings unless revised. | WORKSTREAM-14 | Medium-High | FACT |
| DECISION-22 | Uploaded native Win32 launcher should likely become a separate frontend/tool, not the cross-platform core. | tentative | Assistant recommendation after uploaded files; user did not explicitly finalize. | Prevents Win32-only code from breaking non-Windows launcher builds. | Re-inspect files and confirm before refactor. | WORKSTREAM-18 | Medium | INFERENCE |
| DECISION-23 | Setup binaries may be stubs initially if real installer is absent. | tentative | Generated Codex prompt. | Allows scripts to test before real installer exists. | Must mark stubs clearly. | WORKSTREAM-06 | Medium | INFERENCE |
| DECISION-24 | DX12 is unresolved/deferred, not confirmed current scope. | unclear | Earlier assistant included DX12; latest user omitted it. | Avoid wrong scope. | Ask user or mark deferred. | WORKSTREAM-08 | High uncertainty | UNCERTAIN / UNVERIFIED |

## 3. Task Register

| ID | Task | Owner | Priority | Urgency | Dependencies | Inputs needed | Expected output | Recommended next step | Confidence | Label |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| TASK-01 | Inspect uploaded/repo files before implementation. | new assistant/developer | P0 | U0 | ARTIFACT-01, ARTIFACT-02, ARTIFACT-03, ARTIFACT-04, ARTIFACT-05 | Uploaded files/repo access | Verified current code state | Open launcher files and CMake; extract repo if possible. | High | FACT |
| TASK-02 | Resolve final platform taxonomy. | user/developer | P0 | U0 | WORKSTREAM-07 | Decision on POSIX/SDL/native/X11/Wayland | Canonical platform enum/model | Ask/decide whether X11/Wayland are Native subtypes or explicit. | Medium | UNCERTAIN / UNVERIFIED |
| TASK-03 | Resolve DX12 status. | user/developer | P0 | U0 | WORKSTREAM-08 | User confirmation | Renderer list finalized | Treat DX12 as deferred until confirmed. | Medium | UNCERTAIN / UNVERIFIED |
| TASK-04 | Update project docs with final launcher/platform/render/support/input decisions. | Codex/developer | P0 | U1 | TASK-02, TASK-03 | This package and existing docs | Updated docs | Patch docs/DIRECTORY_CONTEXT.md, docs/BUILDING.md, SPEC_LAUNCHER, SPEC_PLATFORM_SUPPORT, SPEC_INPUT. | High | FACT |
| TASK-05 | Create docs/SPEC_PLATFORM_SUPPORT.md or equivalent. | Codex/developer | P0 | U1 | WORKSTREAM-15 | Final tier list | Support tier doc | Add Tier 1/2/3 table and caveats. | High | FACT |
| TASK-06 | Create/verify capability matrix data and docs. | Codex/developer | P0 | U1 | TASK-02, TASK-03, VERIFY-01 | Renderer/platform taxonomy and verified external facts | Static+runtime capability filtering | Encode matrix with Y/conditional/not supported. | Medium | FACT / UNCERTAIN |
| TASK-07 | Implement launcher C89 core types/config/caps/launch plan. | Codex/developer | P0 | U1 | TASK-01, TASK-02 | Existing launcher code and design | game/launcher/core/* | Add pure C89 core. | High | FACT |
| TASK-08 | Implement launcher state and viewmodel. | Codex/developer | P0 | U1 | TASK-07 | Core config/caps | game/launcher/ui/* | Add action handling and viewmodel. | High | FACT |
| TASK-09 | Implement platform process spawn API. | Codex/developer | P0 | U1 | TASK-07 | Launch plan and platform APIs | dom_platform_launch_spawn and adapters | Add Win32/POSIX/macOS implementations. | High | FACT |
| TASK-10 | Refactor launcher CMake and targets. | Codex/developer | P0 | U1 | TASK-01 | Current CMake | Separated targets | Ensure Win32 code not built on non-Windows. | High | FACT |
| TASK-11 | Create engine-based launcher main. | Codex/developer | P0 | U1 | TASK-01, TASK-08 | Engine platform/render APIs | dom_launcher_engine_main.c | Loop polls input, draws view, presents. | High | FACT |
| TASK-12 | Preserve native Win32 launcher as separate target if desired. | Codex/developer | P1 | U2 | TASK-01, TASK-10 | dom_launcher_main.c | dom_launcher-win32-native | Guard under WIN32 only. | Medium | INFERENCE |
| TASK-13 | Implement universal software renderer. | Codex/developer | P0 | U1 | WORKSTREAM-09 | Render API/draw commands | engine/render/software | Support vector/full and textures/placeholders. | High | FACT |
| TASK-14 | Implement shared draw command core. | Codex/developer | P0 | U1 | TASK-13 | Draw command format | engine/render/core/dom_draw_common | Normalize commands for all renderers. | High | FACT |
| TASK-15 | Add vector/full render mode to API and backends. | Codex/developer | P0 | U1 | TASK-13, TASK-14 | Render API | dom_render_mode support | Mode controls vector vs full graphics. | High | FACT |
| TASK-16 | Implement camera/view/target registries. | Codex/developer | P1 | U2 | TASK-14 | View/camera design | dom_camera/dom_view/dom_target | Enable arbitrary cameras and views. | High | FACT |
| TASK-17 | Add packaging scripts. | Codex/developer | P0 | U1 | TASK-02, TASK-03 | Binary naming | Script templates | Add dominium, setup, dom-client, dom-server. | High | FACT |
| TASK-18 | Add CMake configure/install rules for scripts. | Codex/developer | P0 | U1 | TASK-17 | CMake target names | Generated install scripts | Use configure_file/install(PROGRAMS). | High | FACT |
| TASK-19 | Add setup binaries or stubs. | Codex/developer | P1 | U2 | TASK-17 | Installer path decision | dom_setup-* | Stub if no installer exists. | Medium | FACT |
| TASK-20 | Add input spec/default bindings/action enum. | Codex/developer | P1 | U2 | WORKSTREAM-14 | Keybinding map | SPEC_INPUT/default_bindings/actions | Implement documented controls. | High | FACT |
| TASK-21 | Extend or create input mapping layer. | Codex/developer | P1 | U3 | TASK-20 | Existing input stack | Mapping layer | Avoid duplicate systems; extend existing if present. | Medium | FACT |
| TASK-22 | Verify Linux kernel/libc/toolchain/distro claims. | developer/research | P1 | U1 | WORKSTREAM-15 | External docs/tests | Verified support docs | Research before publishing. | High | UNCERTAIN / UNVERIFIED |
| TASK-23 | Verify DirectX/OpenGL/Vulkan/SDL/macOS/Mac OS support claims. | developer/research | P1 | U1 | WORKSTREAM-16 | External docs/tests | Accurate matrix | Research and test. | High | UNCERTAIN / UNVERIFIED |
| TASK-24 | Smoke-test launcher/scripts. | developer/tester | P0 | U2 | TASK-10, TASK-17, TASK-18 | Built targets | Test results | Run direct and via scripts; test setup/client/server wrappers. | High | FACT |
| TASK-25 | Create final per-chat package files and ZIP. | assistant | P0 | U0 | WORKSTREAM-20 | Prior CTP and visible chat | Markdown/YAML/ZIP package | This task. | High | FACT |

## 4. Constraint Register

| ID | Constraint | Type | Hard or soft | Source / evidence cue | Practical implication | What would violate it | Confidence | Label |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| CONSTRAINT-01 | /engine/core and /engine/sim are C89 only. | technical | hard | User project contract | No C++/C99 in deterministic core/sim. | Using newer language features there. | High | FACT |
| CONSTRAINT-02 | Other engine modules are C++98 max unless explicitly allowed. | technical | hard | User project contract | Avoid C++11+ APIs/features. | Using modern C++ in engine modules. | High | FACT |
| CONSTRAINT-03 | No floats in /engine/core or /engine/sim. | technical/determinism | hard | User project contract | Use integer/fixed point only in core sim. | Any float/double use in core/sim. | High | FACT |
| CONSTRAINT-04 | Fixed tick phase order must be preserved. | technical/determinism | hard | User project contract | Do not reorder INPUT→PRE-STATE→SIMULATION→NETWORKS→MERGE→POST-PROCESS→FINALIZE. | Changing order. | High | FACT |
| CONSTRAINT-05 | Sim is single-threaded deterministic; background threads cannot mutate sim. | technical/determinism | hard | User project contract | Keep async work non-sim or mediated deterministically. | Threaded sim mutation. | High | FACT |
| CONSTRAINT-06 | Renderer/audio/UI never mutate sim state. | technical/layering | hard | User project contract | Render/audio/UI consume state/commands only. | Render-side sim writes. | High | FACT |
| CONSTRAINT-07 | OS headers only in appropriate platform/render/audio boundaries. | technical/layering | hard | User project contract | Launcher core must be OS-free. | Including windows.h in core/model. | High | FACT |
| CONSTRAINT-08 | CMake uses explicit sources and no network fetch. | technical/build | hard | User project contract | No globbing or configure/build downloads. | Network dependency fetch. | High | FACT |
| CONSTRAINT-09 | Launcher backend/core must be C89. | technical | hard | User decision | Write launcher core in C89. | Using C++ in launcher core. | High | FACT |
| CONSTRAINT-10 | Launcher frontends may use C++98, not newer by default. | technical | hard | User decision | Frontend code can be C++98 max. | C++11+ frontend code without approval. | High | FACT |
| CONSTRAINT-11 | Launcher launches separate binaries. | architecture | hard | User decision | Implement spawn plan/API. | In-process client/server switch. | High | FACT |
| CONSTRAINT-12 | Client/server binaries may be single-system. | architecture | hard | User decision | Do not require universal binary. | Assuming one client supports all systems. | High | FACT |
| CONSTRAINT-13 | Software renderer must work on all platforms. | technical | hard | User decision | Universal fallback renderer. | Platform-specific software renderer dependency. | High | FACT |
| CONSTRAINT-14 | Every renderer supports vector and graphics modes. | technical | hard | User decision | Mode must be runtime-capable. | Backend only supports textured path. | High | FACT |
| CONSTRAINT-15 | Every platform should be capable of renderer or headless. | technical | hard | User decision | Platform init must support no-window/headless. | Headless server opening a window. | High | FACT |
| CONSTRAINT-16 | Final OS support tiers must be preserved. | product | hard | User final tier list | Docs/matrix use user-specified ranges. | Dropping tier without user decision. | High | FACT |
| CONSTRAINT-17 | Direct user statements outrank assistant suggestions. | handoff/evidence | hard | User current request | Do not promote unaccepted suggestions. | Treating assistant idea as user decision. | High | FACT |
| CONSTRAINT-18 | External facts require verification before future use. | evidence | hard | User current request | Mark OS/library claims stale. | Publishing unverified compatibility. | High | FACT |
| CONSTRAINT-19 | Preserve rejected/superseded options and contradictions. | handoff | hard | User current request | Record changes of direction. | Repeating rejected designs. | High | FACT |
| CONSTRAINT-20 | Final package must be self-contained and downloadable if tools allow. | formatting | hard | User current request | Create files/ZIP and links. | Only inline summary when files can be made. | High | FACT |

## 5. User Preference Register

| ID | Preference | Area | Explicit or inferred | Strength | Implication for future assistant | Confidence | Label |
| --- | --- | --- | --- | --- | --- | --- | --- |
| PREF-01 | Concise but complete responses. | tone/length | explicit | strong | Avoid fluff but preserve actionable detail. | High | FACT |
| PREF-02 | Cite paths in coding/design work. | coding/evidence | explicit | strong | Use file paths and concrete repo locations. | High | FACT |
| PREF-03 | Propose concrete next steps. | planning | explicit | strong | End architecture with implementation steps when appropriate. | High | FACT |
| PREF-04 | Ask clarification only when blocking. | planning | explicit | strong | Proceed with best-effort when possible. | High | FACT |
| PREF-05 | Prefer Codex-ready prompts when asked. | coding workflow | explicit | strong | Generate complete implementation prompts. | High | FACT |
| PREF-06 | Design for system-agnostic portability and modular extensibility. | architecture | explicit | strong | Separate core from frontends/adapters. | High | FACT |
| PREF-07 | Preserve uncertainty labels in handoffs. | handoff | explicit | strong | Use FACT/INFERENCE/UNCERTAIN. | High | FACT |
| PREF-08 | Do not invent or silently infer. | reasoning | explicit | strong | Mark assumptions and unknowns. | High | FACT |
| PREF-09 | Preserve rejected and superseded options. | handoff | explicit | strong | Keep history and rationale. | High | FACT |
| PREF-10 | Use tables for support/capability matrices. | formatting | explicit | strong | Matrix-style docs are preferred. | High | FACT |
| PREF-11 | Produce downloadable/shareable files when asked. | artifact | explicit | strong | Create Markdown/YAML/ZIP package. | High | FACT |
| PREF-12 | Be rigorous and cite/fact-check where needed. | evidence | project-context visible profile | strong | Verify external platform claims. | Medium | PROJECT-CONTEXT |
| PREF-13 | Direct style, no unnecessary softening. | tone | project-context visible profile | strong | Avoid filler and over-explanation. | Medium | PROJECT-CONTEXT |

## 6. Open Questions Register

| ID | Open question / unresolved issue | Why it matters | What is known | What is unknown | What would resolve it | Priority | Confidence | Label |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| QUESTION-01 | Is DX12 in scope now, deferred, or dropped? | Affects renderer enum, CMake, scripts, docs. | DX12 was discussed earlier. Latest user list omitted DX12. | Final status. | Ask user or treat deferred. | P0 | Medium | UNCERTAIN / UNVERIFIED |
| QUESTION-02 | Are X11 and Wayland explicit platforms or Native Linux subtypes? | Affects platform taxonomy and matrix. | Earlier discussed explicitly; latest platform categories are POSIX/SDL1/SDL2/Native. | Final mapping. | User/developer taxonomy decision. | P0 | Medium | UNCERTAIN / UNVERIFIED |
| QUESTION-03 | Is POSIX headless-only? | Affects server/client capabilities. | POSIX used for headless in generated scripts. | Whether POSIX can render or only provide file/process/timers. | Platform API decision. | P0 | Medium | UNCERTAIN / UNVERIFIED |
| QUESTION-04 | What exactly is Native per OS/tier? | Needed for support matrix. | Native is final category. | Mapping to Win32/Win16/Cocoa/Carbon/X11/Wayland/DOS. | Document platform taxonomy. | P0 | Medium | UNCERTAIN / UNVERIFIED |
| QUESTION-05 | What is the actual current repo state? | Implementation must not assume prompts were applied. | Files were uploaded. | Exact contents and build state. | Inspect repo/files. | P0 | Medium | UNCERTAIN / UNVERIFIED |
| QUESTION-06 | Are prior uploaded-file summaries accurate? | Refactor path depends on them. | Prior assistant summarized them. | Exact code. | Reopen files. | P0 | Medium | UNCERTAIN / UNVERIFIED |
| QUESTION-07 | What libc/libstdc++ baselines accompany Linux kernel tiers? | Kernel ranges alone insufficient. | User finalized kernel versions. | libc/toolchain minima. | External verification and toolchain decision. | P1 | Medium | UNCERTAIN / UNVERIFIED |
| QUESTION-08 | Can SDL2 be supported on Win9x? | Tier 2/3 matrix. | Likely conditional at best. | Exact feasibility/shim. | Research/test. | P1 | Medium | UNCERTAIN / UNVERIFIED |
| QUESTION-09 | How feasible are Mac OS 8.5/9.x targets? | Tier 2/3 support. | User wants them. | Toolchains/API/render strategy. | Research/toolchain proof. | P1 | Medium | UNCERTAIN / UNVERIFIED |
| QUESTION-10 | How feasible is Mac OS X 10.0-latest support? | Tier 3. | User wants 10.0-latest. | Deployment/API split. | Research/test. | P1 | Medium | UNCERTAIN / UNVERIFIED |
| QUESTION-11 | How to support Windows NT 2000 SP4-latest with modern toolchains? | All tiers include NT 2000+. | User wants it. | CRT/toolchain/API split. | Research/test. | P1 | Medium | UNCERTAIN / UNVERIFIED |
| QUESTION-12 | Will retro systems run servers? | Binary matrix. | Servers discussed generally. | DOS/Win3/Mac classic server support. | Product decision. | P2 | Medium | UNCERTAIN / UNVERIFIED |
| QUESTION-13 | Is visual replay determinism required? | Render math choices. | Sim determinism required. | Visual determinism not established. | Product decision. | P2 | Medium | UNCERTAIN / UNVERIFIED |
| QUESTION-14 | What launcher config file format should be used? | Core implementation. | Config needed. | JSON/custom/TOML. | Design decision. | P1 | Medium | UNCERTAIN / UNVERIFIED |
| QUESTION-15 | Should dom-launcher/dom-setup remain aliases? | User-facing UX. | dominium/setup are final primary names. | Alias policy. | User/developer decision. | P2 | High | INFERENCE |
| QUESTION-16 | What installer technology should setup wrap? | Setup command. | Wrapper contract known. | Real installer backend. | Packaging decision. | P2 | Medium | UNCERTAIN / UNVERIFIED |

## 7. Artifact Ledger

| ID | Artifact / file / prompt / link / code / output | Type | Purpose | Current status | Must carry forward? | Location cue in chat | Confidence | Label |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| ARTIFACT-01 | /mnt/data/dominium.7z | file | Repo archive uploaded by user. | Uploaded; prior assistant said .7z could not be opened. | yes | User upload | Medium | FACT / UNCERTAIN |
| ARTIFACT-02 | /mnt/data/dom_launcher_view.c | file/code | Launcher engine-rendered view code. | Uploaded; content summary unverified. | yes | User upload | Medium | FACT / UNCERTAIN |
| ARTIFACT-03 | /mnt/data/dom_launcher_view.h | file/code | Header for launcher view. | Uploaded; content summary unverified. | yes | User upload | Medium | FACT / UNCERTAIN |
| ARTIFACT-04 | /mnt/data/CMakeLists.txt | file/code | Launcher build configuration. | Uploaded; content summary unverified. | yes | User upload | Medium | FACT / UNCERTAIN |
| ARTIFACT-05 | /mnt/data/dom_launcher_main.c | file/code | Native launcher implementation, reportedly Win32. | Uploaded; content summary unverified. | yes | User upload | Medium | FACT / UNCERTAIN |
| ARTIFACT-06 | docs/DIRECTORY_CONTEXT.md | reference doc | Canonical repo layout. | Referenced by user. | yes | User initial context | High | FACT |
| ARTIFACT-07 | docs/SPEC_CORE.md | reference doc | Deterministic core spec. | Referenced by user. | yes | User initial context | High | FACT |
| ARTIFACT-08 | docs/DATA_FORMATS.md | reference doc | Serialization/data formats. | Referenced by user. | yes | User initial context | High | FACT |
| ARTIFACT-09 | docs/BUILDING.md | reference doc | Build/language contract. | Referenced by user. | yes | User initial context | High | FACT |
| ARTIFACT-10 | docs/dev/dominium_new_root.txt | reference doc | Annotated tree/responsibilities. | Referenced by user. | yes | User initial context | High | FACT |
| ARTIFACT-11 | docs/SPEC_LAUNCHER.md | proposed doc | Launcher architecture spec. | Proposed, not confirmed created. | yes | Assistant prompt | High | FACT |
| ARTIFACT-12 | docs/SPEC_ENTRYPOINTS.md | proposed doc | Entrypoint/script semantics. | Proposed earlier; may be merged into launcher/build docs. | maybe | Assistant response | High | FACT |
| ARTIFACT-13 | docs/SPEC_INPUT.md | proposed doc | Input/keybinding spec. | Prompt generated. | yes | Assistant prompt | High | FACT |
| ARTIFACT-14 | docs/SPEC_PLATFORM_SUPPORT.md | proposed doc | Support tiers and capability matrix. | Proposed. | yes | Assistant response | High | FACT |
| ARTIFACT-15 | game/launcher/core/dom_launch_types.h | proposed code | Launcher core types. | Proposed. | yes | Assistant design | High | FACT |
| ARTIFACT-16 | game/launcher/core/dom_launch_config.{h,c} | proposed code | Accounts/instances/profiles config. | Proposed. | yes | Assistant design | High | FACT |
| ARTIFACT-17 | game/launcher/core/dom_launch_caps.{h,c} | proposed code | Capability data. | Proposed. | yes | Assistant design | High | FACT |
| ARTIFACT-18 | game/launcher/core/dom_launch_plan.{h,c} | proposed code | Launch plan builder. | Proposed. | yes | Assistant design | High | FACT |
| ARTIFACT-19 | game/launcher/ui/dom_launcher_state.{h,c} | proposed code | Launcher state/action handling. | Proposed. | yes | Assistant design | High | FACT |
| ARTIFACT-20 | game/launcher/ui/dom_launcher_viewmodel.{h,c} | proposed code | Frontend-neutral launcher viewmodel. | Proposed. | yes | Assistant design | High | FACT |
| ARTIFACT-21 | engine/platform/dom_platform_launch.h | proposed code | Platform-agnostic process spawn API. | Proposed. | yes | Assistant design | High | FACT |
| ARTIFACT-22 | engine/render/dom_render_api.h | proposed code | Render API, modes, caps. | Proposed. | yes | Assistant design | High | FACT |
| ARTIFACT-23 | engine/render/software/dom_render_software.{c,h} | proposed code | Universal software renderer. | Proposed. | yes | Assistant design | High | FACT |
| ARTIFACT-24 | engine/render/core/dom_draw_common.{h,c} | proposed code | Draw command format. | Proposed. | yes | Assistant design | High | FACT |
| ARTIFACT-25 | engine/render/core/dom_view.h/.c | proposed code | View/camera helpers. | Proposed. | yes | Assistant design | High | FACT |
| ARTIFACT-26 | engine/render/core/dom_camera.h / registry | proposed code | Arbitrary camera registry. | Proposed. | yes | Assistant design | High | FACT |
| ARTIFACT-27 | engine/render/core/dom_target.h/.c | proposed code | Render target/window/offscreen mapping. | Proposed. | yes | Assistant design | High | FACT |
| ARTIFACT-28 | game/client/input/default_bindings.json | proposed data | Default keybindings. | Prompt generated. | yes | Assistant prompt | High | FACT |
| ARTIFACT-29 | game/client/input/dom_input_actions.h | proposed code | Input action enum. | Prompt generated. | yes | Assistant prompt | High | FACT |
| ARTIFACT-30 | game/client/input/dom_input_mapping.{h,c} | proposed code | Input mapping layer. | Prompt generated. | yes | Assistant prompt | High | FACT |
| ARTIFACT-31 | packaging/scripts/dominium.sh.in and .cmd.in | proposed script | Launch launcher. | Template generated. | yes | Assistant prompt | High | FACT |
| ARTIFACT-32 | packaging/scripts/setup.sh.in and .cmd.in | proposed script | Setup wrapper. | Template generated. | yes | Assistant prompt | High | FACT |
| ARTIFACT-33 | packaging/scripts/dom-client.sh.in and .cmd.in | proposed script | Client dispatch wrapper. | Template generated. | yes | Assistant prompt | High | FACT |
| ARTIFACT-34 | packaging/scripts/dom-server.sh.in and .cmd.in | proposed script | Server dispatch wrapper. | Template generated. | yes | Assistant prompt | High | FACT |
| ARTIFACT-35 | Codex prompt: docs/platform/render/scripts implementation | prompt | Instruct Codex to update docs and implement architecture. | Generated. | yes | Assistant response | High | FACT |
| ARTIFACT-36 | Codex prompt: launcher build/test/scripts | prompt | Implement CMake targets/scripts/stubs. | Generated. | yes | Assistant response | High | FACT |
| ARTIFACT-37 | Codex prompt: input/keybindings | prompt | Implement input spec/default bindings. | Generated. | yes | Assistant response | High | FACT |
| ARTIFACT-38 | Codex prompt: uploaded launcher refactor | prompt | Refactor current launcher files. | Generated. | yes | Assistant response | Medium | FACT / UNCERTAIN |
| ARTIFACT-39 | F1-F12 keybinding table | table/output | Canonical input reference. | Generated. | yes | Assistant response | High | FACT |
| ARTIFACT-40 | Support tier table | table/output | OS support policy. | Generated from user final list. | yes | Assistant response/user list | High | FACT |
| ARTIFACT-41 | Capability matrix draft | table/output | Renderer/platform filtering. | Generated. | yes | Assistant response | Medium | FACT / UNCERTAIN |
| ARTIFACT-42 | OC-1 Discovery Inventory | handoff output | Inventory of chat state. | Generated. | yes | Assistant response | High | FACT |
| ARTIFACT-43 | Context Transfer Packet | handoff output | Maximum-fidelity state transfer. | Generated. | yes | Assistant response | High | FACT |
| ARTIFACT-44 | This report package | generated document package | Final per-chat downloadable package. | Created now. | yes | Assistant file generation | High | FACT |

## 8. Rejected / Superseded Options Register

| ID | Option | Status | Reason | Is rejection final? | When to reconsider | Confidence | Label |
| --- | --- | --- | --- | --- | --- | --- | --- |
| REJECTED-01 | In-process client/server switching from launcher. | rejected | User clarified launcher executes binaries. | final | Only reconsider if architecture changes. | High | FACT |
| REJECTED-02 | One universal all-system client/server binary. | deprioritised | User allowed single-system client/server binaries. | final for current plan | Reconsider if backend plugin architecture is desired. | High | FACT |
| REJECTED-03 | Minimal vs full backend split. | rejected | User said remove minimal versions and use full single implementation. | final | Reconsider only if legacy support requires special backend. | High | FACT |
| REJECTED-04 | Separate public vector_soft renderer. | superseded | User requested one software renderer. | final | Could survive only as internal implementation detail. | High | FACT |
| REJECTED-05 | Launcher requiring GPU renderer. | deprioritised | Launcher should use software fallback. | final | Optional future themed launcher only. | High | FACT |
| REJECTED-06 | Native Win32 launcher as cross-platform canonical launcher. | deprioritised | Win-only code cannot be cross-platform core. | tentative | Could be official Windows frontend if user chooses. | Medium | INFERENCE |
| REJECTED-07 | dom-launcher as primary command. | superseded | User later requested dominium. | likely final | Keep as alias if desired. | Medium | INFERENCE |
| REJECTED-08 | dom-setup as primary command. | superseded | User later requested setup. | likely final | Keep as alias if desired. | Medium | INFERENCE |
| REJECTED-09 | Linux kernel 2.0/libc5 baseline. | rejected/deprioritised | User chose Linux 2.4 for Tier 3. | final for current tiers | Special retro-port beyond Tier 3. | High | FACT |
| REJECTED-10 | Mac OS X 10.0 in Tier 1/2. | superseded | Final tiers place 10.0 only in Tier 3. | final | If user changes tiers. | High | FACT |
| REJECTED-11 | Treat generated Codex prompts as implemented. | rejected | No evidence of application. | final | Inspect repo to verify implementation. | High | FACT |
| REJECTED-12 | Treat external compatibility claims as verified. | rejected | User requires stale/current facts be marked for verification. | final | Verify with sources/tests. | High | FACT |
| REJECTED-13 | Assume prior assistant uploaded-file summaries are exact. | rejected | Files need reinspection. | final | Inspect files. | High | FACT |

## 9. Risk Register

| ID | Risk / failure mode | Consequence | Likelihood | Severity | Mitigation | Related project | Confidence | Label |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| RISK-01 | Treating brainstorms or assistant suggestions as final user decisions. | Wrong implementation/spec. | medium | high | Prioritize latest direct user statements. | WORKSTREAM-20 | High | FACT |
| RISK-02 | Resurrecting vector_soft as public renderer. | Violates user decision and fragments fallback path. | medium | high | Use software renderer with vector/full modes. | WORKSTREAM-09 | High | FACT |
| RISK-03 | Including DX12 without confirmation. | Scope and docs mismatch. | medium | medium | Mark DX12 unresolved/deferred. | WORKSTREAM-08 | Medium | UNCERTAIN / UNVERIFIED |
| RISK-04 | Ignoring X11/Wayland taxonomy ambiguity. | Invalid platform model. | medium | high | Resolve Native/POSIX mapping. | WORKSTREAM-07 | Medium | UNCERTAIN / UNVERIFIED |
| RISK-05 | Assuming uploaded file summaries are accurate. | Bad refactor. | medium | high | Inspect actual files. | WORKSTREAM-18 | Medium | UNCERTAIN / UNVERIFIED |
| RISK-06 | Assuming generated prompts were applied. | Duplicate/conflicting work. | medium | high | Inspect repo state. | WORKSTREAM-19 | High | FACT |
| RISK-07 | Compiling Win32 native launcher on non-Windows. | Build failure. | medium | high | Separate source lists/targets. | WORKSTREAM-18 | High | FACT |
| RISK-08 | Leaking OS APIs into launcher core. | Portability break. | medium | high | Keep core C89/OS-free. | WORKSTREAM-02 | High | FACT |
| RISK-09 | Camera/view/render state mutating sim. | Determinism violation. | low | critical | Keep view state client/render-side. | WORKSTREAM-11, WORKSTREAM-12 | High | FACT |
| RISK-10 | Software renderer delayed. | Launcher/fallback blocked. | medium | high | Prioritize software renderer. | WORKSTREAM-09 | High | FACT |
| RISK-11 | Capability matrix overpromises support. | User launches unsupported backends. | medium | high | Mark conditional and verify. | WORKSTREAM-16 | Medium | UNCERTAIN / UNVERIFIED |
| RISK-12 | Tier 3 consumes disproportionate effort. | Schedule/resource drag. | medium | medium | Treat as separate retro toolchain track. | WORKSTREAM-15 | High | INFERENCE |
| RISK-13 | Scripts fail on old shells/CMD. | Entrypoints unusable. | medium | medium | Test per tier and simplify scripts. | WORKSTREAM-05 | Medium | UNCERTAIN / UNVERIFIED |
| RISK-14 | Quick load/save semantics in multiplayer cause desync. | Authority/desync issue. | low | high | Disable or route through server/admin. | WORKSTREAM-14 | High | FACT |
| RISK-15 | Docs diverge from code. | Future confusion. | medium | high | Update docs and code together. | WORKSTREAM-19 | High | FACT |
| RISK-16 | Over-compressing handoff loses rejected options. | Future assistant repeats old work. | medium | medium | Use registers and stable IDs. | WORKSTREAM-20 | High | FACT |
| RISK-17 | External platform/library facts stale. | Incorrect support promises. | high | high | Verify before publication. | WORKSTREAM-15, WORKSTREAM-16 | High | FACT |
| RISK-18 | Using hidden reasoning rather than visible rationale in handoff. | Unusable/unsafe provenance. | low | medium | Only include visible rationale. | WORKSTREAM-20 | High | FACT |

## 10. Verification Queue

| ID | Item requiring verification | Why stale or uncertain | What source/type should verify it | Priority | Related project | Label |
| --- | --- | --- | --- | --- | --- | --- |
| VERIFY-01 | Linux kernel 3.2 + modern toolchain/glibc baseline. | Kernel-only support claim may be insufficient. | Linux distro/toolchain docs and build tests. | High | WORKSTREAM-15 | UNCERTAIN / UNVERIFIED |
| VERIFY-02 | Linux kernel 2.6.18 + libc/toolchain feasibility. | Tier 2 support depends on old ABI. | RHEL5/Debian/Ubuntu docs and test builds. | High | WORKSTREAM-15 | UNCERTAIN / UNVERIFIED |
| VERIFY-03 | Linux kernel 2.4 feasibility. | Tier 3 very old. | Toolchain, libc, X11, SDL1 docs/tests. | High | WORKSTREAM-15 | UNCERTAIN / UNVERIFIED |
| VERIFY-04 | Distro mappings for Tier 1. | Assistant-proposed distro mappings may be stale. | Distro release/kernel/glibc records. | Medium | WORKSTREAM-15 | UNCERTAIN / UNVERIFIED |
| VERIFY-05 | Distro mappings for Tier 2. | Assistant-proposed distro mappings may be stale. | Distro release/kernel/glibc records. | Medium | WORKSTREAM-15 | UNCERTAIN / UNVERIFIED |
| VERIFY-06 | Distro mappings for Tier 3. | Very old distro data uncertain. | Distro archives/docs. | Medium | WORKSTREAM-15 | UNCERTAIN / UNVERIFIED |
| VERIFY-07 | DX9.0c support on Windows 98SE-Me and NT 2000+. | Renderer matrix depends on API/runtime reality. | Microsoft DirectX docs/tests. | High | WORKSTREAM-16 | UNCERTAIN / UNVERIFIED |
| VERIFY-08 | DX11 OS/runtime minimum. | Must not expose on unsupported NT 2000/XP systems. | Microsoft DirectX docs/tests. | High | WORKSTREAM-16 | UNCERTAIN / UNVERIFIED |
| VERIFY-09 | Vulkan VK1 availability on Windows/Linux/macOS. | Runtime driver/API support varies. | Vulkan loader/driver/MoltenVK docs/tests. | High | WORKSTREAM-16 | UNCERTAIN / UNVERIFIED |
| VERIFY-10 | MoltenVK support across macOS tiers. | macOS VK1 depends on translation layer. | MoltenVK docs/license/deployment tests. | High | WORKSTREAM-16 | UNCERTAIN / UNVERIFIED |
| VERIFY-11 | OpenGL 1.1 and GL2 support by OS/tier. | Renderer matrix depends on this. | Apple/Microsoft/Mesa/vendor docs/tests. | High | WORKSTREAM-16 | UNCERTAIN / UNVERIFIED |
| VERIFY-12 | Classic Mac OS 8.5/9.x graphics/toolchain feasibility. | Tier 2/3 Mac support. | CodeWarrior/Carbon/QuickDraw/OpenGL docs/tests. | High | WORKSTREAM-15 | UNCERTAIN / UNVERIFIED |
| VERIFY-13 | SDL1 and SDL2 support on legacy Windows/Mac/Linux. | Platform matrix depends on this. | SDL docs/source compatibility/tests. | High | WORKSTREAM-07, WORKSTREAM-16 | UNCERTAIN / UNVERIFIED |
| VERIFY-14 | Wayland support availability by Linux tier. | Wayland is modern; older tiers likely X11 only. | Wayland release/docs. | Medium | WORKSTREAM-07 | UNCERTAIN / UNVERIFIED |
| VERIFY-15 | Windows NT 2000 SP4 to latest toolchain/runtime feasibility. | All tiers include NT 2000+. | Compiler/CRT/Win32 API docs/tests. | High | WORKSTREAM-15 | UNCERTAIN / UNVERIFIED |
| VERIFY-16 | Shell script portability on old POSIX systems. | readlink and shell features may differ. | POSIX shell tests on target systems. | Medium | WORKSTREAM-05 | UNCERTAIN / UNVERIFIED |
| VERIFY-17 | Windows CMD script parsing on supported Windows versions. | Batch parser differs across versions. | Windows test matrix. | Medium | WORKSTREAM-05 | UNCERTAIN / UNVERIFIED |
| VERIFY-18 | Actual CMake target/library names. | Prompt names may not match repo. | Inspect repo CMake. | High | WORKSTREAM-17 | UNCERTAIN / UNVERIFIED |
| VERIFY-19 | Existing input system and render API. | Avoid duplicate systems. | Inspect repo. | High | WORKSTREAM-14, WORKSTREAM-09 | UNCERTAIN / UNVERIFIED |
| VERIFY-20 | Uploaded launcher file summaries. | Prior summary unverified. | Inspect files directly. | High | WORKSTREAM-18 | UNCERTAIN / UNVERIFIED |

## 11. Timeline Register

| Sequence | Event / topic | What changed or was decided | Why it mattered | Current relevance | Confidence |
| --- | --- | --- | --- | --- | --- |
| 01 | User supplied Dominium project identity and deterministic repo constraints. | Established baseline. | Everything must respect architecture. | Active | High |
| 02 | User uploaded dominium.7z. | Repo archive provided but not inspected. | Actual repo state remains unknown. | Needs verification | High |
| 03 | User asked for project explanation. | Assistant summarized architecture. | Contextual orientation. | Historical | High |
| 04 | User proposed tackling launcher with tabs and bottom selectors. | Launcher workstream began. | Defined UI concept. | Active | High |
| 05 | User clarified launcher settings execute binaries. | Separated launcher from client/server execution. | Major architecture decision. | Active | High |
| 06 | User required C89 backend and C++98 frontends. | Language split finalized. | Implementation constraint. | Active | High |
| 07 | Unified scripts discussed. | dom-launcher/dom-client/dom-server/dom-setup idea formed. | Later renamed partly. | Superseded/active | High |
| 08 | User explored minimum platform/render launchers and legacy OS families. | Initial minimal backend idea. | Later removed. | Superseded | High |
| 09 | User removed minimal/full split. | Single full implementation per backend. | Simplified backend architecture. | Active | High |
| 10 | User replaced vector_soft with universal software renderer. | Renderer direction changed. | Critical render decision. | Active | High |
| 11 | User requested instant zoom and vector/graphics toggle. | View-mode requirement added. | Render/view architecture. | Active | High |
| 12 | User requested 2D/3D switching. | View type requirement added. | Render/view architecture. | Active | High |
| 13 | User requested arbitrary cameras. | Camera/view/target architecture added. | Tools/gameplay UI potential. | Active | High |
| 14 | User asked platform/render binaries and scripts. | Matrix and script planning. | Packaging/build decisions. | Active | High |
| 15 | User added setup and dominium scripts. | Primary commands changed. | dominium/setup now primary. | Active | High |
| 16 | User requested Codex prompt for docs/implementation. | Prompt generated. | Implementation artifact. | Historical active | High |
| 17 | User asked build/test launcher plan. | Plan generated. | Implementation path. | Active | High |
| 18 | User asked keybindings and F1-F12. | Canonical keymap generated. | Input workstream. | Active | High |
| 19 | User requested Codex prompt for keybindings. | Prompt generated. | Implementation artifact. | Historical active | High |
| 20 | User uploaded launcher source files. | Implementation artifacts appeared. | Need inspect/refactor. | Active | High |
| 21 | Assistant summarized uploaded files and recommended refactor. | Potential current-state diagnosis. | Must verify. | Unverified | Medium |
| 22 | User asked ground-up modular design. | C89 core/model/viewmodel architecture proposed. | Launcher architecture refined. | Active | High |
| 23 | User asked Linux version tiers and distro mapping. | Assistant proposed Linux baselines. | External claims need verification. | Stale/verify | Medium |
| 24 | User finalized Tier 1/2/3 support lists. | Support tier decision finalized. | Docs/matrix. | Active | High |
| 25 | User requested capability matrix. | Draft platform/render matrix produced. | Needs verification. | Active | Medium |
| 26 | User requested OC-1 discovery. | OC-1 inventory generated. | Handoff process began. | Historical | High |
| 27 | User requested OC-2 registers. | OC-2 began but was superseded by final package request. | Registers integrated here. | Historical | High |
| 28 | User requested Context Transfer Packet. | CTP generated. | Basis for this package. | Historical active | High |
| 29 | User requested final downloadable report package. | This package created. | Final per-chat export. | Active | High |

## 12. Spec Book Contribution Register

| ID | Contribution | Likely spec section | Status | Needs verification? | Label |
| --- | --- | --- | --- | --- | --- |
| SPEC-01 | Launcher process-spawning architecture | Launcher Architecture | Requirement candidate | No | FACT |
| SPEC-02 | C89 launcher core / C++98 frontends | Launcher Architecture / Build Contract | Requirement candidate | No | FACT |
| SPEC-03 | dominium/setup/dom-client/dom-server scripts | Entrypoints / Packaging | Requirement candidate | No | FACT |
| SPEC-04 | Universal software renderer | Render Backends | Requirement candidate | Implementation details yes | FACT |
| SPEC-05 | Vector/full modes on every renderer | Render Modes | Requirement candidate | Backend feasibility yes | FACT |
| SPEC-06 | Camera/view/target architecture | Render/View System | Requirement candidate | Implementation design yes | FACT |
| SPEC-07 | Support tier matrix | Platform Support | Requirement candidate | Feasibility yes | FACT |
| SPEC-08 | Capability matrix | Platform/Renderer Support | Draft requirement | Yes | FACT / UNCERTAIN |
| SPEC-09 | F1-F12 keybindings | Input Spec | Requirement candidate | No unless user revises | FACT |
| SPEC-10 | Uploaded launcher code refactor | Implementation Plan | Context item | File inspection yes | UNCERTAIN / UNVERIFIED |
