# Full Chat Report — Dominium TestX RepoX Governance Handoff

## 0. Report Metadata

| Field | Value |
|---|---|
| Chat label | `dominium_testx_repox_governance_handoff` |
| Generated date anchor | 2026-05-27 Australia/Melbourne |
| Source scope | THIS CHAT ONLY; project-level items from visible pasted project/repo context are labelled as FACT where pasted by the user, otherwise UNCERTAIN / UNVERIFIED. |
| Apparent coverage | full visible-context coverage, based on prior Context Transfer Packet and visible chat context |
| Extraction confidence | 4 / 5 |
| Staleness risk | medium; toolchain facts, actual repo contents, and implementation status require verification |
| Future plans present | yes |
| Pending tasks present | yes |
| Artifacts/files present | yes |
| Safe for aggregation | yes, with caveats |
| Main limitations | No direct repo inspection was performed in this report-generation step; exact full text of prior generated mega-prompts is summarized rather than reproduced verbatim; external toolchain facts require verification before implementation. |


## 1. Executive Summary

This chat was a long-running governance, architecture-continuity, and implementation-planning thread for the Dominium / Domino project. The visible conversation focused less on ordinary feature design and more on building the project’s constitutional scaffolding: how the engine/game, content, applications, build system, repository, toolchains, IDEs, demos, services, piracy containment, and future language transitions should be documented, enforced, and handed off across parallel chats without losing decisions or causing future refactors.

The highest-priority project identity preserved here is that Dominium / Domino is a deterministic universe engine + game, not a typical convenience-driven engine or content-first RPG. The latest upstream canon pasted by the user overrides earlier assistant-generated drafts: architecture is closed, canon is locked, and future work is implementation, audit, optimisation, and maintenance only. The core ontology is Assemblies, Fields, Processes, Agents, and Law. Global invariants include process-only mutation, deterministic replayable simulation, fixed-point authoritative logic, named RNG streams only, strong epistemics and fog-of-war, SRZ-0 distributed simulation/verification, VALIDATE-0/TestX/RepoX enforcement, and no hardcoded content or magic defaults. Engine is C89, game is C++98, public headers must remain parseable forever, and C++ ABI leakage across boundaries is forbidden.

The chat produced and refined a stack of governance prompts and plans. TESTX began as a self-defending verification and versioning system; TESTX2 added optional non-interfering control layers such as DRM/anti-cheat/telemetry without putting secrets or enforcement in engine/game; TESTX3 added authority, entitlements, demos, tourist server access, services, storefront distribution, and piracy containment by selling durable authority rather than bits; REPOX added repository ownership, IDE projections, toolchain and multi-architecture governance; and a proposed TESTX4/language-profile layer would enforce feature allowlists, C ABI discipline, and safe C89/C++98→C17/C++17 transitions. Later upstream canon superseded some earlier details, especially build numbering: BUILD-ID-0 now governs version identity, with manual product SemVer, build kinds dev/ci/beta/rc/release/hotfix, release-grade centrally allocated GBN only for beta/rc/release/hotfix, and always-present BII for dev/ci. Any earlier “global build number increments every build” concept is superseded.

A major workstream was modular content and packs. The engine/game must boot with zero assets; all non-code content is external, open-format, capability-provided, and optional. No mandatory base pack, no implicit Earth/Sol in engine, no hardcoded paths, and no cooked/GPU-specific blobs in packs. Saves/replays/worlds should reference pack IDs and schema/protocol versions, not raw paths. This enables dropping old OS binaries while still delivering compatible data, game rule, backend, pack, and protocol updates where capabilities permit.

Another major workstream was application and UI governance. The application layer is governed by APP-CANON0/1, APP-AUTO-0, and APP-UI-BIND-0. Applications are orchestration shells. CLI is canonical. GUI/TUI are views over the same command graph. UI is data/UI IR, never logic. Tools are read-only by default. Setup is the only install mutation authority. Launcher is the reference application. Existing repo paths such as tools/ui_shared and tools/*/ui doc/gen/user patterns are important implementation anchors.

Repository/toolchain work culminated in REPOX. IDEs must not own the project. CMake + TestX/RepoX own the graph; IDE files are disposable projections, preferably under /ide/**, with existing VS/Xcode/WiX packaging projects classified as grandfathered packaging inputs only if verified. The user supplied a strict OS/toolchain/language matrix for Windows, Mac, and Linux, including VC6, VC7.1, VS2015, modern MSVC, CodeWarrior Classic, era-pinned Xcodes, GCC/Clang, and multiple CPU architectures. The user later installed Windows 10 with VS2022 and received a practical MVP recommendation: use VS2022 as a host for v141/v141_xp and pinned SDKs to build XP→Windows 11 floor targets, while eventually using true legacy VMs for archival VC6/VC7.1 support.

The most important unresolved issues are verification tasks: inspect the actual repo for CANON_INDEX.md, CLEAN-2/BUILD-ID-0/APP/SRZ/VALIDATE docs, status headers, current CMake presets, CI, old build-number files/scripts such as .dominium_build_number and update_build_number.cmake, tracked IDE artifacts, UI binding enforcement, language compliance, zero-asset boot tests, authority profiles, and policy-as-data support. Future assistants must not treat assistant brainstorms as final canon unless accepted by the user or confirmed by latest upstream canon.

## 2. How to Use This Report

This report covers only this old chat. It is not a full Project Spec Book and must not be treated as the entire Dominium / Domino project history. Direct user statements and the latest upstream canon pasted by the user outrank assistant-generated suggestions. Items labelled FACT were explicitly present in this chat. Items labelled INFERENCE are reasonable conclusions from this chat but must not be promoted to canon without confirmation. Items labelled UNCERTAIN / UNVERIFIED require repo inspection, user confirmation, or current external verification. Items labelled PROJECT-CONTEXT would come from outside visible chat context; this package avoids relying on such context except where the user pasted repo/project material into the chat.

For future aggregation, preserve stable IDs. Do not merge similar items from other chats without checking source provenance and contradiction registers. Stale toolchain/software claims should be verified against installed tools or official documentation before acting. Tentative plans such as TESTX4 and policy-as-data should remain planned/recommended until the repo or user confirms adoption.

## 3. User Preferences Visible in This Chat

### 3.1 Explicit Preferences

| ID | Preference | Source / basis | Strength | Implication | Risk if misunderstood | Label |
| --- | --- | --- | --- | --- | --- | --- |
| PREFERENCE-01 | Preserve maximum fidelity rather than over-compressing | Current report-package request and earlier Context Transfer Packet request | strong explicit | Use registers, IDs, and caveat labels. | Loss of decisions, contradictions, prompts, and future actions. | FACT |
| PREFERENCE-02 | Label facts, inferences, uncertainties, and project context | Current user request | strong explicit | Do not silently infer or promote brainstorms to decisions. | False canon and bad aggregation. | FACT |
| PREFERENCE-03 | Prioritise correctness, long-term utility, and auditability over tone/engagement | User profile/instructions visible in chat | strong explicit | Use precise caveats and failure modes. | Overconfident or flattering answers. | FACT |
| PREFERENCE-04 | Create downloadable files where possible | Current request | strong explicit | Use file-generation tool and provide links. | User forced to copy manual output. | FACT |
| PREFERENCE-05 | Future assistants should not make the user re-explain context | Context Transfer Packet request | strong explicit | Reports must be self-contained. | Repeated planning cycles and lost continuity. | FACT |
| PREFERENCE-06 | Treat direct user statements above assistant suggestions | Current request | strong explicit | Assistant-generated prompts are not final unless accepted or upstream canon confirms. | Brainstorms become false requirements. | FACT |
| PREFERENCE-07 | Use structured headings, tables, stable IDs, consistent terminology | Current request | strong explicit | Normalize registers for future aggregation. | Aggregator cannot merge reports reliably. | FACT |
| PREFERENCE-08 | Web/current facts should be verified when used for action | Current request and system/developer factuality rules | strong explicit | Toolchain/version claims must be rechecked before implementation. | Stale VS/SDK/OS decisions. | FACT |

### 3.2 Inferred Preferences

| ID | Preference | Source / basis | Strength | Implication | Risk if misunderstood | Label |
|---|---|---|---|---|---|---|
| PREFERENCE-09 | Prefer governance that is mechanically enforceable rather than prose-only. | Repeated requests for TestX/RepoX, rules-to-checks, and tests for every rule. | strong inferred | Prefer scripts, CI, registers, and policies-as-data. | The project remains dependent on memory and discipline. | INFERENCE |
| PREFERENCE-10 | Prefer long-lived compatibility and graceful retirement over short-term convenience. | Old OS/toolchain support and old binaries receiving updates. | strong inferred | Separate binaries, protocols, packs, and services. | Future assistants may force updates unnecessarily. | INFERENCE |

### 3.3 Preferences Not Established by This Chat

| Topic | Status | Notes |
|---|---|---|
| Exact UI/UX aesthetics | not established | The chat discussed architecture and WYSIWYG workflows, not visual style. |
| Exact commercial pricing | not established | The chat discussed free/demo/upfront/service models, not prices. |
| Exact old-binary support duration | not established | The chat established capability to support old binaries, not a policy length. |
| Exact GBN allocator mechanism | not established | BUILD-ID-0 requires central allocation but implementation details are unverified. |

## 4. Complete Topic and Workstream Inventory

| Stable ID | Name | Objective | Current state | Desired end state | Status | Priority | Confidence | Source label |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| WORKSTREAM-01 | Dominium / Domino core engine and game | Maintain and implement the deterministic universe engine and game under locked canon. | Repo snapshot shows engine/ and game/ with extensive modules, headers, tests, content, rules, and docs. Latest upstream canon says architecture is closed and implementation/audit only. | Deterministic, replayable, fixed-point, process-only mutation simulation with strong epistemics and no hardcoded content. | active | critical | high from chat; repo details unverified | FACT |
| WORKSTREAM-02 | Content system, packs, and zero-asset boot | Keep content external, modular, capability-resolved, open-format, and optional. | Repo snapshot includes data/, game/content, engine content/pkg/mod modules, pack/coredata tools, and content specs. | Engine/game boot with zero assets; packs provide capabilities; missing capabilities produce explicit fallback/refusal. | active | critical | high conceptually; implementation unverified | FACT |
| WORKSTREAM-03 | Application layer canon | Implement client/server/launcher/setup/tools as orchestration shells governed by APP-CANON0/1, APP-AUTO-0, APP-UI-BIND-0. | Repo snapshot has client/, server/, launcher/, setup/, tools/ with CLI/GUI/TUI and UI systems. Latest upstream says CLI is canonical and launcher reference app. | GUI/TUI are views over one command graph; UI is data; setup alone mutates installs; tools read-only by default. | active | critical | high canon; actual enforcement unknown | FACT |
| WORKSTREAM-04 | Renderers, platforms, and headless operation | Keep render/platform support modular, runtime-capability-driven, and non-authoritative. | Repo snapshot has render backends and platform layers. Prior AP response accepted no-silent-fallback and headless-first model. | Null/software/real renderers; explicit selection refuses when unavailable; auto fallback logs; server/headless no GUI/GPU/audio dependency. | active | high | medium-high | FACT |
| WORKSTREAM-05 | TESTX / VALIDATE verification system | Make canon mechanically enforced by tests, assertions, CI, and blocker tracking. | Original TESTX was user-pasted; repo snapshot includes many tests and validation scripts. Later BUILD-ID-0 supersedes older build-number semantics. | Every canon rule maps to checks; CLI-only deterministic tests; no skipped tests; loud failures; version stamping follows BUILD-ID-0. | active, requires revision | critical | high | FACT |
| WORKSTREAM-06 | TESTX2 control layers and non-interference | Support optional DRM/anti-cheat/telemetry/entitlement control layers without corrupting core. | Generated as a mega-prompt in this chat; not confirmed implemented in repo. | Control capabilities disabled by default; engine/game have no DRM/secrets/enforcement; control gates access/connectivity only; tests prove non-interference. | planned / derived | medium-high | medium | FACT |
| WORKSTREAM-07 | TESTX3 authority, demo, tourist, services, and piracy containment | Use authority/entitlement profiles rather than separate binaries for demo/free/paid/service models. | Generated as a mega-prompt and accepted conceptually in this chat; later upstream canon preserves authority framing but exact docs unknown. | One distribution; demo/free base authority; tourist multiplayer; buy grants authority; piracy yields no durable value. | planned / derived | high | medium-high | FACT |
| WORKSTREAM-08 | REPOX repository ownership and IDE projections | Prevent IDE/toolchain/project-file sprawl from corrupting canonical build/source ownership. | Generated REPOX prompt; repo snapshot includes root .vs/.vscode and scattered VS/Xcode/WiX projects, but no visible top-level /ide. | CMake + TestX/RepoX own graph; IDE files are generated projections under /ide except documented packaging inputs; quarantine enforced. | active/planned | critical | high conceptually; implementation unknown | FACT |
| WORKSTREAM-09 | Toolchain and legacy OS matrix | Support old and new OS/compiler/language floors honestly with separate artifacts. | User supplied Windows/Mac/Linux IDE/language matrix and global warnings; later VS2022 MVP advice added practical floor builds. | Separate OS/toolchain/SDK/arch artifacts; legacy tiers frozen once validated; no binary ABI lies. | active/planned | high | high for user decision; current tool availability unverified | FACT |
| WORKSTREAM-10 | TESTX4 language profiles and ABI discipline | Codify feature allowlists by layer and mechanically enforce language/ABI rules. | User pasted random-chat proposal; assistant assessed it as the missing language-level constitution. Not yet top-level authoritative unless user adopts. | SPEC_LANGUAGE_PROFILES / TESTX4 docs; no exceptions/RTTI/static init side effects across boundaries; no STL/FP in deterministic paths; per-file language transitions. | recommended/planned | high | medium-high | INFERENCE |
| WORKSTREAM-11 | Policy-as-data and rules-to-checks automation | Make rules executable and future-proof using machine-readable policies and a unified runner. | Assistant proposed RULES_TO_CHECKS_MATRIX.md, /policies/rules JSON files, validate_repo_policy.py. Not confirmed implemented. | Every rule has an enforcement mapping; gaps are labelled guidance; CI runs policy checks. | recommended/planned | high | medium | INFERENCE |
| WORKSTREAM-12 | Windows MVP build/test plan with VS2022 | Use Windows 10 + VS2022 host to test practical MVP Windows floors while planning older VMs later. | User installed Windows 10 with VS2022; other chat suggested v141/v141_xp/SDK matrix; assistant endorsed for MVP with caveats. | CMake presets and VMs for XP/Win7/Win8/Win10/Win11 floors; later archival VC6/VC7.1 VMs. | active next-step candidate | high | medium-high | FACT |

## 5. Detailed Workstream State

### WORKSTREAM-01 — Dominium / Domino core engine and game

- Label: FACT
- Objective: Maintain and implement the deterministic universe engine and game under locked canon.
- Background: Derived from visible chat discussions and, where applicable, the latest upstream canon pasted by the user.
- Current state: Repo snapshot shows engine/ and game/ with extensive modules, headers, tests, content, rules, and docs. Latest upstream canon says architecture is closed and implementation/audit only.
- Desired end state: Deterministic, replayable, fixed-point, process-only mutation simulation with strong epistemics and no hardcoded content.
- Importance: critical
- Decisions made: DECISION-01, DECISION-02, DECISION-03, DECISION-04
- Decisions pending: None identified beyond implementation verification.
- Pending tasks: No direct task ID assigned; see general audit tasks.
- Constraints: CONSTRAINT-01, CONSTRAINT-02, CONSTRAINT-03, CONSTRAINT-04, CONSTRAINT-05, CONSTRAINT-06, CONSTRAINT-07, CONSTRAINT-09, CONSTRAINT-10, CONSTRAINT-11
- Dependencies: Canon docs, repo audit, CMake/CI state, and related workstreams as applicable.
- Timeline / sequencing: Audit first; implementation after verification; no runtime semantic changes during governance updates.
- Blockers: Unknown actual repo state for this workstream unless verified.
- Risks: See Risk Register for related IDs.
- Artifacts: ARTIFACT-11, ARTIFACT-21, ARTIFACT-22
- Success criteria: Workstream rules are documented, mapped to checks, and enforced without contradicting latest canon.
- Recommended next action: Verify actual files and current implementation before modifying.
- Verification needed: General repo verification.
- Confidence: high from chat; repo details unverified
- Carry-forward priority: critical
### WORKSTREAM-02 — Content system, packs, and zero-asset boot

- Label: FACT
- Objective: Keep content external, modular, capability-resolved, open-format, and optional.
- Background: Derived from visible chat discussions and, where applicable, the latest upstream canon pasted by the user.
- Current state: Repo snapshot includes data/, game/content, engine content/pkg/mod modules, pack/coredata tools, and content specs.
- Desired end state: Engine/game boot with zero assets; packs provide capabilities; missing capabilities produce explicit fallback/refusal.
- Importance: critical
- Decisions made: DECISION-15
- Decisions pending: QUESTION-16
- Pending tasks: TASK-18, TASK-19
- Constraints: CONSTRAINT-08, CONSTRAINT-22, CONSTRAINT-33
- Dependencies: Canon docs, repo audit, CMake/CI state, and related workstreams as applicable.
- Timeline / sequencing: Audit first; implementation after verification; no runtime semantic changes during governance updates.
- Blockers: Unknown actual repo state for this workstream unless verified.
- Risks: See Risk Register for related IDs.
- Artifacts: ARTIFACT-20, ARTIFACT-22
- Success criteria: Workstream rules are documented, mapped to checks, and enforced without contradicting latest canon.
- Recommended next action: Verify actual files and current implementation before modifying.
- Verification needed: QUESTION-16
- Confidence: high conceptually; implementation unverified
- Carry-forward priority: critical
### WORKSTREAM-03 — Application layer canon

- Label: FACT
- Objective: Implement client/server/launcher/setup/tools as orchestration shells governed by APP-CANON0/1, APP-AUTO-0, APP-UI-BIND-0.
- Background: Derived from visible chat discussions and, where applicable, the latest upstream canon pasted by the user.
- Current state: Repo snapshot has client/, server/, launcher/, setup/, tools/ with CLI/GUI/TUI and UI systems. Latest upstream says CLI is canonical and launcher reference app.
- Desired end state: GUI/TUI are views over one command graph; UI is data; setup alone mutates installs; tools read-only by default.
- Importance: critical
- Decisions made: DECISION-10, DECISION-11, DECISION-12, DECISION-13, DECISION-14
- Decisions pending: QUESTION-17, QUESTION-18
- Pending tasks: TASK-09, TASK-10
- Constraints: CONSTRAINT-13, CONSTRAINT-14, CONSTRAINT-15, CONSTRAINT-16, CONSTRAINT-17
- Dependencies: Canon docs, repo audit, CMake/CI state, and related workstreams as applicable.
- Timeline / sequencing: Audit first; implementation after verification; no runtime semantic changes during governance updates.
- Blockers: Unknown actual repo state for this workstream unless verified.
- Risks: See Risk Register for related IDs.
- Artifacts: ARTIFACT-23, ARTIFACT-25, ARTIFACT-26, ARTIFACT-27, ARTIFACT-28, ARTIFACT-29, ARTIFACT-30
- Success criteria: Workstream rules are documented, mapped to checks, and enforced without contradicting latest canon.
- Recommended next action: Verify actual files and current implementation before modifying.
- Verification needed: QUESTION-17, QUESTION-18
- Confidence: high canon; actual enforcement unknown
- Carry-forward priority: critical
### WORKSTREAM-04 — Renderers, platforms, and headless operation

- Label: FACT
- Objective: Keep render/platform support modular, runtime-capability-driven, and non-authoritative.
- Background: Derived from visible chat discussions and, where applicable, the latest upstream canon pasted by the user.
- Current state: Repo snapshot has render backends and platform layers. Prior AP response accepted no-silent-fallback and headless-first model.
- Desired end state: Null/software/real renderers; explicit selection refuses when unavailable; auto fallback logs; server/headless no GUI/GPU/audio dependency.
- Importance: high
- Decisions made: None explicitly isolated in this report.
- Decisions pending: None identified beyond implementation verification.
- Pending tasks: TASK-17
- Constraints: CONSTRAINT-31
- Dependencies: Canon docs, repo audit, CMake/CI state, and related workstreams as applicable.
- Timeline / sequencing: Audit first; implementation after verification; no runtime semantic changes during governance updates.
- Blockers: Unknown actual repo state for this workstream unless verified.
- Risks: See Risk Register for related IDs.
- Artifacts: See Artifact Ledger.
- Success criteria: Workstream rules are documented, mapped to checks, and enforced without contradicting latest canon.
- Recommended next action: Verify actual files and current implementation before modifying.
- Verification needed: General repo verification.
- Confidence: medium-high
- Carry-forward priority: high
### WORKSTREAM-05 — TESTX / VALIDATE verification system

- Label: FACT
- Objective: Make canon mechanically enforced by tests, assertions, CI, and blocker tracking.
- Background: Derived from visible chat discussions and, where applicable, the latest upstream canon pasted by the user.
- Current state: Original TESTX was user-pasted; repo snapshot includes many tests and validation scripts. Later BUILD-ID-0 supersedes older build-number semantics.
- Desired end state: Every canon rule maps to checks; CLI-only deterministic tests; no skipped tests; loud failures; version stamping follows BUILD-ID-0.
- Importance: critical
- Decisions made: DECISION-06, DECISION-07, DECISION-08, DECISION-09
- Decisions pending: QUESTION-01, QUESTION-02, QUESTION-03, QUESTION-04, QUESTION-05, QUESTION-06, QUESTION-07, QUESTION-08
- Pending tasks: TASK-01, TASK-02, TASK-03, TASK-04, TASK-05, TASK-23, TASK-25
- Constraints: CONSTRAINT-18, CONSTRAINT-19, CONSTRAINT-20, CONSTRAINT-21, CONSTRAINT-22, CONSTRAINT-35
- Dependencies: Canon docs, repo audit, CMake/CI state, and related workstreams as applicable.
- Timeline / sequencing: Audit first; implementation after verification; no runtime semantic changes during governance updates.
- Blockers: Unknown actual repo state for this workstream unless verified.
- Risks: See Risk Register for related IDs.
- Artifacts: ARTIFACT-02, ARTIFACT-11, ARTIFACT-13, ARTIFACT-15, ARTIFACT-16, ARTIFACT-34, ARTIFACT-36
- Success criteria: Workstream rules are documented, mapped to checks, and enforced without contradicting latest canon.
- Recommended next action: Verify actual files and current implementation before modifying.
- Verification needed: QUESTION-01, QUESTION-02, QUESTION-03, QUESTION-04, QUESTION-05, QUESTION-06, QUESTION-07, QUESTION-08
- Confidence: high
- Carry-forward priority: critical
### WORKSTREAM-06 — TESTX2 control layers and non-interference

- Label: FACT
- Objective: Support optional DRM/anti-cheat/telemetry/entitlement control layers without corrupting core.
- Background: Derived from visible chat discussions and, where applicable, the latest upstream canon pasted by the user.
- Current state: Generated as a mega-prompt in this chat; not confirmed implemented in repo.
- Desired end state: Control capabilities disabled by default; engine/game have no DRM/secrets/enforcement; control gates access/connectivity only; tests prove non-interference.
- Importance: medium-high
- Decisions made: DECISION-19, DECISION-20
- Decisions pending: None identified beyond implementation verification.
- Pending tasks: TASK-21
- Constraints: CONSTRAINT-29, CONSTRAINT-30
- Dependencies: Canon docs, repo audit, CMake/CI state, and related workstreams as applicable.
- Timeline / sequencing: Audit first; implementation after verification; no runtime semantic changes during governance updates.
- Blockers: Unknown actual repo state for this workstream unless verified.
- Risks: See Risk Register for related IDs.
- Artifacts: See Artifact Ledger.
- Success criteria: Workstream rules are documented, mapped to checks, and enforced without contradicting latest canon.
- Recommended next action: Verify actual files and current implementation before modifying.
- Verification needed: General repo verification.
- Confidence: medium
- Carry-forward priority: medium-high
### WORKSTREAM-07 — TESTX3 authority, demo, tourist, services, and piracy containment

- Label: FACT
- Objective: Use authority/entitlement profiles rather than separate binaries for demo/free/paid/service models.
- Background: Derived from visible chat discussions and, where applicable, the latest upstream canon pasted by the user.
- Current state: Generated as a mega-prompt and accepted conceptually in this chat; later upstream canon preserves authority framing but exact docs unknown.
- Desired end state: One distribution; demo/free base authority; tourist multiplayer; buy grants authority; piracy yields no durable value.
- Importance: high
- Decisions made: DECISION-16, DECISION-17, DECISION-18
- Decisions pending: QUESTION-19
- Pending tasks: TASK-20
- Constraints: CONSTRAINT-32
- Dependencies: Canon docs, repo audit, CMake/CI state, and related workstreams as applicable.
- Timeline / sequencing: Audit first; implementation after verification; no runtime semantic changes during governance updates.
- Blockers: Unknown actual repo state for this workstream unless verified.
- Risks: See Risk Register for related IDs.
- Artifacts: See Artifact Ledger.
- Success criteria: Workstream rules are documented, mapped to checks, and enforced without contradicting latest canon.
- Recommended next action: Verify actual files and current implementation before modifying.
- Verification needed: QUESTION-19
- Confidence: medium-high
- Carry-forward priority: high
### WORKSTREAM-08 — REPOX repository ownership and IDE projections

- Label: FACT
- Objective: Prevent IDE/toolchain/project-file sprawl from corrupting canonical build/source ownership.
- Background: Derived from visible chat discussions and, where applicable, the latest upstream canon pasted by the user.
- Current state: Generated REPOX prompt; repo snapshot includes root .vs/.vscode and scattered VS/Xcode/WiX projects, but no visible top-level /ide.
- Desired end state: CMake + TestX/RepoX own graph; IDE files are generated projections under /ide except documented packaging inputs; quarantine enforced.
- Importance: critical
- Decisions made: DECISION-21, DECISION-22
- Decisions pending: QUESTION-09, QUESTION-10
- Pending tasks: TASK-06, TASK-07, TASK-08
- Constraints: CONSTRAINT-23, CONSTRAINT-24
- Dependencies: Canon docs, repo audit, CMake/CI state, and related workstreams as applicable.
- Timeline / sequencing: Audit first; implementation after verification; no runtime semantic changes during governance updates.
- Blockers: Unknown actual repo state for this workstream unless verified.
- Risks: See Risk Register for related IDs.
- Artifacts: ARTIFACT-09, ARTIFACT-35
- Success criteria: Workstream rules are documented, mapped to checks, and enforced without contradicting latest canon.
- Recommended next action: Verify actual files and current implementation before modifying.
- Verification needed: QUESTION-09, QUESTION-10
- Confidence: high conceptually; implementation unknown
- Carry-forward priority: critical
### WORKSTREAM-09 — Toolchain and legacy OS matrix

- Label: FACT
- Objective: Support old and new OS/compiler/language floors honestly with separate artifacts.
- Background: Derived from visible chat discussions and, where applicable, the latest upstream canon pasted by the user.
- Current state: User supplied Windows/Mac/Linux IDE/language matrix and global warnings; later VS2022 MVP advice added practical floor builds.
- Desired end state: Separate OS/toolchain/SDK/arch artifacts; legacy tiers frozen once validated; no binary ABI lies.
- Importance: high
- Decisions made: DECISION-23, DECISION-24, DECISION-27
- Decisions pending: QUESTION-20
- Pending tasks: TASK-24
- Constraints: CONSTRAINT-25, CONSTRAINT-26, CONSTRAINT-27, CONSTRAINT-28, CONSTRAINT-33
- Dependencies: Canon docs, repo audit, CMake/CI state, and related workstreams as applicable.
- Timeline / sequencing: Audit first; implementation after verification; no runtime semantic changes during governance updates.
- Blockers: Unknown actual repo state for this workstream unless verified.
- Risks: See Risk Register for related IDs.
- Artifacts: See Artifact Ledger.
- Success criteria: Workstream rules are documented, mapped to checks, and enforced without contradicting latest canon.
- Recommended next action: Verify actual files and current implementation before modifying.
- Verification needed: QUESTION-20
- Confidence: high for user decision; current tool availability unverified
- Carry-forward priority: high
### WORKSTREAM-10 — TESTX4 language profiles and ABI discipline

- Label: INFERENCE
- Objective: Codify feature allowlists by layer and mechanically enforce language/ABI rules.
- Background: Derived from visible chat discussions and, where applicable, the latest upstream canon pasted by the user.
- Current state: User pasted random-chat proposal; assistant assessed it as the missing language-level constitution. Not yet top-level authoritative unless user adopts.
- Desired end state: SPEC_LANGUAGE_PROFILES / TESTX4 docs; no exceptions/RTTI/static init side effects across boundaries; no STL/FP in deterministic paths; per-file language transitions.
- Importance: high
- Decisions made: DECISION-05
- Decisions pending: QUESTION-13, QUESTION-14, QUESTION-15
- Pending tasks: TASK-12, TASK-13, TASK-14
- Constraints: CONSTRAINT-09, CONSTRAINT-10, CONSTRAINT-11
- Dependencies: Canon docs, repo audit, CMake/CI state, and related workstreams as applicable.
- Timeline / sequencing: Audit first; implementation after verification; no runtime semantic changes during governance updates.
- Blockers: Unknown actual repo state for this workstream unless verified.
- Risks: See Risk Register for related IDs.
- Artifacts: ARTIFACT-10
- Success criteria: Workstream rules are documented, mapped to checks, and enforced without contradicting latest canon.
- Recommended next action: Verify actual files and current implementation before modifying.
- Verification needed: QUESTION-13, QUESTION-14, QUESTION-15
- Confidence: medium-high
- Carry-forward priority: high
### WORKSTREAM-11 — Policy-as-data and rules-to-checks automation

- Label: INFERENCE
- Objective: Make rules executable and future-proof using machine-readable policies and a unified runner.
- Background: Derived from visible chat discussions and, where applicable, the latest upstream canon pasted by the user.
- Current state: Assistant proposed RULES_TO_CHECKS_MATRIX.md, /policies/rules JSON files, validate_repo_policy.py. Not confirmed implemented.
- Desired end state: Every rule has an enforcement mapping; gaps are labelled guidance; CI runs policy checks.
- Importance: high
- Decisions made: DECISION-26
- Decisions pending: None identified beyond implementation verification.
- Pending tasks: TASK-11, TASK-22
- Constraints: CONSTRAINT-35
- Dependencies: Canon docs, repo audit, CMake/CI state, and related workstreams as applicable.
- Timeline / sequencing: Audit first; implementation after verification; no runtime semantic changes during governance updates.
- Blockers: Unknown actual repo state for this workstream unless verified.
- Risks: See Risk Register for related IDs.
- Artifacts: See Artifact Ledger.
- Success criteria: Workstream rules are documented, mapped to checks, and enforced without contradicting latest canon.
- Recommended next action: Verify actual files and current implementation before modifying.
- Verification needed: General repo verification.
- Confidence: medium
- Carry-forward priority: high
### WORKSTREAM-12 — Windows MVP build/test plan with VS2022

- Label: FACT
- Objective: Use Windows 10 + VS2022 host to test practical MVP Windows floors while planning older VMs later.
- Background: Derived from visible chat discussions and, where applicable, the latest upstream canon pasted by the user.
- Current state: User installed Windows 10 with VS2022; other chat suggested v141/v141_xp/SDK matrix; assistant endorsed for MVP with caveats.
- Desired end state: CMake presets and VMs for XP/Win7/Win8/Win10/Win11 floors; later archival VC6/VC7.1 VMs.
- Importance: high
- Decisions made: DECISION-25
- Decisions pending: QUESTION-11, QUESTION-12
- Pending tasks: TASK-15, TASK-16
- Constraints: CONSTRAINT-25, CONSTRAINT-26, CONSTRAINT-34
- Dependencies: Canon docs, repo audit, CMake/CI state, and related workstreams as applicable.
- Timeline / sequencing: Audit first; implementation after verification; no runtime semantic changes during governance updates.
- Blockers: Unknown actual repo state for this workstream unless verified.
- Risks: See Risk Register for related IDs.
- Artifacts: ARTIFACT-12, ARTIFACT-15
- Success criteria: Workstream rules are documented, mapped to checks, and enforced without contradicting latest canon.
- Recommended next action: Verify actual files and current implementation before modifying.
- Verification needed: QUESTION-11, QUESTION-12
- Confidence: medium-high
- Carry-forward priority: high

## 6. Chronological Timeline

| Sequence | Event / topic | What changed or was decided | Why it mattered | Current relevance | Confidence |
| --- | --- | --- | --- | --- | --- |
| 01 | Initial build/version/CMake design | User wanted global build number and product semver; assistant proposed build/version/changelog/packaging model. | Established initial versioning direction later superseded. | Historical; BUILD-ID-0 supersedes build-number part. | high |
| 02 | Industry acceptance review | Assistant judged versioning/build design industry-valid but upper-rigour. | Validated systems-software-style approach. | Background context. | medium-high |
| 03 | Content modularity and pack system | Zero-asset boot, Universal Pack System, open formats, pack IDs/capabilities discussed. | Established content separation and data-pack model. | Still relevant. | high |
| 04 | Prompts for sister chats | Assistant generated Engine/Game and App/Platform/Render prompts. | Parallel team alignment started. | Historical evidence. | high |
| 05 | Sister chat responses | User pasted acceptances; assistant found no conflicts. | Confirmed alignment at that time. | Historical; later canon refined. | high |
| 06 | TESTX introduced | User pasted authoritative TESTX prompt; assistant generated EG/AP TESTX prompts. | Moved from design to self-defending verification. | Still relevant but versioning revised. | high |
| 07 | EG/AP TESTX responses | Responses accepted TESTX; tensions resolved including build policy/no FP/no silent fallback. | Closed major integration loop. | Evidence for constraints. | high |
| 08 | Control layer scratchpad and TESTX2 | DRM/anti-cheat placement discussed; TESTX2 generated. | Established control non-interference doctrine. | Relevant but implementation unverified. | medium-high |
| 09 | Demo/free/tourist/piracy model | User explored Steam demo, tourist servers, free download, piracy prevention; assistant proposed authority-profile model. | Established same-distribution/demo-as-authority strategy. | Relevant; not fully implementation-verified. | medium-high |
| 10 | TESTX3 generated | Authority/entitlements/services/distribution/piracy containment mega-prompt created. | Formalized business/distribution governance. | Derived; later canon should govern. | medium |
| 11 | IDE/toolchain matrix and projection model | User pasted toolchain matrix and repo tree; assistant proposed IDEs as projections and /ide root. | Established RepoX direction. | Relevant; actual repo audit needed. | high |
| 12 | REPOX generated | Assistant generated REPOX mega-prompt with /ide, CMake projection, multi-arch, quarantine checks. | Formalized repo/toolchain/IDE governance. | Needs revision to latest canon. | medium-high |
| 13 | Old OS dropping discussion | User asked if old support can be dropped while binaries receive updates; assistant said yes via compatibility/capability separation. | Clarified graceful retirement model. | Relevant; policy details pending. | medium-high |
| 14 | Language profiles proposal | User pasted feature allowlist; assistant recommended TESTX4. | Added language/ABI governance workstream. | Recommended but not final unless adopted. | medium |
| 15 | Policy-as-data discussion | Assistant proposed rules-to-checks, policy JSON, future language/backends. | Extended automation plan. | Recommended; not implemented. | medium |
| 16 | Latest upstream canon block | User pasted new authoritative system-role block with closed architecture, ontology, APP/CLEAN/BUILD-ID canon. | Superseded/clarified earlier prompts, especially versioning. | Highest current relevance. | high |
| 17 | Windows VS2022 MVP recommendation | User pasted recommendation for v141/v141_xp builds; assistant endorsed with caveats. | Established practical immediate build path. | Actionable after verification. | medium-high |
| 18 | Context Transfer Packet request | User requested maximum-fidelity handoff; assistant produced CTP. | Created basis for this report package. | Current source artifact. | high |
| 19 | Report package request | User requested final downloadable per-chat package. | Triggered this file bundle. | Current task. | high |

## 7. Decisions

| ID | Decision | Status | Evidence / basis | Rationale | Implications | Related workstream | Confidence | Label |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| DECISION-01 | Architecture is closed and canon locked | final | Latest upstream system-role block | Prevents redesign; new chat implements/audits only. | All future prompts must not reopen settled architecture. | WORKSTREAM-01 | high | FACT |
| DECISION-02 | Core ontology is Assemblies, Fields, Processes, Agents, Law | final | Latest upstream block | All systems reduce to canonical primitives. | New concepts outside ontology invalid unless canon changes. | WORKSTREAM-01 | high | FACT |
| DECISION-03 | Engine baseline language is C89 | final | Latest upstream block | Legacy portability and ABI stability. | Engine feature use constrained; public C ABI reinforced. | WORKSTREAM-01 | high | FACT |
| DECISION-04 | Game baseline language is C++98 | final | Latest upstream block | Supports legacy toolchain floor while allowing game ergonomics. | C++17 may apply to apps/tools but not impose on game. | WORKSTREAM-01 | high | FACT |
| DECISION-05 | Public headers remain parseable forever with no C++ ABI leakage | final | Latest upstream block and language-profile proposal | Cross-toolchain/module stability. | Need header audits and C ABI boundaries. | WORKSTREAM-10 | high | FACT |
| DECISION-06 | BUILD-ID-0 supersedes previous build-number rules | final | Latest upstream block | Separates release identity from dev/CI traceability. | Remove every-build GBN increments; use GBN/BII. | WORKSTREAM-05 | high | FACT |
| DECISION-07 | GBN is centrally allocated only for beta/rc/release/hotfix | final | Latest upstream block | Avoids local/branch/fork global number conflicts. | Release gates needed; no local GBN allocation. | WORKSTREAM-05 | high | FACT |
| DECISION-08 | BII is always present for dev/ci builds | final | Latest upstream block | Traceability without consuming GBN. | Need BII stamping implementation. | WORKSTREAM-05 | medium-high | FACT |
| DECISION-09 | Protocol/schema/API/ABI versions are orthogonal and mismatches refuse loudly | final | Multiple prompts plus upstream block | Compatibility cannot be hidden inside SemVer. | Need negotiation/refusal tests. | WORKSTREAM-05 | high | FACT |
| DECISION-10 | Applications are orchestration shells; CLI is canonical | final | Latest APP canon block | GUI/TUI must not diverge from command graph. | UI binding validation required. | WORKSTREAM-03 | high | FACT |
| DECISION-11 | UI is data and never logic | final | Latest APP canon block | Prevents UI code from mutating simulation or install state. | UI IR and codegen enforce view-only behavior. | WORKSTREAM-03 | high | FACT |
| DECISION-12 | Tools are read-only by default | final | Latest APP canon block | Prevents tooling from becoming hidden mutation authority. | Tools need explicit authority for writes. | WORKSTREAM-03 | high | FACT |
| DECISION-13 | Setup is the only mutation authority for installs | final | Latest APP canon block | Keeps install state changes controlled and auditable. | Launcher/tools must route install mutations through setup. | WORKSTREAM-03 | high | FACT |
| DECISION-14 | Launcher is reference application | final | Latest APP canon block | Unifies app patterns and prelaunch orchestration. | Launcher CLI/command graph should be reference behavior. | WORKSTREAM-03 | high | FACT |
| DECISION-15 | Content must be capability-based and optional | accepted | Engine/game content response and upstream no magic defaults | Allows zero-asset boot and modular packs. | Packs cannot be mandatory requirements. | WORKSTREAM-02 | high | FACT |
| DECISION-16 | Demo/free mode is an authority profile, not a separate product/build | accepted in chat | User wanted no separate code/product; assistant proposed; no later contradiction | Avoids code forks and buyer friction. | Same package can serve demo and full users. | WORKSTREAM-07 | medium-high | FACT |
| DECISION-17 | Tourist role should allow free users to join servers as non-mutating observers/explorers | accepted in chat | User said tourist server access sounded cool; assistant elaborated | Strong demo with server-enforced limits. | Need authority/capability tests. | WORKSTREAM-07 | medium-high | FACT |
| DECISION-18 | Piracy containment means preventing durable value extraction, not preventing copying | accepted in chat | User asked; assistant explained limitation of all-form piracy prevention | Preserves core tenets and avoids DRM rot. | Durable value must be server/entitlement-authorized. | WORKSTREAM-07 | medium-high | FACT |
| DECISION-19 | Control systems are optional external capability-gated layers | accepted in chat | Scratchpad prompt endorsed and TESTX2 generated | Keeps DRM/anti-cheat/telemetry out of deterministic core. | Control non-interference tests needed. | WORKSTREAM-06 | medium-high | FACT |
| DECISION-20 | No DRM/anti-cheat enforcement/secrets in engine/game | accepted in chat | Scratchpad prompt and TESTX2 | Prevents determinism and audit corruption. | Secrets only launcher/platform/cloud/backend. | WORKSTREAM-06 | medium-high | FACT |
| DECISION-21 | IDEs are projections, not project truth | accepted in chat | REPOX prompt and user goal | Avoids IDE corruption and multi-era project drift. | CMake/TestX/RepoX own graph. | WORKSTREAM-08 | high | FACT |
| DECISION-22 | Future IDE project files should live under /ide unless grandfathered packaging input | planned | REPOX prompt; current tree shows no /ide | Creates quarantine root for generated projections. | Need audit before moving/classifying. | WORKSTREAM-08 | medium | INFERENCE |
| DECISION-23 | Separate binaries per OS/toolchain/floor | accepted | User toolchain matrix and warnings | ABI/CRT/SDK reality forbids one binary for all. | CMake artifacts must encode floor/toolchain. | WORKSTREAM-09 | high | FACT |
| DECISION-24 | Legacy tiers are frozen once validated | accepted | User toolchain matrix | Prevents accidental modernization breaking old users. | Old binaries can continue via data/protocol support. | WORKSTREAM-09 | high | FACT |
| DECISION-25 | VS2022-hosted v141_xp is acceptable for Windows MVP, not archival replacement | assessment | Other-chat recommendation and assistant response | Practical immediate testing while preserving archival plan. | Later VC6/VC7.1 VMs still needed. | WORKSTREAM-12 | medium-high | INFERENCE |
| DECISION-26 | Rules should map to executable checks | recommended | Assistant plan after user asked for tests for every rule | Makes canon enforceable and aggregatable. | Need RULES_TO_CHECKS_MATRIX.md. | WORKSTREAM-11 | medium | INFERENCE |
| DECISION-27 | Old OS support can be dropped without forcing old users to update if protocols/data remain compatible | accepted concept | User asked; assistant answered based on separation | Supports graceful retirement. | Do not introduce required unsupported capabilities. | WORKSTREAM-09 | medium-high | INFERENCE |

### Highest-impact decisions

The highest-impact decisions are DECISION-01 through DECISION-14 because they come from the latest upstream canon and directly constrain future implementation. DECISION-06 through DECISION-08 are especially important because they supersede earlier build-number designs. DECISION-21 through DECISION-25 are the key RepoX/toolchain decisions: IDEs are projections, artifacts are per floor/toolchain, and VS2022-hosted old toolsets are only an MVP strategy.

## 8. Pending Tasks and Next Actions

| ID | Task | Priority | Urgency | Owner | Dependencies | Inputs needed | Expected output | Recommended next step | Related workstream | Label |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| TASK-01 | Verify actual repo state against latest upstream canon | critical | immediate | New implementation chat | Repo access | CANON_INDEX.md, docs, version scripts, CMake, CI | Audit report, no changes | Inspect root and docs first | WORKSTREAM-05 | FACT |
| TASK-02 | Find or create CANON_INDEX.md | critical | high | Repo/canon maintainer | CLEAN-2 | Docs inventory | Single canon entrypoint | Search repo before creating | WORKSTREAM-05 | FACT |
| TASK-03 | Audit docs for status headers | critical | high | Repo/canon maintainer | CLEAN-2 | All docs | CANONICAL/DERIVED/HISTORICAL status report | Scan docs/ tree | WORKSTREAM-05 | FACT |
| TASK-04 | Reconcile build/version scripts to BUILD-ID-0 | critical | high | Build/Test maintainer | BUILD-ID-0 | Existing build scripts/version files | GBN/BII implementation plan | Inspect .dominium_build_number and update_build_number.cmake | WORKSTREAM-05 | FACT |
| TASK-05 | Disable or migrate every-build GBN allocation | critical | high | Build/Test maintainer | TASK-04 | Old build-number logic | No local GBN mutation | Patch scripts after audit | WORKSTREAM-05 | FACT |
| TASK-06 | Inventory IDE/project artifacts | high | high | RepoX maintainer | Repo access | File list/git tracking | Projection vs grandfathered packaging classification | Search for .sln/.vcxproj/.pbxproj/.xcodeproj/.mcp/.vs | WORKSTREAM-08 | FACT |
| TASK-07 | Implement /ide projection root if absent | high | medium | RepoX maintainer | TASK-06 | Projection policy | /ide README and structure | Create after classification | WORKSTREAM-08 | INFERENCE |
| TASK-08 | Add verify_ide_quarantine.py | high | medium | RepoX maintainer | TASK-06/07 | Whitelist and rules | CI check preventing IDE pollution | Draft script and tests | WORKSTREAM-08 | INFERENCE |
| TASK-09 | Audit APP-CANON docs and UI binding implementation | high | high | App/tooling maintainer | APP canon | UI IR/codegen docs/tests | Gap report | Search APP-CANON and UI binding refs | WORKSTREAM-03 | FACT |
| TASK-10 | Enforce tools read-only by default | high | medium | Tools maintainer | APP canon | Tool APIs/tests | Contract tests or policy checks | Audit tool mutation paths | WORKSTREAM-03 | FACT |
| TASK-11 | Create or verify RULES_TO_CHECKS_MATRIX.md | critical | high | TestX/RepoX maintainer | Rule inventory | Canon docs/scripts/tests | Matrix mapping rules to checks | Begin Phase 0 rule audit | WORKSTREAM-11 | INFERENCE |
| TASK-12 | Draft SPEC_LANGUAGE_PROFILES / TESTX4 doc | high | medium | Language governance maintainer | Language proposal and upstream constraints | Actual language usage audit | Language/ABI rules doc | Audit before hard enforcement | WORKSTREAM-10 | INFERENCE |
| TASK-13 | Implement public-header parseability checks | high | medium | TESTX4 maintainer | TASK-12 | Public headers | Try-compile/scanner checks | Start with engine/include, game/include, libs/contracts/include | WORKSTREAM-10 | INFERENCE |
| TASK-14 | Audit no FP/STL/static init in deterministic paths | high | medium | TESTX4 maintainer | TASK-12 | Source tree | Violation/blocker report | Define authoritative dirs, then scan | WORKSTREAM-10 | INFERENCE |
| TASK-15 | Create Windows MVP CMake floor presets | high | medium | Build maintainer | VS2022 components | Toolsets/SDKs | XP/Win7/Win8/Win10/Win11 presets | Verify installed components first | WORKSTREAM-12 | INFERENCE |
| TASK-16 | Set up Windows/Linux VMs for runtime floor tests | medium-high | medium | User/build maintainer | ISOs/toolchains | VM images | Runtime matrix | Start XP SP3 and Win7 SP1 | WORKSTREAM-12 | FACT |
| TASK-17 | Add no-silent-fallback renderer/backend tests | medium-high | medium | Render/app maintainer | Renderer caps | Test harness | Explicit selection refusal tests | Locate existing render caps tests | WORKSTREAM-04 | FACT |
| TASK-18 | Add zero-asset boot tests if absent | high | medium | Engine/game maintainer | Content/capability system | Test fixtures | Boot without packs/assets test | Audit existing smoke tests | WORKSTREAM-02 | FACT |
| TASK-19 | Audit hardcoded Earth/Sol/base-pack assumptions | high | medium | Content/game maintainer | Content system | Search patterns | Violation report | Search engine/game for Sol/Earth hardcoded paths | WORKSTREAM-02 | FACT |
| TASK-20 | Add authority/tourist/base_free tests when implementation exists | medium-high | medium | Server/auth maintainer | Authority system | Profiles/capabilities | Tourist non-mutation tests | Find authority profile implementation | WORKSTREAM-07 | INFERENCE |
| TASK-21 | Add no-secrets-in-engine/game scanner | medium-high | medium | Security/build maintainer | TESTX2 | Secret patterns/allowlists | CI check | Implement after control docs located | WORKSTREAM-06 | INFERENCE |
| TASK-22 | Add policy-as-data skeleton | medium | medium | RepoX/TestX maintainer | TASK-11 | Policy schema | /policies/rules + runner skeleton | After matrix drafted | WORKSTREAM-11 | INFERENCE |
| TASK-23 | Add build provenance manifest | medium | low-medium | Build maintainer | BUILD-ID-0 | Compiler/SDK metadata | build_manifest.json per artifact | After version system fixed | WORKSTREAM-05 | INFERENCE |
| TASK-24 | Define support levels for old OS/arch tiers | medium | medium | RepoX/build maintainer | Toolchain matrix | User support policy | Buildable/CI-covered/release-supported doc | After toolchain audit | WORKSTREAM-09 | INFERENCE |
| TASK-25 | Produce revised TESTX/REPOX/APPX prompts aligned with latest canon | medium-high | medium | Prompt/governance maintainer | Audit findings | Existing prompts/latest upstream | Updated implementation prompts | Do after verification, not before | WORKSTREAM-05 | INFERENCE |

### 8.1 Recommended Task Order

1. TASK-01 through TASK-04: verify repo canon and build/version state.
2. TASK-06 and TASK-09: inventory IDE artifacts and APP/UI binding state.
3. TASK-11 through TASK-14: create rule/check and language-profile audit foundations.
4. TASK-15 and TASK-16: implement practical Windows MVP floor builds after toolchain verification.
5. TASK-17 through TASK-24: fill targeted enforcement gaps.

### 8.2 Blocked Tasks

TASK-07, TASK-08, TASK-12, TASK-15, and TASK-22 are blocked on audits or verification.

### 8.3 Quick Wins

- Search for `CANON_INDEX.md`.
- Inspect `.dominium_build_number`.
- Inspect `CMakePresets.json`.
- Inventory IDE files with a simple file search.
- Search for `BUILD-ID-0` and `APP-CANON`.

### 8.4 Tasks Requiring Verification

All tasks touching actual repo state require verification because this package is based on visible chat and a pasted tree, not direct file inspection.

## 9. Constraints and Requirements

### 9.1 Hard Requirements

See constraints marked hard in the table.

### 9.2 Soft Preferences

User preferences are listed in Section 3. Most project constraints here are hard, not soft.

### 9.3 Technical Constraints

Key technical constraints include C89/C++98 baselines, C ABI boundaries, no FP in authoritative logic, no CRT mixing, per-floor artifacts, and no IDE source-of-truth.

### 9.4 Time / Resource Constraints

No explicit dates for implementation were set. User has installed Windows 10 + VS2022 and plans VMs for older Windows/Linux.

### 9.5 Legal / Ethical / Safety Constraints

DRM/anti-cheat/control systems must be optional, external, discoverable, and non-interfering; piracy strategy must not corrupt core tenets.

### 9.6 Evidence / Citation Requirements

External software/toolchain claims require verification before action.

### 9.7 Formatting / Output Requirements

Current request required downloadable files, stable IDs, labels, tables, YAML, manifest, and audit.

### 9.8 Things to Avoid

Do not redesign canon, reintroduce every-build GBN, treat IDE projects as authoritative, add logic to UI, hardcode content, or treat tentative assistant suggestions as final.

| ID | Constraint | Type | Hard/soft | Source / basis | Practical implication | Violation risk | Confidence | Label |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| CONSTRAINT-01 | Architecture is closed; no redesign/reinterpretation | governance | hard | Latest upstream block | Implementation/audit only | High | high | FACT |
| CONSTRAINT-02 | All systems reduce to Assemblies, Fields, Processes, Agents, Law | ontology | hard | Latest upstream block | No new primitives unless canon changes | High | high | FACT |
| CONSTRAINT-03 | Process-only mutation | simulation | hard | Latest upstream block | State changes must be represented as processes | High | high | FACT |
| CONSTRAINT-04 | Deterministic replayable simulation | simulation/test | hard | TESTX/upstream | No nondeterministic authoritative behavior | High | high | FACT |
| CONSTRAINT-05 | Fixed-point authoritative logic; no FP in authoritative paths | numeric | hard | TESTX/upstream | Use fixed/integer math for sim state | High | high | FACT |
| CONSTRAINT-06 | Named RNG streams only | determinism | hard | Latest upstream block | No ad-hoc RNG | High | high | FACT |
| CONSTRAINT-07 | Strong epistemics and fog-of-war everywhere | game/sim | hard | Latest upstream block | No omniscient UI/tool defaults | High | high | FACT |
| CONSTRAINT-08 | No hardcoded content or magic defaults | content | hard | Latest upstream block | Zero-asset boot and capability resolution | High | high | FACT |
| CONSTRAINT-09 | Engine C89 | language | hard | Latest upstream block | No C99/C11 assumptions in engine baseline | High | high | FACT |
| CONSTRAINT-10 | Game C++98 | language | hard | Latest upstream block | No C++17 requirements imposed on game baseline | High | high | FACT |
| CONSTRAINT-11 | Public headers parseable forever and no C++ ABI leakage | ABI | hard | Latest upstream block | C ABI/stable public headers | High | high | FACT |
| CONSTRAINT-12 | Apps may use newer toolchains but must not impose on engine/game | layering | hard | Latest upstream block | Modern app features stay behind boundaries | Medium-high | high | FACT |
| CONSTRAINT-13 | CLI is canonical | application | hard | APP canon | GUI/TUI bind to command graph | High | high | FACT |
| CONSTRAINT-14 | UI is data, never logic | application/UI | hard | APP canon | UI IR/codegen not gameplay | High | high | FACT |
| CONSTRAINT-15 | Tools read-only by default | tools | hard | APP canon | Writes require explicit authority | High | high | FACT |
| CONSTRAINT-16 | Setup only install mutation authority | setup | hard | APP canon | Install mutations route through setup | High | high | FACT |
| CONSTRAINT-17 | Launcher reference application | application | hard | APP canon | Launcher behavior guides app patterns | Medium | high | FACT |
| CONSTRAINT-18 | Product SemVer manual | versioning | hard | BUILD-ID-0 | No automatic SemVer bumps | Medium | high | FACT |
| CONSTRAINT-19 | GBN central/release-only and shared by release products | versioning/release | hard | BUILD-ID-0 | No local GBN allocation | High | high | FACT |
| CONSTRAINT-20 | BII always present for dev/ci | versioning | hard | BUILD-ID-0 | Every build traceable without GBN | Medium | high | FACT |
| CONSTRAINT-21 | No distributed artifact without GBN | release | hard | BUILD-ID-0 | Release/distribution gates required | High | high | FACT |
| CONSTRAINT-22 | Protocol/schema/API/ABI versions orthogonal and mismatches refuse loudly | compatibility | hard | BUILD-ID-0/upstream | No silent compatibility coercion | High | high | FACT |
| CONSTRAINT-23 | IDEs are non-authoritative projections | repo | hard | REPOX plan | CMake/TestX own graph | High | high | FACT |
| CONSTRAINT-24 | Do not open repo root in legacy IDEs | workflow | hard | REPOX plan | Prevent project pollution | Medium-high | medium | INFERENCE |
| CONSTRAINT-25 | Separate binaries per OS/toolchain/floor | build | hard | User toolchain matrix | No one-binary-for-all | High | high | FACT |
| CONSTRAINT-26 | Never mix CRTs across module boundaries | ABI/build | hard | User toolchain matrix | Avoid heap/runtime crashes | High | high | FACT |
| CONSTRAINT-27 | Never pass STL/allocator-owned objects across DLL boundaries | ABI | hard | User toolchain matrix | Use C ABI/handles | High | high | FACT |
| CONSTRAINT-28 | Legacy tiers frozen once validated | support | hard | User toolchain matrix | Avoid accidental capability creep | Medium-high | high | FACT |
| CONSTRAINT-29 | Control systems disabled by default and non-interfering | control/security | hard | TESTX2 plan | No DRM/anti-cheat effect on sim | High | medium-high | FACT |
| CONSTRAINT-30 | No secrets in engine/game | security | hard | TESTX2 plan | Secrets only external layers | High | medium-high | FACT |
| CONSTRAINT-31 | Explicit renderer/backend request fails if unavailable; auto fallback must log | render/app | hard in tests | AP response | No silent fallback | Medium-high | high | FACT |
| CONSTRAINT-32 | Demo/free/paid/services use authority profiles, not code forks | distribution/business | hard if adopted | TESTX3 plan/user acceptance | One distribution model | Medium | medium-high | FACT |
| CONSTRAINT-33 | Old binaries may receive updates only within declared capabilities/protocol compatibility | support | hard by implication | Old OS support discussion | No required unsupported capabilities | Medium-high | medium-high | INFERENCE |
| CONSTRAINT-34 | External-world software/toolchain facts require future verification | evidence | hard | User/system factuality preference | Verify SDK/tool availability before acting | Medium | high | FACT |
| CONSTRAINT-35 | Do not treat brainstorms as user decisions unless accepted | process | hard | User request for report package | Preserve tentative status | Medium-high | high | FACT |

## 10. Open Questions and Unresolved Issues

| ID | Question / issue | Why it matters | Known information | Unknown information | What would resolve it | Priority | Related workstream | Label |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| QUESTION-01 | Does CANON_INDEX.md exist, and where? | Latest canon says it is single source of truth. | Name required by upstream. | Repo snapshot did not show it. | File search | critical | WORKSTREAM-05 | UNCERTAIN / UNVERIFIED |
| QUESTION-02 | Which docs are CANONICAL / DERIVED / HISTORICAL? | CLEAN-2 and RepoX enforcement depend on status headers. | Docs tree is large. | Actual headers unknown. | Scan docs headers | critical | WORKSTREAM-05 | UNCERTAIN / UNVERIFIED |
| QUESTION-03 | Where are BUILD-ID-0, CLEAN-2, APP-CANON0/1, APP-AUTO-0, APP-UI-BIND-0, SRZ-0, VALIDATE-0 documented? | Need exact canon citations and enforcement inputs. | Names provided by upstream. | Paths/content unknown. | Search docs/schema | critical | WORKSTREAM-05 | UNCERTAIN / UNVERIFIED |
| QUESTION-04 | Does .dominium_build_number conflict with BUILD-ID-0? | Old build-number artifacts may violate new release-only GBN. | File exists in tree. | Contents/usage unknown. | Inspect file and references | critical | WORKSTREAM-05 | UNCERTAIN / UNVERIFIED |
| QUESTION-05 | What does update_build_number.cmake do? | Could implement superseded every-build increment. | File exists under setup/packages/scripts. | Behavior unknown. | Inspect script | critical | WORKSTREAM-05 | UNCERTAIN / UNVERIFIED |
| QUESTION-06 | Are product SemVer files present and where? | Manual product versioning required. | Versions discussed, but tree did not show obvious version dir. | Actual files unknown. | Search *.version and version/ | high | WORKSTREAM-05 | UNCERTAIN / UNVERIFIED |
| QUESTION-07 | What is the exact BII format? | Needed for dev/ci stamping. | BII always present. | No exact scheme supplied. | Find BUILD-ID-0 or define under canon | high | WORKSTREAM-05 | UNCERTAIN / UNVERIFIED |
| QUESTION-08 | What counts as a distributed artifact? | No distributed artifact without GBN. | Rule exists. | CI artifacts vs local zips vs store uploads unclear. | Canon clarification | high | WORKSTREAM-05 | UNCERTAIN / UNVERIFIED |
| QUESTION-09 | Which IDE files are tracked and which are accidental local state? | RepoX quarantine must not break packaging. | Tree shows .vs/.vscode and VS/Xcode packaging files. | Git tracking unknown. | git ls-files/search | high | WORKSTREAM-08 | UNCERTAIN / UNVERIFIED |
| QUESTION-10 | Does /ide already exist? | REPOX projection root planned. | Tree did not show it. | Repo may have changed. | File search | medium-high | WORKSTREAM-08 | UNCERTAIN / UNVERIFIED |
| QUESTION-11 | What CMake presets already exist? | Need avoid duplicating and implement Windows MVP floors. | CMakePresets.json exists. | Contents unknown. | Inspect file | high | WORKSTREAM-12 | UNCERTAIN / UNVERIFIED |
| QUESTION-12 | Are VS2022 v141/v141_xp/SDK components installed? | MVP build plan depends on them. | User installed VS2022. | Components unknown. | VS Installer/CMake configure | high | WORKSTREAM-12 | UNCERTAIN / UNVERIFIED |
| QUESTION-13 | Are public headers C89 parseable? | Latest canon requires it. | Headers exist. | Compliance unknown. | Try-compile audit | high | WORKSTREAM-10 | UNCERTAIN / UNVERIFIED |
| QUESTION-14 | Does game code already use C++17 features? | Game baseline C++98. | Many .cpp files exist. | Feature usage unknown. | Language scan/compiler tests | high | WORKSTREAM-10 | UNCERTAIN / UNVERIFIED |
| QUESTION-15 | Are deterministic paths using FP, STL, static init, exceptions, RTTI? | TESTX4 enforcement depends on facts. | Proposal bans them. | Actual violations unknown. | Static scans | high | WORKSTREAM-10 | UNCERTAIN / UNVERIFIED |
| QUESTION-16 | Do zero-asset boot tests already exist? | No hardcoded content/magic defaults. | Smoke tests exist. | Specific zero-asset coverage unknown. | Inspect tests | high | WORKSTREAM-02 | UNCERTAIN / UNVERIFIED |
| QUESTION-17 | Is UI binding validation automatic? | APP-UI-BIND requires it. | UI IR/codegen exists. | Automation unknown. | Inspect scripts/tests/CI | high | WORKSTREAM-03 | UNCERTAIN / UNVERIFIED |
| QUESTION-18 | Are tools actually read-only by default? | APP canon requires it. | Many editor tools exist. | Authority/mutation behavior unknown. | Audit tool APIs/tests | high | WORKSTREAM-03 | UNCERTAIN / UNVERIFIED |
| QUESTION-19 | Is tourist/base_free/full_player authority implemented or only planned? | Demo/piracy model depends on authority profiles. | Concept accepted in chat. | Code/docs unknown. | Search authority/profile docs/code | medium-high | WORKSTREAM-07 | UNCERTAIN / UNVERIFIED |
| QUESTION-20 | How long should old binaries receive protocol/content support after dropping OS builds? | User wants no forced updates ideally. | Architecture supports it. | Support policy/window unknown. | User/canon decision | medium | WORKSTREAM-09 | UNCERTAIN / UNVERIFIED |

## 11. Rejected, Superseded, or Deprioritised Options

| ID | Option | Status | Reason rejected/superseded/deprioritised | Is rejection final? | Reconsider conditions | Related workstream | Label |
| --- | --- | --- | --- | --- | --- | --- | --- |
| REJECTED-01 | Increment global build number on every configure/build | superseded | BUILD-ID-0 makes GBN release-only and centrally allocated. | final | Only if BUILD-ID-0 changes | WORKSTREAM-05 | FACT |
| REJECTED-02 | Increment version/build.txt after all tests for all builds | superseded | BUILD-ID-0 splits GBN and BII. | final | Only with canon change | WORKSTREAM-05 | FACT |
| REJECTED-03 | Treat demo as separate product or code fork | rejected | User wanted no separate product/code; authority-profile model chosen. | final unless platform forces packaging workaround | If storefront requires separate depot while same binaries retained | WORKSTREAM-07 | FACT |
| REJECTED-04 | Use strong client/core DRM to prevent piracy | rejected | Violates determinism/openness and cannot prevent all piracy. | final | Only as optional external control layer, not core | WORKSTREAM-06 | FACT |
| REJECTED-05 | Put DRM or anti-cheat enforcement in engine/game | rejected | Scratchpad and TESTX2 placed enforcement outside core. | final | Never unless canon changes | WORKSTREAM-06 | FACT |
| REJECTED-06 | Silent renderer/backend fallback | rejected in tests | AP response required explicit failure for explicit requests. | final for tests | User-facing auto fallback with explicit logging is allowed | WORKSTREAM-04 | FACT |
| REJECTED-07 | One binary for all OS floors | rejected | Toolchain matrix says compiler/SDK/CRT define ABI reality. | final | Never | WORKSTREAM-09 | FACT |
| REJECTED-08 | Collapse Mac support into one Xcode | rejected | Apple removes SDKs; era-pinned Xcodes needed. | final | Only if verified toolchain proves otherwise | WORKSTREAM-09 | FACT |
| REJECTED-09 | Use modern VS/v143 for XP/early floors | rejected | VS2022/v143 cannot target XP; old toolsets required. | final | Never for those OS floors | WORKSTREAM-12 | FACT |
| REJECTED-10 | Extend VC6 into XP/Vista tier | rejected by matrix | User matrix says VC7.1 is XP/Vista bridge and do not extend VC6. | final for archival | MVP v141_xp is separate practical bridge | WORKSTREAM-09 | FACT |
| REJECTED-11 | Treat IDE projects as source of truth | rejected | REPOX says IDEs are projections. | final | Never | WORKSTREAM-08 | FACT |
| REJECTED-12 | Open repo root in legacy IDEs | rejected | Risks IDE metadata/source-list corruption. | final | Never | WORKSTREAM-08 | INFERENCE |
| REJECTED-13 | Hardcode Earth/Sol/base content into engine | rejected | No hardcoded content/magic defaults and zero-asset boot. | final | Never | WORKSTREAM-02 | FACT |
| REJECTED-14 | Mandatory base content pack | rejected | Packs provide capabilities and cannot be requirements. | final | Never | WORKSTREAM-02 | FACT |
| REJECTED-15 | Put gameplay logic in applications or UI | rejected | APP canon says apps orchestration shells and UI data not logic. | final | Never | WORKSTREAM-03 | FACT |
| REJECTED-16 | Tools mutate by default | rejected | APP canon says tools read-only by default. | final | Never | WORKSTREAM-03 | FACT |
| REJECTED-17 | Add new ontology primitives | rejected by latest canon | Core ontology is non-negotiable. | final unless architecture reopens | Only if user/canon explicitly changes | WORKSTREAM-01 | FACT |
| REJECTED-18 | Continue architectural redesign in implementation chat | rejected by latest canon | Architecture closed/canon locked. | final | Only if user opens design phase | WORKSTREAM-01 | FACT |

Preserving rejected and superseded options prevents repeated work. The most dangerous repeated mistakes would be reviving every-build GBN, treating demo as a separate code fork, allowing IDEs to own project files, or using modern toolchains to claim unsupported old OS compatibility.

## 12. Artifact Ledger

| ID | Artifact / file / prompt / output | Type | Purpose | Status | Where it came from | Carry forward? | Notes | Label |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| ARTIFACT-01 | Original Context Transfer Packet | report/output | Maximum-fidelity handoff from retired chat | produced in previous assistant response | This chat | yes | Basis for this package | FACT |
| ARTIFACT-02 | TESTX original prompt | mega-prompt | Self-defending verification/test/version governance | authoritative but versioning superseded by BUILD-ID-0 | User pasted from Game chat | yes | Revise, do not discard | FACT |
| ARTIFACT-03 | EG-TESTX prompt | forwarding prompt | Inform Engine/Game chat of TESTX-aligned constraints | historical/derived | Assistant generated | concepts only | Use as evidence of alignment, not top canon | FACT |
| ARTIFACT-04 | AP-TESTX prompt | forwarding prompt | Inform Application/Platform/Render chat | historical/derived | Assistant generated | concepts only | Use as evidence of alignment | FACT |
| ARTIFACT-05 | EG response prompt | response | Engine/game acceptance and tensions | historical evidence | User pasted | yes | Contains docs/build/no-FP/comment-density tension resolutions | FACT |
| ARTIFACT-06 | AP response prompt | response | App/platform/render acceptance and tensions | historical evidence | User pasted | yes | Contains no-silent-fallback resolution | FACT |
| ARTIFACT-07 | TESTX2 mega prompt | mega-prompt | Control layers/non-interference/governance | derived/planned | Assistant generated | yes if reconciled | Not proven implemented | FACT |
| ARTIFACT-08 | TESTX3 mega prompt | mega-prompt | Authority/demo/services/piracy containment | derived/planned | Assistant generated | yes if reconciled | Not proven implemented | FACT |
| ARTIFACT-09 | REPOX mega prompt | mega-prompt | Repository/IDE/toolchain/multi-arch governance | derived/planned; needs BUILD-ID/CLEAN-2 revision | Assistant generated | yes | Core of RepoX plan | FACT |
| ARTIFACT-10 | TESTX4 language-profile proposal | proposal | Feature allowlists and transition playbook | recommended; not confirmed top-level canon | User pasted from other chat | yes | Should be audited before enforcement | FACT |
| ARTIFACT-11 | Latest upstream SYSTEM ROLE block | authoritative prompt | Top-of-tree implementation/maintenance canon | authoritative in this chat | User pasted | yes highest priority | Supersedes conflicts | FACT |
| ARTIFACT-12 | Windows VS2022 MVP recommendation | recommendation | Practical XP→11 build floors from Windows 10 host | useful but verify externally | User pasted from other chat | yes | External tool facts require verification | FACT |
| ARTIFACT-13 | .dominium_build_number | repo file | Possible old build number state | exists in user tree; contents unknown | User tree | yes verify | May conflict with BUILD-ID-0 | FACT |
| ARTIFACT-14 | CMakeLists.txt | repo file | Root build graph | exists | User tree | yes | Canonical build input | FACT |
| ARTIFACT-15 | CMakePresets.json | repo file | Build presets | exists; contents unknown | User tree | yes inspect | Needed for floor/IDE presets | FACT |
| ARTIFACT-16 | .github/workflows/ci.yml | repo file | CI workflow | exists; contents unknown | User tree | yes inspect | Needed for TestX/RepoX gates | FACT |
| ARTIFACT-17 | docs/arch/ | repo directory | Architecture docs | exists with many files | User tree | yes | Needs CLEAN-2/status audit | FACT |
| ARTIFACT-18 | docs/policies/ | repo directory | Policy docs | exists | User tree | yes | Potential source for determinism/perf/language policies | FACT |
| ARTIFACT-19 | docs/specs/ | repo directory | Spec docs | exists with large set | User tree | yes | Needs status/canon audit | FACT |
| ARTIFACT-20 | schema/ | repo directory | Schema governance and domain schemas | exists | User tree | yes | Protocol/schema validation source | FACT |
| ARTIFACT-21 | engine/ | repo directory | Engine code/tests/render/platform | exists | User tree | yes | C89/ABI/determinism audit target | FACT |
| ARTIFACT-22 | game/ | repo directory | Game logic/content/rules/tests | exists | User tree | yes | C++98 and sim rules audit target | FACT |
| ARTIFACT-23 | client/ | repo directory | Client product | exists | User tree | yes | APP canon target | FACT |
| ARTIFACT-24 | server/ | repo directory | Server product | exists | User tree | yes | Authority/SRZ/headless target | FACT |
| ARTIFACT-25 | launcher/ | repo directory | Launcher product | exists | User tree | yes | Reference application target | FACT |
| ARTIFACT-26 | setup/ | repo directory | Setup/installer product | exists | User tree | yes | Install mutation authority target | FACT |
| ARTIFACT-27 | tools/ | repo directory | Tools/editors/codegen/validation | exists | User tree | yes | Read-only default/UI tooling target | FACT |
| ARTIFACT-28 | tools/ui_shared and UI IR/codegen dirs | repo dirs | UI IR/codegen substrate | exists | User tree | yes | APP-UI-BIND relevant | FACT |
| ARTIFACT-29 | tools/launcher/ui doc/gen/user pattern | repo dirs/files | Launcher UI generation | exists | User tree | yes | Preserve gen/user model | FACT |
| ARTIFACT-30 | tools/setup/ui doc/gen/user pattern | repo dirs/files | Setup UI generation | exists | User tree | yes | Preserve gen/user model | FACT |
| ARTIFACT-31 | scripts/verify_cmake_no_global_includes.py | script | CMake/include enforcement | exists | User tree | yes extend | Possible policy runner integration | FACT |
| ARTIFACT-32 | scripts/verify_includes_sanity.py | script | Include sanity enforcement | exists | User tree | yes extend | Possible TESTX4 integration | FACT |
| ARTIFACT-33 | scripts/verify_tree_sanity.bat | script | Tree sanity checks | exists | User tree | yes extend | RepoX quarantine integration | FACT |
| ARTIFACT-34 | setup/packages/scripts/update_build_number.cmake | script | Build number updating | exists; behavior unknown | User tree | yes verify | Critical BUILD-ID-0 audit item | FACT |
| ARTIFACT-35 | Proposed /ide directory | planned artifact | IDE projection root | not shown in tree; planned | REPOX prompt | carry if approved | Add only after audit | INFERENCE |
| ARTIFACT-36 | Proposed RULES_TO_CHECKS_MATRIX.md | planned doc | Map every rule to enforcement | not shown; recommended | Assistant plan | yes | High-priority governance artifact | INFERENCE |
| ARTIFACT-37 | Proposed /policies/rules/*.json | planned files | Policy-as-data | not shown; recommended | Assistant plan | yes | Implement after matrix | INFERENCE |

## 13. Rationale and Assumptions

Major choices in this chat were driven by visible, repeated requirements: longevity, determinism, auditability, modularity, old/new toolchain coexistence, and avoidance of future refactors. The rationale for C89/C++98 baselines and C ABI boundaries is not aesthetic; it follows from legacy OS/toolchain goals, cross-CRT risks, and the desire to let applications modernize without imposing requirements on engine/game. The rationale for IDE projections is that IDEs from different eras cannot safely own the project graph. Treating them as generated, disposable views preserves CMake/TestX/RepoX as source of truth while still allowing WYSIWYG design.

The rationale for demo/free/tourist authority profiles is buyer-friction reduction and codebase unification. A separate demo product would create maintenance divergence, while a single distribution with limited authority lets users inspect and experience the game honestly. Piracy containment is framed as prevention of durable value extraction because copying offline binaries cannot be prevented without compromising project tenets. Control systems are therefore placed outside engine/game and must not alter authoritative simulation results.

The latest upstream canon introduces a key assumption: design is closed. Therefore previous prompts should be treated as implementation scaffolding, not invitations to continue design. Another important assumption is that the pasted repo tree accurately represented the repository at that time; this remains unverified in this package. External toolchain recommendations, especially around VS2022, v141_xp, SDK availability, and OS targeting, are useful but require verification before implementation because software versions and installed components are external-world facts.

## 14. Risks and Failure Modes

| ID | Risk / failure mode | Consequence | Likelihood | Severity | Mitigation | Related workstream | Label |
| --- | --- | --- | --- | --- | --- | --- | --- |
| RISK-01 | New assistant treats old generated prompts as higher authority than latest upstream | Could revive obsolete build rules or redesign | medium | high | Use source hierarchy; latest upstream wins | WORKSTREAM-05 | FACT |
| RISK-02 | Old build-number scripts allocate GBN locally | Violates BUILD-ID-0 and corrupts release identity | medium | critical | Audit .dominium_build_number and update_build_number.cmake | WORKSTREAM-05 | FACT |
| RISK-03 | Docs remain unconsolidated | Live code may reference historical docs; contradictions persist | high | high | Implement CLEAN-2 and CANON_INDEX.md | WORKSTREAM-05 | FACT |
| RISK-04 | IDE artifacts become source of truth | Build graph drifts and legacy IDEs corrupt repo | medium | high | RepoX quarantine and /ide projections | WORKSTREAM-08 | FACT |
| RISK-05 | UI designer output contains logic | GUI/TUI bypass command graph or mutate state | medium | high | APP-UI-BIND validation and UI shell purity checks | WORKSTREAM-03 | FACT |
| RISK-06 | Demo/free model becomes a code fork | Maintenance burden and buyer confusion | low-medium | medium-high | Keep demo as authority profile | WORKSTREAM-07 | FACT |
| RISK-07 | DRM/anti-cheat creeps into engine/game | Breaks determinism/replay/openness | low-medium | high | TESTX2 no-secrets/non-interference checks | WORKSTREAM-06 | FACT |
| RISK-08 | Required new capability cuts off old binaries unintentionally | Dropped OS users lose updates or servers unexpectedly | medium | high | Capability negotiation and degradation policy | WORKSTREAM-09 | INFERENCE |
| RISK-09 | Modern C++/SDK features leak into legacy targets | Old OS builds silently fail at runtime | medium | high | TESTX4 language profiles and floor presets | WORKSTREAM-09 | FACT |
| RISK-10 | VS2022 v141_xp mistaken for archival VC7.1 | False confidence in long-term XP/Vista bridge | medium | medium | Label as MVP only; maintain VM archival plan | WORKSTREAM-12 | INFERENCE |
| RISK-11 | Rules remain prose-only | Future contributors bypass canon accidentally | high | high | RULES_TO_CHECKS_MATRIX and policy runner | WORKSTREAM-11 | INFERENCE |
| RISK-12 | Over-refactoring during governance implementation | Runtime semantics change despite maintenance-only canon | medium | high | Audit/docs/scripts first; no runtime behavior changes | WORKSTREAM-05 | FACT |
| RISK-13 | Over-compression loses prompt details | Future aggregation omits important constraints | medium | medium | Use report package plus original saved prompts where possible | WORKSTREAM-05 | INFERENCE |
| RISK-14 | Assistant guesses external tool facts | Bad VS/SDK/OS support decisions | medium | medium-high | Verify current toolchain facts before use | WORKSTREAM-12 | FACT |
| RISK-15 | Treating tentative TESTX4/policy-as-data ideas as already implemented | False assumptions in next chat | medium | medium | Label as recommended/planned until verified | WORKSTREAM-10 | FACT |

## 15. Verification Queue

| ID | Item requiring verification | Why verification is needed | Suggested verification source/type | Priority | Related workstream | Label |
| --- | --- | --- | --- | --- | --- | --- |
| VERIFY-01 | Locate CANON_INDEX.md | Required by CLEAN-2 single source of truth | File search/repo inspection | critical | WORKSTREAM-05 | UNCERTAIN / UNVERIFIED |
| VERIFY-02 | Audit docs status headers | Required to distinguish canonical/derived/historical | Script/manual scan of docs | critical | WORKSTREAM-05 | UNCERTAIN / UNVERIFIED |
| VERIFY-03 | Find CLEAN-2/BUILD-ID-0/APP/SRZ/VALIDATE docs | Need exact canon citations | Repo search | critical | WORKSTREAM-05 | UNCERTAIN / UNVERIFIED |
| VERIFY-04 | Inspect .dominium_build_number | Possible superseded build-number artifact | File contents/reference search | critical | WORKSTREAM-05 | UNCERTAIN / UNVERIFIED |
| VERIFY-05 | Inspect update_build_number.cmake | Could violate BUILD-ID-0 | Read script | critical | WORKSTREAM-05 | UNCERTAIN / UNVERIFIED |
| VERIFY-06 | Search for product version files | Manual SemVer implementation | File search | high | WORKSTREAM-05 | UNCERTAIN / UNVERIFIED |
| VERIFY-07 | Inspect CMakePresets.json | Need existing presets and add floor/projection safely | File inspection | high | WORKSTREAM-12 | UNCERTAIN / UNVERIFIED |
| VERIFY-08 | Inspect CI workflow | Need know existing gates | Read .github/workflows/ci.yml | high | WORKSTREAM-05 | UNCERTAIN / UNVERIFIED |
| VERIFY-09 | Run IDE artifact inventory | RepoX quarantine requires classification | File search and git tracking | high | WORKSTREAM-08 | UNCERTAIN / UNVERIFIED |
| VERIFY-10 | Check whether /ide exists | Projection root state | File search | medium-high | WORKSTREAM-08 | UNCERTAIN / UNVERIFIED |
| VERIFY-11 | Verify VS2022 components/toolsets/SDKs | Windows MVP plan depends on actual install | VS Installer/CMake configure | high | WORKSTREAM-12 | UNCERTAIN / UNVERIFIED |
| VERIFY-12 | Runtime-test XP/Win7/Win8/Win10/Win11 floors in VMs | Compile success is insufficient | VM smoke tests | high | WORKSTREAM-12 | UNCERTAIN / UNVERIFIED |
| VERIFY-13 | Audit public header C89 parseability | Required by upstream | try-compile/scanner | high | WORKSTREAM-10 | UNCERTAIN / UNVERIFIED |
| VERIFY-14 | Audit game C++98 compliance | Required by upstream | compiler/scanner | high | WORKSTREAM-10 | UNCERTAIN / UNVERIFIED |
| VERIFY-15 | Scan deterministic dirs for FP/STL/static init/exceptions/RTTI | Required by TESTX4 proposal | Static scans | high | WORKSTREAM-10 | UNCERTAIN / UNVERIFIED |
| VERIFY-16 | Find zero-asset boot tests | No hardcoded content/magic defaults | Test inventory | high | WORKSTREAM-02 | UNCERTAIN / UNVERIFIED |
| VERIFY-17 | Search hardcoded Sol/Earth/base-pack assumptions | User had content data but engine must not assume it | Source search | high | WORKSTREAM-02 | UNCERTAIN / UNVERIFIED |
| VERIFY-18 | Check APP UI binding validation | APP-UI-BIND required | Test/script inspection | high | WORKSTREAM-03 | UNCERTAIN / UNVERIFIED |
| VERIFY-19 | Check tool read-only default enforcement | APP canon required | Tool API/test audit | high | WORKSTREAM-03 | UNCERTAIN / UNVERIFIED |
| VERIFY-20 | Locate authority profiles implementation/docs | Needed for tourist/demo/piracy model | Repo search | medium-high | WORKSTREAM-07 | UNCERTAIN / UNVERIFIED |
| VERIFY-21 | Verify no secrets in engine/game | TESTX2 security constraint | Secret scanner/manual audit | medium-high | WORKSTREAM-06 | UNCERTAIN / UNVERIFIED |
| VERIFY-22 | Verify renderer no-silent-fallback tests | AP response accepted rule | Test inventory | medium | WORKSTREAM-04 | UNCERTAIN / UNVERIFIED |
| VERIFY-23 | Verify rules-to-checks matrix existence | Policy automation plan depends on it | File search | medium-high | WORKSTREAM-11 | UNCERTAIN / UNVERIFIED |
| VERIFY-24 | Verify policy-as-data files or runner existence | Avoid duplicating if already present | File search | medium | WORKSTREAM-11 | UNCERTAIN / UNVERIFIED |
| VERIFY-25 | Verify external toolchain facts before future use | Software versions/installers change over time | Official docs/installed tools | high before action | WORKSTREAM-12 | UNCERTAIN / UNVERIFIED |

## 16. Spec Book Contribution Notes

Likely future Project Spec Book sections fed by this chat:

- Governance and Canon Management
- TestX / Validate Enforcement
- Build Identity and Release Governance
- RepoX Repository Ownership and IDE Projections
- Language Profiles and ABI Stability
- Toolchain and OS Floor Matrix
- Application Layer Canon
- UI IR and Binding Enforcement
- Content Packs and Zero-Asset Boot
- Authority, Entitlements, Demo, Tourist Mode, and Services
- Control Layers and Non-Interference
- Old Binary Support and Graceful Retirement

Unique contributions from this chat include the integration of TestX/RepoX with build identity changes, the explicit supersession of earlier build-number models by BUILD-ID-0, the IDE-projection strategy, and the link between free/demo/tourist distribution and authority-based piracy containment.

Likely duplicates with other chats include core ontology, T0–T24 architecture, SRZ-0, APP-CANON details, and detailed engine/game/content schemas. Watch for conflicts around build-number naming, current CMake layout, and whether TESTX4/policy-as-data has been adopted elsewhere.

Items that should become formal requirements if not already canon: BUILD-ID-0 enforcement, CANON_INDEX status headers, APP UI binding validation, IDE quarantine, C ABI public headers, and rules-to-checks matrix. Items that should remain background unless confirmed: exact proposed file paths for new REPOX scripts, exact /ide subdirectory names, and exact Windows MVP preset names.

## 17. What Future Assistants Must Preserve

| Priority | Item | Type | Why it matters | Risk if lost | Label | Confidence |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | Latest upstream canon supersedes earlier assistant-generated prompts where conflicts exist. | source hierarchy | Prevents obsolete build/version/design behavior. | Wrong implementation direction. | FACT | high |
| 2 | BUILD-ID-0: GBN release-only, BII dev/ci, manual product SemVer. | versioning | This is the biggest concrete supersession. | Local build-number corruption. | FACT | high |
| 3 | Architecture closed; implementation/audit only. | governance | Stops redesign churn. | Repeated re-litigation. | FACT | high |
| 4 | Core ontology: Assemblies, Fields, Processes, Agents, Law. | ontology | All new implementation must reduce to this. | Invalid primitives introduced. | FACT | high |
| 5 | Engine C89, Game C++98, public headers parseable forever, no C++ ABI leakage. | language/ABI | Legacy/toolchain compatibility. | Old OS support breaks. | FACT | high |
| 6 | Applications are shells; CLI canonical; UI is data, never logic. | app canon | Prevents UI/app logic drift. | GUI bypasses command graph. | FACT | high |
| 7 | Setup is only install mutation authority; tools read-only by default. | app/setup/tools | Protects install/user state. | Hidden mutation paths. | FACT | high |
| 8 | IDEs are projections; CMake/TestX/RepoX own graph. | repo governance | Prevents project-file corruption. | Multi-IDE sprawl. | FACT | high |
| 9 | Content is optional, open-format, capability-provided; zero-asset boot. | content architecture | Modularity and old-binary updates. | Hardcoded base content. | FACT | high |
| 10 | Demo/free/tourist model uses authority profiles, not code forks. | distribution/authority | One distribution and low friction. | Separate demo maintenance. | FACT | medium-high |
| 11 | Piracy containment means preventing durable value extraction, not copying. | security/business | Preserves core tenets. | DRM creep. | FACT | medium-high |
| 12 | Control layers must be optional, external, disabled by default, and non-interfering. | control/security | Avoids deterministic core corruption. | Anti-cheat/DRM in engine. | FACT | medium-high |
| 13 | Toolchain matrix requires separate binaries per OS/toolchain/floor. | build/toolchain | Mechanical ABI reality. | Runtime failures. | FACT | high |
| 14 | VS2022 + v141_xp is MVP-practical but not archival substitute for VC7.1/VC6 VMs. | build planning | Avoids false support claims. | Mislabelled compatibility. | INFERENCE | medium-high |
| 15 | Next step is verification/audit, not modification. | process | Avoids acting on unverified repo state. | Bad patches. | FACT | high |

## 18. What Future Assistants Must Not Assume

- Do not assume TESTX4 is already implemented.
- Do not assume policy-as-data exists.
- Do not assume `/ide` exists.
- Do not assume `CANON_INDEX.md` exists until verified.
- Do not assume `.dominium_build_number` is valid under BUILD-ID-0.
- Do not assume VS2022 has v141/v141_xp/Windows 7.1A SDK installed.
- Do not assume v141_xp replaces archival VC7.1/VC6 VM tiers.
- Do not assume all docs are canonical.
- Do not assume old assistant-generated prompts outrank latest upstream canon.
- Do not assume demo/tourist/authority profiles are implemented in code.
- Do not assume UI binding validation is automatic.
- Do not assume tools are currently read-only by default.
- Do not assume old binaries can receive all updates without capability limits.

## 19. Recommended Next Action

If continuing this chat’s work alone: run a repo audit focused on CANON_INDEX, BUILD-ID-0 files/scripts, CMakePresets, CI, IDE artifacts, APP/UI binding, and language compliance.

If aggregating this chat with other reports: ingest this package as the governance/build/repo/toolchain/authority report, preserve source labels, and compare latest upstream canon with other chats’ canons before merging.

User verification needed before acting: confirm that the latest upstream canon remains top-of-tree, confirm whether TESTX4 should be formalized, and confirm whether `/ide` should be created now or after a repository audit.

## 20. Appendix: Possibly Relevant Details

- Root repo snapshot included `.dominium_build_number`, `CMakeLists.txt`, `CMakePresets.json`, `.github/workflows/ci.yml`, `.vs`, `.vscode`, `ci`, `client`, `cmake`, `data`, `docs`, `engine`, `game`, `launcher`, `legacy`, `libs`, `schema`, `scripts`, `server`, `setup`, and `tools`.
- Existing scripts include include sanity and tree sanity checks, which should be extended rather than duplicated.
- Existing UI codegen already uses doc/gen/user patterns; preserve this model.
- Existing docs are numerous and likely require CLEAN-2 status consolidation.
- Windows MVP build plan should use VS2022 as host for older toolsets only after component verification.
- External toolchain facts are time-sensitive and must be verified before implementation.
