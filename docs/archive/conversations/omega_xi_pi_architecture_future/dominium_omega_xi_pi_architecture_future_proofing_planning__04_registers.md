# STRUCTURED REGISTERS — Dominium Omega/Xi/Pi Architecture & Future-Proofing Planning

## 17. Workstream Register

| ID | Name | Objective | Current state | Desired end state | Status | Priority | Confidence | Label |
|---|---|---|---|---|---|---|---|---|
| WORKSTREAM-01 | Dominium/DOMINO platform doctrine | Define the long-term architecture philosophy | Mature doctrine established | Contracts-first deterministic platform | Active | P0 | High | FACT |
| WORKSTREAM-02 | Ω-series | Runtime/distribution MVP freeze | Planned and reportedly used | Frozen MVP proofs/distribution | Reported complete/used | P0 | Medium | FACT(user-reported) |
| WORKSTREAM-03 | Ξ-series | Repo convergence and drift immunity | User reports Xi-8 complete | Frozen repo structure + CI guardrails | Reported complete | P0 | Medium | FACT(user-reported) |
| WORKSTREAM-04 | Π-series | Meta-blueprint and final prompt inventory | User reports Pi-2 complete | Blueprint/prompt inventory ready for snapshot mapping | Reported complete | P0 | Medium | FACT(user-reported) |
| WORKSTREAM-05 | Ρ-series | Snapshot-driven final planning | Planned, not executed | Repo-specific Σ/Φ/Υ/Z plan | Pending | P0 | High | FACT |
| WORKSTREAM-06 | Σ-series | Agent/human governance | Planned | Vendor-neutral agent/task governance | Pending | P1 | High | FACT |
| WORKSTREAM-07 | Φ-series | Runtime component/service kernel | Planned | Componentized runtime with lifecycle/state foundations | Pending | P1 | Medium | FACT |
| WORKSTREAM-08 | Υ-series | Build/release/control plane | Planned | Unified build/release/archive/manual+auto ops | Pending | P1 | Medium | FACT |
| WORKSTREAM-09 | Ζ-series | Live runtime operations | Long-term planned | Deterministic live ops with rollback/proofs | Future | P3 | Medium | FACT |
| WORKSTREAM-10 | Workbench/AIDE | Visual/agentic production environment | Conceptual | Command-driven workbench modules | Future | P2 | Medium | INFERENCE |
| WORKSTREAM-11 | Second-game proof | Prove Domino reuse | Proposed | Minimal non-Dominium game using Domino/runtime | Pending | P2 | Medium | INFERENCE |

## 18. Decision Register

| ID | Decision | Status | Evidence / basis | Rationale | Implications | Related workstream | Confidence | Label |
|---|---|---|---|---|---|---|---|---|
| DECISION-01 | Treat project as deterministic simulation platform / OS-like runtime | Final direction | Repeated discussion | Matches goals | Guides all architecture | WORKSTREAM-01 | High | FACT |
| DECISION-02 | Keep suite version but decouple from compatibility | Final | Versioning discussion | Suite is curated snapshot | Compatibility by contracts/ranges | WORKSTREAM-08 | High | FACT |
| DECISION-03 | Products/tools/packs/protocols/schemas/formats have independent versions | Final | Versioning discussion | Enables mix-match | Release index must track axes | WORKSTREAM-08 | High | FACT |
| DECISION-04 | Use CAP-NEG/contracts/migration/trust for compatibility | Final | Repeated | Explicit compatibility safer | More registries/gates | WORKSTREAM-08 | High | FACT |
| DECISION-05 | Avoid active generic `src` roots | Final direction | Xi/source discussion | Prevents shadow modules | RepoX enforcement | WORKSTREAM-03 | Medium | FACT/UNCERTAIN current state |
| DECISION-06 | Do not create ArchX subsystem; extend XStack with architecture graph | Final | XStack discussion | Avoid subsystem sprawl | RepoX/AuditX/ControlX/TestX own it | WORKSTREAM-03 | High | FACT |
| DECISION-07 | AGENTS.md useful but non-authoritative | Final | Agent governance discussion | XStack/artifacts must enforce | Generate mirrors | WORKSTREAM-06 | High | FACT |
| DECISION-08 | Run Ρ before Σ/Φ/Υ/Z | Final next-step doctrine | Last planning phase | Grounds plans in repo reality | Immediate next action | WORKSTREAM-05 | High | FACT |
| DECISION-09 | Do not implement Z before foundations | Final | Z discussion | Avoids hacks | Φ/Υ first | WORKSTREAM-09 | High | FACT |
| DECISION-10 | Packs should not contain silent executable authority | Final direction | Pack/trust discussion | Security/determinism | Native/script mods later | WORKSTREAM-08/09 | High | FACT |
| DECISION-11 | Stable contracts, replaceable implementations | Final doctrine | Repeated | Enables rewrites | Boundary focus | WORKSTREAM-01 | High | FACT |
| DECISION-12 | Workbench should start with validation/command spine | Recommended | Workbench discussion | Avoid GUI-first trap | Start with validation dashboard | WORKSTREAM-10 | Medium | INFERENCE |

## 19. Task Register

| ID | Task | Priority | Urgency | Owner | Dependencies | Inputs needed | Expected output | Next step | Related workstream | Label |
|---|---|---|---|---|---|---|---|---|---|---|
| TASK-01 | Generate/execute Ρ-0 Snapshot Intake | P0 | U0 | Future assistant/Codex | Pi outputs/current repo | GitHub main or snapshot | Snapshot intake protocol | Start here | WORKSTREAM-05 | FACT |
| TASK-02 | Execute Ρ-1 Reality Extraction | P0 | U1 | Codex | TASK-01 | Repo tree/build/docs/tools | Reality inventory | After Ρ-0 | WORKSTREAM-05 | FACT |
| TASK-03 | Execute Ρ-2 Blueprint Reconciliation | P0 | U1 | Codex/human review | Ρ-1 + Π | Inventories/blueprints | keep/extend/merge/replace/quarantine | After Ρ-1 | WORKSTREAM-05 | FACT |
| TASK-04 | Execute Ρ-3 Foundation Readiness | P0 | U1 | Codex | Ρ-2 | Reconciliation decisions | readiness matrix | After Ρ-2 | WORKSTREAM-05 | FACT |
| TASK-05 | Execute Ρ-4 Final Prompt Synthesis | P0 | U1 | Codex | Ρ-3 | readiness matrix | final Σ/Φ/Υ/Z plan | After Ρ-3 | WORKSTREAM-05 | FACT |
| TASK-06 | Verify current GitHub main state | P0 | U0 if implementation-specific | Assistant/user | Internet/GitHub | Repo access | Current truth | Before repo-specific claims | WORKSTREAM-03/05 | UNCERTAIN |
| TASK-07 | Implement Σ-0 Agent Governance | P1 | U1 | Codex | Ρ completed | Repo policies | AGENTS/context/tasks | After Ρ | WORKSTREAM-06 | FACT |
| TASK-08 | Implement Φ-0/Φ-1 runtime/component model | P1 | U2 | Codex | Ρ completed | runtime reality | doctrine/schemas/registries | After Ρ | WORKSTREAM-07 | FACT |
| TASK-09 | Implement Υ-0/Υ-1 build graph/preset consolidation | P1 | U2 | Codex | Ρ build map | presets/scripts | locked build graph | After Ρ | WORKSTREAM-08 | FACT |
| TASK-10 | Design second-game proof | P2 | U2 | Codex/human | Engine/runtime boundaries | Candidate game | examples/games minimal proof | After Φ basics | WORKSTREAM-11 | INFERENCE |

## 20. Constraint Register

| ID | Constraint | Type | Hard/soft | Source / basis | Practical implication | Violation risk | Confidence | Label |
|---|---|---|---|---|---|---|---|---|
| CONSTRAINT-01 | Truth paths deterministic | Technical | Hard | Whole chat | fixed-point/named RNG/no wallclock | replay/proofs break | High | FACT |
| CONSTRAINT-02 | Stable semantic IDs | Technical | Hard | Versioning/refactor doctrine | Path moves cannot change identity | saves/mods break | High | FACT |
| CONSTRAINT-03 | XStack authoritative | Process | Hard direction | Xi/agent discussion | Prompts/docs not enough | AI drift | High | FACT |
| CONSTRAINT-04 | No active generic source roots | Repo | Hard direction | Xi/source discussion | ownership roots only | shadow impls | Medium | FACT/UNCERTAIN current |
| CONSTRAINT-05 | Runtime must not own truth | Architecture | Hard | runtime doctrine | runtime services host/present only | semantic coupling | High | FACT |
| CONSTRAINT-06 | Apps thin | Architecture | Hard direction | AppShell/product discussion | product shells call services | duplicated logic | High | FACT |
| CONSTRAINT-07 | Packs no silent authority | Security | Hard direction | pack/trust discussion | package contracts/trust | mod exploits | High | FACT |
| CONSTRAINT-08 | Old releases archived | Release | Hard goal | archive discussion | immutable indices/artifacts | extinction risk | High | FACT |
| CONSTRAINT-09 | Ask only needed clarifying questions | Communication | Soft/hard preference | user instructions | proceed with assumptions when safe | delay/frustration | High | FACT |
| CONSTRAINT-10 | Distinguish facts/inferences/uncertainty | Communication | Hard | user request | epistemic labels | trust loss | High | FACT |

## 21. User Preference Register

| ID | Preference | Area | Explicit/inferred/uncertain | Strength | Practical implication | Risk if wrong | Label |
|---|---|---|---|---|---|---|---|
| PREF-01 | Direct, source-grounded, audit-ready answers | Style | Explicit | High | cite/label evidence | trust loss | FACT |
| PREF-02 | Exhaustive planning when asked | Output | Explicit | High | long structured plans | under-answering | FACT |
| PREF-03 | Challenge framing | Reasoning | Explicit | High | correct assumptions | false agreement | FACT |
| PREF-04 | Preserve rejected options | Continuity | Explicit | High | include rejected/superseded | repeat old work | FACT |
| PREF-05 | Prefer future-proof modular design | Technical | Explicit | High | contracts/interfaces | brittle code | FACT |
| PREF-06 | Avoid over-compression | Handoff | Explicit | High | appendices/registers | context loss | FACT |
| PREF-07 | Use markdown/tables where useful | Format | Inferred/explicit | Medium | headings/tables | poor readability | INFERENCE |
| PREF-08 | Wants ambition preserved | Emotional/context | Inferred | Medium | do not trivialise | demotivation | INFERENCE |

## 22. Open Questions Register

| ID | Question / issue | Why it matters | Known information | Unknown information | Resolution path | Priority | Related workstream | Label |
|---|---|---|---|---|---|---|---|---|
| QUESTION-01 | What is current live repo tree? | Planning accuracy | User reports GitHub main pushed | Actual current files | Browse/inspect GitHub | P0 | WORKSTREAM-05 | UNCERTAIN |
| QUESTION-02 | Does top-level `src` exist now? | Repo doctrine | User reported no; snapshot showed yes | Current truth | Verify repo | P0 | WORKSTREAM-03 | UNCERTAIN |
| QUESTION-03 | Which future prompts already have partial implementation? | Avoid duplication | Pi inventory exists | Repo reality | Ρ-1/Ρ-2 | P0 | WORKSTREAM-05 | FACT |
| QUESTION-04 | Which runtime modules map to Φ components? | Φ execution | Snapshot shows engine/modules | Exact quality/ownership | Ρ-2 | P1 | WORKSTREAM-07 | UNCERTAIN |
| QUESTION-05 | Are agent vendor docs current? | Σ implementation | Prior browse used docs | Current docs | Web verify | P1 | WORKSTREAM-06 | UNCERTAIN |
| QUESTION-06 | What ABI boundary names/prefixes should be final? | API stability | recommendations exist | final choice | human review | P1 | WORKSTREAM-01 | INFERENCE |

## 23. Artifact Ledger

| ID | Artifact / file / prompt / output | Type | Purpose | Status | Origin | Carry forward? | Notes | Label |
|---|---|---|---|---|---|---|---|---|
| ARTIFACT-01 | `NEW.txt` / `dir (1).txt` | uploaded repo snapshot | Snapshot/drift evidence | Available in this runtime | User upload | Yes | May be stale | FACT |
| ARTIFACT-02 | `Pasted text.txt` | uploaded instruction | Defines preservation task | Available | User upload | Yes | Immediate task spec | FACT |
| ARTIFACT-03 | `architecture_graph.v1.json` | repo artifact | Frozen architecture graph | User-reported exists | Xi-6 | Yes | verify live | FACT(user-reported) |
| ARTIFACT-04 | `module_boundary_rules.v1.json` | repo artifact | Module boundaries | User-reported | Xi-6 | Yes | verify live | FACT(user-reported) |
| ARTIFACT-05 | `single_engine_registry.json` | repo artifact | Canonical semantic engines | User-reported | Xi-6 | Yes | verify live | FACT(user-reported) |
| ARTIFACT-06 | `repository_structure_lock.json` | repo artifact | Repo structure lock | User-reported | Xi-8 | Yes | verify live | FACT(user-reported) |
| ARTIFACT-07 | `FINAL_PROMPT_INVENTORY.md/json` | repo artifact | Future prompt inventory | User-reported | Pi-2 | Yes | key input for Ρ | FACT(user-reported) |
| ARTIFACT-08 | `SERIES_EXECUTION_STRATEGY.md/json` | repo artifact | Future execution strategy | User-reported | Pi-1 | Yes | key input for Ρ | FACT(user-reported) |
| ARTIFACT-09 | `META_BLUEPRINT_INDEX.md` | repo artifact | Meta blueprint | User-reported | Pi-0 | Yes | key input for Ρ | FACT(user-reported) |
| ARTIFACT-10 | Ω-series prompts | prompt set | MVP freeze | Generated in chat | Assistant/user | Yes | use as context | FACT |
| ARTIFACT-11 | Ξ-series prompts | prompt set | repo convergence | Generated in chat | Assistant/user | Yes | partly executed | FACT |
| ARTIFACT-12 | Π-series prompts | prompt set | future planning | Generated in chat | Assistant/user | Yes | reportedly executed | FACT |

## 24. Rejected / Superseded Options Register

| ID | Option | Status | Reason | Final or tentative? | Reconsider conditions | Related workstream | Label |
|---|---|---|---|---|---|---|---|
| REJECTED-01 | Remove suite version entirely | Rejected | Suite useful as curated snapshot | Final | If product model changes radically | Υ | FACT |
| REJECTED-02 | Long-lived per-product branches | Rejected | Merge/integration drift | Final | Polyrepo future with strong contracts | Υ | FACT |
| REJECTED-03 | New ArchX subsystem | Rejected | Existing XStack sufficient | Final | If XStack architecture changes | Ξ | FACT |
| REJECTED-04 | Full fluids/chemistry/materials before MVP | Deprioritised | Scope explosion | Temporary | Future domain series | Ω/domain | FACT |
| REJECTED-05 | Implement Z directly now | Deprioritised | Missing foundations | Final for now | After Φ/Υ | Ζ | FACT |
| REJECTED-06 | GUI/Workbench first | Deprioritised | Need command spine first | Tentative | After floors | Workbench | INFERENCE |
| REJECTED-07 | Generic `src` active root | Rejected | Ownership hidden | Final direction | none except classified content source | Ξ | FACT |
| REJECTED-08 | Vendor-specific agent strategy | Rejected | Tool lock-in | Final | none | Σ | FACT |

## 25. Risk Register

| ID | Risk / failure mode | Consequence | Likelihood | Severity | Mitigation | Related workstream | Label |
|---|---|---|---|---|---|---|---|
| RISK-01 | Stale snapshot mistaken for current repo | Wrong plan | Medium | High | verify GitHub/live repo | Ρ | FACT |
| RISK-02 | Assistant restarts Ω/Ξ/Π | wasted work/context drift | Medium | Medium | use handoff | all | FACT |
| RISK-03 | AI creates duplicate implementations | architectural drift | High historically | High | XStack/Ξ gates | Ξ/Σ | FACT |
| RISK-04 | Z implemented before foundations | brittle hacks | Medium | High | dependency gates | Ζ | FACT |
| RISK-05 | Vendor agent docs stale | bad integration | Medium | Medium | web verify | Σ | UNCERTAIN |
| RISK-06 | Runtime semantics leak into UI/tools | truth inconsistency | Medium | High | command/refusal spine | Φ | FACT |
| RISK-07 | Public API not stabilised | reuse/open-closed split fails | Medium | High | ABI table | Φ/Υ | INFERENCE |
| RISK-08 | Packs gain executable authority | security/determinism risk | Medium | High | trust/sandbox | Υ/Ζ | FACT |

## 26. Verification Queue

| ID | Item requiring verification | Why verification is needed | Suggested source/type | Priority | Related workstream | Label |
|---|---|---|---|---|---|---|
| VERIFY-01 | Current GitHub head/commits | user-reported state | GitHub browse/git | P0 | Ρ | UNCERTAIN |
| VERIFY-02 | Current root tree / `src` status | stale snapshot conflict | repo tree | P0 | Ρ/Ξ | UNCERTAIN |
| VERIFY-03 | Xi/Pi artifact hashes | planning inputs | repo files | P0 | Ρ | UNCERTAIN |
| VERIFY-04 | XStack FAST/STRICT pass | enforcement health | local CI | P0 | Ξ/Ρ | UNCERTAIN |
| VERIFY-05 | AGENTS/Copilot/Claude current docs | vendor features change | web docs | P1 | Σ | UNCERTAIN |
| VERIFY-06 | Build presets/scripts current canonical state | Υ planning | repo extraction | P1 | Υ | UNCERTAIN |
| VERIFY-07 | Runtime service code locations | Φ mapping | repo extraction | P1 | Φ | UNCERTAIN |

## 27. Chronological Timeline Register

| Sequence | Event / topic | What changed or was decided | Why it mattered | Current relevance | Confidence |
|---|---|---|---|---|---|
| 1 | MVP/product readiness | products standalone, CLI/TUI/GUI fallback | product family model | AppShell doctrine | High |
| 2 | Earth/Sol/Gal realism | stubs not full sim | scope control | EARTH/SOL/GAL future | High |
| 3 | Compatibility ecosystem | CAP-NEG/PACK/LIB etc. | mix-match versions | release/update foundations | High |
| 4 | DIST/RELEASE | distribution as ecosystem proof | productisation | Υ/DIST | High |
| 5 | Versioning | suite vs product versions | compatibility clarity | Υ | High |
| 6 | Repo `src` concern | Xi-series | drift prevention | completed/reverify | High |
| 7 | Agent governance | AGENTS + mirrors + XStack | AI/human safety | Σ | High |
| 8 | OS-like runtime | Φ/Z planning | live ops foundation | future | High |
| 9 | Pi planning | prompt inventory | plan future series | done/user-reported | Medium |
| 10 | Current preservation request | package chat context | handoff | now | High |

## 28. Spec Book Contribution Register

| Spec-book area | Contribution from this chat | Source IDs | Should become requirement/context/open issue? | Confidence | Notes |
|---|---|---|---|---|---|
| Architecture Doctrine | Stable contracts/replaceable implementations | DECISION-11 | Requirement | High | Core doctrine |
| Repo Governance | Xi/XStack immune system | WORKSTREAM-03 | Requirement/context | High | Verify repo |
| Agent Governance | Σ strategy | WORKSTREAM-06 | Requirement | High | Vendor-neutral |
| Runtime Architecture | Φ service/kernel model | WORKSTREAM-07 | Requirement/context | Medium | Needs mapping |
| Release/Distribution | Υ/component/release index policy | WORKSTREAM-08 | Requirement | High | Many prior prompts |
| Live Operations | Ζ capability ladder | WORKSTREAM-09 | Future roadmap | Medium | foundation dependent |
| Coding Standards | naming/API/schema doctrine | CONSTRAINTS/DECISIONS | Requirement | Medium | formalise later |
| Spec Aggregation | preservation/handoff method | this report | Context/process | High | Useful for other chats |
