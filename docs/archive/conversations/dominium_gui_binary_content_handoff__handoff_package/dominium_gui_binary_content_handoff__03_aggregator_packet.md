# Aggregator Packet — Dominium GUI/Binary + CONTENT0 Handoff

## 1. Packet Metadata

- Chat label: Dominium GUI/Binary + CONTENT0 Handoff
- Filesystem label: `dominium_gui_binary_content_handoff`
- Date anchor: 2026-05-27 Australia/Melbourne
- Source scope: This visible chat only; PROJECT-CONTEXT labels outside context.
- Coverage: Full for visible chat and previous Context Transfer Packet; no repository/file inspection.
- Confidence: 4 / 5
- Staleness risk: Medium
- Merge priority: High for GUI/binary planning; medium for content workstream.
- Main limitations: Linux/Android unresolved; platform facts stale-prone; assistant suggestions not user decisions.

## 2. Ultra-Condensed Carry-Forward Capsule

This chat contributes two major bodies of project state. The first is the CONTENT0 content-layer thread. The user supplied a canonical content-population prompt for Dominium / Domino, targeting GPT-5.2 CODEX and scoped to data, schema extensions, and docs only. It forbids engine/runtime/ECS/domain/authority/time-model changes and requires provenance for every entity. The core principle is causal construction: no entity exists unless created by an explicit process; no population exists unless born; no city unless built; no resource unless extracted or produced; no civilization unless historically emerged; no start condition without historical explanation. The assistant drafted a cleaned prompt, but the user corrected the process and said to discuss before planning or generating prompts. Therefore any assistant-generated CONTENT0 rewrite is draft only. The assistant critique raised unresolved content issues: descriptive schema semantics, deterministic seed hierarchy, macro-to-micro refinement contract, timeline topology, human baseline, civilization taxonomy, conservation domains, knowledge uncertainty/loss, start-scenario exclusions, and documentation traceability.

The second and current main body is GUI/binary strategy. The user decided to redo GUIs from scratch. For every product — setup, launcher, client, server, tools, and related products — CLI must always work, TUI is expected, and multiple modular GUIs should attach to product backends to compile native applications. This creates a first-order need for a shared backend/UI contract. The exact contract is unresolved; possible mechanisms include in-process ABI, IPC, or both. A stable C ABI was suggested by an assistant only as a candidate, not a user decision.

The user proposed concrete Windows frontend families: Win32 ANSI for 32-bit Intel setup/client; Win32 Unicode for 64-bit Intel and ARM setup/client; WinForms .NET Framework for launcher/server with old-framework support originally phrased as .NET 4.8 down to 4.0; and WinUI 3 for 64-bit Intel and ARM launcher/server with Windows 10 1809 graceful degradation. The assistant flagged that old .NET support needs real target/build lanes, not a single .NET 4.8 binary. For macOS, the user proposed AppKit for setup/launcher/client/server, originally 64-bit Intel and down to macOS 10.9, plus SwiftUI for future launcher/server on Intel and ARM with floor around macOS 11. The assistant flagged that macOS 10.9 likely requires frozen legacy Apple tooling and that AppKit need not be Intel-only. Linux and Android are in scope but undecided; Linux should not blindly copy Windows' stack count, and Android should be treated as a mobile host family.

The aggregator must preserve status carefully. User decisions are facts; assistant suggestions are recommendations unless accepted. External platform/toolchain facts require verification before future implementation. The next active work should define GUI/binary doctrine, backend contract, product matrix, platform matrices, compatibility lanes, visual profiles, packaging forms, build/toolchain lanes, and verification plan. Do not begin with code.

## 3. Top Carry-Forward Items

| Priority | Item | Type | Related ID | Why it matters | Label | Confidence |
|---|---|---|---|---|---|---|
| 1 | Redo GUIs from scratch | decision | DECISION-06 | Current main workstream | FACT | high |
| 2 | CLI mandatory for every product | requirement | DECISION-07 | Baseline operability | FACT | high |
| 3 | TUI expected for every product | requirement | DECISION-08 | Terminal workflows | FACT | high |
| 4 | Modular GUIs attach to product backends | architecture | DECISION-09 | Prevents drift | FACT | high |
| 5 | Backend/UI contract unresolved and first priority | open issue | QUESTION-01 | All frontends depend on it | INFERENCE | medium-high |
| 6 | Windows frontend family list | platform plan | WORKSTREAM-08 | Most detailed platform plan | FACT | high |
| 7 | macOS AppKit/SwiftUI list with legacy caveat | platform plan | WORKSTREAM-09 | Defines Apple lanes | FACT / UNCERTAIN | medium-high |
| 8 | Linux and Android open | open plan | WORKSTREAM-10, WORKSTREAM-11 | Avoid false decisions | FACT | high |
| 9 | CONTENT0 data-only provenance doctrine | content requirement | WORKSTREAM-01 | Content spec foundation | FACT | high |
| 10 | External facts require verification | evidence rule | VERIFY-17 | Avoid stale toolchain claims | FACT | high |

## 4. Workstream Summaries

### WORKSTREAM-01 — CONTENT0 canonical content population
- Objective: Populate Dominium/Domino canonical universe, civilization, economy, history, population, technology, and start-condition content through data, schemas, and docs only.
- Current state: User supplied CONTENT0 prompt; assistant produced a draft rewrite; user redirected to discussion-first before more prompting.
- Desired end state: Data-driven canonical content with Sol and Earth macro-defined, all major structures documented, no entity appearing without origin/provenance.
- Priority: medium-high
- Decisions: DECISION-01, DECISION-02
- Tasks: none
- Constraints: see constraint register
- Artifacts: ARTIFACT-01, ARTIFACT-02, ARTIFACT-03
- Risks: RISK-06
- Open questions: none listed
- Next action: Define pending decisions before implementation


### WORKSTREAM-02 — CONTENT0 prompt refinement and discussion-first process
- Objective: Refine the content-generation prompt only after unresolved conceptual issues are discussed.
- Current state: Assistant draft exists but is not accepted as final.
- Desired end state: A Codex-ready prompt that preserves data-only scope, provenance, deterministic seeds, and refinable macro content.
- Priority: medium
- Decisions: DECISION-03
- Tasks: TASK-13
- Constraints: see constraint register
- Artifacts: see artifact ledger
- Risks: see risk register
- Open questions: none listed
- Next action: Use the ten issue list as agenda


### WORKSTREAM-03 — Full-universe/default datapack architecture
- Objective: Plan a universe representation that is efficient in storage and memory and supports fully procedural, partially defined with procedural gaps, and fully defined/architected universes.
- Current state: Goal stated by user; no finalized architecture.
- Desired end state: A scalable content model with explicit definition levels, procedural gaps, provenance, and refinement paths.
- Priority: medium
- Decisions: none
- Tasks: TASK-14
- Constraints: see constraint register
- Artifacts: see artifact ledger
- Risks: RISK-07
- Open questions: QUESTION-13
- Next action: Define levels of definition and importance dimensions


### WORKSTREAM-04 — Default Milky Way datapack
- Objective: Define the default shipped datapack containing the Milky Way and the galaxy's most important stars, systems, and celestial sites.
- Current state: User goal stated; selection criteria unresolved.
- Desired end state: Milky Way data with important visiting, harvesting, research, navigation, and other sites selected by explicit criteria.
- Priority: medium
- Decisions: DECISION-04
- Tasks: none
- Constraints: see constraint register
- Artifacts: see artifact ledger
- Risks: see risk register
- Open questions: QUESTION-14
- Next action: Define pending decisions before implementation


### WORKSTREAM-05 — Sol system canonical data
- Objective: Define the Sol system and its important celestial bodies, structures, satellites, belts, fields, and points.
- Current state: Mandatory in CONTENT0 and emphasized by user; not implemented here.
- Desired end state: Macro-complete, refinable Sol system with formation history, orbital/domain data, visitability rules, and provenance.
- Priority: medium-high
- Decisions: DECISION-05
- Tasks: none
- Constraints: see constraint register
- Artifacts: see artifact ledger
- Risks: see risk register
- Open questions: none listed
- Next action: Define pending decisions before implementation


### WORKSTREAM-06 — GUI and binary rebuild
- Objective: Redo all GUIs from scratch across products while preserving CLI, expected TUI, and modular GUI frontends attached to shared backends.
- Current state: Current main workstream; explicit user decision made.
- Desired end state: A coherent multi-platform frontend/binary strategy for setup, launcher, client, server, and tools.
- Priority: critical
- Decisions: DECISION-06, DECISION-07
- Tasks: TASK-01, TASK-03, TASK-12
- Constraints: see constraint register
- Artifacts: ARTIFACT-07, ARTIFACT-08, ARTIFACT-10
- Risks: RISK-02, RISK-12
- Open questions: QUESTION-03, QUESTION-15
- Next action: Produce first in new chat before code


### WORKSTREAM-07 — Shared backend/UI contract
- Objective: Define the shared contract consumed by CLI, TUI, and GUI frontends so product logic stays backend-owned.
- Current state: Recognized as the first unresolved design issue; no shape finalized.
- Desired end state: Stable command/state/event/error/versioning model exposed through suitable in-process ABI, IPC, or both.
- Priority: critical
- Decisions: DECISION-09, DECISION-16
- Tasks: TASK-02
- Constraints: see constraint register
- Artifacts: see artifact ledger
- Risks: RISK-01
- Open questions: QUESTION-01, QUESTION-02
- Next action: Draft candidate contract model and identify repo facts needed


### WORKSTREAM-08 — Windows frontend family matrix
- Objective: Plan Windows GUI/build lanes: Win32 ANSI, Win32 Unicode, WinForms compatibility family, and WinUI 3 modern family.
- Current state: User proposed families; assistant corrected feasibility issues around .NET Framework targeting.
- Desired end state: Explicit Windows matrix by product, architecture, OS floor, framework/runtime, toolchain, packaging, and support level.
- Priority: high
- Decisions: DECISION-10, DECISION-11
- Tasks: TASK-04
- Constraints: see constraint register
- Artifacts: see artifact ledger
- Risks: RISK-10
- Open questions: QUESTION-05, QUESTION-06
- Next action: Normalize user-proposed Windows families


### WORKSTREAM-09 — macOS frontend family matrix
- Objective: Plan macOS GUI/build lanes using AppKit and SwiftUI with explicit deployment floors and toolchains.
- Current state: User proposed AppKit and SwiftUI lanes; assistant identified macOS 10.9/frozen-toolchain issue.
- Desired end state: Explicit macOS matrix by product, architecture, macOS floor, Xcode/SDK version, packaging/signing, and support level.
- Priority: high
- Decisions: DECISION-12, DECISION-13
- Tasks: TASK-05
- Constraints: see constraint register
- Artifacts: see artifact ledger
- Risks: RISK-09
- Open questions: QUESTION-07, QUESTION-08
- Next action: Clarify whether macOS 10.9 is hard requirement


### WORKSTREAM-10 — Linux frontend strategy
- Objective: Define Linux GUI/build lanes consistent with backend-contract/thin-shell doctrine.
- Current state: In scope but exact stack undecided.
- Desired end state: Linux frontend strategy with distro baseline, toolkit/renderer choice, packaging forms, and support policy.
- Priority: high
- Decisions: DECISION-14
- Tasks: TASK-06
- Constraints: see constraint register
- Artifacts: see artifact ledger
- Risks: RISK-08
- Open questions: QUESTION-09
- Next action: Compare Qt, GTK, Avalonia, custom renderer host, and TUI-first approaches


### WORKSTREAM-11 — Android frontend strategy
- Objective: Define Android role and frontend strategy under the same backend doctrine where appropriate.
- Current state: In scope but exact strategy undecided.
- Desired end state: Android-specific product role and UI/package plan, not merely desktop scaled down.
- Priority: medium-high
- Decisions: DECISION-14
- Tasks: TASK-07
- Constraints: see constraint register
- Artifacts: see artifact ledger
- Risks: RISK-11
- Open questions: QUESTION-10
- Next action: Decide Android role before toolkit selection


### WORKSTREAM-12 — Packaging, linking, and distribution doctrine
- Objective: Decide per-product/per-platform packaging forms, static vs dynamic linking, plugin/library boundaries, installers, and portable artifacts.
- Current state: Partially discussed; no final matrix.
- Desired end state: Clear packaging model by product and platform with support/test implications.
- Priority: high
- Decisions: none
- Tasks: TASK-10
- Constraints: see constraint register
- Artifacts: see artifact ledger
- Risks: see risk register
- Open questions: QUESTION-11
- Next action: Separate static/self-contained vs dynamic/plugin cases


### WORKSTREAM-13 — Build, toolchain, and CI matrix
- Objective: Create a formal build matrix across OS, architecture, framework/runtime, toolchain, packaging, signing, and support status.
- Current state: Recognized as necessary; not built.
- Desired end state: Auditable matrix mapping every support claim to a build lane and test lane.
- Priority: high
- Decisions: none
- Tasks: TASK-11
- Constraints: see constraint register
- Artifacts: see artifact ledger
- Risks: RISK-03, RISK-13
- Open questions: none listed
- Next action: Verify official docs before finalizing


### WORKSTREAM-14 — Visual profile and OEM+ system
- Objective: Use a small set of visual/behavior profiles rather than separate GUI codebases per OS era.
- Current state: Assistant recommendation; user did not explicitly lock exact profile set.
- Desired end state: Defined profile set such as classic/OEM+/modern/reduced-admin with clear behavior and visual differences.
- Priority: medium-high
- Decisions: DECISION-15
- Tasks: TASK-09
- Constraints: see constraint register
- Artifacts: see artifact ledger
- Risks: RISK-04
- Open questions: QUESTION-12
- Next action: Draft classic/OEM+/modern/reduced-admin candidates


### WORKSTREAM-15 — TUI doctrine
- Objective: Define what 'expected to work with TUI' means for every product.
- Current state: Requirement stated; parity level unresolved.
- Desired end state: TUI scope and parity rules mapped to backend contract and product matrix.
- Priority: high
- Decisions: DECISION-08
- Tasks: TASK-08
- Constraints: see constraint register
- Artifacts: see artifact ledger
- Risks: see risk register
- Open questions: QUESTION-04
- Next action: Classify TUI as full parity, admin parity, or fallback per product


### WORKSTREAM-16 — Per-chat context transfer and report package
- Objective: Create a downloadable, shareable, reusable report package for this old chat.
- Current state: This response generates the package.
- Desired end state: Markdown/YAML report files and ZIP package usable for future aggregation.
- Priority: critical
- Decisions: DECISION-17
- Tasks: TASK-15
- Constraints: see constraint register
- Artifacts: see artifact ledger
- Risks: RISK-05, RISK-14, RISK-15
- Open questions: none listed
- Next action: Store Markdown/YAML/ZIP together


## 5. Registers for Merge

### Decision Register

| ID | Decision | Status | Evidence / basis | Rationale | Implications | Related workstream | Confidence | Label |
|---|---|---|---|---|---|---|---|---|
| DECISION-01 | CONTENT0 work is content-layer only: data/, schema/, docs/; no engine/runtime/code logic changes. | decided | User CONTENT0 prompt. | Keeps content population separate from simulation architecture. | Content-generation prompts must not touch engine/game/client/server/tools except documentation where explicitly allowed. | WORKSTREAM-01 | high | FACT |
| DECISION-02 | No entity/population/city/resource/civilization/start may appear without explicit causal origin/provenance. | decided | User CONTENT0 philosophy. | Prevents fabricated gameplay assets and maintains historical/physical continuity. | Schemas/data/docs need origin, process, construction/history, and refinement metadata. | WORKSTREAM-01 | high | FACT |
| DECISION-03 | Discuss before generating more prompts. | decided | User said: 'First, let's discuss this before we plan or generate any prompts.' | Avoid premature prompt-writing and hidden assumptions. | Assistant-cleaned CONTENT0 prompt remains draft/superseded. | WORKSTREAM-02 | high | FACT |
| DECISION-04 | Default shipped datapack should include the Milky Way galaxy. | decided | User explicitly stated default data pack should contain the Milky Way galaxy. | Milky Way is canonical/default galaxy for shipped content. | Need selection criteria for important stars/systems/sites. | WORKSTREAM-04 | high | FACT |
| DECISION-05 | Sol system must be included and specially defined among important systems. | decided | CONTENT0 mandates Sol; user specifically included Sol system. | Sol/Earth/humanity are central canonical anchors. | Sol system requires bodies, structures, satellites, belts, fields, points, histories, and visitability rules. | WORKSTREAM-05 | high | FACT |
| DECISION-06 | Redo GUIs from scratch. | decided | User: 'I've decided I want to redo the GUIs from scratch.' | Latest direction for GUI work. | New planning should not assume old GUI architecture is retained. | WORKSTREAM-06 | high | FACT |
| DECISION-07 | Every product must always work with CLI. | decided | User explicit statement. | Guarantees baseline operability, automation, and headless use. | CLI must be part of every product matrix and should consume the same backend contract. | WORKSTREAM-06 | high | FACT |
| DECISION-08 | Every product is expected to work with TUI. | decided but scope unresolved | User explicit statement. | Provides richer terminal control across products. | TUI doctrine and parity rules are needed. | WORKSTREAM-15 | high | FACT |
| DECISION-09 | Products will have multiple modular GUIs attached to product backends to compile native applications. | decided | User explicit statement. | Supports platform/era-specific frontends while keeping product logic centralized. | Backend/UI contract is first-class; GUI shells must be replaceable. | WORKSTREAM-07 | high | FACT |
| DECISION-10 | Windows frontend family list includes Win32 ANSI x86, Win32 Unicode x64/ARM64, WinForms .NET Framework family, and WinUI 3 x64/ARM64. | proposed/accepted by user statement | User listed these Windows frontends. | Covers legacy native, main native, managed compatibility, and modern Windows lanes. | Must be normalized into build/toolchain lanes. | WORKSTREAM-08 | high | FACT |
| DECISION-11 | WinForms old-framework support must use real distinct target/build lanes, not a single .NET 4.8 binary claiming .NET 4.0 support. | technical correction / not explicitly user-ratified | Assistant correction based on external docs in previous packet; future verification required. | Avoid compatibility fraud. | Need exact .NET target list and tooling versions. | WORKSTREAM-08 | medium | UNCERTAIN / UNVERIFIED |
| DECISION-12 | macOS frontend family list includes AppKit and SwiftUI. | proposed/accepted by user statement | User listed AppKit and SwiftUI lanes. | Covers native Apple desktop and future modern Apple UI. | Need deployment floors, Xcode versions, universal binary policy. | WORKSTREAM-09 | high | FACT |
| DECISION-13 | macOS 10.9 AppKit support requires a frozen legacy Apple toolchain unless later verified otherwise. | technical correction / not explicitly user-ratified | Assistant correction based on external docs in previous packet; future verification required. | Current toolchains generally cannot target such old floors. | Need decide if macOS 10.9 is hard requirement. | WORKSTREAM-09 | medium | UNCERTAIN / UNVERIFIED |
| DECISION-14 | Linux and Android are in scope but exact GUI stacks are open. | open | User said Linux similar and Android similar, without choosing stacks. | Avoid inventing platform plans. | New chat must compare and decide Linux/Android strategies. | WORKSTREAM-10, WORKSTREAM-11 | high | FACT |
| DECISION-15 | Do not make one separate GUI per OS version/era by default; use compatibility lanes and visual profiles. | assistant recommendation / not explicit user final | Assistant recommended this; user later listed frontend families rather than per-version GUIs. | Avoid matrix explosion. | Visual profile system should be planned. | WORKSTREAM-14 | medium | INFERENCE |
| DECISION-16 | Stable C ABI / interop boundary is a candidate backend-contract approach, not a final decision. | candidate | Assistant recommendation in prior packet. | Could support Win32, .NET P/Invoke, AppKit/Swift bridges, Linux, and Android bindings. | Must not be treated as final until user/project validates. | WORKSTREAM-07 | medium | INFERENCE |
| DECISION-17 | Use this chat-specific report package for future aggregation. | decided for current task | Current user requested downloadable, shareable, reusable report package. | Preserve old-chat state for future Project Spec Book. | Create Markdown/YAML/ZIP files and manifest. | WORKSTREAM-16 | high | FACT |

### Task Register

| ID | Task | Priority | Urgency | Owner | Dependencies | Inputs needed | Expected output | Recommended next step | Related workstream | Label |
|---|---|---|---|---|---|---|---|---|---|---|
| TASK-01 | Define GUI/binary architecture doctrine. | critical | immediate | new assistant + user | This package | Current user decisions and open questions | Doctrine for CLI/TUI/GUI/backends/host profiles/packages | Produce first in new chat before code | WORKSTREAM-06 | FACT |
| TASK-02 | Define backend/UI contract shape. | critical | immediate | new assistant + user | Product backend architecture | Repo/API inspection if available; product operation model | In-process ABI/IPC/both; command/state/event/error/versioning model | Draft candidate contract model and identify repo facts needed | WORKSTREAM-07 | INFERENCE |
| TASK-03 | Build product matrix for setup, launcher, client, server, and tools. | critical | early | new assistant | Doctrine and backend contract assumptions | Product list and required capabilities | Matrix mapping products to CLI/TUI/GUI families/packages | Create matrix after doctrine | WORKSTREAM-06 | FACT |
| TASK-04 | Build Windows frontend/build matrix. | high | early | new assistant | Product matrix | OS floors, architectures, VS/SDK/.NET versions | Windows build lanes and artifact list | Normalize user-proposed Windows families | WORKSTREAM-08 | FACT |
| TASK-05 | Build macOS frontend/build matrix. | high | early | new assistant | Product matrix | macOS floors, Xcode/SDK versions, Intel/ARM policy | macOS build lanes and artifact list | Clarify whether macOS 10.9 is hard requirement | WORKSTREAM-09 | FACT |
| TASK-06 | Choose Linux GUI stack/lane model. | high | early | new assistant + user | Backend contract | Distro baselines, toolkit constraints, packaging preferences | Linux strategy and matrix | Compare Qt, GTK, Avalonia, custom renderer host, and TUI-first approaches | WORKSTREAM-10 | FACT |
| TASK-07 | Define Android product role and frontend approach. | medium-high | after desktop doctrine | new assistant + user | Backend contract and product roles | Whether Android is full client, launcher, admin companion, or tools | Android strategy | Decide Android role before toolkit selection | WORKSTREAM-11 | FACT |
| TASK-08 | Define TUI doctrine and parity level. | high | early | new assistant + user | Backend contract | Which operations must be available in TUI | TUI scope/parity rules by product | Classify TUI as full parity, admin parity, or fallback per product | WORKSTREAM-15 | FACT |
| TASK-09 | Define visual profile/OEM+ system. | medium-high | mid | new assistant + user | GUI family matrix | Visual style goals and era/native expectations | Small profile set with scope and constraints | Draft classic/OEM+/modern/reduced-admin candidates | WORKSTREAM-14 | INFERENCE |
| TASK-10 | Define packaging/linking doctrine. | high | early-mid | new assistant | Product/platform matrices | Installer/portable/plugin/update requirements | Packaging matrix by product/platform | Separate static/self-contained vs dynamic/plugin cases | WORKSTREAM-12 | INFERENCE |
| TASK-11 | Define build/toolchain/CI matrix. | high | mid | new assistant | Platform matrices | Toolchain versions, SDKs, runners, signing/notarization | Auditable build matrix | Verify official docs before finalizing | WORKSTREAM-13 | INFERENCE |
| TASK-12 | Inspect actual repository/files before implementation. | critical | before code | new assistant | Repo/file access | Actual project tree and build files | Concrete implementation plan grounded in files | Do not assume prior assistant's repo references | WORKSTREAM-06 | UNCERTAIN / UNVERIFIED |
| TASK-13 | Resolve CONTENT0 conceptual issues before final prompt generation. | medium | later unless content resumes | new assistant + user | CONTENT0 and content architecture | Schema strategy, seed model, timeline/knowledge/conservation rules | Final content prompt doctrine | Use the ten issue list as agenda | WORKSTREAM-02 | FACT |
| TASK-14 | Define universe procedural-gap representation and importance taxonomy. | medium | later unless content resumes | new assistant + user | Content architecture | Storage/memory goals and content importance criteria | Universe/datapack representation strategy | Define levels of definition and importance dimensions | WORKSTREAM-03 | FACT |
| TASK-15 | Use generated report package in future aggregation. | high | when aggregating | user + future aggregator | This file package | Other old-chat packages | Master Project Spec Book and Living State File | Store Markdown/YAML/ZIP together | WORKSTREAM-16 | FACT |

### Constraint Register

| ID | Constraint | Type | Hard/soft | Source / basis | Practical implication | Violation risk | Confidence | Label |
|---|---|---|---|---|---|---|---|---|
| CONSTRAINT-01 | CONTENT0 may touch only data/, schema/, docs/. | scope | hard | User CONTENT0 | No engine/runtime/client/server/tools modifications except documentation where allowed. | high | high | FACT |
| CONSTRAINT-02 | CONTENT0 must not change engine code, runtime logic, execution, ECS, domains, authority, or time models. | scope/architecture | hard | User CONTENT0 | Rules are fixed; content is data-only. | high | high | FACT |
| CONSTRAINT-03 | No entity exists unless created by explicit process. | content philosophy | hard | User CONTENT0 | Every content entity needs origin/provenance. | high | high | FACT |
| CONSTRAINT-04 | No population exists unless born. | content philosophy | hard | User CONTENT0 | Population content needs birth/origin model. | high | high | FACT |
| CONSTRAINT-05 | No city exists unless built. | content philosophy | hard | User CONTENT0 | Settlements require construction/history. | medium-high | high | FACT |
| CONSTRAINT-06 | No resource exists unless extracted or produced. | content/economy | hard | User CONTENT0 | Resource/economy content must obey conservation and production/extraction origin. | high | high | FACT |
| CONSTRAINT-07 | No civilization exists unless it emerged historically. | content/history | hard | User CONTENT0 | Civilizations need origin, governance, territory, economy, legitimacy. | high | high | FACT |
| CONSTRAINT-08 | Macro content may exist without micro simulation, but must be refinable. | content modeling | hard | User CONTENT0 | Need resolution/refinement contract. | medium-high | high | FACT |
| CONSTRAINT-09 | Use deterministic seeds for universe/galaxy content; no procedural generation logic in data prompts. | content modeling | hard | User CONTENT0 | Seeds are parameters, not generation code. | medium-high | high | FACT |
| CONSTRAINT-10 | Every product always works with CLI. | product architecture | hard | User GUI decision | CLI belongs in product matrix and should share backend contract. | high | high | FACT |
| CONSTRAINT-11 | Every product is expected to work with TUI. | product architecture | strong | User GUI decision | TUI doctrine is required. | medium-high | high | FACT |
| CONSTRAINT-12 | GUIs are modular frontends attached to product backends. | architecture | hard | User GUI decision | GUI shells must not own product logic. | high | high | FACT |
| CONSTRAINT-13 | Do not treat assistant suggestions as user decisions unless accepted. | evidence/process | hard | Current user request | Keep brainstorms/tentative items labelled. | high | high | FACT |
| CONSTRAINT-14 | External-world facts/software versions/toolchain support require verification before future use. | evidence/staleness | hard | Current user request | Platform facts should be marked VERIFY before implementation. | high | high | FACT |
| CONSTRAINT-15 | Source scope is this chat only; outside context must be labelled PROJECT-CONTEXT. | scope/evidence | hard | Current user request | Do not summarize whole project. | high | high | FACT |
| CONSTRAINT-16 | Use stable IDs for registers. | format | hard | Current user request | All important items need WORKSTREAM/DECISION/etc. IDs. | medium | high | FACT |
| CONSTRAINT-17 | Windows App SDK / WinUI 3 Windows 10 1809+ support must be reverified before future use. | technical | hard for implementation | Previous packet external reference | Do not finalize WinUI lane without current docs. | medium-high | medium | UNCERTAIN / UNVERIFIED |
| CONSTRAINT-18 | .NET Framework 4.0–4.8 support requires real target/build lanes. | technical | hard for implementation | Assistant correction / external docs in previous packet | Need frozen VS/tooling for old .NET targets. | high | medium | UNCERTAIN / UNVERIFIED |
| CONSTRAINT-19 | macOS 10.9 support cannot be assumed with current Xcode; requires legacy/frozen toolchain or verification. | technical | hard for implementation | Assistant correction / external docs in previous packet | Need decide if 10.9 is real support target. | high | medium | UNCERTAIN / UNVERIFIED |
| CONSTRAINT-20 | .NET MAUI should not be treated as a complete Linux desktop solution without verification. | technical | hard for implementation | Previous packet external reference | Linux stack remains open. | medium | medium | UNCERTAIN / UNVERIFIED |

### Open Questions Register

| ID | Question / issue | Why it matters | Known information | Unknown information | What would resolve it | Priority | Related workstream | Label |
|---|---|---|---|---|---|---|---|---|
| QUESTION-01 | What is the exact backend/UI contract shape? | All CLI/TUI/GUI frontends depend on it. | GUIs must attach to product backends; CLI always works; TUI expected. | ABI vs IPC vs both; command/state/event/error/versioning/security models. | Draft candidate contract and inspect repo/backend APIs. | critical | WORKSTREAM-07 | INFERENCE |
| QUESTION-02 | Should the backend expose a stable C ABI? | Would simplify native and managed interop. | Assistant proposed it as candidate; not user-final. | Backend language, existing API shape, suitability. | Review backend architecture and compare interop options. | high | WORKSTREAM-07 | INFERENCE |
| QUESTION-03 | Is the client GUI primarily host-native, renderer-driven, or hybrid? | Client is likely performance/UX-sensitive. | User listed Win32/AppKit lanes; earlier assistant discussed renderer-driven approach. | Final rendering/UI doctrine. | Decide client requirements and architecture. | critical | WORKSTREAM-06 | UNCERTAIN / UNVERIFIED |
| QUESTION-04 | What level of TUI parity is required? | Affects backend capabilities and implementation scope. | Every product expected to work with TUI. | Full feature parity, admin parity, fallback, or per-product subset. | Define TUI doctrine by product. | high | WORKSTREAM-15 | FACT |
| QUESTION-05 | What exact Windows OS floors are targeted by each lane? | Defines support claims and toolchains. | WinUI 3 lane says Windows 10 1809 graceful degradation; Win32/WinForms floors unspecified. | Legacy Windows versions and support levels. | User decision plus current Microsoft docs. | high | WORKSTREAM-08 | FACT |
| QUESTION-06 | Which .NET Framework versions must be supported? | Determines WinForms build lanes and Visual Studio versions. | User mentioned .NET 4.8 with conditional down to 4.0; assistant corrected that real lanes are needed. | Actual required floors: 4.0, 4.5.2, 4.6.2, 4.8, etc. | User decision and official docs/toolchain verification. | high | WORKSTREAM-08 | FACT |
| QUESTION-07 | Is macOS 10.9 a hard requirement? | May require frozen legacy Xcode/SDK and old build hardware/VMs. | User named macOS 10.9; assistant warned current toolchains likely insufficient. | Hard support target vs aspirational. | User decision and Apple toolchain verification. | high | WORKSTREAM-09 | FACT |
| QUESTION-08 | Should AppKit builds target Apple silicon too? | User listed AppKit as 64-bit Intel only, but Apple silicon matters for modern macOS. | SwiftUI lane includes Intel and ARM; assistant suggested AppKit need not be Intel-only. | Final AppKit arch policy. | User decision. | high | WORKSTREAM-09 | INFERENCE |
| QUESTION-09 | What Linux GUI stack should be used? | Linux support remains undefined. | Linux in scope; same backend doctrine should apply. | Qt, GTK, Avalonia, custom renderer host, TUI-first, etc. | Compare options against goals and distro baselines. | high | WORKSTREAM-10 | FACT |
| QUESTION-10 | What is Android's product role? | Determines whether Android needs full client UI, launcher, admin companion, or tools. | Android in scope. | Role, UI stack, API floor, backend binding. | Define Android use cases before stack choice. | high | WORKSTREAM-11 | FACT |
| QUESTION-11 | What packaging forms are required per product/platform? | Affects executable/library layout and user installation. | User asked compiled vs libraries/DLLs; assistant recommended static/self-contained where useful. | Installer/portable/bundle/package/plugin decisions. | Packaging doctrine and platform matrix. | high | WORKSTREAM-12 | INFERENCE |
| QUESTION-12 | How many visual/OEM+ profiles are desired? | Controls UI consistency and matrix size. | Assistant suggested profiles rather than per-era GUIs. | Exact profile names/count/behavior. | User design decision. | medium | WORKSTREAM-14 | INFERENCE |
| QUESTION-13 | How should procedural gaps and fully defined data coexist in universe content? | Core to minimal storage/memory full-universe goal. | User wants support from fully procedural through fully architected universes. | Data model, levels of definition, provenance for gaps. | Content architecture planning. | medium | WORKSTREAM-03 | FACT |
| QUESTION-14 | What makes a celestial site 'important'? | Default Milky Way selection depends on criteria. | User listed visiting, harvesting, research, navigation, etc. | Weights, thresholds, catalog sources, scenario relevance. | Define importance taxonomy. | medium | WORKSTREAM-04 | FACT |
| QUESTION-15 | Do actual repository files exist and what do they contain? | Implementation cannot proceed from this packet alone. | Previous assistant mentioned repo/files, but this package did not inspect them. | Actual tree, existing code, schemas, build files. | Inspect uploaded repo/files in new chat. | critical before implementation | WORKSTREAM-06 | UNCERTAIN / UNVERIFIED |

### Artifact Ledger

| ID | Artifact / file / prompt / output | Type | Purpose | Status | Where it came from | Carry forward? | Notes | Label |
|---|---|---|---|---|---|---|---|---|
| ARTIFACT-01 | PROMPT CONTENT0 — CANONICAL GAME CONTENT & DATA POPULATION | user prompt | Defines data/schema/docs-only canonical content population scope. | source artifact | User first message in visible context | yes | Reproduced in prior packet; should be preserved verbatim. | FACT |
| ARTIFACT-02 | Assistant cleaned CONTENT0 prompt | assistant draft | Codex-ready rewrite of CONTENT0. | draft/superseded | Assistant response before user discussion-first correction | yes, draft only | Do not treat as accepted final prompt. | FACT |
| ARTIFACT-03 | Assistant CONTENT0 critique | assistant analysis | Lists unresolved content issues. | useful draft analysis | Assistant response after user correction | yes | Issues include schema semantics, seeds, refinement contract, timelines, conservation, knowledge uncertainty. | FACT |
| ARTIFACT-04 | User full-universe/default-Milky-Way goal statement | user planning statement | Defines long-term content/default datapack objective. | active source | User message after CONTENT0 discussion | yes | Includes procedural/full universe compatibility and importance criteria. | FACT |
| ARTIFACT-05 | Cross-platform GUI feasibility answer | assistant output | Discussed Xcode, Linux, .NET, Apple equivalents, static/dynamic packaging. | background guidance | Assistant response | yes with verification | External facts are stale-prone and need rechecking. | INFERENCE |
| ARTIFACT-06 | GUI per OS/era answer | assistant output | Recommended host integrations and visual profiles rather than per-era codebases. | background guidance | Assistant response | yes as recommendation | Not a direct user decision. | INFERENCE |
| ARTIFACT-07 | User GUI rebuild decision and frontend list | user decision | Defines current GUI/binary direction. | active source | User message starting 'Okay, I've decided...' | yes | Most important GUI artifact in chat. | FACT |
| ARTIFACT-08 | Assistant validation/correction of GUI rebuild | assistant output | Corrected WinForms/AppKit/Xcode details and normalized plan. | useful with verification | Assistant response | yes | Technical claims need re-verification before implementation. | INFERENCE |
| ARTIFACT-09 | Transfer Knowledge Base — GUI and Binary Rebuild | assistant output | Initial compact handoff for new chat. | superseded by maximum-fidelity packet but useful | Assistant response | yes, lower priority | Precursor to final packet. | FACT |
| ARTIFACT-10 | CONTEXT TRANSFER PACKET | assistant output | Maximum-fidelity state transfer generated before this package. | primary source for this final package | Assistant response immediately before current request | yes | Audited and normalized here. | FACT |
| ARTIFACT-11 | Microsoft Windows App SDK docs link | external reference | Verify WinUI 3 / Windows App SDK requirements. | requires future verification | Prior packet | yes | https://learn.microsoft.com/en-us/windows/apps/windows-app-sdk/system-requirements | UNCERTAIN / UNVERIFIED |
| ARTIFACT-12 | Microsoft Windows Forms overview link | external reference | Verify WinForms platform/framework context. | requires future verification | Prior packet | yes | https://learn.microsoft.com/en-us/dotnet/desktop/winforms/overview/ | UNCERTAIN / UNVERIFIED |
| ARTIFACT-13 | Microsoft .NET Framework versions/dependencies link | external reference | Verify .NET Framework in-place updates and VS targeting constraints. | requires future verification | Prior packet | yes | https://learn.microsoft.com/en-us/dotnet/framework/migration-guide/versions-and-dependencies | UNCERTAIN / UNVERIFIED |
| ARTIFACT-14 | Microsoft .NET MAUI supported platforms link | external reference | Verify MAUI platform support. | requires future verification | Prior packet | yes | https://learn.microsoft.com/en-us/dotnet/maui/supported-platforms | UNCERTAIN / UNVERIFIED |
| ARTIFACT-15 | Microsoft P/Invoke docs link | external reference | Verify .NET unmanaged interop. | requires future verification | Prior packet | yes | https://learn.microsoft.com/en-us/dotnet/standard/native-interop/pinvoke | UNCERTAIN / UNVERIFIED |
| ARTIFACT-16 | Microsoft Native AOT docs link | external reference | Verify .NET Native AOT packaging constraints. | requires future verification | Prior packet | yes | https://learn.microsoft.com/en-us/dotnet/core/deploying/native-aot/ | UNCERTAIN / UNVERIFIED |
| ARTIFACT-17 | Apple Xcode support page link | external reference | Verify Xcode deployment target/toolchain floors. | requires future verification | Prior packet | yes | https://developer.apple.com/support/xcode/ | UNCERTAIN / UNVERIFIED |
| ARTIFACT-18 | Uploaded repo/files | possible artifact | Implementation context if present. | uncertain/unverified | Prior assistant mentioned repo; no file inspected in this package. | yes, but verify | Do not infer sandbox paths or file contents. | UNCERTAIN / UNVERIFIED |
| ARTIFACT-19 | This final report package | generated package | Downloadable reusable chat-specific report package. | created by current response | Current user request | yes | Includes Markdown, YAML, and ZIP manifest. | FACT |

### Risk Register

| ID | Risk / failure mode | Consequence | Likelihood | Severity | Mitigation | Related workstream | Label |
|---|---|---|---|---|---|---|---|
| RISK-01 | GUI family drift | Different frontends implement different behavior. | medium | high | Define shared backend contract and test CLI/TUI/GUI against same capabilities. | WORKSTREAM-07 | INFERENCE |
| RISK-02 | Framework capture | WinForms/SwiftUI/etc. becomes product architecture instead of shell. | medium | high | Keep product logic backend-owned and shells thin. | WORKSTREAM-06 | INFERENCE |
| RISK-03 | Compatibility fraud | Claimed support for old hosts cannot be built or tested. | high | high | Require toolchain/build/test lane for every support claim. | WORKSTREAM-13 | INFERENCE |
| RISK-04 | Matrix explosion | Too many OS/arch/framework/era/style combinations to maintain. | medium-high | high | Use compatibility lanes and small visual profile set. | WORKSTREAM-14 | INFERENCE |
| RISK-05 | Premature prompt/code generation | Locks in unresolved assumptions. | medium | medium-high | Begin new chat with doctrine and matrices, not code. | WORKSTREAM-16 | FACT |
| RISK-06 | Schema behavior smuggling in CONTENT0 | Data schemas imply runtime mechanics contrary to scope. | medium | high | Limit schemas to shape, units, references, required fields; no behavior/default logic. | WORKSTREAM-01 | INFERENCE |
| RISK-07 | Fake precision in universe/content data | Content appears authoritative but is fabricated or too precise. | medium | medium-high | Use provenance, confidence, macro resolution, and sources. | WORKSTREAM-03 | INFERENCE |
| RISK-08 | Linux fragmentation | GUI/package fails across distros or display stacks. | medium | medium | Choose distro baselines and packaging formats explicitly. | WORKSTREAM-10 | INFERENCE |
| RISK-09 | macOS legacy trap | macOS 10.9 consumes disproportionate tooling effort. | medium | medium-high | Confirm whether 10.9 is hard requirement before committing. | WORKSTREAM-09 | INFERENCE |
| RISK-10 | Old .NET target trap | Supporting .NET 4.0 requires unsupported/old build tooling. | medium | medium-high | Define exact .NET floor and maintain frozen VS lane if needed. | WORKSTREAM-08 | UNCERTAIN / UNVERIFIED |
| RISK-11 | Android scope creep | Mobile project expands into full parity without clear need. | medium | medium | Define Android role first. | WORKSTREAM-11 | INFERENCE |
| RISK-12 | Over-reliance on this package without repo inspection | Future plan may not match actual files. | medium | high | Inspect repo/files before implementation. | WORKSTREAM-06 | UNCERTAIN / UNVERIFIED |
| RISK-13 | Stale platform/toolchain facts | Build matrix uses outdated support data. | medium | high | Re-verify official docs before acting. | WORKSTREAM-13 | FACT |
| RISK-14 | Treating assistant suggestions as user decisions | Spec book gains false requirements. | medium | high | Preserve labels and source hierarchy. | WORKSTREAM-16 | FACT |
| RISK-15 | Bad aggregation with other chat reports | Contradictions or duplicates are silently merged. | medium | high | Use IDs, labels, provenance, and conflict register. | WORKSTREAM-16 | FACT |

### Verification Queue

| ID | Item requiring verification | Why verification is needed | Suggested verification source/type | Priority | Related workstream | Label |
|---|---|---|---|---|---|---|
| VERIFY-01 | Confirm actual repository/file availability and structure. | Prior assistant references to repo/files are unverified here. | File upload/repo inspection | critical before implementation | WORKSTREAM-06 | UNCERTAIN / UNVERIFIED |
| VERIFY-02 | Confirm project name convention: Dominium vs Domino. | Both names appear in prompt context. | User or repo metadata | medium | WORKSTREAM-01 | UNCERTAIN / UNVERIFIED |
| VERIFY-03 | Verify current Windows App SDK / WinUI 3 system requirements and Windows 10 1809 floor. | Toolchain facts are time-sensitive. | Official Microsoft docs | high | WORKSTREAM-08 | UNCERTAIN / UNVERIFIED |
| VERIFY-04 | Verify WinForms/.NET Framework targeting support and Visual Studio versions. | Old .NET support requires real lanes. | Official Microsoft docs and installed toolchains | high | WORKSTREAM-08 | UNCERTAIN / UNVERIFIED |
| VERIFY-05 | Confirm exact .NET Framework target floors desired. | User named .NET 4.0 but support cost may be high. | User decision | high | WORKSTREAM-08 | FACT |
| VERIFY-06 | Verify current Xcode deployment targets and old SDK feasibility. | macOS 10.9 support is toolchain-sensitive. | Official Apple docs and actual Xcode/SDK availability | high | WORKSTREAM-09 | UNCERTAIN / UNVERIFIED |
| VERIFY-07 | Confirm whether macOS 10.9 is hard requirement. | Legacy macOS lane may be expensive. | User decision | high | WORKSTREAM-09 | FACT |
| VERIFY-08 | Verify .NET MAUI supported platforms if considered. | MAUI support changes over time and Linux desktop is not established here. | Official Microsoft docs | medium | WORKSTREAM-10 | UNCERTAIN / UNVERIFIED |
| VERIFY-09 | Compare Linux GUI stack current support: Qt, GTK, Avalonia, custom renderer host. | Linux stack is undecided and current package support matters. | Official docs and distro/package docs | high | WORKSTREAM-10 | UNCERTAIN / UNVERIFIED |
| VERIFY-10 | Confirm Android target role and API floor. | Android is in scope but undefined. | User decision and Android docs | high | WORKSTREAM-11 | FACT |
| VERIFY-11 | Verify Native AOT suitability for any .NET shells. | AOT limitations may conflict with plugins/reflection/dynamic loading. | Official Microsoft docs and prototype | medium | WORKSTREAM-12 | UNCERTAIN / UNVERIFIED |
| VERIFY-12 | Confirm TUI parity expectations. | 'Expected to work with TUI' is not detailed. | User decision | high | WORKSTREAM-15 | FACT |
| VERIFY-13 | Confirm whether stable C ABI is acceptable. | Candidate only; impacts all frontend integration. | User/project architecture review | critical | WORKSTREAM-07 | INFERENCE |
| VERIFY-14 | Resolve CONTENT0 schema semantic boundaries. | Descriptive schemas can accidentally imply behavior. | Schema review and user decision | medium | WORKSTREAM-01 | INFERENCE |
| VERIFY-15 | Define deterministic seed hierarchy for content. | CONTENT0 requires seeds but not seed namespace rules. | Content architecture decision | medium | WORKSTREAM-03 | FACT |
| VERIFY-16 | Define importance criteria for Milky Way celestial sites. | Default datapack selection depends on this. | Design decision and astronomical data-source review | medium | WORKSTREAM-04 | FACT |
| VERIFY-17 | Confirm current facts before final Project Spec Book aggregation. | This package includes stale-prone external references. | Official docs/current source pass | high | WORKSTREAM-16 | FACT |

## 6. Possible Cross-Chat Duplicates

- Existing GUI architecture or old frontend plans.
- Engine/runtime/backend architecture.
- Build tooling and CI strategy.
- Content schema design.
- Universe/Milky Way/Sol/Earth content prompts.
- Packaging and launcher/updater plans.

## 7. Possible Cross-Chat Conflicts

- Later chats may keep old GUI code rather than rebuilding from scratch.
- Other chats may pick a universal GUI framework.
- Other chats may claim legacy Windows/macOS support without real toolchains.
- Other chats may treat CONTENT0 as finalized.
- Other chats may decide Linux/Android stacks differently.

## 8. Spec Book Integration Guidance

Feed this chat into chapters on content doctrine, default universe/datapack, GUI/binary architecture, backend/UI contract, product surfaces, platform frontend lanes, packaging, build matrices, and verification policy. Make user decisions formal requirements; keep assistant suggestions as background or candidate designs until confirmed. Do not merge Linux/Android or C ABI choices prematurely.

## 9. Aggregator Warnings

- Do not promote INFERENCE to FACT.
- Do not merge this chat into whole-project state without source labels.
- Do not assume external platform facts are current.
- Do not assume repo/files were inspected.
- Do not drop the user's discussion-first correction.
