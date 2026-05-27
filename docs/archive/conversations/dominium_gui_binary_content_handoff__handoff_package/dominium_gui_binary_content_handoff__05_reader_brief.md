# Reader Brief — Dominium GUI/Binary + CONTENT0 Handoff

## What This Chat Was About

This chat preserved two connected Dominium / Domino planning threads. The first was CONTENT0, a data/schema/docs-only canonical content prompt for universe, Milky Way, Sol, Earth, populations, civilizations, economies, technology, history, and start scenarios. The binding content principle is that nothing appears without causal provenance: entities must be created, populations born, cities built, resources extracted or produced, and civilizations historically emerged. An assistant produced a cleaned CONTENT0 prompt, but the user then corrected the process: discussion must happen before planning or generating prompts. Treat that cleaned prompt as draft only.

The second and current main thread was GUI and binary planning. The user decided to redo GUIs from scratch. Every product should always work through CLI, is expected to work through TUI, and may have multiple modular GUIs attached to product backends to compile native applications. Products include setup, launcher, client, server, tools, and related products. Windows frontends proposed by the user: Win32 ANSI x86 for setup/client; Win32 Unicode x64/ARM64 for setup/client; WinForms .NET Framework family for launcher/server; WinUI 3 x64/ARM64 for launcher/server. macOS frontends proposed: AppKit for setup/launcher/client/server and SwiftUI for future launcher/server. Linux and Android are in scope but undecided.

The next chat should not start coding. It should first define GUI/binary doctrine, the shared backend/UI contract, product matrix, platform matrices, compatibility lanes, visual profiles, packaging strategy, and build/toolchain verification plan.

## Most Important Things to Know

- GUI rebuild from scratch is an explicit user decision.
- CLI is mandatory for every product.
- TUI is expected for every product, but parity level is unresolved.
- Modular GUIs attach to shared product backends.
- Backend/UI contract is the first unresolved architecture issue.
- Windows frontend families are user-specified but need build-lane normalization.
- WinForms old .NET support needs real target/build lanes; verify before use.
- macOS AppKit/SwiftUI lanes are user-specified but macOS 10.9 needs verification/toolchain decision.
- Linux stack is not chosen.
- Android role/stack is not chosen.
- CONTENT0 is content-layer-only and provenance-driven.
- Assistant-generated CONTENT0 prompt is not final.
- Default datapack should include Milky Way and high-detail Sol.
- External platform/toolchain facts must be reverified.
- Do not treat assistant suggestions as user decisions.

## Active Plans or Workstreams

- WORKSTREAM-06 — GUI and binary rebuild.
- WORKSTREAM-07 — Shared backend/UI contract.
- WORKSTREAM-08 — Windows frontend family matrix.
- WORKSTREAM-09 — macOS frontend family matrix.
- WORKSTREAM-10 — Linux frontend strategy.
- WORKSTREAM-11 — Android frontend strategy.
- WORKSTREAM-15 — TUI doctrine.
- WORKSTREAM-01 through WORKSTREAM-05 — paused content/universe/datapack work.

## Decisions Already Made

- DECISION-01 — CONTENT0 is data/schema/docs-only.
- DECISION-02 — Content requires causal provenance.
- DECISION-03 — Discuss before generating further content prompts.
- DECISION-06 — Redo GUIs from scratch.
- DECISION-07 — CLI always works.
- DECISION-08 — TUI expected.
- DECISION-09 — Modular GUIs attach to backends.
- DECISION-10 — Windows frontend family list.
- DECISION-12 — macOS AppKit/SwiftUI family list.

## Pending Tasks

- TASK-01 — Define GUI/binary doctrine.
- TASK-02 — Define backend/UI contract.
- TASK-03 — Build product matrix.
- TASK-04/TASK-05 — Build Windows/macOS matrices.
- TASK-06/TASK-07 — Decide Linux/Android strategies.
- TASK-08 — Define TUI parity.
- TASK-10/TASK-11 — Define packaging and build/toolchain matrix.
- TASK-12 — Inspect repo/files before implementation.

## Open Questions

- What is the backend/UI contract shape?
- Should stable C ABI be used?
- Is the client host-native, renderer-driven, or hybrid?
- What TUI parity level is required?
- What exact Windows and .NET floors are required?
- Is macOS 10.9 a hard requirement?
- What Linux GUI stack should be used?
- What is Android's role?

## Files / Artifacts / Prompts to Preserve

- ARTIFACT-01 — Original CONTENT0 prompt.
- ARTIFACT-02 — Assistant cleaned CONTENT0 draft, draft only.
- ARTIFACT-03 — Assistant CONTENT0 critique.
- ARTIFACT-07 — User GUI rebuild decision and frontend list.
- ARTIFACT-10 — Previous Context Transfer Packet.
- ARTIFACT-19 — This final report package.

## What to Verify Before Acting

- Actual repository/files.
- Windows App SDK / WinUI 3 support floor.
- .NET Framework targeting and Visual Studio support.
- macOS/Xcode deployment floors and old SDK availability.
- Linux toolkit/package strategy.
- Android product role and API floor.
- TUI parity expectations.
- Backend contract feasibility.

## Best Next Step

Define the GUI/binary architecture doctrine and backend/UI contract first, then map products and platforms into matrices. Do not generate code or final prompts until those decisions are explicit.
