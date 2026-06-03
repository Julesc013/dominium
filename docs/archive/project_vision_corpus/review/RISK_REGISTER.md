Status: DERIVED
Last Reviewed: 2026-06-03
Supersedes: none
Superseded By: none
Stability: provisional
Authority Class: advisory_synthesis
Source Root: `docs/archive/conversations/`
Promotion Status: not_promoted
Canon impact: unchanged
Contract/schema impact: unchanged
Implementation impact: unchanged
Release impact: unchanged
Queue impact: unchanged

# Risk Register

Risks, contradictions, and drift patterns to preserve for review.

- - `SPEC-DEEP-PRIMITIVES-01` - `SPEC-FAILURE-ONTOLOGY-01` - `SPEC-PLAYER-FORMALIZATION-WORKFLOWS-01` - `SPEC-REPRESENTATION-PROOF-01` - `DOMAIN-CONSTITUTION-WAVE-01`
- Verify Unreal capabilities, real Solar System data sources/licensing, planetary science models, determinism risks, sparse terrain tech, MMO scalability, and client-shared compute security.
- Verify latest live repo gate state. If fast-strict/RepoX still fails on stale evidence or launcher marker debt, fix that first. If normal gates are clean, continue with `PROJECTION-CONFORMANCE-01`.
- - Closed root model. - No `framework/` root. - Service-first provider model. - Workbench is not authority. - Third-party libraries are providers. - C17/C++17 with C-compatible ABI. - Full CTest remains debt.
- - deep primitives master doctrine; - failure ontology master taxonomy; - player-facing formalization workflows; - ordinary-life grounding; - domain constitutions; - playable-baseline hardening; - domain-by-domain verification.
- - Profiles, not modes. - Process-only mutation. - Truth/Perceived/Render separation. - XStack removable. - Mechanical failures remediated. - Packs data-only and compiled into registries. - Deterministic packaging and lockfile enforcement.
- - What should AIDE do next? - What should Dominium do next? - Which XStack pieces should be wrapped first? - How should root recycling classify files? - What are the biggest risks? - Which repo files should be verified live? - How do I use this package in a future chat?
- - Did applied Codex prompts fully succeed? - Has launcher hardening already run? - Do command graph/UI IR/binding validator exist? - Does launcher run with zero packs and missing locale? - Does launcher refuse BUILD-ID mismatches? - Are any shared headers ambiguously owned?
- Read first: `01_human_readable_report.md`. Use for continuing in another chat: `02_context_transfer_packet.md`. Use for aggregation: `03_spec_sheet.yaml` and `05_aggregator_packet.md`. Use for precise tables: `04_registers.md`. Use for caveats: `07_verification_and_audit.md`.
- This package preserves the chat's substance in human-readable and machine-mergeable forms. It covers architecture, repo layout, provider strategy, renderer plan, Workbench/UI, Robot OS UX, robotic seed-civilisation design, tasks, risks, verification items, and aggregation guidance.
- The user began from the position that months of planning and refactoring had not produced a clean enough repo to continue development. The user was especially frustrated that prior attempts kept adding new root directories and reintroducing `src/` and `source/` folders, which had already been identified as a core failure mode.
- - User APP0 prompt. - Assistant APP0 implementation pack, with caveats. - APP0 critique. - Platform runtime proposal. - Renderer/platform taxonomy proposal. - Advanced runtime/module/framegraph proposal, with caveats. - Prior Context Transfer Packet. - This final report package. - Old repo snapshot/project attachments, not yet verified.
- - Domino = engine core; Dominium = game/runtime/tooling layer. - Specs are normative; README is descriptive. - 286+ full engine target; CP/M limited only. - Unified source hierarchy for all platforms. - No divergent port implementations. - Capability-based graceful degradation. - Lockstep is canonical. - Disk versions immutable. - `content.lock` mismatch fatal until reconciled.
- The user's core complaint was that Dominium had spent months in refactor/planning cycles without enabling real feature work. The repository had repeatedly accumulated new roots and redundant folder shapes. The user identified one recurring failure mode: assistants and tooling kept adding new root directories and `src/`/`source/` wrappers, directly violating the project's own doctrine.
- 1. Domino/Dominium architecture overview. 2. Workbench Platform. 3. AIDE/Codex development process. 4. Presentation/projection architecture. 5. TUI and rendered GUI doctrine. 6. Theme/style/control/widget system. 7. Provider strategy and third-party fencing. 8. Product-spine task sequence. 9. Targeted maintenance/full-gate debt. 10. Universe Explorer north-star. 11. Progressive self-hosting.
- The chat also produced a user-specified documentation ratio quality gate plan: Python 3 script, CMake integration, local warnings, CI failures, exact min/max thresholds, and no compiler/clang/AST dependency. Later, the user said the project had been heavily refactored in setup, launcher, and game design chats, and asked for a prompt to scan the repo, update every docs/ file, and overhaul README. That latest prompt is the highest-priority repo-facing artifact.
- - Candidates: `135` - Source conversations represented: `45` - Noisy or archival-process candidates: `17` - Overlong candidates: `44` - Candidates with `not_checked` repo conflict: `135`
- At the beginning, the discussion was narrow: the user was choosing fixed-point coordinate precision for a world divided into powers-of-two spatial units. That quickly expanded into a much larger architecture question: how should an enormous procedural world be represented, simulated, saved, streamed, rendered, modified, and extended without becoming inconsistent, bloated, or impossible to maintain?
