Status: DERIVED
Last Reviewed: 2026-05-28
Supersedes: none
Superseded By: none
Stability: provisional
Result: reader_page_generated
Binding Sources: `docs/canon/constitution_v1.md`, `docs/canon/glossary_v1.md`, `AGENTS.md`, `docs/planning/AUTHORITY_ORDER.md`, `docs/planning/SNAPSHOT_INTAKE_PROTOCOL.md`
Authority Class: advisory_only
Source Class: conversation_handoff_export
Source Folder: `docs/archive/conversations/Dominium_Complete_Conversation/`
Promotion Status: not_reviewed

# Dominium Canon, Repository Alignment, and Portability Doctrine - Conversation Reader

This reader page is derived from archived conversation material. It cannot override canon, contracts, schema law, current queue state, live repo structure, or validated repo artifacts.

## What This Conversation Was About

This chat was about preserving and re-grounding Dominium's architecture around a very old constitutional contract, then checking whether the current GitHub repository still follows that contract, and finally broadening the question into a platform-engineering doctrine for portability, modularity, extensibility, reuse, future-proofing, and long-term compatibility.

The chat began with the user pasting the old "DOMINIUM CONSTITUTIONAL ARCHITECTURE & EXECUTION CONTRACT v1" and the old "CANONICAL GLOSSARY v1". Those documents defined Dominium as a deterministic universe simulation platform built around Domino as a C89 deterministic engine, Dominium as a C++98 game layer, product applications such as Client/Server/Setup/Launcher, and XStack as a governance layer. The v1 ontology reduced all systems to Assemblies, Fields, Processes, Agents, and Law. It also insisted on fixed-point authoritative math, named RNG streams, thread-count invariance, replay hash equivalence, explicit AuthorityContext, LawProfile-driven behavior rather than runtime mode flags, and TruthModel -> PerceivedModel -> RenderModel separation. The glossary locked the vocabulary around terms such as Authority, LawProfile, Lens, Process, SessionSpec, UniverseIdentity, UniverseState, Macro Capsule, SRZ, XStack, RepoX, TestX, AuditX, CompatX, SecureX, and related concepts.

The user then asked how the current GitHub repository `julesc013/dominium` aligned with that old v1 contract and glossary, asking specifically: what do the docs say, and what does the code do? The assistant inspected the live repository through the GitHub connector. The main finding was that the old v1 contract and glossary had not been discarded; they had been materialized into repo canon under `docs/canon/constitution_v1.md` and `docs/canon/glossary_v1.md`. The repo also had a newer canon-index regime saying prompts themselves are not authoritative unless materialized as canonical documents. This mattered because it changed the authority model: the old pasted prompt is historically important, but the repo version of the contract is the operational source of truth. The audit found strong alignment in documents, schemas, registries, governance, deterministic build constraints, and client session-pipeline code, but only partial implementation of the full runtime gameplay model. Survival fields and processes exist as registries; full agent gameplay loops, MMO/SRZ distributed runtime, embodiment, and other advanced systems were still described as deferred or future work.

## Why It Mattered

This conversation matters as historical context for the topics tagged here: architecture, content, contracts_schema, determinism, governance, platform, release, simulation, timekeeping, tooling, ui, worldgen, xstack_aide. Its value is explanatory and evidentiary, not authoritative. Any claim must be checked against current repo artifacts before promotion.

## What Was Discussed

The package appears to be a `nested_package_collection` with `67` source files. The primary extracted source is `docs/archive/conversations/Dominium_Complete_Conversation/Accompanying_Report/Dominium_Canon_Portability_Audit__01_human_readable_report.md`.

## What Was Decided

- This chat was about preserving and re-grounding Dominium's architecture around a very old constitutional contract, then checking whether the current GitHub repository still follows that contract, and finally broadening the question into a platform-engineering doctrine for portability, modularity, extensibility, reuse, future-proofing, and long-term compatibility.
- The glossary bound terms such as Authority, Law, Process, Lens, SessionSpec, UniverseIdentity, Macro Capsule, SRZ, RepoX, TestX, AuditX, CompatX, SecureX, and related terms. It matters because future assistants must not use sloppy synonyms like "mode" where the canon requires ExperienceProfile or LawProfile. This topic directly supports modularity because stable vocabulary is part of stable architecture.
- Uncertainty: during this preservation pass, a potential inconsistency appeared: some docs claim product roots moved under `apps/`, while an earlier inspected code path under root `client/` was available and `apps/client` was not fetched successfully. This must be verified against the current physical tree.
- DECISION-01:** The old v1 contract/glossary were accepted as the baseline for this chat because the user supplied them as the old ground truth and asked later questions against them.
- DECISION-02:** The live repo audit refined authority: the repo-materialized canon files and canon index are stronger for current repository work than raw prompts.
- DECISION-03:** Ownership-root layout was preferred because it encodes who owns a file or subsystem, while generic `src`/`source` hides responsibility.
- DECISION-04:** Stable contracts plus replaceable implementations best satisfy the user's desire for rewrites/refactors without losing compatibility.
- DECISION-05:** The repo should not be described as fully implementing the old v1 vision yet; many systems are still declarative, scaffolded, or deferred.
- DECISION-06:** The uploaded preservation prompt directly requested a package, so this response creates one.
- A third tradeoff is between docs ambition and runtime proof. The docs are far ahead, which is acceptable for planning, but dangerous if treated as implementation fact. Future work must always separate "declared contract," "schema/registry exists," "code exists," "tests pass," and "product behavior proven."
- The user likely wants future assistants to challenge weak framing, preserve uncertainty, avoid shallow "best practice" lists, and focus on decisions that survive future rewrites.
- The old v1 contract and glossary remain central, but current repo authority is materialized canon, not raw prompts.

## What Was Not Decided

- Uncertainty: the raw pasted prompt is not the current repo authority unless materialized in repo canon. The later audit found that it had in fact been materialized under `docs/canon/constitution_v1.md`.
- Uncertainty: during this preservation pass, a potential inconsistency appeared: some docs claim product roots moved under `apps/`, while an earlier inspected code path under root `client/` was available and `apps/client` was not fetched successfully. This must be verified against the current physical tree.
- Unresolved goals include verifying the latest physical repo tree, proving runtime implementation maturity, formalizing public ABI/API boundaries, completing layout/naming cleanup, and building a second Domino-based product to prove reuse.
- 1. Verify the current physical repo tree against layout docs and `contracts/repo/layout.contract.toml`.
- The user likely wants future assistants to challenge weak framing, preserve uncertainty, avoid shallow "best practice" lists, and focus on decisions that survive future rewrites.
- "Create a gated plan for verifying current repo layout and exceptions."

## Ideas Rejected, Superseded, Or Deprioritised

- The glossary bound terms such as Authority, Law, Process, Lens, SessionSpec, UniverseIdentity, Macro Capsule, SRZ, RepoX, TestX, AuditX, CompatX, SecureX, and related terms. It matters because future assistants must not use sloppy synonyms like "mode" where the canon requires ExperienceProfile or LawProfile. This topic directly supports modularity because stable vocabulary is part of stable architecture.
- The chat inspected repo layout/naming documents and concluded that the active ownership-root structure is broadly right: `apps/`, `engine/`, `game/`, `runtime/`, `contracts/`, `content/`, `docs/`, `tests/`, `tools/`, `scripts/`, `cmake/`, `external/`, `release/`, and `archive/`. Generic roots like `src/`, `source/`, `common/`, `shared`, and `misc` were rejected because they hide ownership.
- Main prevention rule: do not compress this chat into "repo mostly aligns with canon." The more precise takeaway is: **canon/docs/schemas/gates are strong, runtime implementation is partial, layout direction is good, cleanup remains, and future-proofing requires stable contracts plus replaceable implementations.

## What Future Work Came From It

- This chat was about preserving and re-grounding Dominium's architecture around a very old constitutional contract, then checking whether the current GitHub repository still follows that contract, and finally broadening the question into a platform-engineering doctrine for portability, modularity, extensibility, reuse, future-proofing, and long-term compatibility.
- The conversation opened with a deliberate reconstitution of canon. The user supplied an old self-contained constitutional architecture prompt for Dominium and Domino. The assistant acknowledged it as authoritative within the conversation. The user then supplied a canonical glossary v1.0.0, and the assistant acknowledged that the glossary constrained future terms.
- This preservation task was then uploaded as `Pasted text.txt`. It requested a maximum-fidelity report package for the current chat, with human-readable explanation first, structured registers, context-transfer packet, spec sheet, aggregator packet, self-audit, and downloadable files.
- Uncertainty: the raw pasted prompt is not the current repo authority unless materialized in repo canon. The later audit found that it had in fact been materialized under `docs/canon/constitution_v1.md`.
- The glossary bound terms such as Authority, Law, Process, Lens, SessionSpec, UniverseIdentity, Macro Capsule, SRZ, RepoX, TestX, AuditX, CompatX, SecureX, and related terms. It matters because future assistants must not use sloppy synonyms like "mode" where the canon requires ExperienceProfile or LawProfile. This topic directly supports modularity because stable vocabulary is part of stable architecture.
- The user then asked what practices would make the code reusable for other games and even other engine projects. The assistant answered that the correct goal is not to make all files permanent, but to make boundaries explicit and stable. The doctrine became: stable contracts, replaceable implementations, deterministic behavior, portable projections, and no accidental authority from paths/tools/UIs/prompts.
- The uploaded prompt requested this full preservation package. It requires a human-readable report, registers, context transfer packet, spec sheet, aggregator packet, self-audit, exported files, and an in-chat reader.
- The explicit goals were to restore/preserve old Dominium canon, assess current repository alignment, understand what the docs and code actually say/do, and identify practices to make the code portable, modular, extensible, replaceable, future-proof, and backward compatible.
- DECISION-02:** The live repo audit refined authority: the repo-materialized canon files and canon index are stronger for current repository work than raw prompts.
- DECISION-06:** The uploaded preservation prompt directly requested a package, so this response creates one.
- A third tradeoff is between docs ambition and runtime proof. The docs are far ahead, which is acceptable for planning, but dangerous if treated as implementation fact. Future work must always separate "declared contract," "schema/registry exists," "code exists," "tests pass," and "product behavior proven."
- The user likely wants future assistants to challenge weak framing, preserve uncertainty, avoid shallow "best practice" lists, and focus on decisions that survive future rewrites.

## Important Artifacts

- `handoff`: `2`
- `json`: `2`
- `manifest`: `9`
- `markdown`: `8`
- `primary_report`: `9`
- `prompt`: `3`
- `reader_brief`: `6`
- `registers`: `3`
- `sha256`: `1`
- `source_input`: `2`
- `spec_sheet`: `3`
- `verification`: `8`
- `zip`: `11`

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
