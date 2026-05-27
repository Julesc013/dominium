# Full Chat Report — Dominium Chronology & Celestial Systems

## 0. Report Metadata

| Field | Value |
|---|---|
| Chat label | Dominium Chronology & Celestial Systems |
| Generated date anchor | 2026-05-27 Australia/Melbourne |
| Source scope | THIS CHAT ONLY; PROJECT-CONTEXT appears only where sourced from visible project/system context or user references to other Dominium chats. |
| Apparent coverage | full visible chat context plus previous context transfer packet |
| Extraction confidence | 4/5 |
| Staleness risk | medium |
| Future plans present | yes |
| Pending tasks present | yes |
| Artifacts/files present | artifacts/prompts yes; no prior downloadable files before this package |
| Safe for aggregation | yes, with caveats |
| Main limitations | No access to actual Plan G/The Game chat or codebase; assistant-generated astronomy/calendar details require verification; some names and leap rules remain tentative. |

## 1. Executive Summary

[FACT] This chat developed a substantial design subsystem for the Dominium Game project: a multi-scale chronology, calendar, celestial-content, and diegetic knowledge architecture intended to integrate with The Game / Plan G and eventually feed a Codex implementation prompt. It began with the user asking what celestial bodies and systems should be included in a logical universe simulation without too much redundancy for gameplay. The work expanded into a scale hierarchy: planetary Earth, the Sol system, the Milky Way, and the universe. Sol was explicitly prioritized for maximum detail because the user stated most playtime will be spent there. The resulting celestial doctrine is that gameplay-relevant bodies/sites should be explicit, repetitive content should be procedural/statistical, and non-impactful content should be excluded.

[FACT] The chat then shifted into timekeeping. The core doctrine became: time is real and continuous; calendars are interfaces. Atomic Continuous Time (ACT) is the authoritative monotonic simulation time. Barycentric Sol Time (BST), Galactic Coordinate Time (GCT), and Cosmological Proper Time (CPT) represent larger-scale coordinate frames. Proper time is derived for clocks/biology and never becomes authoritative calendar time. Leap seconds are display-only and absent from core simulation. Calendars must be stateless reversible renderers, not physics drivers.

[FACT] Earth calendar support includes Gregorian, Julian, Islamic, Hebrew, Chinese, Persian/Solar Hijri, Holocene, Metric/French Revolutionary, and a custom Perfect Earth Calendar. The user later gave the final naming structure for the Perfect Earth Calendar: weekdays use Monday through Sunday; the year begins in March; the 13 months are March, April, May, June, July, August, September, October, November, December, Undecember, January, February. The calendar has 13 months of 28 days, with Year Day and Leap Day appended after February. The user explicitly wanted to avoid January 0. Intercalary days are canonically outside week/month; compatibility projection may map them to February 29 and February 30, but this remains a renderer policy, not the canonical form.

[FACT] Additional systems were defined for Luna, Mercury, Venus, Mars, Jovian moons, Saturnian moons, Uranian moons, Neptunian moons, Pluto/TNOs, Sol-wide, galactic, and universal scales. These include both scientific clocks and engineered calendars. Many names and exact leap rules for non-Earth systems are assistant-generated and require user review before becoming final.

[FACT] The user added crucial gameplay constraints: each world/universe instance can start at a different date/time. By default, a world starts from Gregorian January 1, 2000 AD, while the player spawns at local sunrise on the body/time zone/solar context where they appear. At the beginning, the player has no clocks, calendars, date, or time HUD, because the HUD is diegetic and the player lacks timekeeping devices. Players can define their own time/date systems or adopt provided calendars. Organizations, regions, jurisdictions, and individuals may designate standards.

[FACT] The final architecture recommendation was modular: TimeCore for ACT/frames, Chronology for calendar renderers, NameSets for labels, TimeStandards for social/legal standards, KnowledgeCapabilities for fog-of-war/HUD gating, Ephemeris/astronomy for local solar state and sunrise, and Recurrence for physical/civil/astronomical scheduling. The next chat must not assume implementation details from this chat; it must inspect the actual Plan G/The Game context before generating Codex implementation instructions.

## 2. How to Use This Report

This report covers only this old chat and the previously generated context transfer packet visible in this chat. It is not a whole-project summary. Where Project context appears, it is labelled PROJECT-CONTEXT. Direct user statements outrank assistant proposals. Assistant-generated astronomical data, constants, calendar names, implementation-language claims, and codebase assumptions require verification before implementation. Tentative decisions remain tentative. This report is intended for future aggregation into a full Project Spec Book and for a new assistant to continue without asking the user to repeat this chat.

## 3. User Preferences Visible in This Chat

### 3.1 Explicit Preferences

| ID | Preference | Category | Source basis | Strength | Implication | Risk if misunderstood | Label |
| --- | --- | --- | --- | --- | --- | --- | --- |
| PREF-01 | Start messages with model version and build date. | explicit | User profile/instructions visible in chat context | strong | Future assistants should include model/build header if possible. | User may view omission as noncompliance. | FACT |
| PREF-02 | Be straightforward, critical, and fact-check. | explicit | User profile/instructions | strong | Avoid vague reassurance; mark uncertainty. | Overconfident or soft responses reduce usefulness. | FACT |
| PREF-03 | Prefer rigorous, correctly cited, unbiased facts. | explicit | User profile | strong | Verify current/scientific facts before hardcoding. | Assistant-proposed facts may be mistaken. | FACT |
| PREF-04 | Avoid making user repeat decisions. | explicit | User requested handoff and package | strong | Use packet as memory. | Loss of continuity wastes user effort. | FACT |
| PREF-05 | Use modular, extensible, robust architecture. | explicit | User asked directly | strong | Favor plugin/data-driven design. | Hardcoded design will not scale. | FACT |
| PREF-06 | Preserve tentative status and contradictions. | explicit | Current request | strong | Do not flatten uncertainty. | Wrong decisions may be fossilized. | FACT |
| PREF-07 | Diegetic/VR-friendly UI for time information. | explicit | User stated | strong | No free HUD clock/date. | Breaks intended realism. | FACT |
| PREF-08 | Detailed structured outputs with registers and IDs. | explicit | Current request | strong | Use stable IDs/tables. | Harder aggregation if absent. | FACT |
| PREF-09 | High-fidelity Sol system content. | explicit | User stated most playtime in Sol | strong | Prioritize Sol detail in spec. | Underdeveloped core play area. | FACT |

### 3.2 Inferred Preferences

| ID | Preference | Category | Source basis | Strength | Implication | Risk if misunderstood | Label |
| --- | --- | --- | --- | --- | --- | --- | --- |
| PREF-10 | Second/third-order design thinking. | inferred | User profile and project dialogue | medium | Explain implications and failure modes. | Shallow design may miss systemic interactions. | INFERENCE |

### 3.3 Preferences Not Established by This Chat

- UNCERTAIN / UNVERIFIED: Exact implementation language constraints are not established by this chat.
- UNCERTAIN / UNVERIFIED: Exact preferred naming style for every non-Earth engineered calendar is not established.
- UNCERTAIN / UNVERIFIED: Whether all assistant-created planetary/moon calendar names are desired is not established.
- UNCERTAIN / UNVERIFIED: Exact UI visual design for the diegetic HUD is not established.

## 4. Complete Topic and Workstream Inventory

| ID | Name | Objective | Current state | Desired end state | Background | Why it matters | Status | Priority | Confidence | Source label |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| WORKSTREAM-01 | Multi-scale celestial content architecture | Define celestial bodies, structures, regions, systems, and sites for gameplay across Earth, Sol, Milky Way, and universe scales without redundant simulation. | Scope and classification were defined conceptually: explicit, procedural, or parametric; Sol system is highest fidelity; Milky Way has a real-system backbone plus procedural expansion; universe is mostly parametric. | A data-driven celestial registry integrated with simulation, navigation, gameplay mechanics, time, governance, and knowledge/fog-of-war systems. | The chat began with the user asking what celestial bodies/systems to include in a logical universe simulation without too much redundancy. The user then specified gameplay scales: Earth, Sol, Milky Way, and universe. | Celestial content defines map scope, simulation fidelity, gameplay locations, calendars, hazards, and long-term expansion. | active | high | medium-high | FACT / INFERENCE |
| WORKSTREAM-02 | Authoritative time core and coordinate frames | Define simulation-authoritative time layers and frame transforms from local gameplay to cosmological timescales. | ACT, BST, GCT, CPT, CDC, proper-time, leap-second policy, and scale transition doctrine are conceptually defined. | A deterministic engine-level time core storing ACT plus frame/version metadata, with frame transforms and proper-time utilities. | Developed after the user asked for perfect measurement and calendar systems for Earth-centric and Sol-centric civilizations. | Time affects physics, save determinism, calendar rendering, scheduling, governance, and player HUD knowledge. | active | high | high | FACT |
| WORKSTREAM-03 | Earth calendars and Perfect Earth Calendar (HPC-E) | Support existing widely used Earth calendars and define the custom Perfect Earth Calendar with user-specified names and intercalary rules. | Existing calendar set and final HPC-E naming/structure are defined; exact HPC-E leap rule is still pending. | Calendar plugins/renderers, NameSets, strict and compatibility modes, and test vectors. | The user first listed Gregorian, Julian, Islamic, Hebrew, Chinese, Persian, Holocene, Metric, and a custom Perfect calendar. Later the user corrected the Perfect Earth Calendar naming and intercalary placement. | Earth is the planetary baseline and the human cultural/calendar reference point. | active | high | high | FACT |
| WORKSTREAM-04 | Planetary, moon, Pluto, and TNO calendars | Define local scientific and civil time systems for Mars, Venus, Mercury, major moons, Pluto, and TNO/deep-time contexts. | Many assistant-proposed calendar structures and names exist; some are accepted design intent through continuation, but final naming/leap details remain uncertain. | A calendar registry for body/system-specific scientific clocks, civil calendars, engineered calendars, and name sets. | The user asked successively for Mars, Venus, Mercury, Jupiter and moons, Saturn and moons, Uranus, Neptune, Pluto/TNOs/Moon/Sun/Sol/Undefined. | Each body/system should feel different and support local governance, clocks, schedules, and culture. | active | medium-high | medium | FACT / UNCERTAIN |
| WORKSTREAM-05 | Sol-wide, galactic, and universal epoch systems | Define civil/archival time frameworks above the planetary scale. | SCT/SEC, GalCT/GEC, UCT/UEF are defined conceptually; acronym collision risk remains. | Scale-aware renderer/data definitions with no false human calendar semantics at galactic/universal scale. | User asked to extend Sol-system-wide calendars to Milky Way and universe as a whole. | The game spans Sol, galaxy, and universe scales; records and archives need scale-appropriate date/duration systems. | active | medium-high | medium-high | FACT |
| WORKSTREAM-06 | World instantiation and local sunrise start | Define how each world/universe instance starts and how the player’s spawn time is selected. | User-specified default: Gregorian Jan 1, 2000 AD; time starts at local sunrise on the spawn planet/time zone/solar context; fallback rules were proposed but need formalization. | World-instance initialization schema and deterministic sunrise/fallback algorithm. | The user introduced this after prompt-generation work, adding crucial gameplay start-state requirements. | Initial conditions affect player perception, astronomy, save determinism, and diegetic UI. | active | high | high for intent, medium for exact implementation | FACT |
| WORKSTREAM-07 | Diegetic HUD, time knowledge, and fog-of-war | Ensure time/date knowledge is unavailable until obtained through devices, calendars, documents, astronomy, networks, or organizations. | Doctrine defined; capability schema and device models still pending. | Capability-gated diegetic HUD and time-display system integrated with fog-of-war. | User explicitly stated no initial timekeeping devices/calendars and no available HUD information, with VR-friendly diegetic HUD. | Transforms timekeeping into gameplay progression and supports realism/immersion. | active | high | high | FACT |
| WORKSTREAM-08 | Governance, jurisdictions, organizations, and time standards | Model time/calendar standards as social/legal data objects designated by regions, jurisdictions, organizations, and individuals. | User requirement exists; assistant proposed TimeStandard object and resolution order. | TimeStandard schema integrated with governance, contracts, scheduling, law, and individual preferences. | User explicitly said organizations, regions, jurisdictions, and individuals may designate systems as standard. | Makes timekeeping part of governance, contracts, culture, and conflict. | active | high | medium-high | FACT / INFERENCE |
| WORKSTREAM-09 | Modularity, extensibility, reliability, and integration architecture | Refactor the full design into modular layers suitable for the existing game/engine architecture. | Architecture principles and module boundaries were proposed; exact implementation depends on actual codebase/context. | A validated integration design and Codex-ready phased implementation prompt. | User asked how to make the whole system more modular/extensible/robust, then asked to merge with The Game chat. | The system is large and will fail if implemented as ad-hoc hardcoded calendars and UI widgets. | active | high | medium | FACT / INFERENCE |
| WORKSTREAM-10 | Prompt handoff and report packaging | Preserve the decisions and convert the chat into reusable prompts/reports for future chats and Codex implementation. | Context transfer packet exists; this current package creates downloadable report files and a ZIP. | Reusable per-chat package suitable for aggregation into a future full Project Spec Book. | User asked for prompts for The Game chat, then asked for maximum-fidelity context transfer, then asked for final downloadable package. | Prevents the user from repeating large amounts of design context. | active | high | high | FACT |

## 5. Detailed Workstream State

### WORKSTREAM-01 — Multi-scale celestial content architecture
- Label: FACT / INFERENCE
- Objective: Define celestial bodies, structures, regions, systems, and sites for gameplay across Earth, Sol, Milky Way, and universe scales without redundant simulation.
- Background: The chat began with the user asking what celestial bodies/systems to include in a logical universe simulation without too much redundancy. The user then specified gameplay scales: Earth, Sol, Milky Way, and universe.
- Current state: Scope and classification were defined conceptually: explicit, procedural, or parametric; Sol system is highest fidelity; Milky Way has a real-system backbone plus procedural expansion; universe is mostly parametric.
- Desired end state: A data-driven celestial registry integrated with simulation, navigation, gameplay mechanics, time, governance, and knowledge/fog-of-war systems.
- Importance: Celestial content defines map scope, simulation fidelity, gameplay locations, calendars, hazards, and long-term expansion.
- Decisions made: DECISION-01, DECISION-02, DECISION-03
- Decisions pending: QUESTION-07, QUESTION-08, QUESTION-09
- Pending tasks: TASK-02, TASK-18
- Constraints: CONSTRAINT-11, CONSTRAINT-12
- Dependencies: Versioned constants/ephemerides, Verified astronomical data, Plan G integration
- Timeline / sequencing: Defined early, refined after Sol system and celestial scope questions.
- Blockers: Unverified astronomy details, No access in this chat to the actual Plan G codebase or full chat.
- Risks: RISK-07, RISK-08
- Artifacts: ARTIFACT-01, ARTIFACT-02, ARTIFACT-03, ARTIFACT-04, ARTIFACT-16
- Success criteria: Sol system is deep and explicit; Milky Way/universe stay performant; explicit objects are gameplay-relevant.
- Recommended next action: Verify celestial lists, then convert into data schemas with fidelity classes.
- Verification needed: VERIFY-01, VERIFY-02, VERIFY-03
- Confidence: medium-high
- Carry-forward priority: high
### WORKSTREAM-02 — Authoritative time core and coordinate frames
- Label: FACT
- Objective: Define simulation-authoritative time layers and frame transforms from local gameplay to cosmological timescales.
- Background: Developed after the user asked for perfect measurement and calendar systems for Earth-centric and Sol-centric civilizations.
- Current state: ACT, BST, GCT, CPT, CDC, proper-time, leap-second policy, and scale transition doctrine are conceptually defined.
- Desired end state: A deterministic engine-level time core storing ACT plus frame/version metadata, with frame transforms and proper-time utilities.
- Importance: Time affects physics, save determinism, calendar rendering, scheduling, governance, and player HUD knowledge.
- Decisions made: DECISION-04, DECISION-05, DECISION-06, DECISION-07, DECISION-08, DECISION-21, DECISION-22
- Decisions pending: QUESTION-03, QUESTION-16
- Pending tasks: TASK-06, TASK-11, TASK-17
- Constraints: CONSTRAINT-01, CONSTRAINT-02, CONSTRAINT-03, CONSTRAINT-04, CONSTRAINT-05, CONSTRAINT-06
- Dependencies: Constants table, Ephemeris packs, Serialization system, Calendar renderers
- Timeline / sequencing: Established after Earth/Sol timekeeping discussion and reinforced during leap seconds/relativity/cosmology discussion.
- Blockers: Exact epoch/time-scale mapping unresolved, Transform fidelity tiers unresolved
- Risks: RISK-02, RISK-03, RISK-11
- Artifacts: ARTIFACT-05, ARTIFACT-11, ARTIFACT-12
- Success criteria: No calendar or display concept can change physics; all save/load and replay remain deterministic.
- Recommended next action: Define core timestamp schema and frame transform interfaces after inspecting existing engine architecture.
- Verification needed: VERIFY-05, VERIFY-06, VERIFY-07
- Confidence: high
- Carry-forward priority: high
### WORKSTREAM-03 — Earth calendars and Perfect Earth Calendar (HPC-E)
- Label: FACT
- Objective: Support existing widely used Earth calendars and define the custom Perfect Earth Calendar with user-specified names and intercalary rules.
- Background: The user first listed Gregorian, Julian, Islamic, Hebrew, Chinese, Persian, Holocene, Metric, and a custom Perfect calendar. Later the user corrected the Perfect Earth Calendar naming and intercalary placement.
- Current state: Existing calendar set and final HPC-E naming/structure are defined; exact HPC-E leap rule is still pending.
- Desired end state: Calendar plugins/renderers, NameSets, strict and compatibility modes, and test vectors.
- Importance: Earth is the planetary baseline and the human cultural/calendar reference point.
- Decisions made: DECISION-09, DECISION-10, DECISION-11, DECISION-12
- Decisions pending: QUESTION-05, QUESTION-06
- Pending tasks: TASK-03, TASK-07, TASK-13, TASK-14
- Constraints: CONSTRAINT-07, CONSTRAINT-08, CONSTRAINT-14, CONSTRAINT-15
- Dependencies: Calendar renderer architecture, NameSets, Intercalary token model
- Timeline / sequencing: Defined after Earth calendar discussion; revised after user specified March-start and Undecember/February sink.
- Blockers: Leap rule not final
- Risks: RISK-05
- Artifacts: ARTIFACT-06, ARTIFACT-07, ARTIFACT-08, ARTIFACT-11
- Success criteria: HPC-E dates are perpetual; months remain 28 days; intercalary days round-trip correctly; existing calendars remain renderers.
- Recommended next action: Finalize HPC-E leap rule, then implement strict and compatibility renderers.
- Verification needed: VERIFY-08, VERIFY-09
- Confidence: high
- Carry-forward priority: high
### WORKSTREAM-04 — Planetary, moon, Pluto, and TNO calendars
- Label: FACT / UNCERTAIN
- Objective: Define local scientific and civil time systems for Mars, Venus, Mercury, major moons, Pluto, and TNO/deep-time contexts.
- Background: The user asked successively for Mars, Venus, Mercury, Jupiter and moons, Saturn and moons, Uranus, Neptune, Pluto/TNOs/Moon/Sun/Sol/Undefined.
- Current state: Many assistant-proposed calendar structures and names exist; some are accepted design intent through continuation, but final naming/leap details remain uncertain.
- Desired end state: A calendar registry for body/system-specific scientific clocks, civil calendars, engineered calendars, and name sets.
- Importance: Each body/system should feel different and support local governance, clocks, schedules, and culture.
- Decisions made: DECISION-18, DECISION-19
- Decisions pending: QUESTION-10, QUESTION-11, QUESTION-12
- Pending tasks: TASK-04, TASK-05, TASK-07, TASK-13
- Constraints: CONSTRAINT-02, CONSTRAINT-09
- Dependencies: Final naming policy, Calendar plugin interface, Verified body rotation/orbit constants
- Timeline / sequencing: Developed sequentially after Earth calendars.
- Blockers: Names and leap rules not fully validated; some contradictions in naming doctrine.
- Risks: RISK-09, RISK-10
- Artifacts: ARTIFACT-09, ARTIFACT-10, ARTIFACT-11, ARTIFACT-12
- Success criteria: Each inhabited/usable body can expose a local calendar without compromising ACT or forcing global uniformity.
- Recommended next action: Review all assistant-proposed names and classify non-7-day cycles as work cycles or weeks.
- Verification needed: VERIFY-10, VERIFY-11
- Confidence: medium
- Carry-forward priority: medium-high
### WORKSTREAM-05 — Sol-wide, galactic, and universal epoch systems
- Label: FACT
- Objective: Define civil/archival time frameworks above the planetary scale.
- Background: User asked to extend Sol-system-wide calendars to Milky Way and universe as a whole.
- Current state: SCT/SEC, GalCT/GEC, UCT/UEF are defined conceptually; acronym collision risk remains.
- Desired end state: Scale-aware renderer/data definitions with no false human calendar semantics at galactic/universal scale.
- Importance: The game spans Sol, galaxy, and universe scales; records and archives need scale-appropriate date/duration systems.
- Decisions made: DECISION-20
- Decisions pending: QUESTION-06, QUESTION-13
- Pending tasks: TASK-04, TASK-07, TASK-13
- Constraints: CONSTRAINT-10, CONSTRAINT-13
- Dependencies: Time core frames ACT/BST/GCT/CPT, NameSets, Unique IDs
- Timeline / sequencing: Defined after all local calendars were discussed.
- Blockers: Acronym collisions and exact naming policy.
- Risks: RISK-06, RISK-13
- Artifacts: ARTIFACT-10, ARTIFACT-11, ARTIFACT-12
- Success criteria: Sol uses structured empire calendar; galaxy/universe use duration/epoch only.
- Recommended next action: Assign unique internal IDs and keep human-readable aliases separate.
- Verification needed: VERIFY-12
- Confidence: medium-high
- Carry-forward priority: medium-high
### WORKSTREAM-06 — World instantiation and local sunrise start
- Label: FACT
- Objective: Define how each world/universe instance starts and how the player’s spawn time is selected.
- Background: The user introduced this after prompt-generation work, adding crucial gameplay start-state requirements.
- Current state: User-specified default: Gregorian Jan 1, 2000 AD; time starts at local sunrise on the spawn planet/time zone/solar context; fallback rules were proposed but need formalization.
- Desired end state: World-instance initialization schema and deterministic sunrise/fallback algorithm.
- Importance: Initial conditions affect player perception, astronomy, save determinism, and diegetic UI.
- Decisions made: DECISION-13, DECISION-14
- Decisions pending: QUESTION-03, QUESTION-04
- Pending tasks: TASK-10, TASK-11
- Constraints: CONSTRAINT-16, CONSTRAINT-17
- Dependencies: Ephemeris/sunrise solver, World-instance schema, Time core
- Timeline / sequencing: Added late in the chat, after calendar architecture was mostly established.
- Blockers: Exact definition of sunrise and initial date time scale undefined.
- Risks: RISK-12
- Artifacts: ARTIFACT-13
- Success criteria: Every world can start independently; default world starts on the specified civil anchor and player begins at local environmental morning where possible.
- Recommended next action: Define deterministic sunrise/fallback function with exact solar elevation threshold and time-scale mapping.
- Verification needed: VERIFY-13, VERIFY-14
- Confidence: high for intent, medium for exact implementation
- Carry-forward priority: high
### WORKSTREAM-07 — Diegetic HUD, time knowledge, and fog-of-war
- Label: FACT
- Objective: Ensure time/date knowledge is unavailable until obtained through devices, calendars, documents, astronomy, networks, or organizations.
- Background: User explicitly stated no initial timekeeping devices/calendars and no available HUD information, with VR-friendly diegetic HUD.
- Current state: Doctrine defined; capability schema and device models still pending.
- Desired end state: Capability-gated diegetic HUD and time-display system integrated with fog-of-war.
- Importance: Transforms timekeeping into gameplay progression and supports realism/immersion.
- Decisions made: DECISION-15
- Decisions pending: QUESTION-14, QUESTION-15
- Pending tasks: TASK-09, TASK-20
- Constraints: CONSTRAINT-18, CONSTRAINT-19
- Dependencies: Knowledge/fog-of-war system, Device/inventory system, UI/HUD system
- Timeline / sequencing: Added late, then integrated into modularity and The Game handoff discussions.
- Blockers: Existing knowledge/fog-of-war architecture unknown.
- Risks: RISK-04, RISK-15
- Artifacts: ARTIFACT-13, ARTIFACT-14
- Success criteria: HUD only shows time/date through in-world access; damage/loss of device removes or degrades display.
- Recommended next action: Define KnowledgeCapability IDs and map devices/organizations to capabilities.
- Verification needed: VERIFY-15
- Confidence: high
- Carry-forward priority: high
### WORKSTREAM-08 — Governance, jurisdictions, organizations, and time standards
- Label: FACT / INFERENCE
- Objective: Model time/calendar standards as social/legal data objects designated by regions, jurisdictions, organizations, and individuals.
- Background: User explicitly said organizations, regions, jurisdictions, and individuals may designate systems as standard.
- Current state: User requirement exists; assistant proposed TimeStandard object and resolution order.
- Desired end state: TimeStandard schema integrated with governance, contracts, scheduling, law, and individual preferences.
- Importance: Makes timekeeping part of governance, contracts, culture, and conflict.
- Decisions made: DECISION-16, DECISION-17, DECISION-18
- Decisions pending: QUESTION-17
- Pending tasks: TASK-08, TASK-12, TASK-20
- Constraints: CONSTRAINT-20
- Dependencies: Existing governance/jurisdiction systems, Calendar registry, Knowledge system
- Timeline / sequencing: Added with world instantiation and expanded during modularity/integration discussion.
- Blockers: Actual Plan G governance architecture unknown.
- Risks: RISK-14
- Artifacts: ARTIFACT-13, ARTIFACT-14, ARTIFACT-15
- Success criteria: Contracts and jurisdictions can render and enforce time standards without mutating physics time.
- Recommended next action: Inspect existing governance model and define TimeStandard as a data object.
- Verification needed: VERIFY-16
- Confidence: medium-high
- Carry-forward priority: high
### WORKSTREAM-09 — Modularity, extensibility, reliability, and integration architecture
- Label: FACT / INFERENCE
- Objective: Refactor the full design into modular layers suitable for the existing game/engine architecture.
- Background: User asked how to make the whole system more modular/extensible/robust, then asked to merge with The Game chat.
- Current state: Architecture principles and module boundaries were proposed; exact implementation depends on actual codebase/context.
- Desired end state: A validated integration design and Codex-ready phased implementation prompt.
- Importance: The system is large and will fail if implemented as ad-hoc hardcoded calendars and UI widgets.
- Decisions made: DECISION-21, DECISION-22
- Decisions pending: QUESTION-01, QUESTION-02
- Pending tasks: TASK-01, TASK-06, TASK-07, TASK-08, TASK-09, TASK-11, TASK-12, TASK-13, TASK-14, TASK-15, TASK-18
- Constraints: CONSTRAINT-21, CONSTRAINT-22, CONSTRAINT-23
- Dependencies: Actual codebase architecture, Existing Plan G systems
- Timeline / sequencing: Late-stage consolidation after all core design discussions.
- Blockers: No actual access in this chat to other chat/codebase.
- Risks: RISK-01, RISK-11
- Artifacts: ARTIFACT-14, ARTIFACT-15
- Success criteria: New assistant can generate Codex prompt without re-explanation and without assuming unsupported implementation facts.
- Recommended next action: Use this package in The Game chat; inspect actual project context; produce implementation prompt.
- Verification needed: VERIFY-17, VERIFY-18
- Confidence: medium
- Carry-forward priority: high
### WORKSTREAM-10 — Prompt handoff and report packaging
- Label: FACT
- Objective: Preserve the decisions and convert the chat into reusable prompts/reports for future chats and Codex implementation.
- Background: User asked for prompts for The Game chat, then asked for maximum-fidelity context transfer, then asked for final downloadable package.
- Current state: Context transfer packet exists; this current package creates downloadable report files and a ZIP.
- Desired end state: Reusable per-chat package suitable for aggregation into a future full Project Spec Book.
- Importance: Prevents the user from repeating large amounts of design context.
- Decisions made: DECISION-23
- Decisions pending: none recorded
- Pending tasks: TASK-16, TASK-21
- Constraints: CONSTRAINT-24, CONSTRAINT-25
- Dependencies: Visible chat context, Previous context transfer packet
- Timeline / sequencing: Final stage of this retired chat.
- Blockers: none recorded
- Risks: RISK-16, RISK-17
- Artifacts: ARTIFACT-15, ARTIFACT-17, ARTIFACT-18
- Success criteria: Files can be downloaded, shared, and used by future assistants without original chat access.
- Recommended next action: Download and store package; use Section 15 bootstrap prompt in the next chat.
- Verification needed: VERIFY-19
- Confidence: high
- Carry-forward priority: high


## 6. Chronological Timeline

| Sequence | Event / topic | What changed or was decided | Why it mattered | Current relevance | Confidence |
| --- | --- | --- | --- | --- | --- |
| 01 | User asked for important celestial bodies/systems for a logical universe simulation without redundant gameplay content. | Assistant introduced broad celestial categories. | Established redundancy-avoidance and gameplay relevance. | Still foundational. | high |
| 02 | User defined gameplay scales: Earth, Sol, Milky Way, universe. | Scale-specific inclusion problem created. | Set architecture scale ladder. | Current. | high |
| 03 | Assistant proposed Sol bodies, Milky Way structures, universe galaxies/classes. | Initial spatial scope. | Became basis for later refinement. | Partly superseded. | medium |
| 04 | User requested canonical Milky Way real systems, dozens to hundreds. | Explicit real-system backbone introduced. | Requires data verification. | Current but unverified. | high |
| 05 | Assistant listed ~50 real systems/sites. | Artifact created but may contain errors. | Needs verification before hardcoding. | Current with caveats. | medium |
| 06 | User asked for system-by-system bodies/sites. | Assistant began body/site breakdown for subset. | Established over-inclusive system contents pattern. | Incomplete. | medium |
| 07 | User asked gameplay mechanics tied to celestial features. | Mechanics mapping produced. | Linked astronomy to gameplay decisions. | Current rationale. | high |
| 08 | User asked to pull out all stops for Sol system. | Sol system elevated to highest fidelity. | Major content priority locked. | Current. | high |
| 09 | User asked for perfect measurement/calendar systems. | Time architecture started. | Introduced SI/atomic/core-vs-renderer doctrine. | Refined later. | high |
| 10 | User specified Earth calendar set and custom Perfect calendar. | Earth calendar scope locked. | Existing calendars plus HPC-E. | Current. | high |
| 11 | User sequentially requested Mars, Venus, Mercury, Jupiter/Saturn/Uranus/Neptune systems, Pluto/TNOs/Moon/Sun/Sol/Undefined. | Large calendar inventory developed. | Many assistant-proposed names need review. | Current with caveats. | medium |
| 12 | User requested complete list and full specification of calendars. | Inventory and formal spec generated. | Created calendar ontology. | Partly compressed; refined later. | medium |
| 13 | User asked for Sol/Milky Way/Universe calendar extension. | SCT/SEC, GCT/GEC, CPT/UEF defined. | Scale-abstraction doctrine locked. | Current. | high |
| 14 | User requested names for calendar units. | Assistant proposed NameSets. | Created naming layer but later corrected for HPC-E. | Partly superseded. | medium |
| 15 | User specified final Perfect Earth Calendar naming/order/intercalary sink. | HPC-E final form locked. | Important user correction. | Current authoritative. | high |
| 16 | User asked about intercalary dates for compatibility. | Strict canonical mode plus optional Feb29/Feb30 projection proposed. | Compatibility strategy created. | Current with caveat. | medium-high |
| 17 | User asked about leap seconds, relativity, cosmology. | Core doctrine locked: leap display-only; relativity modeled; epochs at scale. | High-impact technical design. | Current. | high |
| 18 | User requested prompts for The Game/dev chat and suffix definitions. | Prompt artifacts created. | Useful handoff material. | Superseded by this package but preserved. | high |
| 19 | User added world instantiation, Jan 1 2000, local sunrise, no HUD, custom calendars, org/jurisdiction standards. | Major gameplay integration requirements locked. | Affected time, knowledge, governance, UI. | Current authoritative. | high |
| 20 | User asked for modularity/extensibility/robustness. | Architecture principles proposed. | Plugin/data-driven design articulated. | Current, codebase-unverified. | medium-high |
| 21 | User asked to merge with The Game/Plan G. | Assistant noted lack of full access and gave conceptual integration. | Important caveat about implementation knowledge. | Current caveat. | high |
| 22 | User requested The Game handoff prompt. | Prompt generated. | Allows continuation without repetition. | Superseded by package but useful. | high |
| 23 | User requested exclusive content lists for core/data/defaults and celestial structures. | Content inventories created. | Scope contract formed. | Current with verification needs. | high |
| 24 | User requested maximum-fidelity context transfer packet. | Packet created. | Direct source for current report package. | Current. | high |
| 25 | User requested final downloadable report package. | This package generated. | Turns chat state into reusable files. | Current. | high |

## 7. Decisions

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

### Highest-impact decisions

- FACT: ACT is authoritative and calendars are pure renderers; this prevents the entire system from corrupting physics, saves, and causality.
- FACT: HPC-E’s final month order and intercalary sink are user-defined and should be treated as locked, except for the still-pending leap rule.
- FACT: The player begins without time/date knowledge, making timekeeping a diegetic gameplay/knowledge system rather than a default HUD overlay.
- FACT: Organizations, jurisdictions, regions, and individuals may designate standards; this makes timekeeping part of governance and social simulation.
- UNCERTAIN / UNVERIFIED: Implementation-language/module assumptions from prior assistant text must not be treated as project facts.

## 8. Pending Tasks and Next Actions

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

### 8.1 Recommended Task Order

1. TASK-21: Download and archive this package.
2. TASK-01: Inspect the actual Plan G/The Game architecture.
3. TASK-18: Decide phase-one implementation scope.
4. TASK-03, TASK-04, TASK-05: Resolve key open design details before coding.
5. TASK-06 through TASK-13: Define core schemas/interfaces.
6. TASK-14 and TASK-15: Add tests and documentation.
7. TASK-16: Generate Codex-ready implementation prompt.

### 8.2 Blocked Tasks

- TASK-06 through TASK-12 are blocked on actual codebase/project architecture inspection.
- TASK-02 and TASK-17 are blocked on authoritative external verification.
- TASK-03 is blocked on user/design decision for HPC-E leap rule.

### 8.3 Quick Wins

- Create unique internal IDs for all calendars/time standards.
- Preserve HPC-E as a formal data record.
- Draft KnowledgeCapability IDs for time displays.
- Separate NameSets from calendar algorithms.

### 8.4 Tasks Requiring Verification

- TASK-02, TASK-03, TASK-10, TASK-17, TASK-20.

## 9. Constraints and Requirements

### 9.1 Hard Requirements

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

### 9.2 Soft Preferences

| ID | Constraint | Type | Hard/soft | Source / basis | Practical implication | Violation risk | Confidence | Label |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| CONSTRAINT-13 | Gas giants and Sun do not have planet-surface civil calendars. | content/design | soft-hard | Assistant proposal carried forward | Use scientific/environmental clocks only. | Medium | medium | INFERENCE |

### 9.3 Technical Constraints

| ID | Constraint | Type | Hard/soft | Source / basis | Practical implication | Violation risk | Confidence | Label |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| CONSTRAINT-01 | Core time must be continuous and monotonic. | technical | hard | Repeated doctrine | Use ACT as authoritative now. | High | high | FACT |
| CONSTRAINT-03 | Leap seconds must not enter core simulation time. | technical | hard | Leap-second discussion | UTC rendering only; external table. | Medium | high | FACT |
| CONSTRAINT-04 | Proper time must not become authoritative civil/calendar time. | technical | hard | Relativity discussion | Proper time used only for clocks/aging. | Medium | high | FACT |
| CONSTRAINT-05 | Save files must not persist rendered dates or names as truth. | serialization | hard | Serialization policy | Persist ACT/frame/version IDs. | High | medium-high | INFERENCE |
| CONSTRAINT-06 | Constants and ephemerides must be versioned and pinned per world. | technical | hard | Modularity discussion | Patch updates cannot alter old saves silently. | High | medium-high | INFERENCE |
| CONSTRAINT-22 | Unknown data should yield UNKNOWN, not fabricated output. | robustness | hard | Modularity recommendation | Prevents false UI/gameplay facts. | Medium | medium-high | INFERENCE |
| CONSTRAINT-23 | Implementation should be modular, extensible, reliable, and robust. | architecture | hard | User explicit | Plugin/data-driven design. | Medium | high | FACT |

### 9.4 Time / Resource Constraints

- UNCERTAIN: No explicit implementation timeline or resource budget was established in this chat.
- INFERENCE: Scope should be phased because the system spans time core, calendars, astronomy, UI, governance, and data.

### 9.5 Legal / Ethical / Safety Constraints

- FACT: No legal/ethical safety constraint specific to this design was established beyond accuracy, provenance, and not inventing facts.
- INFERENCE: Jurisdiction/calendar conflicts may affect in-game law/contracts and should be modeled carefully.

### 9.6 Evidence / Citation Requirements

- FACT: User profile values fact-checking and correctly cited sources.
- FACT: External-world facts, astronomy values, constants, standards, and APIs must be verified before future use.

### 9.7 Formatting / Output Requirements

| ID | Constraint | Type | Hard/soft | Source / basis | Practical implication | Violation risk | Confidence | Label |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| CONSTRAINT-24 | This report must cover this chat only. | reporting | hard | Current user request | Do not summarize whole project. | Medium | high | FACT |
| CONSTRAINT-25 | Important items must be labelled FACT/INFERENCE/UNCERTAIN/PROJECT-CONTEXT. | reporting | hard | Current user request | Preserve reliability states. | Medium | high | FACT |

### 9.8 Things to Avoid

- Do not persist rendered dates as truth.
- Do not treat assistant-generated astronomy as verified.
- Do not assume Plan G implementation details.
- Do not collapse player knowledge into omniscient UI.
- Do not treat tentative names/leap rules as final.

## 10. Open Questions and Unresolved Issues

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

## 11. Rejected, Superseded, or Deprioritised Options

| ID | Option | Status | Reason rejected/superseded/deprioritised | Is rejection final? | Reconsider conditions | Related workstream | Label |
| --- | --- | --- | --- | --- | --- | --- | --- |
| REJECTED-01 | Simulate every star/asteroid/galaxy explicitly. | rejected | Scale explosion and redundancy. | final principle | Reconsider only if object becomes gameplay-critical. | WORKSTREAM-01 | FACT |
| REJECTED-02 | Named real stars only Sol. | superseded | User requested dozens to hundreds of real Milky Way systems. | final for backbone | No blanket Sol-only real names. | WORKSTREAM-01 | FACT |
| REJECTED-03 | Individual asteroids/comets fully explicit by default. | rejected | Too much redundancy; fields better for most. | final default | Major named/player-relevant objects can be explicit. | WORKSTREAM-01 | FACT |
| REJECTED-04 | Civil calendar on Sun. | rejected | No civil habitation on Sun; environmental cycles only. | final | Artificial solar habitats can have their own standards. | WORKSTREAM-04 | INFERENCE |
| REJECTED-05 | Civil calendars on gas giants themselves. | rejected | No lived surface; moons/habitats carry calendars. | mostly final | Floating habitats may define habitat standards. | WORKSTREAM-04 | INFERENCE |
| REJECTED-06 | Leap seconds inside core simulation time. | rejected | Discontinuous and political; breaks computation. | final | Never; display only. | WORKSTREAM-02 | FACT |
| REJECTED-07 | Calendar-driven physics time. | rejected | Breaks causality and determinism. | final | Never. | WORKSTREAM-02 | FACT |
| REJECTED-08 | Proper time as authoritative calendar time. | rejected | Frame-dependent and desynchronizing. | final | Proper time only derived. | WORKSTREAM-02 | FACT |
| REJECTED-09 | Universal/galactic ordinary months/weeks/years. | rejected | Meaningless at scale. | final | Use metadata/lore labels only if needed. | WORKSTREAM-05 | FACT |
| REJECTED-10 | January 0 for intercalary days. | rejected by user | User explicitly avoided January 0. | final | Never. | WORKSTREAM-03 | FACT |
| REJECTED-11 | 14th pseudo-month for intercalary days. | rejected/proposed not recommended | Conflicts with February sink and adds edge cases. | tentative-final | Reconsider only if compatibility systems cannot handle tokens/projection. | WORKSTREAM-03 | INFERENCE |
| REJECTED-12 | Intercalary days as normal canonical February dates. | rejected | Breaks no-week/no-month invariant. | final for canonical | Compatibility projection only. | WORKSTREAM-03 | INFERENCE |
| REJECTED-13 | Forced initial HUD clock/date. | rejected by user | Player starts with no timekeeping devices/calendars. | final | Only scenarios granting devices can show time. | WORKSTREAM-07 | FACT |
| REJECTED-14 | Single hidden global standard calendar for all actors. | rejected by design | User wants orgs/jurisdictions/individuals to designate standards. | final | Use TimeStandard pluralism. | WORKSTREAM-08 | FACT |
| REJECTED-15 | Silent patching of constants/ephemerides/calendar algorithms. | rejected | Would corrupt saves/replays. | final principle | Use versioning and migrations. | WORKSTREAM-09 | INFERENCE |

Preserving rejected options prevents future assistants from repeatedly proposing designs that were already ruled out, such as January 0, leap seconds in core, or an omniscient initial clock HUD.

## 12. Artifact Ledger

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

## 13. Rationale and Assumptions

### 13.1 Rationale

- FACT: Core time/calendar separation exists to protect determinism and causality.
- FACT: Leap seconds are display-only because they are Earth-civil corrections and discontinuous.
- FACT: Sol system is explicit because the user said most playtime will be spent there.
- FACT: Player time ignorance exists because the user wants diegetic HUD realism and no starting timekeeping devices.
- FACT: Governance standards exist because the user explicitly allowed organizations, regions, jurisdictions, and individuals to designate standards.
- INFERENCE: Plugin/data-driven architecture is necessary because the number of calendars and standards is too large for ad-hoc hardcoding.
- INFERENCE: Explicit/procedural/parametric celestial classification preserves gameplay density and performance.

### 13.2 Assumptions

- UNCERTAIN / UNVERIFIED: The actual project has engine/game separation compatible with the proposed architecture.
- UNCERTAIN / UNVERIFIED: The assistant-generated orbital constants and celestial lists are accurate.
- UNCERTAIN: Non-Earth calendar names are final.
- UNCERTAIN: HPC-E leap rule is unresolved.
- UNCERTAIN: The exact default epoch time scale is unresolved.

## 14. Risks and Failure Modes

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

## 15. Verification Queue

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

## 16. Spec Book Contribution Notes

### Likely chapters/sections

- Time Core and Coordinate Frames.
- Calendar and Chronology Systems.
- Perfect Earth Calendar.
- Planetary and Moon Calendars.
- Diegetic HUD and Knowledge/Fog-of-War.
- Governance, Jurisdictions, and Time Standards.
- Celestial Content Scope.
- Sol System High-Fidelity Content.
- Galactic and Universal Scale Abstractions.
- Serialization, Versioning, and Testing.

### Unique contributions from this chat

- FACT: Full time/calendar doctrine from ACT to UEF.
- FACT: User-defined HPC-E month order and intercalary rules.
- FACT: Default world start and local sunrise spawn.
- FACT: Diegetic no-time-HUD start.
- FACT: Time standards as governance/jurisdiction/player objects.
- FACT: Celestial explicit/procedural/parametric scope.

### Overlaps likely duplicated in other chats

- PROJECT-CONTEXT: Governance and jurisdictions likely appear in The Game/Plan G.
- PROJECT-CONTEXT: Knowledge/fog-of-war likely appears elsewhere.
- PROJECT-CONTEXT: Engine/game modularity likely appears elsewhere.
- PROJECT-CONTEXT: Celestial content may overlap with world-generation/system-map chats.

### Conflicts to watch for

- Existing project time/date system may conflict with ACT/calendar-renderer doctrine.
- Existing HUD may assume omniscient clock/date display.
- Existing governance may not support plural standards.
- Existing celestial scale design may differ from explicit/procedural/parametric classification.

### Formal requirements candidates

- ACT as authoritative time.
- Calendars as pure renderers.
- No leap seconds in core.
- HPC-E final structure.
- No initial time/date HUD.
- TimeStandard data model.
- Versioned constants/ephemerides.

### Background context candidates

- Assistant-proposed names for non-Earth calendars.
- Gameplay mechanics mappings.
- Initial Milky Way system list.
- Suffix prompt constants/equations.

### Needs user confirmation before becoming spec

- HPC-E leap rule.
- Non-7-day cycle terminology.
- Non-Earth calendar names.
- Phase-one implementation scope.

## 17. What Future Assistants Must Preserve

| Priority | Item | Type | Why it matters | Risk if lost | Label | Confidence |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | ACT is authoritative; calendars are renderers | core doctrine | Protects simulation determinism | Physics/date corruption | FACT | high |
| 2 | HPC-E final month order and weekdays | calendar decision | User explicitly specified it | Wrong calendar implementation | FACT | high |
| 3 | Year Day/Leap Day after February; no January 0 | calendar decision | User explicitly wanted this | Reintroduces rejected option | FACT | high |
| 4 | Default date anchor Jan 1 2000 Gregorian | world start | User explicitly specified it | Wrong default world start | FACT | high |
| 5 | Player spawns at local sunrise | world start | User explicitly specified it | Wrong initial experiential state | FACT | high |
| 6 | No initial clock/calendar/date HUD | gameplay/UI | Core diegetic requirement | HUD breaks premise | FACT | high |
| 7 | Player-created and provided calendars both allowed | gameplay/system | User explicitly specified it | Loss of agency | FACT | high |
| 8 | Organizations/jurisdictions/individuals may designate standards | governance | User explicitly specified it | Governance integration lost | FACT | high |
| 9 | Sol system high fidelity | content | Most playtime in Sol | Core play space underdeveloped | FACT | high |
| 10 | Celestial data must be verified | verification | Assistant list may contain errors | False astronomy hardcoded | UNCERTAIN / UNVERIFIED | high |
| 11 | Do not assume Plan G/codebase details | process | This chat lacked access | Bad Codex prompt | FACT | high |
| 12 | Version/pin constants and ephemerides | robustness | Prevents patch drift | Save corruption | INFERENCE | medium-high |
| 13 | Separate NameSets from algorithms | modularity | Supports localization/naming changes | Hardcoded labels | INFERENCE | medium |
| 14 | Use TimeStandard data objects | governance architecture | Plural standard support | Hardcoded one calendar | FACT / INFERENCE | medium-high |
| 15 | Preserve uncertainty labels | aggregation | Avoids fossilizing brainstorms | Wrong spec decisions | FACT | high |

## 18. What Future Assistants Must Not Assume

- UNCERTAIN / UNVERIFIED: That Domino is definitely C89 and Dominium is definitely C++98.
- UNCERTAIN / UNVERIFIED: That any assistant-generated astronomical list is accurate.
- UNCERTAIN: That non-Earth calendar names are final.
- UNCERTAIN: That the HPC-E leap rule is decided.
- UNCERTAIN: That compatibility Feb29/Feb30 is default rather than optional.
- UNCERTAIN: That The Game chat has no existing conflicting time/date system.
- UNCERTAIN: That all gas giant moon calendars should be implemented in phase one.
- UNCERTAIN: That all prompt artifacts should be used verbatim; this report supersedes them.

## 19. Recommended Next Action

If continuing this chat’s work alone: download this package, then finalize the HPC-E leap rule and verify the celestial/constant data.

If aggregating with other chat reports: ingest this package as the chronology/celestial-scope report, then compare it against The Game/Plan G reports for governance, knowledge, fog-of-war, engine architecture, and world generation.

User verification needed before acting: confirm HPC-E leap rule, non-Earth calendar naming policy, implementation phase-one scope, and whether compatibility Feb29/Feb30 should be default.

## 20. Appendix: Possibly Relevant Details

## A. Celestial content scope

### Universe-scale structures
- FACT: Observable universe.
- FACT: Expansion metric / cosmological model.
- FACT: Cosmic horizon / light-cone limits.
- FACT: Large-scale structure fields: filaments, voids, walls.
- FACT: Cosmic background radiation as noise floor/metadata.
- FACT: These are parametric, not fully discrete.

### Named galaxies and classes discussed
- FACT: Milky Way.
- FACT: Andromeda Galaxy.
- FACT: Triangulum Galaxy.
- FACT: Dwarf satellite galaxies as a class.
- FACT: Other galaxies remain background/statistical unless made gameplay-relevant.

### Milky Way structures
- FACT: Galactic disk, spiral arms, inter-arm regions, galactic bar, galactic core, galactic halo, dark-matter halo.
- FACT: Galactic barycenter and Sagittarius A*.
- FACT: Open clusters, globular clusters, stellar nurseries, star-forming regions, ancient halo populations.

### Proposed Milky Way real-system backbone requiring verification
UNCERTAIN / UNVERIFIED: Sol, Alpha Centauri, Proxima Centauri, Barnard’s Star, Wolf 359, Lalande 21185, Sirius, Luyten 726-8, Ross 154, Ross 248, Epsilon Eridani, Tau Ceti, TRAPPIST-1, LHS 1140, Kepler-186, Kepler-452, Gliese 667, HD 40307, Vega, Altair, Rigel, Betelgeuse, Deneb, Spica, Cygnus X-1, V404 Cygni, Crab Pulsar, Vela Pulsar, PSR B1257+12, SN 1987A, Pleiades, Hyades, Omega Centauri, 47 Tucanae, Orion Nebula, Eagle Nebula, Sagittarius A*, Arches Cluster, Quintuplet Cluster, Carina Nebula, Lagoon Nebula, Trifid Nebula, Westerlund 1, NGC 3603, Messier 92, Messier 13, Kapteyn’s Star, HE 1523-0901, Tabby’s Star, Fomalhaut.
UNCERTAIN / UNVERIFIED: SN 1987A likely requires correction because it is commonly associated with the Large Magellanic Cloud, not the Milky Way.

### Sol system explicit scope
FACT: Sun layers/sites: core, radiative zone, convective zone, photosphere, chromosphere, corona, heliosphere, termination shock.
FACT: Inner bodies: Mercury, Venus, Earth, Moon, Mars, Phobos, Deimos.
FACT: Asteroid/debris: main belt, Ceres, Vesta, Pallas, Hygiea, near-Earth asteroid populations, Jupiter Trojans.
FACT: Giants: Jupiter, Saturn, Uranus, Neptune.
FACT: Major moons: Io, Europa, Ganymede, Callisto; Titan, Enceladus, Rhea, Iapetus, Dione, Tethys; Miranda, Ariel, Umbriel, Titania, Oberon; Triton, Proteus, Nereid.
FACT: Ring systems: Saturn rings A–G individually; Jupiter rings simplified; Uranus rings; Neptune rings.
FACT: TNO/Oort: Kuiper Belt, Pluto, Charon, Haumea, Makemake, Eris, scattered disk, detached Sedna-class, ʻOumuamua-class interlopers, inner and outer Oort Cloud, long-period comets.
FACT: Orbital/meta sites: low/high orbit, resonant orbits, stable parking orbits, L1–L5, Trojan regions, transfer windows, gravity-assist corridors, low-energy manifolds.

## B. Core calendar/time inventory

FACT: Foundational: ACT, BST/SBT, GCT, CPT, CDC, UTM, OET, HDTF.
FACT: Sol: SCT, SEC.
FACT: Sun: Carrington rotation, solar activity epochs; no civil calendar.
FACT: Earth: Gregorian, Julian, Islamic, Hebrew, Chinese, Persian, Holocene, Metric/French Revolutionary, HPC-E.
FACT: Luna: LMST, Lunar Month Count, SBLC, HSC-Lu.
FACT / UNCERTAIN: Mercury: Mercury Solar Day, Orbital Year, Sidereal Rotation Count, Mean Solar Time, RCC, OIC-Me, HHC.
FACT / UNCERTAIN: Venus: VSD, VSRC, VOY, VMST, VLDC, OHSC-V, HAC-V.
FACT / UNCERTAIN: Mars: MSD, MTC, MY, LMST, Darian, Allison–McEwen, Metric Mars, HAC-Mars.
FACT / UNCERTAIN: Jupiter system: JST, JCT, JRC; Io HVC-Io, Europa HOC-Eu, Ganymede HMC-Ga, Callisto HFC-Ca.
FACT / UNCERTAIN: Saturn system: SST, Saturn coordinated time, SRC, ring shadow epochs; Titan HTC, Enceladus HCC-En, Rhea HLC-Rh, Iapetus HDC-Ia.
FACT / UNCERTAIN: Uranus system: UST, UCT, URC, USL; Miranda HFC-Mi, Ariel HRC-Ar, Umbriel HSC-Um, Titania HAC-Ti, Oberon HIC-Ob.
FACT / UNCERTAIN: Neptune system: NST, NCT, NRC, NSL; Triton HTC-Tr, Proteus HIC-Pr, Nereid orbital epoch only.
FACT / UNCERTAIN: Pluto/TNOs: Pluto Sol, Pluto Orbital Epoch, BEC-Pl, HKC-Pl, OET, HDTF.
FACT: Galactic: GalCT, GEC.
FACT: Universal: UCT, UEF.

## C. Exact user wording that matters

FACT: Perfect Earth Calendar wording from user:
> the existing names for the days of the week, starting with Monday, and ending with Sunday.
> The existing months of the year from the english Gregorian calendar, starting with march at the beginning of spring, December being the 10th month, the 11th mnth having a historically proposed name, and the 12th month being January and ending with the 13th month February which will be appended with all leap or non calendar days, avpiding January 0th designation.

FACT: World/start/HUD wording from user:
> Each world/universe can be instantiated at a different starting date and time.
> By default, I want the game to start on the date Jan 1st, 2000 AD Gregorian, and as for the time I want it to start at sunrise on whatever planet or local time zone solar time the player spawns in.
> In the beginning, there will be no available information to display in the HUD (which will be a diegetic HUD to feel realistic and to work well with VR) BECAUSE the player won't have any time keeping devices or calendars.
> Players should be able to define their own timekeeping and date keeping or choose from one of the provided calendars and clocks which we have defined in this chat.
> Organisations, regions, jurisdictions, and individuals may designate systems to use as standard.

