# Structured Registers — Dominium Timekeeping and 2038 Resilience

## 17. Workstream Register

| ID | Name | Objective | Current state | Desired end state | Status | Priority | Confidence | Label |
|---|---|---|---|---|---|---|---|---|
| WORKSTREAM-01 | 2038 and legacy time-risk analysis | Understand what fails after 2038 and what does not | Explained at conceptual/platform level | External facts verified and converted into coding rules | Active | P1 | 4 | FACT/INFERENCE |
| WORKSTREAM-02 | Timestamp representation design | Choose durable internal representations for broad range and useful precision | Recommended signed 64-bit seconds+nanos, 100 ns or microsecond scalar alternatives | Formal Dominium type policy | Active | P1 | 4 | INFERENCE |
| WORKSTREAM-03 | Cross-platform time framework | Separate instant, duration, monotonic elapsed time, and civil/local time | Proposed as architecture pattern | Canonical platform-neutral contract | Active | P1 | 4 | INFERENCE |
| WORKSTREAM-04 | Dominium time architecture mapping | Apply the framework to Dominium docs and code | Repository docs/code were inspected selectively; core model assessed | Repo-level time doctrine plus tests and backend audit | Active | P0 | 4 | FACT/INFERENCE |
| WORKSTREAM-05 | Preservation and aggregation package | Preserve this chat for later reading and spec-book merging | Current task creates report, registers, spec sheet, files, ZIP | Complete package available for download and later aggregation | Active | P0 | 4 | FACT |

## 18. Decision Register

| ID | Decision | Status | Evidence / basis | Rationale | Implications | Related workstream | Confidence | Label |
|---|---|---|---|---|---|---|---|---|
| DECISION-01 | The 2038 risk is primarily signed 32-bit Unix-style time, not 32-bit hardware itself. | Assistant conclusion; not independently reverified in this turn | Earlier Q&A in this chat | Separates CPU/OS bitness from API/data representation | Focus audits on `time_t`, persisted timestamps, protocols, ABI structs | WORKSTREAM-01 | 4 | INFERENCE |
| DECISION-02 | For new project timekeeping, signed 64-bit should be preferred over unsigned 32-bit. | Assistant recommendation; user not separately confirmed | Earlier Q&A in this chat | Unsigned 32-bit only moves a Unix-second overflow to 2106 and loses signed range | Project code should avoid unsigned 32-bit absolute time | WORKSTREAM-01/02 | 4 | INFERENCE |
| DECISION-03 | For a single int64 spanning about ±10,000 years, use 100 ns ticks or 1 µs ticks; if not scalar-bound, use int64 seconds + nanoseconds. | Assistant recommendation; not explicitly accepted | Earlier Q&A in this chat | Balances range and precision; avoids int64 nanosecond ±292-year limit | Candidate canonical representation for APIs/storage, not necessarily Dominium ACT | WORKSTREAM-02 | 4 | INFERENCE |
| DECISION-04 | Durable software should separate absolute instant, duration, monotonic elapsed time, and civil/local time. | Assistant recommendation; user asked for framework | Earlier Q&A in this chat | Prevents wall-clock, calendar, timezone, and elapsed-time bugs from collapsing into one type | Architecture pattern for Dominium and other projects | WORKSTREAM-03 | 4 | INFERENCE |
| DECISION-05 | Dominium's authoritative world time should remain logical ACT, not wall-clock. | Strongly supported by repo docs/code; aligns with assistant recommendation | `DISTRIBUTED_TIME_MODEL`, `TIMING_AND_CLOCKS`, `dom_time_core.h` | Preserves deterministic replay and cross-shard ordering | Wall-clock APIs must remain outside authority logic | WORKSTREAM-04 | 5 | FACT/INFERENCE |
| DECISION-06 | DSYS/platform monotonic microseconds are non-authoritative runtime timing only. | Strongly supported by repo docs/code | `TIMING_AND_CLOCKS`, `PLATFORM_RUNTIME`, `app_runtime.c` | Suitable for pacing, sleeps, telemetry, UI; unsafe for authoritative ordering | Backend audit should focus on keeping this boundary clean | WORKSTREAM-04 | 4 | FACT/INFERENCE |
| DECISION-07 | Observer/replay/perception clocks should remain derived from ACT and never modify ACT. | Supported by observer-clock and replay docs | `SPEC_OBSERVER_CLOCKS`, `REPLAY_AND_TIME_ASYMMETRY` | Supports replay/spectating/asymmetric perception without changing outcomes | Observer clocks need tests and capability/law constraints | WORKSTREAM-04 | 4 | FACT/INFERENCE |
| DECISION-08 | Civil/astronomical/human-readable time should be a projection layer, not core ACT. | Assistant recommendation supported by placeholder ACT→BST/GCT/CPT code | `dom_time_frames.c` placeholder conversions | Avoids calendar/time-zone/lore changes corrupting simulation authority | Future calendar systems should be schemas/adapters | WORKSTREAM-04 | 4 | INFERENCE |

## 19. Task Register

| ID | Task | Priority | Urgency | Owner | Dependencies | Inputs needed | Expected output | Next step | Related workstream | Label |
|---|---|---|---|---|---|---|---|---|---|---|
| TASK-01 | Audit all DSYS backends for monotonic timer implementation and fallback behavior. | P0 | U1 | User/future assistant | Repo access | Backend source files | Backend compatibility report | Search/fetch Win32, POSIX, Cocoa, X11/Wayland, SDL timer code | WORKSTREAM-04 | INFERENCE |
| TASK-02 | Formalize Dominium time-domain doctrine in one canonical document. | P0 | U1 | User/future assistant | Existing docs | Current timing docs/code | Canonical `TIME_ARCHITECTURE.md` or equivalent | Draft from registers and repo citations | WORKSTREAM-04 | INFERENCE |
| TASK-03 | Freeze ACT unit semantics and serialization rules. | P0 | U1 | User/future assistant | `dom_time_core.h`, save/replay schemas | Existing save/replay docs | Clear rule: ACT seconds remain ACT seconds unless versioned migration exists | Find all ACT serialization paths | WORKSTREAM-04 | INFERENCE |
| TASK-04 | Add tests/analyzers banning wall-clock inputs from authority logic. | P1 | U1 | User/future assistant | AuditX/test framework | Existing analyzers and deterministic tests | CI guard against wall-clock authority leakage | Extend existing wallclock smell analyzers | WORKSTREAM-04 | INFERENCE |
| TASK-05 | Define civil/astronomical projection types separately from ACT. | P1 | U2 | User/future assistant | Calendar/lore/ephemeris decisions | Requirements for game display/calendar | Schema/API for user-facing time displays | Draft projection spec | WORKSTREAM-04 | INFERENCE |
| TASK-06 | Verify current external platform facts cited earlier. | P1 | U1 | Future assistant | Web/current docs | glibc, musl, MSVC, Android, POSIX docs | Verification note with current citations | Search primary sources when continuing | WORKSTREAM-01/03 | UNCERTAIN |
| TASK-07 | Preserve this generated package and feed it into a later master Project Spec Book. | P0 | U0 | User | Files created now | Downloaded package | Old-chat report available for aggregation | Save ZIP and/or individual Markdown/YAML files | WORKSTREAM-05 | FACT |

## 20. Constraint Register

| ID | Constraint | Type | Hard/soft | Source / basis | Practical implication | Violation risk | Confidence | Label |
|---|---|---|---|---|---|---|---|---|
| CONSTRAINT-01 | Source scope is this chat only unless labelled PROJECT-CONTEXT. | Reporting | Hard | User preservation prompt fileciteturn30file0 | Do not import unlabelled project memories as facts | Medium | 5 | FACT |
| CONSTRAINT-02 | Authoritative Dominium ordering must not use wall-clock time. | Technical | Hard | Repo docs: deterministic/distributed time policy | Use logical ticks and deterministic keys | High | 5 | FACT |
| CONSTRAINT-03 | Dominium engine core is C89/C90-style with no platform/calendar dependencies in time core. | Technical | Hard-ish | `dom_time_core.h` and project context | Keep time core portable and deterministic | Medium | 4 | FACT/PROJECT-CONTEXT |
| CONSTRAINT-04 | OS/platform APIs should be isolated in DSYS. | Architecture | Hard | Platform runtime docs | Backend-specific timing quirks must not leak upward | High | 4 | FACT |
| CONSTRAINT-05 | Human-readable report must come before machine-readable registers. | Output | Hard | User preservation prompt fileciteturn30file0 | Preserve narrative explanation as primary output | Medium | 5 | FACT |
| CONSTRAINT-06 | Do not treat assistant suggestions as user decisions unless accepted. | Epistemic | Hard | User preservation prompt fileciteturn30file0 | Mark recommendations separately from decisions | High | 5 | FACT |

## 21. User Preference Register

| ID | Preference | Area | Explicit/inferred/uncertain | Strength | Practical implication | Risk if wrong | Label |
|---|---|---|---|---|---|---|---|
| PREF-01 | Human-readable, intuitive, detailed explanation over machine-readable dumps. | Reporting | Explicit | Strong | Lead with prose and rationale | High | FACT |
| PREF-02 | Preserve uncertainty and avoid invented facts. | Epistemic | Explicit | Strong | Use FACT/INFERENCE/UNCERTAIN labels | High | FACT |
| PREF-03 | Source-grounded, audit-ready technical answers. | Style | Explicit/profile | Strong | Cite repo/tool sources and mark verification items | Medium | FACT/PROJECT-CONTEXT |
| PREF-04 | Direct, structured outputs. | Style | Inferred/profile | Medium | Use headings and compact tables where helpful | Low | INFERENCE |
| PREF-05 | Later aggregation into a master spec book is important. | Workflow | Explicit | Strong | Preserve stable IDs and spec-sheet packet | High | FACT |

## 22. Open Questions Register

| ID | Question / issue | Why it matters | Known information | Unknown information | Resolution path | Priority | Related workstream | Label |
|---|---|---|---|---|---|---|---|---|
| QUESTION-01 | Do all Dominium platform backends implement truly monotonic 64-bit timing safely on target legacy OSes? | Backend failures can reintroduce timing bugs | DSYS contract says monotonic when available; null backend is deterministic | Actual timer code for every backend was not audited here | Fetch/audit each backend file | P0 | WORKSTREAM-04 | UNCERTAIN |
| QUESTION-02 | Should Dominium ACT remain seconds permanently or gain subsecond/subtick authority? | Affects save/replay/network compatibility | `dom_act_time_t` currently means ACT seconds | Future simulation precision requirements | Decide before schema/version freeze | P0 | WORKSTREAM-04 | UNCERTAIN |
| QUESTION-03 | What exact civil/astronomical/lore time model will Dominium need? | Display/calendar/lore systems need a projection model | ACT→BST/GCT/CPT conversions are placeholders | Required calendars, epochs, ephemeris precision | Draft projection requirements | P1 | WORKSTREAM-04 | UNCERTAIN |
| QUESTION-04 | Which earlier external facts about glibc/musl/Windows/Android remain current? | Platform advice can go stale | Earlier answer cited current docs at the time | Current state as of future continuation | Verify with primary docs | P1 | WORKSTREAM-01 | UNCERTAIN |
| QUESTION-05 | How should this chat's report be merged with other Dominium reports? | Avoid duplicates/conflicts in master spec book | This package has registers and aggregator packet | Other chat reports may overlap or supersede | Central aggregator review | P1 | WORKSTREAM-05 | UNCERTAIN |

## 23. Artifact Ledger

| ID | Artifact / file / prompt / output | Type | Purpose | Status | Origin | Carry forward? | Notes | Label |
|---|---|---|---|---|---|---|---|---|
| ARTIFACT-01 | Uploaded `Pasted text.txt` preservation prompt | Prompt/file | Defines preservation/export requirements | Used | User upload | Yes | Contains the requested package structure fileciteturn30file0 | FACT |
| ARTIFACT-02 | Earlier 2038 answer | In-chat answer | Explains 2038 risk and 64-bit mitigation | Existing in chat | Assistant | Yes | External facts need verification before formal spec use | FACT/UNCERTAIN |
| ARTIFACT-03 | Earlier int64 precision/range answer | In-chat answer | Explains tick quantum/range tradeoffs | Existing in chat | Assistant | Yes | Useful for representation design | FACT |
| ARTIFACT-04 | Earlier cross-platform time framework answer | In-chat answer | Defines Instant/Duration/Monotonic/Civil split | Existing in chat | Assistant | Yes | Important architecture pattern | FACT |
| ARTIFACT-05 | Dominium repository files inspected via GitHub connector | Source set | Grounds Dominium-specific assessment | Selective, not exhaustive | GitHub connector | Yes | Includes timing, runtime, deterministic ordering, ACT core, cross-shard docs/code | FACT |
| ARTIFACT-06 | `CHAT_LABEL__handoff_package.zip` | Export package | Bundles all generated preservation files | Created by this task | Assistant/tool | Yes | Download/save for aggregation | FACT |

## 24. Rejected / Superseded Options Register

| ID | Option | Status | Reason | Final or tentative? | Reconsider conditions | Related workstream | Label |
|---|---|---|---|---|---|---|---|
| REJECTED-01 | Treat all 32-bit OSes/apps as stopping completely in 2038. | Rejected | Failure depends on time representation/API/data, not bitness alone | Strong | Only if discussing a specific vulnerable stack | WORKSTREAM-01 | INFERENCE |
| REJECTED-02 | Roll back the wall clock as a general 2038 fix. | Rejected | Breaks real-time/security/network correctness; only possible as isolated containment | Strong | Isolated legacy exhibit/device with no external trust needs | WORKSTREAM-01 | INFERENCE |
| REJECTED-03 | Use unsigned 32-bit Unix seconds as the future-proof fix. | Rejected | Moves cliff to 2106 and loses signed/pre-epoch semantics | Strong | Local wrapping counters only | WORKSTREAM-01/02 | INFERENCE |
| REJECTED-04 | Use one universal time type for all purposes. | Rejected | Instants, durations, monotonic time, and civil time have different semantics | Strong | Small toy programs only | WORKSTREAM-03 | INFERENCE |
| REJECTED-05 | Let platform event timestamps influence authoritative Dominium ordering. | Rejected | Violates deterministic replay/distributed ordering doctrine | Strong | Never for authority; acceptable as UI metadata | WORKSTREAM-04 | FACT/INFERENCE |

## 25. Risk Register

| ID | Risk / failure mode | Consequence | Likelihood | Severity | Mitigation | Related workstream | Label |
|---|---|---|---|---|---|---|---|
| RISK-01 | Future code uses `time_t` or host wall-clock time in save/replay/network schemas. | Y2038/staleness/non-deterministic replay bugs | Medium | High | Ban host ABI time in persistent protocols; add tests | WORKSTREAM-04 | INFERENCE |
| RISK-02 | ACT unit is silently reinterpreted. | Save/replay/network incompatibility | Medium | High | Version any unit migration; freeze current ACT semantics | WORKSTREAM-04 | INFERENCE |
| RISK-03 | Platform monotonic timer fallback is not really monotonic on legacy targets. | Pacing glitches, bad telemetry, possible accidental logic bugs | Medium | Medium | Backend-specific audit and capability flags | WORKSTREAM-04 | UNCERTAIN |
| RISK-04 | Future assistant treats recommendations as accepted user decisions. | Spec book overstates certainty | Medium | Medium | Preserve decision status and labels | WORKSTREAM-05 | FACT/INFERENCE |
| RISK-05 | Aggregator merges project-context or stale platform facts as current truth. | Incorrect master spec | Medium | High | Verification queue and source hierarchy | WORKSTREAM-05 | INFERENCE |
| RISK-06 | Civil/calendar projection leaks into authoritative simulation. | Calendar/timezone/lore changes alter outcomes | Low-Medium | High | Keep civil time as derived projection only | WORKSTREAM-04 | INFERENCE |

## 26. Verification Queue

| ID | Item requiring verification | Why verification is needed | Suggested source/type | Priority | Related workstream | Label |
|---|---|---|---|---|---|---|
| VERIFY-01 | Current glibc `_TIME_BITS=64` and 32-bit time guidance | External software docs can change | Official glibc manual/release notes | P1 | WORKSTREAM-01 | UNCERTAIN |
| VERIFY-02 | Current musl time64 behavior | External software docs can change | Official musl docs/release notes | P1 | WORKSTREAM-01 | UNCERTAIN |
| VERIFY-03 | Current MSVC/Windows `time_t`, FILETIME, and QPC guidance | External software docs can change | Microsoft Learn | P1 | WORKSTREAM-01/03 | UNCERTAIN |
| VERIFY-04 | Current Android 32-bit time behavior | External software docs can change | Android bionic docs/source | P1 | WORKSTREAM-01 | UNCERTAIN |
| VERIFY-05 | Dominium repo state after the inspected commit/main snapshot | Repo may have changed | GitHub repository current main | P0 | WORKSTREAM-04 | UNCERTAIN |
| VERIFY-06 | All DSYS backend timer implementations | Selective repo inspection did not cover all backends | Repo source audit | P0 | WORKSTREAM-04 | UNCERTAIN |
| VERIFY-07 | Save/replay/network serialization of `dom_act_time_t` | Persistence determines long-term compatibility | Repo schema/source audit | P0 | WORKSTREAM-04 | UNCERTAIN |

## 27. Chronological Timeline Register

| Sequence | Event / topic | What changed or was decided | Why it mattered | Current relevance | Confidence |
|---|---|---|---|---|---|
| 01 | User asked what happens to 32-bit OSes/apps after 2038. | Framed problem around total breakage, critical functions, clock rollback, unsigned/signed integers. | Established Y2038 resilience as the topic. | Basis for later architecture decisions. | 5 |
| 02 | Assistant reframed 2038 as a time-representation problem. | Distinguished signed 32-bit Unix time from 32-bit hardware. | Prevented incorrect conclusion that all 32-bit systems die. | Guides audit focus. | 4 |
| 03 | User narrowed range requirement to about ±10,000 years. | Shifted from unlimited time to range/precision tradeoff. | Made representation design quantifiable. | Supports scalar vs split timestamp choices. | 5 |
| 04 | Assistant recommended 100 ns/1 µs scalar or int64 seconds+nanos split. | Established practical representation options. | Useful for project schemas and cross-platform APIs. | Candidate spec input. | 4 |
| 05 | User asked for most-compatible architecture for software longevity. | Shifted from numeric representation to framework/design doctrine. | Led to separated time domains. | General architecture rule. | 5 |
| 06 | Assistant proposed Instant/Duration/Monotonic/Civil split. | Separated absolute time, elapsed time, and human time. | Avoids Y2K/Y2038/timezone-style bugs. | Core carry-forward pattern. | 4 |
| 07 | User asked how it applies to Dominium and requested docs/code/repo reading. | Moved from abstract advice to project-specific audit. | Required repo-grounded answer. | Central workstream. | 5 |
| 08 | Assistant inspected selected Dominium docs/code via GitHub connector. | Found timing, runtime, ACT, deterministic ordering, cross-shard, observer-clock files. | Grounded Dominium assessment. | Strongest evidence source for this chat. | 4 |
| 09 | Assistant concluded Dominium is mostly architecturally correct but needs edge hardening. | Identified ACT/DSYS/observer/civil split and backend/serialization risks. | Becomes project guidance. | High. | 4 |
| 10 | User uploaded preservation prompt. | Current task became maximum-fidelity report/export package. | Ensures this chat can be reused/aggregated. | Immediate deliverable. | 5 |

## 28. Spec Book Contribution Register

| Spec-book area | Contribution from this chat | Source IDs | Should become requirement/context/open issue? | Confidence | Notes |
|---|---|---|---|---|---|
| Time Architecture | Separate ACT authority, DSYS runtime, observer clocks, civil projection | DECISION-05..08 | Requirement | 4 | Central contribution |
| Determinism and Replay | No wall-clock authority; deterministic ordering keys | DECISION-05, CONSTRAINT-02 | Requirement | 5 | Already aligned with repo docs |
| Platform Runtime | DSYS owns monotonic time and sleep; audit backends | DECISION-06, TASK-01 | Requirement/Open issue | 4 | Needs backend verification |
| Serialization/Compatibility | Avoid host ABI time; freeze ACT units | TASK-03, RISK-01/02 | Requirement/Open issue | 4 | Needs repo-wide audit |
| Civil/Astronomical Time | Add as projection layer only | DECISION-08, QUESTION-03 | Open issue/Context | 3 | Design not yet specified |
| Preservation/Aggregation | Use human-readable report plus registers/spec sheet | WORKSTREAM-05 | Context/Process | 5 | Useful for master spec workflow |
