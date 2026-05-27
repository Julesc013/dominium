# Full Chat Report — Dominium GUI/Binary + CONTENT0 Handoff

## 0. Report Metadata

| Field | Value |
|---|---|
| Chat label | Dominium GUI/Binary + CONTENT0 Handoff |
| Filesystem-safe label | `dominium_gui_binary_content_handoff` |
| Generated date anchor | 2026-05-27 Australia/Melbourne |
| Source scope | This visible chat only. Items from project/user context outside the visible transcript are labelled PROJECT-CONTEXT. |
| Apparent coverage | Full for visible chat context and previous Context Transfer Packet; unclear for any inaccessible prior files or repository state. |
| Extraction confidence | 4 / 5 |
| Staleness risk | Medium, mainly because platform/toolchain facts change. |
| Future plans present | Yes |
| Pending tasks present | Yes |
| Artifacts/files present | Yes: prompts, assistant draft outputs, transfer packets, external-reference links, generated package files. No repository files were inspected. |
| Safe for aggregation | Yes, with caveats. |
| Main limitations | No repo/file inspection; Linux and Android remain open; external platform facts require verification; assistant suggestions are not user decisions unless separately labelled. |

## 1. Executive Summary

This chat was primarily a continuity and architecture-planning chat for the Dominium / Domino project. It contains two major workstreams: first, a content-layer planning thread around `PROMPT CONTENT0 — CANONICAL GAME CONTENT & DATA POPULATION`; second, a more developed GUI/binary/front-end rebuild thread. The content workstream established a strict data-only philosophy for canonical universe, galaxy, planetary, historical, population, civilization, economy, technology, and start-condition content. The most important content rule is causal provenance: no entity, population, city, resource, civilization, or start condition may exist without a formation, birth, construction, extraction, production, emergence, or historical explanation. The user supplied the original CONTENT0 prompt and then corrected the process after an assistant generated a polished rewrite: future work should discuss unresolved conceptual issues before planning or generating further prompts.

The content workstream also expanded into a longer-term default-universe datapack goal. The user wants an efficient universe representation that can span fully procedural universes, universes with defined regions and procedural gaps, and fully defined/architected universes. The default shipped datapack should contain the Milky Way galaxy, important stars and celestial sites selected across forms of importance such as visiting, harvesting, research, and navigation, and high-detail treatment of especially important systems including Sol. Sol and Earth remain mandatory macro-level anchors, but no final schema or data generation plan was produced in this chat.

The current active workstream became GUI and binary strategy. The user decided to redo all GUIs from scratch. For every product — setup, launcher, client, server, tools, and related products — CLI must always work, TUI is expected to work, and multiple modular GUIs should attach to product backends to compile native applications. This implies a shared backend/UI contract that all CLI, TUI, and GUI shells consume. The exact contract shape is unresolved and is the first major next decision: it could involve in-process ABI, IPC, or both, and a stable C ABI was suggested by the assistant only as a candidate, not as a user-final decision.

For Windows, the user proposed a frontend selection: Win32 ANSI for 32-bit Intel setup/client; Win32 Unicode for 64-bit Intel and ARM setup/client; WinForms .NET Framework for 32/64-bit Intel launcher/server, originally described as .NET 4.8 with conditional support down to .NET 4.0 machines; and WinUI 3 for 64-bit Intel and ARM launcher/server with graceful degradation to Windows 10 1809. The assistant flagged that .NET old-version support cannot be treated as one later-targeting binary; real target/build lanes would be needed. For macOS, the user proposed AppKit for setup/launcher/client/server down to macOS 10.9 and SwiftUI for future launcher/server down to around macOS 11, including Intel and ARM for SwiftUI. The assistant flagged that true macOS 10.9 support likely requires frozen legacy Apple tooling and that AppKit need not be Intel-only. Linux and Android were included by the user but left open: Linux should follow the same backend/thin-shell doctrine, and Android should be treated as a mobile host family rather than desktop scaled down.

The most important carry-forward rule is that assistant suggestions must not be treated as user decisions. The user explicitly wants uncertainty labels, preservation of rejected and superseded options, and clear separation of facts, inferences, and unverified claims. Platform/toolchain facts are stale-prone and must be reverified before implementation. The next chat should not begin coding. It should first produce a GUI/binary architecture doctrine, then product matrix, platform matrices, compatibility lanes, visual profiles, packaging model, build/toolchain matrix, and verification plan.

## 2. How to Use This Report

This report covers only this old chat. It is not a master project specification and must not be treated as a complete summary of the whole Dominium / Domino project. Use it as a chat-specific evidence packet for future planning and later aggregation.

Source hierarchy:

1. Direct user statements in this chat.
2. User-supplied prompts in this chat.
3. Later user corrections and changes of direction.
4. Assistant outputs, only as drafts, analysis, or recommendations unless explicitly accepted.
5. External links and platform/toolchain facts, which require re-verification before implementation.
6. Inferences in this package, which must not be promoted to requirements without user/project confirmation.

Uncertain items must not be treated as facts. Stale facts about software versions, APIs, toolchains, OS support, products, laws, or institutional rules require current verification before future use. Tentative decisions remain tentative. This report is structured for later master-spec aggregation, so preserve IDs and labels when merging.

## 3. User Preferences Visible in This Chat

### 3.1 Explicit Preferences

| ID | Preference | Category | Source basis | Strength | Implication | Risk if misunderstood | Label |
|---|---|---|---|---|---|---|---|
| PREFERENCE-01 | Discuss before planning or generating prompts when conceptual ambiguity exists. | explicit | User message after initial CONTENT0 rewrite | high | Do discussion/issue resolution first. | Premature prompt/code output may lock wrong assumptions. | FACT |
| PREFERENCE-02 | Maximum-fidelity state transfer rather than normal summary. | explicit | User context-transfer request | high | Preserve decisions, constraints, artifacts, contradictions, and uncertainty. | Over-compression loses reusable project state. | FACT |
| PREFERENCE-03 | Label facts, inferences, and uncertainty explicitly. | explicit | Current and previous transfer-packet prompts | high | Registers must use FACT / INFERENCE / UNCERTAIN / PROJECT-CONTEXT. | Future assistants may promote guesses to decisions. | FACT |
| PREFERENCE-05 | Structured headings, tables, stable IDs, and reusable files. | explicit | Current request | high | Use normalized registers and package files. | Unstructured prose is hard to aggregate. | FACT |
| PREFERENCE-06 | Avoid treating brainstorms or assistant suggestions as decisions. | explicit | Current request | high | Preserve tentative status. | Spec book may contain false commitments. | FACT |

### 3.2 Inferred Preferences

| ID | Preference | Category | Source basis | Strength | Implication | Risk if misunderstood | Label |
|---|---|---|---|---|---|---|---|
| PREFERENCE-07 | Prefer rigorous challenge of feasibility over agreeable answers. | inferred | User accepted/asked about Xcode/.NET/Linux limitations; profile reinforces | medium-high | Correct technical framing when evidence conflicts. | Bad support claims enter build matrix. | INFERENCE |

### 3.3 Preferences Not Established by This Chat

The user profile outside the visible transcript states additional preferences such as direct, source-grounded, audit-ready answers and explicit uncertainty. In this package those are labelled PROJECT-CONTEXT, not visible-chat facts.

| ID | Preference | Category | Source basis | Strength | Implication | Risk if misunderstood | Label |
|---|---|---|---|---|---|---|---|
| PREFERENCE-04 | Direct, source-grounded, audit-ready answers with explicit uncertainty. | project-context | User profile outside visible chat | high | Use citations/verification and confidence labels. | Unsupported claims will reduce trust. | PROJECT-CONTEXT |

## 4. Complete Topic and Workstream Inventory

| ID | Name | Objective | Current state | Desired end state | Status | Priority | Confidence | Label |
|---|---|---|---|---|---|---|---|---|
| WORKSTREAM-01 | CONTENT0 canonical content population | Populate Dominium/Domino canonical universe, civilization, economy, history, population, technology, and start-condition content through data, schemas, and docs only. | User supplied CONTENT0 prompt; assistant produced a draft rewrite; user redirected to discussion-first before more prompting. | Data-driven canonical content with Sol and Earth macro-defined, all major structures documented, no entity appearing without origin/provenance. | active but paused | medium-high | high | FACT |
| WORKSTREAM-02 | CONTENT0 prompt refinement and discussion-first process | Refine the content-generation prompt only after unresolved conceptual issues are discussed. | Assistant draft exists but is not accepted as final. | A Codex-ready prompt that preserves data-only scope, provenance, deterministic seeds, and refinable macro content. | active / draft | medium | high | FACT |
| WORKSTREAM-03 | Full-universe/default datapack architecture | Plan a universe representation that is efficient in storage and memory and supports fully procedural, partially defined with procedural gaps, and fully defined/architected universes. | Goal stated by user; no finalized architecture. | A scalable content model with explicit definition levels, procedural gaps, provenance, and refinement paths. | active concept | medium | high | FACT |
| WORKSTREAM-04 | Default Milky Way datapack | Define the default shipped datapack containing the Milky Way and the galaxy's most important stars, systems, and celestial sites. | User goal stated; selection criteria unresolved. | Milky Way data with important visiting, harvesting, research, navigation, and other sites selected by explicit criteria. | active concept | medium | high | FACT |
| WORKSTREAM-05 | Sol system canonical data | Define the Sol system and its important celestial bodies, structures, satellites, belts, fields, and points. | Mandatory in CONTENT0 and emphasized by user; not implemented here. | Macro-complete, refinable Sol system with formation history, orbital/domain data, visitability rules, and provenance. | required / unresolved | medium-high | high | FACT |
| WORKSTREAM-06 | GUI and binary rebuild | Redo all GUIs from scratch across products while preserving CLI, expected TUI, and modular GUI frontends attached to shared backends. | Current main workstream; explicit user decision made. | A coherent multi-platform frontend/binary strategy for setup, launcher, client, server, and tools. | active | critical | high | FACT |
| WORKSTREAM-07 | Shared backend/UI contract | Define the shared contract consumed by CLI, TUI, and GUI frontends so product logic stays backend-owned. | Recognized as the first unresolved design issue; no shape finalized. | Stable command/state/event/error/versioning model exposed through suitable in-process ABI, IPC, or both. | active / unresolved | critical | medium-high | INFERENCE |
| WORKSTREAM-08 | Windows frontend family matrix | Plan Windows GUI/build lanes: Win32 ANSI, Win32 Unicode, WinForms compatibility family, and WinUI 3 modern family. | User proposed families; assistant corrected feasibility issues around .NET Framework targeting. | Explicit Windows matrix by product, architecture, OS floor, framework/runtime, toolchain, packaging, and support level. | partially specified | high | high | FACT |
| WORKSTREAM-09 | macOS frontend family matrix | Plan macOS GUI/build lanes using AppKit and SwiftUI with explicit deployment floors and toolchains. | User proposed AppKit and SwiftUI lanes; assistant identified macOS 10.9/frozen-toolchain issue. | Explicit macOS matrix by product, architecture, macOS floor, Xcode/SDK version, packaging/signing, and support level. | partially specified | high | high | FACT |
| WORKSTREAM-10 | Linux frontend strategy | Define Linux GUI/build lanes consistent with backend-contract/thin-shell doctrine. | In scope but exact stack undecided. | Linux frontend strategy with distro baseline, toolkit/renderer choice, packaging forms, and support policy. | open | high | high | FACT |
| WORKSTREAM-11 | Android frontend strategy | Define Android role and frontend strategy under the same backend doctrine where appropriate. | In scope but exact strategy undecided. | Android-specific product role and UI/package plan, not merely desktop scaled down. | open | medium-high | high | FACT |
| WORKSTREAM-12 | Packaging, linking, and distribution doctrine | Decide per-product/per-platform packaging forms, static vs dynamic linking, plugin/library boundaries, installers, and portable artifacts. | Partially discussed; no final matrix. | Clear packaging model by product and platform with support/test implications. | open / partially discussed | high | medium | INFERENCE |
| WORKSTREAM-13 | Build, toolchain, and CI matrix | Create a formal build matrix across OS, architecture, framework/runtime, toolchain, packaging, signing, and support status. | Recognized as necessary; not built. | Auditable matrix mapping every support claim to a build lane and test lane. | open | high | medium-high | INFERENCE |
| WORKSTREAM-14 | Visual profile and OEM+ system | Use a small set of visual/behavior profiles rather than separate GUI codebases per OS era. | Assistant recommendation; user did not explicitly lock exact profile set. | Defined profile set such as classic/OEM+/modern/reduced-admin with clear behavior and visual differences. | recommended / unresolved | medium-high | medium | INFERENCE |
| WORKSTREAM-15 | TUI doctrine | Define what 'expected to work with TUI' means for every product. | Requirement stated; parity level unresolved. | TUI scope and parity rules mapped to backend contract and product matrix. | open | high | high | FACT |
| WORKSTREAM-16 | Per-chat context transfer and report package | Create a downloadable, shareable, reusable report package for this old chat. | This response generates the package. | Markdown/YAML report files and ZIP package usable for future aggregation. | active / being completed | critical | high | FACT |

## 5. Detailed Workstream State


### WORKSTREAM-01 — CONTENT0 canonical content population
- Label: FACT
- Objective: Populate Dominium/Domino canonical universe, civilization, economy, history, population, technology, and start-condition content through data, schemas, and docs only.
- Background: CONTENT0 targets GPT-5.2 CODEX and is scoped to data/, schema/, docs/ only.
- Current state: User supplied CONTENT0 prompt; assistant produced a draft rewrite; user redirected to discussion-first before more prompting.
- Desired end state: Data-driven canonical content with Sol and Earth macro-defined, all major structures documented, no entity appearing without origin/provenance.
- Importance: Sets the rules for content authorship and prevents fabricated gameplay state.
- Decisions made: DECISION-01: CONTENT0 work is content-layer only: data/, schema/, docs/; no engine/runtime/code logic changes.; DECISION-02: No entity/population/city/resource/civilization/start may appear without explicit causal origin/provenance.
- Decisions pending: not separately identified
- Pending tasks: none explicitly identified
- Constraints: CONSTRAINT-01: CONTENT0 may touch only data/, schema/, docs/.; CONSTRAINT-02: CONTENT0 must not change engine code, runtime logic, execution, ECS, domains, authority, or time models.; CONSTRAINT-03: No entity exists unless created by explicit process.; CONSTRAINT-04: No population exists unless born.; CONSTRAINT-05: No city exists unless built.; CONSTRAINT-06: No resource exists unless extracted or produced.; CONSTRAINT-07: No civilization exists unless it emerged historically.; CONSTRAINT-08: Macro content may exist without micro simulation, but must be refinable.; CONSTRAINT-09: Use deterministic seeds for universe/galaxy content; no procedural generation logic in data prompts.
- Dependencies: backend contract, product matrix, and verified toolchain data
- Timeline / sequencing: No calendar date established
- Blockers: Conceptual decisions unresolved
- Risks: RISK-06: Schema behavior smuggling in CONTENT0
- Artifacts: ARTIFACT-01: PROMPT CONTENT0 — CANONICAL GAME CONTENT & DATA POPULATION; ARTIFACT-02: Assistant cleaned CONTENT0 prompt; ARTIFACT-03: Assistant CONTENT0 critique
- Success criteria: Defined in objective and desired end state
- Recommended next action: Define pending decisions before implementation
- Verification needed: VERIFY-02: Confirm project name convention: Dominium vs Domino.; VERIFY-14: Resolve CONTENT0 schema semantic boundaries.
- Confidence: high
- Carry-forward priority: medium-high
### WORKSTREAM-02 — CONTENT0 prompt refinement and discussion-first process
- Label: FACT
- Objective: Refine the content-generation prompt only after unresolved conceptual issues are discussed.
- Background: User explicitly said, 'First, let's discuss this before we plan or generate any prompts.'
- Current state: Assistant draft exists but is not accepted as final.
- Desired end state: A Codex-ready prompt that preserves data-only scope, provenance, deterministic seeds, and refinable macro content.
- Importance: Prevents hidden assumptions from being embedded into generated data/schemas/docs.
- Decisions made: DECISION-03: Discuss before generating more prompts.
- Decisions pending: not separately identified
- Pending tasks: TASK-13: Resolve CONTENT0 conceptual issues before final prompt generation.
- Constraints: see constraint register
- Dependencies: backend contract, product matrix, and verified toolchain data
- Timeline / sequencing: No calendar date established
- Blockers: Conceptual decisions unresolved
- Risks: see risk register
- Artifacts: see artifact ledger
- Success criteria: Defined in objective and desired end state
- Recommended next action: Use the ten issue list as agenda
- Verification needed: see verification queue
- Confidence: high
- Carry-forward priority: medium
### WORKSTREAM-03 — Full-universe/default datapack architecture
- Label: FACT
- Objective: Plan a universe representation that is efficient in storage and memory and supports fully procedural, partially defined with procedural gaps, and fully defined/architected universes.
- Background: User wants an 'optimally large macro prompt plan' that can eventually support a full universe.
- Current state: Goal stated by user; no finalized architecture.
- Desired end state: A scalable content model with explicit definition levels, procedural gaps, provenance, and refinement paths.
- Importance: Determines whether the content layer can scale beyond hand-authored Sol/Earth data.
- Decisions made: none finalized in this chat
- Decisions pending: QUESTION-13: How should procedural gaps and fully defined data coexist in universe content?
- Pending tasks: TASK-14: Define universe procedural-gap representation and importance taxonomy.
- Constraints: see constraint register
- Dependencies: backend contract, product matrix, and verified toolchain data
- Timeline / sequencing: No calendar date established
- Blockers: Conceptual decisions unresolved
- Risks: RISK-07: Fake precision in universe/content data
- Artifacts: see artifact ledger
- Success criteria: Defined in objective and desired end state
- Recommended next action: Define levels of definition and importance dimensions
- Verification needed: VERIFY-15: Define deterministic seed hierarchy for content.
- Confidence: high
- Carry-forward priority: medium
### WORKSTREAM-04 — Default Milky Way datapack
- Label: FACT
- Objective: Define the default shipped datapack containing the Milky Way and the galaxy's most important stars, systems, and celestial sites.
- Background: User specifically named the Milky Way as default shipped content.
- Current state: User goal stated; selection criteria unresolved.
- Desired end state: Milky Way data with important visiting, harvesting, research, navigation, and other sites selected by explicit criteria.
- Importance: Core canonical galaxy content for Dominium.
- Decisions made: DECISION-04: Default shipped datapack should include the Milky Way galaxy.
- Decisions pending: QUESTION-14: What makes a celestial site 'important'?
- Pending tasks: none explicitly identified
- Constraints: see constraint register
- Dependencies: backend contract, product matrix, and verified toolchain data
- Timeline / sequencing: No calendar date established
- Blockers: Conceptual decisions unresolved
- Risks: see risk register
- Artifacts: see artifact ledger
- Success criteria: Defined in objective and desired end state
- Recommended next action: Define pending decisions before implementation
- Verification needed: VERIFY-16: Define importance criteria for Milky Way celestial sites.
- Confidence: high
- Carry-forward priority: medium
### WORKSTREAM-05 — Sol system canonical data
- Label: FACT
- Objective: Define the Sol system and its important celestial bodies, structures, satellites, belts, fields, and points.
- Background: CONTENT0 makes Sol mandatory; user specifically included Sol among key systems.
- Current state: Mandatory in CONTENT0 and emphasized by user; not implemented here.
- Desired end state: Macro-complete, refinable Sol system with formation history, orbital/domain data, visitability rules, and provenance.
- Importance: Likely default anchor system for starts and Earth/humanity content.
- Decisions made: DECISION-05: Sol system must be included and specially defined among important systems.
- Decisions pending: not separately identified
- Pending tasks: none explicitly identified
- Constraints: see constraint register
- Dependencies: backend contract, product matrix, and verified toolchain data
- Timeline / sequencing: No calendar date established
- Blockers: Conceptual decisions unresolved
- Risks: see risk register
- Artifacts: see artifact ledger
- Success criteria: Defined in objective and desired end state
- Recommended next action: Define pending decisions before implementation
- Verification needed: see verification queue
- Confidence: high
- Carry-forward priority: medium-high
### WORKSTREAM-06 — GUI and binary rebuild
- Label: FACT
- Objective: Redo all GUIs from scratch across products while preserving CLI, expected TUI, and modular GUI frontends attached to shared backends.
- Background: User decided to rebuild GUIs and listed Windows/macOS lanes; Linux/Android remain open.
- Current state: Current main workstream; explicit user decision made.
- Desired end state: A coherent multi-platform frontend/binary strategy for setup, launcher, client, server, and tools.
- Importance: Defines product operability, compatibility, packaging, and long-term maintainability.
- Decisions made: DECISION-06: Redo GUIs from scratch.; DECISION-07: Every product must always work with CLI.
- Decisions pending: QUESTION-03: Is the client GUI primarily host-native, renderer-driven, or hybrid?; QUESTION-15: Do actual repository files exist and what do they contain?
- Pending tasks: TASK-01: Define GUI/binary architecture doctrine.; TASK-03: Build product matrix for setup, launcher, client, server, and tools.; TASK-12: Inspect actual repository/files before implementation.
- Constraints: CONSTRAINT-10: Every product always works with CLI.; CONSTRAINT-11: Every product is expected to work with TUI.; CONSTRAINT-12: GUIs are modular frontends attached to product backends.
- Dependencies: backend contract, product matrix, and verified toolchain data
- Timeline / sequencing: Immediate first-phase item
- Blockers: Backend contract unresolved
- Risks: RISK-02: Framework capture; RISK-12: Over-reliance on this package without repo inspection
- Artifacts: ARTIFACT-05: Cross-platform GUI feasibility answer; ARTIFACT-06: GUI per OS/era answer; ARTIFACT-07: User GUI rebuild decision and frontend list; ARTIFACT-08: Assistant validation/correction of GUI rebuild; ARTIFACT-09: Transfer Knowledge Base — GUI and Binary Rebuild; ARTIFACT-10: CONTEXT TRANSFER PACKET
- Success criteria: Defined in objective and desired end state
- Recommended next action: Produce first in new chat before code
- Verification needed: VERIFY-01: Confirm actual repository/file availability and structure.
- Confidence: high
- Carry-forward priority: critical
### WORKSTREAM-07 — Shared backend/UI contract
- Label: INFERENCE
- Objective: Define the shared contract consumed by CLI, TUI, and GUI frontends so product logic stays backend-owned.
- Background: The modular-GUI plan implies a common contract beneath every frontend.
- Current state: Recognized as the first unresolved design issue; no shape finalized.
- Desired end state: Stable command/state/event/error/versioning model exposed through suitable in-process ABI, IPC, or both.
- Importance: Prevents GUI family drift and duplicate product behavior.
- Decisions made: DECISION-09: Products will have multiple modular GUIs attached to product backends to compile native applications.; DECISION-16: Stable C ABI / interop boundary is a candidate backend-contract approach, not a final decision.
- Decisions pending: QUESTION-01: What is the exact backend/UI contract shape?; QUESTION-02: Should the backend expose a stable C ABI?
- Pending tasks: TASK-02: Define backend/UI contract shape.
- Constraints: see constraint register
- Dependencies: backend contract, product matrix, and verified toolchain data
- Timeline / sequencing: Immediate first-phase item
- Blockers: Backend contract unresolved
- Risks: RISK-01: GUI family drift
- Artifacts: see artifact ledger
- Success criteria: Defined in objective and desired end state
- Recommended next action: Draft candidate contract model and identify repo facts needed
- Verification needed: VERIFY-13: Confirm whether stable C ABI is acceptable.
- Confidence: medium-high
- Carry-forward priority: critical
### WORKSTREAM-08 — Windows frontend family matrix
- Label: FACT
- Objective: Plan Windows GUI/build lanes: Win32 ANSI, Win32 Unicode, WinForms compatibility family, and WinUI 3 modern family.
- Background: Windows lane has the most detailed user-provided stack list.
- Current state: User proposed families; assistant corrected feasibility issues around .NET Framework targeting.
- Desired end state: Explicit Windows matrix by product, architecture, OS floor, framework/runtime, toolchain, packaging, and support level.
- Importance: Windows likely has the most legacy/modern compatibility complexity.
- Decisions made: DECISION-10: Windows frontend family list includes Win32 ANSI x86, Win32 Unicode x64/ARM64, WinForms .NET Framework family, and WinUI 3 x64/ARM64.; DECISION-11: WinForms old-framework support must use real distinct target/build lanes, not a single .NET 4.8 binary claiming .NET 4.0 support.
- Decisions pending: QUESTION-05: What exact Windows OS floors are targeted by each lane?; QUESTION-06: Which .NET Framework versions must be supported?
- Pending tasks: TASK-04: Build Windows frontend/build matrix.
- Constraints: see constraint register
- Dependencies: backend contract, product matrix, and verified toolchain data
- Timeline / sequencing: No calendar date established
- Blockers: Platform/toolchain decisions unresolved
- Risks: RISK-10: Old .NET target trap
- Artifacts: see artifact ledger
- Success criteria: Defined in objective and desired end state
- Recommended next action: Normalize user-proposed Windows families
- Verification needed: VERIFY-03: Verify current Windows App SDK / WinUI 3 system requirements and Windows 10 1809 floor.; VERIFY-04: Verify WinForms/.NET Framework targeting support and Visual Studio versions.; VERIFY-05: Confirm exact .NET Framework target floors desired.
- Confidence: high
- Carry-forward priority: high
### WORKSTREAM-09 — macOS frontend family matrix
- Label: FACT
- Objective: Plan macOS GUI/build lanes using AppKit and SwiftUI with explicit deployment floors and toolchains.
- Background: User wants AppKit for setup/launcher/client/server and SwiftUI for future launcher/server.
- Current state: User proposed AppKit and SwiftUI lanes; assistant identified macOS 10.9/frozen-toolchain issue.
- Desired end state: Explicit macOS matrix by product, architecture, macOS floor, Xcode/SDK version, packaging/signing, and support level.
- Importance: Mac support depends heavily on Xcode/SDK deployment floors.
- Decisions made: DECISION-12: macOS frontend family list includes AppKit and SwiftUI.; DECISION-13: macOS 10.9 AppKit support requires a frozen legacy Apple toolchain unless later verified otherwise.
- Decisions pending: QUESTION-07: Is macOS 10.9 a hard requirement?; QUESTION-08: Should AppKit builds target Apple silicon too?
- Pending tasks: TASK-05: Build macOS frontend/build matrix.
- Constraints: see constraint register
- Dependencies: backend contract, product matrix, and verified toolchain data
- Timeline / sequencing: No calendar date established
- Blockers: Platform/toolchain decisions unresolved
- Risks: RISK-09: macOS legacy trap
- Artifacts: see artifact ledger
- Success criteria: Defined in objective and desired end state
- Recommended next action: Clarify whether macOS 10.9 is hard requirement
- Verification needed: VERIFY-06: Verify current Xcode deployment targets and old SDK feasibility.; VERIFY-07: Confirm whether macOS 10.9 is hard requirement.
- Confidence: high
- Carry-forward priority: high
### WORKSTREAM-10 — Linux frontend strategy
- Label: FACT
- Objective: Define Linux GUI/build lanes consistent with backend-contract/thin-shell doctrine.
- Background: User said Linux will do something similar; assistant recommended not copying Windows stack count blindly.
- Current state: In scope but exact stack undecided.
- Desired end state: Linux frontend strategy with distro baseline, toolkit/renderer choice, packaging forms, and support policy.
- Importance: Linux support can fragment quickly without clear baselines.
- Decisions made: DECISION-14: Linux and Android are in scope but exact GUI stacks are open.
- Decisions pending: QUESTION-09: What Linux GUI stack should be used?
- Pending tasks: TASK-06: Choose Linux GUI stack/lane model.
- Constraints: see constraint register
- Dependencies: see task register
- Timeline / sequencing: No calendar date established
- Blockers: Platform/toolchain decisions unresolved
- Risks: RISK-08: Linux fragmentation
- Artifacts: see artifact ledger
- Success criteria: Defined in objective and desired end state
- Recommended next action: Compare Qt, GTK, Avalonia, custom renderer host, and TUI-first approaches
- Verification needed: VERIFY-08: Verify .NET MAUI supported platforms if considered.; VERIFY-09: Compare Linux GUI stack current support: Qt, GTK, Avalonia, custom renderer host.
- Confidence: high
- Carry-forward priority: high
### WORKSTREAM-11 — Android frontend strategy
- Label: FACT
- Objective: Define Android role and frontend strategy under the same backend doctrine where appropriate.
- Background: User said Android similar again; assistant noted mobile should be treated as a distinct host family.
- Current state: In scope but exact strategy undecided.
- Desired end state: Android-specific product role and UI/package plan, not merely desktop scaled down.
- Importance: Avoids inappropriate desktop assumptions and mobile scope creep.
- Decisions made: DECISION-14: Linux and Android are in scope but exact GUI stacks are open.
- Decisions pending: QUESTION-10: What is Android's product role?
- Pending tasks: TASK-07: Define Android product role and frontend approach.
- Constraints: see constraint register
- Dependencies: see task register
- Timeline / sequencing: No calendar date established
- Blockers: Platform/toolchain decisions unresolved
- Risks: RISK-11: Android scope creep
- Artifacts: see artifact ledger
- Success criteria: Defined in objective and desired end state
- Recommended next action: Decide Android role before toolkit selection
- Verification needed: VERIFY-10: Confirm Android target role and API floor.
- Confidence: high
- Carry-forward priority: medium-high
### WORKSTREAM-12 — Packaging, linking, and distribution doctrine
- Label: INFERENCE
- Objective: Decide per-product/per-platform packaging forms, static vs dynamic linking, plugin/library boundaries, installers, and portable artifacts.
- Background: User asked whether code compiles into executables or separate libraries/DLLs; assistant advised static/self-contained where it reduces deployment complexity.
- Current state: Partially discussed; no final matrix.
- Desired end state: Clear packaging model by product and platform with support/test implications.
- Importance: Deployment model affects compatibility, updates, memory/storage, and debugging.
- Decisions made: none finalized in this chat
- Decisions pending: QUESTION-11: What packaging forms are required per product/platform?
- Pending tasks: TASK-10: Define packaging/linking doctrine.
- Constraints: see constraint register
- Dependencies: see task register
- Timeline / sequencing: No calendar date established
- Blockers: Platform/toolchain decisions unresolved
- Risks: see risk register
- Artifacts: see artifact ledger
- Success criteria: Defined in objective and desired end state
- Recommended next action: Separate static/self-contained vs dynamic/plugin cases
- Verification needed: VERIFY-11: Verify Native AOT suitability for any .NET shells.
- Confidence: medium
- Carry-forward priority: high
### WORKSTREAM-13 — Build, toolchain, and CI matrix
- Label: INFERENCE
- Objective: Create a formal build matrix across OS, architecture, framework/runtime, toolchain, packaging, signing, and support status.
- Background: Legacy support for .NET and macOS requires real toolchains.
- Current state: Recognized as necessary; not built.
- Desired end state: Auditable matrix mapping every support claim to a build lane and test lane.
- Importance: Prevents compatibility fraud.
- Decisions made: none finalized in this chat
- Decisions pending: not separately identified
- Pending tasks: TASK-11: Define build/toolchain/CI matrix.
- Constraints: see constraint register
- Dependencies: see task register
- Timeline / sequencing: No calendar date established
- Blockers: Platform/toolchain decisions unresolved
- Risks: RISK-03: Compatibility fraud; RISK-13: Stale platform/toolchain facts
- Artifacts: see artifact ledger
- Success criteria: Defined in objective and desired end state
- Recommended next action: Verify official docs before finalizing
- Verification needed: see verification queue
- Confidence: medium-high
- Carry-forward priority: high
### WORKSTREAM-14 — Visual profile and OEM+ system
- Label: INFERENCE
- Objective: Use a small set of visual/behavior profiles rather than separate GUI codebases per OS era.
- Background: Earlier discussion asked whether separate GUIs were needed per era; assistant recommended profiles.
- Current state: Assistant recommendation; user did not explicitly lock exact profile set.
- Desired end state: Defined profile set such as classic/OEM+/modern/reduced-admin with clear behavior and visual differences.
- Importance: Limits matrix explosion while preserving native-ish feel.
- Decisions made: DECISION-15: Do not make one separate GUI per OS version/era by default; use compatibility lanes and visual profiles.
- Decisions pending: QUESTION-12: How many visual/OEM+ profiles are desired?
- Pending tasks: TASK-09: Define visual profile/OEM+ system.
- Constraints: see constraint register
- Dependencies: see task register
- Timeline / sequencing: No calendar date established
- Blockers: Platform/toolchain decisions unresolved
- Risks: RISK-04: Matrix explosion
- Artifacts: see artifact ledger
- Success criteria: Defined in objective and desired end state
- Recommended next action: Draft classic/OEM+/modern/reduced-admin candidates
- Verification needed: see verification queue
- Confidence: medium
- Carry-forward priority: medium-high
### WORKSTREAM-15 — TUI doctrine
- Label: FACT
- Objective: Define what 'expected to work with TUI' means for every product.
- Background: User explicitly said products are expected to work with TUI.
- Current state: Requirement stated; parity level unresolved.
- Desired end state: TUI scope and parity rules mapped to backend contract and product matrix.
- Importance: TUI may be central for server/admin/headless workflows.
- Decisions made: DECISION-08: Every product is expected to work with TUI.
- Decisions pending: QUESTION-04: What level of TUI parity is required?
- Pending tasks: TASK-08: Define TUI doctrine and parity level.
- Constraints: see constraint register
- Dependencies: see task register
- Timeline / sequencing: No calendar date established
- Blockers: Platform/toolchain decisions unresolved
- Risks: see risk register
- Artifacts: see artifact ledger
- Success criteria: Defined in objective and desired end state
- Recommended next action: Classify TUI as full parity, admin parity, or fallback per product
- Verification needed: VERIFY-12: Confirm TUI parity expectations.
- Confidence: high
- Carry-forward priority: high
### WORKSTREAM-16 — Per-chat context transfer and report package
- Label: FACT
- Objective: Create a downloadable, shareable, reusable report package for this old chat.
- Background: User requested maximum-fidelity package with registers, manifest, verification/audit, and spec sheet.
- Current state: This response generates the package.
- Desired end state: Markdown/YAML report files and ZIP package usable for future aggregation.
- Importance: Preserves continuity and enables later master spec construction.
- Decisions made: DECISION-17: Use this chat-specific report package for future aggregation.
- Decisions pending: not separately identified
- Pending tasks: TASK-15: Use generated report package in future aggregation.
- Constraints: see constraint register
- Dependencies: see task register
- Timeline / sequencing: Immediate first-phase item
- Blockers: Platform/toolchain decisions unresolved
- Risks: RISK-05: Premature prompt/code generation; RISK-14: Treating assistant suggestions as user decisions; RISK-15: Bad aggregation with other chat reports
- Artifacts: ARTIFACT-10: CONTEXT TRANSFER PACKET; ARTIFACT-19: This final report package
- Success criteria: Usable, auditable package files created
- Recommended next action: Store Markdown/YAML/ZIP together
- Verification needed: VERIFY-17: Confirm current facts before final Project Spec Book aggregation.
- Confidence: high
- Carry-forward priority: critical

## 6. Chronological Timeline

| Sequence | Event / topic | What changed or was decided | Why it mattered | Current relevance | Confidence |
|---|---|---|---|---|---|
| 01 | User supplied CONTENT0 prompt | Established content-layer-only canonical data population scope. | Defines universe/civilization/economy/history content philosophy. | Preserve as source artifact. | high |
| 02 | Assistant generated cleaned CONTENT0 prompt | Created a polished Codex-style prompt draft. | Potentially useful but premature. | Draft only; superseded by user process correction. | high |
| 03 | User said to discuss before planning/generating prompts | Changed process from prompt-generation to discussion-first. | Prevents hidden assumptions. | High; controls future content-prompt work. | high |
| 04 | Assistant critiqued CONTENT0 | Identified unresolved conceptual issues. | Provides agenda for content refinement. | Medium-high if content work resumes. | high |
| 05 | User defined full-universe/default-Milky-Way goal | Expanded content ambition to efficient full-universe data model and default pack. | Sets long-term content architecture. | Medium-high. | high |
| 06 | User asked GUI compatibility questions | Shifted focus to cross-platform GUIs, Xcode, Linux, .NET, packaging. | Introduced GUI/binary planning workstream. | High for current work. | high |
| 07 | Assistant advised cross-platform GUI approach | Recommended core-first, Xcode for Apple only, .NET thin shells, static/dynamic tradeoffs. | Background rationale for later GUI matrix. | Useful with verification. | medium |
| 08 | User asked about GUI per OS and per era | Clarified desire to understand matrix scope. | Led to profile/lane recommendation. | High for avoiding matrix explosion. | high |
| 09 | Assistant recommended one architecture plus host integrations/profiles | Suggested profiles rather than one GUI per era. | Controls complexity. | Useful as recommendation. | medium |
| 10 | User decided to redo GUIs from scratch and listed platform frontends | Established current GUI/binary direction. | Main active workstream. | Critical. | high |
| 11 | Assistant corrected Windows/macOS feasibility details | Flagged .NET old-target and macOS 10.9 toolchain problems. | Prevents compatibility fraud. | High, but needs future verification. | medium |
| 12 | User requested massive knowledge base | Requested transfer material for new chat. | Led to first handoff artifact. | Superseded by this final package but useful. | high |
| 13 | Assistant produced Transfer Knowledge Base | Compiled GUI/binary handoff. | Precursor to context packet. | Background artifact. | high |
| 14 | User requested maximum-fidelity Context Transfer Packet | Demanded full state transfer with registers, uncertainty labels, and audit. | Created primary context packet. | Primary source for this package. | high |
| 15 | Assistant produced Context Transfer Packet | Organized chat into workstreams, decisions, tasks, constraints, questions, artifacts, risks. | Foundation for downloadable package. | Critical. | high |
| 16 | User requested final downloadable report package | Current task: normalize, repair, create files and ZIP. | Makes the handoff reusable and aggregatable. | Critical. | high |

## 7. Decisions

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

The highest-impact decisions are DECISION-06 through DECISION-09: the GUIs are being redone from scratch; CLI is mandatory; TUI is expected; and modular GUIs attach to shared backends. These collectively imply WORKSTREAM-07, the backend/UI contract, as the first architectural issue to resolve. DECISION-01 through DECISION-03 govern the separate content workstream: CONTENT0 is data/schema/docs only, provenance is mandatory, and further prompt generation should wait until conceptual issues are discussed.

## 8. Pending Tasks and Next Actions

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

### 8.1 Recommended Task Order

1. TASK-01 — Define GUI/binary architecture doctrine.
2. TASK-02 — Define backend/UI contract shape.
3. TASK-03 — Build product matrix.
4. TASK-04 and TASK-05 — Build Windows/macOS matrices.
5. TASK-06 and TASK-07 — Define Linux and Android strategies.
6. TASK-08 — Define TUI doctrine.
7. TASK-09 through TASK-11 — Define visual profiles, packaging, and build/CI matrix.
8. TASK-12 — Inspect repo/files before implementation.
9. TASK-13 and TASK-14 — Resume content/universe work when desired.
10. TASK-15 — Use this package for later aggregation.

### 8.2 Blocked Tasks

TASK-04, TASK-05, TASK-06, TASK-07, TASK-10, and TASK-11 are blocked or partially blocked by TASK-02 and by current verification of platform/toolchain facts. TASK-13 and TASK-14 are blocked by the user's earlier process correction requiring discussion before further prompt generation.

### 8.3 Quick Wins

- Convert the user-proposed Windows/macOS frontend lists into a preliminary matrix.
- Draft candidate TUI parity levels: full, admin, fallback.
- List Linux and Android strategy options without deciding prematurely.
- Create a verification checklist for platform facts before implementation.

### 8.4 Tasks Requiring Verification

TASK-04, TASK-05, TASK-06, TASK-07, TASK-10, TASK-11, TASK-12, TASK-13, and TASK-14 require verification or user confirmation before implementation.

## 9. Constraints and Requirements

### 9.1 Hard Requirements

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
| CONSTRAINT-12 | GUIs are modular frontends attached to product backends. | architecture | hard | User GUI decision | GUI shells must not own product logic. | high | high | FACT |
| CONSTRAINT-13 | Do not treat assistant suggestions as user decisions unless accepted. | evidence/process | hard | Current user request | Keep brainstorms/tentative items labelled. | high | high | FACT |
| CONSTRAINT-14 | External-world facts/software versions/toolchain support require verification before future use. | evidence/staleness | hard | Current user request | Platform facts should be marked VERIFY before implementation. | high | high | FACT |
| CONSTRAINT-15 | Source scope is this chat only; outside context must be labelled PROJECT-CONTEXT. | scope/evidence | hard | Current user request | Do not summarize whole project. | high | high | FACT |
| CONSTRAINT-16 | Use stable IDs for registers. | format | hard | Current user request | All important items need WORKSTREAM/DECISION/etc. IDs. | medium | high | FACT |
| CONSTRAINT-17 | Windows App SDK / WinUI 3 Windows 10 1809+ support must be reverified before future use. | technical | hard for implementation | Previous packet external reference | Do not finalize WinUI lane without current docs. | medium-high | medium | UNCERTAIN / UNVERIFIED |
| CONSTRAINT-18 | .NET Framework 4.0–4.8 support requires real target/build lanes. | technical | hard for implementation | Assistant correction / external docs in previous packet | Need frozen VS/tooling for old .NET targets. | high | medium | UNCERTAIN / UNVERIFIED |
| CONSTRAINT-19 | macOS 10.9 support cannot be assumed with current Xcode; requires legacy/frozen toolchain or verification. | technical | hard for implementation | Assistant correction / external docs in previous packet | Need decide if 10.9 is real support target. | high | medium | UNCERTAIN / UNVERIFIED |
| CONSTRAINT-20 | .NET MAUI should not be treated as a complete Linux desktop solution without verification. | technical | hard for implementation | Previous packet external reference | Linux stack remains open. | medium | medium | UNCERTAIN / UNVERIFIED |

### 9.2 Soft Preferences

| ID | Constraint | Type | Hard/soft | Source / basis | Practical implication | Violation risk | Confidence | Label |
|---|---|---|---|---|---|---|---|---|
| CONSTRAINT-11 | Every product is expected to work with TUI. | product architecture | strong | User GUI decision | TUI doctrine is required. | medium-high | high | FACT |

### 9.3 Technical Constraints

Key technical constraints are CONSTRAINT-17 through CONSTRAINT-20. They are stale-prone and must be verified before implementation.

### 9.4 Time / Resource Constraints

No explicit calendar deadlines or resource limits were established in this chat. Resource implications were discussed indirectly through old toolchain/build-lane complexity and minimal storage/memory goals for universe content.

### 9.5 Legal / Ethical / Safety Constraints

No distinct legal, ethical, or safety regime was established beyond evidence, provenance, and not fabricating facts/content.

### 9.6 Evidence / Citation Requirements

The current user prompt requires external-world facts and software/platform support claims to be marked for verification before future use. The user profile outside the visible chat also prefers source-grounded, audit-ready responses; this is PROJECT-CONTEXT.

### 9.7 Formatting / Output Requirements

The current user request requires stable IDs, normalized registers, Markdown/YAML package files, and a manifest.

### 9.8 Things to Avoid

Avoid inventing facts, silently inferring, converting brainstorms into decisions, ignoring contradictions, treating assistant drafts as accepted, claiming file creation without actual files, and summarizing the whole project instead of this chat.

## 10. Open Questions and Unresolved Issues

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

## 11. Rejected, Superseded, or Deprioritised Options

| ID | Option | Status | Reason rejected/superseded/deprioritised | Is rejection final? | Reconsider conditions | Related workstream | Label |
|---|---|---|---|---|---|---|---|
| REJECTED-01 | Generate final CONTENT0 prompts immediately. | superseded | User explicitly said to discuss before planning/generating prompts. | final process correction | After discussion resolves conceptual issues. | WORKSTREAM-02 | FACT |
| REJECTED-02 | Treat assistant-cleaned CONTENT0 prompt as final. | superseded | It was generated before user's discussion-first correction. | final unless user later accepts revised draft | Use as reference only when revising prompt. | WORKSTREAM-02 | FACT |
| REJECTED-03 | One universal GUI framework as the entire GUI strategy. | deprioritized | Does not fit old/new/native/platform goals as well as modular frontend families. | tentative | If legacy/native goals are reduced. | WORKSTREAM-06 | INFERENCE |
| REJECTED-04 | One separate GUI codebase per OS version/era. | deprioritized | Would cause matrix explosion; profiles/lanes recommended instead. | tentative | If period-authentic retro-native UI becomes explicit product goal. | WORKSTREAM-14 | INFERENCE |
| REJECTED-05 | Let GUI shells own product logic. | rejected | Contradicts modular backend-attached GUI plan and causes drift. | final architecture principle | Only for intentionally independent tools. | WORKSTREAM-07 | INFERENCE |
| REJECTED-06 | Single .NET 4.8 WinForms binary supports .NET 4.0 machines. | rejected/corrected | Assistant identified .NET Framework targeting/version issue; future verification still required. | final as phrased | Never as phrased; use separate target/build lanes. | WORKSTREAM-08 | UNCERTAIN / UNVERIFIED |
| REJECTED-07 | Current Xcode alone supports macOS 10.9 AppKit target. | rejected/corrected | Assistant identified deployment-floor issue; future verification still required. | final as phrased | If an available toolchain actually supports 10.9 or requirement is dropped. | WORKSTREAM-09 | UNCERTAIN / UNVERIFIED |
| REJECTED-08 | Use .NET MAUI as complete Windows/macOS/Linux desktop answer. | rejected for Linux completeness | Prior packet noted MAUI does not cover Linux desktop officially; verify before future use. | tentative but likely | If official Linux support or third-party support becomes acceptable. | WORKSTREAM-10 | UNCERTAIN / UNVERIFIED |
| REJECTED-09 | Treat Android as desktop UI scaled down. | rejected/recommended against | Android is a mobile host family and needs distinct UX/product role. | tentative | Never by default; only if Android role is explicitly limited. | WORKSTREAM-11 | INFERENCE |
| REJECTED-10 | Summarize the whole project rather than this chat. | rejected by current prompt | User limited source scope to this chat only. | final for this package | In a later master aggregation task. | WORKSTREAM-16 | FACT |

Preserving these avoids repeated work. In particular, REJECTED-01 and REJECTED-02 prevent future assistants from treating the assistant-generated CONTENT0 rewrite as final; REJECTED-04 prevents GUI matrix explosion; REJECTED-06 and REJECTED-07 prevent false old-platform support claims.

## 12. Artifact Ledger

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

## 13. Rationale and Assumptions

Major visible rationale:

- The content layer needs provenance because the user explicitly rejects gameplay-fabricated entities/assets.
- The prompt process needs discussion-first because the user corrected the assistant after premature prompt generation.
- GUI shells need to be modular because the user wants multiple native frontends attached to product backends.
- A shared backend/UI contract is inferred as necessary because CLI, TUI, and multiple GUIs otherwise risk divergence.
- Compatibility lanes are preferred over one GUI per OS version because earlier assistant discussion identified matrix explosion as a risk.
- Old-host support needs real toolchains/build lanes because assistant analysis identified .NET and Xcode constraints.

Assumptions that remain unverified:

- Product backends exist or can be factored into shared contracts.
- The CLI can expose all critical operations.
- The TUI can map to the same backend contract as GUI and CLI.
- User values old-host compatibility enough to maintain legacy toolchains.
- 'Compile native applications' means separate native/bundled artifacts per platform/architecture/lane.
- OEM+ means host-respectful/native-ish polish rather than exact period-authentic cloning.
- Actual repository files match the implied architecture.

## 14. Risks and Failure Modes

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

## 15. Verification Queue

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

## 16. Spec Book Contribution Notes

Likely future Project Spec Book sections fed by this chat:

- Content Layer Doctrine
- Canonical Universe and Default Datapack Strategy
- Milky Way / Sol / Earth Content Requirements
- GUI and Binary Architecture Doctrine
- Product Surface Model: CLI, TUI, GUI
- Backend/UI Contract Requirements
- Windows Frontend and Build Lanes
- macOS Frontend and Build Lanes
- Linux and Android Open Strategy
- Packaging and Distribution Doctrine
- Verification and Support Claim Policy

Unique contributions from this chat include the explicit GUI rebuild decision, the Windows/macOS frontend family lists, the content-layer provenance doctrine, the default Milky Way/Sol datapack ambition, and the discussion-first correction for prompt generation.

Possible overlaps with other chats include engine/runtime architecture, actual repository schemas, existing GUI code, content-generation prompts, and build tooling. Conflicts to watch for: any later chat that keeps old GUI architecture; any chat that assumes one universal GUI framework; any chat that claims macOS 10.9 or .NET 4.0 support without actual toolchains; any chat that treats CONTENT0 as already finalized.

Formal requirement candidates: CLI mandatory, TUI expected, modular GUIs attached to product backends, content provenance, data-only CONTENT0 scope, no support claim without build/test lane. Background context candidates: assistant-suggested C ABI, visual profile names, static/self-contained packaging preference. Items needing confirmation: Linux stack, Android role, exact Windows/macOS floors, TUI parity, backend contract shape.

## 17. What Future Assistants Must Preserve

| Priority | Item | Type | Why it matters | Risk if lost | Label | Confidence |
|---|---|---|---|---|---|---|
| 1 | GUI rebuild from scratch | decision | Current main direction | Assistant may preserve old GUI assumptions | FACT | high |
| 2 | CLI mandatory for every product | requirement | Baseline operability | GUI becomes required for operation | FACT | high |
| 3 | TUI expected for every product | requirement | Terminal workflows and server/admin use | TUI omitted or deprioritized | FACT | high |
| 4 | Modular GUIs attach to product backends | architecture | Prevents logic duplication | GUI family drift | FACT | high |
| 5 | Backend/UI contract unresolved and first priority | open question | All frontends depend on it | Premature platform-specific design | INFERENCE | medium-high |
| 6 | Windows frontend family list | platform plan | Most detailed platform direction | Wrong Windows matrix | FACT | high |
| 7 | macOS AppKit/SwiftUI family list and 10.9 caveat | platform plan | Mac support/toolchain planning | False legacy support claim | FACT / UNCERTAIN | medium-high |
| 8 | Linux and Android remain open | open plan | Avoid inventing decisions | Spec hardens unsupported choices | FACT | high |
| 9 | CONTENT0 data-only provenance doctrine | content requirement | Core content philosophy | Generated content fabricates state | FACT | high |
| 10 | Discussion-first before content prompts | process decision | Avoids premature prompt output | Assistant repeats prior mistake | FACT | high |
| 11 | Default datapack includes Milky Way and high-detail Sol | content plan | Core canonical content | Default content scope drifts | FACT | high |
| 12 | External platform facts require verification | evidence rule | Toolchains change | Stale support matrix | FACT | high |
| 13 | Assistant suggestions are not user decisions | evidence rule | Prevents false requirements | Spec pollution | FACT | high |

## 18. What Future Assistants Must Not Assume

- Do not assume the assistant-cleaned CONTENT0 prompt is final.
- Do not assume a repository was inspected in this package.
- Do not assume Linux stack is chosen.
- Do not assume Android role is chosen.
- Do not assume stable C ABI is decided.
- Do not assume one universal GUI framework has been accepted.
- Do not assume exact visual profile names/count are decided.
- Do not assume macOS 10.9 support is feasible with current Xcode.
- Do not assume .NET 4.8 WinForms binary supports .NET 4.0 machines.
- Do not assume Xcode is useful outside Apple-platform lanes.
- Do not assume .NET MAUI solves Linux desktop.
- Do not assume all external links are current.
- Do not assume whole-project context beyond this chat.

## 19. Recommended Next Action

If continuing this chat's work alone: produce a GUI/binary planning doctrine and matrix, starting with the backend/UI contract and product surface model.

If aggregating this chat with other chat reports: ingest this package by IDs, preserve labels, and do not merge similar items until cross-chat evidence supports merging.

User verification needed before acting: exact backend expectations, TUI parity, Linux stack, Android role, macOS 10.9 requirement, .NET Framework floor, and repository/files.

## 20. Appendix: Possibly Relevant Details

Exact user wording that should be preserved:

> “First, let's discuss this before we plan or generate any prompts.”

> “Okay, I've decided I want to redo the GUIs from scratch.”

> “For each of our products, they will always work with CLI, are expected to work with TUI, and will have multiple modular GUIs that we can attach to our product backends to compile native applications.”

> “I want our default data pack that we ship by default to contain: The Milky way galaxy.”

> “All the most important starts and celestial sites in this galaxy. We should consider all forms of importance (for visiting, for harvesting, for research, for navigation, etc).”

Original CONTENT0 prompt is preserved as ARTIFACT-01. For self-containment, the verbatim prompt and the verbatim GUI rebuild plan are included below.

### Appendix A — Verbatim User CONTENT0 Prompt

```text
PROMPT CONTENT0 — CANONICAL GAME CONTENT & DATA POPULATION
TARGET: GPT-5.2 CODEX
SCOPE: DATA + SCHEMA EXTENSIONS + DOCS (NO ENGINE / RUNTIME CODE)
INTENT: POPULATE WORLD, CIVILIZATION, ECONOMY, HISTORY CONTENT CORRECTLY

SYSTEM ROLE
You are continuing the Dominium / Domino project.
You are working on the **content layer only**.

You MUST NOT:
- change engine code
- change runtime logic
- change execution, ECS, domains, authority, or time models
- introduce new architectural concepts

You MUST:
- treat all simulation rules as fixed
- add content only through data and schemas
- ensure everything has provenance and construction history
- ensure nothing is fabricated “for gameplay”

============================================================
CONTENT PHILOSOPHY (BINDING)
============================================================

All content must obey:

- No entity exists unless it was created by an explicit process
- No population exists unless it was born
- No city exists unless it was built
- No resource exists unless it was extracted or produced
- No civilization exists unless it emerged historically
- No “starting assets” without justification

Macro content may exist without micro simulation, but must be refinable.

============================================================
CONTENT OWNERSHIP
============================================================

This prompt may touch ONLY:

data/
schema/ (new schemas allowed if purely descriptive)
docs/ (content documentation only)

It MUST NOT modify:
engine/
game/ (logic)
client/
server/
tools/ (except documentation)

============================================================
REQUIRED CONTENT DOMAINS
============================================================

You MUST populate canonical content for:

1. UNIVERSE STRUCTURE
2. GALAXIES
3. STAR SYSTEMS
4. PLANETS & MOONS
5. SURFACES & REGIONS
6. HISTORICAL TIMELINES
7. POPULATIONS
8. CIVILIZATIONS
9. ECONOMIES
10. INSTITUTIONS
11. TECHNOLOGY & KNOWLEDGE
12. SCENARIOS / START CONDITIONS

============================================================
1) UNIVERSE & GALAXY CONTENT
============================================================

Create data defining:

- Universe instance(s)
- Milky Way galaxy
- Galactic structure:
  - arms
  - core
  - halo
  - voids
- Spatial coordinates and scales
- Domain volumes for:
  - galaxy bounds
  - arms
  - regions of interest

Use deterministic seeds.
No procedural generation logic here — only parameters.

============================================================
2) STAR SYSTEM CONTENT
============================================================

Populate canonical star systems:

- Sol (mandatory)
- Nearby systems (Alpha Centauri, etc.)
- System hierarchy:
  - stars
  - barycenters
  - planets
  - moons
  - belts

Each body must include:
- formation history
- orbital parameters
- domain volumes
- visitability rules

============================================================
3) PLANETARY & SURFACE CONTENT
============================================================

For Earth (minimum):

- Continents
- Oceans
- Climate regions
- Geological layers
- Domain volumes for:
  - land
  - sea
  - atmosphere
  - interior

No gameplay shortcuts.

============================================================
4) HISTORICAL TIMELINES
============================================================

Define:

- Universe start epoch
- Sol system formation
- Earth formation
- Pre-life, life emergence
- Human emergence
- Zero-player start conditions

History is data, not code.

============================================================
5) POPULATION & LIFE CONTENT
============================================================

Define initial populations:

- Humans (zero or minimal)
- Animals
- Microbial life (macro only)
- AI civilizations (optional, macro only)

No NPCs appear without birth processes.

============================================================
6) CIVILIZATIONS & INSTITUTIONS
============================================================

Define:

- Early settlements
- States
- Corporations
- Religions
- Tribes
- Non-human civilizations (if any)

Each must have:
- origin
- governance
- territory (domains)
- economy
- legitimacy

============================================================
7) ECONOMIC CONTENT
============================================================

Define:

- Resources
- Production chains
- Energy sources
- Transport routes
- Trade relationships

Everything must obey conservation.

============================================================
8) TECHNOLOGY & KNOWLEDGE
============================================================

Define:

- Knowledge trees
- Discovery processes
- Cultural diffusion
- Education institutions

No instant tech unlocks.

============================================================
9) SCENARIOS & STARTS
============================================================

Define:

- Single-player starts
- Multiplayer starts
- AI-only autorun starts
- Historical starts

All starts must be explainable historically.

============================================================
DOCUMENTATION OUTPUT
============================================================

Create docs:

docs/content/
- UNIVERSE.md
- MILKY_WAY.md
- SOL_SYSTEM.md
- EARTH.md
- HUMANITY.md
- CIVILIZATIONS.md
- ECONOMY.md
- START_SCENARIOS.md

============================================================
ACCEPTANCE CRITERIA
============================================================

CONTENT0 is complete when:

- All content is data-driven
- Nothing appears from nowhere
- Earth and Sol are fully defined
- Macro content is refinable
- Docs explain content clearly

END PROMPT CONTENT0
```

### Appendix B — Verbatim User GUI Rebuild Plan

```text
Okay, I've decided I want to redo the GUIs from scratch.    
For each of our products, they will always work with CLI, are expected to work with TUI, and will have multiple modular GUIs that we can attach to our product backends to compile native applications.    
    
For windows, we will have the following selection of front ends:     
- Win32 ANSI for 32bit Intel for setup and client.    
- Win32 Unicode for 64bit intel and arm, for setup and client.    
- WinForms .NET 4.8 for 32/64bit Intel, for launcher and server, with multi-targetting and conditional compilation down to .NET 4.0 machines.   
- WinUI 3 for 64bit Intel and ARM, for launcher and server, with graceful degradation to Windows 10 1809 machines.    
    
For Mac OS, we will have:    
- AppKit for 64bit Intel, for setup and launcher and client and server, with multi-targetting and conditional compilation down to Mac OS 10.9 machines.    
- SwiftUI 64bit Intel and arm, for future launcher and server, with graceful degradation to 11.0
    
For Linux we will do something similar.
And for Android similar again.
```

