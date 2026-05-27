# 29. Context Transfer Packet for a Future Chat

## 29.1 Ultra-Condensed Bootstrap Brief

This chat re-established old Dominium canon, audited current repository alignment, and defined future-proofing doctrine. The user pasted an old Dominium Constitutional Architecture & Execution Contract v1 and Canonical Glossary v1. Those defined Dominium/Domino as a deterministic simulation platform: Domino C89 engine, Dominium C++98 game layer, product apps, and XStack governance. Core invariants include deterministic authoritative math, named RNG streams, thread-count invariance, replay hash equivalence, Process-only mutation, LawProfile/AuthorityContext gating, no runtime mode flags, data-defined domains, explicit refusal/degradation, and TruthModel → PerceivedModel → RenderModel separation.

The user then asked how the current GitHub repo `julesc013/dominium` aligns with that old v1 contract and glossary, asking what the docs say and what the code does. The audit found that old v1 canon and glossary are materialized as repo docs under `docs/canon/constitution_v1.md` and `docs/canon/glossary_v1.md`, and that repo authority now flows through materialized canonical docs rather than raw prompts. The repo has strong docs/schema/registry/governance alignment, C90/C++98 build discipline, deterministic RNG/world scaffolding, and a real client session pipeline with explicit transitions and refusal codes. It is not yet a full implementation of every v1 ambition: survival is mostly registry/profile/process-declaration level; full agent gameplay loops, embodiment, MMO distributed authority runtime, and other advanced systems remain deferred or incomplete.

The user then asked a broad architecture question: how to make all code portable, modular, extensible, reusable for other games on Domino and even other game/engine projects, and replaceable down to files/directories. The answer doctrine was: stable contracts, replaceable implementations, deterministic behavior, portable projections, no accidental authority from paths/tools/UIs/prompts. The current ownership-root layout is broadly right: `apps/`, `engine/`, `game/`, `runtime/`, `contracts/`, `content/`, `docs/`, `tests/`, `tools/`, `scripts/`, `cmake/`, `external/`, `release/`, `archive/`. Avoid `src`, `source`, `common`, `shared`, `misc`, `impl`, `old`, `new`, `v2`, etc. Path is storage; semantic IDs and contracts define identity.

Top future tasks: verify current physical repo tree and layout exceptions, formalize public API/ABI boundaries, audit concrete Process runtime implementation, define compatibility/migration rules for schemas/saves/replays/packs/protocols, and build a second minimal Domino-based product to prove engine reuse.

## 29.2 Source Hierarchy

1. Direct user statements in this chat.
2. Explicit decisions accepted by the user.
3. Current task register.
4. Constraint register.
5. Artifact ledger.
6. Inferences.
7. Assistant suggestions not accepted by the user.
8. General model knowledge.

## 29.3 Operating Rules for Future Assistants

- Preserve FACT / INFERENCE / UNCERTAIN / PROJECT-CONTEXT labels.
- Do not assume access to the old chat.
- Do not re-ask answered questions.
- Verify stale facts before relying on them.
- Do not invent missing details.
- Do not treat tentative items as final.
- Do not repeat rejected options as new recommendations.
- Preserve artifacts and semantic IDs.
- Use structured outputs when continuing.
- Separate docs, schemas, code, tests, and product proof.
- Treat raw prompts as lower authority than materialized repo canon for current repository work.

## 29.4 Active Workstreams

| ID | Name | Objective | Current state | Desired end state | Status | Priority | Confidence | Label |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| WORKSTREAM-01 | Canon reconstitution and glossary binding | Preserve and interpret old v1 Constitution and Glossary as the initial comparison baseline. | Old v1 contract/glossary were pasted and acknowledged; live repo canon files were later found. | Repo canon and chat guidance stay aligned without treating raw prompts as stronger than materialized repo docs. | Active | P0 | 4 | FACT/INFERENCE |
| WORKSTREAM-02 | Repository alignment audit | Assess docs and code of `julesc013/dominium` against the v1 contract/glossary. | GitHub connector audit completed at a broad but not exhaustive level. | Repeatable, cited audit tying docs, schemas, code, tests, and gaps to canon clauses. | Partially complete | P0 | 4 | FACT |
| WORKSTREAM-03 | Portability and modularity doctrine | Define practices for reusable engine/game/runtime platform architecture. | A broad doctrine was produced: stable contracts, replaceable implementations, ownership roots, no generic buckets. | Formalize into repo contracts, coding standards, API rules, and validation gates. | Active | P0 | 4 | FACT/INFERENCE |
| WORKSTREAM-04 | Repository layout and naming convergence | Finish ownership-root convergence and naming law enforcement. | Current docs define ownership roots and naming contracts but note transitional debt. | Strict layout with retired exceptions and no new ambiguous roots. | Active | P1 | 4 | FACT |
| WORKSTREAM-05 | Stable API / ABI / schema boundary design | Make public boundaries durable while permitting internal rewrites. | Recommended but not fully implemented in this chat. | Public C ABI, versioned data contracts, module descriptors, compatibility tests. | Planned | P1 | 3 | INFERENCE |
| WORKSTREAM-06 | Runtime implementation maturity | Move from declarative registries/scaffolds to real law-gated runtime processes. | Audit found survival mostly registry-level and advanced systems deferred. | Concrete Process/Authority/Law runtime with tests and replay proofs. | Open | P1 | 3 | INFERENCE |
| WORKSTREAM-07 | Reusable Domino proof project | Prove reuse by building a second minimal game/product on Domino. | Recommended as a strong test; not implemented. | Example product that compiles without hidden Dominium coupling. | Proposed | P2 | 3 | INFERENCE |
| WORKSTREAM-08 | Chat preservation and aggregation | Create package that preserves this chat for later project-spec aggregation. | This response and files implement it. | Human-readable report + structured registers + aggregator/spec packets. | In progress | P0 | 4 | FACT |

## 29.5 Current Priorities

1. Verify current repo physical layout and active exceptions.
2. Formalize API/ABI/schema/protocol boundaries.
3. Audit survival/process runtime implementation status.
4. Preserve ownership-root layout and naming law.
5. Use this package for master spec-book aggregation.

## 29.6 Current Open Questions

| ID | Question / issue | Why it matters | Known information | Unknown information | Resolution path | Priority | Related workstream | Label |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| QUESTION-01 | Which repo layout state is current where docs claim product roots moved but earlier fetched code still appeared under root `client/`? | This affects source-layout truth and cleanup planning. | Docs say `apps/` is canonical; earlier code fetch succeeded under `client/`; `apps/client` fetch failed in this session. | Whether the connector saw stale docs, old paths, branch drift, or unresolved repo inconsistency. | Run full tree listing/local checkout validation. | P0 | WORKSTREAM-04 | UNCERTAIN |
| QUESTION-02 | How much of the survival vertical slice is implemented as runtime Process execution rather than registries? | Determines implementation maturity. | Fields/process IDs/law profiles exist in registries. | Concrete process executor/handlers/tests status. | Inspect game/runtime process code and tests. | P1 | WORKSTREAM-06 | UNCERTAIN |
| QUESTION-03 | What are the exact public API/ABI boundaries for Domino vs Dominium vs runtime? | Needed for reuse and backward compatibility. | General doctrine and some headers exist. | Formal ABI stability map and public/private header inventory. | Create/API audit and contract map. | P1 | WORKSTREAM-05 | INFERENCE |
| QUESTION-04 | What remaining bad roots/exceptions exist today? | Necessary before feature expansion/refactors. | Docs mention exceptions and cleanup waves. | Current exact count/status at HEAD. | Run strict layout validators and read exception ledger. | P1 | WORKSTREAM-04 | UNCERTAIN |
| QUESTION-05 | What should become formal requirements in the master Project Spec Book vs background context? | Prevents over-formalizing suggestions. | This chat contains both accepted canon and assistant recommendations. | User acceptance of specific practices beyond high-level preference. | Aggregator review with labels preserved. | P1 | WORKSTREAM-08 | INFERENCE |
| QUESTION-06 | Should a second minimal Domino product be built now or after layout cleanup? | Determines next practical proof. | Assistant recommended it as reuse proof. | User/project priority and current build readiness. | Decision by project owner after current blockers reviewed. | P2 | WORKSTREAM-07 | UNCERTAIN |

## 29.7 Recommended First Action

Run a current repository structural audit: list root directories, compare to `contracts/repo/layout.contract.toml`, read `contracts/repo/layout_exceptions.toml`, verify whether `apps/` vs root `client/` state is current, and produce a short “docs vs physical tree vs build targets” report before any further broad refactor or feature work.
