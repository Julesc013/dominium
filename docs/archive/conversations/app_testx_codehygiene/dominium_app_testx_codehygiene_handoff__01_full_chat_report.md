# Full Chat Report — Dominium Application/TestX/CodeHygiene Handoff

## 0. Report Metadata

- **Chat label:** Dominium Application/TestX/CodeHygiene Handoff
- **Filesystem-safe label:** `dominium_app_testx_codehygiene_handoff`
- **Generated date anchor:** 2026-05-27 Australia/Melbourne
- **Generated at:** 2026-05-27 14:48:11 Australia/Melbourne
- **Source scope:** This report covers this visible old chat only. User-pasted text from other chats is included but labeled **PROJECT-CONTEXT** where appropriate.
- **Apparent coverage:** full for visible late-chat context; partial for earlier hidden/omitted turns.
- **Extraction confidence:** 4 / 5.
- **Staleness risk:** medium. Architecture and application canon may have evolved in other chats; latest user-pasted bootstraps are treated as current within this chat.
- **Future plans present:** yes.
- **Pending tasks present:** yes.
- **Artifacts/files/prompts present:** yes, mostly as generated prompt artifacts; actual repository files are **UNCERTAIN / UNVERIFIED**.
- **Safe for aggregation:** yes, with caveats.
- **Main limitations:** No source/docs zip was inspected; generated prompts are not proof of execution; external project context is visible only through user-pasted excerpts.

## 1. Executive Summary

This chat was part of a long-running Dominium / Domino planning and implementation-preparation effort. The project is a deterministic, simulation-first universe engine/game intended to support singleplayer, co-op, MMO-scale play, AI-only autorun worlds, player-only worlds, spectator-only worlds, competitive lockdown, in-game anarchy, meta-anarchy, and omnipotent admin/god-mode operations while preserving determinism, strong epistemics, inspectability, and no hidden shortcuts. The latest user-pasted project bootstrap states that architecture is closed and canon locked, and that all systems reduce to **Assemblies, Fields, Processes, Agents, and Law**. It also states that engine code is C89, game code is C++98, applications may use newer toolchains but must not impose them on engine/game, and future work in the relevant chats is implementation, audit, optimisation, and maintenance only.

A major outcome of this chat is the creation of a large prompt corpus and final consolidation around application-layer implementation, testing/versioning governance, source-code hygiene, and chat handoff packaging. The earlier chat designed many systems and prompt families: Phase 1 hardening; deterministic execution; ECS storage; kernel backends; sharding/distribution; reality/existence/domain/travel/time/authority; life/civilization/war/content/agents/tools/mods; documentation consolidation; hardware capability policy; source hygiene; and exhaustive testing. These are not all verified as executed in a repository. They are best understood as planned Codex prompt artifacts unless the user later confirms execution or provides source/docs.

The most current active workstream is the **Application Layer**. The user pasted a current application-layer bootstrap from another chat stating that applications are content-agnostic, rule-agnostic, authority-agnostic orchestration shells; CLI is canonical; GUI/TUI are views over the same command graph; UI is data (UI IR), never logic; tools are read-only by default; setup is the only mutation authority for installs; launcher is the reference app; and no application may contain gameplay logic, mutate world state, invent defaults, hide failures, or bypass RepoX/TestX. Two external setup/launcher plans were merged into **APP-UNIFIED-CANON**, which specifies `libs/contracts/include/dom_contracts/` as a pure POD/TLV-friendly application contract layer and `libs/appcore/` as shared app-only functionality for discovery, profiles, RepoX, validation, invocation, command parsing, and output. It also specifies command sets for setup, launcher, client, server, and tools; UI IR schemas under `schema/ui/`; setup/launcher/client/server/tools responsibilities; RepoX/build/version integration; accessibility/localisation; and strict failure behavior.

A second major active workstream is **testing, versioning, release governance, and changelog automation**. The chat generated TEST0, then replaced it with **TESTX**, which mandates exhaustive, CLI-only, portable, long-lived tests; assertion tiers; comment-density enforcement; blockers documented in docs and source; deterministic test harnesses; product versions, build kinds, GBN/BII rules, and changelog generation. The latest user-pasted BUILD-ID-0 model supersedes earlier simpler build-number concepts: product SemVer is manual; build kind is `dev | ci | beta | rc | release | hotfix`; global build number is centrally allocated only for beta/rc/release/hotfix; build instance ID is always present for dev/ci; all release products share the same GBN; channels are separate; and protocols/schemas/APIs/ABIs have orthogonal versions with loud refusal on mismatch.

A third active workstream is **source-code hygiene and data/code boundary enforcement**. The user noticed hardcoded systems, types, variables, magic numbers, and enums with “custom/other” style values and wanted them moved to data where appropriate. The resulting **CODEHYGIENE-X** prompt defines permanent categories: architectural enums remain closed-world code; taxonomies of reality must be data-driven and registry-backed; tunable parameters are data-driven and validated; derived conveniences are generated deterministically. It also mandates scanners for custom/other enums, magic numbers, switch-on-taxonomy patterns, raw TODOs, comment density, and admin/cheat flags; a `HYGIENE_QUEUE.md`; registry patterns using stable `uint32_t` IDs; and safe migration batches compatible with TestX and RepoX.

This chat also produced this final report package request and response. The highest-priority carry-forward facts are: do not redesign canon; distinguish generated prompts from executed repo state; use the latest bootstraps and APP-UNIFIED-CANON for application work; use TESTX for testing/versioning/changelog unless superseded; use CODEHYGIENE-X for source hygiene; verify RepoX/TestX/VALIDATE-0/BUILD-ID-0 actual paths before implementation; and always label project context and uncertainty.

## 2. How to Use This Report

This report covers only this retired chat. It is not a complete Project Spec Book. It is intended to be combined later with other chat-specific reports.

Important handling rules:

- Direct user statements outrank assistant suggestions.
- User-pasted text from other chats is included as **PROJECT-CONTEXT** because it was visible here but originated elsewhere.
- Generated prompts are artifacts, not evidence of repository execution.
- Items labeled **UNCERTAIN / UNVERIFIED** must not be treated as facts.
- External-world facts, software versions, laws, APIs, or current institutional rules require fresh verification before future use.
- Tentative or superseded plans are preserved so future assistants do not repeat rejected work.
- This report is suitable for later master-spec aggregation with caveats.

## 3. User Preferences Visible in This Chat

### 3.1 Explicit Preferences

| ID | Preference | Basis | Strength | Implication | Risk if Misunderstood | Label |
| --- | --- | --- | --- | --- | --- | --- |
| PREF-01 | Wants maximum-fidelity transfer reports, not normal summaries. | explicit | high | Future assistants should preserve detail and labels. | Future assistant may produce too little detail or wrong style. | FACT |
| PREF-02 | Prefers modular, extensible, robust, future-proof designs. | explicit | high | Outputs should emphasize modularity and long-term maintainability. | Future assistant may produce too little detail or wrong style. | FACT |
| PREF-03 | Wants CLI-only tests/apps unless GUI/TUI specifically required. | explicit | high | Avoid UI testing friction. | Future assistant may produce too little detail or wrong style. | FACT |
| PREF-04 | Wants data-driven taxonomies and minimal hardcoded assumptions. | explicit | high | Use registries/data for open-world concepts. | Future assistant may produce too little detail or wrong style. | FACT |
| PREF-05 | Wants strict documentation/comment density and cross-referenced blockers. | explicit | medium-high | Implement comment/doc policies. | Future assistant may produce too little detail or wrong style. | FACT |
| PREF-07 | Values auditability, verifiability, and stable IDs. | explicit | high | Use registers/tables/IDs. | Future assistant may produce too little detail or wrong style. | FACT |

### 3.2 Inferred Preferences

| ID | Preference | Basis | Strength | Implication | Risk if Misunderstood | Label |
| --- | --- | --- | --- | --- | --- | --- |
| PREF-06 | Likes contiguous TXT blocks for Codex prompts. | Multiple asks for one big txt block | high | Provide copy-paste prompts in code fences. | Prompt outputs may be too fragmented or insufficiently Codex-ready. | INFERENCE |

### 3.3 Preferences Not Established by This Chat

- **UNCERTAIN / UNVERIFIED:** Preferred concrete CMake target names beyond those proposed in prompts.
- **UNCERTAIN / UNVERIFIED:** Exact final RepoX/TestX command names.
- **UNCERTAIN / UNVERIFIED:** Whether the user wants GUI/TUI application implementation now or CLI-only first beyond the stated CLI-canonical rule.
- **UNCERTAIN / UNVERIFIED:** Whether generated prompts have been executed.

## 4. Complete Topic and Workstream Inventory

| ID | Name | Objective | Current State | Desired End State | Status | Priority | Confidence | Label |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| WORKSTREAM-01 | Dominium / Domino overall canon and architecture closure | Preserve and continue a locked deterministic universe engine/game architecture without redesign. | Design canon declared closed/locked in user-pasted bootstrap; repo execution state unverified. | Implementation, audit, optimisation, maintenance under canon only. | active | critical | high | FACT / PROJECT-CONTEXT |
| WORKSTREAM-02 | Application layer implementation | Implement setup, launcher, client, server, tools as content-agnostic orchestration shells over engine/game. | APP-UNIFIED-CANON generated; latest user-pasted app bootstrap says app layer only. | Contracts, appcore, command graph, UI IR, RepoX/TestX integration, zero-pack operation. | active | critical | high | FACT / PROJECT-CONTEXT |
| WORKSTREAM-03 | Setup and launcher unified application canon | Unify setup/launcher plans into final application-layer prompt and share with all app chats. | APP-UNIFIED-CANON produced after comparing two other-chat plans. | Use as binding app-layer implementation prompt. | active | high | high | FACT |
| WORKSTREAM-04 | Testing, versioning, changelog, RepoX/TestX governance | Create long-lived exhaustive testing/version/build/changelog enforcement. | TEST0 superseded by TESTX; BUILD-ID-0 semantics pasted from other chat. | Run TESTX or implement equivalent repository-wide self-defending test system. | active | critical | high | FACT |
| WORKSTREAM-05 | Source code hygiene and data/code boundary | Audit code for hardcoded taxonomies, magic numbers, custom/other enums, mode flags; migrate to registries/data where appropriate. | CODEHYGIENE-X generated. | Run scan -> queue -> safe migrations -> CI enforcement. | active | high | high | FACT |
| WORKSTREAM-06 | Documentation/canon population and chat handoff system | Create docs/canon package and per-chat transferable reports. | DOCS0 generated; prior Context Transfer Packet generated; this package finalizes old-chat report. | Store package and use in future aggregation/spec book. | active | critical | high | FACT |
| WORKSTREAM-07 | Content/data population | Add universe, Sol, Earth, Milky Way, civilizations, economy, scenarios as data only. | Standalone CONTENT0 generated; earlier CONTENT0–3 generated. | Separate content chat can proceed independently later. | planned | medium | medium | FACT |
| WORKSTREAM-08 | Runtime/execution substrate and hardware abstraction | Implement Work IR, Access IR, schedulers, ECS storage, kernels, HWCAPS. | EXEC/ECSX/KERN/HWCAPS prompts generated; execution state unverified. | Use if/when implementing engine runtime internals. | planned / historical | medium | medium | FACT |
| WORKSTREAM-09 | Reality layer: existence, domain, travel, time, authority | Formalize existence/refinement/domain volumes/travel/observer time/omnipotence. | EXIST/DOMAIN/TRAVEL/TIME/OMNI prompts generated; REALITY0 macro generated. | Referenced by docs/canon; likely not current app-layer implementation target. | historical / planned | medium | medium | FACT |
| WORKSTREAM-10 | Life/civilization/war/agent/tool/mod systems | Earlier game/simulation systems prompt families for life, civ, war, agents, tools, mods, final policies. | Many prompts generated; latest bootstrap says T0–T24 completed and locked. | Do not redesign here; treat as project context unless docs/source provided. | historical / project-context | medium | medium | FACT |
| WORKSTREAM-11 | Application UI / UI IR / accessibility/localisation | Ensure all application UI is declarative, accessible, localized, and command-graph-backed. | APP-UNIFIED-CANON and latest app bootstrap require UI IR and locale packs. | Implement UI IR schemas and CLI-first parity later. | active | high | high | FACT / PROJECT-CONTEXT |
| WORKSTREAM-12 | Release/build identity system | Apply BUILD-ID-0 model: SemVer products, build kinds, GBN/BII, channels, protocol/schema/API/ABI versions. | Latest user-pasted global bootstrap defines locked version model. | Implementation must align with BUILD-ID-0, not earlier simple build-number idea. | active | high | high | FACT / PROJECT-CONTEXT |

## 5. Detailed Workstream State


### WORKSTREAM-01 — Dominium / Domino overall canon and architecture closure

- **Label:** FACT / PROJECT-CONTEXT
- **Objective:** Preserve and continue a locked deterministic universe engine/game architecture without redesign.
- **Background:** Developed through this chat’s planning, prompt generation, and/or user-pasted project context.
- **Current state:** Design canon declared closed/locked in user-pasted bootstrap; repo execution state unverified.
- **Desired end state:** Implementation, audit, optimisation, maintenance under canon only.
- **Importance:** critical
- **Decisions made:** See Decision Register entries related to WORKSTREAM-01.
- **Decisions pending:** See Open Questions Register.
- **Pending tasks:** See Task Register entries related to WORKSTREAM-01.
- **Constraints:** See Constraint Register.
- **Dependencies:** Repo files, docs, TestX/RepoX/VALIDATE-0/SRZ-0 as applicable.
- **Timeline / sequencing:** Determined by current workstream priority; application layer and verification are current likely focus.
- **Blockers:** Actual repository state is unverified unless user provides source/docs.
- **Risks:** Treating planned prompts as executed files; terminology drift; implementation crossing boundaries.
- **Artifacts:** See Artifact Ledger.
- **Success criteria:** Workstream-specific criteria in relevant generated prompt(s).
- **Recommended next action:** Verify repo state, then run or implement the relevant current prompt.
- **Verification needed:** Inspect actual files/commits before implementation claims.
- **Confidence:** high
- **Carry-forward priority:** critical

### WORKSTREAM-02 — Application layer implementation

- **Label:** FACT / PROJECT-CONTEXT
- **Objective:** Implement setup, launcher, client, server, tools as content-agnostic orchestration shells over engine/game.
- **Background:** Developed through this chat’s planning, prompt generation, and/or user-pasted project context.
- **Current state:** APP-UNIFIED-CANON generated; latest user-pasted app bootstrap says app layer only.
- **Desired end state:** Contracts, appcore, command graph, UI IR, RepoX/TestX integration, zero-pack operation.
- **Importance:** critical
- **Decisions made:** See Decision Register entries related to WORKSTREAM-02.
- **Decisions pending:** See Open Questions Register.
- **Pending tasks:** See Task Register entries related to WORKSTREAM-02.
- **Constraints:** See Constraint Register.
- **Dependencies:** Repo files, docs, TestX/RepoX/VALIDATE-0/SRZ-0 as applicable.
- **Timeline / sequencing:** Determined by current workstream priority; application layer and verification are current likely focus.
- **Blockers:** Actual repository state is unverified unless user provides source/docs.
- **Risks:** Treating planned prompts as executed files; terminology drift; implementation crossing boundaries.
- **Artifacts:** See Artifact Ledger.
- **Success criteria:** Workstream-specific criteria in relevant generated prompt(s).
- **Recommended next action:** Verify repo state, then run or implement the relevant current prompt.
- **Verification needed:** Inspect actual files/commits before implementation claims.
- **Confidence:** high
- **Carry-forward priority:** critical

### WORKSTREAM-03 — Setup and launcher unified application canon

- **Label:** FACT
- **Objective:** Unify setup/launcher plans into final application-layer prompt and share with all app chats.
- **Background:** Developed through this chat’s planning, prompt generation, and/or user-pasted project context.
- **Current state:** APP-UNIFIED-CANON produced after comparing two other-chat plans.
- **Desired end state:** Use as binding app-layer implementation prompt.
- **Importance:** high
- **Decisions made:** See Decision Register entries related to WORKSTREAM-03.
- **Decisions pending:** See Open Questions Register.
- **Pending tasks:** See Task Register entries related to WORKSTREAM-03.
- **Constraints:** See Constraint Register.
- **Dependencies:** Repo files, docs, TestX/RepoX/VALIDATE-0/SRZ-0 as applicable.
- **Timeline / sequencing:** Determined by current workstream priority; application layer and verification are current likely focus.
- **Blockers:** Actual repository state is unverified unless user provides source/docs.
- **Risks:** Treating planned prompts as executed files; terminology drift; implementation crossing boundaries.
- **Artifacts:** See Artifact Ledger.
- **Success criteria:** Workstream-specific criteria in relevant generated prompt(s).
- **Recommended next action:** Verify repo state, then run or implement the relevant current prompt.
- **Verification needed:** Inspect actual files/commits before implementation claims.
- **Confidence:** high
- **Carry-forward priority:** high

### WORKSTREAM-04 — Testing, versioning, changelog, RepoX/TestX governance

- **Label:** FACT
- **Objective:** Create long-lived exhaustive testing/version/build/changelog enforcement.
- **Background:** Developed through this chat’s planning, prompt generation, and/or user-pasted project context.
- **Current state:** TEST0 superseded by TESTX; BUILD-ID-0 semantics pasted from other chat.
- **Desired end state:** Run TESTX or implement equivalent repository-wide self-defending test system.
- **Importance:** critical
- **Decisions made:** See Decision Register entries related to WORKSTREAM-04.
- **Decisions pending:** See Open Questions Register.
- **Pending tasks:** See Task Register entries related to WORKSTREAM-04.
- **Constraints:** See Constraint Register.
- **Dependencies:** Repo files, docs, TestX/RepoX/VALIDATE-0/SRZ-0 as applicable.
- **Timeline / sequencing:** Determined by current workstream priority; application layer and verification are current likely focus.
- **Blockers:** Actual repository state is unverified unless user provides source/docs.
- **Risks:** Treating planned prompts as executed files; terminology drift; implementation crossing boundaries.
- **Artifacts:** See Artifact Ledger.
- **Success criteria:** Workstream-specific criteria in relevant generated prompt(s).
- **Recommended next action:** Verify repo state, then run or implement the relevant current prompt.
- **Verification needed:** Inspect actual files/commits before implementation claims.
- **Confidence:** high
- **Carry-forward priority:** critical

### WORKSTREAM-05 — Source code hygiene and data/code boundary

- **Label:** FACT
- **Objective:** Audit code for hardcoded taxonomies, magic numbers, custom/other enums, mode flags; migrate to registries/data where appropriate.
- **Background:** Developed through this chat’s planning, prompt generation, and/or user-pasted project context.
- **Current state:** CODEHYGIENE-X generated.
- **Desired end state:** Run scan -> queue -> safe migrations -> CI enforcement.
- **Importance:** high
- **Decisions made:** See Decision Register entries related to WORKSTREAM-05.
- **Decisions pending:** See Open Questions Register.
- **Pending tasks:** See Task Register entries related to WORKSTREAM-05.
- **Constraints:** See Constraint Register.
- **Dependencies:** Repo files, docs, TestX/RepoX/VALIDATE-0/SRZ-0 as applicable.
- **Timeline / sequencing:** Determined by current workstream priority; application layer and verification are current likely focus.
- **Blockers:** Actual repository state is unverified unless user provides source/docs.
- **Risks:** Treating planned prompts as executed files; terminology drift; implementation crossing boundaries.
- **Artifacts:** See Artifact Ledger.
- **Success criteria:** Workstream-specific criteria in relevant generated prompt(s).
- **Recommended next action:** Verify repo state, then run or implement the relevant current prompt.
- **Verification needed:** Inspect actual files/commits before implementation claims.
- **Confidence:** high
- **Carry-forward priority:** high

### WORKSTREAM-06 — Documentation/canon population and chat handoff system

- **Label:** FACT
- **Objective:** Create docs/canon package and per-chat transferable reports.
- **Background:** Developed through this chat’s planning, prompt generation, and/or user-pasted project context.
- **Current state:** DOCS0 generated; prior Context Transfer Packet generated; this package finalizes old-chat report.
- **Desired end state:** Store package and use in future aggregation/spec book.
- **Importance:** critical
- **Decisions made:** See Decision Register entries related to WORKSTREAM-06.
- **Decisions pending:** See Open Questions Register.
- **Pending tasks:** See Task Register entries related to WORKSTREAM-06.
- **Constraints:** See Constraint Register.
- **Dependencies:** Repo files, docs, TestX/RepoX/VALIDATE-0/SRZ-0 as applicable.
- **Timeline / sequencing:** Determined by current workstream priority; application layer and verification are current likely focus.
- **Blockers:** Actual repository state is unverified unless user provides source/docs.
- **Risks:** Treating planned prompts as executed files; terminology drift; implementation crossing boundaries.
- **Artifacts:** See Artifact Ledger.
- **Success criteria:** Workstream-specific criteria in relevant generated prompt(s).
- **Recommended next action:** Verify repo state, then run or implement the relevant current prompt.
- **Verification needed:** Inspect actual files/commits before implementation claims.
- **Confidence:** high
- **Carry-forward priority:** critical

### WORKSTREAM-07 — Content/data population

- **Label:** FACT
- **Objective:** Add universe, Sol, Earth, Milky Way, civilizations, economy, scenarios as data only.
- **Background:** Developed through this chat’s planning, prompt generation, and/or user-pasted project context.
- **Current state:** Standalone CONTENT0 generated; earlier CONTENT0–3 generated.
- **Desired end state:** Separate content chat can proceed independently later.
- **Importance:** medium
- **Decisions made:** See Decision Register entries related to WORKSTREAM-07.
- **Decisions pending:** See Open Questions Register.
- **Pending tasks:** See Task Register entries related to WORKSTREAM-07.
- **Constraints:** See Constraint Register.
- **Dependencies:** Repo files, docs, TestX/RepoX/VALIDATE-0/SRZ-0 as applicable.
- **Timeline / sequencing:** Determined by current workstream priority; application layer and verification are current likely focus.
- **Blockers:** Actual repository state is unverified unless user provides source/docs.
- **Risks:** Treating planned prompts as executed files; terminology drift; implementation crossing boundaries.
- **Artifacts:** See Artifact Ledger.
- **Success criteria:** Workstream-specific criteria in relevant generated prompt(s).
- **Recommended next action:** Verify repo state, then run or implement the relevant current prompt.
- **Verification needed:** Inspect actual files/commits before implementation claims.
- **Confidence:** medium
- **Carry-forward priority:** medium

### WORKSTREAM-08 — Runtime/execution substrate and hardware abstraction

- **Label:** FACT
- **Objective:** Implement Work IR, Access IR, schedulers, ECS storage, kernels, HWCAPS.
- **Background:** Developed through this chat’s planning, prompt generation, and/or user-pasted project context.
- **Current state:** EXEC/ECSX/KERN/HWCAPS prompts generated; execution state unverified.
- **Desired end state:** Use if/when implementing engine runtime internals.
- **Importance:** medium
- **Decisions made:** See Decision Register entries related to WORKSTREAM-08.
- **Decisions pending:** See Open Questions Register.
- **Pending tasks:** See Task Register entries related to WORKSTREAM-08.
- **Constraints:** See Constraint Register.
- **Dependencies:** Repo files, docs, TestX/RepoX/VALIDATE-0/SRZ-0 as applicable.
- **Timeline / sequencing:** Determined by current workstream priority; application layer and verification are current likely focus.
- **Blockers:** Actual repository state is unverified unless user provides source/docs.
- **Risks:** Treating planned prompts as executed files; terminology drift; implementation crossing boundaries.
- **Artifacts:** See Artifact Ledger.
- **Success criteria:** Workstream-specific criteria in relevant generated prompt(s).
- **Recommended next action:** Verify repo state, then run or implement the relevant current prompt.
- **Verification needed:** Inspect actual files/commits before implementation claims.
- **Confidence:** medium
- **Carry-forward priority:** medium

### WORKSTREAM-09 — Reality layer: existence, domain, travel, time, authority

- **Label:** FACT
- **Objective:** Formalize existence/refinement/domain volumes/travel/observer time/omnipotence.
- **Background:** Developed through this chat’s planning, prompt generation, and/or user-pasted project context.
- **Current state:** EXIST/DOMAIN/TRAVEL/TIME/OMNI prompts generated; REALITY0 macro generated.
- **Desired end state:** Referenced by docs/canon; likely not current app-layer implementation target.
- **Importance:** medium
- **Decisions made:** See Decision Register entries related to WORKSTREAM-09.
- **Decisions pending:** See Open Questions Register.
- **Pending tasks:** See Task Register entries related to WORKSTREAM-09.
- **Constraints:** See Constraint Register.
- **Dependencies:** Repo files, docs, TestX/RepoX/VALIDATE-0/SRZ-0 as applicable.
- **Timeline / sequencing:** Determined by current workstream priority; application layer and verification are current likely focus.
- **Blockers:** Actual repository state is unverified unless user provides source/docs.
- **Risks:** Treating planned prompts as executed files; terminology drift; implementation crossing boundaries.
- **Artifacts:** See Artifact Ledger.
- **Success criteria:** Workstream-specific criteria in relevant generated prompt(s).
- **Recommended next action:** Verify repo state, then run or implement the relevant current prompt.
- **Verification needed:** Inspect actual files/commits before implementation claims.
- **Confidence:** medium
- **Carry-forward priority:** medium

### WORKSTREAM-10 — Life/civilization/war/agent/tool/mod systems

- **Label:** FACT
- **Objective:** Earlier game/simulation systems prompt families for life, civ, war, agents, tools, mods, final policies.
- **Background:** Developed through this chat’s planning, prompt generation, and/or user-pasted project context.
- **Current state:** Many prompts generated; latest bootstrap says T0–T24 completed and locked.
- **Desired end state:** Do not redesign here; treat as project context unless docs/source provided.
- **Importance:** medium
- **Decisions made:** See Decision Register entries related to WORKSTREAM-10.
- **Decisions pending:** See Open Questions Register.
- **Pending tasks:** See Task Register entries related to WORKSTREAM-10.
- **Constraints:** See Constraint Register.
- **Dependencies:** Repo files, docs, TestX/RepoX/VALIDATE-0/SRZ-0 as applicable.
- **Timeline / sequencing:** Determined by current workstream priority; application layer and verification are current likely focus.
- **Blockers:** Actual repository state is unverified unless user provides source/docs.
- **Risks:** Treating planned prompts as executed files; terminology drift; implementation crossing boundaries.
- **Artifacts:** See Artifact Ledger.
- **Success criteria:** Workstream-specific criteria in relevant generated prompt(s).
- **Recommended next action:** Verify repo state, then run or implement the relevant current prompt.
- **Verification needed:** Inspect actual files/commits before implementation claims.
- **Confidence:** medium
- **Carry-forward priority:** medium

### WORKSTREAM-11 — Application UI / UI IR / accessibility/localisation

- **Label:** FACT / PROJECT-CONTEXT
- **Objective:** Ensure all application UI is declarative, accessible, localized, and command-graph-backed.
- **Background:** Developed through this chat’s planning, prompt generation, and/or user-pasted project context.
- **Current state:** APP-UNIFIED-CANON and latest app bootstrap require UI IR and locale packs.
- **Desired end state:** Implement UI IR schemas and CLI-first parity later.
- **Importance:** high
- **Decisions made:** See Decision Register entries related to WORKSTREAM-11.
- **Decisions pending:** See Open Questions Register.
- **Pending tasks:** See Task Register entries related to WORKSTREAM-11.
- **Constraints:** See Constraint Register.
- **Dependencies:** Repo files, docs, TestX/RepoX/VALIDATE-0/SRZ-0 as applicable.
- **Timeline / sequencing:** Determined by current workstream priority; application layer and verification are current likely focus.
- **Blockers:** Actual repository state is unverified unless user provides source/docs.
- **Risks:** Treating planned prompts as executed files; terminology drift; implementation crossing boundaries.
- **Artifacts:** See Artifact Ledger.
- **Success criteria:** Workstream-specific criteria in relevant generated prompt(s).
- **Recommended next action:** Verify repo state, then run or implement the relevant current prompt.
- **Verification needed:** Inspect actual files/commits before implementation claims.
- **Confidence:** high
- **Carry-forward priority:** high

### WORKSTREAM-12 — Release/build identity system

- **Label:** FACT / PROJECT-CONTEXT
- **Objective:** Apply BUILD-ID-0 model: SemVer products, build kinds, GBN/BII, channels, protocol/schema/API/ABI versions.
- **Background:** Developed through this chat’s planning, prompt generation, and/or user-pasted project context.
- **Current state:** Latest user-pasted global bootstrap defines locked version model.
- **Desired end state:** Implementation must align with BUILD-ID-0, not earlier simple build-number idea.
- **Importance:** high
- **Decisions made:** See Decision Register entries related to WORKSTREAM-12.
- **Decisions pending:** See Open Questions Register.
- **Pending tasks:** See Task Register entries related to WORKSTREAM-12.
- **Constraints:** See Constraint Register.
- **Dependencies:** Repo files, docs, TestX/RepoX/VALIDATE-0/SRZ-0 as applicable.
- **Timeline / sequencing:** Determined by current workstream priority; application layer and verification are current likely focus.
- **Blockers:** Actual repository state is unverified unless user provides source/docs.
- **Risks:** Treating planned prompts as executed files; terminology drift; implementation crossing boundaries.
- **Artifacts:** See Artifact Ledger.
- **Success criteria:** Workstream-specific criteria in relevant generated prompt(s).
- **Recommended next action:** Verify repo state, then run or implement the relevant current prompt.
- **Verification needed:** Inspect actual files/commits before implementation claims.
- **Confidence:** high
- **Carry-forward priority:** high

## 6. Chronological Timeline

| Sequence | Event / Topic | What Changed or Was Decided | Why It Mattered | Current Relevance | Confidence |
| --- | --- | --- | --- | --- | --- |
| T-01 | Initial prompt-plan/documentation work | Generated early cd prompts and project plans. | Set long-running Codex prompt-generation style. | historical | medium |
| T-02 | Sol System canonical inclusion | User pasted detailed Sol system inclusion rules. | Anchored real-world content ambition. | historical/content | high |
| T-03 | Physics/time/fog-of-war expansion | User asked for relativistic/quantum/fog-of-war/command gameplay. | Expanded simulation ambition and epistemics. | historical | high |
| T-04 | Massive scale and no fake systems | User required millions/trillions scale, deterministic aggregates, no products/services from nowhere. | Created macro/micro, provenance, event-driven constraints. | core canon | high |
| T-05 | Time/calendar epistemic canon | User pasted detailed temporal/calendar handoff. | Locked time as ACT/cals renderers/diegetic knowledge. | historical/project-context | high |
| T-06 | Canonical repo refactor | User pasted engine/game/client/server/launcher/setup/tools/libs/schema layout. | Shifted plans to strict repo boundaries. | historical | high |
| T-07 | Phase 1 hardening prompts | Generated ENF/DET/PERF/SCALE/DATA/REND/EPIS/PH1 audit. | Established enforcement and CI guardrail plans. | historical | high |
| T-08 | Life/Civ/War/Content/Agent/Tool prompt sequences | Generated many system prompts through FINAL0. | Created broad project prompt corpus. | historical | high |
| T-09 | Execution substrate refactor | Generated ARCH0, EXEC/ECSX/KERN/ADOPT/DIST prompts. | Added backend-swappable execution and performance future-proofing. | historical | high |
| T-10 | Domain/existence/travel/time/omni layer | Generated EXIST/DOMAIN/TRAVEL/TIME/OMNI prompts. | Added reality/authority/refinement model. | historical | high |
| T-11 | Macro docs consolidation | Generated DOCS0, CANON0, REALITY0, LIFE0+, CIV0+, FUTURE0. | Reduced prompt count and created docs-canon path. | historical | high |
| T-12 | Testing/version/changelog governance | Generated TEST0 then TESTX; discussed build/version/changelog/git rules. | Established self-defending test/version plan. | active | high |
| T-13 | Code hygiene/data boundary | Generated CODEHYGIENE-X. | Established data/code boundary audit/migration/CI. | active | high |
| T-14 | Application-layer bootstraps and setup/launcher plans | User pasted latest app context and two app plans. | Shifted focus to app layer implementation. | current | high |
| T-15 | APP-UNIFIED-CANON | Assistant unified app plans into final app prompt. | Latest application-layer artifact. | current | high |
| T-16 | Context Transfer Packet | Assistant generated prior maximum-fidelity packet. | Base handoff for final package. | current | high |
| T-17 | Final report package request | User requested downloadable/shareable reusable report package. | Current task. | current | high |

## 7. Decisions

| ID | Decision | Status | Evidence / Basis | Rationale | Implications / Related Workstream | Confidence | Label |
| --- | --- | --- | --- | --- | --- | --- | --- |
| DECISION-01 | Architecture is closed; canon is locked. | accepted / current | User-pasted bootstrap: 'Architecture is CLOSED. Canon is LOCKED.' | Prevents re-architecture in new chats; implementation/audit only. | WORKSTREAM-01 | high | FACT / PROJECT-CONTEXT |
| DECISION-02 | Core ontology is Assemblies, Fields, Processes, Agents, Law. | accepted / current | User-pasted bootstrap explicitly lists this ontology. | All proposals must reduce to these primitives or be invalid. | WORKSTREAM-01 | high | FACT / PROJECT-CONTEXT |
| DECISION-03 | Engine uses C89; game uses C++98; apps may use newer toolchains without imposing them on engine/game. | accepted / current | User-pasted bootstrap language/tooling section. | Public headers remain stable; apps separate from engine/game ABI. | WORKSTREAM-01 | high | FACT / PROJECT-CONTEXT |
| DECISION-04 | Applications are orchestration shells, not gameplay systems. | accepted / current | Latest app bootstrap and APP-UNIFIED-CANON. | Apps cannot contain simulation logic or mutate authoritative state. | WORKSTREAM-02 | high | FACT |
| DECISION-05 | CLI is canonical; TUI/GUI are views over the same command graph. | accepted / current | Latest app bootstrap and merged setup/launcher plans. | One command graph avoids UI divergence and enables automation. | WORKSTREAM-02 | high | FACT |
| DECISION-06 | Setup is the only install mutation authority. | accepted / current | APP-UNIFIED-CANON and other-chat app plan. | Launcher invokes setup for install/repair; client/server/tools do not install/repair. | WORKSTREAM-02 | high | FACT |
| DECISION-07 | Launcher is the reference application. | accepted / current | Other-chat plan and APP-UNIFIED-CANON. | Other apps should follow launcher module/command/failure patterns. | WORKSTREAM-03 | high | FACT |
| DECISION-08 | Tools are read-only by default. | accepted / current | Latest app bootstrap and APP-UNIFIED-CANON. | Mutation tools require explicit write flags/capabilities and audits. | WORKSTREAM-02 | high | FACT |
| DECISION-09 | UI is data (UI IR), never business logic. | accepted / current | Latest app bootstrap and APP-UNIFIED-CANON. | Declarative UI, externalized strings, CLI/TUI/GUI parity. | WORKSTREAM-11 | high | FACT |
| DECISION-10 | Applications must run with zero content packs installed. | accepted / current | Latest app bootstrap. | Apps show raw keys/diagnostics; no invented defaults. | WORKSTREAM-02 | high | FACT |
| DECISION-11 | RepoX is source of truth for build number, commits, changelogs, canon-clean tags, compatibility data. | accepted / current | Latest app bootstrap. | Apps display RepoX, no manual changelogs. | WORKSTREAM-04 | high | FACT / PROJECT-CONTEXT |
| DECISION-12 | Versioning uses product SemVer + build kind + GBN/BII; protocols/schema/API/ABI orthogonal. | accepted / current | Latest global bootstrap BUILD-ID-0 section. | Supersedes earlier simpler build-number idea. | WORKSTREAM-12 | high | FACT / PROJECT-CONTEXT |
| DECISION-13 | No distributed artifact without GBN; local/branch/fork builds cannot allocate GBN. | accepted / current | Latest global bootstrap. | Release builds centralized and reproducible. | WORKSTREAM-12 | high | FACT / PROJECT-CONTEXT |
| DECISION-14 | Generated prompts are not evidence of executed repo changes. | accepted in packet | Prior Context Transfer Packet explicitly marked repo execution state unknown. | Future assistant must inspect repo before claiming file state. | WORKSTREAM-06 | high | FACT |
| DECISION-15 | TESTX supersedes TEST0. | accepted / current | User asked to replace TEST0 with TESTX; assistant generated TESTX. | Use TESTX for verification/versioning/changelog plan unless user provides newer. | WORKSTREAM-04 | high | FACT |
| DECISION-16 | CODEHYGIENE-X is current code hygiene/data-boundary mega-prompt. | accepted / current | User asked to proceed; assistant generated CODEHYGIENE-X. | Use it for scan/queue/migrate/enforce hygiene program. | WORKSTREAM-05 | high | FACT |
| DECISION-17 | APP-UNIFIED-CANON supersedes prior app-layer plans. | accepted in latest exchange | Assistant explicitly replaced previous application-layer planning prompts; user asked to integrate other-chat setup/launcher plans. | Use APP-UNIFIED-CANON for app chats. | WORKSTREAM-02 | high | FACT |
| DECISION-18 | Hardcoded taxonomies should become data/registries where possible; structural invariants remain code. | accepted / current | User requested avoiding hardcoded systems; assistant plan generated CODEHYGIENE-X. | Prevents over-data-driving execution semantics while enabling modding. | WORKSTREAM-05 | medium-high | FACT |
| DECISION-19 | No GUI/TUI tests unless specifically needed; Windows tests CLI-only. | accepted / current | User explicitly requested CLI-only for simple testing. | Test harness avoids UI build/run fragility. | WORKSTREAM-04 | high | FACT |
| DECISION-20 | Comment density target ~30% with useful documentation, not noise. | accepted / current | User explicitly requested ~30% source docs/comments. | CODEHYGIENE-X/TESTX include comment-density checks. | WORKSTREAM-05 | medium-high | FACT |
| DECISION-21 | Manual changelog editing is disallowed; changelogs generated from commits. | accepted / current | Latest app bootstrap says no manual changelog editing. | Commit taxonomy and RepoX generation required. | WORKSTREAM-04 | high | FACT / PROJECT-CONTEXT |
| DECISION-22 | Source scope for this package is this chat only; project context must be labeled. | accepted for current task | User explicitly requested source scope rules. | Report uses FACT / PROJECT-CONTEXT labels. | WORKSTREAM-06 | high | FACT |

### Highest-impact decisions

The highest-impact decisions are DECISION-01 through DECISION-04: architecture is closed, the ontology is Assemblies/Fields/Processes/Agents/Law, engine/game language constraints are fixed, and applications are orchestration shells only. DECISION-12 through DECISION-13 are critical for build/release correctness because they supersede earlier simpler build-number thinking with BUILD-ID-0’s GBN/BII/build-kind model. DECISION-17 is the current application-layer anchor: APP-UNIFIED-CANON supersedes earlier app plans.

## 8. Pending Tasks and Next Actions

| ID | Task | Priority | Urgency | Owner | Dependencies | Inputs Needed | Expected Output | Recommended Next Step | Related Workstream | Label |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| TASK-01 | Use this final report package as source material for a new chat. | critical | immediate | User / future assistant |  | Download/save package | New chat bootstrapped without re-explanation. | Paste bootstrap + attach package or key files. | WORKSTREAM-06 | FACT |
| TASK-02 | Verify actual repo state before implementation claims. | critical | immediate | Future assistant / Codex | Repo access | Source/docs zip or repo | Known actual files/commits/prompts executed. | Inspect repo; do not infer from generated prompts. | WORKSTREAM-01 | FACT |
| TASK-03 | Choose next active workstream. | high | immediate | User | This packet | User choice | Focused next chat. | Likely options: application implementation, TESTX, CODEHYGIENE-X, docs, content. | WORKSTREAM-01 | FACT |
| TASK-04 | If app implementation continues, implement libs/contracts and appcore skeleton. | high | near-term | Codex | APP-UNIFIED-CANON, Repo | Repo source | `libs/contracts` POD/TLV headers and `libs/appcore` modules scaffolded. | Generate concrete implementation prompt. | WORKSTREAM-02 | INFERENCE |
| TASK-05 | Run or adapt TESTX. | high | near-term | Codex | Repo, TestX prompt | Build/test environment | Self-defending test/version/changelog system. | Execute TESTX or adjust to BUILD-ID-0 docs first. | WORKSTREAM-04 | FACT |
| TASK-06 | Run or adapt CODEHYGIENE-X. | high | after baseline tests | Codex | Repo, CODEHYGIENE-X | Source tree | HYGIENE_QUEUE, CI scanners, first safe migrations. | Run after/alongside TESTX baseline. | WORKSTREAM-05 | FACT |
| TASK-07 | Run DOCS0/CANON0 or verify docs status. | medium-high | near-term | Codex | Repo docs | Docs tree | Canon docs populated and status-labeled. | Inspect docs; run DOCS0 if incomplete. | WORKSTREAM-06 | FACT |
| TASK-08 | Resolve latest ontology vs older intent/action/effect wording in docs. | high | before canon docs finalization | Future assistant/Codex | CANON_INDEX or docs | Docs/context | Terminology consistent. | Treat Assemblies/Fields/Processes/Agents/Law as root ontology unless docs say otherwise. | WORKSTREAM-01 | INFERENCE |
| TASK-09 | Start separate content chat later using standalone CONTENT0. | medium | later | User / assistant | CONTENT0 prompt | Content scope | Content/data population plan or prompt execution. | Use content chat, not app/source chat. | WORKSTREAM-07 | FACT |
| TASK-10 | Create application failure-mode docs when implementing launcher/setup. | high | near-term app impl | Codex | APP-UNIFIED-CANON | App source/docs | `launcher/docs/FAILURE_MODES.md` or equivalent. | Include detection, key, exit code, no auto-repair. | WORKSTREAM-02 | FACT |
| TASK-11 | Confirm exact RepoX metadata file paths/formats. | high | before app implementation | User/Codex | Repo | RepoX docs/source | Appcore repox reader has real contract. | Inspect repo or ask user. | WORKSTREAM-04 | UNCERTAIN / UNVERIFIED |
| TASK-12 | Confirm exact TestX/VALIDATE-0 invocation commands. | high | before app validation integration | Codex | Repo | Docs/source | App validate module invokes correct tools. | Inspect docs/source. | WORKSTREAM-04 | UNCERTAIN / UNVERIFIED |
| TASK-13 | Create/verify UI IR schemas if app UI work begins. | medium-high | near-term app UI | Codex | APP-UNIFIED-CANON | Schema tree | `schema/ui/*` present and used by views. | Generate specific UI IR implementation prompt. | WORKSTREAM-11 | FACT |
| TASK-14 | Package and store this chat report files. | critical | now | Assistant/User |  | Generated files | Old chat safely retired. | Download ZIP and files. | WORKSTREAM-06 | FACT |

### 8.1 Recommended Task Order

1. TASK-01: Preserve/use this report package in the next chat.
2. TASK-02: Verify actual repo state before claiming files exist.
3. TASK-03: Choose active workstream.
4. If application work: TASK-04, TASK-10, TASK-11, TASK-12.
5. If verification work: TASK-05, then TASK-06.
6. If docs/canon work: TASK-07 and TASK-08.

### 8.2 Blocked Tasks

- TASK-04 is blocked on repo inspection if implementing real files.
- TASK-11 and TASK-12 are blocked on actual RepoX/TestX/VALIDATE-0 docs/source.
- TASK-13 is blocked on whether UI implementation is now desired.

### 8.3 Quick Wins

- Create next chat from bootstrap.
- Inspect repo for `libs/contracts`, `libs/appcore`, RepoX, TestX.
- Generate concrete implementation prompt for application contracts once repo state is known.

### 8.4 Tasks Requiring Verification

TASK-02, TASK-11, TASK-12, TASK-13.

## 9. Constraints and Requirements

### 9.1 Hard Requirements
| ID | Constraint | Type | Hard/Soft | Source / Basis | Practical Implication | Violation Risk | Confidence | Label |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| CONSTRAINT-01 | Do not redesign closed architecture. | governance | hard | Latest user-pasted bootstrap | Implementation/audit/maintenance only. | Very high | high | FACT / PROJECT-CONTEXT |
| CONSTRAINT-02 | All systems reduce to Assemblies, Fields, Processes, Agents, Law. | ontology | hard | Latest user-pasted bootstrap | New proposals outside ontology invalid. | High | high | FACT / PROJECT-CONTEXT |
| CONSTRAINT-03 | Engine C89; game C++98. | language | hard | Latest user-pasted bootstrap | No newer language features in those layers. | High | high | FACT / PROJECT-CONTEXT |
| CONSTRAINT-04 | Apps may use newer toolchains but cannot impose requirements on engine/game. | language / boundary | hard | Latest user-pasted bootstrap | Keep app dependencies isolated. | Medium | high | FACT / PROJECT-CONTEXT |
| CONSTRAINT-05 | Applications contain no gameplay logic. | app boundary | hard | Latest app bootstrap | Apps orchestrate only. | Very high | high | FACT |
| CONSTRAINT-06 | Applications do not mutate authoritative state. | authority | hard | Latest app bootstrap | World changes through engine/game processes only. | Very high | high | FACT |
| CONSTRAINT-07 | Applications run with zero content packs installed. | app/content | hard | Latest app bootstrap | No hidden defaults; diagnostics/raw keys. | High | high | FACT |
| CONSTRAINT-08 | CLI is canonical. | UX/tooling | hard | Latest app bootstrap | TUI/GUI parity over command graph. | Medium-high | high | FACT |
| CONSTRAINT-09 | UI is data; UI contains no business logic. | UX/architecture | hard | Latest app bootstrap | Use UI IR and commands. | High | high | FACT |
| CONSTRAINT-10 | Tools read-only by default. | tools/integrity | hard | Latest app bootstrap | Explicit write if permitted. | High | high | FACT |
| CONSTRAINT-11 | Setup only install mutation authority. | app boundary | hard | APP-UNIFIED-CANON | Launcher invokes setup for mutations. | High | high | FACT |
| CONSTRAINT-12 | RepoX/TestX must not be bypassed. | CI/release | hard | Latest bootstrap | Build/push gates. | High | high | FACT / PROJECT-CONTEXT |
| CONSTRAINT-13 | No manual changelog editing. | release | hard | Latest app bootstrap | Changelogs generated from RepoX commits. | Medium-high | high | FACT |
| CONSTRAINT-14 | No distributed artifact without GBN. | release | hard | Latest bootstrap BUILD-ID-0 | Release governance. | High | high | FACT / PROJECT-CONTEXT |
| CONSTRAINT-15 | Mismatch of protocol/schema/API/ABI versions refuses loudly. | compatibility | hard | Latest bootstrap | No silent fallback. | High | high | FACT / PROJECT-CONTEXT |
| CONSTRAINT-16 | No GUI/TUI tests unless required; Win32 simple tests CLI-only. | testing | hard | User message | Avoid UI build/run errors. | Medium | high | FACT |
| CONSTRAINT-17 | No hardcoded content or magic defaults. | data/code boundary | hard | Latest bootstrap and user request | Taxonomies/data via registries. | High | high | FACT |
| CONSTRAINT-19 | Label important report items FACT/INFERENCE/UNCERTAIN/PROJECT-CONTEXT. | reporting | hard | Current user request | Avoid inventing facts. | High | high | FACT |
| CONSTRAINT-20 | This report covers this chat only. | source scope | hard | Current user request | Project context labeled separately. | Medium | high | FACT |

### 9.2 Soft Preferences
| ID | Constraint | Type | Hard/Soft | Source / Basis | Practical Implication | Violation Risk | Confidence | Label |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| CONSTRAINT-18 | ~30% source comments/docs target. | documentation | soft-hard requested | User message | Comment-density checks with meaningful comments. | Medium | medium-high | FACT |

### 9.3 Technical Constraints

Engine C89, Game C++98, no C++ ABI leakage across boundaries, CLI-first apps, deterministic tests, no wall-clock/randomness in authoritative logic, content-agnostic apps, zero-pack operation, fixed-point authoritative logic, named RNG streams only.

### 9.4 Time / Resource Constraints

No explicit deadline was established in this chat. The user wanted to retire this chat due to size/slowness and split future work into separate chats.

### 9.5 Legal / Ethical / Safety Constraints

No legal/safety-specific constraints were established beyond general anti-cheat/integrity, no hidden admin bypass, and strong epistemics.

### 9.6 Evidence / Citation Requirements

The user profile prefers correctly cited, unbiased, rigorously tested facts. In this chat’s project-planning context, future assistants must verify external/up-to-date facts separately.

### 9.7 Formatting / Output Requirements

Stable IDs, tables, files/ZIP when available, contiguous prompt blocks for Codex, FACT/INFERENCE/UNCERTAIN labels.

### 9.8 Things to Avoid

Redesigning canon, treating prompts as executed code, hidden defaults, app gameplay logic, manual changelogs, GUI/TUI test friction, magic enums/numbers, admin bypasses.

## 10. Open Questions and Unresolved Issues

| ID | Question / Issue | Why It Matters | Known Information | Unknown Information | What Would Resolve It | Priority | Related Workstream | Label |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| QUESTION-01 | Which generated prompts were actually executed in Codex? | Determines actual repo state. | Many prompts were generated. | Execution/commit status unknown. | Ask user or inspect repo. | critical | WORKSTREAM-01 | UNCERTAIN / UNVERIFIED |
| QUESTION-02 | Does CANON_INDEX.md exist and is it current? | Latest bootstrap says it is single source of truth. | CLEAN-2 mentioned. | Actual file unknown. | Inspect docs. | high | WORKSTREAM-06 | UNCERTAIN / UNVERIFIED |
| QUESTION-03 | Where exactly does RepoX metadata live? | Apps need paths/formats for readers. | RepoX is authoritative. | Files/format unknown. | Inspect RepoX docs/source. | high | WORKSTREAM-04 | UNCERTAIN / UNVERIFIED |
| QUESTION-04 | What are exact TestX/TestX2/TestX3 CLI commands and outputs? | Apps and CI need to invoke them. | TestX exists in canon. | Actual implementation unknown. | Inspect docs/source. | high | WORKSTREAM-04 | UNCERTAIN / UNVERIFIED |
| QUESTION-05 | What is VALIDATE-0 interface? | Setup/launcher validation integration. | VALIDATE-0 mentioned. | Commands/schemas unknown. | Inspect docs/source. | high | WORKSTREAM-04 | UNCERTAIN / UNVERIFIED |
| QUESTION-06 | Are `libs/contracts` and `libs/appcore` already present? | Determines first app implementation task. | Plans propose them. | Repo state unknown. | Inspect repo. | high | WORKSTREAM-02 | UNCERTAIN / UNVERIFIED |
| QUESTION-07 | Which environment variables are canonical: DOMINIUM_RUN_ROOT, DOMINIUM_HOME, both? | Launch/invoke contract. | APP-UNIFIED-CANON mentions both. | Exact semantics unknown. | Inspect app docs or ask. | medium | WORKSTREAM-02 | UNCERTAIN / UNVERIFIED |
| QUESTION-08 | Does latest ontology supersede older intent/action/effect phrasing? | Avoid terminology conflict. | Latest bootstrap root ontology; older prompts operational flow. | Canonical doc resolution unknown. | Inspect CANON_INDEX/docs or ask. | high | WORKSTREAM-01 | INFERENCE |
| QUESTION-09 | Are UI IR schemas already implemented? | App UI work depends on them. | Plans propose schema/ui. | Repo status unknown. | Inspect schema. | medium | WORKSTREAM-11 | UNCERTAIN / UNVERIFIED |
| QUESTION-10 | Is BUILD-ID-0 implemented or only specified? | Versioning/build automation. | Bootstrap says governed by BUILD-ID-0. | Implementation unknown. | Inspect repo/docs. | high | WORKSTREAM-12 | UNCERTAIN / UNVERIFIED |

## 11. Rejected, Superseded, or Deprioritised Options

| ID | Option | Status | Reason Rejected / Superseded | Final? | Reconsider Conditions | Related Workstream | Label |
| --- | --- | --- | --- | --- | --- | --- | --- |
| REJECTED-01 | Hardcoded app modes / game modes. | superseded | Canon uses laws/capabilities, no modes. | final | Never unless canon reopened. | WORKSTREAM-02 | FACT |
| REJECTED-02 | Admin bypass / isAdmin checks. | rejected | Omnipotence is capability/law/audit, no hidden flags. | final | Never; use capabilities and ToolIntents. | WORKSTREAM-02 | FACT |
| REJECTED-03 | Manual changelog editing. | rejected | RepoX-generated changelogs only. | final | Only if RepoX canon changes. | WORKSTREAM-04 | FACT / PROJECT-CONTEXT |
| REJECTED-04 | Apps auto-repairing hidden failures. | rejected | Failure behavior requires explicit user-invoked repair and reports. | final | Never unless setup repair explicitly invoked. | WORKSTREAM-02 | FACT |
| REJECTED-05 | Apps inferring state from filesystem heuristics where schema artifact exists. | rejected | Schema artifacts are authoritative. | final | Never. | WORKSTREAM-02 | FACT |
| REJECTED-06 | GUI/TUI as canonical semantics layer. | rejected | CLI is canonical; GUI/TUI are views. | final | Only if app canon reopened. | WORKSTREAM-11 | FACT |
| REJECTED-07 | Runtime strings instead of registries for data taxonomies. | rejected | Performance/determinism; use IDs/registries. | final | Never in hot paths. | WORKSTREAM-05 | FACT |
| REJECTED-08 | Enums with CUSTOM/OTHER for open taxonomies. | rejected | Use data registries; architectural enums closed-world only. | final | Never for reality taxonomies. | WORKSTREAM-05 | FACT |
| REJECTED-09 | Build number as simple global increment after tests for all builds. | superseded | BUILD-ID-0 differentiates GBN/BII/build kind. | final under current canon | Only if BUILD-ID-0 revised. | WORKSTREAM-12 | FACT |
| REJECTED-10 | Content assumptions in launcher/client/server/tools. | rejected | Apps run with zero packs installed. | final | Never. | WORKSTREAM-02 | FACT |

Preserving these prevents future assistants from reintroducing old approaches such as hidden admin flags, manual changelogs, or app-layer gameplay logic.

## 12. Artifact Ledger

| ID | Artifact / File / Prompt / Output | Type | Purpose | Status / Origin | Carry Forward? | Notes | Label |
| --- | --- | --- | --- | --- | --- | --- | --- |
| ARTIFACT-01 | Previous Context Transfer Packet | report | Base handoff generated before current package | generated in this chat | yes | Needs repair into final package. | FACT |
| ARTIFACT-02 | APP-UNIFIED-CANON | prompt | Final unified application-layer plan | generated in this chat | yes | Current app-layer prompt. | FACT |
| ARTIFACT-03 | TESTX | prompt | Superseding permanent test/version/changelog prompt | generated in this chat | yes | Current testing prompt. | FACT |
| ARTIFACT-04 | CODEHYGIENE-X | prompt | Permanent data/code boundary hygiene prompt | generated in this chat | yes | Current hygiene prompt. | FACT |
| ARTIFACT-05 | DOCS0 | prompt | Complete canonical documentation population pass | generated in this chat | yes | Docs prompt. | FACT |
| ARTIFACT-06 | CONTENT0 standalone | prompt | Content/data-only parallel chat prompt | generated in this chat | yes | Content chat. | FACT |
| ARTIFACT-07 | APP0 standalone | prompt | App/runtime/platform/renderers prompt | generated in this chat | superseded | Superseded by APP-UNIFIED-CANON for app layer. | FACT |
| ARTIFACT-08 | CANON0 | prompt | Global canon verification/docs sync | generated in this chat | yes | Macro docs prompt. | FACT |
| ARTIFACT-09 | REALITY0 | prompt | Unified reality layer docs | generated in this chat | yes | Macro docs prompt. | FACT |
| ARTIFACT-10 | LIFE0+ | prompt | Life/population macro docs | generated in this chat | yes | Macro docs prompt. | FACT |
| ARTIFACT-11 | CIV0+ | prompt | Civilization/economy macro docs | generated in this chat | yes | Macro docs prompt. | FACT |
| ARTIFACT-12 | FUTURE0 | prompt | Future-proofing/contributing/modding macro docs | generated in this chat | yes | Macro docs prompt. | FACT |
| ARTIFACT-13 | Latest global implementation/maintenance bootstrap | user-pasted text | Closed canon/current mode statement | from other chat, pasted by user | yes | Project-context but visible. | FACT |
| ARTIFACT-14 | Latest application-layer bootstrap | user-pasted text | App-specific constraints and responsibilities | from other chat, pasted by user | yes | Project-context but visible. | FACT |
| ARTIFACT-15 | Setup/launcher external plans | user-pasted text | Additional app execution planning | from other chat, pasted by user | yes | Merged into APP-UNIFIED-CANON. | FACT |
| ARTIFACT-16 | ARCH0 | prompt | Architectural constitution | generated in this chat | yes | Historical canonical prompt. | FACT |
| ARTIFACT-17 | EXEC0–EXEC4 | prompt family | Work IR/execution substrate | generated in this chat | yes | Historical prompt family. | FACT |
| ARTIFACT-18 | ECSX0–ECSX3 | prompt family | ECS/storage modularity | generated in this chat | yes | Historical prompt family. | FACT |
| ARTIFACT-19 | KERN0–KERN4 | prompt family | Kernel backend interface/scalar/SIMD/GPU/policy | generated in this chat | yes | Historical prompt family. | FACT |
| ARTIFACT-20 | ADOPT0–ADOPT6 | prompt family | Work IR adoption migration | generated in this chat | yes | Historical prompt family. | FACT |
| ARTIFACT-21 | DIST0–DIST2 | prompt family | Sharding/distribution/integrity checkpoints | generated in this chat | yes | Historical prompt family. | FACT |
| ARTIFACT-22 | EXIST/DOMAIN/TRAVEL/TIME/OMNI prompts | prompt families | Reality layer details | generated in this chat | yes | Historical prompt families. | FACT |
| ARTIFACT-23 | Phase 1 hardening prompts | prompt families | ENF/DET/PERF/SCALE/DATA/REND/EPIS/PH1 audit | generated in this chat | yes | Historical prompt families. | FACT |
| ARTIFACT-24 | LIFE/CIV/WAR/CONTENT/AGENT/TOOL/MOD/FINAL prompt sequences | prompt families | Gameplay/content/tooling plan | generated in this chat | yes | Historical; not necessarily current implementation target. | FACT |

## 13. Rationale and Assumptions

Major choices in this chat were made to preserve longevity, determinism, modularity, and implementation clarity. The application layer was made content-agnostic and contract-driven to avoid simulation leakage into setup/launcher/client/server/tools. CLI was made canonical so automation, testing, accessibility, and GUI/TUI parity can share a single semantic command graph. RepoX/TestX/BUILD-ID-0 were emphasized because the user wants automatic build/version/changelog/testing governance with minimal human ceremony. CODEHYGIENE-X exists because hardcoded taxonomies and magic values would violate the data-driven, mod-friendly nature of the project.

Key assumptions:
- The latest user-pasted bootstraps are the current project context.
- Generated prompts may or may not have been executed.
- Future work should inspect actual source/docs before implementation claims.
- The latest BUILD-ID-0 semantics supersede earlier simple build-number suggestions.

## 14. Risks and Failure Modes

| ID | Risk / Failure Mode | Consequence | Likelihood | Severity | Mitigation | Related Workstream | Label |
| --- | --- | --- | --- | --- | --- | --- | --- |
| RISK-01 | Future assistant treats prompt text as executed repo state. | Misleading implementation claims. | medium | high | Require repo inspection and mark unverified. | WORKSTREAM-01 | FACT |
| RISK-02 | Architecture re-litigation. | Time loss and canon drift. | medium | high | Use latest bootstrap: architecture closed. | WORKSTREAM-01 | FACT / PROJECT-CONTEXT |
| RISK-03 | Application logic creep. | Launcher/client/tools embed game rules. | medium | high | Use contracts/appcore and CI boundaries. | WORKSTREAM-02 | FACT |
| RISK-04 | Build/version model conflict. | Wrong artifact versioning/changelog behavior. | medium | high | Use BUILD-ID-0 latest semantics. | WORKSTREAM-12 | FACT |
| RISK-05 | Manual changelog editing creeps back. | RepoX divergence. | low-medium | medium | Enforce generated changelogs. | WORKSTREAM-04 | FACT |
| RISK-06 | Source hygiene becomes over-data-driven. | Performance/complexity loss. | medium | medium | Keep structural invariants in code. | WORKSTREAM-05 | FACT |
| RISK-07 | GUI/TUI testing friction slows implementation. | Build/run errors not needed for core tests. | medium | medium | CLI-only tests unless UI-specific. | WORKSTREAM-04 | FACT |
| RISK-08 | External other-chat context not available in future. | Missing exact APP-CANON1/BUILD-ID docs. | medium | medium-high | Ask user or upload docs/source. | WORKSTREAM-01 | PROJECT-CONTEXT |
| RISK-09 | Terminology mismatch in docs. | Confusion across prompts/chats. | medium | medium | Canonicalize via CANON_INDEX and latest ontology. | WORKSTREAM-06 | INFERENCE |
| RISK-10 | Future aggregator merges tentative prompts as decisions. | Spec pollution. | medium | high | Use labels and decision evidence. | WORKSTREAM-06 | FACT |

## 15. Verification Queue

| ID | Item Requiring Verification | Why Verification Is Needed | Suggested Verification Source/Type | Priority | Related Workstream | Label |
| --- | --- | --- | --- | --- | --- | --- |
| VERIFY-01 | Which prompts have actually been executed/committed? | Generated prompts are not repo state. | Repo history / user confirmation | critical | WORKSTREAM-01 | UNCERTAIN / UNVERIFIED |
| VERIFY-02 | Existence and content of CANON_INDEX.md. | Latest bootstrap names it single source of truth. | docs tree | high | WORKSTREAM-06 | UNCERTAIN / UNVERIFIED |
| VERIFY-03 | RepoX metadata paths and schemas. | Apps need reader contracts. | RepoX docs/source | high | WORKSTREAM-04, WORKSTREAM-02 | UNCERTAIN / UNVERIFIED |
| VERIFY-04 | TestX/VALIDATE-0 commands and outputs. | Appcore validate and tests depend on them. | Docs/source/scripts | high | WORKSTREAM-04 | UNCERTAIN / UNVERIFIED |
| VERIFY-05 | BUILD-ID-0 implementation status. | Version stamping and release enforcement. | Docs/source/version files | high | WORKSTREAM-12 | UNCERTAIN / UNVERIFIED |
| VERIFY-06 | Whether app contract/appcore dirs already exist. | Avoid duplicating or conflicting paths. | Repo source | high | WORKSTREAM-02 | UNCERTAIN / UNVERIFIED |
| VERIFY-07 | UI IR schema status. | UI implementation requirements. | schema/ui | medium | WORKSTREAM-11 | UNCERTAIN / UNVERIFIED |
| VERIFY-08 | Docs status headers and archived docs policy. | CLEAN-2 compliance. | docs tree | medium | WORKSTREAM-06 | UNCERTAIN / UNVERIFIED |

## 16. Spec Book Contribution Notes

Likely future Project Spec Book sections:
- Application Layer and Product Responsibilities
- Setup/Launcher Canon
- RepoX/TestX/Build-ID Governance
- Source Hygiene and Data/Code Boundary
- Chat Handoff and Canon Preservation
- Testing, Diagnostics, Blockers, and Changelog Automation

Unique contributions from this chat:
- APP-UNIFIED-CANON
- TESTX
- CODEHYGIENE-X
- Per-chat report package workflow
- Distinction between generated prompts and executed repo state

Likely duplicated with other chats:
- Core architecture, T0–T24 systems, SRZ-0, RepoX/TestX, APP-CANON0/1, BUILD-ID-0.

Conflicts to watch:
- Older build-number plan vs BUILD-ID-0.
- Older intent/action/effect wording vs latest Assemblies/Fields/Processes/Agents/Law ontology.
- APP0 vs APP-UNIFIED-CANON.

Formal requirements candidates:
- Apps run with zero packs.
- CLI canonical.
- Setup only install mutation authority.
- Tools read-only default.
- Product/protocol version mismatch refuses loudly.
- Changelogs generated, not manual.

Background context candidates:
- Earlier detailed Sol/content prompts.
- Large prompt family history.

Needs user confirmation:
- Actual execution status of prompts.
- Exact RepoX/TestX/VALIDATE-0 file paths and commands.

## 17. What Future Assistants Must Preserve

| Priority | Item | Type | Why It Matters | Risk If Lost | Label | Confidence |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | Architecture closed; no redesign | Constraint | Prevents drift | Re-litigation and incompatibility | FACT / PROJECT-CONTEXT | high |
| 2 | Core ontology: Assemblies, Fields, Processes, Agents, Law | Ontology | Unifies future work | Invalid abstractions | FACT / PROJECT-CONTEXT | high |
| 3 | Applications are orchestration shells only | Boundary | Prevents app logic creep | Launcher/client/server rule leakage | FACT | high |
| 4 | APP-UNIFIED-CANON is current app plan | Artifact | Guides setup/launcher/app work | Conflicting app implementations | FACT | high |
| 5 | TESTX supersedes TEST0 | Artifact | Testing/version/changelog governance | Using stale test plan | FACT | high |
| 6 | CODEHYGIENE-X current code hygiene plan | Artifact | Data/code boundary cleanup | Hardcoding persists | FACT | high |
| 7 | BUILD-ID-0 semantics supersede earlier build-number model | Decision | Release correctness | Wrong versioning/build IDs | FACT / PROJECT-CONTEXT | high |
| 8 | Generated prompts are not repo execution proof | Reliability rule | Prevents false claims | Implementation hallucination | FACT | high |
| 9 | CLI canonical and GUI/TUI are views | UX rule | Parity and automation | UI semantic drift | FACT | high |
| 10 | Tools read-only by default | Integrity rule | Prevents hidden mutation | Tool-based corruption | FACT | high |
| 11 | No manual changelog editing | Release rule | RepoX source of truth | Changelog drift | FACT | high |
| 12 | Zero content packs must work | App rule | Content agnosticism | Hidden defaults | FACT | high |

## 18. What Future Assistants Must Not Assume

- Do not assume prompts were executed.
- Do not assume files listed in prompts exist.
- Do not assume RepoX/TestX/VALIDATE-0 paths or interfaces.
- Do not assume the latest source tree matches any proposed directory structure.
- Do not assume GUI/TUI implementation is currently desired.
- Do not assume earlier build-number rules are current.
- Do not assume external other-chat content is fully available beyond pasted excerpts.
- Do not assume all project-level systems should be discussed in an application-layer chat.

## 19. Recommended Next Action

If continuing this chat’s work alone: start a new chat with the bootstrap prompt and ask the user which scope to continue. If application work is chosen, inspect repo or ask for source/docs, then generate a concrete Codex implementation prompt for `libs/contracts` and `libs/appcore`.

If aggregating this chat with other chat reports: import `spec_sheet.yaml`, `aggregator_packet.md`, and `registers.md`; preserve this chat as a source for application-layer canon, testing/version governance, and code hygiene.

User verification needed before acting:
- Which prompts have run?
- Is source/docs available?
- What are exact RepoX/TestX/VALIDATE-0 paths?
- Does CANON_INDEX exist?

## 20. Appendix: Possibly Relevant Details

- The user repeatedly prefers large, detailed, modular, future-proof prompt plans.
- The user often asks to reduce prompt count by using macro prompts but still wants maximum detail.
- The user wants future chats to be independent and possibly run concurrently in Codex.
- The user asked for separate content and app prompts to run without zipped docs/source; later provided more current app bootstraps.
- The user explicitly retired this chat and requested a final report package.
- The final package itself should be saved per-chat and later combined with reports from other old chats.
