# Aggregator Packet — Dominium Chronology & Celestial Systems

## 1. Packet Metadata

- Chat label: Dominium Chronology & Celestial Systems
- Date anchor: 2026-05-27 Australia/Melbourne
- Source scope: THIS CHAT ONLY; PROJECT-CONTEXT appears only where sourced from visible project/system context or user references to other Dominium chats.
- Coverage: full visible chat context plus prior context transfer packet
- Confidence: 4/5
- Staleness risk: medium
- Merge priority: high
- Main limitations: no direct access to The Game/Plan G codebase; astronomy/constants require verification; some calendar names/leap rules tentative.

## 2. Ultra-Condensed Carry-Forward Capsule

[FACT] This chat developed a substantial design subsystem for the Dominium Game project: a multi-scale chronology, calendar, celestial-content, and diegetic knowledge architecture intended to integrate with The Game / Plan G and eventually feed a Codex implementation prompt. It began with the user asking what celestial bodies and systems should be included in a logical universe simulation without too much redundancy for gameplay. The work expanded into a scale hierarchy: planetary Earth, the Sol system, the Milky Way, and the universe. Sol was explicitly prioritized for maximum detail because the user stated most playtime will be spent there. The resulting celestial doctrine is that gameplay-relevant bodies/sites should be explicit, repetitive content should be procedural/statistical, and non-impactful content should be excluded.

[FACT] The chat then shifted into timekeeping. The core doctrine became: time is real and continuous; calendars are interfaces. Atomic Continuous Time (ACT) is the authoritative monotonic simulation time. Barycentric Sol Time (BST), Galactic Coordinate Time (GCT), and Cosmological Proper Time (CPT) represent larger-scale coordinate frames. Proper time is derived for clocks/biology and never becomes authoritative calendar time. Leap seconds are display-only and absent from core simulation. Calendars must be stateless reversible renderers, not physics drivers.

[FACT] Earth calendar support includes Gregorian, Julian, Islamic, Hebrew, Chinese, Persian/Solar Hijri, Holocene, Metric/French Revolutionary, and a custom Perfect Earth Calendar. The user later gave the final naming structure for the Perfect Earth Calendar: weekdays use Monday through Sunday; the year begins in March; the 13 months are March, April, May, June, July, August, September, October, November, December, Undecember, January, February. The calendar has 13 months of 28 days, with Year Day and Leap Day appended after February. The user explicitly wanted to avoid January 0. Intercalary days are canonically outside week/month; compatibility projection may map them to February 29 and February 30, but this remains a renderer policy, not the canonical form.

[FACT] Additional systems were defined for Luna, Mercury, Venus, Mars, Jovian moons, Saturnian moons, Uranian moons, Neptunian moons, Pluto/TNOs, Sol-wide, galactic, and universal scales. These include both scientific clocks and engineered calendars. Many names and exact leap rules for non-Earth systems are assistant-generated and require user review before becoming final.

[FACT] The user added crucial gameplay constraints: each world/universe instance can start at a different date/time. By default, a world starts from Gregorian January 1, 2000 AD, while the player spawns at local sunrise on the body/time zone/solar context where they appear. At the beginning, the player has no clocks, calendars, date, or time HUD, because the HUD is diegetic and the player lacks timekeeping devices. Players can define their own time/date systems or adopt provided calendars. Organizations, regions, jurisdictions, and individuals may designate standards.

[FACT] The final architecture recommendation was modular: TimeCore for ACT/frames, Chronology for calendar renderers, NameSets for labels, TimeStandards for social/legal standards, KnowledgeCapabilities for fog-of-war/HUD gating, Ephemeris/astronomy for local solar state and sunrise, and Recurrence for physical/civil/astronomical scheduling. The next chat must not assume implementation details from this chat; it must inspect the actual Plan G/The Game context before generating Codex implementation instructions.

The highest-value merge points are: ACT as authoritative simulation time; calendars as pure renderers; no leap seconds in core; proper time derived only; user-defined HPC-E; default Jan 1 2000 Gregorian anchor plus local sunrise spawn; no initial time/date HUD; player-defined calendars; governance/jurisdiction/organization/person standards; Sol high-fidelity celestial scope; and explicit/procedural/parametric celestial classification. These should merge into any broader Project Spec Book as requirements or design doctrine, not as casual notes. Assistant-generated constants, astronomy lists, and non-Earth names need verification before becoming formal data.

## 3. Top Carry-Forward Items

| Priority | Item | Type | Related ID | Why it matters | Label | Confidence |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | ACT authoritative; calendars pure renderers | core doctrine | DECISION-04/06 | Protects determinism and causality | FACT | high |
| 2 | HPC-E final structure and month order | calendar spec | DECISION-10/11/12 | User-defined calendar must be preserved | FACT | high |
| 3 | Default Jan 1 2000 Gregorian + local sunrise spawn | world start | DECISION-13/14 | Initial conditions and player experience | FACT | high |
| 4 | No starting time/date HUD | UI/knowledge | DECISION-15 | Diegetic VR/fog-of-war premise | FACT | high |
| 5 | Standards designated by orgs/jurisdictions/individuals | governance | DECISION-17 | Integrates time with law/social systems | FACT | high |
| 6 | Sol system high-detail explicit scope | celestial content | DECISION-02 | Most playtime occurs there | FACT | high |
| 7 | Celestial explicit/procedural/parametric doctrine | content architecture | DECISION-03 | Prevents scope explosion | INFERENCE | medium |
| 8 | Versioned constants/ephemerides/calendar models | robustness | DECISION-21 | Prevents save drift | INFERENCE | medium-high |
| 9 | Verify assistant-generated astronomy/constants | verification | VERIFY-01..04 | Prevents false data in spec | UNCERTAIN / UNVERIFIED | high |
| 10 | Do not assume codebase/module claims | process | QUESTION-01/02 | Avoid bad Codex prompt | UNCERTAIN / UNVERIFIED | high |

## 4. Workstream Summaries

### WORKSTREAM-01: Multi-scale celestial content architecture
- Objective: Define celestial bodies, structures, regions, systems, and sites for gameplay across Earth, Sol, Milky Way, and universe scales without redundant simulation.
- Current state: Scope and classification were defined conceptually: explicit, procedural, or parametric; Sol system is highest fidelity; Milky Way has a real-system backbone plus procedural expansion; universe is mostly parametric.
- Desired end state: A data-driven celestial registry integrated with simulation, navigation, gameplay mechanics, time, governance, and knowledge/fog-of-war systems.
- Priority: high
- Decisions: DECISION-01, DECISION-02, DECISION-03
- Tasks: TASK-02, TASK-18
- Constraints: CONSTRAINT-11, CONSTRAINT-12
- Artifacts: ARTIFACT-01, ARTIFACT-02, ARTIFACT-03, ARTIFACT-04, ARTIFACT-16
- Risks: RISK-07, RISK-08
- Open questions: QUESTION-07, QUESTION-08, QUESTION-09
- Next action: Verify celestial lists, then convert into data schemas with fidelity classes.

### WORKSTREAM-02: Authoritative time core and coordinate frames
- Objective: Define simulation-authoritative time layers and frame transforms from local gameplay to cosmological timescales.
- Current state: ACT, BST, GCT, CPT, CDC, proper-time, leap-second policy, and scale transition doctrine are conceptually defined.
- Desired end state: A deterministic engine-level time core storing ACT plus frame/version metadata, with frame transforms and proper-time utilities.
- Priority: high
- Decisions: DECISION-04, DECISION-05, DECISION-06, DECISION-07, DECISION-08, DECISION-21, DECISION-22
- Tasks: TASK-06, TASK-11, TASK-17
- Constraints: CONSTRAINT-01, CONSTRAINT-02, CONSTRAINT-03, CONSTRAINT-04, CONSTRAINT-05, CONSTRAINT-06
- Artifacts: ARTIFACT-05, ARTIFACT-11, ARTIFACT-12
- Risks: RISK-02, RISK-03, RISK-11
- Open questions: QUESTION-03, QUESTION-16
- Next action: Define core timestamp schema and frame transform interfaces after inspecting existing engine architecture.

### WORKSTREAM-03: Earth calendars and Perfect Earth Calendar (HPC-E)
- Objective: Support existing widely used Earth calendars and define the custom Perfect Earth Calendar with user-specified names and intercalary rules.
- Current state: Existing calendar set and final HPC-E naming/structure are defined; exact HPC-E leap rule is still pending.
- Desired end state: Calendar plugins/renderers, NameSets, strict and compatibility modes, and test vectors.
- Priority: high
- Decisions: DECISION-09, DECISION-10, DECISION-11, DECISION-12
- Tasks: TASK-03, TASK-07, TASK-13, TASK-14
- Constraints: CONSTRAINT-07, CONSTRAINT-08, CONSTRAINT-14, CONSTRAINT-15
- Artifacts: ARTIFACT-06, ARTIFACT-07, ARTIFACT-08, ARTIFACT-11
- Risks: RISK-05
- Open questions: QUESTION-05, QUESTION-06
- Next action: Finalize HPC-E leap rule, then implement strict and compatibility renderers.

### WORKSTREAM-04: Planetary, moon, Pluto, and TNO calendars
- Objective: Define local scientific and civil time systems for Mars, Venus, Mercury, major moons, Pluto, and TNO/deep-time contexts.
- Current state: Many assistant-proposed calendar structures and names exist; some are accepted design intent through continuation, but final naming/leap details remain uncertain.
- Desired end state: A calendar registry for body/system-specific scientific clocks, civil calendars, engineered calendars, and name sets.
- Priority: medium-high
- Decisions: DECISION-18, DECISION-19
- Tasks: TASK-04, TASK-05, TASK-07, TASK-13
- Constraints: CONSTRAINT-02, CONSTRAINT-09
- Artifacts: ARTIFACT-09, ARTIFACT-10, ARTIFACT-11, ARTIFACT-12
- Risks: RISK-09, RISK-10
- Open questions: QUESTION-10, QUESTION-11, QUESTION-12
- Next action: Review all assistant-proposed names and classify non-7-day cycles as work cycles or weeks.

### WORKSTREAM-05: Sol-wide, galactic, and universal epoch systems
- Objective: Define civil/archival time frameworks above the planetary scale.
- Current state: SCT/SEC, GalCT/GEC, UCT/UEF are defined conceptually; acronym collision risk remains.
- Desired end state: Scale-aware renderer/data definitions with no false human calendar semantics at galactic/universal scale.
- Priority: medium-high
- Decisions: DECISION-20
- Tasks: TASK-04, TASK-07, TASK-13
- Constraints: CONSTRAINT-10, CONSTRAINT-13
- Artifacts: ARTIFACT-10, ARTIFACT-11, ARTIFACT-12
- Risks: RISK-06, RISK-13
- Open questions: QUESTION-06, QUESTION-13
- Next action: Assign unique internal IDs and keep human-readable aliases separate.

### WORKSTREAM-06: World instantiation and local sunrise start
- Objective: Define how each world/universe instance starts and how the player’s spawn time is selected.
- Current state: User-specified default: Gregorian Jan 1, 2000 AD; time starts at local sunrise on the spawn planet/time zone/solar context; fallback rules were proposed but need formalization.
- Desired end state: World-instance initialization schema and deterministic sunrise/fallback algorithm.
- Priority: high
- Decisions: DECISION-13, DECISION-14
- Tasks: TASK-10, TASK-11
- Constraints: CONSTRAINT-16, CONSTRAINT-17
- Artifacts: ARTIFACT-13
- Risks: RISK-12
- Open questions: QUESTION-03, QUESTION-04
- Next action: Define deterministic sunrise/fallback function with exact solar elevation threshold and time-scale mapping.

### WORKSTREAM-07: Diegetic HUD, time knowledge, and fog-of-war
- Objective: Ensure time/date knowledge is unavailable until obtained through devices, calendars, documents, astronomy, networks, or organizations.
- Current state: Doctrine defined; capability schema and device models still pending.
- Desired end state: Capability-gated diegetic HUD and time-display system integrated with fog-of-war.
- Priority: high
- Decisions: DECISION-15
- Tasks: TASK-09, TASK-20
- Constraints: CONSTRAINT-18, CONSTRAINT-19
- Artifacts: ARTIFACT-13, ARTIFACT-14
- Risks: RISK-04, RISK-15
- Open questions: QUESTION-14, QUESTION-15
- Next action: Define KnowledgeCapability IDs and map devices/organizations to capabilities.

### WORKSTREAM-08: Governance, jurisdictions, organizations, and time standards
- Objective: Model time/calendar standards as social/legal data objects designated by regions, jurisdictions, organizations, and individuals.
- Current state: User requirement exists; assistant proposed TimeStandard object and resolution order.
- Desired end state: TimeStandard schema integrated with governance, contracts, scheduling, law, and individual preferences.
- Priority: high
- Decisions: DECISION-16, DECISION-17, DECISION-18
- Tasks: TASK-08, TASK-12, TASK-20
- Constraints: CONSTRAINT-20
- Artifacts: ARTIFACT-13, ARTIFACT-14, ARTIFACT-15
- Risks: RISK-14
- Open questions: QUESTION-17
- Next action: Inspect existing governance model and define TimeStandard as a data object.

### WORKSTREAM-09: Modularity, extensibility, reliability, and integration architecture
- Objective: Refactor the full design into modular layers suitable for the existing game/engine architecture.
- Current state: Architecture principles and module boundaries were proposed; exact implementation depends on actual codebase/context.
- Desired end state: A validated integration design and Codex-ready phased implementation prompt.
- Priority: high
- Decisions: DECISION-21, DECISION-22
- Tasks: TASK-01, TASK-06, TASK-07, TASK-08, TASK-09, TASK-11, TASK-12, TASK-13, TASK-14, TASK-15, TASK-18
- Constraints: CONSTRAINT-21, CONSTRAINT-22, CONSTRAINT-23
- Artifacts: ARTIFACT-14, ARTIFACT-15
- Risks: RISK-01, RISK-11
- Open questions: QUESTION-01, QUESTION-02
- Next action: Use this package in The Game chat; inspect actual project context; produce implementation prompt.

### WORKSTREAM-10: Prompt handoff and report packaging
- Objective: Preserve the decisions and convert the chat into reusable prompts/reports for future chats and Codex implementation.
- Current state: Context transfer packet exists; this current package creates downloadable report files and a ZIP.
- Desired end state: Reusable per-chat package suitable for aggregation into a future full Project Spec Book.
- Priority: high
- Decisions: DECISION-23
- Tasks: TASK-16, TASK-21
- Constraints: CONSTRAINT-24, CONSTRAINT-25
- Artifacts: ARTIFACT-15, ARTIFACT-17, ARTIFACT-18
- Risks: RISK-16, RISK-17
- Open questions: none recorded
- Next action: Download and store package; use Section 15 bootstrap prompt in the next chat.



## 5. Registers for Merge

### Decision Register
| ID | Decision | Status | Evidence / basis | Rationale | Implications | Related workstream | Confidence | Label |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| DECISION-01 | Game operates across Earth, Sol, Milky Way, and universe scales. | locked | User explicitly listed the four gameplay scales. | Scale determines content and time system architecture. | Requires hierarchical fidelity and time models. | WORKSTREAM-01 | high | FACT |
| DECISION-02 | Sol system receives maximum explicit detail. | locked | User said most playtime will be in Sol and to pull out all the stops. | Sol is the main play space. | Sol bodies/sites must be explicit and rich. | WORKSTREAM-01 | high | FACT |
| DECISION-03 | Celestial content uses explicit/procedural/parametric classification. | accepted design principle | Assistant proposed; carried forward in later scope lists. | Avoids simulation redundancy. | Data schemas need fidelity tags. | WORKSTREAM-01 | medium | INFERENCE |
| DECISION-04 | Atomic Continuous Time (ACT) is authoritative simulation time. | locked | Repeated doctrine in calendar/time specs. | Monotonic determinism. | Save files store ACT, not dates. | WORKSTREAM-02 | high | FACT |
| DECISION-05 | Use coordinate frames BST, GCT, and CPT above ACT. | accepted design principle | Defined in Sol/Galactic/Universal time discussions. | Supports scale transitions. | Need versioned transforms. | WORKSTREAM-02 | medium-high | FACT |
| DECISION-06 | Calendars are pure renderers and never affect physics. | locked | Repeated doctrine: calendars are interfaces. | Prevents causality corruption. | Calendar plugins must be stateless/reversible. | WORKSTREAM-02 | high | FACT |
| DECISION-07 | Leap seconds are display-only and absent from core time. | locked | Leap-second discussion. | Avoids discontinuities. | UTC renderer may use external leap tables. | WORKSTREAM-02 | high | FACT |
| DECISION-08 | Proper time is derived only; calendars render coordinate time. | locked | Relativity discussion. | Avoids frame-dependent civil authority. | Proper time used for clocks/aging, not authoritative now. | WORKSTREAM-02 | high | FACT |
| DECISION-09 | Earth supports Gregorian, Julian, Islamic, Hebrew, Chinese, Persian, Holocene, Metric/French Revolutionary calendars. | locked | User explicitly listed them. | Cultural/historical coverage. | Need plugins/renderers for each. | WORKSTREAM-03 | high | FACT |
| DECISION-10 | Perfect Earth Calendar has 13 months × 28 days and Monday–Sunday weeks. | locked | User specified days and final calendar direction; assistant formalized. | Perpetual regularity with familiar names. | HPC-E implementation invariant. | WORKSTREAM-03 | high | FACT |
| DECISION-11 | Perfect Earth Calendar month order is March through February with Undecember as 11th month. | locked | User explicitly specified March start, December 10th, 11th historically proposed, January 12th, February 13th. | Seasonal start while preserving English Gregorian names. | HPC-E month array fixed. | WORKSTREAM-03 | high | FACT |
| DECISION-12 | HPC-E Year Day and Leap Day are appended after February; canonical mode is undated and compatibility mode may use Feb 29/30. | mostly accepted; compatibility is assistant recommendation | User required February sink and no January 0; assistant proposed strict+compat mode. | Preserves perpetual weeks while supporting software compatibility. | Need intercalary tokens and optional projection. | WORKSTREAM-03 | medium-high | FACT / INFERENCE |
| DECISION-13 | Default world date anchor is Gregorian January 1, 2000 AD. | locked | User explicit. | Known reference start point. | Exact time scale still pending. | WORKSTREAM-06 | high | FACT |
| DECISION-14 | Player spawn time is local sunrise at spawn location. | locked | User explicit. | Embodied local start rather than abstract timestamp. | Requires deterministic sunrise solver and fallbacks. | WORKSTREAM-06 | high | FACT |
| DECISION-15 | Player starts with no clock/calendar/date HUD. | locked | User explicit. | Diegetic VR realism and knowledge progression. | UI must be capability-gated. | WORKSTREAM-07 | high | FACT |
| DECISION-16 | Players can define custom timekeeping/date systems or choose provided systems. | locked | User explicit. | Player agency/culture simulation. | Need safe custom calendar schema. | WORKSTREAM-08 | high | FACT |
| DECISION-17 | Organizations, regions, jurisdictions, and individuals may designate standard systems. | locked | User explicit. | Governance and social standard gameplay. | Need TimeStandard data object. | WORKSTREAM-08 | high | FACT |
| DECISION-18 | TimeStandard resolution order proposed: explicit context, organization, jurisdiction, personal, fallback. | proposal | Assistant proposed during integration. | Provides deterministic conflict resolution. | Must be checked against real governance systems. | WORKSTREAM-08 | medium | INFERENCE |
| DECISION-19 | Gas giants and the Sun have no civil calendars; moons/habitats may. | accepted design principle | Assistant proposed repeatedly; user continued building on it. | No lived surface; only scientific/environmental clocks. | Use local/moon/habitat standards. | WORKSTREAM-04 | medium | INFERENCE |
| DECISION-20 | Galactic and universal scales use epoch/duration frameworks rather than normal calendars. | accepted design principle | Milky Way/universe extension discussion. | No meaningful local days/months at those scales. | GEC/UEF numeric only. | WORKSTREAM-05 | medium-high | FACT |
| DECISION-21 | Constants, ephemerides, time models, and calendar plugins must be versioned/pinned. | accepted design principle | Modularity discussion. | Prevent patch drift and save corruption. | World saves pin versions. | WORKSTREAM-09 | medium-high | INFERENCE |
| DECISION-22 | Save files persist ACT/frame/version/knowledge state, not rendered date strings. | accepted design principle | Serialization policy from assistant; consistent with core doctrine. | Round-trip and patch safety. | Requires derived rendering on load. | WORKSTREAM-09 | medium-high | INFERENCE |
| DECISION-23 | The old chat must be converted into downloadable per-chat report package. | locked | Current user request. | Future aggregation and reuse. | This response must create files and ZIP if possible. | WORKSTREAM-10 | high | FACT |

### Task Register
| ID | Task | Priority | Urgency | Owner | Dependencies | Inputs needed | Expected output | Recommended next step | Related workstream | Label |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| TASK-01 | Inspect actual Plan G/The Game architecture before implementation planning. | high | immediate | new assistant | Access to project context | Actual chat/codebase/design docs | Validated integration constraints | Open The Game/Plan G context and compare with this package. | WORKSTREAM-09 | FACT |
| TASK-02 | Verify celestial body/system lists against authoritative astronomy sources. | high | near-term | new assistant/user | Canonical lists from this chat | Astronomical catalogs/sources | Corrected celestial registry | Flag and repair likely errors such as SN 1987A classification. | WORKSTREAM-01 | FACT |
| TASK-03 | Finalize HPC-E leap rule. | high | near-term | user/new assistant | HPC-E structure | Tropical-year correction options | Exact leap algorithm | Choose Gregorian-like rule or drift accumulator. | WORKSTREAM-03 | FACT |
| TASK-04 | Resolve acronym collisions and internal calendar IDs. | medium | near-term | new assistant | Calendar inventory | Naming/ID policy | Unique registry IDs | Rename internal IDs such as SOL_SCT vs SAT_CT. | WORKSTREAM-05, WORKSTREAM-04 | FACT |
| TASK-05 | Normalize week vs work-cycle terminology. | medium | near-term | user/new assistant | Planetary calendar list | UX/naming policy | Final cycle terminology | Decide if non-7-day cycles are weeks or work cycles. | WORKSTREAM-04 | FACT |
| TASK-06 | Define TimeCore schema and API. | high | near-term | Codex/new assistant | Existing engine architecture | ACT/frame/version requirements | Engine-level time core design | Design canonical timestamp record. | WORKSTREAM-02, WORKSTREAM-09 | INFERENCE |
| TASK-07 | Define calendar renderer/plugin interface. | high | near-term | Codex/new assistant | Calendar inventory | Render/parse/intercalary needs | Calendar plugin API | Specify stateless reversible interfaces. | WORKSTREAM-03, WORKSTREAM-04, WORKSTREAM-05 | INFERENCE |
| TASK-08 | Define TimeStandard schema. | high | near-term | new assistant/Codex | Governance architecture | Org/jurisdiction requirements | TimeStandard data object | Bind calendar, clock, frame, policy, NameSet. | WORKSTREAM-08 | FACT / INFERENCE |
| TASK-09 | Define KnowledgeCapability schema for time/date access. | high | near-term | new assistant/Codex | Fog-of-war/knowledge systems | Device and standard needs | Capability graph | Map devices/docs/orgs to capabilities. | WORKSTREAM-07 | FACT / INFERENCE |
| TASK-10 | Define deterministic sunrise/fallback algorithm. | high | near-term | new assistant/Codex | Ephemeris/astronomy model | Spawn body/location/context | Sunrise solver spec | Define solar elevation threshold and fallbacks. | WORKSTREAM-06 | FACT |
| TASK-11 | Define serialization/save policy. | high | near-term | Codex/new assistant | Save system | ACT/frame/version doctrine | Save schema | Prevent rendered dates from being persisted. | WORKSTREAM-02, WORKSTREAM-09 | INFERENCE |
| TASK-12 | Build recurrence/scheduling model. | medium | medium | Codex/new assistant | Calendar plugins, TimeStandards | Scheduling requirements | Physical/civil/astronomical recurrence engine | Define intercalary inclusion policies. | WORKSTREAM-08, WORKSTREAM-09 | INFERENCE |
| TASK-13 | Separate NameSets/localization from calendar algorithms. | medium | medium | Codex/new assistant | Calendar names | Localization needs | NameSet registry | Implement inheritance (e.g. HPC-E weekdays). | WORKSTREAM-03, WORKSTREAM-04, WORKSTREAM-05 | INFERENCE |
| TASK-14 | Create tests and golden vectors. | high | medium | Codex/new assistant | Exact algorithms | Calendar/time definitions | Test suite | Prioritize round-trip, intercalary, serialization, sunrise determinism. | WORKSTREAM-03, WORKSTREAM-09 | INFERENCE |
| TASK-15 | Write project docs for time/calendar systems. | high | medium | Codex/new assistant | Final schemas | Report package | Documentation set | Produce TIMECORE, CALENDARS, STANDARDS, TEST_VECTORS docs. | WORKSTREAM-09 | INFERENCE |
| TASK-16 | Generate Codex-ready implementation prompt in The Game chat. | high | near-term | The Game chat/new assistant | This package + actual project context | Architecture verification | Phased Codex prompt | Use this package as source material. | WORKSTREAM-10 | FACT |
| TASK-17 | Verify constants/equations before coding. | high | near-term | new assistant/Codex | Suffix prompt constants | NASA/JPL/IAU/IERS or relevant sources | Verified constants pack | Do not hardcode assistant-provided numbers blindly. | WORKSTREAM-02 | FACT |
| TASK-18 | Decide phase-one implementation scope. | high | near-term | user/new assistant | Project capacity | All workstreams | Phased roadmap | Implement core/HPC-E/knowledge first or similar. | WORKSTREAM-09, WORKSTREAM-01 | INFERENCE |
| TASK-19 | Define custom calendar/player-created clock schema. | medium | medium | new assistant/Codex | User requirement | Validation rules | Safe custom calendar system | Require reversibility and ACT mapping. | WORKSTREAM-08 | FACT / INFERENCE |
| TASK-20 | Integrate with governance, jurisdiction, knowledge, and fog-of-war systems. | high | near-term | new assistant/Codex | Actual project systems | Existing data models | Integration plan | Do after inspecting Plan G context. | WORKSTREAM-07, WORKSTREAM-08, WORKSTREAM-09 | FACT |
| TASK-21 | Download and archive this report package. | high | immediate | user | Generated files | Download links | Stored per-chat package | Save ZIP and Markdown/YAML files together. | WORKSTREAM-10 | FACT |

### Constraint Register
| ID | Constraint | Type | Hard/soft | Source / basis | Practical implication | Violation risk | Confidence | Label |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| CONSTRAINT-01 | Core time must be continuous and monotonic. | technical | hard | Repeated doctrine | Use ACT as authoritative now. | High | high | FACT |
| CONSTRAINT-02 | Calendars must never affect physics. | technical/design | hard | Repeated doctrine | Calendar code only renders/parses. | High | high | FACT |
| CONSTRAINT-03 | Leap seconds must not enter core simulation time. | technical | hard | Leap-second discussion | UTC rendering only; external table. | Medium | high | FACT |
| CONSTRAINT-04 | Proper time must not become authoritative civil/calendar time. | technical | hard | Relativity discussion | Proper time used only for clocks/aging. | Medium | high | FACT |
| CONSTRAINT-05 | Save files must not persist rendered dates or names as truth. | serialization | hard | Serialization policy | Persist ACT/frame/version IDs. | High | medium-high | INFERENCE |
| CONSTRAINT-06 | Constants and ephemerides must be versioned and pinned per world. | technical | hard | Modularity discussion | Patch updates cannot alter old saves silently. | High | medium-high | INFERENCE |
| CONSTRAINT-07 | HPC-E months must remain 28 days. | calendar | hard | User-defined calendar | No normal month variation. | High | high | FACT |
| CONSTRAINT-08 | HPC-E weekdays Monday–Sunday must not drift. | calendar | hard | User-defined calendar | Intercalary days outside week. | High | high | FACT |
| CONSTRAINT-09 | Intercalary days are explicit tokens canonically. | calendar | hard | Intercalary compatibility discussion | Do not treat as normal dates except compatibility projection. | Medium | medium-high | FACT / INFERENCE |
| CONSTRAINT-10 | Galactic/universal frameworks must avoid false local calendar semantics. | design | hard | Scale discussion | Use duration/epochs only. | Medium | medium-high | FACT |
| CONSTRAINT-11 | Sol system must be high fidelity. | content | hard | User explicitly requested | Full explicit Sol scope. | Medium | high | FACT |
| CONSTRAINT-12 | Avoid redundant explicit simulation. | performance/design | hard | Initial user request | Use explicit/procedural/parametric classes. | High | high | FACT |
| CONSTRAINT-13 | Gas giants and Sun do not have planet-surface civil calendars. | content/design | soft-hard | Assistant proposal carried forward | Use scientific/environmental clocks only. | Medium | medium | INFERENCE |
| CONSTRAINT-14 | No January 0 designation. | calendar/naming | hard | User explicit | Intercalary sink after February. | High | high | FACT |
| CONSTRAINT-15 | Existing English weekday/month names used for HPC-E as specified. | calendar/naming | hard | User explicit | NameSet must preserve exact order. | Medium | high | FACT |
| CONSTRAINT-16 | Each world/universe can instantiate at different date/time. | world generation | hard | User explicit | World instance has independent epoch. | Medium | high | FACT |
| CONSTRAINT-17 | Default spawn occurs at local sunrise where possible. | world generation | hard | User explicit | Requires deterministic astronomy query. | Medium | high | FACT |
| CONSTRAINT-18 | No initial time/date HUD without device/knowledge. | UI/gameplay | hard | User explicit | Capability-gated diegetic HUD. | High | high | FACT |
| CONSTRAINT-19 | HUD should be diegetic and VR-friendly. | UI/gameplay | hard | User explicit | Use in-world devices/displays. | Medium | high | FACT |
| CONSTRAINT-20 | Organizations, regions, jurisdictions, and individuals may designate standards. | governance | hard | User explicit | TimeStandard data objects. | Medium | high | FACT |
| CONSTRAINT-21 | Do not assume codebase details from this chat. | process | hard | User said The Game chat will handle implementation; assistant admitted limited access | New chat must inspect actual project. | High | high | FACT |
| CONSTRAINT-22 | Unknown data should yield UNKNOWN, not fabricated output. | robustness | hard | Modularity recommendation | Prevents false UI/gameplay facts. | Medium | medium-high | INFERENCE |
| CONSTRAINT-23 | Implementation should be modular, extensible, reliable, and robust. | architecture | hard | User explicit | Plugin/data-driven design. | Medium | high | FACT |
| CONSTRAINT-24 | This report must cover this chat only. | reporting | hard | Current user request | Do not summarize whole project. | Medium | high | FACT |
| CONSTRAINT-25 | Important items must be labelled FACT/INFERENCE/UNCERTAIN/PROJECT-CONTEXT. | reporting | hard | Current user request | Preserve reliability states. | Medium | high | FACT |

### Open Questions Register
| ID | Question / issue | Why it matters | Known information | Unknown information | What would resolve it | Priority | Related workstream | Label |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| QUESTION-01 | What is the actual Plan G/The Game architecture? | Implementation must align with real systems. | User referenced it; this chat lacks access. | Codebase/chats/module layout. | Inspect project context. | high | WORKSTREAM-09 | UNCERTAIN / UNVERIFIED |
| QUESTION-02 | Are Domino C89 / Dominium C++98 constraints real? | Language/API decisions depend on it. | Assistant previously claimed this. | User did not confirm in visible chat. | Verify project docs/code. | high | WORKSTREAM-09 | UNCERTAIN / UNVERIFIED |
| QUESTION-03 | What exact time scale maps Jan 1 2000 to ACT? | Start timestamp determinism. | User specified Gregorian Jan 1 2000 AD. | UTC/TAI/TT/game-defined noon/midnight mapping. | Choose and document epoch. | high | WORKSTREAM-06, WORKSTREAM-02 | UNCERTAIN |
| QUESTION-04 | What exact definition of sunrise is used? | Spawn time and astronomical recurrence need consistency. | User wants local sunrise; assistant proposed solar elevation crossing 0 degrees. | Refraction, terrain horizon, solar radius, atmosphere, fallback priority. | Define deterministic algorithm. | high | WORKSTREAM-06 | UNCERTAIN |
| QUESTION-05 | What is the exact HPC-E leap rule? | Leap Day placement requires cadence. | Year Day/Leap Day exist; drift-based idea discussed. | Exact algorithm. | User/design decision. | high | WORKSTREAM-03 | UNCERTAIN |
| QUESTION-06 | Should compatibility projection Feb 29/Feb 30 be default? | External API/date-string behavior. | Assistant proposed optional compatibility. | Default mode/policy not user-confirmed. | User or implementation decision. | medium | WORKSTREAM-03 | UNCERTAIN |
| QUESTION-07 | How many real Milky Way systems should be explicit? | Data scope/performance. | User wanted dozens to hundreds; assistant listed ~50. | Final count and criteria. | Design/data review. | medium | WORKSTREAM-01 | UNCERTAIN |
| QUESTION-08 | Which assistant-listed celestial systems are scientifically correct? | Avoid hardcoding false astronomical data. | Initial list exists. | Verification status. | Authoritative catalogs/sources. | high | WORKSTREAM-01 | UNCERTAIN / UNVERIFIED |
| QUESTION-09 | Which exoplanets/sites per Milky Way system are explicit? | System detail level. | Some system contents listed; incomplete. | Final bodies/sites for each system. | Data design review. | medium | WORKSTREAM-01 | UNCERTAIN |
| QUESTION-10 | Which planetary/moon calendar names are final? | Avoid freezing assistant brainstorm names. | Many names proposed. | User did not confirm each. | User review/naming policy. | medium | WORKSTREAM-04 | UNCERTAIN |
| QUESTION-11 | Should non-7-day cycles be weeks or work cycles? | UX and naming consistency. | Some calendars had 5/8/11-day cycles. | Final terminology. | User/design decision. | medium | WORKSTREAM-04 | UNCERTAIN |
| QUESTION-12 | Do engineered mythological names remain despite no-mythology rule? | Naming consistency. | Names such as Arean/Aphrodite appeared. | Whether user wants them. | User review. | medium | WORKSTREAM-04 | UNCERTAIN |
| QUESTION-13 | How to resolve SCT acronym collision? | Avoid registry/serialization bugs. | Sol Coordinated Time and Saturn Coordinated Time both had SCT in assistant output. | Final unique IDs. | Registry design. | medium | WORKSTREAM-05 | UNCERTAIN |
| QUESTION-14 | What is the exact time-knowledge capability list? | HUD gating and fog-of-war. | Concept defined. | Capability IDs and unlock logic. | Design implementation. | high | WORKSTREAM-07 | UNCERTAIN |
| QUESTION-15 | How do device drift, damage, and synchronization work? | Diegetic realism. | Devices mentioned. | Mechanics per device class. | Gameplay design. | medium | WORKSTREAM-07 | UNCERTAIN |
| QUESTION-16 | How much relativity is implemented initially? | Scope/performance. | Relativity first-class conceptually. | Fidelity tiers and phase-one scope. | Implementation planning. | medium | WORKSTREAM-02 | UNCERTAIN |
| QUESTION-17 | How do governance conflicts over time standards work mechanically? | Contracts/law/gameplay. | Standards can differ. | Enforcement/disputes/precedence in existing governance model. | The Game integration. | medium | WORKSTREAM-08 | UNCERTAIN |
| QUESTION-18 | Which generated prompts should remain canonical? | Avoid outdated prompt copies. | Several prompts generated; packet supersedes them. | Whether to use old prompt or this package. | Use latest package unless user says otherwise. | medium | WORKSTREAM-10 | UNCERTAIN |

### Artifact Ledger
| ID | Artifact / file / prompt / output | Type | Purpose | Status | Where it came from | Carry forward? | Notes | Label |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| ARTIFACT-01 | Broad celestial body/system category list | output/spec | Initial universe simulation categories | superseded but useful | Early assistant response | yes | Use as rationale only. | FACT |
| ARTIFACT-02 | Sol/Milky Way/Universe inclusion list | output/spec | Scale-specific content scope | partially superseded | Assistant response after user defined scales | yes | Use with later refined celestial inventory. | FACT |
| ARTIFACT-03 | Canonical Milky Way system set v1.0 | output/spec | Real-system backbone | needs verification | Assistant-generated | yes | Likely contains errors; verify before hardcoding. | UNCERTAIN / UNVERIFIED |
| ARTIFACT-04 | System-by-system body/site breakdown | output/spec | Contents per canonical system | incomplete subset | Assistant-generated | partial | Useful as template, not final data. | UNCERTAIN |
| ARTIFACT-05 | Gameplay mechanics mapping for celestial features | output/spec | Connect astronomical features to gameplay | current rationale | Assistant-generated | yes | Preserve as design rationale. | FACT / INFERENCE |
| ARTIFACT-06 | Full Sol system inclusion spec | output/spec | High-detail Sol scope | current design intent | Assistant-generated after user requested all stops | yes | Use as Sol content baseline. | FACT / INFERENCE |
| ARTIFACT-07 | Earth calendar specification | output/spec | Existing calendars + initial perfect calendar | superseded by final HPC-E | Assistant-generated | yes | Historical context only for HPC-E evolution. | FACT |
| ARTIFACT-08 | Final HPC-E definition | output/spec | Authoritative Perfect Earth Calendar | locked except leap rule | User correction + assistant formalization | yes | High-priority carry-forward. | FACT |
| ARTIFACT-09 | Planetary/moon calendar specs | output/spec | Mars/Venus/Mercury/gas giants/moons/Pluto systems | needs refinement | Assistant-generated | yes | Review names and leap rules. | UNCERTAIN |
| ARTIFACT-10 | Complete calendar inventory | output/spec | List of calendars/time systems | current but partly tentative | Assistant-generated | yes | Use with uncertainty labels. | FACT / UNCERTAIN |
| ARTIFACT-11 | Calendar naming layer | output/spec | Names for days/months/seasons | partly superseded | Assistant-generated | yes with caveats | HPC-E portion superseded by user correction. | UNCERTAIN |
| ARTIFACT-12 | Leap seconds/relativity doctrine | output/spec | Core physics/time policy | current doctrine | Assistant response to user question | yes | High-priority carry-forward. | FACT |
| ARTIFACT-13 | World initialization/time discovery addendum | output/spec | Default start, sunrise spawn, no HUD, custom standards | current doctrine | User + assistant formalization | yes | High-priority carry-forward. | FACT |
| ARTIFACT-14 | Modularity/extensibility plan | output/spec | Architecture recommendations | current but codebase-unverified | Assistant-generated | yes | Use after inspecting project. | INFERENCE |
| ARTIFACT-15 | The Game chat handoff prompt | prompt | Paste into The Game chat to generate Codex prompt | useful but superseded by this package | Assistant-generated | yes | Prefer this package plus bootstrap prompt now. | FACT |
| ARTIFACT-16 | Celestial content inventory | output/spec | Astronomical/spatial scope counterpart to time scope | current design intent | Assistant-generated | yes | Needs scientific verification. | FACT / UNCERTAIN |
| ARTIFACT-17 | Maximum-fidelity Context Transfer Packet | handoff | State transfer for new chat | completed before this request | Assistant-generated | yes | Source basis for this package. | FACT |
| ARTIFACT-18 | Final downloadable report package | report package | Markdown/YAML/ZIP package for this chat | created by current response | Current task | yes | Contains normalized IDs and reports. | FACT |

### Risk Register
| ID | Risk / failure mode | Consequence | Likelihood | Severity | Mitigation | Related workstream | Label |
| --- | --- | --- | --- | --- | --- | --- | --- |
| RISK-01 | New chat assumes unverified codebase details. | Implementation mismatch. | medium | high | Inspect actual Plan G/codebase before Codex prompt. | WORKSTREAM-09 | UNCERTAIN / UNVERIFIED |
| RISK-02 | Calendars contaminate physics time. | Causality/save corruption. | medium | high | Enforce one-way dependency and pure renderers. | WORKSTREAM-02 | FACT |
| RISK-03 | Rendered dates persisted as truth. | Patch drift and date corruption. | medium | high | Persist ACT/frame/version only. | WORKSTREAM-02, WORKSTREAM-09 | INFERENCE |
| RISK-04 | HUD leaks unknown time/date. | Breaks fog-of-war and diegetic premise. | medium | high | Capability-gate all displays. | WORKSTREAM-07 | FACT |
| RISK-05 | Intercalary days mishandled as normal dates. | Week/month invariants break. | medium | high | Use canonical tokens and optional projection. | WORKSTREAM-03 | FACT / INFERENCE |
| RISK-06 | Acronym collisions cause registry bugs. | Wrong standard/calendar selected. | medium | medium | Use unique internal IDs. | WORKSTREAM-05 | UNCERTAIN |
| RISK-07 | Assistant-generated astronomy errors become hardcoded. | Scientific/design inaccuracies. | high | high | Verify celestial lists before data entry. | WORKSTREAM-01 | UNCERTAIN / UNVERIFIED |
| RISK-08 | Overimplementation of galaxy/universe detail. | Performance/scope explosion. | medium | high | Use explicit/procedural/parametric classes. | WORKSTREAM-01 | FACT |
| RISK-09 | Non-7-day cycles confuse players. | UX and calendar semantics problems. | medium | medium | Classify as WorkCycles if appropriate. | WORKSTREAM-04 | UNCERTAIN |
| RISK-10 | Assistant-created names conflict with naming principles. | Spec inconsistency. | medium | medium | Review and normalize naming policy. | WORKSTREAM-04 | UNCERTAIN |
| RISK-11 | Patch updates alter constants/ephemerides/calendar behavior. | Old saves/replays change. | medium | high | Version and pin all data/model packs. | WORKSTREAM-09 | INFERENCE |
| RISK-12 | Sunrise undefined at spawn location. | Start condition failure. | medium | medium | Define deterministic fallbacks. | WORKSTREAM-06 | FACT |
| RISK-13 | Over-humanizing galactic/universal calendars. | False conceptual model. | low | medium | Keep GEC/UEF as epoch/duration frameworks. | WORKSTREAM-05 | FACT |
| RISK-14 | Governance standards hardcoded too early. | Plural standards become brittle. | medium | medium | Use data-driven TimeStandard objects. | WORKSTREAM-08 | FACT / INFERENCE |
| RISK-15 | Device knowledge model too shallow. | Diegetic HUD loses gameplay depth. | medium | medium | Define capability/device/drift models. | WORKSTREAM-07 | INFERENCE |
| RISK-16 | Report package overcompresses or loses context. | Future assistant asks user to repeat work. | low | high | Use full report plus registers and YAML. | WORKSTREAM-10 | FACT |
| RISK-17 | Future aggregator treats tentative assistant proposals as locked decisions. | Spec book fossilizes brainstorms. | medium | high | Preserve labels and source hierarchy. | WORKSTREAM-10 | FACT |

### Verification Queue
| ID | Item requiring verification | Why verification is needed | Suggested verification source/type | Priority | Related workstream | Label |
| --- | --- | --- | --- | --- | --- | --- |
| VERIFY-01 | Verify all canonical Milky Way system entries. | Assistant-generated astronomy list may contain errors. | Astronomical catalogs / NASA / ESA / SIMBAD / peer-reviewed sources. | high | WORKSTREAM-01 | UNCERTAIN / UNVERIFIED |
| VERIFY-02 | Check SN 1987A classification/location. | Likely issue: commonly associated with LMC, not Milky Way. | Authoritative astronomy references. | high | WORKSTREAM-01 | UNCERTAIN / UNVERIFIED |
| VERIFY-03 | Verify Sol system body/site scope against desired gameplay and science. | Prevent omissions or over-scope. | NASA/JPL/IAU plus gameplay review. | medium | WORKSTREAM-01 | UNCERTAIN |
| VERIFY-04 | Verify celestial mechanics constants before coding. | Assistant-supplied values may be approximations. | NASA/JPL Horizons, IAU, SPICE kernels. | high | WORKSTREAM-01, WORKSTREAM-02 | UNCERTAIN / UNVERIFIED |
| VERIFY-05 | Verify ACT epoch and Jan 1 2000 mapping. | Required for deterministic start. | Time-scale standards: UTC/TAI/TT/TDB; project decision. | high | WORKSTREAM-02, WORKSTREAM-06 | UNCERTAIN |
| VERIFY-06 | Verify leap-second handling against intended UTC display compatibility. | Avoid UTC bugs. | IERS/ITU/official leap-second tables; project display requirements. | medium | WORKSTREAM-02 | UNCERTAIN / UNVERIFIED |
| VERIFY-07 | Verify relativity equation/fidelity tier before implementation. | Assistant equation was illustrative and may not be sufficient. | Physics review / authoritative astrodynamics sources. | medium | WORKSTREAM-02 | UNCERTAIN / UNVERIFIED |
| VERIFY-08 | Verify historical status and spelling of Undecember. | User requested historically proposed name. | Calendar history sources. | medium | WORKSTREAM-03 | UNCERTAIN / UNVERIFIED |
| VERIFY-09 | Finalize and verify HPC-E leap algorithm. | Calendar consistency. | User decision + calendar arithmetic tests. | high | WORKSTREAM-03 | UNCERTAIN |
| VERIFY-10 | Review planetary/moon calendar names for consistency and user preference. | Some names may be assistant brainstorms. | User review. | medium | WORKSTREAM-04 | UNCERTAIN |
| VERIFY-11 | Verify planetary/moon rotation/orbit periods before data pack creation. | Scientific values require accuracy. | NASA/JPL/IAU sources. | high | WORKSTREAM-04 | UNCERTAIN / UNVERIFIED |
| VERIFY-12 | Resolve internal calendar/time standard IDs. | Acronym collisions exist. | Registry design review. | medium | WORKSTREAM-05 | UNCERTAIN |
| VERIFY-13 | Define deterministic sunrise algorithm and edge cases. | Spawn and astronomical recurrence depend on it. | Astro algorithm spec + gameplay review. | high | WORKSTREAM-06 | UNCERTAIN |
| VERIFY-14 | Verify default start date should be Jan 1 2000 Gregorian at what time of day before sunrise adjustment. | User specified date but not initial time-scale instant. | User confirmation / design choice. | high | WORKSTREAM-06 | UNCERTAIN |
| VERIFY-15 | Verify existing knowledge/fog-of-war systems in The Game. | Integration depends on actual architecture. | Plan G/The Game chat/codebase. | high | WORKSTREAM-07, WORKSTREAM-09 | UNCERTAIN / UNVERIFIED |
| VERIFY-16 | Verify existing governance/jurisdiction/contract systems. | TimeStandard integration depends on these. | Plan G/The Game chat/codebase. | high | WORKSTREAM-08, WORKSTREAM-09 | UNCERTAIN / UNVERIFIED |
| VERIFY-17 | Verify codebase language, architecture, and module boundaries. | Prior implementation claims are unverified. | Project repo/docs. | high | WORKSTREAM-09 | UNCERTAIN / UNVERIFIED |
| VERIFY-18 | Check generated prompts against current project conventions before Codex use. | Avoid stale or over-broad implementation instructions. | The Game chat and repo context. | medium | WORKSTREAM-10 | UNCERTAIN |
| VERIFY-19 | Manual review of this report package for completeness before aggregation. | Final package may still omit nuances from visible chat. | User review. | medium | WORKSTREAM-10 | UNCERTAIN |

## 6. Possible Cross-Chat Duplicates

- PROJECT-CONTEXT: Governance and jurisdictions.
- PROJECT-CONTEXT: Knowledge and fog-of-war.
- PROJECT-CONTEXT: Engine/game architecture and modularity.
- PROJECT-CONTEXT: World generation and celestial map scale.
- PROJECT-CONTEXT: UI/HUD design.
- PROJECT-CONTEXT: Codex implementation prompts and docs.

## 7. Possible Cross-Chat Conflicts

- Existing time/date system may conflict with ACT/calendar-renderer doctrine.
- Existing HUD may assume a free universal clock/date display.
- Existing governance may have different standard/contract precedence.
- Existing celestial scope may include more/fewer explicit objects.
- Existing implementation language constraints may contradict assistant assumptions.

## 8. Spec Book Integration Guidance

This chat should feed chapters on chronology, calendars, time core, celestial content, Sol system scope, diegetic HUD/knowledge, governance standards, and versioning/testing. ACT, calendar-renderer separation, HPC-E, local-sunrise start, no-time-HUD start, and TimeStandard pluralism should become formal requirements. Assistant-proposed non-Earth names, constants, and Milky Way systems should remain background until verified.

## 9. Aggregator Warnings

Do not treat assistant-generated astronomy, constants, or codebase claims as verified. Do not merge tentative non-Earth calendar names as final. Do not lose the user’s exact HPC-E wording. Do not collapse diegetic knowledge into ordinary UI. Do not reintroduce rejected concepts such as January 0, leap seconds in core, or universal ordinary months/weeks.
