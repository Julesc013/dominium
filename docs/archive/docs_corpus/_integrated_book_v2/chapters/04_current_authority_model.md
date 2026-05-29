## 4. Current Authority Model

Authority is layered: canon and glossary outrank AGENTS, which outranks lower planning, generated outputs, archive material, and conversation evidence.

**Why this chapter matters.** Authority order and snapshot intake protocol define how conflicts must be resolved without convenience-based promotion. The docs and conversation corpora are useful because they make history reviewable while preserving the authority boundary.

> [!CURRENT_TRUTH] Current repo truth comes first in this chapter. Archive and conversation evidence is used to explain design intent, recurring concerns, and review candidates without promoting it.

### Integrated Evidence

The current repo-backed evidence emphasizes: Keep target-specific project state in '.aide/memory/'; do not copy source AIDE memory, queue history, generated context, reports, route decisions, cache-key reports, Gateway/provider status reports, '.aide.local/', raw prompts, raw responses, or secrets (EVC-00012). Travel scheduling, replay, and law decisions become nondeterministic (EVC-00065). Rendering is presentational only and MUST NOT mutate truth or enforce authority decisions (EVC-01433). Foundation Lock is the repository decision gate that determines whether Dominium can leave the Foundation Lock queue and begin a first narrow governed product slice (EVC-01457).
The archive and conversation corpus add: 'DECISION-0006': Should this conversation-derived claim become a future review item, remain historical, or be deferred: The assistant formalized this as the Perfect Earth Calendar, later called HPC-E. The final structure is clear, though the exact leap (EVC-00691). 'DECISION-0007': What disposition should be chosen for this unresolved claim: Before relying on this chat as project authority, a future assistant or human reviewer must confirm whether Dominium is actually intended to be simulation-heavy, whether strict...? (EVC-00692). Not safe now: implementation work in blocked scopes, canon/schema/contract rewrites from archive claims, release publication, renderer implementation, gameplay, provider/package runtime, broad Workbench UI, native GUI (EVC-01069). Any claim touching canon, glossary, authority order, contracts, schema law, current queue, release, implementation, or blocked scope (EVC-01070).
The downstream implication is that: Future Series: DOC-CONVERGENCE Replacement Target: canon-aligned documentation set for convergence and release preparation (EVC-00041). Future Series: DOC-CONVERGENCE Replacement Target: canon-aligned documentation set for convergence and release preparation (EVC-00055). Future Series: DOC-CONVERGENCE Replacement Target: canon-aligned documentation set for convergence and release preparation (EVC-00062). Future Series: DOC-CONVERGENCE Replacement Target: canon-aligned documentation set for convergence and release preparation (EVC-00090).

### Decisions Already Visible

- **Decision:** Keep target-specific project state in '.aide/memory/'; do not copy source AIDE memory, queue history, generated context, reports, route decisions, cache-key reports, Gateway/provider status reports, '.aide.local/', raw prompts, raw responses, or secrets. _Evidence:_ `EVC-00012` from `AGENTS.md`. _Status:_ current repo source.
- **Decision:** Travel scheduling, replay, and law decisions become nondeterministic. _Evidence:_ `EVC-00065` from `docs/architecture/INVARIANTS.md`. _Status:_ current repo source.
- **Decision:** Rendering is presentational only and MUST NOT mutate truth or enforce authority decisions. _Evidence:_ `EVC-01433` from `docs/canon/constitution_v1.md`. _Status:_ current repo source.
- **Decision:** Foundation Lock is the repository decision gate that determines whether Dominium can leave the Foundation Lock queue and begin a first narrow governed product slice. _Evidence:_ `EVC-01457` from `docs/repo/FOUNDATION_LOCK.md`. _Status:_ current repo source.
- **Decision:** 'DECISION-0006': Should this conversation-derived claim become a future review item, remain historical, or be deferred: The assistant formalized this as the Perfect Earth Calendar, later called HPC-E. The final structure is clear, though the exact leap... _Evidence:_ `EVC-00691` from `docs/archive/conversations/_decision/DECISION_SUMMARY_v0.md`. _Status:_ conversation advisory evidence.
- **Decision:** 'DECISION-0007': What disposition should be chosen for this unresolved claim: Before relying on this chat as project authority, a future assistant or human reviewer must confirm whether Dominium is actually intended to be simulation-heavy, whether strict...? _Evidence:_ `EVC-00692` from `docs/archive/conversations/_decision/DECISION_SUMMARY_v0.md`. _Status:_ conversation advisory evidence.
- **Decision:** '04_registers': workstreams, decisions, tasks, risks, verification queue. _Evidence:_ `EVC-00198` from `docs/archive/conversations/Dominium_Complete_Conversation/Accompanying_Report/Dominium_Canon_Portability_Audit__09_in_chat_reader.md`. _Status:_ conversation advisory evidence.
- **Decision:** Finally, the user pasted a newer repo-status summary saying the structure was now clean enough to stop broad structure refactors: canonical structure passed with warnings, fast strict and smoke proof passed, full CTest remained blocked by stale full-gate... _Evidence:_ `EVC-00620` from `docs/archive/conversations/Universe_Explorer_Planning/Dominium_Universe_Explorer_Planning_Handoff__01_human_readable_report.md`. _Status:_ conversation advisory evidence; future queue review.

### Specifications and Requirements

- **Specification:** Run 'AIDE-WORKFLOW-LAW-01' next if the queue remains reconciled after _Evidence:_ `EVC-01464` from `docs/repo/FOUNDATION_LOCK.md`. _Status:_ current repo source.
- **Specification:** Future Series: Sigma-1, Sigma-2, Sigma-3, Sigma-4, Sigma-5, Phi, Upsilon, Zeta Replacement Target: none; later mirrors and machine-readable governance surfaces must derive from this file rather than compete with it Binding Sources... _Evidence:_ `EVC-00001` from `AGENTS.md`. _Status:_ current repo source.
- **Specification:** 1. 'docs/canon/constitution_v1.md' 2. 'docs/canon/glossary_v1.md' 3. 'AGENTS.md' 4. scope-specific canonical planning, semantic, schema, contract, release, and policy artifacts named by the active task 5. operational registries, projections, mirrors... _Evidence:_ `EVC-00003` from `AGENTS.md`. _Status:_ current repo source.
- **Specification:** create or resume a bounded AIDE task before reporting blocked; ask the user only for semantic authority conflicts, destructive ambiguity, missing external secrets, or required review gates. _Evidence:_ `EVC-00014` from `AGENTS.md`. _Status:_ current repo source; future queue review.
- **Specification:** Required updates: documentation surface exists, but current canon ownership is not explicit _Evidence:_ `EVC-00031` from `docs/README.md`. _Status:_ current repo source.
- **Specification:** Archived documents are kept for provenance only. Canonical contracts are in 'docs/architecture/'. _Evidence:_ `EVC-00040` from `docs/README.md`. _Status:_ current repo source.
- **Specification:** Dependency direction is authoritative and must not be inverted. _Evidence:_ `EVC-00044` from `docs/architecture/CANONICAL_SYSTEM_MAP.md`. _Status:_ current repo source.
- **Specification:** Law admission gates sit before scheduling, before execution, and before commit. _Evidence:_ `EVC-00048` from `docs/architecture/CANONICAL_SYSTEM_MAP.md`. _Status:_ current repo source.

### Constraints, Prohibitions, and Prerequisites

- **Constraint:** Future Series: DOC-CONVERGENCE Replacement Target: patched document aligned to current canon ownership and release scope _Evidence:_ `EVC-00029` from `docs/README.md`. _Status:_ current repo source.
- **Constraint:** Scope: single-source dependency map and forbidden edges for Dominium/Domino. _Evidence:_ `EVC-00042` from `docs/architecture/CANONICAL_SYSTEM_MAP.md`. _Status:_ current repo source.
- **Constraint:** Scope: canonical statement of identity and intent. _Evidence:_ `EVC-00077` from `docs/architecture/WHAT_THIS_IS.md`. _Status:_ current repo source.
- **Constraint:** An Assembly capable of submitting Intents under AuthorityContext and LawProfile constraints. _Evidence:_ `EVC-01449` from `docs/canon/glossary_v1.md`. _Status:_ current repo source.
- **Constraint:** Foundation Lock does not mean full CTest is green, every compatibility corpus exists, every provider is implemented, every runtime trust rule is enforced, Workbench UI exists, or broad feature work is open. _Evidence:_ `EVC-01460` from `docs/repo/FOUNDATION_LOCK.md`. _Status:_ current repo source; future queue review.
- **Constraint:** Continue narrow governed product-spine slices recorded by '.aide/queue/current.toml'. _Evidence:_ `EVC-01463` from `docs/repo/FOUNDATION_LOCK.md`. _Status:_ current repo source.
- **Constraint:** Keep Queue B hardening planned but not a substitute for the blocker repair. _Evidence:_ `EVC-01467` from `docs/repo/FOUNDATION_LOCK.md`. _Status:_ current repo source.
- **Prohibition:** Responsibilities and forbidden dependencies (quick map) _Evidence:_ `EVC-00046` from `docs/architecture/CANONICAL_SYSTEM_MAP.md`. _Status:_ current repo source.
- **Prohibition:** Executables do not embed content; packs are external and optional. _Evidence:_ `EVC-00094` from `docs/architecture/WHAT_THIS_IS_NOT.md`. _Status:_ current repo source.
- **Prohibition:** Global iteration and implicit background simulation are forbidden. _Evidence:_ `EVC-00100` from `docs/architecture/WHAT_THIS_IS_NOT.md`. _Status:_ current repo source.

### Contradictions, Risks, and Open Ends

- **Contradiction:** if repo artifacts conflict materially, resolve the conflict with 'docs/planning/AUTHORITY_ORDER.md' and 'docs/planning/SNAPSHOT_INTAKE_PROTOCOL.md' rather than by convenience _Evidence:_ `EVC-00004` from `AGENTS.md`. _Status:_ current repo source.
- **Contradiction:** Inconsistent clients, shard drift, and audit failure. _Evidence:_ `EVC-00074` from `docs/architecture/INVARIANTS.md`. _Status:_ current repo source.
- **Contradiction:** Constitutional conflicts are resolved by this document, not by prompt convenience. _Evidence:_ `EVC-01441` from `docs/canon/constitution_v1.md`. _Status:_ current repo source.
- **Contradiction:** This is the full canonical glossary v1.0.0. If terminology conflicts with local or legacy docs, this glossary wins. _Evidence:_ `EVC-01444` from `docs/canon/glossary_v1.md`. _Status:_ current repo source.
- **Unresolved Question:** Refusal and defer semantics are part of determinism and replay guarantees. _Evidence:_ `EVC-00073` from `docs/architecture/INVARIANTS.md`. _Status:_ current repo source.
- **Unresolved Question:** Speculative future feature not yet implemented. _Evidence:_ `EVC-01456` from `docs/canon/glossary_v1.md`. _Status:_ current repo source.
- **Risk:** Continue documentation and evidence updates that keep remaining warnings and full-gate debt visible. _Evidence:_ `EVC-01466` from `docs/repo/FOUNDATION_LOCK.md`. _Status:_ current repo source.
- **Change Of Direction:** 'archive/': historical, superseded, quarantined, or provenance-retained _Evidence:_ `EVC-00021` from `README.md`. _Status:_ current repo source.
- **Change Of Direction:** 'docs/archive/' historical and superseded docs only _Evidence:_ `EVC-00039` from `docs/README.md`. _Status:_ current repo source.
- **Unresolved Question:** Should this conversation-derived claim become a future review item, remain historical, or be deferred: The assistant formalized this as the Perfect Earth Calendar, later called HPC-E. The final structure is clear, though the exact leap rule remains... _Evidence:_ `EVC-00684` from `docs/archive/conversations/_decision/DECISION_SUMMARY_v0.md`. _Status:_ conversation advisory evidence.

### Second- and Third-Order Effects

- **Third Order Effect:** Future Series: DOC-CONVERGENCE Replacement Target: canon-aligned documentation set for convergence and release preparation _Evidence:_ `EVC-00041` from `docs/architecture/CANONICAL_SYSTEM_MAP.md`. _Status:_ current repo source.
- **Third Order Effect:** Future Series: DOC-CONVERGENCE Replacement Target: canon-aligned documentation set for convergence and release preparation _Evidence:_ `EVC-00055` from `docs/architecture/CONTRACTS_INDEX.md`. _Status:_ current repo source.
- **Third Order Effect:** Future Series: DOC-CONVERGENCE Replacement Target: canon-aligned documentation set for convergence and release preparation _Evidence:_ `EVC-00062` from `docs/architecture/INVARIANTS.md`. _Status:_ current repo source.
- **Third Order Effect:** Future Series: DOC-CONVERGENCE Replacement Target: canon-aligned documentation set for convergence and release preparation _Evidence:_ `EVC-00090` from `docs/architecture/WHAT_THIS_IS_NOT.md`. _Status:_ current repo source.
- **Third Order Effect:** 'docs/release/roadmap/' goals and coverage tests only _Evidence:_ `EVC-00037` from `docs/README.md`. _Status:_ current repo source.
- **Design Goal:** Tools are read-only by default and mutate state only via ToolIntents. _Evidence:_ `EVC-00045` from `docs/architecture/CANONICAL_SYSTEM_MAP.md`. _Status:_ current repo source.
- **Design Goal:** SP and MP produce different outcomes for the same intent streams. _Evidence:_ `EVC-00075` from `docs/architecture/INVARIANTS.md`. _Status:_ current repo source.
- **Design Goal:** Use this prompt block for future work so tasks remain short and stable: _Evidence:_ `EVC-01442` from `docs/canon/constitution_v1.md`. _Status:_ current repo source.
- **Design Goal:** Architecturally designed to allow extension without refactor. _Evidence:_ `EVC-01455` from `docs/canon/glossary_v1.md`. _Status:_ current repo source.
- **Design Goal:** 1. Manually review the decision docket and choose defer/preserve/promote-later dispositions. 2. Select a small subset of Wave 1 candidates for docs-only microtasks. 3. For each microtask, name the source claim ID, exact target doc, authority support... _Evidence:_ `EVC-01073` from `docs/archive/conversations/_synthesis/CURRENT_PROJECT_ATLAS_v0.md`. _Status:_ conversation advisory evidence; future queue review.

### Implications for Next Work

Near-term work should use the book as a map, then promote only through explicit scoped tasks.

Any later task that wants to move a claim from this chapter into live authority needs source IDs, target paths, authority compatibility, queue compatibility, and validation evidence. This chapter is therefore a review map, not a permission slip.

### Source Trail

- `AGENTS.md`
- `docs/architecture/INVARIANTS.md`
- `docs/canon/constitution_v1.md`
- `docs/repo/FOUNDATION_LOCK.md`
- `docs/README.md`
- `docs/architecture/CANONICAL_SYSTEM_MAP.md`
- `docs/architecture/WHAT_THIS_IS.md`
- `docs/architecture/WHAT_THIS_IS_NOT.md`
- `docs/canon/glossary_v1.md`
- `docs/architecture/CONTRACTS_INDEX.md`
- `README.md`
- `docs/archive/conversations/_decision/DECISION_SUMMARY_v0.md`
- `docs/archive/conversations/_synthesis/CURRENT_PROJECT_ATLAS_v0.md`
- `docs/archive/conversations/_synthesis/PROJECT_SYNTHESIS_BOOK_v0.md`
- `docs/archive/conversations/_synthesis/READ_THIS_FIRST_v0.md`
- `docs/archive/docs_corpus/_archive/DOCS_CONVERSATION_CORPUS_INTEGRATION_v0.md`
- `docs/archive/docs_corpus/_reconciliation/DOCS_CURRENT_PROJECT_PICTURE_v0.md`
- `docs/archive/conversations/_synthesis/FULL_PROJECT_PICTURE_v0.md`
