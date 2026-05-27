# Aggregator Packet — Dominium Canon, Repository Alignment, and Portability Doctrine

## Packet Metadata

* Chat label: Dominium Canon, Repository Alignment, and Portability Doctrine
* Date anchor: 2026-05-27 Australia/Melbourne
* Source scope: This chat only unless labelled PROJECT-CONTEXT
* Coverage: Partial visible chat + uploaded preservation prompt + connector evidence
* Confidence: 4/5 for visible chat; lower for unavailable prior context
* Staleness risk: Medium
* Merge priority: High
* Main limitations: no full local checkout/test run; some repo layout state needs verification; assistant recommendations must not all become decisions.

## Ultra-Condensed Carry-Forward Capsule

This chat was about preserving and re-grounding Dominium’s architecture around a very old constitutional contract, then checking whether the current GitHub repository still follows that contract, and finally broadening the question into a platform-engineering doctrine for portability, modularity, extensibility, reuse, future-proofing, and long-term compatibility.

The chat began with the user pasting the old “DOMINIUM CONSTITUTIONAL ARCHITECTURE & EXECUTION CONTRACT v1” and the old “CANONICAL GLOSSARY v1”. Those documents defined Dominium as a deterministic universe simulation platform built around Domino as a C89 deterministic engine, Dominium as a C++98 game layer, product applications such as Client/Server/Setup/Launcher, and XStack as a governance layer. The v1 ontology reduced all systems to Assemblies, Fields, Processes, Agents, and Law. It also insisted on fixed-point authoritative math, named RNG streams, thread-count invariance, replay hash equivalence, explicit AuthorityContext, LawProfile-driven behavior rather than runtime mode flags, and TruthModel → PerceivedModel → RenderModel separation. The glossary locked the vocabulary around terms such as Authority, LawProfile, Lens, Process, SessionSpec, UniverseIdentity, UniverseState, Macro Capsule, SRZ, XStack, RepoX, TestX, AuditX, CompatX, SecureX, and related concepts.

The user then asked how the current GitHub repository `julesc013/dominium` aligned with that old v1 contract and glossary, asking specifically: what do the docs say, and what does the code do? The assistant inspected the live repository through the GitHub connector. The main finding was that the old v1 contract and glossary had not been discarded; they had been materialized into repo canon under `docs/canon/constitution_v1.md` and `docs/canon/glossary_v1.md`. The repo also had a newer canon-index regime saying prompts themselves are not authoritative unless materialized as canonical documents. This mattered because it changed the authority model: the old pasted prompt is historically important, but the repo version of the contract is the operational source of truth. The audit found strong alignment in documents, schemas, registries, governance, deterministic build constraints, and client session-pipeline code, but only partial implementation of the full runtime gameplay model. Survival fields and processes exist as registries; full agent gameplay loops, MMO/SRZ distributed runtime, embodiment, and other advanced systems were still described as deferred or future work.

The user then reframed the issue around engineering quality: they wanted the code to be portable, modular, extensible, reusable for other games on the same Domino engine, reusable for different engine or game projects, and replaceable down to files and directories if a rewrite/refactor is needed. They explicitly said the project should be developed like a proper game or OS, not a one-off indie project. The assistant’s answer converted that into a doctrine: stable contracts, replaceable implementations, deterministic behavior, portable projections, and no accidental authority from paths, tools, UIs, or prompts. The answer emphasized that the goal is not to freeze every file, but to make every boundary explicit, versioned, testable, and replaceable. It identified the ownership-based source layout as broadly right: `apps/`, `engine/`, `game/`, `runtime/`, `contracts/`, `content/`, `docs/`, `tests/`, `tools/`, `scripts/`, `cmake/`, `external/`, `release/`, and `archive/`. It also identified remaining cleanup debt and recommended finishing ownership-contract convergence rather than starting a grand rewrite.

The unique value of this chat is that it bridges three layers: old constitutional intent, current repository reality, and future engineering doctrine. It is not merely a summary of Dominium’s game design. It is a portability and governance checkpoint: what is canon, what is implemented, what remains declarative, what structure should remain, what structure still needs cleanup, and what practices should govern future coding.

The highest-value carry-forward is the doctrine: stable contracts, replaceable implementations, deterministic behavior, portable projections, and no accidental authority from paths/tools/UIs/prompts. The current ownership-root layout appears directionally correct, but verification of current physical tree and exception status is required before acting.

## Top Carry-Forward Items

| Priority | Item | Type | Related ID | Why it matters | Label | Confidence |
| --- | --- | --- | --- | --- | --- | --- |
| P0 | Repo-materialized canon outranks raw prompt for current repo authority | Authority rule | DECISION-02 | Prevents chat-memory drift | FACT/INFERENCE | 4 |
| P0 | Stable contracts + replaceable implementations | Doctrine | DECISION-04 | Core future-proofing answer | INFERENCE | 4 |
| P0 | Verify current physical repo layout | Task | TASK-01 / VERIFY-01 | Potential docs/code inconsistency observed | UNCERTAIN | 3 |
| P1 | Formalize public API/ABI/data compatibility surfaces | Task | TASK-02/TASK-03 | Needed for reuse and backward compatibility | INFERENCE | 3 |
| P1 | Do not overstate runtime implementation maturity | Risk | RISK-01 | Docs/registries are not product proof | INFERENCE | 4 |

## Workstream Summaries

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

## Compact Registers for Merge

### Decisions

| ID | Decision | Status | Evidence / basis | Rationale | Implications | Related workstream | Confidence | Label |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| DECISION-01 | Treat old v1 Constitution and Glossary as the comparison baseline for this chat. | Accepted in-chat; repo authority later refined. | User pasted them as ground truth; assistant acknowledged. | Provides baseline for audit but must not override repo-materialized canon in live repo. | WORKSTREAM-01 | 4 | FACT |
| DECISION-02 | Prefer repo-materialized canonical documents over raw prompts for current repository authority. | Established by audit; not directly stated by user, but supported by repo docs. | `CANON_INDEX` says prompts are execution artifacts and not authoritative unless materialized. | Future work should cite `docs/canon/*` and canon index, not raw chat memory alone. | WORKSTREAM-01 | 4 | FACT/INFERENCE |
| DECISION-03 | Use ownership-based source roots instead of generic `src/`/`source/` layout. | Recommended and supported by current repo naming/layout docs. | Repo docs forbid new `src`/`source` directories and use ownership roots. | Preserve `apps/ engine/ game/ runtime/ contracts/ content/ ...` model. | WORKSTREAM-04 | 4 | FACT/INFERENCE |
| DECISION-04 | Do not freeze all code; freeze contracts and make implementations replaceable. | Assistant recommendation; user intent strongly supports it. | User requested full replaceability and reuse across games/projects. | Directs future architecture toward ABI/schema/protocol boundaries. | WORKSTREAM-03 | 4 | INFERENCE |
| DECISION-05 | Treat survival/runtime gameplay as not fully implemented yet despite strong declarative scaffold. | Audit conclusion, not a user decision. | Survival processes/fields found in registries; full agent gameplay loops deferred in status docs. | Avoid overstating implementation maturity. | WORKSTREAM-06 | 4 | INFERENCE |
| DECISION-06 | Create this preservation package with human-readable report plus structured exports. | Triggered by uploaded preservation prompt. | Uploaded prompt explicitly requested files and package without asking whether to proceed. | This answer creates the artifact set. | WORKSTREAM-08 | 5 | FACT |

### Tasks

| ID | Task | Priority | Urgency | Owner | Dependencies | Inputs needed | Expected output | Next step | Related workstream | Label |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| TASK-01 | Retire or resolve remaining layout/naming exceptions through gated move waves. | P1 | U1 | Project maintainer / future assistant | Layout contract, root allowlist, exception ledger | Current repo tree, move maps, strict validators | Reduced bad-root debt with preserved semantic IDs | Plan next safe move/refactor batch | WORKSTREAM-04 | FACT/INFERENCE |
| TASK-02 | Define stable public Domino ABI/API spine. | P1 | U1 | Engine architect | Constitution, glossary, existing headers | Public header inventory, ABI contract needs | ABI contract files and public C header rules | Draft `contracts/abi/*` and validate headers | WORKSTREAM-05 | INFERENCE |
| TASK-03 | Formalize schema/registry/protocol compatibility rules. | P1 | U1 | Contracts owner | Existing schemas/registries | Schema versioning inventory | Migration/refusal/round-trip policy | Audit all schemas for ID/version/stability/migration | WORKSTREAM-05 | INFERENCE |
| TASK-04 | Add a second minimal Domino-based product/game as reuse proof. | P2 | U2 | Future implementation owner | Domino public API, runtime services | Minimal product requirements | Example app proving engine reuse | Create a small example and measure coupling | WORKSTREAM-07 | INFERENCE |
| TASK-05 | Implement or audit concrete law-gated Process execution for survival slice. | P1 | U2 | Game/runtime owner | Survival registries, LawProfiles, AuthorityContext schema | Process executor design/status | Runtime proof that registries drive behavior | Inspect process execution code and tests; implement missing handlers | WORKSTREAM-06 | INFERENCE |
| TASK-06 | Repeat repository audit with full tree and test outputs when needed. | P1 | U1 | Future assistant/Codex | GitHub repo, local checkout, CI logs | Full file list, test results | More complete alignment report | Run strict validators and code search locally | WORKSTREAM-02 | INFERENCE |
| TASK-07 | Merge this chat package into the master Project Spec Book only with uncertainty labels preserved. | P1 | U1 | Aggregator | This handoff package and other chat reports | Other reports/conflicts | Spec-book sections with source labels | Use aggregator packet first | WORKSTREAM-08 | FACT/INFERENCE |

### Constraints

| ID | Constraint | Type | Hard/soft | Source / basis | Practical implication | Violation risk | Confidence | Label |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| CONSTRAINT-01 | Determinism remains primary: fixed-point authoritative math, named RNG, replay/hash equivalence, thread-count invariance. | Technical/canon | Hard | Old v1 contract and live repo constitution | Do not introduce nondeterministic authoritative behavior. | High | 5 | FACT |
| CONSTRAINT-02 | Process-only mutation and law-gated authority. | Technical/canon | Hard | v1 and live constitution | All authoritative state changes must route through processes and AuthorityContext/LawProfile. | High | 5 | FACT |
| CONSTRAINT-03 | No runtime mode flags; behavior derives from ExperienceProfile/LawProfile/ParameterBundle. | Technical/canon | Hard | v1 and live constitution | Avoid `*_mode` gameplay branches and mode-specific logic forks. | Medium | 5 | FACT |
| CONSTRAINT-04 | TruthModel → PerceivedModel → RenderModel separation. | Architecture | Hard | v1 and repo docs | Renderer/runtime must not access or mutate truth directly. | High | 5 | FACT |
| CONSTRAINT-05 | Ownership-root layout; no new generic `src`/`source`/`common`/`shared`/`misc` buckets. | Repository structure | Hard for new work | Naming/layout contracts | New files must be placed by ownership and role. | Medium | 4 | FACT |
| CONSTRAINT-06 | Source repo layout is not install/package/runtime projection layout. | Repository/distribution | Hard | Layout docs and no-src policy | Do not infer runtime store/save/export roots from source roots. | Medium | 4 | FACT |
| CONSTRAINT-07 | Content/packs must not contain untrusted executable authority. | Security/architecture | Hard | Pack-driven integration doctrine | Future extension code needs separate trust/capability contract. | High | 4 | INFERENCE |
| CONSTRAINT-08 | Human-readable explanation must come before machine-readable handoff in preservation tasks. | Communication | Hard for this task | Uploaded preservation prompt | This output must be understandable without downloading files. | Medium | 5 | FACT |

### Open Questions

| ID | Question / issue | Why it matters | Known information | Unknown information | Resolution path | Priority | Related workstream | Label |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| QUESTION-01 | Which repo layout state is current where docs claim product roots moved but earlier fetched code still appeared under root `client/`? | This affects source-layout truth and cleanup planning. | Docs say `apps/` is canonical; earlier code fetch succeeded under `client/`; `apps/client` fetch failed in this session. | Whether the connector saw stale docs, old paths, branch drift, or unresolved repo inconsistency. | Run full tree listing/local checkout validation. | P0 | WORKSTREAM-04 | UNCERTAIN |
| QUESTION-02 | How much of the survival vertical slice is implemented as runtime Process execution rather than registries? | Determines implementation maturity. | Fields/process IDs/law profiles exist in registries. | Concrete process executor/handlers/tests status. | Inspect game/runtime process code and tests. | P1 | WORKSTREAM-06 | UNCERTAIN |
| QUESTION-03 | What are the exact public API/ABI boundaries for Domino vs Dominium vs runtime? | Needed for reuse and backward compatibility. | General doctrine and some headers exist. | Formal ABI stability map and public/private header inventory. | Create/API audit and contract map. | P1 | WORKSTREAM-05 | INFERENCE |
| QUESTION-04 | What remaining bad roots/exceptions exist today? | Necessary before feature expansion/refactors. | Docs mention exceptions and cleanup waves. | Current exact count/status at HEAD. | Run strict layout validators and read exception ledger. | P1 | WORKSTREAM-04 | UNCERTAIN |
| QUESTION-05 | What should become formal requirements in the master Project Spec Book vs background context? | Prevents over-formalizing suggestions. | This chat contains both accepted canon and assistant recommendations. | User acceptance of specific practices beyond high-level preference. | Aggregator review with labels preserved. | P1 | WORKSTREAM-08 | INFERENCE |
| QUESTION-06 | Should a second minimal Domino product be built now or after layout cleanup? | Determines next practical proof. | Assistant recommended it as reuse proof. | User/project priority and current build readiness. | Decision by project owner after current blockers reviewed. | P2 | WORKSTREAM-07 | UNCERTAIN |

### Artifact Ledger

| ID | Artifact / file / prompt / output | Type | Purpose | Status | Origin | Carry forward? | Notes | Label |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| ARTIFACT-01 | DOMINIUM CONSTITUTIONAL ARCHITECTURE & EXECUTION CONTRACT v1 | Pasted prompt/doc | Baseline architecture contract for chat comparison. | Used in chat; repo has canonical materialized version. | User pasted in current chat | Yes | Treat raw prompt as baseline but repo canon as current authority. | FACT |
| ARTIFACT-02 | DOMINIUM CANONICAL GLOSSARY v1.0.0 | Pasted prompt/doc | Vocabulary authority for current chat. | Used in chat; repo has canonical materialized version. | User pasted in current chat | Yes | Preserve definitions and deprecated/reserved words. | FACT |
| ARTIFACT-03 | Repository alignment audit answer | Chat output | Compared live repo docs/code to old v1. | Produced in chat, not a file until this package. | Assistant | Yes | Key finding: strong docs/schema alignment, partial implementation. | FACT |
| ARTIFACT-04 | Portability/modularity/future-proofing doctrine answer | Chat output | Broad guidance on coding practices and repo structure. | Produced in chat, not a file until this package. | Assistant | Yes | Contains recommendations; not all are user decisions. | FACT |
| ARTIFACT-05 | Uploaded `Pasted text.txt` | Uploaded text file | Mega prompt instructing this preservation/export task. | Current attachment read successfully. | User upload | Yes | This task’s direct instruction source. | FACT |
| ARTIFACT-06 | GitHub connector source observations | Connector output | Evidence from repo files used for audit. | Available in current chat through citations; not a local repo checkout. | Assistant/tool | Yes | Partial because not full tree/local test run. | FACT |

### Risk Register

| ID | Risk / failure mode | Consequence | Likelihood | Severity | Mitigation | Related workstream | Label |
| --- | --- | --- | --- | --- | --- | --- | --- |
| RISK-01 | Treating repo docs as fully implemented behavior. | Overstates maturity and causes bad planning. | Medium | High | Separate docs/schema/code/test status. | WORKSTREAM-02 | FACT/INFERENCE |
| RISK-02 | Treating assistant recommendations as accepted decisions. | Spec book may formalize unapproved practices. | Medium | High | Use decision status and labels. | WORKSTREAM-08 | FACT |
| RISK-03 | Breaking semantic IDs during path cleanup. | Saves/packs/contracts/replays may become incompatible. | Medium | High | Path moves must preserve IDs unless explicit migration. | WORKSTREAM-04 | INFERENCE |
| RISK-04 | Creating new generic buckets during refactor. | Ownership ambiguity returns. | Medium | Medium | Use layout/naming contracts and validators. | WORKSTREAM-04 | FACT/INFERENCE |
| RISK-05 | Hidden coupling prevents Domino reuse by other games. | Engine becomes Dominium-specific. | Medium | High | Add second minimal product reuse proof. | WORKSTREAM-07 | INFERENCE |
| RISK-06 | Runtime/platform/UI layers gain truth authority. | Violates canon and harms multiplayer fairness/determinism. | Medium | High | Enforce Truth/Perceived/Render and command/refusal spine. | WORKSTREAM-03 | FACT/INFERENCE |
| RISK-07 | Current preservation is incomplete because full historical transcript is unavailable. | Future aggregation may miss context outside visible chat. | Medium | Medium | State coverage limitation and use PROJECT-CONTEXT labels. | WORKSTREAM-08 | FACT |

### Verification Queue

| ID | Item requiring verification | Why verification is needed | Suggested source/type | Priority | Related workstream | Label |
| --- | --- | --- | --- | --- | --- | --- |
| VERIFY-01 | Current physical repo tree vs claimed converged `apps/` layout. | Potential doc/code inconsistency observed in this session. | Local checkout tree listing or GitHub tree API. | P0 | WORKSTREAM-04 | UNCERTAIN |
| VERIFY-02 | Current strict layout/root validator status and active exceptions. | Needed before claiming cleanup completion. | Run `tools/validators/check_repo_layout.py --strict` and root allowlist validators. | P1 | WORKSTREAM-04 | UNCERTAIN |
| VERIFY-03 | Survival process runtime implementation status. | Registry existence does not prove behavior. | Code search/local tests for process executor/handlers. | P1 | WORKSTREAM-06 | UNCERTAIN |
| VERIFY-04 | XStack/RepoX/TestX latest pass/fail status. | Earlier chat audit may be stale. | Current CI/local `scripts/dev/gate.py verify` and CTest outputs. | P1 | WORKSTREAM-02 | UNCERTAIN |
| VERIFY-05 | External examples cited in prior answer: Linux, SQLite, NASA cFS, SemVer. | External-world facts may have changed or were not reverified in this preservation task. | Official docs/web verification. | P2 | WORKSTREAM-03 | UNVERIFIED |

## Possible Cross-Chat Duplicates

- Dominium architecture constitution.
- Repo layout convergence.
- XStack/RepoX/TestX governance.
- Distribution/portable projection doctrine.
- Engine/runtime/render/platform separation.
- C89/C++98 language strategy.
- `.dompkg`, lockfiles, virtual roots, install layouts.

## Possible Cross-Chat Conflicts

- Old proposed `src/`/`source` layouts vs current no-src ownership-root doctrine.
- Older root names like `client/`, `server/`, `setup/`, `launcher/` vs claimed `apps/` convergence.
- Assistant recommendations vs user-accepted decisions.
- Docs claiming implementation maturity vs code/tests proving only scaffolding.

## Spec Book Integration Guidance

Feed this chat into architecture constitution, repository layout, API/ABI doctrine, data contracts, governance/verification, and implementation status chapters. Make accepted canon and ownership rules requirements. Treat external examples and assistant-only best-practice proposals as context or requirement candidates until verified/accepted. Do not merge claims of full runtime implementation prematurely.

## Aggregator Warnings

Do not compress this chat into “Dominium aligns with v1.” The precise result is: old canon is materialized; docs/schemas/gates are strong; implementation is partial; layout direction is good; cleanup and verification remain; portability depends on stable contracts plus replaceable implementations.
