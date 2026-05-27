# Registers — Dominium Application/TestX/CodeHygiene Handoff

## Workstream Register
| ID | Name | Label | Objective | Current State | Desired End State | Status | Priority |
| --- | --- | --- | --- | --- | --- | --- | --- |
| WORKSTREAM-01 | Dominium / Domino overall canon and architecture closure | FACT / PROJECT-CONTEXT | Preserve and continue a locked deterministic universe engine/game architecture without redesign. | Design canon declared closed/locked in user-pasted bootstrap; repo execution state unverified. | Implementation, audit, optimisation, maintenance under canon only. | active | critical |
| WORKSTREAM-02 | Application layer implementation | FACT / PROJECT-CONTEXT | Implement setup, launcher, client, server, tools as content-agnostic orchestration shells over engine/game. | APP-UNIFIED-CANON generated; latest user-pasted app bootstrap says app layer only. | Contracts, appcore, command graph, UI IR, RepoX/TestX integration, zero-pack operation. | active | critical |
| WORKSTREAM-03 | Setup and launcher unified application canon | FACT | Unify setup/launcher plans into final application-layer prompt and share with all app chats. | APP-UNIFIED-CANON produced after comparing two other-chat plans. | Use as binding app-layer implementation prompt. | active | high |
| WORKSTREAM-04 | Testing, versioning, changelog, RepoX/TestX governance | FACT | Create long-lived exhaustive testing/version/build/changelog enforcement. | TEST0 superseded by TESTX; BUILD-ID-0 semantics pasted from other chat. | Run TESTX or implement equivalent repository-wide self-defending test system. | active | critical |
| WORKSTREAM-05 | Source code hygiene and data/code boundary | FACT | Audit code for hardcoded taxonomies, magic numbers, custom/other enums, mode flags; migrate to registries/data where appropriate. | CODEHYGIENE-X generated. | Run scan -> queue -> safe migrations -> CI enforcement. | active | high |
| WORKSTREAM-06 | Documentation/canon population and chat handoff system | FACT | Create docs/canon package and per-chat transferable reports. | DOCS0 generated; prior Context Transfer Packet generated; this package finalizes old-chat report. | Store package and use in future aggregation/spec book. | active | critical |
| WORKSTREAM-07 | Content/data population | FACT | Add universe, Sol, Earth, Milky Way, civilizations, economy, scenarios as data only. | Standalone CONTENT0 generated; earlier CONTENT0–3 generated. | Separate content chat can proceed independently later. | planned | medium |
| WORKSTREAM-08 | Runtime/execution substrate and hardware abstraction | FACT | Implement Work IR, Access IR, schedulers, ECS storage, kernels, HWCAPS. | EXEC/ECSX/KERN/HWCAPS prompts generated; execution state unverified. | Use if/when implementing engine runtime internals. | planned / historical | medium |
| WORKSTREAM-09 | Reality layer: existence, domain, travel, time, authority | FACT | Formalize existence/refinement/domain volumes/travel/observer time/omnipotence. | EXIST/DOMAIN/TRAVEL/TIME/OMNI prompts generated; REALITY0 macro generated. | Referenced by docs/canon; likely not current app-layer implementation target. | historical / planned | medium |
| WORKSTREAM-10 | Life/civilization/war/agent/tool/mod systems | FACT | Earlier game/simulation systems prompt families for life, civ, war, agents, tools, mods, final policies. | Many prompts generated; latest bootstrap says T0–T24 completed and locked. | Do not redesign here; treat as project context unless docs/source provided. | historical / project-context | medium |
| WORKSTREAM-11 | Application UI / UI IR / accessibility/localisation | FACT / PROJECT-CONTEXT | Ensure all application UI is declarative, accessible, localized, and command-graph-backed. | APP-UNIFIED-CANON and latest app bootstrap require UI IR and locale packs. | Implement UI IR schemas and CLI-first parity later. | active | high |
| WORKSTREAM-12 | Release/build identity system | FACT / PROJECT-CONTEXT | Apply BUILD-ID-0 model: SemVer products, build kinds, GBN/BII, channels, protocol/schema/API/ABI versions. | Latest user-pasted global bootstrap defines locked version model. | Implementation must align with BUILD-ID-0, not earlier simple build-number idea. | active | high |

## Decision Register
| ID | Decision | Status | Evidence / Basis | Rationale | Related Workstream | Confidence | Label |
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

## Task Register
| ID | Task | Priority | Urgency | Owner | Dependencies | Inputs Needed | Expected Output | Next Step | Related Workstream | Label | Confidence |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| TASK-01 | Use this final report package as source material for a new chat. | critical | immediate | User / future assistant |  | Download/save package | New chat bootstrapped without re-explanation. | Paste bootstrap + attach package or key files. | WORKSTREAM-06 | FACT | high |
| TASK-02 | Verify actual repo state before implementation claims. | critical | immediate | Future assistant / Codex | Repo access | Source/docs zip or repo | Known actual files/commits/prompts executed. | Inspect repo; do not infer from generated prompts. | WORKSTREAM-01 | FACT | high |
| TASK-03 | Choose next active workstream. | high | immediate | User | This packet | User choice | Focused next chat. | Likely options: application implementation, TESTX, CODEHYGIENE-X, docs, content. | WORKSTREAM-01 | FACT | high |
| TASK-04 | If app implementation continues, implement libs/contracts and appcore skeleton. | high | near-term | Codex | APP-UNIFIED-CANON, Repo | Repo source | `libs/contracts` POD/TLV headers and `libs/appcore` modules scaffolded. | Generate concrete implementation prompt. | WORKSTREAM-02 | INFERENCE | medium-high |
| TASK-05 | Run or adapt TESTX. | high | near-term | Codex | Repo, TestX prompt | Build/test environment | Self-defending test/version/changelog system. | Execute TESTX or adjust to BUILD-ID-0 docs first. | WORKSTREAM-04 | FACT | high |
| TASK-06 | Run or adapt CODEHYGIENE-X. | high | after baseline tests | Codex | Repo, CODEHYGIENE-X | Source tree | HYGIENE_QUEUE, CI scanners, first safe migrations. | Run after/alongside TESTX baseline. | WORKSTREAM-05 | FACT | high |
| TASK-07 | Run DOCS0/CANON0 or verify docs status. | medium-high | near-term | Codex | Repo docs | Docs tree | Canon docs populated and status-labeled. | Inspect docs; run DOCS0 if incomplete. | WORKSTREAM-06 | FACT | medium-high |
| TASK-08 | Resolve latest ontology vs older intent/action/effect wording in docs. | high | before canon docs finalization | Future assistant/Codex | CANON_INDEX or docs | Docs/context | Terminology consistent. | Treat Assemblies/Fields/Processes/Agents/Law as root ontology unless docs say otherwise. | WORKSTREAM-01 | INFERENCE | medium |
| TASK-09 | Start separate content chat later using standalone CONTENT0. | medium | later | User / assistant | CONTENT0 prompt | Content scope | Content/data population plan or prompt execution. | Use content chat, not app/source chat. | WORKSTREAM-07 | FACT | medium |
| TASK-10 | Create application failure-mode docs when implementing launcher/setup. | high | near-term app impl | Codex | APP-UNIFIED-CANON | App source/docs | `launcher/docs/FAILURE_MODES.md` or equivalent. | Include detection, key, exit code, no auto-repair. | WORKSTREAM-02 | FACT | high |
| TASK-11 | Confirm exact RepoX metadata file paths/formats. | high | before app implementation | User/Codex | Repo | RepoX docs/source | Appcore repox reader has real contract. | Inspect repo or ask user. | WORKSTREAM-04 | UNCERTAIN / UNVERIFIED | high |
| TASK-12 | Confirm exact TestX/VALIDATE-0 invocation commands. | high | before app validation integration | Codex | Repo | Docs/source | App validate module invokes correct tools. | Inspect docs/source. | WORKSTREAM-04 | UNCERTAIN / UNVERIFIED | high |
| TASK-13 | Create/verify UI IR schemas if app UI work begins. | medium-high | near-term app UI | Codex | APP-UNIFIED-CANON | Schema tree | `schema/ui/*` present and used by views. | Generate specific UI IR implementation prompt. | WORKSTREAM-11 | FACT | medium-high |
| TASK-14 | Package and store this chat report files. | critical | now | Assistant/User |  | Generated files | Old chat safely retired. | Download ZIP and files. | WORKSTREAM-06 | FACT | high |

## Constraint Register
| ID | Constraint | Type | Hard/Soft | Source / Basis | Practical Implication | Violation Risk | Label | Confidence |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| CONSTRAINT-01 | Do not redesign closed architecture. | governance | hard | Latest user-pasted bootstrap | Implementation/audit/maintenance only. | Very high | FACT / PROJECT-CONTEXT | high |
| CONSTRAINT-02 | All systems reduce to Assemblies, Fields, Processes, Agents, Law. | ontology | hard | Latest user-pasted bootstrap | New proposals outside ontology invalid. | High | FACT / PROJECT-CONTEXT | high |
| CONSTRAINT-03 | Engine C89; game C++98. | language | hard | Latest user-pasted bootstrap | No newer language features in those layers. | High | FACT / PROJECT-CONTEXT | high |
| CONSTRAINT-04 | Apps may use newer toolchains but cannot impose requirements on engine/game. | language / boundary | hard | Latest user-pasted bootstrap | Keep app dependencies isolated. | Medium | FACT / PROJECT-CONTEXT | high |
| CONSTRAINT-05 | Applications contain no gameplay logic. | app boundary | hard | Latest app bootstrap | Apps orchestrate only. | Very high | FACT | high |
| CONSTRAINT-06 | Applications do not mutate authoritative state. | authority | hard | Latest app bootstrap | World changes through engine/game processes only. | Very high | FACT | high |
| CONSTRAINT-07 | Applications run with zero content packs installed. | app/content | hard | Latest app bootstrap | No hidden defaults; diagnostics/raw keys. | High | FACT | high |
| CONSTRAINT-08 | CLI is canonical. | UX/tooling | hard | Latest app bootstrap | TUI/GUI parity over command graph. | Medium-high | FACT | high |
| CONSTRAINT-09 | UI is data; UI contains no business logic. | UX/architecture | hard | Latest app bootstrap | Use UI IR and commands. | High | FACT | high |
| CONSTRAINT-10 | Tools read-only by default. | tools/integrity | hard | Latest app bootstrap | Explicit write if permitted. | High | FACT | high |
| CONSTRAINT-11 | Setup only install mutation authority. | app boundary | hard | APP-UNIFIED-CANON | Launcher invokes setup for mutations. | High | FACT | high |
| CONSTRAINT-12 | RepoX/TestX must not be bypassed. | CI/release | hard | Latest bootstrap | Build/push gates. | High | FACT / PROJECT-CONTEXT | high |
| CONSTRAINT-13 | No manual changelog editing. | release | hard | Latest app bootstrap | Changelogs generated from RepoX commits. | Medium-high | FACT | high |
| CONSTRAINT-14 | No distributed artifact without GBN. | release | hard | Latest bootstrap BUILD-ID-0 | Release governance. | High | FACT / PROJECT-CONTEXT | high |
| CONSTRAINT-15 | Mismatch of protocol/schema/API/ABI versions refuses loudly. | compatibility | hard | Latest bootstrap | No silent fallback. | High | FACT / PROJECT-CONTEXT | high |
| CONSTRAINT-16 | No GUI/TUI tests unless required; Win32 simple tests CLI-only. | testing | hard | User message | Avoid UI build/run errors. | Medium | FACT | high |
| CONSTRAINT-17 | No hardcoded content or magic defaults. | data/code boundary | hard | Latest bootstrap and user request | Taxonomies/data via registries. | High | FACT | high |
| CONSTRAINT-18 | ~30% source comments/docs target. | documentation | soft-hard requested | User message | Comment-density checks with meaningful comments. | Medium | FACT | medium-high |
| CONSTRAINT-19 | Label important report items FACT/INFERENCE/UNCERTAIN/PROJECT-CONTEXT. | reporting | hard | Current user request | Avoid inventing facts. | High | FACT | high |
| CONSTRAINT-20 | This report covers this chat only. | source scope | hard | Current user request | Project context labeled separately. | Medium | FACT | high |

## User Preference Register
| ID | Preference | Basis Type | Source Basis | Strength | Implication | Label |
| --- | --- | --- | --- | --- | --- | --- |
| PREF-01 | Wants maximum-fidelity transfer reports, not normal summaries. | explicit | Current user request | high | Future assistants should preserve detail and labels. | FACT |
| PREF-02 | Prefers modular, extensible, robust, future-proof designs. | explicit | Repeated user wording throughout chat | high | Outputs should emphasize modularity and long-term maintainability. | FACT |
| PREF-03 | Wants CLI-only tests/apps unless GUI/TUI specifically required. | explicit | User testing request | high | Avoid UI testing friction. | FACT |
| PREF-04 | Wants data-driven taxonomies and minimal hardcoded assumptions. | explicit | User code hygiene request | high | Use registries/data for open-world concepts. | FACT |
| PREF-05 | Wants strict documentation/comment density and cross-referenced blockers. | explicit | User CODEHYGIENE/TESTX requests | medium-high | Implement comment/doc policies. | FACT |
| PREF-06 | Likes contiguous TXT blocks for Codex prompts. | inferred | Multiple asks for one big txt block | high | Provide copy-paste prompts in code fences. | INFERENCE |
| PREF-07 | Values auditability, verifiability, and stable IDs. | explicit | Current report package requirements and prior prompts | high | Use registers/tables/IDs. | FACT |

## Open Questions Register
| ID | Question | Why It Matters | Known | Unknown | Resolution Path | Priority | Related Workstream | Label |
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

## Artifact Ledger
| ID | Artifact / File / Prompt / Output | Type | Purpose | Status / Origin | Carry Forward? | Notes |
| --- | --- | --- | --- | --- | --- | --- |
| ARTIFACT-01 | Previous Context Transfer Packet | report | Base handoff generated before current package | generated in this chat | yes | Needs repair into final package. |
| ARTIFACT-02 | APP-UNIFIED-CANON | prompt | Final unified application-layer plan | generated in this chat | yes | Current app-layer prompt. |
| ARTIFACT-03 | TESTX | prompt | Superseding permanent test/version/changelog prompt | generated in this chat | yes | Current testing prompt. |
| ARTIFACT-04 | CODEHYGIENE-X | prompt | Permanent data/code boundary hygiene prompt | generated in this chat | yes | Current hygiene prompt. |
| ARTIFACT-05 | DOCS0 | prompt | Complete canonical documentation population pass | generated in this chat | yes | Docs prompt. |
| ARTIFACT-06 | CONTENT0 standalone | prompt | Content/data-only parallel chat prompt | generated in this chat | yes | Content chat. |
| ARTIFACT-07 | APP0 standalone | prompt | App/runtime/platform/renderers prompt | generated in this chat | superseded | Superseded by APP-UNIFIED-CANON for app layer. |
| ARTIFACT-08 | CANON0 | prompt | Global canon verification/docs sync | generated in this chat | yes | Macro docs prompt. |
| ARTIFACT-09 | REALITY0 | prompt | Unified reality layer docs | generated in this chat | yes | Macro docs prompt. |
| ARTIFACT-10 | LIFE0+ | prompt | Life/population macro docs | generated in this chat | yes | Macro docs prompt. |
| ARTIFACT-11 | CIV0+ | prompt | Civilization/economy macro docs | generated in this chat | yes | Macro docs prompt. |
| ARTIFACT-12 | FUTURE0 | prompt | Future-proofing/contributing/modding macro docs | generated in this chat | yes | Macro docs prompt. |
| ARTIFACT-13 | Latest global implementation/maintenance bootstrap | user-pasted text | Closed canon/current mode statement | from other chat, pasted by user | yes | Project-context but visible. |
| ARTIFACT-14 | Latest application-layer bootstrap | user-pasted text | App-specific constraints and responsibilities | from other chat, pasted by user | yes | Project-context but visible. |
| ARTIFACT-15 | Setup/launcher external plans | user-pasted text | Additional app execution planning | from other chat, pasted by user | yes | Merged into APP-UNIFIED-CANON. |
| ARTIFACT-16 | ARCH0 | prompt | Architectural constitution | generated in this chat | yes | Historical canonical prompt. |
| ARTIFACT-17 | EXEC0–EXEC4 | prompt family | Work IR/execution substrate | generated in this chat | yes | Historical prompt family. |
| ARTIFACT-18 | ECSX0–ECSX3 | prompt family | ECS/storage modularity | generated in this chat | yes | Historical prompt family. |
| ARTIFACT-19 | KERN0–KERN4 | prompt family | Kernel backend interface/scalar/SIMD/GPU/policy | generated in this chat | yes | Historical prompt family. |
| ARTIFACT-20 | ADOPT0–ADOPT6 | prompt family | Work IR adoption migration | generated in this chat | yes | Historical prompt family. |
| ARTIFACT-21 | DIST0–DIST2 | prompt family | Sharding/distribution/integrity checkpoints | generated in this chat | yes | Historical prompt family. |
| ARTIFACT-22 | EXIST/DOMAIN/TRAVEL/TIME/OMNI prompts | prompt families | Reality layer details | generated in this chat | yes | Historical prompt families. |
| ARTIFACT-23 | Phase 1 hardening prompts | prompt families | ENF/DET/PERF/SCALE/DATA/REND/EPIS/PH1 audit | generated in this chat | yes | Historical prompt families. |
| ARTIFACT-24 | LIFE/CIV/WAR/CONTENT/AGENT/TOOL/MOD/FINAL prompt sequences | prompt families | Gameplay/content/tooling plan | generated in this chat | yes | Historical; not necessarily current implementation target. |

## Rejected / Superseded Options Register
| ID | Option | Status | Reason | Final? | Reconsider Conditions | Related Workstream | Label |
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

## Risk Register
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

## Verification Queue
| ID | Item Requiring Verification | Why Verification Is Needed | Suggested Source Type | Priority | Related Workstreams | Label |
| --- | --- | --- | --- | --- | --- | --- |
| VERIFY-01 | Which prompts have actually been executed/committed? | Generated prompts are not repo state. | Repo history / user confirmation | critical | WORKSTREAM-01 | UNCERTAIN / UNVERIFIED |
| VERIFY-02 | Existence and content of CANON_INDEX.md. | Latest bootstrap names it single source of truth. | docs tree | high | WORKSTREAM-06 | UNCERTAIN / UNVERIFIED |
| VERIFY-03 | RepoX metadata paths and schemas. | Apps need reader contracts. | RepoX docs/source | high | WORKSTREAM-04, WORKSTREAM-02 | UNCERTAIN / UNVERIFIED |
| VERIFY-04 | TestX/VALIDATE-0 commands and outputs. | Appcore validate and tests depend on them. | Docs/source/scripts | high | WORKSTREAM-04 | UNCERTAIN / UNVERIFIED |
| VERIFY-05 | BUILD-ID-0 implementation status. | Version stamping and release enforcement. | Docs/source/version files | high | WORKSTREAM-12 | UNCERTAIN / UNVERIFIED |
| VERIFY-06 | Whether app contract/appcore dirs already exist. | Avoid duplicating or conflicting paths. | Repo source | high | WORKSTREAM-02 | UNCERTAIN / UNVERIFIED |
| VERIFY-07 | UI IR schema status. | UI implementation requirements. | schema/ui | medium | WORKSTREAM-11 | UNCERTAIN / UNVERIFIED |
| VERIFY-08 | Docs status headers and archived docs policy. | CLEAN-2 compliance. | docs tree | medium | WORKSTREAM-06 | UNCERTAIN / UNVERIFIED |

## Timeline Register
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

## Spec Book Contribution Register
| Section Candidate | Contribution From This Chat | Status | Verification Needed |
| --- | --- | --- | --- |
| Application Layer | APP-UNIFIED-CANON; setup/launcher/client/server/tools boundaries; command graph; UI IR; RepoX integration | High-value current material | Verify against APP-CANON0/1/APP-AUTO-0 docs |
| Testing and Release Governance | TESTX; BUILD-ID-0 semantics; changelog/version rules | High-value current material | Verify actual TestX/RepoX/BUILD-ID docs |
| Source Code Hygiene | CODEHYGIENE-X; registry/data boundary; comment density; TODO blockers | High-value current material | Inspect source and run scanners |
| Canon Transfer Process | DOCS0, Context Transfer Packet, final report package design | High-value meta-process | Keep per-chat package provenance |
