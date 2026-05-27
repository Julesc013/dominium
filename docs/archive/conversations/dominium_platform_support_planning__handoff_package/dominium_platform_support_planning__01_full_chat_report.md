# Full Chat Report — Dominium Platform Support Planning

## 0. Report Metadata

| Field | Value |
|---|---|
| Chat label | Dominium Platform Support Planning |
| Generated date anchor | 2026-05-27 Australia/Melbourne |
| Source scope | THIS CHAT ONLY: visible user/assistant turns in this chat, including the previously generated Context Transfer Packet. No web browsing, uploaded files, File Library, or external project materials were used. |
| Apparent coverage | full with caveats |
| Extraction confidence | 4 / 5 |
| Staleness risk | high |
| Future plans present | yes |
| Pending tasks present | yes |
| Artifacts/files present | yes: chat prompts/outputs and this generated package; no pre-existing downloadable files in the visible chat |
| Safe for aggregation | yes, with caveats |
| Main limitations | No external verification was performed for current platform facts.; Prior assistant citations are not portable into future chats.; No engine/toolchain, timeline, budget, team, or repository details were established.; Some assistant-introduced concepts, especially “Domino,” are unconfirmed.; This package intentionally covers only this chat, not the entire Dominium project. |

## 1. Executive Summary

This chat was about defining the operating systems, hardware families, runtime environments, and support strategy for the Dominium Game. The conversation began with a broad question about what “systems” would be supported, briefly expanded into a retro-heavy assistant proposal covering bare-metal/firmware targets, CP/M, DOS, classic GUI systems, and old OSes, then narrowed to what operating systems Dominium itself could run on. A later assistant response introduced a split between the full Dominium product and a reduced engine/core concept called “Domino,” but that name and split remain assistant-introduced and unconfirmed by the user.

The user then expanded the scope substantially, asking to support as many devices as possible across PlayStation consoles and handhelds, Xbox consoles, PC handhelds, Nintendo consoles and handhelds, Android, iOS, Web, and related families. The user supplied a comprehensive target inventory including PlayStation, Xbox, Nintendo, PC handhelds, Android device classes, Apple hardware/software, Web technologies and browsers, AR devices and runtimes, VR devices and runtimes, and cross-cutting software targets such as C/C++ runtimes, Vulkan, OpenGL/OpenGL ES, DirectX, Metal, SDL, GLFW, Unity Runtime, Unreal Runtime, Wine, and Proton. That inventory is a central artifact of this chat, but it is a conversation fact rather than verified current platform truth.

The most important decision came after the large inventory: the user explicitly stated that “Android, iOS, and Web will be our primary focus after PC, and should be primary top tier support likewise.” This is the controlling carry-forward decision. The current working hierarchy is therefore: PC first; Android, iOS, and Web also Tier-0 / primary / first-class. PC implies Windows, macOS, and Linux, though exact versions and CPU architectures remain undecided. Android means at minimum a first-class Android strategy, but exact support for Android TV, Google TV, Android Automotive, Android Go, Chromebooks, and vendor ROMs is unresolved. iOS is Tier-0, with iPadOS included by assistant synthesis but not separately stated in the final user wording; tvOS, watchOS, macOS, and visionOS require separate classification. Web is Tier-0, with WASM/browser support central; WebGPU, WebGL fallback, PWA/offline behavior, storage, and browser baselines remain unresolved.

The assistant’s current working model placed current commercial consoles as secondary/gated targets and legacy consoles/old handhelds as constrained, research, engine-only, emulator-hosted, community, or unsupported unless later elevated. That model is practical but remains assistant-authored. Closed-console support must be verified through current official platform-holder sources before implementation planning. Likewise, all real-world platform claims, SDK rules, store requirements, browser support claims, hardware statuses, and OS facts require verification before future use.

The highest-value next action is to create a formal Platform Support Matrix with stable support categories and platform contracts. The matrix should specify platform family, specific targets, tier, product scope, minimum OS/API, CPU/ABI, graphics backend, input model, audio, storage/save model, networking, distribution channel, QA obligation, certification/legal constraints, dependencies, risks, verification status, and next action. The next assistant must not lose the fact that Android/iOS/Web are top-tier primary targets after PC, must not treat mobile/web as late ports, must not turn assistant suggestions into user decisions, and must not treat the long device inventory as a literal full-parity commitment.

## 2. How to Use This Report

This report covers only this old chat. It is designed for human reading, assistant handoff, later aggregation with other chat reports, and eventual Project Spec Book construction. It should not be treated as a full project specification by itself.

Use the labels literally. FACT means explicitly present in this chat, not necessarily true in the external world. INFERENCE means a reasonable reconstruction from this chat, not a user decision. UNCERTAIN / UNVERIFIED means unclear, stale-risk, or not directly established. PROJECT-CONTEXT is reserved for information outside the visible chat; this package intentionally avoids relying on such context except where the project name is already visible in the chat.

Direct user statements outrank assistant outputs. Latest user statements outrank earlier brainstorms. Assistant proposals remain lower-trust unless the user accepted them. External facts about platforms, SDKs, stores, hardware, browsers, legal requirements, or products must be verified from current official sources before they become implementation facts.

Use this report as a source packet for later aggregation. Do not merge uncertain items with confirmed decisions without preserving provenance. Do not erase contradictions or changes of direction.

## 3. User Preferences Visible in This Chat

### 3.1 Explicit Preferences

| Label | Preference | Source basis | Strength | Implication for future assistants | Risk if misunderstood | Source label |
| --- | --- | --- | --- | --- | --- | --- |
| PREFERENCE-01 | Maximum-fidelity state transfer, not normal summary. | User requested a Context Transfer Packet and later a final report package; both prompts emphasize not compressing aggressively. | strong | Preserve details, uncertainty, rejected options, and next actions. | Critical project state may be lost. | FACT |
| PREFERENCE-02 | No invented facts and no silent inference. | Current user prompt critical rules. | strong | Use labels and unknowns rather than filling gaps. | False requirements or platform claims may enter the spec. | FACT |
| PREFERENCE-03 | Important items must be labeled by evidentiary status. | Current user prompt. | strong | Use FACT, INFERENCE, UNCERTAIN / UNVERIFIED, PROJECT-CONTEXT consistently. | Future assistants may mistake speculation for decision. | FACT |
| PREFERENCE-04 | User statements outrank assistant statements. | Current user prompt; previous packet rules. | strong | Latest explicit user priority controls platform hierarchy. | Assistant proposals like “Domino” or retro tiers may become false decisions. | FACT |
| PREFERENCE-05 | Preserve rejected, superseded, deprioritized, contradictory, and tentative items. | Current user prompt. | strong | Registers must include rejected options and changes of direction. | Future work may repeat old mistakes or erase unresolved conflicts. | FACT |
| PREFERENCE-06 | Structured headings, tables, stable IDs, and consistent terminology. | Current user prompt specifies ID patterns and file structures. | strong | Use normalized registers suitable for aggregation. | Later spec-book construction becomes harder. | FACT |
| PREFERENCE-07 | Downloadable files and ZIP if possible. | Current user prompt. | strong | Create actual Markdown/YAML files and archive them; do not merely print content if tools are available. | User may not get reusable package. | FACT |
| PREFERENCE-08 | Use date anchor 2026-05-27 Australia/Melbourne. | Current user prompt. | strong | Metadata and staleness notes should use the supplied anchor. | Reports may mix incompatible dates. | FACT |
| PREFERENCE-09 | This-chat-only source scope unless external context is labeled PROJECT-CONTEXT. | Current user prompt. | strong | Avoid importing whole-project memories or user profile into this package unless labeled. | Aggregation may contaminate chat-specific provenance. | FACT |
| PREFERENCE-10 | Report should support future master Project Spec Book construction. | Current user prompt and aggregator prompt included by user. | strong | Include YAML, aggregator packet, spec-book notes, and merge warnings. | Output may be readable but not machine/aggregation-ready. | FACT |

### 3.2 Inferred Preferences

| Label | Preference | Source basis | Strength | Implication for future assistants | Risk if misunderstood | Source label |
| --- | --- | --- | --- | --- | --- | --- |
| PREFERENCE-12 | Engine or implementation details should not be assumed. | The chat listed many runtimes/APIs but did not choose one. | medium | Ask/decide engine separately; avoid defaulting to Unity/Unreal/custom. | Planning may lock into unsupported architecture prematurely. | INFERENCE |

### 3.3 Preferences Not Established by This Chat

- No engine/toolchain preference is established in this chat.
- No budget, team size, release date, or commercial priority order is established.
- No exact minimum OS/API versions are established.
- No confirmed name for a separate engine/core layer is established.
- No final decision on console generation priority is established.
- No final decision on XR priority is established.
- No final decision on tvOS, watchOS, visionOS, Android Automotive, or Android TV tier status is established.
- No existing source files, repositories, build scripts, or design documents were provided in this chat.

## 4. Complete Topic and Workstream Inventory

| Stable ID | Name | Objective | Current state | Desired end state | Status | Priority | Confidence | Source label |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| WORKSTREAM-01 | Overall Dominium platform support strategy and tier model | Define which operating systems, devices, and runtime families Dominium should support and classify each into a support tier. | Latest visible priority: PC first; Android, iOS, and Web are also primary top-tier support. Consoles and legacy systems remain desired but not equal to Tier-0 unless later elevated. | A formal platform support matrix and platform-contract system with explicit support scope, minimum versions, APIs, QA obligations, and legal constraints per target. | active | highest | 5 | FACT / INFERENCE |
| WORKSTREAM-02 | Tier-0 PC desktop operating system support | Support PC as the first primary platform family, including Windows, macOS, and Linux. | PC is established by user wording as the platform before Android/iOS/Web. Earlier assistant outputs proposed Windows 10/11, macOS Apple Silicon/Intel optional, Linux x64/ARM64 with X11/Wayland. | A precise PC support contract covering Windows, macOS, Linux, CPU architectures, graphics APIs, packaging, input, storage, and QA targets. | active | highest | 4 | FACT / INFERENCE |
| WORKSTREAM-03 | Tier-0 Android ecosystem support | Make Android primary top-tier support after PC across relevant Android phones, tablets, TV/handheld classes, and compatible environments. | User explicitly elevated Android to primary top-tier support. User listed Android phones, tablets, Android TV/Google TV, Android Automotive, Android handheld consoles, Chromebooks, AOSP, Android Go, and vendor ROMs. | A first-class Android support contract with minimum API level, ABI list, graphics backend, lifecycle model, input model, device class support, store/distribution rules, and QA tiers. | active | highest | 5 | FACT |
| WORKSTREAM-04 | Tier-0 iOS/iPadOS and Apple-family classification | Make iOS primary top-tier support after PC and classify related Apple platforms. | User explicitly elevated iOS to primary top-tier support. Assistant included iPadOS as co-primary. User listed iPhone, iPod Touch, iPad families, Apple TV, Apple Watch, Mac Intel/Apple Silicon, iOS, iPadOS, tvOS, watchOS, and macOS. | A clear Apple support contract distinguishing Tier-0 iOS/iPadOS/macOS from possible secondary or unsupported Apple-family targets such as tvOS, watchOS, and visionOS. | active | highest | 4 | FACT / INFERENCE |
| WORKSTREAM-05 | Tier-0 Web/WASM/browser/PWA support | Make Web primary top-tier support after PC using WASM/browser technologies. | User explicitly elevated Web to primary top-tier support. User listed WASM, HTML5, JavaScript, WebGL, WebGPU, PWA, and major browsers. | A first-class Web support contract specifying browser baselines, WASM features, graphics fallback policy, storage/save behavior, asset loading, PWA/offline status, and QA matrix. | active | highest | 5 | FACT |
| WORKSTREAM-06 | Closed console support strategy: PlayStation, Xbox, Nintendo | Plan support for PlayStation, Xbox, and Nintendo hardware/software families without confusing official commercial support with legacy/research or emulator support. | User requested broad console support. Assistant proposed current commercial consoles as Tier-1/gated and legacy consoles as constrained/research. No user acceptance of exact console tiering beyond not objecting before elevating Android/iOS/Web. | A console strategy that separates current officially supported SKUs from legacy, handheld, remote-play, and research-only targets. | active but secondary | medium-high | 4 | FACT / INFERENCE |
| WORKSTREAM-07 | PC handheld support | Support PC handheld devices through PC OS targets plus handheld-specific UX, input, and performance profiles. | User listed Steam Deck, ROG Ally, Legion Go, Ayaneo, GPD, OneXPlayer, MSI Claw, Zotac Zone, AOKZOE, and Smach Z. Assistant proposed mapping them to Windows/Linux/SteamOS rather than treating each as a separate OS target. | A PC handheld submatrix with Steam Deck, Windows handhelds, and Linux handhelds mapped to support levels, performance targets, controller UI, resolution scaling, and suspend/resume behavior. | active | high | 4 | FACT / INFERENCE |
| WORKSTREAM-08 | AR/VR/XR support strategy | Classify AR/VR/XR devices and runtimes in the broader support plan. | User listed AR and VR hardware/software. Assistant proposed runtime-first support via OpenXR and WebXR but XR priority was not decided. | A clear XR tier decision and runtime strategy that maps XR devices to OpenXR/WebXR/platform-specific paths without derailing Tier-0 PC/mobile/web. | unclear / future | medium | 3 | FACT / INFERENCE |
| WORKSTREAM-09 | Legacy, retro, bare-metal, and constrained support | Preserve optional legacy/retro/bare-metal possibilities without turning them into full Dominium parity commitments. | Earlier assistant listed CP/M, DOS, Win16/Win9x, Classic Mac, AmigaOS, OS/2, Z80/8080/8085, S-100, RC2014, and firmware targets. Later framing demoted these to constrained/research/engine-only. | A legacy target policy defining which, if any, retro systems receive engine-only demos, validation builds, community ports, or no support. | historical / secondary | low-medium | 4 | FACT / INFERENCE |
| WORKSTREAM-10 | Cross-cutting architecture, backend, runtime, and compatibility strategy | Define shared technical architecture needed to support PC, Android, iOS, Web, consoles, handhelds, and XR. | User listed native C/C++ runtimes, Vulkan, OpenGL/ES, DirectX 9–12, Metal, SDL, GLFW, Unity Runtime, Unreal Runtime, Wine, and Proton. Assistant proposed a portable core plus platform host layers and render backends, but engine/toolchain remains undecided. | An architecture decision record covering engine choice, platform abstraction, renderer backends, input/UI abstraction, audio, filesystem/save, networking, asset pipeline, deterministic core, and compatibility policies. | active / unresolved | highest | 4 | FACT / INFERENCE |
| WORKSTREAM-11 | Chat-specific handoff/report package | Convert the previously generated Context Transfer Packet and visible chat context into downloadable Markdown/YAML/ZIP report files. | This package is being generated from the visible chat and previous Context Transfer Packet. | A reusable per-chat package containing a full report, spec sheet YAML, aggregator packet, registers, reader brief, verification/audit, manifest, and ZIP archive. | active during this response | highest for current task | 5 | FACT |

## 5. Detailed Workstream State

### WORKSTREAM-01 — Overall Dominium platform support strategy and tier model
- **Label:** FACT / INFERENCE
- **Objective:** Define which operating systems, devices, and runtime families Dominium should support and classify each into a support tier.
- **Background:** The user started with broad system/OS questions, expanded to console/mobile/web/XR device families, then explicitly elevated Android/iOS/Web after PC.
- **Current state:** Latest visible priority: PC first; Android, iOS, and Web are also primary top-tier support. Consoles and legacy systems remain desired but not equal to Tier-0 unless later elevated.
- **Desired end state:** A formal platform support matrix and platform-contract system with explicit support scope, minimum versions, APIs, QA obligations, and legal constraints per target.
- **Importance:** This workstream affects support scope, architecture, QA, legal constraints, and future aggregation for its target area.
- **Decisions made:** DECISION-01; DECISION-02; DECISION-03; DECISION-04; DECISION-05; DECISION-10
- **Decisions pending:** QUESTION-01; QUESTION-18; QUESTION-19
- **Pending tasks:** TASK-01; TASK-02; TASK-17; TASK-18
- **Constraints:** CONSTRAINT-01; CONSTRAINT-02; CONSTRAINT-03; CONSTRAINT-07; CONSTRAINT-12
- **Dependencies:** Current official platform facts; Engine/toolchain decision; Formal definition of support levels
- **Timeline / sequencing:** No implementation timeline provided. Sequencing inferred: define matrix first, then contracts, then baselines and verification.
- **Blockers:** Undefined meaning of support for many devices; Unknown engine/toolchain; Unverified platform requirements
- **Risks:** RISK-01; RISK-03; RISK-07; RISK-15
- **Artifacts:** ARTIFACT-07; ARTIFACT-09; ARTIFACT-10; ARTIFACT-11
- **Success criteria:** Every device family maps to an explicit tier; Tier-0 obligations are unambiguous; Secondary/research targets are not confused with parity support
- **Recommended next action:** Create a formal Platform Support Matrix with stable support categories and verification status per platform family.
- **Verification needed:** VERIFY-01; VERIFY-05; VERIFY-06; VERIFY-07
- **Confidence:** 5
- **Carry-forward priority:** critical

### WORKSTREAM-02 — Tier-0 PC desktop operating system support
- **Label:** FACT / INFERENCE
- **Objective:** Support PC as the first primary platform family, including Windows, macOS, and Linux.
- **Background:** User asked what operating systems Dominium can run on. Assistant repeatedly placed Windows/macOS/Linux as full-product targets.
- **Current state:** PC is established by user wording as the platform before Android/iOS/Web. Earlier assistant outputs proposed Windows 10/11, macOS Apple Silicon/Intel optional, Linux x64/ARM64 with X11/Wayland.
- **Desired end state:** A precise PC support contract covering Windows, macOS, Linux, CPU architectures, graphics APIs, packaging, input, storage, and QA targets.
- **Importance:** This workstream affects support scope, architecture, QA, legal constraints, and future aggregation for its target area.
- **Decisions made:** DECISION-01
- **Decisions pending:** QUESTION-06; QUESTION-07; QUESTION-08; QUESTION-20
- **Pending tasks:** TASK-03; TASK-13; TASK-14; TASK-17
- **Constraints:** CONSTRAINT-07; CONSTRAINT-08; CONSTRAINT-12
- **Dependencies:** Renderer strategy; Build system; Distribution channels; QA device coverage
- **Timeline / sequencing:** Should be specified before implementation planning; no dates given.
- **Blockers:** Minimum OS versions unknown; Architecture targets unknown; Engine/toolchain unknown
- **Risks:** RISK-02; RISK-08; RISK-15
- **Artifacts:** ARTIFACT-04; ARTIFACT-10; ARTIFACT-11
- **Success criteria:** PC platforms have explicit minimum versions; Windows/macOS/Linux are supported with defined renderer/input/storage backends; PC does not become the only architecture driver
- **Recommended next action:** Define Windows/macOS/Linux baseline rows in the platform matrix.
- **Verification needed:** VERIFY-15; VERIFY-19
- **Confidence:** 4
- **Carry-forward priority:** critical

### WORKSTREAM-03 — Tier-0 Android ecosystem support
- **Label:** FACT
- **Objective:** Make Android primary top-tier support after PC across relevant Android phones, tablets, TV/handheld classes, and compatible environments.
- **Background:** Android was initially one of many device families, then was explicitly promoted by the user after PC.
- **Current state:** User explicitly elevated Android to primary top-tier support. User listed Android phones, tablets, Android TV/Google TV, Android Automotive, Android handheld consoles, Chromebooks, AOSP, Android Go, and vendor ROMs.
- **Desired end state:** A first-class Android support contract with minimum API level, ABI list, graphics backend, lifecycle model, input model, device class support, store/distribution rules, and QA tiers.
- **Importance:** This workstream affects support scope, architecture, QA, legal constraints, and future aggregation for its target area.
- **Decisions made:** DECISION-02; DECISION-05
- **Decisions pending:** QUESTION-02; QUESTION-09; QUESTION-25
- **Pending tasks:** TASK-04; TASK-13; TASK-14; TASK-15; TASK-16; TASK-18
- **Constraints:** CONSTRAINT-07; CONSTRAINT-08; CONSTRAINT-12; CONSTRAINT-18
- **Dependencies:** Android SDK/NDK facts; Graphics backend decision; Input/UI strategy; QA device plan
- **Timeline / sequencing:** Tier-0 contract should be defined immediately after the global support matrix.
- **Blockers:** Minimum API and ABI not chosen; Android TV/Automotive/Go scope unresolved; Store targets not chosen
- **Risks:** RISK-06; RISK-18
- **Artifacts:** ARTIFACT-07; ARTIFACT-09; ARTIFACT-10
- **Success criteria:** Android is not treated as a port; Lifecycle and memory constraints shape core architecture; Supported Android subfamilies are explicitly classified
- **Recommended next action:** Define Android subtargets and minimum API/ABI/graphics baseline; mark Android Go, TV, Automotive, and Chromebooks as pending until scoped.
- **Verification needed:** VERIFY-05; VERIFY-11
- **Confidence:** 5
- **Carry-forward priority:** critical

### WORKSTREAM-04 — Tier-0 iOS/iPadOS and Apple-family classification
- **Label:** FACT / INFERENCE
- **Objective:** Make iOS primary top-tier support after PC and classify related Apple platforms.
- **Background:** Apple platforms appeared in the target inventory, and iOS was later promoted to top-tier after PC.
- **Current state:** User explicitly elevated iOS to primary top-tier support. Assistant included iPadOS as co-primary. User listed iPhone, iPod Touch, iPad families, Apple TV, Apple Watch, Mac Intel/Apple Silicon, iOS, iPadOS, tvOS, watchOS, and macOS.
- **Desired end state:** A clear Apple support contract distinguishing Tier-0 iOS/iPadOS/macOS from possible secondary or unsupported Apple-family targets such as tvOS, watchOS, and visionOS.
- **Importance:** This workstream affects support scope, architecture, QA, legal constraints, and future aggregation for its target area.
- **Decisions made:** DECISION-03; DECISION-05
- **Decisions pending:** QUESTION-03; QUESTION-10; QUESTION-26
- **Pending tasks:** TASK-05; TASK-13; TASK-14; TASK-15; TASK-16; TASK-18
- **Constraints:** CONSTRAINT-07; CONSTRAINT-08; CONSTRAINT-12
- **Dependencies:** Apple SDK and distribution rules; Metal or engine rendering path; Device baseline decision
- **Timeline / sequencing:** Should be defined alongside Android and Web because it is Tier-0.
- **Blockers:** Minimum OS version unknown; iPadOS explicit status not separately confirmed; tvOS/watchOS/visionOS unresolved
- **Risks:** RISK-06; RISK-17
- **Artifacts:** ARTIFACT-07; ARTIFACT-09; ARTIFACT-10
- **Success criteria:** iOS/iPadOS support is first-class; Apple-family non-mobile platforms are not accidentally promised; Apple-specific lifecycle and sandbox constraints are captured
- **Recommended next action:** Define iOS/iPadOS minimum OS/device baseline and classify tvOS/watchOS/visionOS separately.
- **Verification needed:** VERIFY-06; VERIFY-10
- **Confidence:** 4
- **Carry-forward priority:** critical

### WORKSTREAM-05 — Tier-0 Web/WASM/browser/PWA support
- **Label:** FACT
- **Objective:** Make Web primary top-tier support after PC using WASM/browser technologies.
- **Background:** Web was first described by assistant as a universal fallback; latest user decision makes it a top-tier primary target, not merely a fallback.
- **Current state:** User explicitly elevated Web to primary top-tier support. User listed WASM, HTML5, JavaScript, WebGL, WebGPU, PWA, and major browsers.
- **Desired end state:** A first-class Web support contract specifying browser baselines, WASM features, graphics fallback policy, storage/save behavior, asset loading, PWA/offline status, and QA matrix.
- **Importance:** This workstream affects support scope, architecture, QA, legal constraints, and future aggregation for its target area.
- **Decisions made:** DECISION-04; DECISION-05; DECISION-09
- **Decisions pending:** QUESTION-04; QUESTION-05; QUESTION-22
- **Pending tasks:** TASK-06; TASK-14; TASK-15; TASK-16; TASK-18
- **Constraints:** CONSTRAINT-07; CONSTRAINT-08; CONSTRAINT-12; CONSTRAINT-20
- **Dependencies:** WASM toolchain; WebGPU/WebGL policy; Browser storage strategy; Asset pipeline
- **Timeline / sequencing:** Should be defined at the same level as PC/mobile contracts.
- **Blockers:** Browser minimums unknown; WebGPU/WebGL fallback unresolved; PWA/offline status unknown
- **Risks:** RISK-02; RISK-06; RISK-19
- **Artifacts:** ARTIFACT-07; ARTIFACT-09; ARTIFACT-10
- **Success criteria:** Web build is not a demo unless explicitly scoped; Browser compatibility matrix exists; Web constraints influence core design
- **Recommended next action:** Define browser support matrix and WebGPU/WebGL/WASM feature policy.
- **Verification needed:** VERIFY-07; VERIFY-08; VERIFY-18
- **Confidence:** 5
- **Carry-forward priority:** critical

### WORKSTREAM-06 — Closed console support strategy: PlayStation, Xbox, Nintendo
- **Label:** FACT / INFERENCE
- **Objective:** Plan support for PlayStation, Xbox, and Nintendo hardware/software families without confusing official commercial support with legacy/research or emulator support.
- **Background:** User listed many PlayStation, Xbox, and Nintendo generations, firmware/OS names, and handhelds.
- **Current state:** User requested broad console support. Assistant proposed current commercial consoles as Tier-1/gated and legacy consoles as constrained/research. No user acceptance of exact console tiering beyond not objecting before elevating Android/iOS/Web.
- **Desired end state:** A console strategy that separates current officially supported SKUs from legacy, handheld, remote-play, and research-only targets.
- **Importance:** This workstream affects support scope, architecture, QA, legal constraints, and future aggregation for its target area.
- **Decisions made:** DECISION-06; DECISION-11; DECISION-12
- **Decisions pending:** QUESTION-14; QUESTION-15
- **Pending tasks:** TASK-08; TASK-09; TASK-18
- **Constraints:** CONSTRAINT-09; CONSTRAINT-10; CONSTRAINT-11; CONSTRAINT-19
- **Dependencies:** Official platform-holder access; Devkits/toolchains; Certification rules; Console-specific QA
- **Timeline / sequencing:** After Tier-0 platform contracts unless the user elevates consoles.
- **Blockers:** No confirmed partner program/devkit access; Specific current-gen/cross-gen strategy undecided
- **Risks:** RISK-05; RISK-07; RISK-11; RISK-16
- **Artifacts:** ARTIFACT-07; ARTIFACT-08
- **Success criteria:** Console claims are legal, official, and scoped; Legacy console claims are not mistaken for parity support; Every console family maps to a clear status
- **Recommended next action:** Create a console submatrix: current commercial, legacy research, remote-play only, emulator-hosted, unsupported.
- **Verification needed:** VERIFY-01; VERIFY-02; VERIFY-03; VERIFY-04; VERIFY-13
- **Confidence:** 4
- **Carry-forward priority:** high

### WORKSTREAM-07 — PC handheld support
- **Label:** FACT / INFERENCE
- **Objective:** Support PC handheld devices through PC OS targets plus handheld-specific UX, input, and performance profiles.
- **Background:** PC handhelds were included in the user's expanded hardware family list and are closely related to Tier-0 PC support.
- **Current state:** User listed Steam Deck, ROG Ally, Legion Go, Ayaneo, GPD, OneXPlayer, MSI Claw, Zotac Zone, AOKZOE, and Smach Z. Assistant proposed mapping them to Windows/Linux/SteamOS rather than treating each as a separate OS target.
- **Desired end state:** A PC handheld submatrix with Steam Deck, Windows handhelds, and Linux handhelds mapped to support levels, performance targets, controller UI, resolution scaling, and suspend/resume behavior.
- **Importance:** This workstream affects support scope, architecture, QA, legal constraints, and future aggregation for its target area.
- **Decisions made:** DECISION-08
- **Decisions pending:** QUESTION-13; QUESTION-17
- **Pending tasks:** TASK-07; TASK-15; TASK-17; TASK-18
- **Constraints:** CONSTRAINT-07; CONSTRAINT-08; CONSTRAINT-12
- **Dependencies:** PC support contract; Controller-first UI; Performance presets; Steam/handheld QA devices
- **Timeline / sequencing:** Should be specified after PC baseline but before claiming handheld support.
- **Blockers:** Steam Deck status undecided; Handheld performance floor unknown
- **Risks:** RISK-06; RISK-09; RISK-15
- **Artifacts:** ARTIFACT-07
- **Success criteria:** Handheld devices are not treated as generic desktops; Controller UI and small-screen behavior are specified; Steam Deck/Windows handhelds have clear verification status
- **Recommended next action:** Add PC handheld profiles to the support matrix and decide Steam Deck tier.
- **Verification needed:** VERIFY-09; VERIFY-14
- **Confidence:** 4
- **Carry-forward priority:** high

### WORKSTREAM-08 — AR/VR/XR support strategy
- **Label:** FACT / INFERENCE
- **Objective:** Classify AR/VR/XR devices and runtimes in the broader support plan.
- **Background:** XR appeared in the user's comprehensive device list but was not included in the latest top-tier priority statement.
- **Current state:** User listed AR and VR hardware/software. Assistant proposed runtime-first support via OpenXR and WebXR but XR priority was not decided.
- **Desired end state:** A clear XR tier decision and runtime strategy that maps XR devices to OpenXR/WebXR/platform-specific paths without derailing Tier-0 PC/mobile/web.
- **Importance:** This workstream affects support scope, architecture, QA, legal constraints, and future aggregation for its target area.
- **Decisions made:** DECISION-14
- **Decisions pending:** QUESTION-16
- **Pending tasks:** TASK-10; TASK-18
- **Constraints:** CONSTRAINT-12; CONSTRAINT-18
- **Dependencies:** Product design decision; Renderer stereo support; OpenXR/WebXR status; Platform-specific stores
- **Timeline / sequencing:** Not sequenced; likely after Tier-0 contracts unless elevated.
- **Blockers:** No XR priority; No confirmed engine/runtime; No XR-specific gameplay requirement
- **Risks:** RISK-07; RISK-14; RISK-20
- **Artifacts:** ARTIFACT-07; ARTIFACT-08
- **Success criteria:** XR support is explicitly scoped; XR does not implicitly become Tier-0; Runtime-based approach is verified before use
- **Recommended next action:** Classify XR as pending/future unless user elevates it, then verify OpenXR/WebXR feasibility.
- **Verification needed:** VERIFY-12
- **Confidence:** 3
- **Carry-forward priority:** medium

### WORKSTREAM-09 — Legacy, retro, bare-metal, and constrained support
- **Label:** FACT / INFERENCE
- **Objective:** Preserve optional legacy/retro/bare-metal possibilities without turning them into full Dominium parity commitments.
- **Background:** The first assistant answer was broad and retro-heavy; later user focus shifted to console/mobile/web and then Tier-0 PC/mobile/web.
- **Current state:** Earlier assistant listed CP/M, DOS, Win16/Win9x, Classic Mac, AmigaOS, OS/2, Z80/8080/8085, S-100, RC2014, and firmware targets. Later framing demoted these to constrained/research/engine-only.
- **Desired end state:** A legacy target policy defining which, if any, retro systems receive engine-only demos, validation builds, community ports, or no support.
- **Importance:** This workstream affects support scope, architecture, QA, legal constraints, and future aggregation for its target area.
- **Decisions made:** DECISION-07; DECISION-12
- **Decisions pending:** QUESTION-15
- **Pending tasks:** TASK-09; TASK-18
- **Constraints:** CONSTRAINT-09; CONSTRAINT-11; CONSTRAINT-12
- **Dependencies:** Engine/core portability; Legal BIOS/firmware approach; Retro toolchains
- **Timeline / sequencing:** No timeline; should not precede Tier-0 contracts unless the user reprioritizes.
- **Blockers:** No explicit latest user commitment; Severe technical limits; Legal uncertainty for firmware/BIOS
- **Risks:** RISK-05; RISK-07; RISK-10
- **Artifacts:** ARTIFACT-02; ARTIFACT-04; ARTIFACT-11
- **Success criteria:** Retro systems are not mistaken for full-product targets; Any reduced builds are explicitly labeled; No proprietary firmware/BIOS is bundled
- **Recommended next action:** Keep legacy as Tier-2/research in the matrix and avoid architecture debt unless there is low-cost portability benefit.
- **Verification needed:** VERIFY-13
- **Confidence:** 4
- **Carry-forward priority:** medium

### WORKSTREAM-10 — Cross-cutting architecture, backend, runtime, and compatibility strategy
- **Label:** FACT / INFERENCE
- **Objective:** Define shared technical architecture needed to support PC, Android, iOS, Web, consoles, handhelds, and XR.
- **Background:** The breadth of desired platforms creates hard architecture constraints before implementation starts.
- **Current state:** User listed native C/C++ runtimes, Vulkan, OpenGL/ES, DirectX 9–12, Metal, SDL, GLFW, Unity Runtime, Unreal Runtime, Wine, and Proton. Assistant proposed a portable core plus platform host layers and render backends, but engine/toolchain remains undecided.
- **Desired end state:** An architecture decision record covering engine choice, platform abstraction, renderer backends, input/UI abstraction, audio, filesystem/save, networking, asset pipeline, deterministic core, and compatibility policies.
- **Importance:** This workstream affects support scope, architecture, QA, legal constraints, and future aggregation for its target area.
- **Decisions made:** DECISION-13; DECISION-15
- **Decisions pending:** QUESTION-11; QUESTION-20; QUESTION-21; QUESTION-22; QUESTION-23
- **Pending tasks:** TASK-11; TASK-13; TASK-14; TASK-15; TASK-16; TASK-17
- **Constraints:** CONSTRAINT-07; CONSTRAINT-08; CONSTRAINT-12; CONSTRAINT-20
- **Dependencies:** Platform contracts; Engine/toolchain decision; Renderer API feasibility; Input/UI requirements
- **Timeline / sequencing:** Must be resolved before implementation claims are made.
- **Blockers:** Engine choice unknown; Backend policy unknown; Support scope unknown for many devices
- **Risks:** RISK-06; RISK-08; RISK-15; RISK-19
- **Artifacts:** ARTIFACT-07; ARTIFACT-08; ARTIFACT-10; ARTIFACT-11
- **Success criteria:** Architecture can serve Tier-0 without PC-only assumptions; Backend policies are explicit; Compatibility layers are not overpromised
- **Recommended next action:** After the support matrix, create architecture contracts for platform abstraction, render, input, storage, network, and build/release.
- **Verification needed:** VERIFY-15; VERIFY-16; VERIFY-19
- **Confidence:** 4
- **Carry-forward priority:** critical

### WORKSTREAM-11 — Chat-specific handoff/report package
- **Label:** FACT
- **Objective:** Convert the previously generated Context Transfer Packet and visible chat context into downloadable Markdown/YAML/ZIP report files.
- **Background:** User explicitly requested a final downloadable, shareable, reusable report package for this individual old chat.
- **Current state:** This package is being generated from the visible chat and previous Context Transfer Packet.
- **Desired end state:** A reusable per-chat package containing a full report, spec sheet YAML, aggregator packet, registers, reader brief, verification/audit, manifest, and ZIP archive.
- **Importance:** This workstream affects support scope, architecture, QA, legal constraints, and future aggregation for its target area.
- **Decisions made:** DECISION-16
- **Decisions pending:** none
- **Pending tasks:** TASK-19
- **Constraints:** CONSTRAINT-01; CONSTRAINT-02; CONSTRAINT-03; CONSTRAINT-04; CONSTRAINT-14; CONSTRAINT-15; CONSTRAINT-16
- **Dependencies:** Visible chat context; Previously generated Context Transfer Packet; File generation tools
- **Timeline / sequencing:** Current response.
- **Blockers:** none
- **Risks:** RISK-01; RISK-12; RISK-13
- **Artifacts:** ARTIFACT-11; ARTIFACT-12; ARTIFACT-13
- **Success criteria:** All requested files are created; ZIP exists if possible; Files use stable IDs; Report is safe for later aggregation with caveats
- **Recommended next action:** Store the package and use it as input to a later cross-chat aggregation process.
- **Verification needed:** VERIFY-20
- **Confidence:** 5
- **Carry-forward priority:** critical

## 6. Chronological Timeline

| Sequence | Event / topic | What changed or was decided | Why it mattered | Current relevance | Confidence |
| --- | --- | --- | --- | --- | --- |
| 1 | User asked what systems would ultimately be supported. | Opened broad support-scope discussion. | Established platform-support planning as the chat topic. | Historical origin; superseded by later specificity. | 5 |
| 2 | Assistant proposed broad retro-oriented tiers. | Introduced bare-metal/firmware, legacy OS, and classic GUI systems. | Created a very broad support horizon including CP/M, DOS, Z80, Win16, Classic Mac, etc. | Historical/deprioritized; not latest priority. | 5 |
| 3 | User clarified the question: what operating systems can Dominium run on? | Shifted from broad systems to Dominium OS support. | Focused planning on the Dominium product rather than arbitrary hardware systems. | Still relevant to PC/mobile/web OS matrix. | 5 |
| 4 | Assistant split Dominium full product from “Domino” reduced engine/core. | Proposed full product targets vs constrained engine-only/legacy builds. | Introduced useful product-scope distinction, but also an unconfirmed name. | Use scope distinction cautiously; do not treat “Domino” as confirmed. | 5 |
| 5 | User requested support for as many devices as possible across PlayStation, Xbox, PC handhelds, Nintendo, Android, iOS, Web, etc. | Expanded scope from OSes to device families and ecosystems. | Required moving from simple OS list to tiered support contracts. | Still relevant as broad ambition. | 5 |
| 6 | Assistant proposed platform-family target categories. | Grouped targets into Web, PC handhelds, Android, iOS, consoles, and top-level PC/mobile/web/console families. | Provided a preliminary classification but contained count inconsistency. | Intermediate; superseded by later detailed model. | 5 |
| 7 | User provided comprehensive hardware/software inventory. | Listed PlayStation, Xbox, Nintendo, PC handhelds, Android, Apple, Web, AR, VR, and cross-cutting runtimes/APIs. | Became the master visible target list for this chat. | Central artifact; facts require verification before implementation. | 5 |
| 8 | Assistant classified targets into Class A open platforms, Class B closed consoles, Class C legacy closed consoles, and Class D emulated runtime. | Introduced official/gated vs open vs legacy/research distinctions and OpenXR/WebXR runtime approach. | Gave a practical framework for controlling scope and legal risk. | Useful assistant framework, lower authority than user decisions. | 5 |
| 9 | User explicitly elevated Android, iOS, and Web after PC. | Made Android, iOS, and Web primary top-tier support after PC. | This is the controlling platform-priority decision. | Highest-priority carry-forward fact. | 5 |
| 10 | Assistant locked a working hierarchy: Tier-0 PC + Android + iOS/iPadOS + Web; Tier-1 consoles; Tier-2 legacy/research. | Synthesized latest priority into tier model and architecture consequences. | Provides current working hierarchy but includes assistant-authored details requiring care. | Current working model, with caveats. | 5 |
| 11 | User requested maximum-fidelity Context Transfer Packet. | Required state-transfer preservation of decisions, constraints, artifacts, open questions, risks, and next actions. | Created prior handoff artifact for this chat. | Source for current package; repaired and normalized here. | 5 |
| 12 | Assistant produced the Context Transfer Packet. | Summarized and organized platform-support state but lacked stable IDs and files; included some broad context that needed source-scope repair. | Main input to final package. | Consumed, audited, normalized, and repaired in current files. | 5 |
| 13 | User requested final downloadable report package. | Specified exact files, stable IDs, YAML schema, registers, audit, manifest, ZIP, and final response format. | Current task converts handoff into reusable per-chat package. | Directly controls current output. | 5 |

## 7. Decisions

| ID | Decision | Status | Evidence / basis | Rationale | Implications | Related workstream | Confidence | Label |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| DECISION-01 | PC is the first primary platform family for Dominium. | decided by explicit user wording | User: “Android, iOS, and Web will be our primary focus after PC...” | The phrase “after PC” establishes PC as the preceding primary focus. | Windows, macOS, and Linux need first-class planning before or alongside other Tier-0 contracts. | WORKSTREAM-01; WORKSTREAM-02 | 5 | FACT |
| DECISION-02 | Android is primary top-tier support after PC. | decided by explicit user statement | User: “Android... will be our primary focus after PC, and should be primary top tier support likewise.” | User explicitly elevated Android. | Android lifecycle, memory, touch/controller input, ABI, graphics, packaging, and QA must shape architecture early. | WORKSTREAM-01; WORKSTREAM-03; WORKSTREAM-10 | 5 | FACT |
| DECISION-03 | iOS is primary top-tier support after PC. | decided by explicit user statement | User: “iOS... will be our primary focus after PC, and should be primary top tier support likewise.” | User explicitly elevated iOS. | iOS and likely iPadOS must be first-class mobile targets, not ports. | WORKSTREAM-01; WORKSTREAM-04; WORKSTREAM-10 | 5 | FACT |
| DECISION-04 | Web is primary top-tier support after PC. | decided by explicit user statement | User: “Web will be our primary focus after PC, and should be primary top tier support likewise.” | User explicitly elevated Web. | WASM/browser constraints must be architectural drivers, not afterthoughts. | WORKSTREAM-01; WORKSTREAM-05; WORKSTREAM-10 | 5 | FACT |
| DECISION-05 | Mobile and Web should be treated as co-equal roots with PC, not late ports. | inferred working decision based on explicit user priority and prior assistant framing | Latest user priority plus assistant statement: “Mobile and Web are not ‘ports.’ They are co-equal roots with PC.” | Top-tier support cannot be credible if mobile/web constraints are deferred until after PC-only design. | Core systems must account for touch, suspend/resume, browser sandboxing, memory limits, variable refresh, and asset size from the beginning. | WORKSTREAM-01; WORKSTREAM-03; WORKSTREAM-04; WORKSTREAM-05; WORKSTREAM-10 | 4 | INFERENCE |
| DECISION-06 | Closed commercial consoles are secondary/gated support targets, not current Tier-0. | assistant-proposed working classification; not explicitly accepted or rejected | Assistant classified PS4/PS5, Xbox One/Series, and Switch as Tier-1/gated; user then elevated Android/iOS/Web after PC without elevating consoles. | Console SDKs, devkits, partner programs, certification, and distribution are gated by platform holders. | Console planning should not block Tier-0 PC/mobile/web. Console-specific code should be isolated. | WORKSTREAM-01; WORKSTREAM-06 | 4 | INFERENCE |
| DECISION-07 | Legacy consoles and retro systems are constrained/research/engine-only targets by default, not full Dominium parity targets. | assistant-proposed working classification | Assistant classified PS1/PS2/PS3/PSP/Vita, original Xbox/360, pre-Switch Nintendo, and retro OSes as Class C/Tier-2 constrained/research. | Severe hardware limits, obsolete/restricted tooling, and BIOS/firmware/legal constraints make parity support unrealistic by default. | Legacy support should be explicitly scoped as research, demo, emulator-hosted, community, or unsupported. | WORKSTREAM-06; WORKSTREAM-09 | 4 | INFERENCE |
| DECISION-08 | PC handhelds should map primarily to PC OS targets rather than become separate base platform families. | assistant-proposed working classification | Assistant classified Steam Deck as SteamOS/Linux, Windows handhelds as Windows, and Linux handhelds as Linux. | Most listed PC handhelds run Windows/Linux/SteamOS and can share PC builds plus handheld-specific QA. | Support matrix should include handheld profiles under PC, with controller/UI/performance requirements. | WORKSTREAM-02; WORKSTREAM-07 | 4 | INFERENCE |
| DECISION-09 | Web/WASM is both a universal fallback and a Tier-0 support target. | decided/inferred from latest user priority | Assistant previously called Web/WASM universal fallback; user later promoted Web to primary top-tier. | Web reaches many device classes without console-style platform gatekeeping, but latest priority means it must not be demoted to demo/fallback only. | Web build should have formal parity/degradation rules and browser QA. | WORKSTREAM-05 | 5 | FACT / INFERENCE |
| DECISION-10 | Use platform contracts/support matrix rather than an undifferentiated “support everything” claim. | assistant-proposed; strongly implied by scope | Assistant repeatedly proposed platform contracts and tiering; user requested many devices and later report normalization. | Device breadth is too large to manage without explicit support levels. | Future planning should use formal rows/columns for target, tier, scope, APIs, QA, and verification. | WORKSTREAM-01; WORKSTREAM-10 | 5 | INFERENCE |
| DECISION-11 | Closed console support must use official platform-holder paths for commercial/native support. | assistant-proposed constraint requiring external verification | Assistant stated PlayStation, Xbox, and Nintendo support require partner programs/devkits/SDKs/certification. | Commercial console development is generally gated by platform-holder processes. | Do not plan commercial console ports around unofficial tooling or public reverse-engineered details. | WORKSTREAM-06 | 4 | UNCERTAIN / UNVERIFIED |
| DECISION-12 | Do not bundle proprietary BIOS/firmware or rely on firmware redistribution for legacy support. | assistant-proposed legal/safety constraint | Assistant warned not to ship copyrighted BIOS/firmware for legacy/emulated targets. | Firmware/BIOS redistribution may violate IP rights unless licensed. | Legacy/emulated strategies must support user-provided/legal system software or avoid requiring it. | WORKSTREAM-06; WORKSTREAM-09 | 4 | INFERENCE |
| DECISION-13 | A platform abstraction layer and backend strategy are needed. | assistant-proposed architectural conclusion | Assistant proposed one portable core with host layers for window/input/audio/filesystem/network and render backends. | The platform matrix spans PC, mobile, web, consoles, handhelds, and XR. | Architecture must isolate platform differences and avoid PC-only assumptions. | WORKSTREAM-10 | 5 | INFERENCE |
| DECISION-14 | XR should be runtime-first via OpenXR/WebXR if pursued. | assistant-proposed; not user-confirmed | Assistant proposed OpenXR as primary XR abstraction and WebXR as browser complement. | Targeting runtimes reduces device-specific fragmentation. | XR devices should map through runtime support rather than every headset being a separate primary platform. | WORKSTREAM-08 | 3 | INFERENCE |
| DECISION-15 | The prior “Dominium full product vs Domino engine/core” split is unconfirmed. | not decided; naming flagged as uncertain | Assistant introduced “Domino” as engine core/reduced mode; user did not confirm the name. | Useful architectural split, but assistant-introduced names should not become project decisions without user acceptance. | New chats should say “engine/core” unless the user confirms “Domino.” | WORKSTREAM-09; WORKSTREAM-10 | 5 | UNCERTAIN / UNVERIFIED |
| DECISION-16 | This report package uses chat-only scope, normalized IDs, and the 2026-05-27 Australia/Melbourne date anchor. | decided by current user instruction | Current user prompt explicitly provided source scope, ID pattern, file set, and date anchor. | Enables future aggregation across many old-chat packages. | The package should not silently import whole-project memories or unverified external facts. | WORKSTREAM-11 | 5 | FACT |

### Highest-Impact Decisions

The highest-impact decision is DECISION-01 through DECISION-04 together: PC, Android, iOS, and Web are the primary Tier-0 platform set. DECISION-05 follows as an architectural implication: mobile and Web cannot be treated as late ports. DECISION-10 is the planning mechanism required by the breadth of the user’s target list: a platform support matrix and platform contracts. DECISION-06 and DECISION-07 are lower-authority assistant classifications, not explicit user decisions, but they are important for scope control: consoles are gated secondary targets by default, while legacy systems are constrained/research by default.

## 8. Pending Tasks and Next Actions

| ID | Task | Priority | Urgency | Owner | Dependencies | Inputs needed | Expected output | Recommended next step | Related workstream | Label |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| TASK-01 | Create a formal Platform Support Matrix for Dominium. | highest | high | future assistant / project owner | DECISION-01; DECISION-02; DECISION-03; DECISION-04; DECISION-10 | User target list; Tier model; Current verification data | Matrix of platform family, targets, tier, scope, OS/API, CPU/ABI, graphics, input, storage, networking, distribution, QA, legal constraints, risks, verification status, next action. | Start with Tier-0 rows: PC, Android, iOS/iPadOS, Web. | WORKSTREAM-01 | INFERENCE |
| TASK-02 | Define Tier-0 platform contracts. | highest | high | project owner / future assistant | TASK-01 | Definition of support levels; Platform baselines | Contract per Tier-0 family defining parity, allowed degradation, test requirements, and release obligations. | Draft contracts with unknowns explicitly marked. | WORKSTREAM-01; WORKSTREAM-10 | INFERENCE |
| TASK-03 | Define PC OS baselines. | high | medium | project owner | TASK-01 | Windows/macOS/Linux support goals; Current OS/API facts | Windows, macOS, Linux baseline table including architecture, graphics, packaging, and QA targets. | Decide Windows 10/11, macOS Apple Silicon/Intel, Linux distro/runtime assumptions. | WORKSTREAM-02 | INFERENCE |
| TASK-04 | Define Android minimum API, ABI, graphics, and subdevice scope. | highest | high | project owner | TASK-01; TASK-02 | Android SDK/NDK facts; Device-class priorities | Android support contract including phones/tablets, TV/handhelds, Automotive, Go, Chromebooks, vendor ROMs. | Verify current Android/Google Play requirements and choose baseline. | WORKSTREAM-03 | INFERENCE |
| TASK-05 | Define iOS/iPadOS minimum OS/device baseline and Apple-family classification. | highest | high | project owner | TASK-01; TASK-02 | Apple SDK/App Store facts; Apple platform priorities | Apple mobile/desktop classification table: iOS, iPadOS, macOS, tvOS, watchOS, visionOS if relevant. | Verify current Apple requirements and classify tvOS/watchOS/visionOS. | WORKSTREAM-04 | INFERENCE |
| TASK-06 | Define Web/WASM/browser/PWA baseline. | highest | high | project owner | TASK-01; TASK-02 | Browser support goals; WASM feature needs; Graphics policy | Web support contract covering browser minimums, WASM features, WebGPU/WebGL, PWA/offline, storage, and QA. | Decide whether WebGPU is required and WebGL fallback mandatory. | WORKSTREAM-05 | INFERENCE |
| TASK-07 | Create PC handheld profile. | high | medium | project owner | TASK-03; TASK-15 | Steam Deck priority; Windows/Linux handheld list; UX/performance targets | Handheld profile for Steam Deck, Windows handhelds, Linux handhelds, controller UI, performance and suspend/resume requirements. | Decide whether Steam Deck is an explicit Tier-0 subtarget. | WORKSTREAM-07 | INFERENCE |
| TASK-08 | Define console Tier-1 strategy. | medium-high | medium | project owner | TASK-01; VERIFY-01 | Platform-holder access status; Current console generation priorities | Console submatrix for PlayStation, Xbox, Nintendo: current commercial, cross-gen, legacy, remote-play, research, unsupported. | Verify official partner/development requirements from current sources. | WORKSTREAM-06 | INFERENCE |
| TASK-09 | Define legacy/retro target policy. | medium | low | project owner | TASK-01 | User appetite for retro work; Legal/toolchain constraints | Policy for engine-only demos, emulator-hosted support, community ports, and unsupported legacy targets. | Keep legacy targets Tier-2/research unless user elevates them. | WORKSTREAM-09 | INFERENCE |
| TASK-10 | Decide XR priority and runtime strategy. | medium | low | project owner | TASK-01; TASK-14 | XR product goals; OpenXR/WebXR feasibility | XR classification: future, Tier-2, Tier-1, or Tier-0; runtime targets and device mappings. | Do not elevate XR without explicit product decision. | WORKSTREAM-08 | INFERENCE |
| TASK-11 | Choose or confirm engine/toolchain strategy. | highest | high | project owner | TASK-01 | Custom engine vs Unity vs Unreal vs SDL/GLFW preference; Rendering/input/platform needs | Architecture decision record for engine/toolchain. | Ask/decide only when continuing implementation planning; do not infer from current chat. | WORKSTREAM-10 | UNCERTAIN / UNVERIFIED |
| TASK-12 | Confirm or retire the “Domino” engine/core name. | medium | low | user / project owner |  | User naming preference | Confirmed engine/core naming or instruction to avoid “Domino.” | Treat as unconfirmed until user states otherwise. | WORKSTREAM-09; WORKSTREAM-10 | UNCERTAIN / UNVERIFIED |
| TASK-13 | Design platform abstraction layer. | highest | high | engineering / future assistant | TASK-01; TASK-11 | Platform contracts; Engine/toolchain decision | Host-layer architecture for windowing, input, audio, filesystem/storage, networking, lifecycle, and build integration. | Use Tier-0 constraints as non-negotiable inputs. | WORKSTREAM-10 | INFERENCE |
| TASK-14 | Define rendering backend policy. | highest | high | engineering / project owner | TASK-01; TASK-11 | Graphics targets; Browser/mobile/console requirements | Renderer policy for Vulkan/Metal/WebGPU/WebGL/GLES/OpenGL/DirectX as applicable. | Verify backend feasibility and avoid treating assistant proposal as final. | WORKSTREAM-10 | INFERENCE |
| TASK-15 | Define input and UI strategy across desktop, touch, controller, TV, handheld, and browser. | highest | high | design / engineering | TASK-01 | Supported device classes; UX priorities | Input/UI contract for mouse/keyboard, touch, gamepad, TV remote if relevant, XR controllers if relevant. | Design touch/controller-first requirements before locking UI framework. | WORKSTREAM-03; WORKSTREAM-04; WORKSTREAM-05; WORKSTREAM-07; WORKSTREAM-10 | INFERENCE |
| TASK-16 | Define save/storage/sync model across native, mobile, and Web. | high | medium | engineering / product owner | TASK-01; TASK-05; TASK-06 | Persistence requirements; Offline/cloud goals; Browser/mobile sandbox constraints | Storage/save contract and migration/sync strategy. | Separate local saves, browser storage, mobile sandboxing, and optional cloud sync. | WORKSTREAM-03; WORKSTREAM-04; WORKSTREAM-05; WORKSTREAM-10 | INFERENCE |
| TASK-17 | Define QA and release cadence by tier. | high | medium | project owner / QA | TASK-01; TASK-02 | Tier definitions; Release priorities | QA obligations and release cadence for Tier-0, Tier-1, Tier-2. | Determine whether PC+Android+iOS+Web ship simultaneously or in synchronized windows. | WORKSTREAM-01; WORKSTREAM-07 | INFERENCE |
| TASK-18 | Verify all external-world platform facts with current official sources. | highest | high before implementation | future assistant / project owner |  | Official platform docs; Current SDK/store/browser data | Verified source-backed platform fact sheet replacing unverified assistant claims. | Use official sources for Android, Apple, browser, console, SteamOS, XR, and SDK facts. | WORKSTREAM-01; WORKSTREAM-03; WORKSTREAM-04; WORKSTREAM-05; WORKSTREAM-06; WORKSTREAM-08; WORKSTREAM-09; WORKSTREAM-10 | FACT / INFERENCE |
| TASK-19 | Use this package in later cross-chat aggregation and Project Spec Book construction. | high | when aggregating | future aggregator assistant / user | ARTIFACT-13 | This package; Other old-chat packages | Merged master spec book, master living state file, conflict register, deduplication register, master task/decision/artifact registers. | Store package in its own folder and feed the ZIP or key files into aggregator chat later. | WORKSTREAM-11 | FACT / INFERENCE |

### 8.1 Recommended Task Order

- TASK-01: Create formal Platform Support Matrix.
- TASK-02: Define Tier-0 platform contracts.
- TASK-03/TASK-04/TASK-05/TASK-06: Define PC, Android, iOS/iPadOS, and Web baselines.
- TASK-11: Choose/confirm engine/toolchain.
- TASK-13/TASK-14/TASK-15/TASK-16: Define platform abstraction, rendering, input/UI, and storage/save architecture.
- TASK-17: Define QA/release cadence.
- TASK-08/TASK-09/TASK-10: Classify consoles, legacy targets, and XR after Tier-0 baseline.
- TASK-18: Verify all external platform facts before implementation.

### 8.2 Blocked Tasks

- TASK-04 is blocked by Android API/ABI/device-class decisions and current policy verification.
- TASK-05 is blocked by current Apple SDK/App Store facts and Apple subplatform decisions.
- TASK-06 is blocked by browser/WebGPU/WebGL/WASM feature decisions.
- TASK-08 is blocked by official console access status and current platform-holder rules.
- TASK-11 is blocked by absence of a visible engine/toolchain decision.

### 8.3 Quick Wins

- Create the initial matrix with unknown fields marked rather than waiting for all facts.
- Confirm whether iPadOS is explicitly bundled with iOS Tier-0.
- Confirm whether “Domino” should be used or discarded.
- Classify Apple Watch/watchOS, Android Automotive, and PlayStation Portal as pending/secondary unless elevated.
- Replace prior citation IDs with a verification queue instead of attempting to preserve them.

### 8.4 Tasks Requiring Verification

- TASK-03
- TASK-04
- TASK-05
- TASK-06
- TASK-08
- TASK-10
- TASK-14
- TASK-18

## 9. Constraints and Requirements

### 9.1 Hard Requirements

| ID | Constraint | Type | Source / basis | Implication | Violation risk | Label |
| --- | --- | --- | --- | --- | --- | --- |
| CONSTRAINT-01 | Direct user statements outrank assistant suggestions. | source hierarchy | Current user prompt and previous Context Transfer Packet rules. | Do not treat assistant-proposed platform tiers or names as user decisions unless accepted. | high | FACT |
| CONSTRAINT-02 | Important items must be labeled FACT, INFERENCE, UNCERTAIN / UNVERIFIED, or PROJECT-CONTEXT. | epistemic | Current user prompt. | Registers and prose must preserve uncertainty and source type. | high | FACT |
| CONSTRAINT-03 | Do not invent facts or silently infer. | epistemic | Current user prompt. | Unknown platform details must remain unknown until verified. | high | FACT |
| CONSTRAINT-04 | Do not turn brainstorms into decisions. | decision integrity | Current user prompt. | Earlier assistant lists and proposals must remain tentative unless user confirmed them. | high | FACT |
| CONSTRAINT-05 | Use 2026-05-27 Australia/Melbourne as date anchor. | metadata | Current user prompt. | Reports and verification should use that date anchor, not any earlier date in the previous packet. | medium | FACT |
| CONSTRAINT-06 | Source scope is this chat only unless external context is explicitly labeled PROJECT-CONTEXT. | scope | Current user prompt. | Do not import memories, file-library content, or whole-project assumptions silently. | high | FACT |
| CONSTRAINT-07 | PC, Android, iOS, and Web are primary top-tier support. | product priority | Latest explicit user platform decision. | These targets must drive architecture, QA, and release planning. | high | FACT |
| CONSTRAINT-08 | Mobile and Web cannot be treated as afterthought ports. | architecture/product | Latest user priority plus assistant's accepted framing in previous reply. | Touch, lifecycle, browser sandbox, memory, and asset constraints must be designed early. | high | INFERENCE |
| CONSTRAINT-09 | Do not plan to redistribute proprietary BIOS/firmware for legacy or emulated targets. | legal/IP | Assistant constraint in prior context packet. | Legacy/emulator support must avoid bundled proprietary system software unless licensed. | high | INFERENCE |
| CONSTRAINT-10 | Commercial closed-console support requires official platform-holder access. | legal/commercial/technical | Prior assistant classification; external details unverified. | PlayStation/Xbox/Nintendo support cannot be promised as native commercial builds without partner/devkit/certification path. | high | UNCERTAIN / UNVERIFIED |
| CONSTRAINT-12 | External-world platform facts require current verification before future use. | evidence/staleness | Current user prompt and platform volatility. | SDK, store, console, browser, device, and OS claims must be checked against current official sources. | high | FACT |
| CONSTRAINT-13 | Preserve visible rationale and assumptions but do not reveal hidden chain-of-thought. | reasoning/output | Current user prompt. | Report may explain why decisions were made using visible conversation only. | high | FACT |
| CONSTRAINT-14 | Create the exact requested file set if file generation is available. | output/file | Current user prompt. | Generate full report, YAML spec sheet, aggregator packet, registers, reader brief, verification/audit, manifest, and ZIP if possible. | medium | FACT |
| CONSTRAINT-15 | Normalize important items into stable IDs. | format/aggregation | Current user prompt. | Use WORKSTREAM, DECISION, TASK, CONSTRAINT, QUESTION, ARTIFACT, RISK, REJECTED, VERIFY IDs. | medium | FACT |
| CONSTRAINT-16 | Do not claim files were saved unless downloadable files were actually created. | truthfulness/output | Current user prompt. | Final response must only list real files created in sandbox. | high | FACT |
| CONSTRAINT-17 | Rejected, superseded, and deprioritized options must be preserved. | state preservation | Current and previous user prompts. | Include rejected options to avoid future repeated work. | medium | FACT |
| CONSTRAINT-18 | Cross-platform input, UI, lifecycle, memory, and asset constraints must be explicit. | technical | Prior assistant architecture consequences and latest user priority. | Platform contracts must include touch, gamepad, suspend/resume, low-memory, and browser/mobile constraints. | high | INFERENCE |
| CONSTRAINT-19 | Console-specific restricted material should be isolated and not leaked into open/public code. | legal/process | Prior assistant console strategy. | NDA-bound SDK headers/docs/libraries must not enter unrestricted repos or public artifacts. | high | INFERENCE |
| CONSTRAINT-20 | Prior non-portable citations and assistant claims are not sufficient verification. | evidence | Previous packet’s audit and current prompt’s verification requirement. | Do not rely on earlier turn citation IDs; rebuild citations from official current sources later. | medium | FACT |

### 9.2 Soft Preferences

| ID | Constraint | Type | Source / basis | Implication | Violation risk | Label |
| --- | --- | --- | --- | --- | --- | --- |
| CONSTRAINT-11 | Legacy consoles and retro OSes are not parity targets by default. | scope/technical | Prior assistant classification. | Classify them as research, engine-only, reduced, emulator-hosted, or unsupported unless user elevates them. | high | INFERENCE |

### 9.3 Technical Constraints

| ID | Constraint | Type | Source / basis | Implication | Violation risk | Label |
| --- | --- | --- | --- | --- | --- | --- |
| CONSTRAINT-08 | Mobile and Web cannot be treated as afterthought ports. | architecture/product | Latest user priority plus assistant's accepted framing in previous reply. | Touch, lifecycle, browser sandbox, memory, and asset constraints must be designed early. | high | INFERENCE |
| CONSTRAINT-11 | Legacy consoles and retro OSes are not parity targets by default. | scope/technical | Prior assistant classification. | Classify them as research, engine-only, reduced, emulator-hosted, or unsupported unless user elevates them. | high | INFERENCE |
| CONSTRAINT-18 | Cross-platform input, UI, lifecycle, memory, and asset constraints must be explicit. | technical | Prior assistant architecture consequences and latest user priority. | Platform contracts must include touch, gamepad, suspend/resume, low-memory, and browser/mobile constraints. | high | INFERENCE |

### 9.4 Time / Resource Constraints

No concrete schedule, budget, team size, or implementation resources were established in this chat. FACT: The only time anchor for this package is 2026-05-27 Australia/Melbourne. INFERENCE: Resource risk is high because the user’s target list is extremely broad.

### 9.5 Legal / Ethical / Safety Constraints

| ID | Constraint | Type | Source / basis | Implication | Violation risk | Label |
| --- | --- | --- | --- | --- | --- | --- |
| CONSTRAINT-09 | Do not plan to redistribute proprietary BIOS/firmware for legacy or emulated targets. | legal/IP | Assistant constraint in prior context packet. | Legacy/emulator support must avoid bundled proprietary system software unless licensed. | high | INFERENCE |
| CONSTRAINT-10 | Commercial closed-console support requires official platform-holder access. | legal/commercial/technical | Prior assistant classification; external details unverified. | PlayStation/Xbox/Nintendo support cannot be promised as native commercial builds without partner/devkit/certification path. | high | UNCERTAIN / UNVERIFIED |
| CONSTRAINT-19 | Console-specific restricted material should be isolated and not leaked into open/public code. | legal/process | Prior assistant console strategy. | NDA-bound SDK headers/docs/libraries must not enter unrestricted repos or public artifacts. | high | INFERENCE |

### 9.6 Evidence / Citation Requirements

| ID | Constraint | Type | Source / basis | Implication | Violation risk | Label |
| --- | --- | --- | --- | --- | --- | --- |
| CONSTRAINT-01 | Direct user statements outrank assistant suggestions. | source hierarchy | Current user prompt and previous Context Transfer Packet rules. | Do not treat assistant-proposed platform tiers or names as user decisions unless accepted. | high | FACT |
| CONSTRAINT-02 | Important items must be labeled FACT, INFERENCE, UNCERTAIN / UNVERIFIED, or PROJECT-CONTEXT. | epistemic | Current user prompt. | Registers and prose must preserve uncertainty and source type. | high | FACT |
| CONSTRAINT-03 | Do not invent facts or silently infer. | epistemic | Current user prompt. | Unknown platform details must remain unknown until verified. | high | FACT |
| CONSTRAINT-06 | Source scope is this chat only unless external context is explicitly labeled PROJECT-CONTEXT. | scope | Current user prompt. | Do not import memories, file-library content, or whole-project assumptions silently. | high | FACT |
| CONSTRAINT-12 | External-world platform facts require current verification before future use. | evidence/staleness | Current user prompt and platform volatility. | SDK, store, console, browser, device, and OS claims must be checked against current official sources. | high | FACT |
| CONSTRAINT-20 | Prior non-portable citations and assistant claims are not sufficient verification. | evidence | Previous packet’s audit and current prompt’s verification requirement. | Do not rely on earlier turn citation IDs; rebuild citations from official current sources later. | medium | FACT |

### 9.7 Formatting / Output Requirements

| ID | Constraint | Type | Source / basis | Implication | Violation risk | Label |
| --- | --- | --- | --- | --- | --- | --- |
| CONSTRAINT-05 | Use 2026-05-27 Australia/Melbourne as date anchor. | metadata | Current user prompt. | Reports and verification should use that date anchor, not any earlier date in the previous packet. | medium | FACT |
| CONSTRAINT-14 | Create the exact requested file set if file generation is available. | output/file | Current user prompt. | Generate full report, YAML spec sheet, aggregator packet, registers, reader brief, verification/audit, manifest, and ZIP if possible. | medium | FACT |
| CONSTRAINT-15 | Normalize important items into stable IDs. | format/aggregation | Current user prompt. | Use WORKSTREAM, DECISION, TASK, CONSTRAINT, QUESTION, ARTIFACT, RISK, REJECTED, VERIFY IDs. | medium | FACT |

### 9.8 Things to Avoid

- Do not treat assistant-generated platform proposals as user decisions.
- Do not demote Android/iOS/Web to late ports.
- Do not claim literal support for every listed historical device.
- Do not rely on prior non-portable citation IDs.
- Do not assume “Domino” is confirmed.
- Do not bundle or advise redistribution of proprietary BIOS/firmware.
- Do not use console homebrew/modding as a commercial support path.
- Do not merge this chat with project-wide context without preserving provenance.

### Full Constraint Register

| ID | Constraint | Type | Hard/soft | Source / basis | Practical implication | Violation risk | Confidence | Label |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| CONSTRAINT-01 | Direct user statements outrank assistant suggestions. | source hierarchy | hard | Current user prompt and previous Context Transfer Packet rules. | Do not treat assistant-proposed platform tiers or names as user decisions unless accepted. | high | 5 | FACT |
| CONSTRAINT-02 | Important items must be labeled FACT, INFERENCE, UNCERTAIN / UNVERIFIED, or PROJECT-CONTEXT. | epistemic | hard | Current user prompt. | Registers and prose must preserve uncertainty and source type. | high | 5 | FACT |
| CONSTRAINT-03 | Do not invent facts or silently infer. | epistemic | hard | Current user prompt. | Unknown platform details must remain unknown until verified. | high | 5 | FACT |
| CONSTRAINT-04 | Do not turn brainstorms into decisions. | decision integrity | hard | Current user prompt. | Earlier assistant lists and proposals must remain tentative unless user confirmed them. | high | 5 | FACT |
| CONSTRAINT-05 | Use 2026-05-27 Australia/Melbourne as date anchor. | metadata | hard | Current user prompt. | Reports and verification should use that date anchor, not any earlier date in the previous packet. | medium | 5 | FACT |
| CONSTRAINT-06 | Source scope is this chat only unless external context is explicitly labeled PROJECT-CONTEXT. | scope | hard | Current user prompt. | Do not import memories, file-library content, or whole-project assumptions silently. | high | 5 | FACT |
| CONSTRAINT-07 | PC, Android, iOS, and Web are primary top-tier support. | product priority | hard unless user changes it | Latest explicit user platform decision. | These targets must drive architecture, QA, and release planning. | high | 5 | FACT |
| CONSTRAINT-08 | Mobile and Web cannot be treated as afterthought ports. | architecture/product | hard by implication | Latest user priority plus assistant's accepted framing in previous reply. | Touch, lifecycle, browser sandbox, memory, and asset constraints must be designed early. | high | 4 | INFERENCE |
| CONSTRAINT-09 | Do not plan to redistribute proprietary BIOS/firmware for legacy or emulated targets. | legal/IP | hard pending legal review | Assistant constraint in prior context packet. | Legacy/emulator support must avoid bundled proprietary system software unless licensed. | high | 4 | INFERENCE |
| CONSTRAINT-10 | Commercial closed-console support requires official platform-holder access. | legal/commercial/technical | hard pending verification | Prior assistant classification; external details unverified. | PlayStation/Xbox/Nintendo support cannot be promised as native commercial builds without partner/devkit/certification path. | high | 4 | UNCERTAIN / UNVERIFIED |
| CONSTRAINT-11 | Legacy consoles and retro OSes are not parity targets by default. | scope/technical | soft-to-hard working guardrail | Prior assistant classification. | Classify them as research, engine-only, reduced, emulator-hosted, or unsupported unless user elevates them. | high | 4 | INFERENCE |
| CONSTRAINT-12 | External-world platform facts require current verification before future use. | evidence/staleness | hard | Current user prompt and platform volatility. | SDK, store, console, browser, device, and OS claims must be checked against current official sources. | high | 5 | FACT |
| CONSTRAINT-13 | Preserve visible rationale and assumptions but do not reveal hidden chain-of-thought. | reasoning/output | hard | Current user prompt. | Report may explain why decisions were made using visible conversation only. | high | 5 | FACT |
| CONSTRAINT-14 | Create the exact requested file set if file generation is available. | output/file | hard for current task | Current user prompt. | Generate full report, YAML spec sheet, aggregator packet, registers, reader brief, verification/audit, manifest, and ZIP if possible. | medium | 5 | FACT |
| CONSTRAINT-15 | Normalize important items into stable IDs. | format/aggregation | hard | Current user prompt. | Use WORKSTREAM, DECISION, TASK, CONSTRAINT, QUESTION, ARTIFACT, RISK, REJECTED, VERIFY IDs. | medium | 5 | FACT |
| CONSTRAINT-16 | Do not claim files were saved unless downloadable files were actually created. | truthfulness/output | hard | Current user prompt. | Final response must only list real files created in sandbox. | high | 5 | FACT |
| CONSTRAINT-17 | Rejected, superseded, and deprioritized options must be preserved. | state preservation | hard | Current and previous user prompts. | Include rejected options to avoid future repeated work. | medium | 5 | FACT |
| CONSTRAINT-18 | Cross-platform input, UI, lifecycle, memory, and asset constraints must be explicit. | technical | hard by implication for Tier-0 | Prior assistant architecture consequences and latest user priority. | Platform contracts must include touch, gamepad, suspend/resume, low-memory, and browser/mobile constraints. | high | 4 | INFERENCE |
| CONSTRAINT-19 | Console-specific restricted material should be isolated and not leaked into open/public code. | legal/process | hard if console development proceeds | Prior assistant console strategy. | NDA-bound SDK headers/docs/libraries must not enter unrestricted repos or public artifacts. | high | 4 | INFERENCE |
| CONSTRAINT-20 | Prior non-portable citations and assistant claims are not sufficient verification. | evidence | hard | Previous packet’s audit and current prompt’s verification requirement. | Do not rely on earlier turn citation IDs; rebuild citations from official current sources later. | medium | 5 | FACT |

## 10. Open Questions and Unresolved Issues

| ID | Question / issue | Why it matters | Known information | Unknown information | What would resolve it | Priority | Related workstream | Label |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| QUESTION-01 | What exact target families are Tier-0 besides PC, Android, iOS, and Web? | Tier-0 determines architecture, QA, release cadence, and support obligations. | PC, Android, iOS, and Web are primary top-tier by latest user statement. | Whether iPadOS, Android TV, tvOS, Steam Deck, or other subfamilies are formally Tier-0. | User/project decision during platform matrix construction. | highest | WORKSTREAM-01 | FACT / INFERENCE |
| QUESTION-02 | What minimum Android API level and ABI set will be supported? | Affects engine, NDK, graphics, store compliance, device reach, and QA. | Android is Tier-0; arm64-v8a was earlier proposed but not verified/final. | API level, ABI list, Vulkan/GLES requirements, Android Go support. | Verify current Android/Google Play requirements and choose product baseline. | highest | WORKSTREAM-03 | UNCERTAIN / UNVERIFIED |
| QUESTION-03 | What minimum iOS/iPadOS version and device generations will be supported? | Affects Apple SDK, App Store submission, Metal support, memory/performance budgets. | iOS is Tier-0; iPadOS was included by assistant as likely co-target. | Minimum iOS/iPadOS version, supported iPhone/iPad generations, iPod Touch treatment. | Verify Apple current requirements and choose baseline. | highest | WORKSTREAM-04 | UNCERTAIN / UNVERIFIED |
| QUESTION-04 | What is the Web/browser baseline? | Affects WASM features, memory, threading, WebGPU/WebGL, PWA support, and testing. | Web is Tier-0; user listed major browsers. | Minimum browser versions, required browser APIs, Safari constraints. | Verify current browser support and define matrix. | highest | WORKSTREAM-05 | UNCERTAIN / UNVERIFIED |
| QUESTION-05 | Is WebGPU required, preferred, or optional, and is WebGL fallback mandatory? | Determines renderer architecture and browser reach. | Assistant proposed WebGPU primary and WebGL fallback; user listed both. | Final graphics policy. | Architecture decision after verifying browser support and performance needs. | highest | WORKSTREAM-05; WORKSTREAM-10 | UNCERTAIN / UNVERIFIED |
| QUESTION-06 | Which Windows versions and CPU architectures are supported? | Defines PC compatibility and build targets. | Assistant previously proposed Windows 10/11 x64 and optional ARM64. | Whether Windows 10 is required, whether Windows 11 only, whether ARM64 is in scope. | Project decision plus current toolchain verification. | high | WORKSTREAM-02 | UNCERTAIN / UNVERIFIED |
| QUESTION-07 | Which macOS versions and Mac architectures are supported? | Affects Apple Silicon/Intel builds, Metal version, packaging, and QA. | Assistant previously proposed Apple Silicon primary and Intel optional; user listed Mac Intel and Apple Silicon. | Minimum macOS, Intel Mac support, Apple Silicon-only possibility. | Project decision plus Apple platform verification. | high | WORKSTREAM-02; WORKSTREAM-04 | UNCERTAIN / UNVERIFIED |
| QUESTION-08 | What Linux baseline is required? | Affects distro compatibility, glibc/musl, packaging, graphics, X11/Wayland, and Steam Deck. | Assistant proposed Linux x64/ARM64 and X11/Wayland; user listed Linux distros for handhelds. | Distros, package formats, runtime targets, ARM64 status. | Define Linux support contract and verify current ecosystem assumptions. | high | WORKSTREAM-02; WORKSTREAM-07 | UNCERTAIN / UNVERIFIED |
| QUESTION-09 | Are Android TV / Google TV first-class Tier-0 targets or secondary Android subtargets? | TV UX, remote/controller input, store compliance, and QA differ from phones/tablets. | User listed Android TV / Google TV devices and software. | Tier and feature scope. | User/project decision in Android submatrix. | medium-high | WORKSTREAM-03 | UNCERTAIN / UNVERIFIED |
| QUESTION-10 | Are tvOS, watchOS, and visionOS in scope, and at what tier? | Apple TV, Apple Watch, and Vision Pro require different UX/runtime assumptions than iPhone/iPad/Mac. | User listed Apple TV, Apple Watch, and Apple platform software; Apple Vision Pro appeared under AR. | Full support, companion-only, future XR, or unsupported status. | User/project decision after classifying Apple-family targets. | medium-high | WORKSTREAM-04; WORKSTREAM-08 | UNCERTAIN / UNVERIFIED |
| QUESTION-11 | What engine/toolchain will Dominium use? | All platform feasibility depends on custom engine vs Unity vs Unreal vs SDL/GLFW or another stack. | User listed cross-cutting runtimes/APIs; assistant proposed a portable core but did not confirm engine. | Actual engine/toolchain. | User/project architecture decision. | highest | WORKSTREAM-10 | UNCERTAIN / UNVERIFIED |
| QUESTION-12 | Is “Domino” the real name for the engine/core layer? | Avoids naming drift and false project terminology. | Assistant introduced “Domino”; user did not confirm. | Whether to use, rename, or discard it. | User confirmation. | medium | WORKSTREAM-09; WORKSTREAM-10 | UNCERTAIN / UNVERIFIED |
| QUESTION-13 | Is Steam Deck a named Tier-0 subtarget? | Steam Deck support implies specific performance, controller, resolution, suspend/resume, and possibly Steam verification goals. | User listed Steam Deck LCD/OLED; assistant maps it to SteamOS/Linux PC. | Tier, QA, and distribution status. | Project decision in PC handheld submatrix. | medium-high | WORKSTREAM-07 | UNCERTAIN / UNVERIFIED |
| QUESTION-14 | Which current console generations are commercial targets? | Affects partner onboarding, devkit needs, certification, performance floors, and release planning. | User listed PS4/PS5, Xbox One/Series, Switch; assistant placed current consoles in Tier-1. | PS4 vs PS5, Xbox One vs Series, Switch vs successor-class priorities. | User/project decision after verifying official access. | medium-high | WORKSTREAM-06 | UNCERTAIN / UNVERIFIED |
| QUESTION-15 | Are any legacy consoles or retro OSes actual goals rather than aspirational coverage? | Legacy support can consume large effort and force feature reductions. | User listed many legacy consoles; assistant proposed research/constrained status. | Which legacy targets, if any, get real work. | User/project decision after Tier-0 matrix. | medium | WORKSTREAM-06; WORKSTREAM-09 | UNCERTAIN / UNVERIFIED |
| QUESTION-16 | What priority does XR have? | XR can require stereo rendering, low-latency frame pacing, comfort design, and different input models. | User listed AR/VR devices; assistant proposed OpenXR/WebXR runtime-first. | Future-only, Tier-2, Tier-1, or Tier-0. | User/product decision. | medium | WORKSTREAM-08 | UNCERTAIN / UNVERIFIED |
| QUESTION-17 | Should Tier-0 platforms ship simultaneously? | Release cadence affects build farm, QA, certification, store submission, and scope control. | Assistant proposed PC+Android+iOS+Web ship together; user did not explicitly confirm. | Actual release cadence. | Project release planning decision. | medium | WORKSTREAM-01; WORKSTREAM-07 | INFERENCE |
| QUESTION-18 | What are the QA obligations for each support tier? | Tier names are meaningless without test and release obligations. | Assistant used terms like first-class, full QA, parity, constrained, research. | Concrete pass/fail criteria and device coverage. | Define tier contract document. | highest | WORKSTREAM-01 | INFERENCE |
| QUESTION-19 | What does “support” mean for each device family? | Prevents conflating full product, playable, engine-only, emulator-hosted, remote-play, or unsupported. | Prior packet recommended explicit categories. | Final category meanings and obligations. | Define support taxonomy before platform matrix. | highest | WORKSTREAM-01 | INFERENCE |
| QUESTION-20 | What is the final rendering backend policy? | Rendering drives platform reach and engine complexity. | User listed Vulkan, OpenGL/ES, DirectX, Metal, WebGL, WebGPU; assistant proposed Vulkan/Metal/WebGPU first with fallbacks. | Final API support and fallback obligations. | Architecture decision after platform baselines and verification. | highest | WORKSTREAM-10 | UNCERTAIN / UNVERIFIED |
| QUESTION-21 | What is the cross-platform input/UI model? | PC, mobile, TV, handheld, browser, console, and XR inputs differ substantially. | Assistant warned against PC-only assumptions. | Input devices, UI scaling, controller/touch-first rules. | UX/platform contract decision. | high | WORKSTREAM-10 | INFERENCE |
| QUESTION-22 | What is the save/storage/sync model across native, mobile, and web? | Storage APIs and sandboxing differ; future compatibility depends on early design. | Need storage abstraction was inferred; no concrete design exists. | Local saves, cloud sync, browser storage, file exports/imports, account system. | Architecture/product decision. | high | WORKSTREAM-05; WORKSTREAM-10 | UNCERTAIN / UNVERIFIED |
| QUESTION-23 | What distribution channels are targeted per Tier-0 platform? | Stores impose packaging, entitlement, review, and update constraints. | No distribution plan established; possible stores are implied by platforms. | Steam, Epic, itch, App Store, Play Store, direct web hosting, PWA install, etc. | Product/distribution planning. | medium-high | WORKSTREAM-01; WORKSTREAM-10 | UNCERTAIN / UNVERIFIED |
| QUESTION-24 | Which previous assistant claims require source re-verification? | The retired chat contained non-portable citations and current-fact claims. | The prior packet warned that citations and platform facts are not portable/current. | Which claims survive official-source verification. | Create verification pass using official sources. | highest | WORKSTREAM-01 | FACT / UNCERTAIN |
| QUESTION-25 | Is Android Automotive an actual target? | Automotive platforms differ legally, UX-wise, and operationally from normal Android game devices. | User listed Android Automotive head units and OS. | Support tier or rejection. | Classify separately in Android submatrix. | medium | WORKSTREAM-03 | UNCERTAIN / UNVERIFIED |
| QUESTION-26 | Is Apple Watch/watchOS full support, companion-only, or out of scope? | Full Dominium on watchOS is a radically different product scope from iOS/iPadOS. | User listed Apple Watch/watchOS. | Intended support meaning. | User/project decision in Apple-family classification. | medium | WORKSTREAM-04 | UNCERTAIN / UNVERIFIED |

## 11. Rejected, Superseded, or Deprioritised Options

| ID | Option | Status | Reason rejected/superseded/deprioritized | Is rejection final? | Reconsider conditions | Related workstream | Label |
| --- | --- | --- | --- | --- | --- | --- | --- |
| REJECTED-01 | Treat Android, iOS, and Web as secondary ports after PC. | superseded | User explicitly promoted Android, iOS, and Web to primary top-tier support after PC. | final unless user changes priority | Only if user explicitly demotes any of these targets. | WORKSTREAM-01; WORKSTREAM-03; WORKSTREAM-04; WORKSTREAM-05 | FACT |
| REJECTED-02 | Treat all console families as equal Tier-0 by default. | deprioritized | Latest priority explicitly names PC then Android/iOS/Web; assistant classified consoles as gated secondary targets. | tentative | If user elevates consoles or confirms official platform access and business priority. | WORKSTREAM-06 | INFERENCE |
| REJECTED-03 | Promise full Dominium parity on legacy consoles and old handhelds. | deprioritized/rejected by working model | Assistant classified legacy consoles as constrained/research due severe hardware, tooling, and legal limitations. | tentative but strongly recommended | If user commissions reduced product profiles or legally supported research ports. | WORKSTREAM-06; WORKSTREAM-09 | INFERENCE |
| REJECTED-04 | Bundle proprietary BIOS/firmware for old systems or emulators. | rejected | Legal/IP risk identified by assistant; no license established in this chat. | final unless rights are obtained | Only with explicit legal rights/licensing and separate legal review. | WORKSTREAM-06; WORKSTREAM-09 | INFERENCE |
| REJECTED-05 | Use console homebrew/modding paths as official commercial support strategy. | rejected for commercial support | Official console support should use platform-holder programs; homebrew/modding is not a credible commercial-native path in this planning context. | final for commercial product | Research/community discussion only, with legal boundaries and no bypass instructions. | WORKSTREAM-06 | INFERENCE |
| REJECTED-06 | Treat PlayStation Portal as a native compute target. | deprioritized/rejected by prior assistant classification | Assistant classified it as a remote-play client rather than a native Dominium platform. | tentative pending verification | If current official facts show native app/game execution capability or if streaming support is separately planned. | WORKSTREAM-06 | UNCERTAIN / UNVERIFIED |
| REJECTED-07 | Use the claim “supports everything” without tiers. | rejected | Too ambiguous for engineering, QA, legal, and future aggregation; support must be tiered and scoped. | final | Do not reconsider; use explicit tier/category language instead. | WORKSTREAM-01 | INFERENCE |
| REJECTED-08 | Design a PC-only architecture and later retrofit mobile/web. | rejected/superseded | Contradicts the user’s latest Tier-0 mobile/web priority. | final unless priority changes | Only if user explicitly changes product strategy. | WORKSTREAM-03; WORKSTREAM-04; WORKSTREAM-05; WORKSTREAM-10 | FACT / INFERENCE |
| REJECTED-09 | Rely on prior assistant citation IDs as source evidence in future chats. | rejected | Prior citations are non-portable and may be stale; current prompt requires verification of external facts. | final | Do not rely on them; rebuild source citations from official current sources. | WORKSTREAM-01 | FACT |
| REJECTED-10 | Treat “Domino” as a confirmed engine/core name. | rejected as a fact; retained as unconfirmed placeholder | Assistant introduced the name; user did not confirm it. | tentative | If user confirms or rejects the name. | WORKSTREAM-09; WORKSTREAM-10 | UNCERTAIN / UNVERIFIED |
| REJECTED-11 | Treat Web as only a demo or fallback rather than a primary product target. | superseded | User explicitly made Web primary top-tier after PC. | final unless user demotes Web. | Only if Web scope is explicitly reduced by user/project decision. | WORKSTREAM-05 | FACT |
| REJECTED-12 | Treat all Apple devices as equivalent Dominium targets. | deprioritized | User listed many Apple devices, but only iOS was explicitly promoted; macOS belongs to PC; tvOS/watchOS/visionOS remain unclassified. | tentative | Classify Apple TV, Apple Watch, and Vision Pro after platform-specific feasibility review. | WORKSTREAM-04; WORKSTREAM-08 | INFERENCE |
| REJECTED-13 | Interpret “iPhone all generations” literally as support for every iPhone ever released. | deprioritized as likely impractical | The user list included “all generations,” but no minimum OS/device baseline was chosen and platform support must be technically feasible. | tentative | If a separate legacy iOS compatibility policy is created, verified, and funded. | WORKSTREAM-04 | INFERENCE |
| REJECTED-14 | Make Wine/Proton a core contract instead of native Linux. | deprioritized by previous assistant response | Assistant framed Proton/Wine as nice-to-have while native Linux remains the contract. | tentative | If Steam Deck strategy changes or native Linux is not shipped. | WORKSTREAM-02; WORKSTREAM-07 | INFERENCE |

Preserving these items prevents future assistants from restarting old debates, accidentally reversing the user’s latest priority, or treating assistant brainstorms as accepted requirements.

## 12. Artifact Ledger

| ID | Artifact / file / prompt / output | Type | Purpose | Status | Where it came from | Carry forward? | Notes | Label |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| ARTIFACT-01 | User prompt: “So, in the end, what systems will we support?” | prompt | Started broad support-systems discussion. | preserved in report | visible user message in this chat | True | Broad origin of platform-support discussion. | FACT |
| ARTIFACT-02 | Assistant retro-heavy Tier 0/1/2 systems answer | assistant output | Proposed bare-metal/firmware, legacy OS, and classic GUI targets. | historical / partly superseded | visible assistant message | True | Do not treat as user decision; useful as rejected/deprioritized context. | FACT |
| ARTIFACT-03 | User prompt: “what operating systems will we be able to run Dominium on?” | prompt | Narrowed the discussion from systems to operating systems. | preserved | visible user message | True | Introduced explicit Dominium OS framing. | FACT |
| ARTIFACT-04 | Assistant Dominium full product vs Domino engine/core split | assistant output | Separated full product targets from reduced/engine-only legacy targets. | useful but unconfirmed naming | visible assistant message | True | “Domino” is assistant-introduced and must not be treated as confirmed. | UNCERTAIN / UNVERIFIED |
| ARTIFACT-05 | User prompt requesting support for PlayStation, Xbox, PC handhelds, Nintendo, Android, iOS, Web, etc. | prompt | Expanded scope to major device families. | preserved | visible user message | True | Led to family-level target planning. | FACT |
| ARTIFACT-06 | Assistant family-target answer with Web, PC handhelds, Android/iOS, and consoles | assistant output | Proposed top-level family support approach. | intermediate / partly superseded | visible assistant message | True | Contained count inconsistency: said roughly 8 top-level targets but listed 9. | FACT |
| ARTIFACT-07 | User comprehensive hardware/software target inventory | prompt / target list | Master list of PlayStation, Xbox, Nintendo, PC handheld, Android, Apple, Web, AR, VR, and cross-cutting runtimes/APIs. | central source artifact | visible user message | True | Conversation fact, not verified as current real-world truth. | FACT |
| ARTIFACT-08 | Assistant Class A/B/C/D classification output | assistant output / planning framework | Classified open platforms, closed consoles, legacy closed consoles, and emulated runtime; proposed OpenXR/WebXR for XR. | useful assistant proposal | visible assistant message | True | Lower trust than user decisions; requires current verification for external facts. | INFERENCE |
| ARTIFACT-09 | User prompt: “Android, iOS, and Web will be our primary focus after PC...” | prompt / decision statement | Promoted Android, iOS, and Web to primary top-tier support after PC. | highest-priority carry-forward artifact | visible user message | True | Controls current platform hierarchy. | FACT |
| ARTIFACT-10 | Assistant Tier-0 lock response | assistant output | Locked working hierarchy as PC + Android + iOS/iPadOS + Web Tier-0, consoles Tier-1, legacy Tier-2. | current working assistant synthesis | visible assistant message | True | Aligned with latest user priority but still assistant-authored details should be checked. | INFERENCE |
| ARTIFACT-11 | Previously generated maximum-fidelity Context Transfer Packet | handoff artifact | Transferred state from this old chat before package generation. | complete but repaired/normalized by this package | visible assistant final response before current prompt | True | Strong foundation; lacked stable IDs/files and included some external/profile context not strictly visible-chat scoped. | FACT |
| ARTIFACT-12 | Current user prompt requesting downloadable final report package | prompt / packaging instruction | Specified exact files, schema, stable ID patterns, audit/repair process, date anchor, and final response format. | current task driver | visible user message | True | Defines this package’s output requirements. | FACT |
| ARTIFACT-13 | Final report package generated in this response | generated files | Downloadable package with Markdown/YAML/ZIP files for later reading, sharing, aggregation, and spec-book construction. | created by current response | assistant-generated file outputs | True | Files are listed in the manifest; ZIP created if available. | FACT |
| ARTIFACT-14 | Prior web-style citation references such as turn0search/turn1search IDs | reference/citation artifact | Previously supported some assistant claims in the old chat. | non-portable; do not rely on them | prior assistant outputs | False | Rebuild citations from official sources in a future verification pass. | UNCERTAIN / UNVERIFIED |
| ARTIFACT-15 | No downloadable files existed before the current report package | artifact absence note | Prevents future reader from looking for missing earlier files. | absence recorded | visible chat inspection | True | Previous outputs were chat messages, not saved files. | FACT |

## 13. Rationale and Assumptions

Major visible rationale in the chat was pragmatic scope control. The user wants very broad device coverage, but broad coverage without tiering would produce ambiguous, untestable claims. The assistant therefore proposed platform contracts and support classes. That model remains an inference, not an explicit user-authored specification, but it is the most coherent continuation structure.

The strongest assumption is that “primary top-tier support” implies first-class architecture, QA, and release planning. This follows from ordinary planning logic and the assistant’s prior synthesis, but the user has not yet provided formal definitions for parity, full support, or release cadence. A future assistant should turn these words into explicit contracts before implementation work.

Another assumption is that console and legacy targets should not drive core architecture unless elevated. This follows from the latest explicit priority and from the known gating/constraint pattern of closed consoles and old hardware, but exact platform-holder facts must be verified externally. The report preserves the user's broad console/handheld/retro ambition while refusing to convert it into a full-parity commitment.

The prior assistant’s “Dominium full product vs Domino engine/core” split is useful as a conceptual scope separator, but the name “Domino” is not a confirmed project term. Future assistants should say “engine/core” unless the user confirms the name.

All current platform facts, including console OS descriptions, hardware statuses, Android/Apple/browser rules, XR runtime support, and SDK availability, are stale-risk and must be verified before future use.

## 14. Risks and Failure Modes

| ID | Risk / failure mode | Consequence | Likelihood | Severity | Mitigation | Related workstream | Label |
| --- | --- | --- | --- | --- | --- | --- | --- |
| RISK-01 | Summarisation loss during handoff or aggregation. | Future assistants may lose latest priority, unresolved status, or assistant-vs-user distinction. | medium | high | Use stable IDs, labels, and this package’s full report/YAML/registers together. | WORKSTREAM-11 | INFERENCE |
| RISK-02 | Stale external platform facts. | SDK/store/browser/console assumptions may be wrong when implementation starts. | high | high | Verify all platform facts from current official sources before acting. | WORKSTREAM-01 | FACT / UNCERTAIN |
| RISK-03 | Assistant suggestions treated as user decisions. | The project may adopt unconfirmed names, tiers, or technical strategies. | medium | high | Apply source hierarchy; user statements outrank assistant outputs. | WORKSTREAM-01 | FACT |
| RISK-04 | Tentative or superseded options repeated in future chats. | Repeated planning churn and possible contradiction of latest user priority. | medium | medium | Use Rejected/Superseded register. | WORKSTREAM-01 | INFERENCE |
| RISK-05 | Legal/IP mistakes around console firmware, BIOS, or unofficial tooling. | Unsafe or noncommercially viable implementation path. | medium | high | Use official console paths and avoid proprietary firmware redistribution unless licensed. | WORKSTREAM-06; WORKSTREAM-09 | INFERENCE |
| RISK-06 | Mobile/Web constraints under-designed because PC dominates early architecture. | Tier-0 Android/iOS/Web support becomes expensive or impossible to retrofit. | medium | high | Treat mobile and Web as co-equal architecture roots. | WORKSTREAM-03; WORKSTREAM-04; WORKSTREAM-05; WORKSTREAM-10 | INFERENCE |
| RISK-07 | Scope explosion from trying to support every listed device literally. | Unbounded engineering, QA, legal, and support burden. | high | high | Use platform contracts and classify unsupported/research/constrained targets explicitly. | WORKSTREAM-01; WORKSTREAM-06; WORKSTREAM-08; WORKSTREAM-09 | INFERENCE |
| RISK-08 | Engine/toolchain decision remains unknown. | Platform feasibility estimates may be speculative. | high | high | Create an architecture decision record before implementation planning. | WORKSTREAM-10 | UNCERTAIN / UNVERIFIED |
| RISK-09 | PC handheld support overclaimed without device-specific UX/performance testing. | Poor Steam Deck/handheld usability despite PC build running. | medium | medium-high | Define handheld profiles and test on representative devices. | WORKSTREAM-07 | INFERENCE |
| RISK-10 | Retro/legacy work diverts effort from Tier-0 delivery. | Primary platform progress slows and architecture may overfit obsolete constraints. | medium | medium-high | Keep legacy as Tier-2/research unless explicitly elevated. | WORKSTREAM-09 | INFERENCE |
| RISK-11 | Console support promised before official access or certification plan exists. | Unreliable roadmap and possible platform-holder/process blockers. | medium | high | Mark consoles as gated and verify partner/developer requirements. | WORKSTREAM-06 | INFERENCE |
| RISK-12 | Project-context contamination. | Report may import preferences, files, or plans not actually established in this chat. | low-medium | medium | Use THIS CHAT ONLY scope; label external context as PROJECT-CONTEXT if used. | WORKSTREAM-11 | FACT |
| RISK-13 | Bad future aggregation merges distinct workstreams too aggressively. | Loss of provenance, contradictions erased, decisions falsely deduplicated. | medium | high | Use IDs, source labels, and possible cross-chat conflict notes. | WORKSTREAM-11 | INFERENCE |
| RISK-14 | XR support becomes hidden major scope increase. | XR renderer/input/comfort requirements could derail core product planning. | medium | medium-high | Keep XR priority undecided/future until explicitly elevated. | WORKSTREAM-08 | INFERENCE |
| RISK-15 | Support term remains undefined. | Different readers may interpret support as full parity, compatibility, emulator-hosted, or research demo. | high | high | Define support taxonomy before matrix finalization. | WORKSTREAM-01 | INFERENCE |
| RISK-16 | Current hardware status in user list is stale or historically phrased. | Examples like “PS5 Pro (announced)” may no longer match current reality. | high | medium | Treat user list as conversation artifact and verify current market/platform facts later. | WORKSTREAM-06 | UNCERTAIN / UNVERIFIED |
| RISK-17 | Apple-family targets are overgeneralized. | Future plan may accidentally imply full Dominium on Apple Watch/tvOS/visionOS without scope. | medium | medium-high | Classify Apple subplatforms separately. | WORKSTREAM-04 | INFERENCE |
| RISK-18 | Android ecosystem fragmentation is underestimated. | Vendor ROMs, Android Go, TV, Automotive, and handheld devices may fail assumptions. | high | medium-high | Tier Android subtargets and set device/API baselines. | WORKSTREAM-03 | INFERENCE |
| RISK-19 | Web parity is promised without resolving browser/storage/performance limits. | Web build may fail to meet full product expectations. | medium | high | Define Web-specific parity/degradation rules and browser tests. | WORKSTREAM-05 | INFERENCE |
| RISK-20 | OpenXR/WebXR assumptions become stale or device-specific gaps appear. | XR plan may be incompatible with targeted devices or runtimes. | medium | medium | Verify XR runtime status and keep XR secondary until scoped. | WORKSTREAM-08 | UNCERTAIN / UNVERIFIED |

## 15. Verification Queue

| ID | Item requiring verification | Why verification is needed | Suggested verification source/type | Priority | Related workstream | Label |
| --- | --- | --- | --- | --- | --- | --- |
| VERIFY-01 | Current official commercial console developer access requirements for PlayStation, Xbox, and Nintendo. | Prior assistant claims about partner programs/devkits/certification are unverified and time-sensitive. | Official platform-holder developer/partner sites and current documentation. | highest | WORKSTREAM-06 | UNCERTAIN / UNVERIFIED |
| VERIFY-02 | Current PlayStation hardware/platform support status, including PS4/PS5/PS5 variants and PlayStation Portal role. | User list may be stale and assistant classified Portal as remote-play only without current verification. | Official Sony/PlayStation developer and product sources. | high | WORKSTREAM-06 | UNCERTAIN / UNVERIFIED |
| VERIFY-03 | Current Xbox One/Series development and compatibility model. | Assistant claims about Xbox OS/GDK/certification need current official backing. | Official Microsoft Xbox developer documentation. | high | WORKSTREAM-06 | UNCERTAIN / UNVERIFIED |
| VERIFY-04 | Current Nintendo Switch/successor developer support and platform facts. | Nintendo hardware/platform status can change; official access is gated. | Official Nintendo developer portal and public product information. | high | WORKSTREAM-06 | UNCERTAIN / UNVERIFIED |
| VERIFY-05 | Current Android SDK/NDK, Google Play target API, ABI, Android TV/Go/Automotive requirements. | Android is Tier-0 and platform rules change. | Official Android Developers and Google Play policy documentation. | highest | WORKSTREAM-03 | UNCERTAIN / UNVERIFIED |
| VERIFY-06 | Current Apple SDK, App Store, iOS/iPadOS/macOS/tvOS/watchOS/visionOS submission and support requirements. | iOS is Tier-0 and Apple rules are time-sensitive. | Official Apple Developer documentation and App Store Connect guidelines. | highest | WORKSTREAM-04 | UNCERTAIN / UNVERIFIED |
| VERIFY-07 | Current WebGPU browser support and limitations. | Web is Tier-0 and rendering policy depends on WebGPU availability. | Official browser/platform documentation, MDN, W3C/WebGPU status pages where applicable. | highest | WORKSTREAM-05; WORKSTREAM-10 | UNCERTAIN / UNVERIFIED |
| VERIFY-08 | Current WebAssembly features needed for Dominium, including SIMD, threads, memory limits, filesystem/storage patterns. | WASM feature availability affects Web parity. | Official WebAssembly docs, browser docs, MDN, Emscripten docs if used. | high | WORKSTREAM-05 | UNCERTAIN / UNVERIFIED |
| VERIFY-09 | Steam Deck/SteamOS current developer guidance, Steam Deck Verified requirements, and Linux runtime assumptions. | PC handheld support and Steam Deck target status need current facts. | Official Steamworks/Valve documentation. | medium-high | WORKSTREAM-07 | UNCERTAIN / UNVERIFIED |
| VERIFY-10 | Feasibility of listed Apple devices: iPod Touch, Apple TV, Apple Watch, Vision Pro, Intel Mac, Apple Silicon Mac. | User listed broad Apple hardware but only iOS was explicitly promoted. | Official Apple platform docs and current product/OS support matrices. | medium-high | WORKSTREAM-04; WORKSTREAM-08 | UNCERTAIN / UNVERIFIED |
| VERIFY-11 | Android TV, Google TV, Android Automotive, Chromebook Android compatibility, and vendor ROM constraints. | User listed them, but support meaning and app/game suitability differ. | Official Android/ChromeOS/Automotive developer docs and platform policies. | medium-high | WORKSTREAM-03 | UNCERTAIN / UNVERIFIED |
| VERIFY-12 | Current OpenXR, WebXR, ARKit, ARCore, SteamVR, Meta, PlayStation VR, Windows Mixed Reality, and Pico runtime status. | XR strategy was assistant-proposed and may be stale or platform-specific. | Official Khronos/OpenXR, W3C/WebXR, Apple, Google, Valve, Meta, Sony, Microsoft, Pico docs. | medium | WORKSTREAM-08 | UNCERTAIN / UNVERIFIED |
| VERIFY-13 | Legal and technical feasibility for legacy console/handheld/firmware targets and emulator-hosted support. | Legacy paths can involve copyrighted BIOS/firmware or obsolete toolchains. | Official platform/legal docs if available; legal review; public emulator licensing docs for emulator-hosted strategy. | medium | WORKSTREAM-06; WORKSTREAM-09 | UNCERTAIN / UNVERIFIED |
| VERIFY-14 | Wine/Proton compatibility strategy and whether Proton should be official support or best-effort. | Assistant called Proton/Wine nice-to-have but Steam Deck strategy may change this. | Steamworks/Proton documentation and project decision. | medium | WORKSTREAM-02; WORKSTREAM-07 | UNCERTAIN / UNVERIFIED |
| VERIFY-15 | Feasibility of Vulkan, Metal, WebGPU, WebGL, GLES, OpenGL, DirectX backend strategy. | Rendering stack determines platform reach and complexity. | Official API docs and engine/toolchain support docs. | highest | WORKSTREAM-10 | UNCERTAIN / UNVERIFIED |
| VERIFY-16 | Unity/Unreal/custom engine export/support implications if one is chosen. | User listed Unity Runtime and Unreal Runtime but engine choice is not established. | Official Unity/Unreal/custom build tool docs once engine choice is known. | high | WORKSTREAM-10 | UNCERTAIN / UNVERIFIED |
| VERIFY-17 | Current status of user-listed hardware examples, especially historically phrased items such as PS5 Pro “announced” and Smach Z “cancelled.” | User list may be outdated or intentionally historical; future claims should be current. | Official product pages and reputable current references. | medium | WORKSTREAM-06; WORKSTREAM-07 | UNCERTAIN / UNVERIFIED |
| VERIFY-18 | Browser storage, PWA/offline, service worker, IndexedDB/OPFS, and save-file feasibility. | Web Tier-0 requires reliable persistence strategy. | Official browser docs, MDN, web platform specifications. | high | WORKSTREAM-05 | UNCERTAIN / UNVERIFIED |
| VERIFY-19 | Cross-platform audio, filesystem, networking, and input library support for selected engine/toolchain. | Platform contracts require more than graphics support. | Official engine/library/platform documentation after toolchain decision. | high | WORKSTREAM-10 | UNCERTAIN / UNVERIFIED |
| VERIFY-20 | Package files exist, YAML parses, ZIP includes all requested files. | Current task requires real downloadable files, not claimed files. | Local file system check and YAML parser. | highest | WORKSTREAM-11 | FACT |

## 16. Spec Book Contribution Notes

This chat should feed into a future Project Spec Book primarily as the platform-support and target-environment chapter. Its unique contribution is the user’s explicit priority ordering: PC first, then Android, iOS, and Web as primary top-tier support. It also contributes a broad target inventory across consoles, handhelds, mobile, web, AR/VR/XR, and cross-cutting APIs.

Likely chapters include: Platform Support Strategy; Tier-0 Platform Contracts; Mobile Architecture Requirements; Web/WASM Runtime Requirements; PC and PC Handheld Support; Closed Console Strategy; Legacy/Retro Research Targets; XR Roadmap; Rendering and Runtime Backend Strategy; QA and Release Tiering; Verification and External Source Requirements.

Items that should become formal requirements after user confirmation: PC/Android/iOS/Web as Tier-0, the platform-contract matrix, explicit definitions of support levels, and current-source verification before implementation claims. Items that should remain background context until confirmed: “Domino,” legacy console ambitions, specific graphics backend ordering, XR runtime strategy, and exact console generation coverage.

| ID | Likely Spec Book section | Contribution | Related IDs | Label |
| --- | --- | --- | --- | --- |
| SPECBOOK-01 | Platform Support Strategy | Defines core tier hierarchy and support-contract approach. | WORKSTREAM-01; DECISION-01; DECISION-02; DECISION-03; DECISION-04 | FACT / INFERENCE |
| SPECBOOK-02 | Tier-0 Platforms | Establishes PC, Android, iOS/iPadOS, and Web as first-class planning targets. | WORKSTREAM-02; WORKSTREAM-03; WORKSTREAM-04; WORKSTREAM-05 | FACT |
| SPECBOOK-03 | Console Strategy | Separates current official commercial consoles from legacy/research targets. | WORKSTREAM-06; DECISION-06; DECISION-11 | INFERENCE |
| SPECBOOK-04 | PC Handheld Strategy | Maps handheld PCs to Windows/Linux/SteamOS plus handheld-specific QA/UX profiles. | WORKSTREAM-07; DECISION-08 | INFERENCE |
| SPECBOOK-05 | Web Runtime Strategy | Promotes Web/WASM from fallback to Tier-0 product target requiring browser matrix and rendering/storage decisions. | WORKSTREAM-05; DECISION-04; DECISION-09 | FACT / INFERENCE |
| SPECBOOK-06 | Mobile Runtime Strategy | Identifies Android and iOS constraints as architecture drivers. | WORKSTREAM-03; WORKSTREAM-04; DECISION-05 | FACT / INFERENCE |
| SPECBOOK-07 | XR Roadmap | Preserves AR/VR device inventory and runtime-first OpenXR/WebXR proposal while marking priority unresolved. | WORKSTREAM-08; DECISION-14; QUESTION-16 | INFERENCE |
| SPECBOOK-08 | Legacy/Retro Research Targets | Preserves retro OS/console ambitions as constrained/research/background rather than parity commitments. | WORKSTREAM-09; REJECTED-03 | INFERENCE |
| SPECBOOK-09 | Architecture Requirements | Identifies need for platform abstraction, rendering backend policy, input/UI strategy, storage/save model, and QA/release contracts. | WORKSTREAM-10; TASK-13; TASK-14; TASK-15; TASK-16 | INFERENCE |
| SPECBOOK-10 | Verification Queue | Lists external platform facts requiring official-source verification before spec hardening. | VERIFY-01; VERIFY-05; VERIFY-06; VERIFY-07; VERIFY-15 | FACT / UNCERTAIN |

## 17. What Future Assistants Must Preserve

| Priority | Item | Type | Why it matters | Risk if lost | Label | Confidence |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | PC is the first primary platform family. | decision | Controls initial platform strategy and architecture baseline. | Future work may mis-prioritize platforms. | FACT | 5 |
| 2 | Android is primary top-tier support after PC. | decision | Android constraints must be designed early. | Android becomes an expensive late port. | FACT | 5 |
| 3 | iOS is primary top-tier support after PC. | decision | Apple mobile constraints must shape architecture. | iOS/iPadOS feasibility may be compromised. | FACT | 5 |
| 4 | Web is primary top-tier support after PC. | decision | WASM/browser constraints must shape architecture. | Web becomes a demo/fallback instead of full target. | FACT | 5 |
| 5 | Mobile and Web should not be treated as late ports. | architectural implication | Prevents PC-only assumptions. | Architecture may fail Tier-0 goals. | INFERENCE | 4 |
| 6 | Use a formal platform support matrix/platform contracts. | next action | Makes broad device support concrete. | “Support” remains ambiguous. | INFERENCE | 5 |
| 7 | Consoles are desired but gated/secondary unless elevated. | working classification | Controls legal/commercial scope. | Console promises may be unrealistic. | INFERENCE | 4 |
| 8 | Legacy consoles/retro OSes are constrained/research by default. | working classification | Prevents parity overcommitment. | Scope explosion and legal risk. | INFERENCE | 4 |
| 9 | “Domino” engine/core name is unconfirmed. | uncertainty | Avoids false project terminology. | Assistant-invented name becomes spec fact. | UNCERTAIN / UNVERIFIED | 5 |
| 10 | All external platform facts require verification before future use. | constraint | Platform rules and hardware status change. | Spec may encode stale or false facts. | FACT | 5 |
| 11 | Do not bundle proprietary BIOS/firmware for legacy/emulated support. | legal constraint | Avoids IP/legal risk. | Unsafe legacy strategy. | INFERENCE | 4 |
| 12 | Closed console support must use official access for commercial/native support. | constraint | SDK/devkit/certification requirements are gated. | Unusable console plan. | UNCERTAIN / UNVERIFIED | 4 |
| 13 | PC handhelds map primarily to PC OS targets plus handheld QA/UX profiles. | working classification | Keeps handheld strategy manageable. | Every handheld may be treated as separate platform. | INFERENCE | 4 |
| 14 | XR priority is unresolved; runtime-first OpenXR/WebXR was only an assistant proposal. | uncertainty | Prevents hidden XR scope expansion. | XR may distort core platform planning. | INFERENCE | 3 |
| 15 | Engine/toolchain choice is not established. | open question | Determines platform feasibility. | Future plans may assume Unity/Unreal/custom without basis. | UNCERTAIN / UNVERIFIED | 5 |
| 16 | Support must be defined by scope: full product, reduced build, engine-only, emulator-hosted, remote-play, unsupported. | taxonomy | Prevents false equivalence among device families. | Support claims become meaningless. | INFERENCE | 5 |
| 17 | This package is chat-specific and not a whole-project summary. | scope rule | Protects provenance during aggregation. | Project-context contamination. | FACT | 5 |

## 18. What Future Assistants Must Not Assume

- Do not assume the engine is custom, Unity, Unreal, SDL, GLFW, or any other stack.
- Do not assume “Domino” is a confirmed engine/core name.
- Do not assume iPadOS is separately confirmed beyond assistant synthesis.
- Do not assume tvOS, watchOS, visionOS, Android TV, Android Automotive, or Android Go are Tier-0.
- Do not assume all historical consoles are full product targets.
- Do not assume official console developer access exists.
- Do not assume WebGPU is mandatory or that WebGL fallback is final.
- Do not assume Windows/macOS/Linux minimum versions.
- Do not assume Android/iOS minimum OS/API versions.
- Do not assume release cadence or simultaneous launch.
- Do not assume prior web citation IDs can be reused.
- Do not assume any pre-existing files or repositories were uploaded in this chat.
- Do not assume the user’s broad device inventory is verified current-world truth.

## 19. Recommended Next Action

- Best next action if continuing this chat’s work alone: create the formal Platform Support Matrix and Tier-0 contracts for PC, Android, iOS/iPadOS, and Web.
- Best next action if aggregating this chat with other reports: ingest this package as the platform-support source packet, preserve IDs and labels, and compare against other chats for conflicting platform priorities.
- User verification needed before acting: confirm exact meaning of “support,” whether iPadOS is included with iOS Tier-0, whether “Domino” is a real name, and whether any console/XR/legacy targets should be elevated.

## 20. Appendix: Possibly Relevant Details

Major user-provided target families to preserve: PlayStation consoles/handhelds/software; Xbox consoles/software; Nintendo home consoles/handhelds/software; PC handhelds; Android devices/software/ROMs; Apple devices/software; Web platforms/browsers; AR hardware/software; VR hardware/software; cross-cutting runtimes/APIs such as C/C++, Vulkan, OpenGL/OpenGL ES, DirectX 9–12, Metal, SDL, GLFW, Unity Runtime, Unreal Runtime, Wine, and Proton.

Known contradiction: one assistant answer said there were roughly 8 top-level targets but listed 9: Windows, macOS, Linux, Web, Android, iOS/iPadOS, PlayStation, Xbox, Nintendo. Use the explicit list, not the count.

Known direction change: the earliest assistant response was retro-heavy; the latest explicit user decision makes PC plus Android/iOS/Web the primary top tier.

Known stale phrase: user’s list included “PS5 Pro (announced).” Treat that as historical user wording requiring current verification, not as a current fact.

No code, source files, repositories, datasets, PDFs, images, spreadsheets, slides, or downloadable artifacts existed in the visible chat before this package.
