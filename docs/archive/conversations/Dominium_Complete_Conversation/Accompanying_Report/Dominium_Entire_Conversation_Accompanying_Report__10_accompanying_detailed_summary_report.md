# Accompanying Human-Readable Detailed Summary and Report — Dominium Canon, Repository Alignment, and Portability Doctrine

Date anchor: 2026-05-27 Australia/Melbourne  
Generated: 2026-05-27 21:01 AEST  
Scope: This conversation, plus the currently available preservation files in `/mnt/data` and the uploaded preservation prompt.  
Epistemic status: mixed. Items marked FACT were visible in this conversation or present in the generated files. Items marked INFERENCE are reasoned summaries. Items marked UNCERTAIN / UNVERIFIED require a fresh repo checkout, tool run, or user confirmation.

---

## 1. Executive summary

This conversation centered on Dominium/Domino as a long-lived, deterministic, reusable simulation and game-platform project. It began with the user re-establishing an old **Dominium Constitutional Architecture & Execution Contract v1** and an old **Canonical Glossary v1** as the baseline for discussion. Those documents defined the project as a deterministic universe simulation stack: Domino as the C89 engine, Dominium as the C++98 game layer, Client/Server/Setup/Launcher as products, and XStack as the governance and verification layer.

The user then asked how the current GitHub repository `julesc013/dominium` aligned with those old documents. A repository inspection was performed through the GitHub connector. The result was not that the repository fully implements the old vision, but that it has strongly **materialized** much of that vision into current canonical documents, schemas, registries, governance tools, CMake policy, deterministic world scaffolding, session pipeline code, and layout/naming contracts. The key distinction established in the conversation was: **docs and registries show architectural intent; runtime code and tests prove implementation maturity**. The repository appeared far more mature as a constitutional/governance scaffold than as a complete game runtime.

The user then broadened the question. They emphasized that the code must be portable, modular, extensible, reusable for different games on the same Domino engine, and reusable in completely different engine or game projects. They wanted a proper game/platform/OS-like development model rather than a one-off indie-project codebase. The answer developed a doctrine around **stable contracts and replaceable implementations**. The central recommendation was not to freeze every directory or every file, but to stabilize public boundaries: ABIs, schemas, semantic IDs, save/replay formats, command/refusal protocols, pack contracts, build/release manifests, and compatibility rules. Implementations behind those boundaries should remain replaceable.

The discussion also examined repository layout. The active layout doctrine discovered in the repo favors ownership-based roots: `apps/`, `engine/`, `game/`, `runtime/`, `contracts/`, `content/`, `docs/`, `tests/`, `tools/`, `scripts/`, `cmake/`, `external/`, `release/`, and `archive/`. This was judged directionally better than a generic `src/` or `source/` structure because it encodes ownership directly. The live repo naming policy explicitly rejects new `src/`, `source`, `common`, `shared`, `misc`, `impl`, `old`, `new`, `legacy`, and similar generic/status terms in active paths.

A preservation package was then generated. This current task adds an accompanying detailed report and bundles it with the earlier preservation files, the uploaded preservation prompt, a new manifest, and a ZIP package. Some previously uploaded files were reported expired by the file-search system. Those expired files cannot be included unless re-uploaded. The package therefore includes only files currently available in `/mnt/data` plus the newly generated files.

The highest-priority practical next step remains: **run a fresh repository audit from an actual current checkout** to verify physical layout, API boundaries, runtime implementation maturity, public contract surfaces, and test/build status.

---

## 2. Conversation chronology

### 2.1 Re-establishing the old constitutional baseline

FACT: The user first pasted a self-contained **Dominium Constitutional Architecture & Execution Contract v1**. It defined the system identity, ontology, structural layers, survival vertical slice, domain/solver architecture, XStack governance, performance doctrine, agentic development doctrine, UX philosophy, packaging/distribution model, long-term scalability model, and forbidden behaviors.

Important old-v1 principles included:

- Domino is the deterministic universe engine in C89.
- Dominium is the game layer in C++98.
- Applications include Client, Server, Setup, and Launcher.
- XStack governs development, audit, verification, compatibility, performance, security, and remediation.
- All simulation systems reduce to Assemblies, Fields, Processes, Agents, and Law.
- Process-only mutation is mandatory.
- AuthorityContext is required before intent execution.
- LawProfile, ExperienceProfile, ParameterBundle, ScenarioSpec, MissionSpec, and BundleProfile define behavior/data surfaces.
- Determinism requires fixed-point authoritative math, named RNG streams, thread-count invariance, and replay-hash equivalence.
- Epistemics require TruthModel → PerceivedModel → RenderModel separation and no omniscient truth leakage.
- No runtime mode flags are allowed; behavior differences derive from LawProfile and data.
- Survival defaults are diegetic-first and minimal.
- MMO/galaxy-scale/SRZ-0 scaling is a long-term architectural direction, not a baseline proof.

The assistant acknowledged this as ground truth for later work in the chat.

### 2.2 Binding the old glossary

FACT: The user then pasted **Dominium — Canonical Glossary v1.0.0**. It defined canonical terms such as Account, Agent, AuthorityContext, AuditX, Canon, Capability, Client, Collapse, CompatX, Determinism, Domain, Engine, ExperienceProfile, Field, Game, Hardcore, LawProfile, Lens, Macro Capsule, MissionSpec, Observation Kernel, Pack, ParameterBundle, Process, Refusal Contract, RepoX, ScenarioSpec, SecureX, SessionSpec, TestX, TruthModel, UniverseIdentity, UniverseState, and many others.

The glossary also deprecated legacy mode-flag terms such as `survival_mode`, `creative_mode`, `hardcore_mode`, `spectator_mode`, `debug_mode`, `godmode`, and `sandbox`.

The assistant acknowledged the glossary as a terminology constraint layer.

### 2.3 Auditing the current GitHub repository against old v1

FACT: The user asked how the current GitHub repository `julesc013/dominium` aligned with the old contract and glossary. They asked specifically: “What do the docs say? What does the code do?”

The repository was inspected through the GitHub connector. Key files inspected or referenced included:

- `README.md`
- `docs/STATUS_NOW.md`
- `docs/architecture/ARCH0_CONSTITUTION.md`
- `docs/architecture/CANON_INDEX.md`
- `docs/canon/constitution_v1.md`
- `docs/canon/glossary_v1.md`
- `docs/ARCHITECTURE.md`
- `docs/XSTACK.md`
- `CMakeLists.txt`
- `client/core/session_pipeline.c`
- `client/core/session_stage_registry.c`
- `client/core/session_artifacts.h`
- `engine/include/domino/domain.h`
- `engine/include/domino/core/rng_streams.h`
- `engine/modules/core/rng_streams.c`
- `engine/modules/sim/sim.c`
- `engine/modules/world/d_world.c`
- `data/registries/survival_vertical_slice.json`
- `data/registries/process_requirements.json`
- `data/registries/experience_profiles.json`
- `data/registries/law_profiles.json`
- `schema/session/session_spec.schema`
- `schema/authority/authority_context.schema`
- `scripts/dev/gate.py`

The audit conclusion was:

- The repository strongly aligns with old v1 at the documentation/schema/registry/governance level.
- It partially aligns at implemented runtime-code level.
- The old v1 contract and glossary exist as current canonical repo files: `docs/canon/constitution_v1.md` and `docs/canon/glossary_v1.md`.
- The repo has a newer canon-index rule: prompts are not authoritative unless materialized as exactly one canonical document.
- The survival vertical slice exists structurally in data registries, but full runtime gameplay implementation was not proven.
- The session pipeline has real deterministic code and refusal handling.
- The engine has deterministic RNG and world/tile save-load/checksum scaffolding.
- Full agent gameplay loops, MMO distributed authority runtime, embodiment, and narrative/campaign systems were described as deferred in repo status docs.

### 2.4 Portability, modularity, extensibility, and future-proofing doctrine

FACT: The user then stated that code portability, modularity, extensibility, and reuse are very important. They wanted the code reusable for different games on Domino and for unrelated engine/game projects. They also wanted everything connected so code/data/files/directories can be replaced or rewritten in a future refactor. The user explicitly said the project should be developed like a proper game or OS, not a one-off indie project.

The answer developed a general doctrine:

```text
Stable contracts.
Replaceable implementations.
Deterministic behavior.
Portable projections.
No accidental authority from paths, tools, UIs, or prompts.
```

Important ideas discussed:

- Do not freeze every file. Stabilize contracts and semantic boundaries.
- Treat paths as storage, not identity.
- Introduce stability classes: frozen ABI, stable API, stable data contract, stable wire/replay contract, internal replaceable code, derived generated artifacts, and run-meta artifacts.
- Require replacement seams: every module should have a contract, version, owner, inputs, outputs, failure/refusal behavior, migration rule, tests, and dependency direction.
- Use negative architecture rules to prevent drift.
- Prove reuse with a second minimal Domino-based product.
- Keep public Domino APIs C-compatible and C89/C++98 parseable.
- Avoid exposing C++ classes across stable binary boundaries.
- Use versioned schemas, migration contracts, round-trip tests, and compatibility matrices.
- Keep runtime services from owning truth or Law.
- Keep `apps/` thin.
- Keep packs data-only unless a separate trust/capability contract exists.
- Use ownership-based directory roots rather than generic source buckets.

### 2.5 Preservation package creation

FACT: The user uploaded a preservation prompt in `Pasted text.txt` requesting a maximum-fidelity chat preservation package. The assistant generated a preservation report and files named with the prefix `Dominium_Canon_Portability_Audit__...`.

The generated files currently available in `/mnt/data` are:

- `Dominium_Canon_Portability_Audit__00_manifest.md`
- `Dominium_Canon_Portability_Audit__01_human_readable_report.md`
- `Dominium_Canon_Portability_Audit__02_context_transfer_packet.md`
- `Dominium_Canon_Portability_Audit__03_spec_sheet.yaml`
- `Dominium_Canon_Portability_Audit__04_registers.md`
- `Dominium_Canon_Portability_Audit__05_aggregator_packet.md`
- `Dominium_Canon_Portability_Audit__06_reader_brief.md`
- `Dominium_Canon_Portability_Audit__07_verification_and_audit.md`
- `Dominium_Canon_Portability_Audit__08_future_chat_bootstrap_prompt.md`
- `Dominium_Canon_Portability_Audit__09_in_chat_reader.md`
- `Dominium_Canon_Portability_Audit__handoff_package.zip`
- `Pasted text.txt`

FACT: The user then asked for an accompanying human-readable detailed summary/report of the entire conversation and to bundle everything into a single ZIP. This file is the accompanying report generated in response.

---

## 3. What was decided, what was only suggested, and what remains tentative

### 3.1 Decisions clearly established in the conversation

| ID | Decision / established direction | Status | Label |
|---|---|---|---|
| DECISION-A01 | Old v1 Constitution and Glossary are the comparison baseline for this chat. | Accepted for this chat | FACT |
| DECISION-A02 | Current repo authority is repo-materialized canon, not raw prompts. | Established by repo docs inspected | FACT |
| DECISION-A03 | Treat docs/registries as evidence of architectural intent, not runtime proof. | Adopted analysis principle | INFERENCE |
| DECISION-A04 | Stable contracts matter more than stable file paths. | Recommended and aligned with user goals | INFERENCE |
| DECISION-A05 | Ownership-based roots are preferable to generic `src/`/`source` roots for this project. | Recommended; supported by repo docs | INFERENCE / FACT for repo policy |
| DECISION-A06 | Future work should preserve semantic IDs during path moves. | Recommended as strong doctrine | INFERENCE |
| DECISION-A07 | A reuse proof via a second minimal Domino product would be valuable. | Recommended, not yet user-confirmed as task | INFERENCE |
| DECISION-A08 | Create and preserve a report package for later aggregation/spec-book work. | Explicit user request | FACT |

### 3.2 Suggestions not yet confirmed as formal project law

The following were assistant recommendations. They should not be treated as binding project decisions unless the user or repo canon later adopts them:

- Add an explicit public API/ABI inventory.
- Create a second minimal Domino-based product example.
- Define module descriptors for statically and dynamically linked modules.
- Add more formal versioning per surface: engine ABI, runtime service API, schema, save format, replay format, pack format, wire protocol, command contract, refusal contract, component matrix, release manifest.
- Add an API stability report tool.
- Convert all transitional debt into owner/path/semantic-ID/risk/verification queues.
- Use the proposed function-prefix discipline (`domino_*`, `d_*`, `dominium_*`, runtime prefixes, etc.).

### 3.3 Things explicitly deferred or not proven

- Full runtime survival gameplay loop proof.
- Full local build/test run of the repository.
- Current physical repo layout verification from a fresh checkout.
- Full API/ABI surface audit.
- Public release/package proof.
- Real second-product reuse proof.
- Full TestX/XStack run.
- Migration of remaining bad-root/transitional debt.
- Confirmation of whether the inspected old paths such as `client/core/session_pipeline.c` still physically exist or were aliases/historical references relative to the later `apps/` convergence docs.

---

## 4. What the repository audit found

### 4.1 Documentation and canon

FACT: The repository has canonical documents corresponding to the old v1 Constitution and Glossary. The repo’s canon-index document says that if a document is not listed as canonical, it is not binding, and that prompts themselves are execution artifacts rather than authority.

INFERENCE: This matters because it prevents future assistants from treating pasted chat prompts as stronger than the current repo files. For future work, old chat text should be used as context unless it has been materialized into canonical repo files.

### 4.2 Architecture docs

FACT: Current architecture docs describe Engine/Game/Client/Server/XStack boundaries, SessionSpec, AuthorityContext, UniverseIdentity/UniverseState separation, ExperienceProfile/LawProfile/ParameterBundle registries, session pipeline, Macro Capsule, Domain/Solver architecture, Truth/Perceived/Render separation, SRZ-0, determinism/replay, world representation, and worldgen.

INFERENCE: The architecture is highly documented and contract-heavy. The main risk is mistaking architectural density for implementation completeness.

### 4.3 Code implementation

FACT: The inspected code includes a real deterministic session pipeline and session-stage registry. It supports explicit stage transitions, refusal codes, artifact readiness checks, and stage logs.

FACT: The engine contains deterministic RNG stream support and a deterministic world/tile substrate with save/load/checksum behavior.

FACT: CMake enforces C90/C++98 standards, reads version files, performs boundary checks, disables build-time downloads by default, and exposes many quality/governance targets.

UNCERTAIN / UNVERIFIED: The full runtime Process/Law/Authority execution path was not exhaustively traced. Survival process IDs exist in registries, but concrete C/C++ handlers for every survival process were not proven in the inspected surface.

### 4.4 Survival vertical slice

FACT: The survival vertical slice registry contains the old v1 baseline fields and processes, including energy, hydration, exposure, health, alive status, environment temperature, daylight, need tick, exposure tick, consume item, gather resource, craft basic tool, build shelter, and death process.

INFERENCE: This shows strong structural alignment with old v1, but it remains largely declarative unless linked to runtime process execution and tests.

### 4.5 Current repo layout doctrine

FACT: Later repo docs and contracts define an ownership-root layout model and explicitly say old `src`/`source` proposals are historical or superseded. The active roots include `apps`, `engine`, `game`, `runtime`, `contracts`, `content`, `docs`, `tests`, `tools`, `scripts`, `cmake`, `external`, `release`, and `archive`.

FACT: The naming contract forbids generic source buckets such as `src`, `source`, `code`, `impl`, `common`, `shared`, and `misc` for new active paths.

INFERENCE: This is a good long-term structure for modularity because it assigns ownership rather than merely grouping implementation files.

---

## 5. Portability and modularity doctrine distilled

The conversation produced a durable design doctrine. The core principle is:

> A path answers who owns this. A file name answers what role this artifact plays. An ID answers what stable semantic object this is. A schema answers what shape and compatibility rules apply. A contract answers what behavior is allowed. A test answers how we know it still holds.

This doctrine has several practical consequences.

### 5.1 Stable contracts, replaceable implementations

Dominium should not aim to make every implementation permanent. It should make public contracts stable and explicit. Implementations should be rewritable behind those contracts.

Stable surfaces should include:

- public C ABI headers,
- schema IDs and schema versions,
- semantic IDs such as `process.*`, `law.*`, `lens.*`, and `pack.*`,
- save/replay formats,
- command/result/refusal protocols,
- wire protocols,
- package manifests,
- build/release manifests,
- migration rules,
- compatibility matrices.

Replaceable surfaces should include:

- internal engine algorithms,
- solver implementations,
- renderer backends,
- runtime adapters,
- product shells,
- UI implementations,
- tooling internals,
- generated-code internals.

### 5.2 Replacement seams

A component is replaceable only when it has:

- a clear owner,
- an explicit contract,
- a version,
- declared dependencies,
- declared inputs/outputs,
- deterministic failure/refusal behavior,
- tests/golden fixtures,
- migration rules,
- diagnostics and proof artifacts.

A directory alone is not a module. A module is an enforceable boundary.

### 5.3 Reuse proof

The strongest proposed test of reusability is a second minimal game/product on Domino. If a minimal non-Dominium product cannot be built without dragging in Dominium-specific LawProfiles, content, UI, or product assumptions, the engine is not cleanly reusable yet.

This remains a recommended future task, not a completed one.

### 5.4 Public API practice

The recommendation was to keep public Domino APIs C-compatible and C89/C++98 parseable:

- opaque handles,
- `struct_size` fields,
- explicit allocator ownership,
- no platform types in public engine headers,
- no global mutable state,
- deterministic error codes,
- fixed-width integer types,
- append-only extension where possible,
- no exposed C++ ABI across stable plugin/module boundaries.

### 5.5 Data and schema practice

Every schema/registry/manifest/save/replay/lockfile should declare:

- `schema_id`,
- `schema_version`,
- stability,
- canonical encoding,
- unknown-field policy,
- migration/refusal policy,
- golden fixtures,
- round-trip tests,
- compatibility matrix.

### 5.6 Runtime and apps practice

The recommended ownership rule is:

- `engine/` owns deterministic truth substrate.
- `game/` owns Law, process semantics, and domain implementation.
- `runtime/` owns platform/render/input/audio/network/storage/shell/diagnostics adapters.
- `apps/` owns thin product entrypoints and product composition only.
- `contracts/` owns machine-readable law.
- `content/` owns authored data/packs/profiles/assets.
- `tools/` owns developer and governance tooling.

Runtime may host, adapt, present, connect, persist, and diagnose. It must not own simulation truth or Law.

---

## 6. What was put off for later

The conversation intentionally did not attempt to do all work immediately. Deferred items include:

1. **Fresh repo checkout audit** — Needed to resolve current physical layout, active code paths, and potentially stale references.
2. **Full build/test verification** — Needed to prove CMake, CTest, XStack, RepoX/TestX/AuditX, and product binaries in the current environment.
3. **Runtime Process execution audit** — Needed to distinguish survival registry declarations from implemented processes.
4. **Public API/ABI inventory** — Needed before stable versioning promises can be made.
5. **Schema/save/replay compatibility audit** — Needed for backward compatibility claims.
6. **Second product reuse proof** — Needed to prove Domino can support a non-Dominium game cleanly.
7. **Remaining layout-debt migration** — Needed to retire bad roots and transitional exceptions safely.
8. **Function/file/schema naming audit** — Needed to determine whether current names are optimal or just transitional.
9. **Formal adoption of recommendations as repo law** — Needed before assistant recommendations become binding project rules.
10. **Master spec book aggregation** — This report is a source packet, not the final master spec book.

---

## 7. Open questions and verification queue

### Open questions

1. **What is the exact current physical repo layout at HEAD?**  
   Reason: earlier inspection fetched old paths while later docs say product roots moved under `apps/`.

2. **Which old v1 rules are fully implemented, partially implemented, only documented, or deferred?**  
   Reason: architecture and runtime maturity must not be conflated.

3. **Where is the complete LawProfile/AuthorityContext-gated Process execution path?**  
   Reason: Process-only mutation and Law-gated authority are central to the constitution.

4. **Are survival processes implemented as real runtime Process handlers?**  
   Reason: the survival vertical slice exists structurally, but runtime proof is needed.

5. **What are the stable public APIs/ABIs today?**  
   Reason: long-term portability requires a known public surface.

6. **Can a minimal second game use Domino without Dominium coupling?**  
   Reason: that is the clearest test of engine reuse.

7. **Which naming/layout recommendations should become formal repo law?**  
   Reason: assistant recommendations are not binding until adopted.

8. **Which generated artifacts are canonical, derived, or run-meta?**  
   Reason: reproducibility and governance depend on artifact classification.

### Verification queue

| ID | Item | Why it needs verification | Priority |
|---|---|---|---|
| VERIFY-A01 | Current physical repo tree | Resolve layout/path uncertainty | P0 |
| VERIFY-A02 | CMake configure/build status | Prove current build health | P0 |
| VERIFY-A03 | CTest/XStack/RepoX/TestX/AuditX status | Prove governance health | P0 |
| VERIFY-A04 | Runtime survival process implementation | Separate declaration from implementation | P1 |
| VERIFY-A05 | Public API/ABI inventory | Needed for stability/versioning plan | P1 |
| VERIFY-A06 | Save/replay compatibility surfaces | Needed for long-term backward compatibility | P1 |
| VERIFY-A07 | Pack/content trust enforcement | Needed for extensibility/security | P1 |
| VERIFY-A08 | Second Domino product proof | Needed for actual reuse proof | P2 |
| VERIFY-A09 | Naming and function-prefix audit | Needed for consistency and extensibility | P2 |
| VERIFY-A10 | Artifact-class audit | Needed for generated/canonical/run-meta correctness | P2 |

---

## 8. Artifacts included or referenced

### 8.1 Prior preservation package

The earlier package contains the first structured preservation pass. It includes a manifest, human-readable report, context transfer packet, YAML spec sheet, registers, aggregator packet, reader brief, verification/audit report, future-chat bootstrap prompt, and in-chat reader.

This new bundle includes those files as source material.

### 8.2 Uploaded preservation prompt

`Pasted text.txt` contains the user’s detailed instructions for maximum-fidelity chat preservation. It is included so the future reader can understand why the preservation package has its structure.

### 8.3 This accompanying report

This file summarizes the entire conversation in a more direct, narrative style and explains what was discussed, decided, suggested, deferred, and left open.

### 8.4 New bundle manifest

The new manifest records what files were included in the final ZIP, their purpose, size, and SHA-256 hash.

### 8.5 Final ZIP package

The final ZIP bundles the prior files, the uploaded prompt, this accompanying report, and the new manifest/checksum metadata.

---

## 9. Risks and future-assistant failure modes

### RISK-A01 — Treating architectural docs as runtime proof

A future assistant might say “Dominium implements X” when the repo only documents or declares X. Avoid this by classifying evidence as docs, schema, registry, code, tests, build, or runtime behavior.

### RISK-A02 — Treating assistant suggestions as user decisions

Several portability recommendations were assistant proposals. They should become project law only if the user or repo canon adopts them.

### RISK-A03 — Losing uncertainty about repo state

The repository can change. The prior GitHub inspection is time-bound and not equivalent to a fresh local checkout. Re-verify before modifying code.

### RISK-A04 — Recreating forbidden generic roots

Avoid `src/`, `source/`, `common/`, `shared/`, `misc`, `impl`, and status/era buckets unless a current contract explicitly allows them.

### RISK-A05 — Breaking semantic identity during file moves

Do not change process IDs, pack IDs, schema IDs, ABI IDs, product IDs, save IDs, or compatibility versions merely because storage paths change.

### RISK-A06 — Over-cleanup before proof

Mass moves or broad rewrites can break build, tests, imports, packaging, and compatibility. Use small gated migrations.

### RISK-A07 — Conflating Domino and Dominium

Domino should remain a reusable deterministic engine substrate. Dominium is one game/product layer on top. Keep that distinction strong.

### RISK-A08 — Accidental runtime dependency on tools

Tools may inspect and generate; runtime/product code must not depend on developer-only tooling.

### RISK-A09 — UI/runtime owning truth

Runtime and UI may project, present, and submit commands; they must not own simulation truth or decide Law.

### RISK-A10 — Expired uploads and missing files

Some previous uploads were reported expired. Future work should ask the user to re-upload any missing files needed for deeper analysis.

---

## 10. Recommended next-action sequence

1. **Open a fresh current repo audit task.**  
   Objective: verify physical tree, root exceptions, current active paths, and whether old `client/` paths remain.

2. **Run or inspect strict layout validators.**  
   Objective: compare actual tree against `contracts/repo/layout.contract.toml`, root allowlist, and layout exceptions.

3. **Create an implementation maturity matrix.**  
   Columns: docs, schema, registry, code, tests, build proof, runtime proof. Rows: determinism, authority, LawProfile, Process, survival, session, replay, packs, SRZ, XStack, packaging.

4. **Create public API/ABI inventory.**  
   Objective: identify what surfaces are stable, private, generated, transitional, or deprecated.

5. **Trace survival process execution.**  
   Objective: determine whether `process.need_tick`, `process.exposure_tick`, etc. are runtime-executable Processes or only registry entries.

6. **Design the second Domino product proof.**  
   Objective: prove engine reuse without Dominium coupling.

7. **Convert recommendations to formal task prompts.**  
   Objective: avoid ambiguous future work and preserve governance requirements.

8. **Only then start large refactors or feature expansion.**  
   Objective: preserve build/test/compatibility while improving structure.

---

## 11. What to preserve for the master spec book

This conversation should feed into these future spec-book chapters:

- Project identity and constitutional baseline.
- Glossary and terminology law.
- Evidence model: docs vs code vs tests vs runtime proof.
- Repository ownership layout.
- Naming and path identity doctrine.
- Stable contracts vs replaceable implementations.
- Public API/ABI policy.
- Schema, registry, save, replay, and pack compatibility.
- Runtime/app/game/engine boundary model.
- XStack governance and verification doctrine.
- Portability and second-product reuse proof.
- Migration/refactor rules.
- Risk and verification model.

Items that should become formal requirements if not already present:

- Path is storage, not identity.
- All stable surfaces require explicit versioning and compatibility rules.
- Every module needs a replacement seam.
- A second-product proof should be required before claiming engine reuse.
- No broad refactor without build/test/proof gates.
- Assistant suggestions cannot become canon without repo/user adoption.

Items that should remain background context unless adopted:

- Specific proposed function prefixes.
- Exact module descriptor sketch.
- Exact public C API sketch.
- Specific example-game ideas.
- External analogies to Linux, SQLite, NASA cFS, or SemVer.

---

## 12. Best questions to ask next

### Understanding

1. What is the difference between the old v1 Constitution and the current repo canon?
2. Which parts of the repo audit were proven by code, and which were only docs/registries?
3. What does “path is storage, not identity” mean for Dominium?
4. Why is an ownership-root layout better than a `src/` layout here?

### Decisions

5. Which portability recommendations should we promote into formal repo law?
6. Should we require a second-product proof before calling Domino reusable?
7. Should public Domino APIs be frozen as C ABI surfaces now or later?

### Tasks

8. Turn the next-action sequence into a Codex-ready task prompt.
9. Draft an implementation maturity matrix for current Dominium.
10. Create a repo audit checklist for layout, naming, API, schemas, and runtime proof.
11. Design the minimal second Domino-based game/product proof.

### Artifacts

12. Which file in the preservation package should be read first?
13. Which parts of this package should feed the master spec book?
14. Compare the prior human-readable report to this accompanying report and identify gaps.

### Verification

15. What current repo facts must be re-verified before coding?
16. How should we verify survival Process implementation?
17. How should we audit public API/ABI stability?

### Risk

18. What are the biggest ways a future assistant might misunderstand this conversation?
19. Which refactors are dangerous before build/test proof?
20. Which items are still assistant suggestions rather than user decisions?

---

## 13. Final package note

This accompanying report is meant to be read alongside the earlier preservation package. It does not replace the earlier structured registers and spec sheet; it provides a clearer narrative and a sharper explanation of what the conversation actually accomplished.

The final bundle includes both the earlier package files and this new report. Some older uploaded files are unavailable because they were reported expired. If those are needed, they must be uploaded again.
