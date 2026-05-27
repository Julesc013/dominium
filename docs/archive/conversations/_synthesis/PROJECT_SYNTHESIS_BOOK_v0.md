Status: DERIVED
Last Reviewed: 2026-05-28
Supersedes: none
Superseded By: none
Stability: provisional
Result: project_synthesis_book_generated
Binding Sources: `docs/canon/constitution_v1.md`, `docs/canon/glossary_v1.md`, `AGENTS.md`, `docs/planning/AUTHORITY_ORDER.md`, `docs/planning/SNAPSHOT_INTAKE_PROTOCOL.md`
Authority Class: advisory_synthesis
Promotion Status: not_promoted
Source Class: conversation_corpus_synthesis


# Dominium Conversation Corpus Synthesis Book v0

This book is a derived reading guide over the archived conversation corpus. It is not canon, not architecture doctrine, not a contract, and not an implementation plan.

## 1. Status And Authority

- Acceptance review result: `PASS_WITH_WARNINGS`.
- Authority class: `advisory_synthesis`.
- Promotion status: `not_promoted`.
- Current repo artifacts outrank every conversation-derived statement in this book.

## 2. Executive Overview

The archive describes Dominium as a long-horizon deterministic simulation product: a game, engine-backed operating environment, validation workbench, content platform, and governance-heavy repository. Across the conversations, the recurring intent is not to build a renderer-owned game loop or a pile of UI screens. The recurring intent is to preserve lawful simulation truth, expose it through command/result/evidence surfaces, and let products project that truth without mutating it.

The current repo already establishes the strongest version of that principle through canon, glossary, README, and queue state. The conversation corpus adds historical design intent around world scale, Workbench, setup/launcher, release identity, provider/content boundaries, and future UI/editor experiences. Those claims remain advisory until reconciled and promoted.

## 3. What Dominium Is Trying To Be

Repo-established truth: Dominium is the official game/product/domain layer on top of Domino, the reusable deterministic substrate. It is concerned with invention, production, logistics, economics, settlement, trust, communication, and institutional power emerging from lawful simulation.

Conversation-derived intent: the archive repeatedly extends that picture toward a broad universe-scale simulation platform, with real-world defaults, arbitrary authored packs, robust tooling, deterministic evidence, long-term portability, and a Workbench that makes the project inspectable and operable.

## 4. Core Mental Model

The current README gives the clearest spine: intent -> command -> capability/refusal check -> service or deterministic process -> result/document/snapshot -> diagnostics/evidence -> view/action model -> projection -> shell. The conversations mostly orbit that same model, even when they discuss UI, renderer, platform, setup, or release packaging.

## 5. Engine / Game / Runtime / Product Boundaries

Repo truth keeps Engine, Game, Client, Server, Workbench, setup, launcher, tools, contracts, and content in separate roles. Conversation-derived material reinforces the boundary: renderer and UI project state, clients issue intents, server/game/engine law remains authoritative, and tools validate or inspect rather than silently mutate truth.

Representative sources: [Dominium Advanced Simulation and Infrastructure Architecture](../_reader/by_chat/advanced_simulation_infrastructure.md), [Dominium APP0 Runtime, Platform, and Renderer Architecture](../_reader/by_chat/app_runtime_platform_renderers.md), [Dominium Architecture, Application Layer, TestX, and CodeHygiene Planning](../_reader/by_chat/app_testx_codehygiene.md), [Dominium/Domino Architecture and Codex Prompt Roadmap](../_reader/by_chat/architecture_codex_prompts.md), [Dominium Architecture, UI, Providers, and Robot OS Strategy](../_reader/by_chat/architecture_ui_providers.md), [Dominium Build and Future-Proofing Architecture](../_reader/by_chat/build_and_future_proofing.md), [Dominium Canonical Architecture, Repository Foundation, and Provider Model](../_reader/by_chat/canonical_structure_and_framework.md), [Dominium Chronology & Celestial Systems](../_reader/by_chat/chronology_celestial_systems.md).

## 6. Determinism, Replay, And Provenance

The canon makes determinism primary: ordering, reductions, RNG streams, replay, hash partitions, and provenance are non-negotiable. The corpus adds historical emphasis on deterministic world scale, portable builds, replay proofs, verification artifacts, and avoiding hidden fallback behavior.

Representative sources: [Dominium Advanced Simulation and Infrastructure Architecture](../_reader/by_chat/advanced_simulation_infrastructure.md), [Dominium APP0 Runtime, Platform, and Renderer Architecture](../_reader/by_chat/app_runtime_platform_renderers.md), [Dominium Architecture, Application Layer, TestX, and CodeHygiene Planning](../_reader/by_chat/app_testx_codehygiene.md), [Dominium/Domino Architecture and Codex Prompt Roadmap](../_reader/by_chat/architecture_codex_prompts.md), [Dominium Architecture, UI, Providers, and Robot OS Strategy](../_reader/by_chat/architecture_ui_providers.md), [Dominium Build and Future-Proofing Architecture](../_reader/by_chat/build_and_future_proofing.md), [Dominium Canonical Architecture, Repository Foundation, and Provider Model](../_reader/by_chat/canonical_structure_and_framework.md), [Dominium Development Routes and Continuity Preservation](../_reader/by_chat/development_routes.md).

## 7. Law, Authority, Refusal, And Capability Model

Current repo truth says authority permits attempts, law decides accept/refuse/transform, and refusals must be deterministic and auditable. Conversations often use different local language, but the recurring direction is aligned: no convenience bypass, no generated output as truth, and no old prompt as authority.

Representative sources: [Dominium Advanced Simulation and Infrastructure Architecture](../_reader/by_chat/advanced_simulation_infrastructure.md), [Dominium APP0 Runtime, Platform, and Renderer Architecture](../_reader/by_chat/app_runtime_platform_renderers.md), [Dominium Architecture, Application Layer, TestX, and CodeHygiene Planning](../_reader/by_chat/app_testx_codehygiene.md), [Dominium/Domino Architecture and Codex Prompt Roadmap](../_reader/by_chat/architecture_codex_prompts.md), [Dominium Architecture, UI, Providers, and Robot OS Strategy](../_reader/by_chat/architecture_ui_providers.md), [Dominium Build and Future-Proofing Architecture](../_reader/by_chat/build_and_future_proofing.md), [Dominium Canonical Architecture, Repository Foundation, and Provider Model](../_reader/by_chat/canonical_structure_and_framework.md), [Dominium Chronology & Celestial Systems](../_reader/by_chat/chronology_celestial_systems.md).

## 8. World, Reality, Scale, And Refinement Model

Conversation-derived intent is expansive: worlds, planets, celestial systems, universe explorer concepts, chronology, spatial refinement, simulation domains, macro/micro transitions, and real-world defaults recur across the archive. This is a design-intent signal, not current implementation authority.

Representative sources: [Dominium APP0 Runtime, Platform, and Renderer Architecture](../_reader/by_chat/app_runtime_platform_renderers.md), [Dominium Architecture, Application Layer, TestX, and CodeHygiene Planning](../_reader/by_chat/app_testx_codehygiene.md), [Dominium/Domino Architecture and Codex Prompt Roadmap](../_reader/by_chat/architecture_codex_prompts.md), [Dominium Architecture, UI, Providers, and Robot OS Strategy](../_reader/by_chat/architecture_ui_providers.md), [Dominium Build and Future-Proofing Architecture](../_reader/by_chat/build_and_future_proofing.md), [Dominium Chronology & Celestial Systems](../_reader/by_chat/chronology_celestial_systems.md), [Dominium Development Routes and Continuity Preservation](../_reader/by_chat/development_routes.md), [Dominium Architecture I](../_reader/by_chat/dominium_architecture_i.md).

## 9. Timekeeping, Chronology, And 2038 Resilience

Time appears as both a simulation domain and a platform durability concern. The archive repeatedly points to chronology, calendars, celestial alignment, 2038 resilience, and timestamp policy. Current promotion must verify all such claims against current contracts and language/platform baselines.

Representative sources: [Dominium Advanced Simulation and Infrastructure Architecture](../_reader/by_chat/advanced_simulation_infrastructure.md), [Dominium APP0 Runtime, Platform, and Renderer Architecture](../_reader/by_chat/app_runtime_platform_renderers.md), [Dominium Architecture, Application Layer, TestX, and CodeHygiene Planning](../_reader/by_chat/app_testx_codehygiene.md), [Dominium/Domino Architecture and Codex Prompt Roadmap](../_reader/by_chat/architecture_codex_prompts.md), [Dominium Canonical Architecture, Repository Foundation, and Provider Model](../_reader/by_chat/canonical_structure_and_framework.md), [Dominium Chronology & Celestial Systems](../_reader/by_chat/chronology_celestial_systems.md), [Dominium Development Routes and Continuity Preservation](../_reader/by_chat/development_routes.md), [Documentation Standards, README Strategy, and Handoff Packaging](../_reader/by_chat/documentation_standards_readme.md).

## 10. Civilization, Institutions, Economy, Logistics

The corpus frames Dominium around emergent production, logistics, economics, settlement, communication, trust, institutions, and power. These are project identity themes; they are not authorization to open gameplay or runtime work while the current queue blocks it.

Representative sources: [Dominium Advanced Simulation and Infrastructure Architecture](../_reader/by_chat/advanced_simulation_infrastructure.md), [Dominium APP0 Runtime, Platform, and Renderer Architecture](../_reader/by_chat/app_runtime_platform_renderers.md), [Dominium Architecture, Application Layer, TestX, and CodeHygiene Planning](../_reader/by_chat/app_testx_codehygiene.md), [Dominium/Domino Architecture and Codex Prompt Roadmap](../_reader/by_chat/architecture_codex_prompts.md), [Dominium Architecture, UI, Providers, and Robot OS Strategy](../_reader/by_chat/architecture_ui_providers.md), [Dominium Build and Future-Proofing Architecture](../_reader/by_chat/build_and_future_proofing.md), [Dominium Canonical Architecture, Repository Foundation, and Provider Model](../_reader/by_chat/canonical_structure_and_framework.md), [Dominium Chronology & Celestial Systems](../_reader/by_chat/chronology_celestial_systems.md).

## 11. UI, Renderer, Workbench, And Tools

The conversations strongly prefer a rich Workbench and eventual editor/operator surfaces. Current authority is narrower: broad Workbench UI, renderer implementation, and native GUI remain blocked. Therefore synthesis may describe intent, but follow-up tasks must stay contract/planning scoped until the queue opens implementation scope.

Representative sources: [Dominium Advanced Simulation and Infrastructure Architecture](../_reader/by_chat/advanced_simulation_infrastructure.md), [Dominium Architecture, UI, Providers, and Robot OS Strategy](../_reader/by_chat/architecture_ui_providers.md), [Dominium Canonical Architecture, Repository Foundation, and Provider Model](../_reader/by_chat/canonical_structure_and_framework.md), [Dominium Development Routes and Continuity Preservation](../_reader/by_chat/development_routes.md), [Dominium Architecture IV](../_reader/by_chat/dominium_architecture_iv.md), [Dominium + Domino Codex Planning and Handoff](../_reader/by_chat/dominium_domino_codex_planning.md), [Dominium Workbench, AIDE, Presentation Architecture, Provider Strategy, Product-Spine Planning, and Preservation Companion](../_reader/by_chat/dominium_full_conversation.md), [Domino Dominium Workbench](../_reader/by_chat/domino_dominium_workbench.md).

## 12. AIDE, Codex, Governance, And Patch Workflow

The archive treats AIDE/Codex/XStack as repo-control and patch-execution aids. Current repo truth agrees that they do not replace canon, contracts, review gates, or validation. Their correct role is bounded evidence-producing work, not direct semantic authority.

Representative sources: [Dominium Architecture, Application Layer, TestX, and CodeHygiene Planning](../_reader/by_chat/app_testx_codehygiene.md), [Dominium Canonical Architecture, Repository Foundation, and Provider Model](../_reader/by_chat/canonical_structure_and_framework.md), [Dominium Canon, Repository Alignment, and Portability Doctrine](../_reader/by_chat/dominium_complete_conversation.md), [Dominium Workbench, AIDE, Presentation Architecture, Provider Strategy, Product-Spine Planning, and Preservation Companion](../_reader/by_chat/dominium_full_conversation.md), [Dominium Foundation Lock, Workbench Spine, and Parallel Codex Handoff](../_reader/by_chat/foundation_workbench_codex.md), [Dominium Language, Platform, and Architecture Baseline](../_reader/by_chat/language_platform_architecture.md), [Dominium Modularity, AIDE Refactorability, and Future-Proof Architecture](../_reader/by_chat/modularity_aide_refactorability.md), [Dominium Omega/Xi/Pi Architecture & Future-Proofing Planning](../_reader/by_chat/omega_xi_pi_architecture_future.md).

## 13. Release, Setup, Launcher, Platform, Portability

Conversations cover setup, launcher, release identity, versioning, portability, platform support, and public distribution. Current queue still blocks release publication, so these remain planning and audit material unless a later reviewed task opens the scope.

Representative sources: [Dominium Advanced Simulation and Infrastructure Architecture](../_reader/by_chat/advanced_simulation_infrastructure.md), [Dominium APP0 Runtime, Platform, and Renderer Architecture](../_reader/by_chat/app_runtime_platform_renderers.md), [Dominium Architecture, Application Layer, TestX, and CodeHygiene Planning](../_reader/by_chat/app_testx_codehygiene.md), [Dominium/Domino Architecture and Codex Prompt Roadmap](../_reader/by_chat/architecture_codex_prompts.md), [Dominium Architecture, UI, Providers, and Robot OS Strategy](../_reader/by_chat/architecture_ui_providers.md), [Dominium Build and Future-Proofing Architecture](../_reader/by_chat/build_and_future_proofing.md), [Dominium Canonical Architecture, Repository Foundation, and Provider Model](../_reader/by_chat/canonical_structure_and_framework.md), [Dominium Development Routes and Continuity Preservation](../_reader/by_chat/development_routes.md).

## 14. Content, Packs, Modding, Providers

The corpus repeatedly returns to pack-driven composition, authored content, providers, binary/content boundaries, and modding. Canon requires pack-driven integration and explicit refusal for missing packs. Current queue blocks package runtime and provider runtime, so promotion must be careful.

Representative sources: [Dominium Advanced Simulation and Infrastructure Architecture](../_reader/by_chat/advanced_simulation_infrastructure.md), [Dominium APP0 Runtime, Platform, and Renderer Architecture](../_reader/by_chat/app_runtime_platform_renderers.md), [Dominium Architecture, Application Layer, TestX, and CodeHygiene Planning](../_reader/by_chat/app_testx_codehygiene.md), [Dominium/Domino Architecture and Codex Prompt Roadmap](../_reader/by_chat/architecture_codex_prompts.md), [Dominium Architecture, UI, Providers, and Robot OS Strategy](../_reader/by_chat/architecture_ui_providers.md), [Dominium Build and Future-Proofing Architecture](../_reader/by_chat/build_and_future_proofing.md), [Dominium Canonical Architecture, Repository Foundation, and Provider Model](../_reader/by_chat/canonical_structure_and_framework.md), [Dominium Chronology & Celestial Systems](../_reader/by_chat/chronology_celestial_systems.md).

## 15. What Was Decided Across Conversations

The strongest recurring conversation-level decisions are advisory: keep simulation truth deterministic, separate rendering from authority, keep Workbench a projection/inspection/control surface rather than truth owner, preserve source provenance, and avoid direct promotion from old chats. These are valuable because they align with current repo doctrine, but alignment is not the same as promotion.

## 16. What Is Still Unresolved

- Promotion candidate triage: The raw promotion queue contains useful leads but also preservation-process noise. Source: [../_promotion/PROMOTION_QUEUE.md](../_promotion/PROMOTION_QUEUE.md).
- Workbench scope: Old conversations discuss Workbench as rich operator surface, but the current queue blocks broad Workbench UI. Source: [../_wiki/topics/workbench.md](../_wiki/topics/workbench.md).
- Renderer and platform boundary: Conversations repeatedly discuss renderer/platform plans, while current authority keeps rendering presentational and implementation scope blocked. Source: [../_wiki/topics/platform.md](../_wiki/topics/platform.md).
- Provider and content boundaries: Provider, pack, and content discussions need separation from runtime module loading and package runtime blocks. Source: [../_wiki/topics/content.md](../_wiki/topics/content.md).
- World scale and fidelity roadmap: Universe, world, chronology, and simulation conversations need sequencing against current contracts and queue limits. Source: [../_wiki/topics/worldgen.md](../_wiki/topics/worldgen.md).
- Release/publication meaning: Release/versioning conversations should remain planning until release publication authority opens. Source: [../_wiki/topics/release.md](../_wiki/topics/release.md).

## 17. Contradictions And Drift

The audit layer contains review triggers, not resolved contradictions. The main risk classes are conversation claims against current queue restrictions, stale external/platform claims, old docs/baseline drift, and conversation-vs-conversation disagreements.

- `conversation_vs_conversation`: `2` findings.
- `conversation_vs_current_queue`: `102` findings.
- `conversation_vs_docs`: `2` findings.
- `stale_external_claim`: `121` findings.

## 18. Stale Claims And Verification Queue

External platform, SDK, renderer, language baseline, release, provider, package runtime, and implementation claims must be rechecked. The synthesis should use those old claims to identify questions, not to assert current facts.

## 19. Promotion Candidates

The raw queue contains `135` generated candidates in [PROMOTION_QUEUE.md](../_promotion/PROMOTION_QUEUE.md). Acceptance review found the queue useful but noisy. It should be triaged before any candidate patch work.

## 20. Recommended Reconciliation Roadmap

1. Keep this synthesis advisory and archive-scoped.
2. Build a claim review matrix against canon, glossary, AGENTS, current queue, contracts, schema law, and targeted current docs.
3. Triage promotion candidates into serious, historical, stale, noisy, rejected, and needs-user-decision groups.
4. Patch live docs only through narrow promotion tasks with named source claims and validation.

## 21. Appendices

Current repo truth, as used by this synthesis:

- [README.md](../../../../README.md) describes Dominium as a deterministic, contract-governed simulation game and operating environment built on the Domino deterministic substrate.
- [docs/canon/constitution_v1.md](../../../canon/constitution_v1.md) binds determinism, process-only mutation, law-gated authority, no runtime mode flags, pack-driven integration, explicit refusal, and truth/perceived/render separation.
- [docs/canon/glossary_v1.md](../../../canon/glossary_v1.md) defines vocabulary such as Engine, Client, AuthorityContext, Domain, Derived artifact, and Contract.
- [AGENTS.md](../../../../AGENTS.md) and [docs/planning/AUTHORITY_ORDER.md](../../../planning/AUTHORITY_ORDER.md) keep archived conversations below canon, glossary, governance, contracts, current queue, and validated repo artifacts.
- [.aide/queue/current.toml](../../../../.aide/queue/current.toml) currently blocks broad feature work including: `broad_workbench_ui`, `gameplay`, `native_gui`, `package_runtime`, `provider_runtime`, `release_publication`, `renderer_implementation`, `runtime_module_loader`.


### Topic Coverage

- `architecture` (45 conversations): system boundaries, product shape, engine/game/client/server separation, and repository structure. Sources: [Dominium Advanced Simulation and Infrastructure Architecture](../_reader/by_chat/advanced_simulation_infrastructure.md), [Dominium APP0 Runtime, Platform, and Renderer Architecture](../_reader/by_chat/app_runtime_platform_renderers.md), [Dominium Architecture, Application Layer, TestX, and CodeHygiene Planning](../_reader/by_chat/app_testx_codehygiene.md), [Dominium/Domino Architecture and Codex Prompt Roadmap](../_reader/by_chat/architecture_codex_prompts.md), [Dominium Architecture, UI, Providers, and Robot OS Strategy](../_reader/by_chat/architecture_ui_providers.md).
- `content` (45 conversations): packs, mods, authored payload, GUI/content boundaries, and provider/content separation. Sources: [Dominium Advanced Simulation and Infrastructure Architecture](../_reader/by_chat/advanced_simulation_infrastructure.md), [Dominium APP0 Runtime, Platform, and Renderer Architecture](../_reader/by_chat/app_runtime_platform_renderers.md), [Dominium Architecture, Application Layer, TestX, and CodeHygiene Planning](../_reader/by_chat/app_testx_codehygiene.md), [Dominium/Domino Architecture and Codex Prompt Roadmap](../_reader/by_chat/architecture_codex_prompts.md), [Dominium Architecture, UI, Providers, and Robot OS Strategy](../_reader/by_chat/architecture_ui_providers.md).
- `ui` (45 conversations): presentation, tools, editor concepts, perceived model surfaces, and command/result display. Sources: [Dominium Advanced Simulation and Infrastructure Architecture](../_reader/by_chat/advanced_simulation_infrastructure.md), [Dominium APP0 Runtime, Platform, and Renderer Architecture](../_reader/by_chat/app_runtime_platform_renderers.md), [Dominium Architecture, Application Layer, TestX, and CodeHygiene Planning](../_reader/by_chat/app_testx_codehygiene.md), [Dominium/Domino Architecture and Codex Prompt Roadmap](../_reader/by_chat/architecture_codex_prompts.md), [Dominium Architecture, UI, Providers, and Robot OS Strategy](../_reader/by_chat/architecture_ui_providers.md).
- `governance` (44 conversations): authority order, canon, contracts, refusal, review gates, and agent operation. Sources: [Dominium Advanced Simulation and Infrastructure Architecture](../_reader/by_chat/advanced_simulation_infrastructure.md), [Dominium APP0 Runtime, Platform, and Renderer Architecture](../_reader/by_chat/app_runtime_platform_renderers.md), [Dominium Architecture, Application Layer, TestX, and CodeHygiene Planning](../_reader/by_chat/app_testx_codehygiene.md), [Dominium/Domino Architecture and Codex Prompt Roadmap](../_reader/by_chat/architecture_codex_prompts.md), [Dominium Architecture, UI, Providers, and Robot OS Strategy](../_reader/by_chat/architecture_ui_providers.md).
- `simulation` (44 conversations): deterministic domains, processes, machines, physical systems, economy, and civilization dynamics. Sources: [Dominium Advanced Simulation and Infrastructure Architecture](../_reader/by_chat/advanced_simulation_infrastructure.md), [Dominium APP0 Runtime, Platform, and Renderer Architecture](../_reader/by_chat/app_runtime_platform_renderers.md), [Dominium Architecture, Application Layer, TestX, and CodeHygiene Planning](../_reader/by_chat/app_testx_codehygiene.md), [Dominium/Domino Architecture and Codex Prompt Roadmap](../_reader/by_chat/architecture_codex_prompts.md), [Dominium Architecture, UI, Providers, and Robot OS Strategy](../_reader/by_chat/architecture_ui_providers.md).
- `tooling` (44 conversations): Codex/AIDE/XStack/TestX/RepoX/AuditX tooling and patch workflow. Sources: [Dominium Advanced Simulation and Infrastructure Architecture](../_reader/by_chat/advanced_simulation_infrastructure.md), [Dominium APP0 Runtime, Platform, and Renderer Architecture](../_reader/by_chat/app_runtime_platform_renderers.md), [Dominium Architecture, Application Layer, TestX, and CodeHygiene Planning](../_reader/by_chat/app_testx_codehygiene.md), [Dominium/Domino Architecture and Codex Prompt Roadmap](../_reader/by_chat/architecture_codex_prompts.md), [Dominium Architecture, UI, Providers, and Robot OS Strategy](../_reader/by_chat/architecture_ui_providers.md).
- `release` (43 conversations): version identity, packaging, setup, update, publication, and release-control concerns. Sources: [Dominium Advanced Simulation and Infrastructure Architecture](../_reader/by_chat/advanced_simulation_infrastructure.md), [Dominium APP0 Runtime, Platform, and Renderer Architecture](../_reader/by_chat/app_runtime_platform_renderers.md), [Dominium Architecture, Application Layer, TestX, and CodeHygiene Planning](../_reader/by_chat/app_testx_codehygiene.md), [Dominium/Domino Architecture and Codex Prompt Roadmap](../_reader/by_chat/architecture_codex_prompts.md), [Dominium Architecture, UI, Providers, and Robot OS Strategy](../_reader/by_chat/architecture_ui_providers.md).
- `contracts_schema` (42 conversations): machine-readable contracts, schemas, compatibility, manifests, and registries. Sources: [Dominium Advanced Simulation and Infrastructure Architecture](../_reader/by_chat/advanced_simulation_infrastructure.md), [Dominium APP0 Runtime, Platform, and Renderer Architecture](../_reader/by_chat/app_runtime_platform_renderers.md), [Dominium Architecture, Application Layer, TestX, and CodeHygiene Planning](../_reader/by_chat/app_testx_codehygiene.md), [Dominium/Domino Architecture and Codex Prompt Roadmap](../_reader/by_chat/architecture_codex_prompts.md), [Dominium Architecture, UI, Providers, and Robot OS Strategy](../_reader/by_chat/architecture_ui_providers.md).
- `determinism` (39 conversations): replay, ordering, proof, fixed identity, RNG discipline, and thread-count invariance. Sources: [Dominium Advanced Simulation and Infrastructure Architecture](../_reader/by_chat/advanced_simulation_infrastructure.md), [Dominium APP0 Runtime, Platform, and Renderer Architecture](../_reader/by_chat/app_runtime_platform_renderers.md), [Dominium Architecture, Application Layer, TestX, and CodeHygiene Planning](../_reader/by_chat/app_testx_codehygiene.md), [Dominium/Domino Architecture and Codex Prompt Roadmap](../_reader/by_chat/architecture_codex_prompts.md), [Dominium Architecture, UI, Providers, and Robot OS Strategy](../_reader/by_chat/architecture_ui_providers.md).
- `platform` (39 conversations): runtime shell, platform adapter, renderer boundary, operating-system support, and portability. Sources: [Dominium Advanced Simulation and Infrastructure Architecture](../_reader/by_chat/advanced_simulation_infrastructure.md), [Dominium APP0 Runtime, Platform, and Renderer Architecture](../_reader/by_chat/app_runtime_platform_renderers.md), [Dominium Architecture, Application Layer, TestX, and CodeHygiene Planning](../_reader/by_chat/app_testx_codehygiene.md), [Dominium Architecture, UI, Providers, and Robot OS Strategy](../_reader/by_chat/architecture_ui_providers.md), [Dominium Build and Future-Proofing Architecture](../_reader/by_chat/build_and_future_proofing.md).
- `worldgen` (39 conversations): world, universe, celestial, terrain, chronology, and large-scale reality modeling. Sources: [Dominium APP0 Runtime, Platform, and Renderer Architecture](../_reader/by_chat/app_runtime_platform_renderers.md), [Dominium Architecture, Application Layer, TestX, and CodeHygiene Planning](../_reader/by_chat/app_testx_codehygiene.md), [Dominium/Domino Architecture and Codex Prompt Roadmap](../_reader/by_chat/architecture_codex_prompts.md), [Dominium Architecture, UI, Providers, and Robot OS Strategy](../_reader/by_chat/architecture_ui_providers.md), [Dominium Build and Future-Proofing Architecture](../_reader/by_chat/build_and_future_proofing.md).
- `timekeeping` (35 conversations): calendar, chronology, timestamp durability, 2038 resilience, and time-domain law. Sources: [Dominium Advanced Simulation and Infrastructure Architecture](../_reader/by_chat/advanced_simulation_infrastructure.md), [Dominium APP0 Runtime, Platform, and Renderer Architecture](../_reader/by_chat/app_runtime_platform_renderers.md), [Dominium Architecture, Application Layer, TestX, and CodeHygiene Planning](../_reader/by_chat/app_testx_codehygiene.md), [Dominium/Domino Architecture and Codex Prompt Roadmap](../_reader/by_chat/architecture_codex_prompts.md), [Dominium Canonical Architecture, Repository Foundation, and Provider Model](../_reader/by_chat/canonical_structure_and_framework.md).
- `setup_launcher` (25 conversations): setup, repair, rollback, launcher profiles, instances, and product orchestration. Sources: [Dominium APP0 Runtime, Platform, and Renderer Architecture](../_reader/by_chat/app_runtime_platform_renderers.md), [Dominium Architecture, Application Layer, TestX, and CodeHygiene Planning](../_reader/by_chat/app_testx_codehygiene.md), [Dominium/Domino Architecture and Codex Prompt Roadmap](../_reader/by_chat/architecture_codex_prompts.md), [Dominium Canonical Architecture, Repository Foundation, and Provider Model](../_reader/by_chat/canonical_structure_and_framework.md), [Documentation Standards, README Strategy, and Handoff Packaging](../_reader/by_chat/documentation_standards_readme.md).
- `workbench` (20 conversations): operator-facing validation, evidence, inspection, and later authoring surfaces. Sources: [Dominium Advanced Simulation and Infrastructure Architecture](../_reader/by_chat/advanced_simulation_infrastructure.md), [Dominium Architecture, UI, Providers, and Robot OS Strategy](../_reader/by_chat/architecture_ui_providers.md), [Dominium Canonical Architecture, Repository Foundation, and Provider Model](../_reader/by_chat/canonical_structure_and_framework.md), [Dominium Development Routes and Continuity Preservation](../_reader/by_chat/development_routes.md), [Dominium Architecture IV](../_reader/by_chat/dominium_architecture_iv.md).
- `xstack_aide` (14 conversations): repo-control and assistant-operation systems around AIDE, XStack, AuditX, RepoX, and TestX. Sources: [Dominium Architecture, Application Layer, TestX, and CodeHygiene Planning](../_reader/by_chat/app_testx_codehygiene.md), [Dominium Canonical Architecture, Repository Foundation, and Provider Model](../_reader/by_chat/canonical_structure_and_framework.md), [Dominium Canon, Repository Alignment, and Portability Doctrine](../_reader/by_chat/dominium_complete_conversation.md), [Dominium Workbench, AIDE, Presentation Architecture, Provider Strategy, Product-Spine Planning, and Preservation Companion](../_reader/by_chat/dominium_full_conversation.md), [Dominium Foundation Lock, Workbench Spine, and Parallel Codex Handoff](../_reader/by_chat/foundation_workbench_codex.md).
