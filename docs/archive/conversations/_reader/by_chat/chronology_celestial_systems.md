Status: DERIVED
Last Reviewed: 2026-05-28
Supersedes: none
Superseded By: none
Stability: provisional
Result: reader_page_generated
Binding Sources: `docs/canon/constitution_v1.md`, `docs/canon/glossary_v1.md`, `AGENTS.md`, `docs/planning/AUTHORITY_ORDER.md`, `docs/planning/SNAPSHOT_INTAKE_PROTOCOL.md`
Authority Class: advisory_only
Source Class: conversation_handoff_export
Source Folder: `docs/archive/conversations/Chronology_Celestial_Systems/`
Promotion Status: not_reviewed

# Dominium Chronology & Celestial Systems - Conversation Reader

This reader page is derived from archived conversation material. It cannot override canon, contracts, schema law, current queue state, live repo structure, or validated repo artifacts.

## What This Conversation Was About

This chat was mainly about designing a major subsystem for the Dominium Game project: how the game should represent celestial bodies, astronomical structures, time, calendars, dates, clocks, local standards, diegetic HUD knowledge, and large-scale chronology across Earth, the Sol system, the Milky Way, and the universe.

The conversation began with a practical worldbuilding and simulation-design question: if the game logically simulates the universe, which celestial bodies and systems should be included without making the simulation bloated or redundant for gameplay? That initial question expanded into a much larger architecture. The user clarified that the game operates at multiple scales: planetary Earth, the Sol system, the Milky Way, and the universe. That scale ladder became the foundation for almost everything that followed.

A central design theme emerged: not everything should be simulated at the same fidelity. The Sol system should be represented in great detail because the user explicitly said most playtime will happen there. The Milky Way should have a backbone of real, named systems and sites, plus procedural expansion. The universe should mostly be parametric or abstract, using large-scale structures like filaments, voids, horizons, and cosmic epochs rather than hand-simulating every galaxy. The underlying principle became: a celestial object or region should be explicit if it changes gameplay, navigation, physics, history, or player decisions; otherwise it should be procedural, statistical, or omitted.

## Why It Mattered

This conversation matters as historical context for the topics tagged here: architecture, content, contracts_schema, governance, platform, simulation, timekeeping, tooling, ui, worldgen. Its value is explanatory and evidentiary, not authoritative. Any claim must be checked against current repo artifacts before promotion.

## What Was Discussed

The package appears to be a `conversation_handoff_package` with `8` source files. The primary extracted source is `docs/archive/conversations/Chronology_Celestial_Systems/Dominium_Chronology_Celestial_Systems__human_readable_chat_report.txt`.

## What Was Decided

- This reinforced the core celestial-content rule: locations should exist explicitly when they change player decisions.
- This became the spatial foundation for later time/calendar decisions because every major body or region could potentially have its own local time, calendar, or operational standard.
- The assistant formalized this as the Perfect Earth Calendar, later called HPC-E. The final structure is clear, though the exact leap rule remains unresolved.
- This material is useful but less final than the Earth calendar. The user asked to apply the same approach broadly, but did not individually confirm every name or number. The final package correctly marks these as needing review.
- The final state is that this chat became both a design discussion and a packaged source document for future aggregation.
- The conclusion was not "simulate everything." The conclusion was to classify content by relevance. Explicit objects are justified when they create gameplay, physics, navigation, history, strategy, or meaningful decisions. Otherwise, they should be procedural or statistical.
- What remains uncertain is the exact verified object list. The assistant generated a real Milky Way system list, but that list must be checked before becoming data.
- The conclusion was that every explicit celestial feature should change player decisions in at least one way. If it does not, it probably should not be explicit.
- The unresolved issue is exact fidelity. The chat specified what should exist conceptually, but not the final data schema, map resolution, object attributes, or implementation priority.
- The central time philosophy is that physical time and civil time must be separated. The simulation should not "run on calendars." It should run on monotonic physical time. Calendars are renderers that label time for humans, societies, devices, and UI.
- The most important Earth decision was the custom Perfect Earth Calendar. The user corrected the assistant's earlier generic proposal and specified the actual naming and ordering scheme. The year begins in March, the months are all 28 days, the weekdays remain Monday through Sunday, and intercalary days go after February.
- The reason is that days, months, and years are local conveniences. They stop making sense at galaxy and universe scale. The final principle was that at large scales, duration replaces dates and epochs replace calendars.

## What Was Not Decided

- The assistant formalized this as the Perfect Earth Calendar, later called HPC-E. The final structure is clear, though the exact leap rule remains unresolved.
- What remains uncertain is the exact verified object list. The assistant generated a real Milky Way system list, but that list must be checked before becoming data.
- The unresolved issue is exact fidelity. The chat specified what should exist conceptually, but not the final data schema, map resolution, object attributes, or implementation priority.
- What remains unresolved is the exact mathematical implementation of these frames and how much relativistic fidelity should exist in phase one.
- The uncertainty is high relative to Earth. Many names and structures were assistant-generated and should be reviewed before implementation.
- The unresolved issue is implementation reality. The actual Plan G/The Game codebase was not visible here, so any implementation plan must be reconciled with real architecture.
- The only major unresolved part is the leap rule.
- The user wants rigorous, structured, fact-aware assistance. The user specifically requested preservation of uncertainty labels and does not want assistant suggestions treated as user decisions.
- Future assistants should not invent Plan G details, assume codebase language constraints, hardcode unverified astronomy, treat all assistant-generated calendars as final, flatten tentative items into decisions, or reveal time/date in UI without in-world justification.
- The most important unresolved issue is the real Plan G/The Game architecture. This chat could not inspect it. Any implementation plan must first compare this design to the actual project.
- The second major unresolved issue is the exact HPC-E leap rule. The calendar structure is set, but the leap cadence is not. This must be decided before implementation.
- The third unresolved issue is the exact time-scale mapping for Gregorian January 1, 2000 AD. The user specified the civil date, but not the exact technical instant. This affects deterministic world start.

## Ideas Rejected, Superseded, Or Deprioritised

- The conclusion was that inhabited or operationally important bodies may have local calendars or clocks, but those calendars should still be renderers over physical time. Gas giants and the Sun do not get ordinary civil calendars, because civilizations do not live on their surfaces. Habitats around them may define their own standards.
- The player initially has no time/date HUD because they do not possess clocks, calendars, or timekeeping devices. This means the simulation knows time, but the player does not. Timekeeping becomes diegetic knowledge.
- The sunrise algorithm and time-scale mapping are not finalized.
- The idea of representing every star, asteroid, comet, galaxy, or minor body explicitly was rejected because it creates massive data volume without proportional gameplay value. The design settled on explicit/procedural/parametric representation.
- An earlier narrower approach treated Sol as the only named real star system. That was superseded when the user asked for dozens to hundreds of real Milky Way systems. The final direction is to use a real-system backbone, plus procedural expansion.
- Individual minor bodies were mostly deprioritized in favor of fields, populations, and major exemplars. Ceres, Vesta, Pallas, Hygiea, Pluto, Charon, and other major objects can be explicit, but countless small bodies should be statistical unless they matter.
- The assistant proposed that the Sun and gas giants should not have ordinary civil calendars because civilizations do not live on their surfaces. They can have rotation counts, activity cycles, atmospheric clocks, magnetospheric periods, or habitat standards, but not planet-surface civil calendars.
- Leap seconds were rejected from the simulation core because they are irregular, Earth-specific, and discontinuous. They may appear only in a UTC display renderer.
- The idea that a calendar could affect physics was rejected. Calendars are renderers. Physics uses continuous time.
- Proper time matters for local clocks, aging, and relativistic effects, but making it the basis of civil calendars would create frame-dependent disagreements and log problems. It was rejected as authoritative calendar time.

## What Future Work Came From It

- The final state is that this chat became both a design discussion and a packaged source document for future aggregation.
- What remains unresolved is the exact mathematical implementation of these frames and how much relativistic fidelity should exist in phase one.
- The user asked how to extend calendars beyond planets. The answer was that the larger the scale, the less ordinary calendar structure survives. Sol can have a system-wide civil time and epoch calendar. The Milky Way should use galactic coordinate time and epoch blocks. The universe should use cosmological time and large phases/ages/eras.
- The reason is to avoid losing context across chats and to support a future Project Spec Book. This chat produced many artifacts: prompts, reports, registers, YAML, a ZIP package, and explanatory summaries. The artifacts matter, but the substance remains the design decisions described above.
- It is reasonable to infer that the user wants a future implementation path, likely through another assistant and eventually Codex, but does not want premature code before the broader project context is inspected.
- It is also reasonable to infer that the user wants a future Project Spec Book assembled from multiple old-chat reports, and that this chat should contribute the chronology/celestial/timekeeping chapters.
- This decision makes sense because it separates clean internal logic from messy external software expectations. However, it is less directly user-confirmed than the month order. Future work should ask whether compatibility projection should be default or optional.
- The future project architecture can support data-driven systems.
- This is the most important next step before implementation. The chat discussed how the system should integrate with engine/game systems, but the actual other chat and codebase were not visible here.
- What could go wrong: a future assistant may assume the architecture invented here is real and generate an unusable Codex prompt.
- The user appears to want future Project Spec Book aggregation. This is inferred from the report-package and aggregator-packet workflow.
- Future assistants should not invent Plan G details, assume codebase language constraints, hardcode unverified astronomy, treat all assistant-generated calendars as final, flatten tentative items into decisions, or reveal time/date in UI without in-world justification.

## Important Artifacts

- `manifest`: `1`
- `markdown`: `1`
- `primary_report`: `2`
- `reader_brief`: `1`
- `registers`: `1`
- `spec_sheet`: `1`
- `verification`: `1`

## Verification Needed

- Verify every implementation, platform, tooling, release, and queue claim against current repo artifacts.
- Treat external platform or SDK claims as stale until independently checked.
- Treat old language-baseline claims as historical unless they match current `README.md` and current contracts.
- Do not infer current authority from the existence of this archive package.

## Candidate Promotions

Candidate promotions, if any, are recorded in `_promotion/PROMOTION_QUEUE.md`. This page does not promote claims.

## Do Not Assume

- Do not assume this conversation established current repo truth.
- Do not assume generated package reports are canonical.
- Do not assume old prompts were executed.
- Do not assume unresolved items are safe to implement.
- Do not use this package to open blocked work without stronger current authority.
