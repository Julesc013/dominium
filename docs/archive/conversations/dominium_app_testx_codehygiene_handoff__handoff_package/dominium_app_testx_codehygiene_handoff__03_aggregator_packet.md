# Aggregator Packet — Dominium Application/TestX/CodeHygiene Handoff

## 1. Packet Metadata

- **Chat label:** Dominium Application/TestX/CodeHygiene Handoff
- **Date anchor:** 2026-05-27 Australia/Melbourne
- **Source scope:** This chat only; user-pasted other-chat material is labeled PROJECT-CONTEXT.
- **Coverage:** full for late visible context; partial for earlier hidden/omitted turns.
- **Confidence:** 4/5.
- **Staleness risk:** medium.
- **Merge priority:** high for application layer, testing/versioning/changelog, and code hygiene.
- **Main limitations:** No repo/source/docs inspection; generated prompts not proven executed.

## 2. Ultra-Condensed Carry-Forward Capsule

This chat’s aggregation value is primarily the convergence of several long-running Dominium/Domino planning streams into current implementation-facing plans. The project is treated as a deterministic universe engine/game whose architecture is closed and canon locked. Latest user-pasted PROJECT-CONTEXT states that all systems reduce to Assemblies, Fields, Processes, Agents, and Law; engine is C89; game is C++98; applications may use newer toolchains but must not impose requirements on engine/game; process-only mutation, deterministic replay, fixed-point authoritative logic, named RNG streams, strong epistemics, collapse/expand via macro capsules, SRZ-0, VALIDATE-0, TestX, RepoX, CLEAN-2, and DEV-OPS-0 are enforced. This chat must not be used to reopen architecture.

The most current actionable plan is APP-UNIFIED-CANON. It says application products are orchestration shells only: setup, launcher, client, server, tools. They must not contain gameplay logic, mutate authoritative world state, bypass law/authority/epistemics, invent defaults, hide failures, or bypass RepoX/TestX. CLI is canonical; GUI/TUI are views over the same command graph. UI is data via UI IR and contains no business logic. Setup is the only install mutation authority; launcher is the reference application; tools are read-only by default. Applications must run with zero content packs installed and expose RepoX build/changelog/compatibility information explicitly.

The chat also created TESTX, superseding TEST0. TESTX is a repository-wide self-defending test/version/changelog plan: CLI-only tests, Debug/Release/Windows CLI smoke builds, deterministic tests, assertion tiers, comment density, blocker cross-references, product versions, build kinds, GBN/BII, protocol/schema/API/ABI versions, strict commit taxonomy, and automatic changelog generation. However, latest BUILD-ID-0 pasted context supersedes earlier simple build-number concepts: GBN only for beta/rc/release/hotfix distributed artifacts, BII always for dev/ci, product SemVer manual, channels separate, mismatch refuses loudly.

The chat created CODEHYGIENE-X for source-code data/code boundary hygiene. It distinguishes architectural enums that stay in code from data-driven taxonomies of reality, tunable parameters, and derived generated conveniences. It mandates stable registries with `uint32_t` IDs, scanners for magic numbers, custom/other enums, switch-on-taxonomy, raw TODOs, comment density, admin/cheat flags, and a HYGIENE_QUEUE.

This chat also produced many earlier prompts across architecture, execution, ECS, kernels, domains, existence, travel, time, authority, life/civ/war/content/agents/tools/mods/final policies. Aggregators should preserve them as artifact history but not assume execution. The central warning is: generated prompts are not repository state.

## 3. Top Carry-Forward Items

| Priority | Item | Type | Related ID | Why It Matters | Label | Confidence |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | Architecture closed/canon locked | constraint | DECISION-01 | Prevents redesign drift | FACT / PROJECT-CONTEXT | high |
| 2 | APP-UNIFIED-CANON current app plan | artifact | ARTIFACT-02 | Application implementation anchor | FACT | high |
| 3 | TESTX current testing/version/changelog plan | artifact | ARTIFACT-03 | Verification/release governance anchor | FACT | high |
| 4 | CODEHYGIENE-X current hygiene plan | artifact | ARTIFACT-04 | Data/code boundary anchor | FACT | high |
| 5 | BUILD-ID-0 supersedes earlier build-number model | decision | DECISION-12 | Release identity correctness | FACT / PROJECT-CONTEXT | high |
| 6 | Generated prompts are not executed repo state | reliability | DECISION-14 | Avoids false file claims | FACT | high |
| 7 | Apps run with zero packs | constraint | CONSTRAINT-07 | Content-agnostic app design | FACT | high |
| 8 | Tools read-only default | constraint | CONSTRAINT-10 | Integrity and safety | FACT | high |

## 4. Workstream Summaries


### WORKSTREAM-01 — Dominium / Domino overall canon and architecture closure
- **Objective:** Preserve and continue a locked deterministic universe engine/game architecture without redesign.
- **Current state:** Design canon declared closed/locked in user-pasted bootstrap; repo execution state unverified.
- **Desired end state:** Implementation, audit, optimisation, maintenance under canon only.
- **Priority:** critical
- **Decisions:** DECISION-01, DECISION-02, DECISION-03
- **Tasks:** TASK-02, TASK-03, TASK-08
- **Constraints:** see constraint register
- **Artifacts:** see artifact ledger
- **Risks:** RISK-01, RISK-02, RISK-08
- **Open questions:** QUESTION-01, QUESTION-08
- **Next action:** Verify repo state and run/implement relevant current prompt.

### WORKSTREAM-02 — Application layer implementation
- **Objective:** Implement setup, launcher, client, server, tools as content-agnostic orchestration shells over engine/game.
- **Current state:** APP-UNIFIED-CANON generated; latest user-pasted app bootstrap says app layer only.
- **Desired end state:** Contracts, appcore, command graph, UI IR, RepoX/TestX integration, zero-pack operation.
- **Priority:** critical
- **Decisions:** DECISION-04, DECISION-05, DECISION-06, DECISION-08, DECISION-10, DECISION-17
- **Tasks:** TASK-04, TASK-10
- **Constraints:** see constraint register
- **Artifacts:** see artifact ledger
- **Risks:** RISK-03
- **Open questions:** QUESTION-06, QUESTION-07
- **Next action:** Verify repo state and run/implement relevant current prompt.

### WORKSTREAM-03 — Setup and launcher unified application canon
- **Objective:** Unify setup/launcher plans into final application-layer prompt and share with all app chats.
- **Current state:** APP-UNIFIED-CANON produced after comparing two other-chat plans.
- **Desired end state:** Use as binding app-layer implementation prompt.
- **Priority:** high
- **Decisions:** DECISION-07
- **Tasks:** see task register
- **Constraints:** see constraint register
- **Artifacts:** see artifact ledger
- **Risks:** general canon/repo-state risks
- **Open questions:** none specific
- **Next action:** Verify repo state and run/implement relevant current prompt.

### WORKSTREAM-04 — Testing, versioning, changelog, RepoX/TestX governance
- **Objective:** Create long-lived exhaustive testing/version/build/changelog enforcement.
- **Current state:** TEST0 superseded by TESTX; BUILD-ID-0 semantics pasted from other chat.
- **Desired end state:** Run TESTX or implement equivalent repository-wide self-defending test system.
- **Priority:** critical
- **Decisions:** DECISION-11, DECISION-15, DECISION-19, DECISION-21
- **Tasks:** TASK-05, TASK-11, TASK-12
- **Constraints:** see constraint register
- **Artifacts:** see artifact ledger
- **Risks:** RISK-05, RISK-07
- **Open questions:** QUESTION-03, QUESTION-04, QUESTION-05
- **Next action:** Verify repo state and run/implement relevant current prompt.

### WORKSTREAM-05 — Source code hygiene and data/code boundary
- **Objective:** Audit code for hardcoded taxonomies, magic numbers, custom/other enums, mode flags; migrate to registries/data where appropriate.
- **Current state:** CODEHYGIENE-X generated.
- **Desired end state:** Run scan -> queue -> safe migrations -> CI enforcement.
- **Priority:** high
- **Decisions:** DECISION-16, DECISION-18, DECISION-20
- **Tasks:** TASK-06
- **Constraints:** see constraint register
- **Artifacts:** see artifact ledger
- **Risks:** RISK-06
- **Open questions:** none specific
- **Next action:** Verify repo state and run/implement relevant current prompt.

### WORKSTREAM-06 — Documentation/canon population and chat handoff system
- **Objective:** Create docs/canon package and per-chat transferable reports.
- **Current state:** DOCS0 generated; prior Context Transfer Packet generated; this package finalizes old-chat report.
- **Desired end state:** Store package and use in future aggregation/spec book.
- **Priority:** critical
- **Decisions:** DECISION-14, DECISION-22
- **Tasks:** TASK-01, TASK-07, TASK-14
- **Constraints:** see constraint register
- **Artifacts:** see artifact ledger
- **Risks:** RISK-09, RISK-10
- **Open questions:** QUESTION-02
- **Next action:** Verify repo state and run/implement relevant current prompt.

### WORKSTREAM-07 — Content/data population
- **Objective:** Add universe, Sol, Earth, Milky Way, civilizations, economy, scenarios as data only.
- **Current state:** Standalone CONTENT0 generated; earlier CONTENT0–3 generated.
- **Desired end state:** Separate content chat can proceed independently later.
- **Priority:** medium
- **Decisions:** see master register
- **Tasks:** TASK-09
- **Constraints:** see constraint register
- **Artifacts:** see artifact ledger
- **Risks:** general canon/repo-state risks
- **Open questions:** none specific
- **Next action:** Verify repo state and run/implement relevant current prompt.

### WORKSTREAM-08 — Runtime/execution substrate and hardware abstraction
- **Objective:** Implement Work IR, Access IR, schedulers, ECS storage, kernels, HWCAPS.
- **Current state:** EXEC/ECSX/KERN/HWCAPS prompts generated; execution state unverified.
- **Desired end state:** Use if/when implementing engine runtime internals.
- **Priority:** medium
- **Decisions:** see master register
- **Tasks:** see task register
- **Constraints:** see constraint register
- **Artifacts:** see artifact ledger
- **Risks:** general canon/repo-state risks
- **Open questions:** none specific
- **Next action:** Verify repo state and run/implement relevant current prompt.

### WORKSTREAM-09 — Reality layer: existence, domain, travel, time, authority
- **Objective:** Formalize existence/refinement/domain volumes/travel/observer time/omnipotence.
- **Current state:** EXIST/DOMAIN/TRAVEL/TIME/OMNI prompts generated; REALITY0 macro generated.
- **Desired end state:** Referenced by docs/canon; likely not current app-layer implementation target.
- **Priority:** medium
- **Decisions:** see master register
- **Tasks:** see task register
- **Constraints:** see constraint register
- **Artifacts:** see artifact ledger
- **Risks:** general canon/repo-state risks
- **Open questions:** none specific
- **Next action:** Verify repo state and run/implement relevant current prompt.

### WORKSTREAM-10 — Life/civilization/war/agent/tool/mod systems
- **Objective:** Earlier game/simulation systems prompt families for life, civ, war, agents, tools, mods, final policies.
- **Current state:** Many prompts generated; latest bootstrap says T0–T24 completed and locked.
- **Desired end state:** Do not redesign here; treat as project context unless docs/source provided.
- **Priority:** medium
- **Decisions:** see master register
- **Tasks:** see task register
- **Constraints:** see constraint register
- **Artifacts:** see artifact ledger
- **Risks:** general canon/repo-state risks
- **Open questions:** none specific
- **Next action:** Verify repo state and run/implement relevant current prompt.

### WORKSTREAM-11 — Application UI / UI IR / accessibility/localisation
- **Objective:** Ensure all application UI is declarative, accessible, localized, and command-graph-backed.
- **Current state:** APP-UNIFIED-CANON and latest app bootstrap require UI IR and locale packs.
- **Desired end state:** Implement UI IR schemas and CLI-first parity later.
- **Priority:** high
- **Decisions:** DECISION-09
- **Tasks:** TASK-13
- **Constraints:** see constraint register
- **Artifacts:** see artifact ledger
- **Risks:** general canon/repo-state risks
- **Open questions:** QUESTION-09
- **Next action:** Verify repo state and run/implement relevant current prompt.

### WORKSTREAM-12 — Release/build identity system
- **Objective:** Apply BUILD-ID-0 model: SemVer products, build kinds, GBN/BII, channels, protocol/schema/API/ABI versions.
- **Current state:** Latest user-pasted global bootstrap defines locked version model.
- **Desired end state:** Implementation must align with BUILD-ID-0, not earlier simple build-number idea.
- **Priority:** high
- **Decisions:** DECISION-12, DECISION-13
- **Tasks:** see task register
- **Constraints:** see constraint register
- **Artifacts:** see artifact ledger
- **Risks:** RISK-04
- **Open questions:** QUESTION-10
- **Next action:** Verify repo state and run/implement relevant current prompt.


## 5. Registers for Merge

See `dominium_app_testx_codehygiene_handoff__04_registers.md` for full standalone registers. Compact key registers are included in the YAML spec sheet.

## 6. Possible Cross-Chat Duplicates

- APP-CANON0/1, APP-AUTO-0, APP-UI-BIND-0 likely appear in application chats.
- BUILD-ID-0 likely appears in release/governance chats.
- RepoX/TestX/VALIDATE-0 likely appear in tooling chats.
- Core T0–T24 architecture likely appears in design chats.
- Code hygiene/data boundary may overlap with cleanup/refactor chats.

## 7. Possible Cross-Chat Conflicts

- Earlier simple build-number model vs BUILD-ID-0.
- APP0 broad runtime prompt vs APP-UNIFIED-CANON.
- Older intent/action/effect wording vs latest Assemblies/Fields/Processes/Agents/Law ontology.
- Generated prompt deliverables vs actual repository state.

## 8. Spec Book Integration Guidance

Use this chat for chapters on:
- Application Layer Canon
- Setup/Launcher Reference Architecture
- RepoX/TestX/Build-ID Governance
- Code Hygiene and Data/Code Boundary
- Chat Handoff / Canon Preservation Process

Promote to requirements:
- CLI canonical.
- Setup only install mutation authority.
- Tools read-only by default.
- Apps run with zero content packs.
- No manual changelog editing.
- Mismatches refuse loudly.

Keep as context:
- Historical prompt families, unless executed and reflected in docs/source.

Need verification:
- Actual RepoX/TestX/VALIDATE-0 paths and commands.
- Actual state of app contracts/appcore.

## 9. Aggregator Warnings

- Do not treat assistant-generated prompts as completed implementation.
- Preserve PROJECT-CONTEXT labels for user-pasted other-chat material.
- Preserve superseded items; they explain why later decisions exist.
- Do not merge application-layer constraints into engine/game semantics.
- Do not discard BUILD-ID-0 nuance.
