Status: DERIVED
Last Reviewed: 2026-05-29
Supersedes: docs/archive/docs_corpus/_integrated_book_v2/**
Superseded By: none
Stability: provisional
Authority Class: advisory_synthesis
Source Root: `docs/`
Conversation Corpus Root: `docs/archive/conversations/`
Promotion Status: not_promoted
Canon impact: unchanged
Contract/schema impact: unchanged
Implementation impact: unchanged
Release impact: unchanged
Queue impact: unchanged

# Open Questions Index

- Crosses unresolved or quarantined ownership areas.
- It is also not currently release-ready. Full CTest and broader release/trust proof remain visible debt outside the normal fast strict development gate.
- Refusal and defer semantics are part of determinism and replay guarantees.
- Inconsistent clients, shard drift, and audit failure.
- 12. Risks, Failure Modes, and What Future Chats Might Get Wrong.
- SDK locking was treated as mandatory. The warning was that allowing a newer Windows SDK to leak into old-floor builds can create symbol/runtime-loader failures and hidden dependency creep.
- Another tradeoff is between a clean theoretical structure and the current repo's transitional debt. The current ownership-root target is good, but the repo still has cleanup work. The safe path is not broad movement by directory name; it is gated.
- The current repo should not be overstated as a complete runtime implementation of all v1 goals.
- Included specific risks about overclaiming implementation status.
- Full agent gameplay loops, MMO distributed authority runtime, embodiment, and narrative/campaign systems were described as deferred in repo status docs.
- Use negative architecture rules to prevent drift.
- 12. Risks, Failure Modes, and What Future Chats Might Get Wrong.
- 12. Risks, Failure Modes, and What Future Chats Might Get Wrong.
- The main unresolved work is converting this concept into a formal spec and vertical slice. The best proposed first slice is: one planet region, one mothership, one robot body, one ore deposit, one power source, one cut/fill tool, one blueprint system.
- The strongest technical identity is sparse deterministic simulation. The world should be generated from seeds and data, modified through sparse deltas and event logs, and expanded into visual detail only when sensed. Distant machines become process.
- Factories and machines should also be multi-representation systems. Nearby, they can look detailed and physical. Far away, they should collapse into process graphs and equations: inputs, outputs, power draw, heat, throughput, buffers, maintenance debt.
- The unresolved detail is the exact representation: voxel chunks, signed-distance functions, heightfields, material fields, climate grids, graph overlays, or hybrid systems.
- The strongest technical design pattern was high-fidelity when sensed, collapsed when not sensed . A factory near the player can be visually rich. It can show belts, arms, lights, sparks, vehicles, modules, robots, and moving parts. Far away, the same.
- Players spawn into manufactured robot bodies. Possible forms include bipeds, quadrupeds, spiders, tank-like frames, drones, heavy industrial bodies, aquatic bodies, and aerial bodies. The exact launch list is deferred.
- 00 Manifest: file list, purpose, caveats, status.
- 12. Risks, Failure Modes, and What Future Chats Might Get Wrong.
- The idea of using open-source games shifted from potential code reuse to reference/research material due to license and architecture risks.
- The unique contribution is the synthesis: Dominium should not be framed only as a game or editor suite; it should be a deterministic operating environment with a reusable interface layer. This likely overlaps with other chats on worldgen, domain realism.
- 7. The current code is promising but not yet the full vision. It is modular at build/source level and partly data-driven, but many runtime pathways are still hard-coded or only partially wired.
- DDAP/DIL is proposed, not yet user-ratified.
- DDAP/DIL is proposed, not yet user-ratified.
- The standards discussion produced a risk-scaled approach. Ordinary UI, lore, concept art, and experiments should not carry heavy assurance burdens. Saves, packs, replay, deterministic state, installers, updaters, signed releases, mod loading, multiplayer.
- Codex prompts were generated; application status is unknown.
- The main managed risks were drift, over-abstraction, lost validation, hidden path assumptions, bad agent memory, and premature feature work. The dominant tradeoff was speed versus safety: moving folders or deleting old tools would look faster but would.
- 11. Open Questions and Unresolved Issues.
- 12. Risks, Failure Modes, and What Future Chats Might Get Wrong.
- The main unresolved goals are backend audit, ACT serialization audit, civil/astronomical projection design, and verification of external platform facts.
- Safe for later aggregation: with caveats.
- This distinction became one of the most important conceptual tools from the chat. A distant planet can exist as procedural data and sparse edits without being actively simulated at per-object fidelity. A factory can exist and produce resources as a.
- Deep primitives and failure ontology gaps.
- How can Dominium grow for years or decades without collapsing into special cases, silent semantic drift, contradictory abstractions, or unmaintainable simulation layers?
- The current project direction should integrate the latest repo state and not ignore Foundation Lock / structure warnings.
- What are the known warnings and blockers?
- 'PACKAGE-MOUNT-SLICE-01' was reported as complete with 'PASS WITH WARNINGS', and the next intended product-spine task was 'REPLAY-PROOF-SLICE-01'.
- UNCERTAIN / UNVERIFIED The exact VM is unresolved.
- The exact module architecture remains unresolved. The exact platform/renderer support matrix remains unresolved. The exact relationship to the current repository remains unresolved because the old snapshot has not been verified. The exact setup trust.
- The most important caveat is that actual repo state is unknown.
- The exact first playable slice remains unresolved. The first provider wedge is clear, but exact sequence between client/workbench gameplay, Robot OS, and gameplay mechanics still needs a formal milestone. The exact Lua version, Linux baseline, current.
- The strongest immediate maintenance tasks are: refresh stale generated evidence, repair launcher pack-verification marker debt if still blocking fast strict, run or audit full CTest/T4 failures, and classify remaining full-gate failures by cause. The.
- Proper time matters for local clocks, aging, and relativistic effects, but making it the basis of civil calendars would create frame-dependent disagreements and log problems. It was rejected as authoritative calendar time.
- 'UNCERTAIN / UNVERIFIED:' Whether the project has similarly named files or modules is unknown.
- The major unresolved issue is taxonomy: how exactly POSIX, SDL1, SDL2, and Native map to Win32, Cocoa, Carbon, X11, Wayland, headless, and retro platforms.
- The unresolved work is to generate this prompt, ideally after inspecting actual content/pack docs and source files. The prompt should probably be staged, because pack integration touches content loading, dependency resolution, audio, rendering, shader.
- Reason: The old plan risked becoming a separate one-off tool architecture. Workbench can instead prove and reuse the same systems as the client, launcher, setup, server, and future tools.
- The conversation did not yet define how those product backends are exposed. That remains the most important unresolved design issue.
- A third unresolved goal is confirming whether command graph, UI IR, binding validation, zero-pack tests, RepoX changelog display, and BUILD-ID mismatch refusal are implemented.
- The unresolved goals are mostly implementation-definition questions.
- The key unresolved point is implementation timing. The report preserves this architecture, but the initial Codex refactor was not supposed to rewrite the entire UI system immediately.
- The main unresolved goals are backend audit, ACT serialization audit, civil/astronomical projection design, and verification of external platform facts.
- The unresolved risk is implementation complexity. Real native tab controls, splitter behavior, and scroll panels can be nontrivial in a child-HWND Win32 UI.
- 6. Broad structure refactor prompts: now deprioritised because current structure is clean enough with warnings.
- The biggest unresolved goal is verifying the actual repository. The package says what was reported, but not what is proven. Another unresolved goal is deciding what comes next: survival, Lab Galaxy UX, distributed SRZ, or documentation polish.
- Old repo snapshot/project attachments, not yet verified.
- The exact first playable slice remains unresolved. The first provider wedge is clear, but exact sequence between client/workbench gameplay, Robot OS, and gameplay mechanics still needs a formal milestone. The exact Lua version, Linux baseline, current.
- Source rules: labels used: "FACT", "INFERENCE", "UNCERTAIN / UNVERIFIED", "PROJECT-CONTEXT" conflict rules.
- Verify latest live repo gate state. If fast-strict/RepoX still fails on stale evidence or launcher marker debt, fix that first. If normal gates are clean, continue with 'PROJECTION-CONFORMANCE-01'.
- The following were not finished or intentionally deferred.
- The following were not finished or intentionally deferred.
- Produce Dominium Technical Roadmap v0.1 using this report as input, explicitly marking every assumption and open question.
- Startup prompt has a linker-risk caveat.
- Workbench remains unresolved at the implementation level: read-only first is agreed, but exact UI shell design, renderer path, modules, and self-hosting milestones remain future tasks.
- Unresolved goals include confirming live repo state, executing pending maintenance and projection prompts, building read-only Workbench, implementing provider manifests/fences, building raylib provider wedge, proving Universe Explorer.
- VM-only vs native plugin policy is unresolved.
- The reason these were deferred is not that they are unimportant. They were deferred because the local playable baseline path is not yet reliable. Feature work before baseline proof would increase uncertainty and project risk.
- TUI is expected for every product, but parity level is unresolved.
- Resolve DSYS vs 'domino sys ' if conflict appears.
- Constitutional conflicts are resolved by this document, not by prompt convenience.
- This is the full canonical glossary v1.0.0. If terminology conflicts with local or legacy docs, this glossary wins.
- Speculative future feature not yet implemented.
- Continue documentation and evidence updates that keep remaining warnings and full-gate debt visible.
- Current state: process guard scaffolding exists, but mutation sites are not yet uniformly wrapped.
- Time, energy, fuel, bandwidth, economic, risk.
- Effective frozen mod policy remains 'mod policy.lab'; requested strict baseline policy is recorded separately to avoid drifting the Omega-1 pack lock.
- Ready for DIST-1 packaging pass: not yet.
- No reference mismatches were observed in GR3 FULL runs.
- On boot failure or supervised spawned-process exit.
- Stop conditions exist for every phase and for the high-risk hot-reload, distributed, and agent-automation cases.
- Implementation evidence outranked prose when the two disagreed.
- Deferred rows left untouched: '253' dangerous-root residuals, plus later Xi-5b/Xi-5c deferred rows outside this pass.
- Auditx Summary: INFO: 1 RISK: 3122 VIOLATION: 16 WARN: 1284.
- Convergence Risk Report: Generated: 2026-03-26 Fingerprint: '73aac832765e57652be4b887b21ed0921dcd29647971d4707ff93f0d11fee505' HIGH risk actions: 16676 MED risk actions: 9465 LOW risk actions: 920.
- Deferred rows still present under dangerous roots: '253'.
- Branch roles distinguish canonical, integration, task, release, hotfix, deploy, and unknown branches. Role classification is evidence for review and does not promote, merge, delete, or publish branches by itself.
- Conflicts are expected and must be shown. If a higher-precedence standard is blocked by knowledge or access, the result is UNKNOWN and resolution proceeds. Different actors may legitimately disagree on time/date; conflicts are visible.
- The MOVE-BULK wave is not closed cleanly. This audit records remaining root debt after the only completed apply batch, 'MOVE-BULK-01-APPLY-DOCS-ARCHIVE'.
- 'AIDE-MOVE-01-PLAN ? First Low-Risk Move Plan'.
