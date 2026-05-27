# STRUCTURED REGISTERS — Dominium Canon, Repository Alignment, and Portability Doctrine

## 17. Workstream Register

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

## 18. Decision Register

| ID | Decision | Status | Evidence / basis | Rationale | Implications | Related workstream | Confidence | Label |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| DECISION-01 | Treat old v1 Constitution and Glossary as the comparison baseline for this chat. | Accepted in-chat; repo authority later refined. | User pasted them as ground truth; assistant acknowledged. | Provides baseline for audit but must not override repo-materialized canon in live repo. | WORKSTREAM-01 | 4 | FACT |
| DECISION-02 | Prefer repo-materialized canonical documents over raw prompts for current repository authority. | Established by audit; not directly stated by user, but supported by repo docs. | `CANON_INDEX` says prompts are execution artifacts and not authoritative unless materialized. | Future work should cite `docs/canon/*` and canon index, not raw chat memory alone. | WORKSTREAM-01 | 4 | FACT/INFERENCE |
| DECISION-03 | Use ownership-based source roots instead of generic `src/`/`source/` layout. | Recommended and supported by current repo naming/layout docs. | Repo docs forbid new `src`/`source` directories and use ownership roots. | Preserve `apps/ engine/ game/ runtime/ contracts/ content/ ...` model. | WORKSTREAM-04 | 4 | FACT/INFERENCE |
| DECISION-04 | Do not freeze all code; freeze contracts and make implementations replaceable. | Assistant recommendation; user intent strongly supports it. | User requested full replaceability and reuse across games/projects. | Directs future architecture toward ABI/schema/protocol boundaries. | WORKSTREAM-03 | 4 | INFERENCE |
| DECISION-05 | Treat survival/runtime gameplay as not fully implemented yet despite strong declarative scaffold. | Audit conclusion, not a user decision. | Survival processes/fields found in registries; full agent gameplay loops deferred in status docs. | Avoid overstating implementation maturity. | WORKSTREAM-06 | 4 | INFERENCE |
| DECISION-06 | Create this preservation package with human-readable report plus structured exports. | Triggered by uploaded preservation prompt. | Uploaded prompt explicitly requested files and package without asking whether to proceed. | This answer creates the artifact set. | WORKSTREAM-08 | 5 | FACT |

## 19. Task Register

| ID | Task | Priority | Urgency | Owner | Dependencies | Inputs needed | Expected output | Next step | Related workstream | Label |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| TASK-01 | Retire or resolve remaining layout/naming exceptions through gated move waves. | P1 | U1 | Project maintainer / future assistant | Layout contract, root allowlist, exception ledger | Current repo tree, move maps, strict validators | Reduced bad-root debt with preserved semantic IDs | Plan next safe move/refactor batch | WORKSTREAM-04 | FACT/INFERENCE |
| TASK-02 | Define stable public Domino ABI/API spine. | P1 | U1 | Engine architect | Constitution, glossary, existing headers | Public header inventory, ABI contract needs | ABI contract files and public C header rules | Draft `contracts/abi/*` and validate headers | WORKSTREAM-05 | INFERENCE |
| TASK-03 | Formalize schema/registry/protocol compatibility rules. | P1 | U1 | Contracts owner | Existing schemas/registries | Schema versioning inventory | Migration/refusal/round-trip policy | Audit all schemas for ID/version/stability/migration | WORKSTREAM-05 | INFERENCE |
| TASK-04 | Add a second minimal Domino-based product/game as reuse proof. | P2 | U2 | Future implementation owner | Domino public API, runtime services | Minimal product requirements | Example app proving engine reuse | Create a small example and measure coupling | WORKSTREAM-07 | INFERENCE |
| TASK-05 | Implement or audit concrete law-gated Process execution for survival slice. | P1 | U2 | Game/runtime owner | Survival registries, LawProfiles, AuthorityContext schema | Process executor design/status | Runtime proof that registries drive behavior | Inspect process execution code and tests; implement missing handlers | WORKSTREAM-06 | INFERENCE |
| TASK-06 | Repeat repository audit with full tree and test outputs when needed. | P1 | U1 | Future assistant/Codex | GitHub repo, local checkout, CI logs | Full file list, test results | More complete alignment report | Run strict validators and code search locally | WORKSTREAM-02 | INFERENCE |
| TASK-07 | Merge this chat package into the master Project Spec Book only with uncertainty labels preserved. | P1 | U1 | Aggregator | This handoff package and other chat reports | Other reports/conflicts | Spec-book sections with source labels | Use aggregator packet first | WORKSTREAM-08 | FACT/INFERENCE |

## 20. Constraint Register

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

## 21. User Preference Register

| ID | Preference | Area | Explicit/inferred/uncertain | Strength | Practical implication | Risk if wrong | Label |
| --- | --- | --- | --- | --- | --- | --- | --- |
| PREF-01 | Direct, source-grounded, audit-ready answers. | Communication | Explicit | High | Use citations/labels and identify uncertainty. | Loss of trust if unsupported claims appear. | FACT |
| PREF-02 | Human-readable narrative over machine-readable dumps for chat preservation. | Communication | Explicit | High | Start with prose and explanation before registers/specs. | Output may feel unusable if only YAML/tables. | FACT |
| PREF-03 | Do not treat brainstorms as decisions. | Epistemics | Explicit | High | Mark assistant suggestions separately from accepted decisions. | Future assistants may formalize tentative ideas incorrectly. | FACT |
| PREF-04 | Broad/deep architectural reasoning for Dominium structure and future-proofing. | Technical | Explicit | High | Discuss system-level practices, not just file renames. | May miss key engineering risks if too narrow. | FACT |
| PREF-05 | Prefer portability, modularity, extensibility, replaceability, and backward compatibility. | Technical | Explicit | High | Design around stable contracts and replaceable implementations. | Project may become one-off and hard to reuse. | FACT |
| PREF-06 | Use labels FACT/INFERENCE/UNCERTAIN/PROJECT-CONTEXT where important. | Epistemics | Explicit | High | Preserve confidence and source scope in reports. | Merging reports may corrupt source hierarchy. | FACT |

## 22. Open Questions Register

| ID | Question / issue | Why it matters | Known information | Unknown information | Resolution path | Priority | Related workstream | Label |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| QUESTION-01 | Which repo layout state is current where docs claim product roots moved but earlier fetched code still appeared under root `client/`? | This affects source-layout truth and cleanup planning. | Docs say `apps/` is canonical; earlier code fetch succeeded under `client/`; `apps/client` fetch failed in this session. | Whether the connector saw stale docs, old paths, branch drift, or unresolved repo inconsistency. | Run full tree listing/local checkout validation. | P0 | WORKSTREAM-04 | UNCERTAIN |
| QUESTION-02 | How much of the survival vertical slice is implemented as runtime Process execution rather than registries? | Determines implementation maturity. | Fields/process IDs/law profiles exist in registries. | Concrete process executor/handlers/tests status. | Inspect game/runtime process code and tests. | P1 | WORKSTREAM-06 | UNCERTAIN |
| QUESTION-03 | What are the exact public API/ABI boundaries for Domino vs Dominium vs runtime? | Needed for reuse and backward compatibility. | General doctrine and some headers exist. | Formal ABI stability map and public/private header inventory. | Create/API audit and contract map. | P1 | WORKSTREAM-05 | INFERENCE |
| QUESTION-04 | What remaining bad roots/exceptions exist today? | Necessary before feature expansion/refactors. | Docs mention exceptions and cleanup waves. | Current exact count/status at HEAD. | Run strict layout validators and read exception ledger. | P1 | WORKSTREAM-04 | UNCERTAIN |
| QUESTION-05 | What should become formal requirements in the master Project Spec Book vs background context? | Prevents over-formalizing suggestions. | This chat contains both accepted canon and assistant recommendations. | User acceptance of specific practices beyond high-level preference. | Aggregator review with labels preserved. | P1 | WORKSTREAM-08 | INFERENCE |
| QUESTION-06 | Should a second minimal Domino product be built now or after layout cleanup? | Determines next practical proof. | Assistant recommended it as reuse proof. | User/project priority and current build readiness. | Decision by project owner after current blockers reviewed. | P2 | WORKSTREAM-07 | UNCERTAIN |

## 23. Artifact Ledger

| ID | Artifact / file / prompt / output | Type | Purpose | Status | Origin | Carry forward? | Notes | Label |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| ARTIFACT-01 | DOMINIUM CONSTITUTIONAL ARCHITECTURE & EXECUTION CONTRACT v1 | Pasted prompt/doc | Baseline architecture contract for chat comparison. | Used in chat; repo has canonical materialized version. | User pasted in current chat | Yes | Treat raw prompt as baseline but repo canon as current authority. | FACT |
| ARTIFACT-02 | DOMINIUM CANONICAL GLOSSARY v1.0.0 | Pasted prompt/doc | Vocabulary authority for current chat. | Used in chat; repo has canonical materialized version. | User pasted in current chat | Yes | Preserve definitions and deprecated/reserved words. | FACT |
| ARTIFACT-03 | Repository alignment audit answer | Chat output | Compared live repo docs/code to old v1. | Produced in chat, not a file until this package. | Assistant | Yes | Key finding: strong docs/schema alignment, partial implementation. | FACT |
| ARTIFACT-04 | Portability/modularity/future-proofing doctrine answer | Chat output | Broad guidance on coding practices and repo structure. | Produced in chat, not a file until this package. | Assistant | Yes | Contains recommendations; not all are user decisions. | FACT |
| ARTIFACT-05 | Uploaded `Pasted text.txt` | Uploaded text file | Mega prompt instructing this preservation/export task. | Current attachment read successfully. | User upload | Yes | This task’s direct instruction source. | FACT |
| ARTIFACT-06 | GitHub connector source observations | Connector output | Evidence from repo files used for audit. | Available in current chat through citations; not a local repo checkout. | Assistant/tool | Yes | Partial because not full tree/local test run. | FACT |

## 24. Rejected / Superseded Options Register

| ID | Option | Status | Reason | Final or tentative? | Reconsider conditions | Related workstream | Label |
| --- | --- | --- | --- | --- | --- | --- | --- |
| REJECTED-01 | Treat raw chat prompts as stronger than repo-materialized canon. | Superseded | Repo canon index says prompts are execution artifacts unless materialized. | Final for current repo authority unless canon changes. | Only reconsider if repo authority order changes. | WORKSTREAM-01 | FACT |
| REJECTED-02 | Use generic `src/` or `source/` root as the active layout. | Rejected/superseded | Current naming/no-src policy says ownership roots are active model. | Final for new active source work. | Only reconsider by explicit repo contract amendment. | WORKSTREAM-04 | FACT |
| REJECTED-03 | Treat docs and registries as proof that full gameplay is implemented. | Rejected as unsafe | Audit separated docs/schema from code behavior. | Final as epistemic discipline. | Reconsider after runtime tests prove behavior. | WORKSTREAM-02 | INFERENCE |
| REJECTED-04 | Perform a grand rewrite/refactor without gated ownership migration. | Deprioritised | Would risk breaking identity, imports, ABI, and compatibility. | Tentative; controlled rewrites remain allowed. | Only after contracts/tests/migration plan exist. | WORKSTREAM-04 | INFERENCE |

## 25. Risk Register

| ID | Risk / failure mode | Consequence | Likelihood | Severity | Mitigation | Related workstream | Label |
| --- | --- | --- | --- | --- | --- | --- | --- |
| RISK-01 | Treating repo docs as fully implemented behavior. | Overstates maturity and causes bad planning. | Medium | High | Separate docs/schema/code/test status. | WORKSTREAM-02 | FACT/INFERENCE |
| RISK-02 | Treating assistant recommendations as accepted decisions. | Spec book may formalize unapproved practices. | Medium | High | Use decision status and labels. | WORKSTREAM-08 | FACT |
| RISK-03 | Breaking semantic IDs during path cleanup. | Saves/packs/contracts/replays may become incompatible. | Medium | High | Path moves must preserve IDs unless explicit migration. | WORKSTREAM-04 | INFERENCE |
| RISK-04 | Creating new generic buckets during refactor. | Ownership ambiguity returns. | Medium | Medium | Use layout/naming contracts and validators. | WORKSTREAM-04 | FACT/INFERENCE |
| RISK-05 | Hidden coupling prevents Domino reuse by other games. | Engine becomes Dominium-specific. | Medium | High | Add second minimal product reuse proof. | WORKSTREAM-07 | INFERENCE |
| RISK-06 | Runtime/platform/UI layers gain truth authority. | Violates canon and harms multiplayer fairness/determinism. | Medium | High | Enforce Truth/Perceived/Render and command/refusal spine. | WORKSTREAM-03 | FACT/INFERENCE |
| RISK-07 | Current preservation is incomplete because full historical transcript is unavailable. | Future aggregation may miss context outside visible chat. | Medium | Medium | State coverage limitation and use PROJECT-CONTEXT labels. | WORKSTREAM-08 | FACT |

## 26. Verification Queue

| ID | Item requiring verification | Why verification is needed | Suggested source/type | Priority | Related workstream | Label |
| --- | --- | --- | --- | --- | --- | --- |
| VERIFY-01 | Current physical repo tree vs claimed converged `apps/` layout. | Potential doc/code inconsistency observed in this session. | Local checkout tree listing or GitHub tree API. | P0 | WORKSTREAM-04 | UNCERTAIN |
| VERIFY-02 | Current strict layout/root validator status and active exceptions. | Needed before claiming cleanup completion. | Run `tools/validators/check_repo_layout.py --strict` and root allowlist validators. | P1 | WORKSTREAM-04 | UNCERTAIN |
| VERIFY-03 | Survival process runtime implementation status. | Registry existence does not prove behavior. | Code search/local tests for process executor/handlers. | P1 | WORKSTREAM-06 | UNCERTAIN |
| VERIFY-04 | XStack/RepoX/TestX latest pass/fail status. | Earlier chat audit may be stale. | Current CI/local `scripts/dev/gate.py verify` and CTest outputs. | P1 | WORKSTREAM-02 | UNCERTAIN |
| VERIFY-05 | External examples cited in prior answer: Linux, SQLite, NASA cFS, SemVer. | External-world facts may have changed or were not reverified in this preservation task. | Official docs/web verification. | P2 | WORKSTREAM-03 | UNVERIFIED |

## 27. Chronological Timeline Register

| Sequence | Event / topic | What changed or was decided | Why it mattered | Current relevance | Confidence |
| --- | --- | --- | --- | --- | --- |
| 1 | User pasted old Dominium Constitutional Architecture & Execution Contract v1. | Established comparison baseline and canon claims. | Anchored all later alignment questions. | Still important as source artifact. | 5 |
| 2 | User pasted old Canonical Glossary v1.0.0. | Bound terminology for current chat. | Prevents term drift and mode-flag ambiguity. | Still important. | 5 |
| 3 | User asked how current GitHub repo aligns with old v1 and what docs/code say. | Shifted from acceptance to audit. | Required live repo inspection. | Core output of chat. | 5 |
| 4 | Assistant inspected live repo docs/code and reported strong docs/schema alignment but partial implementation. | Produced nuanced state assessment. | Prevents overclaiming maturity. | Carry forward to spec book. | 4 |
| 5 | User asked for broad/deep practices for portability/modularity/extensibility/future-proofing. | Shifted from audit to engineering doctrine. | Established what the project should optimize for. | Core future-work input. | 5 |
| 6 | Assistant inspected layout/naming docs and recommended contract-first ownership-root architecture. | Connected current repo convergence to future coding standards. | Defines next structural doctrine. | Carry forward with labels. | 4 |
| 7 | User uploaded preservation mega-prompt. | Requested complete preservation package for this chat. | Creates this artifact package. | Current task. | 5 |

## 28. Spec Book Contribution Register

| Spec-book area | Contribution from this chat | Source IDs | Should become requirement/context/open issue? | Confidence | Notes |
| --- | --- | --- | --- | --- | --- |
| Architecture Constitution | Use v1 Constitution/Glossary and live repo canon hierarchy as foundational source hierarchy. | DECISION-01, DECISION-02 | Requirement/context | 4 | Preserve repo-materialized canon as stronger than raw prompts. |
| Repository Layout and Ownership | Ownership-root layout and no-src/source policy. | DECISION-03, CONSTRAINT-05 | Requirement | 4 | Verify current tree/exception status before finalizing. |
| Portability and API Doctrine | Stable contracts, replaceable implementations, C ABI, schema/protocol versioning. | DECISION-04, TASK-02, TASK-03 | Requirement candidate | 3 | Some parts are assistant recommendations, not explicit user decisions. |
| Implementation Status | Docs/schema strong; runtime gameplay partial; advanced systems deferred. | DECISION-05, QUESTION-02 | Open issue/context | 4 | Avoid overstating current implementation. |
| Governance and Verification | Use XStack/RepoX/TestX/AuditX and strict validators as gates. | CONSTRAINTS, TASK-06 | Requirement/context | 4 | Latest status must be verified. |
| Reuse Proof | Add second minimal game/product on Domino. | TASK-04 | Open issue/requirement candidate | 3 | Needs user/project prioritization. |
