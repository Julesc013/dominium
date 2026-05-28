# Dominium Human-Readable Project Book

Version: 1
Authority Class: advisory_synthesis
Source Root: `docs/`
Conversation Corpus Root: `docs/archive/conversations/`
Promotion Status: not_promoted
Canon impact: unchanged
Contract/schema impact: unchanged
Implementation impact: unchanged
Release impact: unchanged
Queue impact: unchanged


> [!AUTHORITY] This book is **DERIVED** and advisory. It is a human-readable synthesis of current docs, archive context, and conversation evidence. It is not canon, not a contract, not schema law, not release authority, and not queue state.

## How To Read This Book

Start with Part I if you need the project in one sitting. Use Parts II through IV when you need architecture, simulation, tooling, and archive context. Use Part V to plan review work. Source trails at the end of each chapter point to the documents that support the synthesis.

## What This Book Is

This is a readable project book. It explains the project in coherent prose, draws current repo truth from the strongest authority surfaces, and uses archive and conversation material as historical evidence.

## What This Book Is Not

This book does not promote archive claims. It does not apply promotion candidates. It does not open blocked Workbench UI, renderer, gameplay, provider runtime, package runtime, native GUI, or release publication work. It does not resolve contradictions by convenience.

It also does not print raw JSON, raw YAML, hash manifests, validation logs, or giant file registers as chapter content. Those materials remain available through the source manifest, reference reports, and source-reader HTML where they are easier to audit.

## Source Hierarchy

1. `docs/canon/constitution_v1.md`
2. `docs/canon/glossary_v1.md`
3. `AGENTS.md`
4. Scope-specific current planning, schema, contract, release, policy, and queue artifacts
5. Operational registries, projections, mirrors, manifests, and generated evidence
6. Archive material and conversation-derived synthesis

## Reading Paths

- **Fast orientation:** chapters 1, 3, 4, 16, and 20.
- **Architecture review:** chapters 5 through 9.
- **Simulation/world review:** chapters 10 through 12.
- **Tooling and governance review:** chapters 13 through 15.
- **Decision/promotion review:** chapters 17 through 20.

## Status Labels

- **Current repo truth:** supported by current canon, glossary, AGENTS, contracts, queue, or live docs.
- **Archive/historical:** useful for provenance but not current authority.
- **Conversation advisory:** design intent from archived conversations, not promoted truth.
- **Blocked by queue:** related implementation scope remains closed.
- **Needs decision:** cannot be resolved by generated synthesis.


# Part I - The Project In One Sitting


## 1. What Dominium Is

Dominium is best understood as a deterministic, contract-governed simulation game and operating environment built on the Domino deterministic substrate. The project is not just a game executable; it is a set of lawful simulation, validation, content, evidence, and product surfaces that have to agree about truth.

This chapter is part of the synthesized reader, not a source-file transcript. It is written to preserve the meaning that recurs across current docs, archive material, and conversation synthesis while keeping the authority boundary visible.

**Current repo-backed picture.** The README identifies Dominium as the official game/product/domain layer on top of Domino. The canon and glossary provide binding meaning, while AGENTS defines how repo work must respect that authority. The current queue keeps broad implementation work constrained.

The practical consequence is that this topic should be read through the current authority model first. If a current source and an archive source appear to disagree, the archive source becomes review evidence rather than a shortcut around current doctrine.

**Historical and advisory context.** The archive and conversations expand the picture into a long-horizon product ecosystem: Workbench, setup/launcher, content packs, portability, release identity, provider boundaries, and repo-governed assistant workflows. Those materials explain intent but do not override current repo truth.

That historical context is still useful. It shows why the topic kept returning, which boundaries people were worried about, and what kind of future work the project repeatedly imagined. The book preserves that context so it can be reviewed instead of rediscovered or silently re-invented.

**What remains unresolved.** The exact product boundary between long-term vision and current allowed implementation remains queue-gated. Future work must distinguish 'what the project intends' from 'what the current queue permits'.

**What not to assume.** Do not treat historical breadth as current permission. Do not infer implementation readiness from a polished description. Do not treat this book, the source reader, or any generated corpus report as a promotion into canon, contracts, schema, implementation, release state, or queue state.

**Review questions.**

- Which parts of this topic are already current repo truth?
- Which parts are merely consistent with current docs but not formalized?
- Which parts are blocked by queue state or need explicit human decision?
- Which source paths should be inspected before any later docs-only promotion?

**How to use this chapter.** Read this chapter as orientation, not as promotion. If later work wants to change canon, contracts, architecture, schema, implementation, release state, or queue state, it needs a separate scoped promotion task with explicit validation.

**Source trail:**

- `README.md`
- `docs/canon/constitution_v1.md`
- `docs/canon/glossary_v1.md`
- `AGENTS.md`
- `docs/archive/conversations/_synthesis/CURRENT_PROJECT_ATLAS_v0.md`


## 2. Why This Project Exists

The recurring project ambition is to make invention, production, logistics, economics, settlement, trust, communication, and institutional power emerge from lawful simulation rather than from one-off scripts or renderer-owned state.

This chapter is part of the synthesized reader, not a source-file transcript. It is written to preserve the meaning that recurs across current docs, archive material, and conversation synthesis while keeping the authority boundary visible.

**Current repo-backed picture.** Current docs emphasize deterministic execution, process-only mutation, explicit refusal, pack-driven integration, and validation evidence. These are not aesthetic preferences; they are the controls that keep a large simulation explainable and replayable.

The practical consequence is that this topic should be read through the current authority model first. If a current source and an archive source appear to disagree, the archive source becomes review evidence rather than a shortcut around current doctrine.

**Historical and advisory context.** Conversation material repeatedly pushes the same ambition outward: world scale, tooling, release discipline, long-term portability, and operator interfaces that make the system inspectable. The archive is valuable because it preserves why those themes mattered.

That historical context is still useful. It shows why the topic kept returning, which boundaries people were worried about, and what kind of future work the project repeatedly imagined. The book preserves that context so it can be reviewed instead of rediscovered or silently re-invented.

**What remains unresolved.** The project still needs adjudication on which historical design intents become current docs, which remain history, and which are blocked until later queue phases.

**What not to assume.** Do not treat historical breadth as current permission. Do not infer implementation readiness from a polished description. Do not treat this book, the source reader, or any generated corpus report as a promotion into canon, contracts, schema, implementation, release state, or queue state.

**Review questions.**

- Which parts of this topic are already current repo truth?
- Which parts are merely consistent with current docs but not formalized?
- Which parts are blocked by queue state or need explicit human decision?
- Which source paths should be inspected before any later docs-only promotion?

**How to use this chapter.** Read this chapter as orientation, not as promotion. If later work wants to change canon, contracts, architecture, schema, implementation, release state, or queue state, it needs a separate scoped promotion task with explicit validation.

**Source trail:**

- `README.md`
- `docs/archive/conversations/_synthesis/PROJECT_SYNTHESIS_BOOK_v0.md`
- `docs/archive/docs_corpus/_reconciliation/DOCS_CURRENT_PROJECT_PICTURE_v0.md`


## 3. The Core Mental Model

The clearest mental model is the command/result spine: intent becomes command, capability/refusal law checks it, a deterministic service or process produces a result, diagnostics and evidence make it inspectable, and product shells project the outcome.

This chapter is part of the synthesized reader, not a source-file transcript. It is written to preserve the meaning that recurs across current docs, archive material, and conversation synthesis while keeping the authority boundary visible.

**Current repo-backed picture.** Current repo truth separates authoritative truth, perceived/observed views, and rendering. UI and rendering are presentation. Authoritative mutation happens only through lawful deterministic process execution.

The practical consequence is that this topic should be read through the current authority model first. If a current source and an archive source appear to disagree, the archive source becomes review evidence rather than a shortcut around current doctrine.

**Historical and advisory context.** Archived conversations apply the same model to Workbench, renderer, setup, provider, and content discussions. They often differ in vocabulary, but the direction is consistent: products should project truth, not invent hidden state.

That historical context is still useful. It shows why the topic kept returning, which boundaries people were worried about, and what kind of future work the project repeatedly imagined. The book preserves that context so it can be reviewed instead of rediscovered or silently re-invented.

**What remains unresolved.** Some old conversations imply future UI/editor powers that are not currently open. Those should be read as design intent and decision backlog, not implementation authorization.

**What not to assume.** Do not treat historical breadth as current permission. Do not infer implementation readiness from a polished description. Do not treat this book, the source reader, or any generated corpus report as a promotion into canon, contracts, schema, implementation, release state, or queue state.

**Review questions.**

- Which parts of this topic are already current repo truth?
- Which parts are merely consistent with current docs but not formalized?
- Which parts are blocked by queue state or need explicit human decision?
- Which source paths should be inspected before any later docs-only promotion?

**How to use this chapter.** Read this chapter as orientation, not as promotion. If later work wants to change canon, contracts, architecture, schema, implementation, release state, or queue state, it needs a separate scoped promotion task with explicit validation.

**Source trail:**

- `README.md`
- `AGENTS.md`
- `docs/architecture/INVARIANTS.md`
- `docs/archive/conversations/_synthesis/PROJECT_SYNTHESIS_BOOK_v0.md`


## 4. What Is Current Repo Truth Vs Historical Context

The most important reading rule is authority ordering. Repo artifacts outrank chat memory. Canon and glossary outrank lower-level prose. Current queue state controls what work is allowed now.

This chapter is part of the synthesized reader, not a source-file transcript. It is written to preserve the meaning that recurs across current docs, archive material, and conversation synthesis while keeping the authority boundary visible.

**Current repo-backed picture.** AGENTS and the planning authority docs make this explicit. Generated outputs are evidence unless promoted by a stronger source. Archive and conversation material can orient review, but it cannot silently become doctrine.

The practical consequence is that this topic should be read through the current authority model first. If a current source and an archive source appear to disagree, the archive source becomes review evidence rather than a shortcut around current doctrine.

**Historical and advisory context.** The docs corpus and conversation corpus are useful precisely because they preserve history without contaminating current authority. They create review queues, contradiction maps, and source trails.

That historical context is still useful. It shows why the topic kept returning, which boundaries people were worried about, and what kind of future work the project repeatedly imagined. The book preserves that context so it can be reviewed instead of rediscovered or silently re-invented.

**What remains unresolved.** The remaining work is human adjudication: decide what to preserve as history, what to promote through narrow docs tasks, what conflicts with authority, and what needs future queue opening.

**What not to assume.** Do not treat historical breadth as current permission. Do not infer implementation readiness from a polished description. Do not treat this book, the source reader, or any generated corpus report as a promotion into canon, contracts, schema, implementation, release state, or queue state.

**Review questions.**

- Which parts of this topic are already current repo truth?
- Which parts are merely consistent with current docs but not formalized?
- Which parts are blocked by queue state or need explicit human decision?
- Which source paths should be inspected before any later docs-only promotion?

**How to use this chapter.** Read this chapter as orientation, not as promotion. If later work wants to change canon, contracts, architecture, schema, implementation, release state, or queue state, it needs a separate scoped promotion task with explicit validation.

**Source trail:**

- `AGENTS.md`
- `docs/planning/AUTHORITY_ORDER.md`
- `docs/planning/SNAPSHOT_INTAKE_PROTOCOL.md`
- `docs/archive/docs_corpus/_reconciliation/DOCS_CURRENT_PROJECT_PICTURE_v0.md`


# Part II - Current Architecture


## 5. The System Stack

The project stack separates Domino substrate, Dominium domain/product meaning, runtime/product shells, Workbench/operator surfaces, contracts/schema law, content packs, and documentation/governance.

This chapter is part of the synthesized reader, not a source-file transcript. It is written to preserve the meaning that recurs across current docs, archive material, and conversation synthesis while keeping the authority boundary visible.

**Current repo-backed picture.** Current sources keep these roles distinct. The engine substrate owns deterministic mechanics; the game/domain layer owns official interpretation; apps compose products; contracts and schema define compatibility surfaces; docs and queue state govern allowed work.

The practical consequence is that this topic should be read through the current authority model first. If a current source and an archive source appear to disagree, the archive source becomes review evidence rather than a shortcut around current doctrine.

**Historical and advisory context.** Conversation archives reinforce this layered picture but sometimes discuss future experiences as if they already exist. The book keeps those statements advisory.

That historical context is still useful. It shows why the topic kept returning, which boundaries people were worried about, and what kind of future work the project repeatedly imagined. The book preserves that context so it can be reviewed instead of rediscovered or silently re-invented.

**What remains unresolved.** The current stack map needs future promotion only where current docs are thin, not where archive language merely repeats unsupported future ambition.

**What not to assume.** Do not treat historical breadth as current permission. Do not infer implementation readiness from a polished description. Do not treat this book, the source reader, or any generated corpus report as a promotion into canon, contracts, schema, implementation, release state, or queue state.

**Review questions.**

- Which parts of this topic are already current repo truth?
- Which parts are merely consistent with current docs but not formalized?
- Which parts are blocked by queue state or need explicit human decision?
- Which source paths should be inspected before any later docs-only promotion?

**How to use this chapter.** Read this chapter as orientation, not as promotion. If later work wants to change canon, contracts, architecture, schema, implementation, release state, or queue state, it needs a separate scoped promotion task with explicit validation.

**Source trail:**

- `README.md`
- `docs/architecture/CANONICAL_SYSTEM_MAP.md`
- `docs/architecture/CONTRACTS_INDEX.md`
- `docs/archive/conversations/_synthesis/FULL_PROJECT_PICTURE_v0.md`


## 6. Authority, Law, Capability, And Refusal

Authority in Dominium is not convenience power. Authority permits or frames attempts; law decides whether an attempt is accepted, refused, transformed, or degraded in a deterministic and auditable way.

This chapter is part of the synthesized reader, not a source-file transcript. It is written to preserve the meaning that recurs across current docs, archive material, and conversation synthesis while keeping the authority boundary visible.

**Current repo-backed picture.** AGENTS inherits the constitutional floor: process-only mutation, explicit refusal, no silent migrations, no hidden fallback magic, profiles over mode flags, and pack-driven integration. These rules protect replayability and semantic ownership.

The practical consequence is that this topic should be read through the current authority model first. If a current source and an archive source appear to disagree, the archive source becomes review evidence rather than a shortcut around current doctrine.

**Historical and advisory context.** The archive adds many examples of why this matters: Workbench must not become a hidden truth owner, providers must not silently substitute incompatible behavior, and generated assistant outputs must not become doctrine by accident.

That historical context is still useful. It shows why the topic kept returning, which boundaries people were worried about, and what kind of future work the project repeatedly imagined. The book preserves that context so it can be reviewed instead of rediscovered or silently re-invented.

**What remains unresolved.** Future promotion needs careful language around capability, refusal, and operator tools so that convenience workflows do not collapse authority boundaries.

**What not to assume.** Do not treat historical breadth as current permission. Do not infer implementation readiness from a polished description. Do not treat this book, the source reader, or any generated corpus report as a promotion into canon, contracts, schema, implementation, release state, or queue state.

**Review questions.**

- Which parts of this topic are already current repo truth?
- Which parts are merely consistent with current docs but not formalized?
- Which parts are blocked by queue state or need explicit human decision?
- Which source paths should be inspected before any later docs-only promotion?

**How to use this chapter.** Read this chapter as orientation, not as promotion. If later work wants to change canon, contracts, architecture, schema, implementation, release state, or queue state, it needs a separate scoped promotion task with explicit validation.

**Source trail:**

- `AGENTS.md`
- `docs/canon/constitution_v1.md`
- `docs/canon/glossary_v1.md`
- `docs/archive/conversations/_synthesis/PROJECT_SYNTHESIS_BOOK_v0.md`


## 7. Determinism, Replay, Provenance, And Validation

Determinism is the project's engineering spine. Identical canonical inputs should produce identical authoritative outputs, and evidence must make that fact reviewable.

This chapter is part of the synthesized reader, not a source-file transcript. It is written to preserve the meaning that recurs across current docs, archive material, and conversation synthesis while keeping the authority boundary visible.

**Current repo-backed picture.** Current governance requires named RNG streams, deterministic ordering, deterministic reductions, replay-hash equivalence where applicable, and validation before success is claimed. Validation reports are evidence, not replacement authority.

The practical consequence is that this topic should be read through the current authority model first. If a current source and an archive source appear to disagree, the archive source becomes review evidence rather than a shortcut around current doctrine.

**Historical and advisory context.** Conversation material extends this concern into long-term portability, world scale, release trust, and tool-assisted inspection. It treats evidence as a first-class product surface.

That historical context is still useful. It shows why the topic kept returning, which boundaries people were worried about, and what kind of future work the project repeatedly imagined. The book preserves that context so it can be reviewed instead of rediscovered or silently re-invented.

**What remains unresolved.** Full validation depth and release/trust proof remain visible debt outside narrow docs publication tasks. Generated books should report validation honestly and avoid implying runtime progress.

**What not to assume.** Do not treat historical breadth as current permission. Do not infer implementation readiness from a polished description. Do not treat this book, the source reader, or any generated corpus report as a promotion into canon, contracts, schema, implementation, release state, or queue state.

**Review questions.**

- Which parts of this topic are already current repo truth?
- Which parts are merely consistent with current docs but not formalized?
- Which parts are blocked by queue state or need explicit human decision?
- Which source paths should be inspected before any later docs-only promotion?

**How to use this chapter.** Read this chapter as orientation, not as promotion. If later work wants to change canon, contracts, architecture, schema, implementation, release state, or queue state, it needs a separate scoped promotion task with explicit validation.

**Source trail:**

- `README.md`
- `AGENTS.md`
- `docs/architecture/INVARIANTS.md`
- `docs/repo/FOUNDATION_LOCK.md`


## 8. Content, Packs, Modding, And Compatibility

Content and optional capability are meant to be declared, validated, and integrated through packs, registries, contracts, and compatibility law rather than hardcoded hidden branches.

This chapter is part of the synthesized reader, not a source-file transcript. It is written to preserve the meaning that recurs across current docs, archive material, and conversation synthesis while keeping the authority boundary visible.

**Current repo-backed picture.** Current doctrine requires explicit refusal or degradation when packs are missing. Contract and schema identity must be respected, and silent compatibility reinterpretation is forbidden.

The practical consequence is that this topic should be read through the current authority model first. If a current source and an archive source appear to disagree, the archive source becomes review evidence rather than a shortcut around current doctrine.

**Historical and advisory context.** The archive contains a wide design space around providers, content packs, modding, authored data, and future runtime packaging. That material is useful but queue-sensitive.

That historical context is still useful. It shows why the topic kept returning, which boundaries people were worried about, and what kind of future work the project repeatedly imagined. The book preserves that context so it can be reviewed instead of rediscovered or silently re-invented.

**What remains unresolved.** Provider runtime and package runtime remain blocked by current queue. Any promotion touching those areas should stay docs-only until the queue opens implementation scope.

**What not to assume.** Do not treat historical breadth as current permission. Do not infer implementation readiness from a polished description. Do not treat this book, the source reader, or any generated corpus report as a promotion into canon, contracts, schema, implementation, release state, or queue state.

**Review questions.**

- Which parts of this topic are already current repo truth?
- Which parts are merely consistent with current docs but not formalized?
- Which parts are blocked by queue state or need explicit human decision?
- Which source paths should be inspected before any later docs-only promotion?

**How to use this chapter.** Read this chapter as orientation, not as promotion. If later work wants to change canon, contracts, architecture, schema, implementation, release state, or queue state, it needs a separate scoped promotion task with explicit validation.

**Source trail:**

- `AGENTS.md`
- `README.md`
- `docs/archive/conversations/_promotion/PROMOTION_WAVE_1_CANDIDATES_v0.md`
- `docs/archive/docs_corpus/_reconciliation/DOCS_BLOCKED_SCOPE_ALIGNMENT_v0.md`


## 9. Runtime, Product Shells, UI, Renderer, And Platform

Product shells should project command/result/refusal/diagnostic/evidence truth. Rendering is presentation. UI is an operator or player surface. Neither should mutate authoritative truth directly.

This chapter is part of the synthesized reader, not a source-file transcript. It is written to preserve the meaning that recurs across current docs, archive material, and conversation synthesis while keeping the authority boundary visible.

**Current repo-backed picture.** Current queue state blocks broad Workbench UI, renderer implementation, native GUI, gameplay, provider runtime, package runtime, runtime module loading, and release publication. That queue fact is part of current truth.

The practical consequence is that this topic should be read through the current authority model first. If a current source and an archive source appear to disagree, the archive source becomes review evidence rather than a shortcut around current doctrine.

**Historical and advisory context.** Archived conversations are rich with renderer, platform, Workbench, setup, and product-shell ideas. They are valuable as future design backlog, but they cannot authorize implementation now.

That historical context is still useful. It shows why the topic kept returning, which boundaries people were worried about, and what kind of future work the project repeatedly imagined. The book preserves that context so it can be reviewed instead of rediscovered or silently re-invented.

**What remains unresolved.** The next safe work in this area is review, clarification, and narrow docs-only promotion candidate preparation, not broad feature execution.

**What not to assume.** Do not treat historical breadth as current permission. Do not infer implementation readiness from a polished description. Do not treat this book, the source reader, or any generated corpus report as a promotion into canon, contracts, schema, implementation, release state, or queue state.

**Review questions.**

- Which parts of this topic are already current repo truth?
- Which parts are merely consistent with current docs but not formalized?
- Which parts are blocked by queue state or need explicit human decision?
- Which source paths should be inspected before any later docs-only promotion?

**How to use this chapter.** Read this chapter as orientation, not as promotion. If later work wants to change canon, contracts, architecture, schema, implementation, release state, or queue state, it needs a separate scoped promotion task with explicit validation.

**Source trail:**

- `README.md`
- `.aide/queue/current.toml`
- `docs/repo/FOUNDATION_LOCK.md`
- `docs/archive/conversations/_synthesis/CURRENT_PROJECT_ATLAS_v0.md`


# Part III - Simulation And World Model


## 10. Reality, Existence, Space, Time, And Scale

The long-horizon world model is ambitious: existence, spatial refinement, visitability, timekeeping, chronology, scale, and simulation domains recur across the docs and conversations.

This chapter is part of the synthesized reader, not a source-file transcript. It is written to preserve the meaning that recurs across current docs, archive material, and conversation synthesis while keeping the authority boundary visible.

**Current repo-backed picture.** Current authority supports the separation of truth, perception, and render, plus deterministic process execution. It does not automatically promote every archived world-scale concept into current implementation scope.

The practical consequence is that this topic should be read through the current authority model first. If a current source and an archive source appear to disagree, the archive source becomes review evidence rather than a shortcut around current doctrine.

**Historical and advisory context.** Conversation synthesis adds the richest picture: worlds, planets, celestial systems, universe explorer ideas, real-world defaults, macro/micro transitions, and 2038 resilience concerns.

That historical context is still useful. It shows why the topic kept returning, which boundaries people were worried about, and what kind of future work the project repeatedly imagined. The book preserves that context so it can be reviewed instead of rediscovered or silently re-invented.

**What remains unresolved.** Each domain claim needs review against current contracts, code, and queue state before becoming current docs. The strongest near-term value is vocabulary and roadmap clarification.

**What not to assume.** Do not treat historical breadth as current permission. Do not infer implementation readiness from a polished description. Do not treat this book, the source reader, or any generated corpus report as a promotion into canon, contracts, schema, implementation, release state, or queue state.

**Review questions.**

- Which parts of this topic are already current repo truth?
- Which parts are merely consistent with current docs but not formalized?
- Which parts are blocked by queue state or need explicit human decision?
- Which source paths should be inspected before any later docs-only promotion?

**How to use this chapter.** Read this chapter as orientation, not as promotion. If later work wants to change canon, contracts, architecture, schema, implementation, release state, or queue state, it needs a separate scoped promotion task with explicit validation.

**Source trail:**

- `docs/archive/conversations/_synthesis/PROJECT_SYNTHESIS_BOOK_v0.md`
- `docs/archive/conversations/_synthesis/FULL_PROJECT_PICTURE_v0.md`
- `docs/archive/docs_corpus/_reconciliation/DOCS_CURRENT_PROJECT_PICTURE_v0.md`


## 11. Civilization, Economy, Logistics, Institutions, And Signals

Dominium's product identity repeatedly points toward systems where production, logistics, economics, settlement, trust, communication, institutions, and power emerge from lawful simulation.

This chapter is part of the synthesized reader, not a source-file transcript. It is written to preserve the meaning that recurs across current docs, archive material, and conversation synthesis while keeping the authority boundary visible.

**Current repo-backed picture.** The README directly names invention, production, logistics, economics, settlement, trust, communication, and institutional power. That makes these themes current identity, even where detailed gameplay remains blocked.

The practical consequence is that this topic should be read through the current authority model first. If a current source and an archive source appear to disagree, the archive source becomes review evidence rather than a shortcut around current doctrine.

**Historical and advisory context.** The archive expands these themes into civilization simulation, infrastructure, economy, governance, signals, and long-term world dynamics. Those are design signals rather than permission to implement gameplay.

That historical context is still useful. It shows why the topic kept returning, which boundaries people were worried about, and what kind of future work the project repeatedly imagined. The book preserves that context so it can be reviewed instead of rediscovered or silently re-invented.

**What remains unresolved.** The unresolved question is sequencing: which social and economic concepts need canon vocabulary, which need architecture docs, and which must wait for gameplay scope to open.

**What not to assume.** Do not treat historical breadth as current permission. Do not infer implementation readiness from a polished description. Do not treat this book, the source reader, or any generated corpus report as a promotion into canon, contracts, schema, implementation, release state, or queue state.

**Review questions.**

- Which parts of this topic are already current repo truth?
- Which parts are merely consistent with current docs but not formalized?
- Which parts are blocked by queue state or need explicit human decision?
- Which source paths should be inspected before any later docs-only promotion?

**How to use this chapter.** Read this chapter as orientation, not as promotion. If later work wants to change canon, contracts, architecture, schema, implementation, release state, or queue state, it needs a separate scoped promotion task with explicit validation.

**Source trail:**

- `README.md`
- `docs/archive/conversations/_synthesis/PROJECT_SYNTHESIS_BOOK_v0.md`
- `docs/archive/conversations/_decision/DECISION_SUMMARY_v0.md`


## 12. Worldgen, Astronomy, Planetary Systems, And Domains

World generation and planetary/celestial systems appear as recurring domain ambitions. The material matters because scale and chronology affect determinism, storage, rendering, and simulation law.

This chapter is part of the synthesized reader, not a source-file transcript. It is written to preserve the meaning that recurs across current docs, archive material, and conversation synthesis while keeping the authority boundary visible.

**Current repo-backed picture.** Current repo truth requires deterministic ordering, explicit constraints, and clear contract boundaries. A worldgen idea is not current authority unless supported by current docs or later promotion.

The practical consequence is that this topic should be read through the current authority model first. If a current source and an archive source appear to disagree, the archive source becomes review evidence rather than a shortcut around current doctrine.

**Historical and advisory context.** Conversation material includes chronology, celestial alignment, universe-scale thinking, planetary systems, and domain-specific packs. It is a strong source of historical design intent.

That historical context is still useful. It shows why the topic kept returning, which boundaries people were worried about, and what kind of future work the project repeatedly imagined. The book preserves that context so it can be reviewed instead of rediscovered or silently re-invented.

**What remains unresolved.** Future review should separate vocabulary, deterministic model requirements, data/pack boundaries, and implementation plans. Those are different promotion tracks.

**What not to assume.** Do not treat historical breadth as current permission. Do not infer implementation readiness from a polished description. Do not treat this book, the source reader, or any generated corpus report as a promotion into canon, contracts, schema, implementation, release state, or queue state.

**Review questions.**

- Which parts of this topic are already current repo truth?
- Which parts are merely consistent with current docs but not formalized?
- Which parts are blocked by queue state or need explicit human decision?
- Which source paths should be inspected before any later docs-only promotion?

**How to use this chapter.** Read this chapter as orientation, not as promotion. If later work wants to change canon, contracts, architecture, schema, implementation, release state, or queue state, it needs a separate scoped promotion task with explicit validation.

**Source trail:**

- `docs/archive/conversations/_synthesis/PROJECT_SYNTHESIS_BOOK_v0.md`
- `docs/archive/conversations/_synthesis/WHAT_NEEDS_DECISION_v0.md`
- `docs/archive/docs_corpus/_audit/DOCS_STALENESS_AND_VERIFICATION_v0.md`


# Part IV - Tools, Workbench, AIDE, Codex, And Governance


## 13. Workbench As A Governed Operator Surface

Workbench should be read as an operator, validation, evidence, inspection, and later editing surface. It is not an authority layer.

This chapter is part of the synthesized reader, not a source-file transcript. It is written to preserve the meaning that recurs across current docs, archive material, and conversation synthesis while keeping the authority boundary visible.

**Current repo-backed picture.** The README says Workbench consumes the same contracts and services as other products. Current queue blocks broad Workbench UI, so even aligned Workbench ideas remain future-scoped.

The practical consequence is that this topic should be read through the current authority model first. If a current source and an archive source appear to disagree, the archive source becomes review evidence rather than a shortcut around current doctrine.

**Historical and advisory context.** The conversation corpus strongly values Workbench because it makes a large deterministic system inspectable. That design intent is useful, but it must be reconciled with queue limits.

That historical context is still useful. It shows why the topic kept returning, which boundaries people were worried about, and what kind of future work the project repeatedly imagined. The book preserves that context so it can be reviewed instead of rediscovered or silently re-invented.

**What remains unresolved.** Near-term Workbench work should remain narrow, validation-oriented, and contract-aware unless a later reviewed queue opens broad UI scope.

**What not to assume.** Do not treat historical breadth as current permission. Do not infer implementation readiness from a polished description. Do not treat this book, the source reader, or any generated corpus report as a promotion into canon, contracts, schema, implementation, release state, or queue state.

**Review questions.**

- Which parts of this topic are already current repo truth?
- Which parts are merely consistent with current docs but not formalized?
- Which parts are blocked by queue state or need explicit human decision?
- Which source paths should be inspected before any later docs-only promotion?

**How to use this chapter.** Read this chapter as orientation, not as promotion. If later work wants to change canon, contracts, architecture, schema, implementation, release state, or queue state, it needs a separate scoped promotion task with explicit validation.

**Source trail:**

- `README.md`
- `.aide/queue/current.toml`
- `docs/archive/conversations/_synthesis/CURRENT_PROJECT_ATLAS_v0.md`


## 14. AIDE And Codex As Repo Control-Plane Harnesses

AIDE and Codex are useful because they can inventory, generate, validate, package, and patch bounded repo artifacts. They are dangerous if treated as semantic authority.

This chapter is part of the synthesized reader, not a source-file transcript. It is written to preserve the meaning that recurs across current docs, archive material, and conversation synthesis while keeping the authority boundary visible.

**Current repo-backed picture.** AGENTS defines the role clearly: agents must consult doctrine, preserve authority ordering, avoid replacing repo truth with chat memory, and validate honestly. Generated outputs are evidence unless promoted by stronger authority.

The practical consequence is that this topic should be read through the current authority model first. If a current source and an archive source appear to disagree, the archive source becomes review evidence rather than a shortcut around current doctrine.

**Historical and advisory context.** The archive shows AIDE/Codex as future control-plane and workflow helpers. That is compatible with current governance only when bounded by queue state, validation, and review gates.

That historical context is still useful. It shows why the topic kept returning, which boundaries people were worried about, and what kind of future work the project repeatedly imagined. The book preserves that context so it can be reviewed instead of rediscovered or silently re-invented.

**What remains unresolved.** Future automation should improve reviewability rather than bypass review. This book itself is evidence and orientation, not authority.

**What not to assume.** Do not treat historical breadth as current permission. Do not infer implementation readiness from a polished description. Do not treat this book, the source reader, or any generated corpus report as a promotion into canon, contracts, schema, implementation, release state, or queue state.

**Review questions.**

- Which parts of this topic are already current repo truth?
- Which parts are merely consistent with current docs but not formalized?
- Which parts are blocked by queue state or need explicit human decision?
- Which source paths should be inspected before any later docs-only promotion?

**How to use this chapter.** Read this chapter as orientation, not as promotion. If later work wants to change canon, contracts, architecture, schema, implementation, release state, or queue state, it needs a separate scoped promotion task with explicit validation.

**Source trail:**

- `AGENTS.md`
- `docs/planning/AUTHORITY_ORDER.md`
- `docs/archive/conversations/_synthesis/PROJECT_SYNTHESIS_BOOK_v0.md`


## 15. Documentation, Archive, And Conversation Corpus

The docs corpus is now a navigable source map. The conversation corpus is a historical design-intent layer. The archive preserves context that would be unsafe to merge directly into canon.

This chapter is part of the synthesized reader, not a source-file transcript. It is written to preserve the meaning that recurs across current docs, archive material, and conversation synthesis while keeping the authority boundary visible.

**Current repo-backed picture.** Current docs taxonomy and AGENTS both support the distinction: archive material may inform future work, but current repo artifacts outrank generated summaries and chat claims.

The practical consequence is that this topic should be read through the current authority model first. If a current source and an archive source appear to disagree, the archive source becomes review evidence rather than a shortcut around current doctrine.

**Historical and advisory context.** The conversation pipeline created readers, wiki pages, audit reports, decision dockets, promotion queues, and synthesis books. Those are valuable review surfaces.

That historical context is still useful. It shows why the topic kept returning, which boundaries people were worried about, and what kind of future work the project repeatedly imagined. The book preserves that context so it can be reviewed instead of rediscovered or silently re-invented.

**What remains unresolved.** The next step is selective adjudication, not bulk promotion. Every future doc patch should name source claims, target docs, authority support, non-goals, and validation.

**What not to assume.** Do not treat historical breadth as current permission. Do not infer implementation readiness from a polished description. Do not treat this book, the source reader, or any generated corpus report as a promotion into canon, contracts, schema, implementation, release state, or queue state.

**Review questions.**

- Which parts of this topic are already current repo truth?
- Which parts are merely consistent with current docs but not formalized?
- Which parts are blocked by queue state or need explicit human decision?
- Which source paths should be inspected before any later docs-only promotion?

**How to use this chapter.** Read this chapter as orientation, not as promotion. If later work wants to change canon, contracts, architecture, schema, implementation, release state, or queue state, it needs a separate scoped promotion task with explicit validation.

**Source trail:**

- `docs/README.md`
- `AGENTS.md`
- `docs/archive/conversations/_synthesis/READ_THIS_FIRST_v0.md`
- `docs/archive/docs_corpus/_archive/DOCS_CONVERSATION_CORPUS_INTEGRATION_v0.md`


# Part V - What We Know, What We Do Not Know, And What Comes Next


## 16. Current Confirmed Picture

The strongest confirmed picture is layered and conservative: Dominium is the official simulation/product/domain layer on Domino; Domino is the deterministic substrate; truth mutation is process-only; products project command/result/evidence surfaces; archive material is advisory.

This chapter is part of the synthesized reader, not a source-file transcript. It is written to preserve the meaning that recurs across current docs, archive material, and conversation synthesis while keeping the authority boundary visible.

**Current repo-backed picture.** This picture is supported by README, canon, glossary, AGENTS, current queue state, and docs-corpus reconciliation. It is stronger than any single archive conversation.

The practical consequence is that this topic should be read through the current authority model first. If a current source and an archive source appear to disagree, the archive source becomes review evidence rather than a shortcut around current doctrine.

**Historical and advisory context.** Historical sources add breadth: world scale, Workbench aspirations, release identity, provider/content boundaries, setup, launcher, and long-term platform goals.

That historical context is still useful. It shows why the topic kept returning, which boundaries people were worried about, and what kind of future work the project repeatedly imagined. The book preserves that context so it can be reviewed instead of rediscovered or silently re-invented.

**What remains unresolved.** The confirmed picture is not the same as a complete roadmap. Many details remain in decision, promotion, blocked-scope, or verification queues.

**What not to assume.** Do not treat historical breadth as current permission. Do not infer implementation readiness from a polished description. Do not treat this book, the source reader, or any generated corpus report as a promotion into canon, contracts, schema, implementation, release state, or queue state.

**Review questions.**

- Which parts of this topic are already current repo truth?
- Which parts are merely consistent with current docs but not formalized?
- Which parts are blocked by queue state or need explicit human decision?
- Which source paths should be inspected before any later docs-only promotion?

**How to use this chapter.** Read this chapter as orientation, not as promotion. If later work wants to change canon, contracts, architecture, schema, implementation, release state, or queue state, it needs a separate scoped promotion task with explicit validation.

**Source trail:**

- `README.md`
- `docs/canon/constitution_v1.md`
- `docs/canon/glossary_v1.md`
- `AGENTS.md`
- `docs/archive/docs_corpus/_reconciliation/DOCS_CURRENT_PROJECT_PICTURE_v0.md`


## 17. Major Open Decisions

The decision backlog is now a review surface. It should be read as a set of human questions, future queue decisions, and repo-authority decisions rather than as accepted answers.

This chapter is part of the synthesized reader, not a source-file transcript. It is written to preserve the meaning that recurs across current docs, archive material, and conversation synthesis while keeping the authority boundary visible.

**Current repo-backed picture.** Current reconciliation separates user decisions, future queue decisions, deferred items, blocked-scope decisions, and evidence gaps. That separation prevents old conversations from silently becoming live doctrine.

The practical consequence is that this topic should be read through the current authority model first. If a current source and an archive source appear to disagree, the archive source becomes review evidence rather than a shortcut around current doctrine.

**Historical and advisory context.** The most important categories are architecture/boundaries, Workbench/AIDE/Codex/tooling, renderer/UI/platform, provider/content/packs, world/time/civilization simulation, release/setup/launcher, and documentation/canon/spec structure.

That historical context is still useful. It shows why the topic kept returning, which boundaries people were worried about, and what kind of future work the project repeatedly imagined. The book preserves that context so it can be reviewed instead of rediscovered or silently re-invented.

**What remains unresolved.** Unresolved decisions should default to defer unless there is current authority support and a narrow task that can patch documentation without widening scope.

**What not to assume.** Do not treat historical breadth as current permission. Do not infer implementation readiness from a polished description. Do not treat this book, the source reader, or any generated corpus report as a promotion into canon, contracts, schema, implementation, release state, or queue state.

**Review questions.**

- Which parts of this topic are already current repo truth?
- Which parts are merely consistent with current docs but not formalized?
- Which parts are blocked by queue state or need explicit human decision?
- Which source paths should be inspected before any later docs-only promotion?

**How to use this chapter.** Read this chapter as orientation, not as promotion. If later work wants to change canon, contracts, architecture, schema, implementation, release state, or queue state, it needs a separate scoped promotion task with explicit validation.

**Source trail:**

- `docs/archive/docs_corpus/_reconciliation/DOCS_DECISION_DOCKET_v0.md`
- `docs/archive/conversations/_decision/DECISION_SUMMARY_v0.md`
- `docs/archive/conversations/_decision/DECISION_DOCKET_v0.md`


## 18. Contradictions, Stale Material, And Archive Drift

Contradictions are not defects in the book; they are review triggers. A mature corpus should show where old claims disagree with current authority, current queue state, or other archive material.

This chapter is part of the synthesized reader, not a source-file transcript. It is written to preserve the meaning that recurs across current docs, archive material, and conversation synthesis while keeping the authority boundary visible.

**Current repo-backed picture.** Current audit reports identify stale claims, duplicate shadows, authority conflicts, and coverage gaps. The correct response is quarantine and review, not convenient synthesis.

The practical consequence is that this topic should be read through the current authority model first. If a current source and an archive source appear to disagree, the archive source becomes review evidence rather than a shortcut around current doctrine.

**Historical and advisory context.** Conversation material is especially prone to drift because it was produced across many sessions and goals. The value of the audit layer is that it prevents drift from hiding inside polished prose.

That historical context is still useful. It shows why the topic kept returning, which boundaries people were worried about, and what kind of future work the project repeatedly imagined. The book preserves that context so it can be reviewed instead of rediscovered or silently re-invented.

**What remains unresolved.** Future review should prioritize contradictions that touch canon, contracts, schema, queue scope, release meaning, or implementation authority.

**What not to assume.** Do not treat historical breadth as current permission. Do not infer implementation readiness from a polished description. Do not treat this book, the source reader, or any generated corpus report as a promotion into canon, contracts, schema, implementation, release state, or queue state.

**Review questions.**

- Which parts of this topic are already current repo truth?
- Which parts are merely consistent with current docs but not formalized?
- Which parts are blocked by queue state or need explicit human decision?
- Which source paths should be inspected before any later docs-only promotion?

**How to use this chapter.** Read this chapter as orientation, not as promotion. If later work wants to change canon, contracts, architecture, schema, implementation, release state, or queue state, it needs a separate scoped promotion task with explicit validation.

**Source trail:**

- `docs/archive/docs_corpus/_audit/DOCS_CONTRADICTION_MATRIX_v0.md`
- `docs/archive/docs_corpus/_audit/DOCS_STALENESS_AND_VERIFICATION_v0.md`
- `docs/archive/conversations/_synthesis/CONTRADICTIONS_TO_RECONCILE_v0.md`


## 19. Promotion Candidates And Safe Next Steps

Promotion candidates are leads, not instructions. A candidate becomes useful only when a later task names the exact source claim, target doc, authority compatibility, validation, and review disposition.

This chapter is part of the synthesized reader, not a source-file transcript. It is written to preserve the meaning that recurs across current docs, archive material, and conversation synthesis while keeping the authority boundary visible.

**Current repo-backed picture.** Current promotion surfaces include docs-corpus candidates and conversation-derived candidates. Many are metadata/header hygiene rather than substantive doctrine. Some are blocked by queue or require user decision.

The practical consequence is that this topic should be read through the current authority model first. If a current source and an archive source appear to disagree, the archive source becomes review evidence rather than a shortcut around current doctrine.

**Historical and advisory context.** The safest near-term promotions are narrow docs-only clarifications that do not alter canon, contracts, schema, implementation, release, or queue state. Anything broader needs explicit human review.

That historical context is still useful. It shows why the topic kept returning, which boundaries people were worried about, and what kind of future work the project repeatedly imagined. The book preserves that context so it can be reviewed instead of rediscovered or silently re-invented.

**What remains unresolved.** The next practical step is to triage the promotion queue into hygiene, genuine clarification, archive-only preservation, blocked, noisy, and user-decision groups.

**What not to assume.** Do not treat historical breadth as current permission. Do not infer implementation readiness from a polished description. Do not treat this book, the source reader, or any generated corpus report as a promotion into canon, contracts, schema, implementation, release state, or queue state.

**Review questions.**

- Which parts of this topic are already current repo truth?
- Which parts are merely consistent with current docs but not formalized?
- Which parts are blocked by queue state or need explicit human decision?
- Which source paths should be inspected before any later docs-only promotion?

**How to use this chapter.** Read this chapter as orientation, not as promotion. If later work wants to change canon, contracts, architecture, schema, implementation, release state, or queue state, it needs a separate scoped promotion task with explicit validation.

**Source trail:**

- `docs/archive/docs_corpus/_reconciliation/DOCS_PROMOTION_QUEUE_v0.md`
- `docs/archive/conversations/_promotion/PROMOTION_WAVE_1_CANDIDATES_v0.md`
- `docs/archive/conversations/_promotion/PROMOTION_TRIAGE_v0.md`


## 20. Recommended Reading And Review Roadmap

Use the HTML book for navigation and search. Use the PDF for sequential reading. Use the source reader when you need original prose. Use manifests and registers only when auditing.

This chapter is part of the synthesized reader, not a source-file transcript. It is written to preserve the meaning that recurs across current docs, archive material, and conversation synthesis while keeping the authority boundary visible.

**Current repo-backed picture.** Start with the current authority packet, then the current project picture, then the conversation atlas, then the decision docket and promotion queue. Do not start with raw manifests.

The practical consequence is that this topic should be read through the current authority model first. If a current source and an archive source appear to disagree, the archive source becomes review evidence rather than a shortcut around current doctrine.

**Historical and advisory context.** Review should proceed from comprehension to decision to promotion. Live-doc changes should remain narrow and traceable, with validation evidence and no silent authority changes.

That historical context is still useful. It shows why the topic kept returning, which boundaries people were worried about, and what kind of future work the project repeatedly imagined. The book preserves that context so it can be reviewed instead of rediscovered or silently re-invented.

**What remains unresolved.** This book should be reviewed as a human artifact. The next iteration should incorporate reader feedback, improve topic indexing, and only then prepare a small docs-only promotion wave.

**What not to assume.** Do not treat historical breadth as current permission. Do not infer implementation readiness from a polished description. Do not treat this book, the source reader, or any generated corpus report as a promotion into canon, contracts, schema, implementation, release state, or queue state.

**Review questions.**

- Which parts of this topic are already current repo truth?
- Which parts are merely consistent with current docs but not formalized?
- Which parts are blocked by queue state or need explicit human decision?
- Which source paths should be inspected before any later docs-only promotion?

**How to use this chapter.** Read this chapter as orientation, not as promotion. If later work wants to change canon, contracts, architecture, schema, implementation, release state, or queue state, it needs a separate scoped promotion task with explicit validation.

**Source trail:**

- `docs/archive/docs_corpus/_human_source/HUMAN_SOURCE_INDEX.md`
- `docs/archive/docs_corpus/_reconciliation/DOCS_CURRENT_PROJECT_PICTURE_v0.md`
- `docs/archive/docs_corpus/_reconciliation/DOCS_PROMOTION_QUEUE_v0.md`


# Appendices

## Appendix A - Source Documents Used

Human-readable full-text documents: 189.

- `AGENTS.md` - Dominium Agent Governance
- `README.md` - Dominium / Domino
- `docs/README.md` - Dominium Documentation
- `docs/architecture/CANONICAL_SYSTEM_MAP.md` - Canonical System Map (canon0)
- `docs/architecture/CONTRACTS_INDEX.md` - Contracts Index (const0)
- `docs/architecture/INVARIANTS.md` - Invariants (canon0)
- `docs/architecture/WHAT_THIS_IS.md` - What This Project Is (canon0)
- `docs/architecture/WHAT_THIS_IS_NOT.md` - What This Project Is Not (canon0)
- `docs/archive/conversations/Build_and_Future_Proofing/Dominium_Build_and_Future_Proofing_Architecture__01_human_readable_report.md` - Complete Chat Preservation Report Dominium Build And Future Proofing Architecture
- `docs/archive/conversations/Build_and_Future_Proofing/Dominium_Build_and_Future_Proofing_Architecture__06_reader_brief.md` - Reader Brief Dominium Build And Future Proofing Architecture
- `docs/archive/conversations/Build_and_Future_Proofing/Dominium_Build_and_Future_Proofing_Architecture__09_in_chat_reader.md` - In Chat Reader Dominium Build And Future Proofing Architecture
- `docs/archive/conversations/Build_and_Future_Proofing/Dominium_Build_and_Future_Proofing_Architecture__10_accompanying_human_readable_detailed_summary_report.md` - Accompanying Human Readable Detailed Conversation Report
- `docs/archive/conversations/Chronology_Celestial_Systems/Dominium_Chronology_Celestial_Systems__05_reader_brief.md` - Reader Brief Dominium Chronology & Celestial Systems
- `docs/archive/conversations/Dominium_Architecture_I/Dominium_Architecture_I__05_reader_brief.md` - Reader Brief Dominium Architecture I
- `docs/archive/conversations/Dominium_Architecture_II/Dominium_Architecture_II__05_reader_brief.md` - Reader Brief Dominium Architecture Ii
- `docs/archive/conversations/Dominium_Architecture_III/Dominium_Architecture_III__05_reader_brief.md` - Reader Brief Dominium Architecture Iii
- `docs/archive/conversations/Dominium_Architecture_IV/Dominium_Architecture_IV__05_reader_brief.md` - Reader Brief Dominium Architecture Iv
- `docs/archive/conversations/Dominium_Complete_Conversation/Accompanying_Report/Dominium_Canon_Portability_Audit__01_human_readable_report.md` - Complete Chat Preservation Report Dominium Canon, Repository Alignment, And Portability Doctrine
- `docs/archive/conversations/Dominium_Complete_Conversation/Accompanying_Report/Dominium_Canon_Portability_Audit__06_reader_brief.md` - Reader Brief Dominium Canon, Repository Alignment, And Portability Doctrine
- `docs/archive/conversations/Dominium_Complete_Conversation/Accompanying_Report/Dominium_Canon_Portability_Audit__07_verification_and_audit.md` - Self Audit And Revision Dominium Canon, Repository Alignment, And Portability Doctrine
- `docs/archive/conversations/Dominium_Complete_Conversation/Accompanying_Report/Dominium_Canon_Portability_Audit__08_future_chat_bootstrap_prompt.md` - Future Chat Bootstrap Prompt
- `docs/archive/conversations/Dominium_Complete_Conversation/Accompanying_Report/Dominium_Canon_Portability_Audit__09_in_chat_reader.md` - In Chat Reader Dominium Canon, Repository Alignment, And Portability Doctrine
- `docs/archive/conversations/Dominium_Complete_Conversation/Accompanying_Report/Dominium_Entire_Conversation_Accompanying_Report__10_accompanying_detailed_summary_report.md` - Accompanying Human Readable Detailed Summary And Report Dominium Canon, Repository Alignment, And Portability Doctrine
- `docs/archive/conversations/Dominium_Complete_Conversation/Accompanying_Report/Dominium_Entire_Conversation_Accompanying_Report__README_FIRST.md` - Readme First Dominium Conversation Complete Bundle
- `docs/archive/conversations/Dominium_Complete_Conversation/Accompanying_Report/Dominium_Entire_Conversation_Accompanying_Report__source_uploaded_preservation_prompt.txt` - Complete Chat Preservation Report [chat Label]
- `docs/archive/conversations/Dominium_Complete_Conversation/Accompanying_Report/Pasted text.txt` - Complete Chat Preservation Report [chat Label]
- `docs/archive/conversations/Dominium_Complete_Conversation/deterministic_solar_system_handoff_file/Dominium_Deterministic_Solar_System_Architecture__01_human_readable_report.md` - Complete Chat Preservation Report Dominium Deterministic Solar System Architecture
- `docs/archive/conversations/Dominium_Complete_Conversation/deterministic_solar_system_handoff_file/Dominium_Deterministic_Solar_System_Architecture__06_reader_brief.md` - Reader Brief Dominium Deterministic Solar System Architecture
- `docs/archive/conversations/Dominium_Complete_Conversation/deterministic_solar_system_handoff_file/Dominium_Deterministic_Solar_System_Architecture__09_in_chat_reader.md` - In Chat Reader Dominium Deterministic Solar System Architecture
- `docs/archive/conversations/Dominium_Complete_Conversation/deterministic_solar_system_handoff_file/Dominium_Deterministic_Solar_System_Architecture__10_accompanying_detailed_summary_and_report.md` - Accompanying Detailed Human Readable Summary And Report Dominium Deterministic Solar System Architecture
- `docs/archive/conversations/Dominium_Complete_Conversation/deterministic_solar_system_handoff_file/Dominium_Deterministic_Solar_System_Architecture__10_accompanying_human_readable_detailed_summary_report.md` - Accompanying Human Readable Detailed Summary And Report
- `docs/archive/conversations/Dominium_Complete_Conversation/existing_companion_report_package/Dominium_Complete_Conversation_Companion_Report__human_readable_detailed_summary.md` - Dominium / Domino Complete Conversation Companion Report
- `docs/archive/conversations/Dominium_Complete_Conversation/existing_complete_preservation_package/Dominium_Complete_Conversation_Preservation__10_accompanying_human_readable_detailed_summary_report.md` - Accompanying Human Readable Detailed Summary And Report
- `docs/archive/conversations/Dominium_Complete_Conversation/robotic_seed_civilisation_handoff_file/Dominium_Robotic_Seed_Civilisation_Architecture__01_human_readable_report.md` - Complete Chat Preservation Report Dominium Robotic Seed Civilisation Architecture
- `docs/archive/conversations/Dominium_Complete_Conversation/robotic_seed_civilisation_handoff_file/Dominium_Robotic_Seed_Civilisation_Architecture__06_reader_brief.md` - Reader Brief Dominium Robotic Seed Civilisation Architecture
- `docs/archive/conversations/Dominium_Complete_Conversation/robotic_seed_civilisation_handoff_file/Dominium_Robotic_Seed_Civilisation_Architecture__09_in_chat_reader.md` - In Chat Reader Dominium Robotic Seed Civilisation Architecture
- `docs/archive/conversations/Domino_Dominium_Workbench/dominium_workbench_full_conversation_companion__human_readable_detailed_summary_report.md` - Dominium Workbench Full Conversation Companion Report
- `docs/archive/conversations/Domino_Dominium_Workbench/prior_preservation_files/dominium_workbench_presentation_spine_universe_explorer_planning__01_human_readable_report.md` - Complete Chat Preservation Report Dominium Workbench, Presentation Spine, And Universe Explorer Planning
- `docs/archive/conversations/Domino_Dominium_Workbench/prior_preservation_files/dominium_workbench_presentation_spine_universe_explorer_planning__06_reader_brief.md` - Reader Brief Dominium Workbench, Presentation Spine, And Universe Explorer Planning
- `docs/archive/conversations/Domino_Dominium_Workbench/prior_preservation_files/dominium_workbench_presentation_spine_universe_explorer_planning__09_in_chat_reader.md` - In Chat Reader Dominium Workbench, Presentation Spine, And Universe Explorer Planning
- `docs/archive/conversations/Foundation_Workbench_Codex/Dominium_Foundation_Workbench_Parallel_Codex_Preservation__01_human_readable_report.md` - Complete Chat Preservation Report Dominium Foundation Lock, Workbench Spine, And Parallel Codex Handoff
- `docs/archive/conversations/Foundation_Workbench_Codex/Dominium_Foundation_Workbench_Parallel_Codex_Preservation__06_reader_brief.md` - Reader Brief Dominium Foundation Lock, Workbench Spine, And Parallel Codex Handoff
- `docs/archive/conversations/Foundation_Workbench_Codex/Dominium_Foundation_Workbench_Parallel_Codex_Preservation__09_in_chat_reader.md` - In Chat Reader Dominium Foundation Lock, Workbench Spine, And Parallel Codex Handoff
- `docs/archive/conversations/Foundation_Workbench_Codex/Dominium_Foundation_Workbench_Parallel_Codex_Preservation__10_accompanying_detailed_summary_report.md` - Accompanying Human Readable Detailed Summary And Continuity Report
- `docs/archive/conversations/Framework_Open_Source_Provider/Domino_Framework_Open_Source_Provider_Architecture__01_human_readable_report.md` - Complete Chat Preservation Report Domino Framework And Open Source Provider Architecture
- `docs/archive/conversations/Framework_Open_Source_Provider/Domino_Framework_Open_Source_Provider_Architecture__06_reader_brief.md` - Reader Brief Domino Framework And Open Source Provider Architecture
- `docs/archive/conversations/Framework_Open_Source_Provider/Domino_Framework_Open_Source_Provider_Architecture__09_in_chat_reader.md` - In Chat Reader Domino Framework And Open Source Provider Architecture
- `docs/archive/conversations/Language_Platform_Architecture/Dominium_Language_Platform_Architecture_Baseline__01_human_readable_report.md` - Complete Chat Preservation Report Dominium Language, Platform, And Architecture Baseline
- `docs/archive/conversations/Language_Platform_Architecture/Dominium_Language_Platform_Architecture_Baseline__06_reader_brief.md` - Reader Brief Dominium Language, Platform, And Architecture Baseline
- `docs/archive/conversations/Language_Platform_Architecture/Dominium_Language_Platform_Architecture_Baseline__09_in_chat_reader.md` - In Chat Reader Dominium Language, Platform, And Architecture Baseline
- `docs/archive/conversations/Launcher_Setup_Architecture/Dominium_Launcher_Setup_Architecture__05_reader_brief.md` - Reader Brief Dominium Launcher Setup Architecture
- `docs/archive/conversations/Modularity_AIDE_Refactorability/Dominium_Modularity_AIDE_Refactorability_Architecture__01_human_readable_report.md` - Complete Chat Preservation Report Dominium Modularity, AIDE Refactorability, And Future Proof Architecture
- `docs/archive/conversations/Modularity_AIDE_Refactorability/Dominium_Modularity_AIDE_Refactorability_Architecture__06_reader_brief.md` - Reader Brief Dominium Modularity, AIDE Refactorability, And Future Proof Architecture
- `docs/archive/conversations/Modularity_AIDE_Refactorability/Dominium_Modularity_AIDE_Refactorability_Architecture__09_in_chat_reader.md` - In Chat Reader Dominium Modularity, AIDE Refactorability, And Future Proof Architecture
- `docs/archive/conversations/OS_Interface_Repo_Architecture/Dominium_OS_Interface_Repo_Architecture__01_human_readable_report.md` - Complete Chat Preservation Report Dominium Os Like Architecture, Repository Convergence, And Interface Operating Layer
- `docs/archive/conversations/OS_Interface_Repo_Architecture/Dominium_OS_Interface_Repo_Architecture__06_reader_brief.md` - Reader Brief Dominium Os Like Architecture, Repository Convergence, And Interface Operating Layer
- `docs/archive/conversations/OS_Interface_Repo_Architecture/Dominium_OS_Interface_Repo_Architecture__09_in_chat_reader.md` - In Chat Reader Dominium Os Like Architecture, Repository Convergence, And Interface Operating Layer
- `docs/archive/conversations/OS_Interface_Repo_Architecture/Dominium_OS_Interface_Repo_Architecture__10_accompanying_detailed_summary_report.md` - Accompanying Human Readable Detailed Summary And Report
- `docs/archive/conversations/Portability_Assurance_Future_Proof/Domino_Dominium_Portability_Assurance_Future_Proof_Architecture__01_human_readable_report.md` - Complete Chat Preservation Report Domino/dominium Portability, Assurance, And Future Proof Architecture
- `docs/archive/conversations/Portability_Assurance_Future_Proof/Domino_Dominium_Portability_Assurance_Future_Proof_Architecture__06_reader_brief.md` - Reader Brief Domino/dominium Portability, Assurance, And Future Proof Architecture
- `docs/archive/conversations/Portability_Assurance_Future_Proof/Domino_Dominium_Portability_Assurance_Future_Proof_Architecture__09_in_chat_reader.md` - In Chat Reader Domino/dominium Portability, Assurance, And Future Proof Architecture
- `docs/archive/conversations/Portability_Assurance_Future_Proof/Domino_Dominium_Portability_Assurance_Future_Proof_Architecture__10_accompanying_detailed_summary_report.md` - Accompanying Human Readable Detailed Summary And Report
- `docs/archive/conversations/Refactor_Architecture/Dominium_Domino_Refactor_Architecture__05_reader_brief.md` - Reader Brief Dominium + Domino Refactor Architecture
- `docs/archive/conversations/Refactor_Control_Plane/AIDE_XStack_Dominium_Refactor_Control_Plane__01_human_readable_report.md` - Complete Chat Preservation Report Aide, Xstack, And Dominium Refactor Control Plane
- `docs/archive/conversations/Refactor_Control_Plane/AIDE_XStack_Dominium_Refactor_Control_Plane__06_reader_brief.md` - Reader Brief AIDE Xstack Dominium Refactor Control Plane
- `docs/archive/conversations/Refactor_Control_Plane/AIDE_XStack_Dominium_Refactor_Control_Plane__09_in_chat_reader.md` - In Chat Reader AIDE Xstack Dominium Refactor Control Plane
- `docs/archive/conversations/Release_Identity_and_Versioning/Dominium_XStack_Release_Identity_and_Versioning__01_human_readable_report.md` - Complete Chat Preservation Report Dominium Xstack Release Identity And Versioning
- `docs/archive/conversations/Release_Identity_and_Versioning/Dominium_XStack_Release_Identity_and_Versioning__06_reader_brief.md` - Reader Brief Dominium Xstack Release Identity And Versioning
- `docs/archive/conversations/Release_Identity_and_Versioning/Dominium_XStack_Release_Identity_and_Versioning__09_in_chat_reader.md` - In Chat Reader Dominium Xstack Release Identity And Versioning
- `docs/archive/conversations/Timekeeping_and_2038_Resilience/Dominium_Timekeeping_and_2038_Resilience__01_human_readable_report.md` - Complete Chat Preservation Report Dominium Timekeeping And 2038 Resilience
- `docs/archive/conversations/Timekeeping_and_2038_Resilience/Dominium_Timekeeping_and_2038_Resilience__06_reader_brief.md` - Reader Brief Dominium Timekeeping And 2038 Resilience
- `docs/archive/conversations/Timekeeping_and_2038_Resilience/Dominium_Timekeeping_and_2038_Resilience__09_in_chat_reader.md` - In Chat Reader Dominium Timekeeping And 2038 Resilience
- `docs/archive/conversations/Timekeeping_and_2038_Resilience/Dominium_Timekeeping_and_2038_Resilience__10_accompanying_detailed_summary_report.md` - Accompanying Human Readable Detailed Summary And Report Dominium Timekeeping And 2038 Resilience
- `docs/archive/conversations/UE6_Domino_Deterministic_Universe/Dominium_UE6_Domino_Deterministic_Universe__01_human_readable_report.md` - Complete Chat Preservation Report Dominium Ue6, Domino, And Deterministic Universe Feasibility
- `docs/archive/conversations/UE6_Domino_Deterministic_Universe/Dominium_UE6_Domino_Deterministic_Universe__06_reader_brief.md` - Reader Brief Dominium Ue6, Domino, And Deterministic Universe Feasibility
- `docs/archive/conversations/UE6_Domino_Deterministic_Universe/Dominium_UE6_Domino_Deterministic_Universe__09_in_chat_reader.md` - In Chat Reader Dominium Ue6, Domino, And Deterministic Universe Feasibility
- `docs/archive/conversations/UE6_Domino_Deterministic_Universe/Dominium_UE6_Domino_Deterministic_Universe__10_accompanying_human_readable_detailed_summary_and_report.md` - Accompanying Human Readable Detailed Summary And Report Dominium Ue6, Domino, And Deterministic Universe Feasibility
- `docs/archive/conversations/Universe_Explorer_Planning/Dominium_Universe_Explorer_Planning_Handoff__01_human_readable_report.md` - Complete Chat Preservation Report Dominium Universe Explorer Planning And Repo Handoff
- `docs/archive/conversations/Universe_Explorer_Planning/Dominium_Universe_Explorer_Planning_Handoff__06_reader_brief.md` - Reader Brief Dominium Universe Explorer Planning And Repo Handoff
- `docs/archive/conversations/Universe_Explorer_Planning/Dominium_Universe_Explorer_Planning_Handoff__09_in_chat_reader.md` - In Chat Reader Dominium Universe Explorer Planning And Repo Handoff
- `docs/archive/conversations/Universe_Explorer_Planning/Dominium_Universe_Explorer_Planning_Handoff__10_accompanying_human_readable_detailed_summary.md` - Accompanying Human Readable Detailed Summary And Report
- `docs/archive/conversations/Workbench_AIDE_Product_Spine/Dominium_Architecture_Workbench_AIDE_Product_Spine_Planning__01_human_readable_report.md` - Complete Chat Preservation Report Dominium Architecture, Workbench, Aide, And Product Spine Planning
- `docs/archive/conversations/Workbench_AIDE_Product_Spine/Dominium_Architecture_Workbench_AIDE_Product_Spine_Planning__06_reader_brief.md` - Reader Brief Dominium Architecture, Workbench, Aide, And Product Spine Planning
- `docs/archive/conversations/Workbench_AIDE_Product_Spine/Dominium_Architecture_Workbench_AIDE_Product_Spine_Planning__09_in_chat_reader.md` - In Chat Reader Dominium Architecture, Workbench, Aide, And Product Spine Planning
- `docs/archive/conversations/Workbench_AIDE_Product_Spine/Dominium_Architecture_Workbench_AIDE_Product_Spine_Planning__10_accompanying_detailed_summary.md` - Accompanying Human Readable Detailed Summary And Report
- `docs/archive/conversations/World_Architecture/Dominium_World_Architecture__05_reader_brief.md` - Reader Brief Dominium World Architecture
- `docs/archive/conversations/_decision/DECISION_SUMMARY_v0.md` - Decision Summary V0
- `docs/archive/conversations/_promotion/PROMOTION_WAVE_1_CANDIDATES_v0.md` - Promotion Wave 1 Candidates V0
- `docs/archive/conversations/_reader/by_chat/advanced_simulation_infrastructure.md` - Dominium Advanced Simulation And Infrastructure Architecture Conversation Reader
- `docs/archive/conversations/_reader/by_chat/app_runtime_platform_renderers.md` - Dominium App0 Runtime, Platform, And Renderer Architecture Conversation Reader
- `docs/archive/conversations/_reader/by_chat/app_testx_codehygiene.md` - Dominium Architecture, Application Layer, Testx, And Codehygiene Planning Conversation Reader
- `docs/archive/conversations/_reader/by_chat/architecture_codex_prompts.md` - Dominium/domino Architecture And Codex Prompt Roadmap Conversation Reader
- `docs/archive/conversations/_reader/by_chat/architecture_ui_providers.md` - Dominium Architecture, Ui, Providers, And Robot Os Strategy Conversation Reader
- `docs/archive/conversations/_reader/by_chat/build_and_future_proofing.md` - Dominium Build And Future Proofing Architecture Conversation Reader
- `docs/archive/conversations/_reader/by_chat/canonical_structure_and_framework.md` - Dominium Canonical Architecture, Repository Foundation, And Provider Model Conversation Reader
- `docs/archive/conversations/_reader/by_chat/chronology_celestial_systems.md` - Dominium Chronology & Celestial Systems Conversation Reader
- `docs/archive/conversations/_reader/by_chat/development_routes.md` - Dominium Development Routes And Continuity Preservation Conversation Reader
- `docs/archive/conversations/_reader/by_chat/documentation_standards_readme.md` - Documentation Standards, Readme Strategy, And Handoff Packaging Conversation Reader
- `docs/archive/conversations/_reader/by_chat/dominium_architecture_i.md` - Dominium Architecture I Conversation Reader
- `docs/archive/conversations/_reader/by_chat/dominium_architecture_ii.md` - Dominium Architecture Ii Conversation Reader
- `docs/archive/conversations/_reader/by_chat/dominium_architecture_iii.md` - Dominium Architecture Iii: Launcher, Platform, Renderer, And Handoff Architecture Conversation Reader
- `docs/archive/conversations/_reader/by_chat/dominium_architecture_iv.md` - Dominium Architecture Iv Conversation Reader
- `docs/archive/conversations/_reader/by_chat/dominium_complete_conversation.md` - Dominium Canon, Repository Alignment, And Portability Doctrine Conversation Reader
- `docs/archive/conversations/_reader/by_chat/dominium_domino_codex_planning.md` - Dominium + Domino Codex Planning And Handoff Conversation Reader
- `docs/archive/conversations/_reader/by_chat/dominium_full_conversation.md` - Dominium Workbench, Aide, Presentation Architecture, Provider Strategy, Product Spine Planning, And Preservation Companion Conversation Reader
- `docs/archive/conversations/_reader/by_chat/dominium_setup.md` - Dominium Setup Architecture And Handoff Conversation Reader
- `docs/archive/conversations/_reader/by_chat/domino_dominium_workbench.md` - Domino Dominium Workbench Conversation Reader
- `docs/archive/conversations/_reader/by_chat/domino_engine_refactor_prompts.md` - Dominium/domino Engine Refactor Planning Conversation Reader
- `docs/archive/conversations/_reader/by_chat/engine_baseline_architecture.md` - Domino/dominium Engine Baseline, Architecture, And Feasibility Conversation Reader
- `docs/archive/conversations/_reader/by_chat/foundation_workbench_codex.md` - Dominium Foundation Lock, Workbench Spine, And Parallel Codex Handoff Conversation Reader
- `docs/archive/conversations/_reader/by_chat/framework_open_source_provider.md` - Domino Framework And Open Source Provider Architecture Conversation Reader
- `docs/archive/conversations/_reader/by_chat/gui_binary_content.md` - Dominium Content And GUI Rebuild Planning Conversation Reader
- `docs/archive/conversations/_reader/by_chat/language_platform_architecture.md` - Dominium Language, Platform, And Architecture Baseline Conversation Reader
- `docs/archive/conversations/_reader/by_chat/launcher_app_layer.md` - Dominium Launcher Application Layer Handoff Conversation Reader
- `docs/archive/conversations/_reader/by_chat/launcher_setup_architecture.md` - Dominium Launcher And Setup Architecture Conversation Reader
- `docs/archive/conversations/_reader/by_chat/modularity_aide_refactorability.md` - Dominium Modularity, AIDE Refactorability, And Future Proof Architecture Conversation Reader
- `docs/archive/conversations/_reader/by_chat/omega_xi_pi_architecture_future.md` - Dominium Omega/xi/pi Architecture & Future Proofing Planning Conversation Reader
- `docs/archive/conversations/_reader/by_chat/os_interface_repo_architecture.md` - Dominium Os Like Architecture, Repository Convergence, And Interface Operating Layer Conversation Reader
- `docs/archive/conversations/_reader/by_chat/platform_renderer_api_plan.md` - Dominium Codex Platform Renderer API Plan Conversation Reader
- `docs/archive/conversations/_reader/by_chat/platform_support.md` - Dominium Platform Support Planning Conversation Reader
- ... 69 more entries in `HUMAN_SOURCE_MANIFEST.yml`.

## Appendix B - Documents Summarized But Not Printed

Summarized documents: 3978.

- `docs/apps/ARTIFACT_IDENTITY.md` - Artifact Identity
- `docs/apps/CLIENT_IDE_START_POINTS.md` - Client Ide Start Points
- `docs/apps/CLIENT_READONLY_INTEGRATION.md` - Client Read Only Integration
- `docs/apps/CLIENT_RENDERER_UI.md` - Client Renderer UI
- `docs/apps/CLIENT_UI_LAYER.md` - Client UI Layer
- `docs/apps/CLI_CONTRACTS.md` - CLI Contracts
- `docs/apps/COMMAND_GRAPH_CAMERA_AND_BLUEPRINT.md` - Command Graph: Camera And Blueprint
- `docs/apps/COMPATIBILITY_ENFORCEMENT.md` - Compatibility Enforcement
- `docs/apps/ENGINE_GAME_DIAGNOSTICS.md` - Engine/game Diagnostics
- `docs/apps/GUI_MODE.md` - GUI Mode
- `docs/apps/HEADLESS_AND_ZERO_PACK.md` - Headless And Zero Pack Boot
- `docs/apps/IDE_WORKFLOW.md` - Ide Workflow
- `docs/apps/NATIVE_UI_POLICY.md` - Native UI Policy
- `docs/apps/OBSERVABILITY_PIPELINES.md` - Observability Pipelines
- `docs/apps/PRODUCT_BOUNDARIES.md` - Product Boundaries
- `docs/apps/README.md` - Application DOCS Index
- `docs/apps/READONLY_ADAPTER.md` - Read Only Adapter
- `docs/apps/RUNTIME_LOOP.md` - Runtime Loop Contract
- `docs/apps/TESTX_COMPLIANCE.md` - Testx Compliance (apr0)
- `docs/apps/TIMING_AND_CLOCKS.md` - Timing And Clock Domains
- `docs/apps/TOOLS_OBSERVABILITY.md` - Tools Observability
- `docs/apps/TOOLS_UI_POLICY.md` - Tools UI Policy
- `docs/apps/TUI_MODE.md` - TUI Mode
- `docs/apps/UI_MODES.md` - UI Modes
- `docs/apps/client/CLIENT_COMMAND_GRAPH.md` - Client Command Graph
- `docs/apps/client/CLIENT_FLOW.md` - Client Flow
- `docs/apps/client/CLIENT_LIFECYCLE_PIPELINE.md` - Client Lifecycle Pipeline
- `docs/apps/client/CLIENT_SETTINGS.md` - Client Settings
- `docs/apps/client/CLIENT_UI_AND_FLOW.md` - Client UI And Flow
- `docs/apps/client/CLI_TUI_GUI_PARITY.md` - CLI TUI GUI Parity
- `docs/apps/client/SERVER_DISCOVERY.md` - Server Discovery
- `docs/apps/client/SESSION_READY_AND_RUNNING.md` - Session Ready And Running
- `docs/apps/client/SESSION_SPEC_AND_AUTHORITY_CONTEXT.md` - Sessionspec And Authoritycontext
- `docs/apps/client/SESSION_TRANSITION_WORKSPACE.md` - Session Transition Workspace
- `docs/apps/client/WORLD_MANAGER.md` - World Manager
- `docs/apps/launcher/LAUNCHER_SETTINGS.md` - Launcher Settings
- `docs/apps/server/LOCAL_SINGLEPLAYER_MODEL.md` - Local Singleplayer Model
- `docs/apps/server/SERVER_MVP_BASELINE.md` - Server Mvp Baseline
- `docs/apps/server/SERVER_SETTINGS.md` - Server Settings
- `docs/apps/setup/SETUP_SETTINGS.md` - Setup Settings
- `docs/architecture/ADAPTER_PATTERN.md` - Adapter Pattern
- `docs/architecture/ADOPTION_PROTOCOL.md` - Adopt0 Adoption Protocol
- `docs/architecture/AI_AND_DELEGATED_AUTONOMY_MODEL.md` - Ai And Delegated Autonomy Model (aia0)
- `docs/architecture/AI_BUDGET_MODEL.md` - Ai Budget Model (ai0)
- `docs/architecture/AI_INTENT_MODEL.md` - Ai Intent Model (ai0)
- `docs/architecture/ANTI_CHEAT_AS_LAW.md` - Anti Cheat As Law (omni0)
- `docs/architecture/ANTI_ENTROPY_RULES.md` - Anti Entropy Rules (entropy0)
- `docs/architecture/APPLICATION_CONTRACTS.md` - Application Contracts (summary)
- `docs/architecture/APP_AUTOMATION_MODEL.md` - Application Automation Model (app Auto 0)
- `docs/architecture/APP_CANON0.md` - Application Layer Canon (app Canon0)
- `docs/architecture/APP_CANON1.md` - Application Layer Canon (app Canon1)
- `docs/architecture/ARCH0_CONSTITUTION.md` - Arch0 Constitution
- `docs/architecture/ARCHITECTURE.md` - Architecture (high Level)
- `docs/architecture/ARCHITECTURE_GRAPH_SPEC_v1.md` - Architecture Graph Spec V1
- `docs/architecture/ARCHITECTURE_LAYERS.md` - Architecture Layers
- `docs/architecture/ARCHIVAL_AND_PERMANENCE.md` - Archival And Permanence (exist2)
- `docs/architecture/ARCH_BUILD_ENFORCEMENT.md` - Arch Build Enforcement Build And Boundary Lockdown (enf2)
- `docs/architecture/ARCH_CHANGE_PROCESS.md` - Architectural Change Process (future0)
- `docs/architecture/ARCH_ENFORCEMENT.md` - Architecture Enforcement Law (enf0)
- `docs/architecture/ARCH_REPO_LAYOUT.md` - Arch Repo Layout Canonical Repository Layout And Ownership
- `docs/architecture/ARCH_SPEC_OWNERSHIP.md` - Arch Spec Ownership Spec Responsibility Model
- `docs/architecture/ARTIFACT_LIFECYCLE.md` - Artifact Lifecycle
- `docs/architecture/ARTIFACT_MODEL.md` - Artifact Model (lib 4)
- `docs/architecture/AUDITABILITY_AND_DISCLOSURE.md` - Auditability And Disclosure (testx2)
- `docs/architecture/AUTHORITY_AND_ENTITLEMENTS.md` - Authority And Entitlements (testx3)
- `docs/architecture/AUTHORITY_AND_OMNIPOTENCE.md` - Authority And Omnipotence (omni0)
- `docs/architecture/AUTHORITY_IN_REALITY.md` - Authority In Reality (reality0)
- `docs/architecture/AUTHORITY_MODEL.md` - Authority Model (canon0)
- `docs/architecture/BEHAVIORAL_COMPONENTS_STANDARD.md` - Behavioral Components Standard
- `docs/architecture/BOUNDARY_ENFORCEMENT.md` - Boundary Enforcement
- `docs/architecture/BUDGET_POLICY.md` - Budget Policy V1
- `docs/architecture/BUGREPORT_MODEL.md` - Bugreport Bundle Model (bug 0)
- `docs/architecture/BUILD_IDENTITY_MODEL.md` - Build Identity Model (build ID 0)
- `docs/architecture/CANON_CUT_LINE.md` - Canon Cut Line (cons 0)
- `docs/architecture/CANON_INDEX.md` - Canon Index (clean 2)
- `docs/architecture/CAPABILITY_BASELINES.md` - Capability Baselines (capbase0)
- `docs/architecture/CAPABILITY_ONLY_CANON.md` - Capability Only Canon
- `docs/architecture/CHANGELOG_ARCH.md` - Architecture Changelog (clean1)
- `docs/architecture/CHANGE_PROTOCOL.md` - Change Protocol (arch0 Binding)
- `docs/architecture/CHEATS_ARE_JUST_LAWS.md` - Cheats Are Just Laws (omni1)
- `docs/architecture/CHECKPOINTING_MODEL.md` - Checkpointing Model (mmo 2)
- `docs/architecture/CHECKPOINTS.md` - Acceptance Checkpoints (chk0)
- `docs/architecture/CIVILIZATION_MODEL.md` - Civilization Model (civ0+)
- `docs/architecture/CODE_DATA_BOUNDARY.md` - Code/data Boundary (codehygiene X)
- `docs/architecture/CODE_KNOWLEDGE_BOUNDARY.md` - Code Knowledge Boundary (codeknow0)
- `docs/architecture/COLLAPSE_AND_DECAY.md` - Collapse And Decay (civ0+)
- `docs/architecture/COLLAPSE_EXPAND_CONTRACT.md` - Collapse/expand Contract (scale0)
- `docs/architecture/COLLAPSE_EXPAND_SOLVERS.md` - Collapse Expand Solvers
- `docs/architecture/COMPATIBILITY_MODEL.md` - Compatibility Model (ops1)
- `docs/architecture/COMPLEXITY_AND_SCALE.md` - Complexity And Scale
- `docs/architecture/COMPONENTS.md` - Components
- `docs/architecture/CONFLICT_AND_WAR_MODEL.md` - Conflict And War Model (war0)
- `docs/architecture/CONSTANT_COST_GUARANTEE.md` - Constant Cost Guarantee (scale3)
- `docs/architecture/CONTENT_AND_STORAGE_MODEL.md` - Content And Storage Model (stor0 / Lib 0)
- `docs/architecture/CONTROL_LAYERS.md` - Control Layers (testx2)
- `docs/architecture/CORE_ABSTRACTIONS.md` - Core Abstractions
- `docs/architecture/CRASH_RECOVERY.md` - Crash Recovery (mmo 2)
- `docs/architecture/CROSS_SHARD_LOG.md` - Cross Shard Log (mmo0)
- `docs/architecture/C_COMPATIBLE_ABI_BOUNDARY.md` - C Compatible Abi Boundary
- `docs/architecture/DEATH_AND_CONTINUITY.md` - Death And Continuity (life0+)
- `docs/architecture/DECAY_EROSION_REGEN.md` - Decay, Erosion, Regeneration (terrain0)
- `docs/architecture/DEMO_AND_TOURIST_MODEL.md` - Demo And Tourist Model (testx3)
- `docs/architecture/DEPRECATION_AND_QUARANTINE.md` - Deprecation And Quarantine
- `docs/architecture/DEPRECATION_LIFECYCLE.md` - Deprecation Lifecycle
- `docs/architecture/DETERMINISTIC_ORDERING_POLICY.md` - Deterministic Ordering Policy (order0)
- `docs/architecture/DETERMINISTIC_REDUCTION_RULES.md` - Deterministic Reduction Rules (exec0b)
- `docs/architecture/DEV_OPS_MODEL.md` - Dev/ops Model (dev Ops 0)
- `docs/architecture/DIRECTORY_CONTEXT.md` - Dominium Directory Context (authoritative)
- `docs/architecture/DIRECTORY_STRUCTURE.md` - Directory Structure (fs0)
- `docs/architecture/DISTRIBUTED_SIMULATION_MODEL.md` - Distributed Simulation Model (mmo Srz)
- `docs/architecture/DISTRIBUTED_TIME_MODEL.md` - Distributed Time Model (mmo0)
- `docs/architecture/DISTRIBUTION_AND_STOREFRONTS.md` - Distribution And Storefronts (testx3)
- `docs/architecture/DISTRIBUTION_LAYOUT.md` - Distribution Layout (dist0)
- `docs/architecture/DISTRIBUTION_PROFILES.md` - Distribution Profiles (testx2)
- `docs/architecture/DOMAIN_JURISDICTIONS_AND_LAW.md` - Domain Jurisdictions And Law (domain2)
- `docs/architecture/DOMAIN_SHARDING_AND_STREAMING.md` - Domain Sharding And Streaming (domain3)
- `docs/architecture/DOMAIN_VOLUMES.md` - Domain Volumes (domain0)
- `docs/architecture/DUPLICATION_DETECTION_RULES.md` - Duplication Detection Rules
- `docs/architecture/ECONOMIC_MODEL.md` - Economic Model (econ0)
- `docs/architecture/ECONOMY_AND_LOGISTICS.md` - Economy And Logistics (civ0+)
- ... 3858 more entries in `HUMAN_SOURCE_MANIFEST.yml`.

## Appendix C - Machine-Readable And Reference Material Excluded From The Main Book

Machine/index-only documents: 268. Reference-only documents: 620. These files remain represented in the source manifest and reference outputs.

- `docs/.gitignore` - Generated Draft Changelog (see Scripts\gen Changelog.bat).
- `docs/architecture/FROZEN_CONTRACT_HASHES.json` - Frozen Contract Hashes
- `docs/architecture/LOCKLIST_OVERRIDES.json` - Locklist Overrides
- `docs/architecture/SEMANTIC_STABILITY_LOCK.json` - Semantic Stability Lock
- `docs/archive/audit/CONSISTENCY_MATRIX.json` - Consistency Matrix
- `docs/archive/audit/DOMAIN_REGISTRY_REPORT.json` - Domain Registry Report
- `docs/archive/audit/GR3_FAST_COMPACTION_SANITY.json` - Gr3 FAST Compaction Sanity
- `docs/archive/audit/GR3_FAST_COMPACTION_STATE.json` - Gr3 FAST Compaction State
- `docs/archive/audit/GR3_FAST_REFERENCE_SUITE.json` - Gr3 FAST Reference Suite
- `docs/archive/audit/GR3_FULL_CHEM_SCENARIO.json` - Gr3 Full Chem Scenario
- `docs/archive/audit/GR3_FULL_CHEM_STRESS.json` - Gr3 Full Chem Stress
- `docs/archive/audit/GR3_FULL_ELEC_SCENARIO.json` - Gr3 Full Elec Scenario
- `docs/archive/audit/GR3_FULL_ELEC_STRESS.json` - Gr3 Full Elec Stress
- `docs/archive/audit/GR3_FULL_FLUID_SCENARIO.json` - Gr3 Full Fluid Scenario
- `docs/archive/audit/GR3_FULL_FLUID_STRESS.json` - Gr3 Full Fluid Stress
- `docs/archive/audit/GR3_FULL_POLL_SCENARIO.json` - Gr3 Full Poll Scenario
- `docs/archive/audit/GR3_FULL_POLL_STRESS.json` - Gr3 Full Poll Stress
- `docs/archive/audit/GR3_FULL_PROC_COMPACTION_VERIFY.json` - Gr3 Full Proc Compaction Verify
- `docs/archive/audit/GR3_FULL_PROC_REPLAY.json` - Gr3 Full Proc Replay
- `docs/archive/audit/GR3_FULL_PROC_SCENARIO.json` - Gr3 Full Proc Scenario
- `docs/archive/audit/GR3_FULL_PROC_STATE.json` - Gr3 Full Proc State
- `docs/archive/audit/GR3_FULL_PROC_STATE_COMPACTED.json` - Gr3 Full Proc State Compacted
- `docs/archive/audit/GR3_FULL_PROC_STRESS.json` - Gr3 Full Proc Stress
- `docs/archive/audit/GR3_FULL_PROV_STRESS.json` - Gr3 Full Prov Stress
- `docs/archive/audit/GR3_FULL_REFERENCE_SUITE.json` - Gr3 Full Reference Suite
- `docs/archive/audit/GR3_FULL_SIG_SCENARIO.json` - Gr3 Full Sig Scenario
- `docs/archive/audit/GR3_FULL_SIG_SCENARIO_RUN.json` - Gr3 Full Sig Scenario Run
- `docs/archive/audit/GR3_FULL_SIG_STRESS.json` - Gr3 Full Sig Stress
- `docs/archive/audit/GR3_FULL_SYS_CROSS_SHARD_STRESS_MANIFEST.json` - Gr3 Full Sys Cross Shard Stress Manifest
- `docs/archive/audit/GR3_FULL_SYS_REPLAY.json` - Gr3 Full Sys Replay
- `docs/archive/audit/GR3_FULL_SYS_SCENARIO.json` - Gr3 Full Sys Scenario
- `docs/archive/audit/GR3_FULL_SYS_SCENARIO_RUN.json` - Gr3 Full Sys Scenario Run
- `docs/archive/audit/GR3_FULL_SYS_STRESS_MANIFEST.json` - Gr3 Full Sys Stress Manifest
- `docs/archive/audit/GR3_FULL_THERM_SCENARIO.json` - Gr3 Full Therm Scenario
- `docs/archive/audit/GR3_FULL_THERM_STRESS.json` - Gr3 Full Therm Stress
- `docs/archive/audit/HANDSHAKE_COMPAT_MATRIX.json` - Handshake Compat Matrix
- `docs/archive/audit/INVENTORY.json` - Inventory
- `docs/archive/audit/INVENTORY_MACHINE.json` - Inventory Machine
- `docs/archive/audit/LOGIC10_REFERENCE_RESULTS.json` - Logic10 Reference Results
- `docs/archive/audit/LOGIC10_STRESS_RESULTS.json` - Logic10 Stress Results
- `docs/archive/audit/LOGIC5_TIMING_STRESS.json` - Logic5 Timing Stress
- `docs/archive/audit/LOGIC6_COMPILE_STRESS.json` - Logic6 Compile Stress
- `docs/archive/audit/LOGIC7_DEBUG_STRESS.json` - Logic7 Debug Stress
- `docs/archive/audit/LOGIC8_FAULT_STRESS.json` - Logic8 Fault Stress
- `docs/archive/audit/LOGIC9_PROTOCOL_STRESS.json` - Logic9 Protocol Stress
- `docs/archive/audit/REPO_STRUCTURE_AUDIT.json` - Repo Structure Audit
- `docs/archive/audit/SEMANTIC_IMPACT_GLOBAL.json` - Semantic Impact Global
- `docs/archive/audit/STUB_REPORT.json` - Stub Report
- `docs/archive/audit/TOPOLOGY_MAP.json` - Topology Map
- `docs/archive/audit/auditx/FINDINGS.json` - Findings
- `docs/archive/audit/auditx/INVARIANT_MAP.json` - Invariant Map
- `docs/archive/audit/auditx/PROMOTION_CANDIDATES.json` - Promotion Candidates
- `docs/archive/audit/auditx/RUN_META.json` - Run Meta
- `docs/archive/audit/auditx/TRENDS.json` - Trends
- `docs/archive/audit/compat/COMPAT_BASELINE.json` - Compat Baseline
- `docs/archive/audit/compute_budget_stress_results.json` - Compute Budget Stress Results
- `docs/archive/audit/identity_fingerprint.json` - Identity Fingerprint
- `docs/archive/audit/perf/multiplayer_profile_trace.json` - Multiplayer Profile Trace
- `docs/archive/audit/performance/PERFORMX_BASELINE.json` - Performx Baseline
- `docs/archive/audit/performance/PERFORMX_REGRESSIONS.json` - Performx Regressions
- `docs/archive/audit/performance/PERFORMX_RESULTS.json` - Performx Results
- `docs/archive/audit/performance/RUN_META.json` - Run Meta
- `docs/archive/audit/proof_manifest.json` - Proof Manifest
- `docs/archive/audit/remediation/anb-omega-empty-path/20260211T215035Z_precheck_ok/actions_taken.json` - Actions Taken
- `docs/archive/audit/remediation/anb-omega-empty-path/20260211T215035Z_precheck_ok/failure.json` - Failure
- `docs/archive/audit/remediation/anb-omega-empty-path/20260211T215035Z_precheck_ok/prevention_links.json` - Prevention Links
- `docs/archive/audit/remediation/anb-omega-empty-path/20260211T215035Z_precheck_ok/verification.json` - Verification
- `docs/archive/audit/remediation/anb-omega-empty-path/20260211T220047Z_precheck_OTHER/actions_taken.json` - Actions Taken
- `docs/archive/audit/remediation/anb-omega-empty-path/20260211T220047Z_precheck_OTHER/failure.json` - Failure
- `docs/archive/audit/remediation/anb-omega-empty-path/20260211T220047Z_precheck_OTHER/prevention_links.json` - Prevention Links
- `docs/archive/audit/remediation/anb-omega-empty-path/20260211T220047Z_precheck_OTHER/verification.json` - Verification
- `docs/archive/audit/remediation/vs2026/20260211T080631Z_verify_DERIVED_ARTIFACT_STALE/actions_taken.json` - Actions Taken
- `docs/archive/audit/remediation/vs2026/20260211T080631Z_verify_DERIVED_ARTIFACT_STALE/failure.json` - Failure
- `docs/archive/audit/remediation/vs2026/20260211T080631Z_verify_DERIVED_ARTIFACT_STALE/prevention_links.json` - Prevention Links
- `docs/archive/audit/remediation/vs2026/20260211T080631Z_verify_DERIVED_ARTIFACT_STALE/verification.json` - Verification
- `docs/archive/audit/remediation/vs2026/20260211T080838Z_verify_OTHER/actions_taken.json` - Actions Taken
- `docs/archive/audit/remediation/vs2026/20260211T080838Z_verify_OTHER/failure.json` - Failure
- `docs/archive/audit/remediation/vs2026/20260211T080838Z_verify_OTHER/prevention_links.json` - Prevention Links
- `docs/archive/audit/remediation/vs2026/20260211T080838Z_verify_OTHER/verification.json` - Verification
- `docs/archive/audit/remediation/vs2026/20260211T081813Z_verify_ok/actions_taken.json` - Actions Taken
- `docs/archive/audit/remediation/vs2026/20260211T081813Z_verify_ok/failure.json` - Failure
- `docs/archive/audit/remediation/vs2026/20260211T081813Z_verify_ok/prevention_links.json` - Prevention Links
- `docs/archive/audit/remediation/vs2026/20260211T081813Z_verify_ok/verification.json` - Verification
- `docs/archive/audit/remediation/vs2026/20260211T083343Z_verify_DERIVED_ARTIFACT_STALE/actions_taken.json` - Actions Taken
- `docs/archive/audit/remediation/vs2026/20260211T083343Z_verify_DERIVED_ARTIFACT_STALE/failure.json` - Failure
- `docs/archive/audit/remediation/vs2026/20260211T083343Z_verify_DERIVED_ARTIFACT_STALE/prevention_links.json` - Prevention Links
- `docs/archive/audit/remediation/vs2026/20260211T083343Z_verify_DERIVED_ARTIFACT_STALE/verification.json` - Verification
- `docs/archive/audit/remediation/vs2026/20260211T090841Z_verify_OTHER/actions_taken.json` - Actions Taken
- `docs/archive/audit/remediation/vs2026/20260211T090841Z_verify_OTHER/failure.json` - Failure
- `docs/archive/audit/remediation/vs2026/20260211T090841Z_verify_OTHER/prevention_links.json` - Prevention Links
- `docs/archive/audit/remediation/vs2026/20260211T090841Z_verify_OTHER/verification.json` - Verification
- `docs/archive/audit/remediation/vs2026/20260211T111036Z_verify_OTHER/actions_taken.json` - Actions Taken
- `docs/archive/audit/remediation/vs2026/20260211T111036Z_verify_OTHER/failure.json` - Failure
- `docs/archive/audit/remediation/vs2026/20260211T111036Z_verify_OTHER/prevention_links.json` - Prevention Links
- `docs/archive/audit/remediation/vs2026/20260211T111036Z_verify_OTHER/verification.json` - Verification
- `docs/archive/audit/remediation/vs2026/20260211T121513Z_verify_ok/actions_taken.json` - Actions Taken
- `docs/archive/audit/remediation/vs2026/20260211T121513Z_verify_ok/failure.json` - Failure
- `docs/archive/audit/remediation/vs2026/20260211T121513Z_verify_ok/prevention_links.json` - Prevention Links
- `docs/archive/audit/remediation/vs2026/20260211T121513Z_verify_ok/verification.json` - Verification
- `docs/archive/audit/remediation/vs2026/20260211T130308Z_verify_ok/actions_taken.json` - Actions Taken
- `docs/archive/audit/remediation/vs2026/20260211T130308Z_verify_ok/failure.json` - Failure
- `docs/archive/audit/remediation/vs2026/20260211T130308Z_verify_ok/prevention_links.json` - Prevention Links
- `docs/archive/audit/remediation/vs2026/20260211T130308Z_verify_ok/verification.json` - Verification
- `docs/archive/audit/remediation/vs2026/20260211T163146Z_verify_OTHER/actions_taken.json` - Actions Taken
- `docs/archive/audit/remediation/vs2026/20260211T163146Z_verify_OTHER/failure.json` - Failure
- `docs/archive/audit/remediation/vs2026/20260211T163146Z_verify_OTHER/prevention_links.json` - Prevention Links
- `docs/archive/audit/remediation/vs2026/20260211T163146Z_verify_OTHER/verification.json` - Verification
- `docs/archive/audit/remediation/vs2026/20260211T233128Z_verify_ok/actions_taken.json` - Actions Taken
- `docs/archive/audit/remediation/vs2026/20260211T233128Z_verify_ok/failure.json` - Failure
- `docs/archive/audit/remediation/vs2026/20260211T233128Z_verify_ok/prevention_links.json` - Prevention Links
- `docs/archive/audit/remediation/vs2026/20260211T233128Z_verify_ok/verification.json` - Verification
- `docs/archive/audit/remediation/vs2026/20260212T143108Z_verify_ok/actions_taken.json` - Actions Taken
- `docs/archive/audit/remediation/vs2026/20260212T143108Z_verify_ok/failure.json` - Failure
- `docs/archive/audit/remediation/vs2026/20260212T143108Z_verify_ok/prevention_links.json` - Prevention Links
- `docs/archive/audit/remediation/vs2026/20260212T143108Z_verify_ok/verification.json` - Verification
- `docs/archive/audit/remediation/vs2026/20260213T052649Z_precheck_DERIVED_ARTIFACT_STALE/actions_taken.json` - Actions Taken
- `docs/archive/audit/remediation/vs2026/20260213T052649Z_precheck_DERIVED_ARTIFACT_STALE/failure.json` - Failure
- `docs/archive/audit/remediation/vs2026/20260213T052649Z_precheck_DERIVED_ARTIFACT_STALE/prevention_links.json` - Prevention Links
- `docs/archive/audit/remediation/vs2026/20260213T052649Z_precheck_DERIVED_ARTIFACT_STALE/verification.json` - Verification
- `docs/archive/audit/remediation/vs2026/20260213T054938Z_exitcheck_OTHER/actions_taken.json` - Actions Taken
- ... 768 more entries in `HUMAN_SOURCE_MANIFEST.yml`.

## Appendix D - Decision Index

- Architecture and boundaries.
- Workbench, AIDE, Codex, and tooling.
- Renderer, UI, platform, and native GUI.
- Provider, content, packs, and compatibility.
- World, time, civilization, and simulation domains.
- Release, setup, launcher, and publication.
- Documentation, canon, spec structure, and archive promotion.

See `docs/archive/docs_corpus/_reconciliation/DOCS_DECISION_DOCKET_v0.md` and `docs/archive/conversations/_decision/DECISION_DOCKET_v0.md`.

## Appendix E - Source Path Index

The full source path index is `docs/archive/docs_corpus/_human_source/HUMAN_SOURCE_INDEX.md`. This appendix intentionally avoids reproducing thousands of paths in the main book.

## Appendix F - Glossary And Abbreviations

- **AIDE:** repo/control-plane harness and context/validation helper.
- **Archive:** historical/provenance docs that do not override current authority.
- **Canon:** binding constitutional project meaning.
- **Conversation advisory:** derived historical conversation evidence.
- **Domino:** deterministic reusable substrate.
- **Dominium:** official game/product/domain layer.
- **Process-only mutation:** authoritative truth changes only through lawful deterministic processes.
- **Queue:** current scope gate for allowed work.
