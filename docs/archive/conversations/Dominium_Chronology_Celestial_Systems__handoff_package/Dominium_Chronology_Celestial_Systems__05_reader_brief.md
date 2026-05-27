# Reader Brief — Dominium Chronology & Celestial Systems

## What This Chat Was About

This chat defined a major Dominium Game subsystem covering celestial scope, time, calendars, chronology, diegetic time knowledge, and governance standards. It began with the question of what celestial objects and systems should be included in a logical universe simulation without redundant gameplay. The resulting content doctrine is scale-aware: Sol system gets maximum explicit detail because most playtime will occur there; the Milky Way uses a named real-system backbone plus procedural/statistical expansion; the universe uses parametric cosmological structures.

The chat then developed a time architecture. The core rule is that time is continuous and authoritative, while calendars are interfaces. Atomic Continuous Time (ACT) is the simulation truth. Barycentric Sol Time, Galactic Coordinate Time, and Cosmological Proper Time support larger scales. Calendars, civil clocks, and naming systems are stateless renderers. Leap seconds are display-only. Proper time is derived for clocks/biology but never authoritative.

The most important specific calendar is the user-defined Perfect Earth Calendar (HPC-E): 13 months of 28 days, weekdays Monday–Sunday, year begins in March, month order March through February with Undecember as the 11th month, and all intercalary days appended after February. Year Day and Leap Day are canonically outside weeks/months, with optional compatibility projection to February 29/30.

The user also specified world start and UI rules: default date anchor is Gregorian January 1, 2000 AD, but the player spawns at local sunrise. At game start the player has no clock, calendar, date, or time HUD. Time/date knowledge is diegetic and must come from devices, calendars, organizations, jurisdictions, networks, or custom player-defined systems.

## Most Important Things to Know

- FACT: ACT is authoritative; calendars are renderers only.
- FACT: Leap seconds are not in core.
- FACT: Proper time is derived, not authoritative.
- FACT: Sol system is the highest-detail play area.
- FACT: HPC-E month order and weekday names are user-defined and must be preserved.
- FACT: No January 0; intercalary days go after February.
- FACT: Default date anchor is Gregorian Jan 1, 2000 AD.
- FACT: Spawn time is local sunrise where possible.
- FACT: Player starts with no time/date HUD.
- FACT: Players can define calendars/clocks.
- FACT: Orgs, regions, jurisdictions, and individuals can designate standards.
- UNCERTAIN: HPC-E leap rule is not finalized.
- UNCERTAIN / UNVERIFIED: Assistant-generated astronomy data requires verification.
- UNCERTAIN / UNVERIFIED: Actual Plan G/The Game implementation details were not accessible.

## Active Plans or Workstreams

- WORKSTREAM-01: Multi-scale celestial content architecture (high)
- WORKSTREAM-02: Authoritative time core and coordinate frames (high)
- WORKSTREAM-03: Earth calendars and Perfect Earth Calendar (HPC-E) (high)
- WORKSTREAM-04: Planetary, moon, Pluto, and TNO calendars (medium-high)
- WORKSTREAM-05: Sol-wide, galactic, and universal epoch systems (medium-high)
- WORKSTREAM-06: World instantiation and local sunrise start (high)
- WORKSTREAM-07: Diegetic HUD, time knowledge, and fog-of-war (high)
- WORKSTREAM-08: Governance, jurisdictions, organizations, and time standards (high)
- WORKSTREAM-09: Modularity, extensibility, reliability, and integration architecture (high)
- WORKSTREAM-10: Prompt handoff and report packaging (high)

## Decisions Already Made

- DECISION-01: Game operates across Earth, Sol, Milky Way, and universe scales. [FACT]
- DECISION-02: Sol system receives maximum explicit detail. [FACT]
- DECISION-03: Celestial content uses explicit/procedural/parametric classification. [INFERENCE]
- DECISION-04: Atomic Continuous Time (ACT) is authoritative simulation time. [FACT]
- DECISION-05: Use coordinate frames BST, GCT, and CPT above ACT. [FACT]
- DECISION-06: Calendars are pure renderers and never affect physics. [FACT]
- DECISION-07: Leap seconds are display-only and absent from core time. [FACT]
- DECISION-08: Proper time is derived only; calendars render coordinate time. [FACT]
- DECISION-09: Earth supports Gregorian, Julian, Islamic, Hebrew, Chinese, Persian, Holocene, Metric/French Revolutionary calendars. [FACT]
- DECISION-10: Perfect Earth Calendar has 13 months × 28 days and Monday–Sunday weeks. [FACT]
- DECISION-11: Perfect Earth Calendar month order is March through February with Undecember as 11th month. [FACT]
- DECISION-12: HPC-E Year Day and Leap Day are appended after February; canonical mode is undated and compatibility mode may use Feb 29/30. [FACT / INFERENCE]
- DECISION-13: Default world date anchor is Gregorian January 1, 2000 AD. [FACT]
- DECISION-14: Player spawn time is local sunrise at spawn location. [FACT]
- DECISION-15: Player starts with no clock/calendar/date HUD. [FACT]

## Pending Tasks

- TASK-01: Inspect actual Plan G/The Game architecture before implementation planning. (high)
- TASK-02: Verify celestial body/system lists against authoritative astronomy sources. (high)
- TASK-03: Finalize HPC-E leap rule. (high)
- TASK-04: Resolve acronym collisions and internal calendar IDs. (medium)
- TASK-05: Normalize week vs work-cycle terminology. (medium)
- TASK-06: Define TimeCore schema and API. (high)
- TASK-07: Define calendar renderer/plugin interface. (high)
- TASK-08: Define TimeStandard schema. (high)
- TASK-09: Define KnowledgeCapability schema for time/date access. (high)
- TASK-10: Define deterministic sunrise/fallback algorithm. (high)
- TASK-11: Define serialization/save policy. (high)
- TASK-12: Build recurrence/scheduling model. (medium)

## Open Questions

- QUESTION-01: What is the actual Plan G/The Game architecture?
- QUESTION-02: Are Domino C89 / Dominium C++98 constraints real?
- QUESTION-03: What exact time scale maps Jan 1 2000 to ACT?
- QUESTION-04: What exact definition of sunrise is used?
- QUESTION-05: What is the exact HPC-E leap rule?
- QUESTION-06: Should compatibility projection Feb 29/Feb 30 be default?
- QUESTION-07: How many real Milky Way systems should be explicit?
- QUESTION-08: Which assistant-listed celestial systems are scientifically correct?
- QUESTION-09: Which exoplanets/sites per Milky Way system are explicit?
- QUESTION-10: Which planetary/moon calendar names are final?
- QUESTION-11: Should non-7-day cycles be weeks or work cycles?
- QUESTION-12: Do engineered mythological names remain despite no-mythology rule?

## Files / Artifacts / Prompts to Preserve

- ARTIFACT-08: Final HPC-E definition.
- ARTIFACT-12: Leap seconds/relativity doctrine.
- ARTIFACT-13: World initialization/time discovery addendum.
- ARTIFACT-15: The Game handoff prompt.
- ARTIFACT-16: Celestial content inventory.
- ARTIFACT-17: Maximum-fidelity context transfer packet.
- ARTIFACT-18: This final report package.

## What to Verify Before Acting

- Actual Plan G/The Game architecture.
- Codebase language/module assumptions.
- Celestial system list.
- Orbital/rotation constants.
- HPC-E leap rule.
- Non-Earth calendar names and cycle terminology.
- Sunrise algorithm and epoch mapping.

## Best Next Step

Use this package in the new The Game/Plan G chat. First reconcile it with the actual project architecture. Then generate a phased Codex implementation/documentation/testing prompt, preserving uncertainty labels and not assuming codebase details from this chat.
