# Accompanying Human-Readable Detailed Summary and Report

**Chat label:** Domino/Dominium Portability, Assurance, and Future-Proof Architecture  
**Date anchor:** 2026-05-27 Australia/Melbourne  
**Generated:** 2026-05-27 21:02:29 AEST  
**Source scope:** This report covers the visible current chat plus the generated preservation files currently available in `/mnt/data`. It does not claim access to hidden model reasoning, a full external repository, or other old chats unless explicitly labelled as PROJECT-CONTEXT.

---

## 1. Executive summary

This conversation was about turning Domino and Dominium from a one-off game project into a long-lived, reusable, portable, modular engine-and-product ecosystem. The user’s core requirement was not merely “clean code.” The user wanted code and data that can survive major rewrites, directory replacement, engine reuse, new games, new platforms, and future refactors without collapsing into project-specific coupling.

The conversation first addressed whether high-assurance standards such as DO-178B/C and adjacent security/supply-chain standards could inform Domino and Dominium. The answer was that such standards are useful as design inputs, but not as literal compliance targets. The proposed approach was a project-native assurance profile: standards-informed, but not certification cosplay. This became the proposed **Domino/Dominium Assurance Profile** concept, with internal integrity levels rather than aviation labels.

The discussion then moved into a broader architecture doctrine. The central idea was:

> **Stable public contracts; replaceable internals.**

This means Domino should expose durable, versioned, tested contracts at the boundaries that matter: public C APIs, save formats, pack formats, replay formats, schemas, protocol IDs, command/result APIs, error codes, capability IDs, and migration rules. It does **not** mean every internal function, file, or helper should be frozen. A future-proof system must be strict where external compatibility matters and flexible where internal redesign is valuable.

The conversation also identified the need for conformance tests, schema evolution rules, deterministic simulation boundaries, platform abstraction, render abstraction, transactional setup/update behavior, launcher separation, toolchain discipline, and a hierarchy between Domino as engine/platform and Dominium as one product built on that engine.

A later uploaded preservation prompt requested a maximum-fidelity preservation package for the chat. A full package was generated with ten files: manifest, human-readable report, context transfer packet, YAML spec sheet, registers, aggregator packet, reader brief, verification/audit file, future-chat bootstrap prompt, and in-chat reader. This accompanying report is now being added to that set and bundled into a consolidated ZIP.

The most important unresolved point is that the proposed architecture is still a **candidate doctrine**, not a completed repo migration. The actual repository was not inspected in this chat, and many assistant outputs are recommendations rather than user-ratified decisions. The next proper step is to inspect the repo, identify the real coupling points, decide which recommendations become canonical, and draft enforceable policies for public APIs, data evolution, module boundaries, and conformance tests.

---

## 2. Coverage and reliability check

| Field | Assessment |
|---|---|
| Apparent chat access | Partial-to-visible context only. The report covers what is visible in this chat and the generated files available in `/mnt/data`. |
| Repository access | No actual Domino/Dominium repository was inspected. |
| Uploaded files | Yes. The user uploaded a preservation/export prompt as `Pasted text.txt`. |
| Previously generated files | Yes. Ten preservation package files and one prior handoff ZIP existed before this companion report. |
| Current new files | This companion report, a consolidated bundle manifest, checksums, and a new complete ZIP. |
| Contains explicit user goals | Yes. Portability, modularity, extensibility, replaceability, future-proofing, OS-grade/game-engine-grade development, and preservation/export. |
| Contains assistant recommendations | Yes. DDAP/DIL, target directory tree, API rules, schema policy, tests, module contracts, and next actions. |
| Contains final decisions | Some explicit user priorities are clear; most technical architecture items remain recommendations until accepted by the user. |
| Staleness risk | Medium. Standards references and external claims should be verified before being placed in formal specs. |
| Extraction confidence | 4/5 for visible conversation and generated files; lower for anything outside visible context. |
| Safe for aggregation | Yes, with caveats. Keep FACT / INFERENCE / UNCERTAIN status and do not convert suggestions into ratified decisions. |

### Plain-language limitation statement

This report is reliable for explaining what was discussed in the visible chat. It is not proof that the real repository has the recommended structure, not proof that the user formally accepted every recommendation, and not a substitute for verifying the current official standards or inspecting actual code. Future aggregation should treat this as a design-intent and architecture-doctrine package, not as a completed implementation record.

---

## 3. Chronological story of the conversation

### 3.1 Standards and assurance question

The conversation began with the user presenting a long assessment of whether Eureka should borrow from DO-178B/C and related standards. The pasted assessment argued that the right approach is not full DO-178C compliance, but a DO-178C-inspired assurance layer for high-trust paths. It also corrected several overstatements about DO-178C, such as treating it as simply “stricter everywhere” or as a proof of correctness.

The user then asked whether something similar should be used for Domino and Dominium, and whether it was wise.

The assistant’s answer was that it is wise only if used as **standards-informed design discipline**, not as a literal certification regime. The recommended doctrine was that Domino/Dominium should borrow from DO-178C-style traceability and verification, NIST SSDF secure-development practices, OWASP ASVS web/API security verification, SLSA build provenance, SPDX/SBOM metadata, and functional-safety thinking where the project creates trust, authority, persistence, execution, or external impact.

This led to the proposed **DDAP v0 — Domino/Dominium Assurance Profile**. It defined internal levels such as DIL-0 exploratory through DIL-5 external-impacting. It also separated Domino as an engine/toolchain substrate from Dominium as the product/game/content ecosystem using that substrate.

### 3.2 User’s deeper portability/modularity requirement

The user then clarified that the core concern was broader than assurance standards. They wanted all code to be portable, modular, extensible, reusable, replaceable, and future-proof. They wanted the codebase to support different games on the same Domino engine and also reuse modules in entirely different engine or game projects.

The user also emphasized that code, data, files, and directories should be replaceable or rewriteable during future refactors. The project should be developed like a proper game or OS, not like a one-off indie project.

The assistant responded with the main architectural doctrine:

> **Stable outside, replaceable inside.**

This was framed as the central rule for the project. Public contracts, save/pack/replay formats, command protocols, schemas, and tool outputs should be stable and versioned. Private implementation details should remain free to change.

### 3.3 Architecture, naming, directory, API, and data-evolution recommendations

The assistant then proposed a much broader set of practices.

The most important architectural recommendation was to structure the repo around ownership and replacement boundaries. Domino should remain reusable and product-independent. Dominium should use Domino through public contracts and should not become entangled with Domino internals. The proposed tree included `include/`, `contracts/`, `source/domino/`, `source/dominium/`, `data/`, `state/`, `tests/`, `tools/`, `scripts/`, `docs/`, `examples/`, `external/`, `cmake/`, `release/`, and `dist/`.

The answer also recommended clear layering: contracts first, public headers next, Domino core and subsystem implementations below that, then Dominium product code. It emphasized dependency direction and suggested layer-checking scripts to prevent accidental reverse dependencies.

The API guidance focused on C-compatible public boundaries: opaque handles, explicit `size` and `version` fields in public structs, project-owned integer types, explicit allocator ownership, no platform types in core APIs, no exposed private structs, no bitfields in public ABI, no C++ ABI across plugin boundaries, and no hidden global singleton state.

Naming guidance recommended prefixes such as `dom_`, `dcore_`, `dsys_`, `dgfx_`, `dui_`, `dsim_`, `dpack_`, `dnet_`, `dreplay_`, `dser_`, and `dtlv_`. It warned against names such as `utils.c`, `helpers.c`, `misc.c`, `manager.c`, `new_render.c`, and `legacy_render.c`.

Data-format guidance emphasized that persistent formats must include magic values, format IDs, versions, writer version, minimum reader version, endianness, schema/profile IDs, chunk tables or TLV registries, checksums, optional signatures, migrations, unknown-field policies, and reserved tag registries. The key rule was that no tag, enum value, error code, protocol opcode, save chunk ID, or capability ID should ever be reused after release.

### 3.4 Testing, determinism, tooling, and OS-grade discipline

The conversation then moved into testing and maintainability. The assistant argued that every stable boundary needs conformance tests. A boundary is not really replaceable unless another implementation can satisfy the same public API, fixtures, golden outputs, invalid/malformed cases, and migration tests.

The answer also emphasized deterministic simulation: fixed tick rates, named RNG streams, no wall-clock calls in simulation, deterministic serialization order, deterministic replay logs, and clear separation between truth state, perceived state, view model, render commands, and backend presentation.

Setup, launcher, tools, and UI were separated conceptually:

- **Setup** should be transactional and auditable: plan, stage, verify, commit, receipt, rollback.
- **Launcher** should orchestrate products, instances, profiles, packs, diagnostics, and launching, without containing gameplay logic.
- **Tools** should consume the same public contracts as runtime code.
- **UI** should submit commands and receive results rather than directly mutating authoritative game state.

### 3.5 Preservation package generation

The user then uploaded a preservation/export prompt requesting a maximum-fidelity preservation package for this chat. The prompt required a human-readable report, structured registers, spec sheet, aggregator packet, self-audit, file exports, and a ZIP.

The assistant created the package with the inferred label:

> **Domino/Dominium Portability, Assurance, and Future-Proof Architecture**

The generated files were:

1. `00_manifest.md`
2. `01_human_readable_report.md`
3. `02_context_transfer_packet.md`
4. `03_spec_sheet.yaml`
5. `04_registers.md`
6. `05_aggregator_packet.md`
7. `06_reader_brief.md`
8. `07_verification_and_audit.md`
9. `08_future_chat_bootstrap_prompt.md`
10. `09_in_chat_reader.md`
11. `handoff_package.zip`

The user then asked for an accompanying human-readable detailed summary/report of the entire conversation, including what was discussed, decided, deferred, and any missing considerations, and asked for everything to be bundled into one ZIP. This current report and bundle fulfill that request.

---

## 4. What was actually decided versus only proposed

A key preservation issue is separating user decisions from assistant recommendations.

### 4.1 Clear user-stated requirements

The user explicitly cared about:

- code portability;
- modularity;
- extensibility;
- reuse across multiple Domino-engine games;
- reuse across completely different engine or game projects;
- ability to replace or rewrite code, data, files, and directories during major refactors;
- developing the project like a proper game/platform/OS-style system rather than a one-off indie project;
- future-proofing;
- backward compatibility;
- directory structure, file names, function names, schemas, protocols, and APIs;
- broad/deep reasoning about what was missing;
- preserving the chat and generated outputs for future aggregation and a master Project Spec Book.

These are FACTS from the visible user messages.

### 4.2 Strong assistant recommendations not yet fully ratified

The following were assistant recommendations. They should not be treated as final canon unless the user later accepts them:

- Create **DDAP v0** as a Domino/Dominium Assurance Profile.
- Use internal **DIL-0 through DIL-5** integrity levels.
- Adopt the doctrine **stable public contracts, replaceable internals**.
- Use `source/domino/` for reusable engine/platform code and `source/dominium/` for product/game code.
- Add `contracts/`, conformance tests, migration tests, fuzz tests, and validators.
- Use C89-style public ABI boundaries where appropriate.
- Use opaque handles and `size`/`version` public structs.
- Define registries for tags, IDs, error codes, capabilities, opcodes, and subsystem IDs.
- Make save/pack/replay/protocol formats explicitly versioned and migration-tested.
- Build setup as transactional and launcher as orchestration only.
- Enforce architecture using layer-check scripts, public-header checks, schema-evolution checks, and traceability checks.

These recommendations are highly aligned with the user’s stated goals, but they remain provisional until accepted and adapted to the actual repository.

### 4.3 Items explicitly deferred or not completed

The following were put off for later or remain unresolved:

- Inspecting the actual Domino/Dominium repository.
- Verifying the proposed directory tree against real files.
- Deciding which proposed architecture policies become project canon.
- Verifying current official details of external standards before including them in formal docs.
- Choosing final naming conventions.
- Creating actual `docs/architecture/*.md` policy files.
- Creating actual `contracts/` schemas and registries.
- Implementing layer-check, schema-evolution, conformance, fuzz, and replay test scripts.
- Deciding where C89, C++98, or other language constraints apply exactly.
- Defining the real platform matrix.
- Defining the first conformance-test pilot.
- Determining how much backward compatibility to promise at each stage of project maturity.
- Aggregating this chat with other old chats into a master Project Spec Book.

---

## 5. Main architecture doctrine preserved from the conversation

### 5.1 Stable public contracts; replaceable internals

This is the most important architecture doctrine. It means the project should deliberately distinguish between public contracts and private implementation. Public contracts should be rare, well-designed, versioned, documented, tested, and hard to break. Internals should be easy to delete and rewrite.

A practical replacement test was proposed:

> Can we delete this directory and reimplement it against only public contracts, then pass the same conformance tests and load the same data?

If yes, the system is modular. If no, coupling has leaked through private assumptions.

### 5.2 Domino as reusable platform, Dominium as product

Domino should own reusable engine/platform concepts: deterministic simulation, public ABI boundaries, platform abstraction, render command abstraction, data/pack/replay systems, mod/package validation, and conformance targets.

Dominium should own product-specific game rules, content, UI composition, launcher policy, setup/install plans, server/client/headless modes, and game-specific tooling.

The boundary matters because a reusable engine dies if its flagship game infects its internals with product-specific assumptions.

### 5.3 Contracts before implementation

The conversation emphasized that real modularity is created by contracts, not folders. A folder is not a module unless it has a purpose, owner, public API, private implementation, dependency declaration, conformance tests, fixtures, replacement criteria, versioning policy, diagnostics/error policy, and migration policy if relevant.

### 5.4 Data compatibility is equal to code compatibility

The chat made clear that saves, packs, replays, protocols, and content schemas are long-term project assets. Bad data evolution can destroy portability even if the code is clean.

The preserved rule is:

> No released ID is reused. Removed IDs are reserved forever. Old data gets migration tests.

### 5.5 Testing is the enforcement mechanism

The conversation treated tests not merely as bug-finding tools but as architectural enforcement. The recommended test classes included unit tests, contract tests, conformance tests, golden tests, replay tests, migration tests, fuzz tests, fault injection, platform tests, layer tests, build-matrix tests, performance budgets, and security tests.

### 5.6 Assurance should scale by risk

The standards discussion produced a risk-scaled approach. Ordinary UI, lore, concept art, and experiments should not carry heavy assurance burdens. Saves, packs, replay, deterministic state, installers, updaters, signed releases, mod loading, multiplayer authority, and external-impacting features should receive stronger controls.

---

## 6. What “big systems” contributed to the reasoning

The conversation used several large-system lessons as analogies:

- **Linux-like lesson:** stable external interfaces, flexible internals.
- **SQLite-like lesson:** trust comes from aggressive testing of observable behavior, malformed inputs, failure modes, and old data.
- **Protocol Buffers / FlatBuffers-like lesson:** schema evolution rules must be established early and IDs must not be reused.
- **Google-like lesson:** small, reviewable changes are better than huge uncontrolled refactors.
- **LLVM-like lesson:** large codebases need local style discipline and avoid unrelated mass churn.
- **DO-178C-like lesson:** traceability, verification evidence, and independent review are valuable for high-trust paths, but aviation certification itself is not the goal.
- **NIST SSDF / OWASP ASVS / SLSA / SPDX-like lesson:** security, web/API verification, build provenance, and SBOM/component metadata are useful where relevant.

These were not presented as external compliance obligations. They were used as design inspiration.

---

## 7. Directory structure and naming conclusions

The assistant proposed a target repo structure with major roots such as:

```text
include/
contracts/
source/domino/
source/dominium/
data/
state/
tests/
tools/
scripts/
docs/
examples/
external/
cmake/
release/
dist/
```

The most important structural point was not the exact names. It was the separation of stable contracts, reusable engine code, product-specific game code, data, tools, tests, and documentation.

The naming recommendations emphasized ownership and role. Names like `utils.c`, `helpers.c`, `misc.c`, and `manager.c` were discouraged because they hide responsibility and usually become dumping grounds. More explicit names like `d_tlv_reader.c`, `d_pack_validate.c`, `d_replay_verify.c`, `d_gfx_command_buffer.c`, and `d_sys_win32_window.c` were proposed.

Function naming should be consistent and subsystem-oriented, such as:

```text
dpack_manifest_parse
dpack_manifest_validate
dpack_manifest_write
dreplay_log_open
dreplay_log_append
dgfx_command_buffer_begin
dgfx_command_buffer_push_rect
```

The open issue is whether these exact prefixes and names should become canon. That requires repo inspection and user acceptance.

---

## 8. API and ABI guidance preserved

The conversation strongly emphasized public API discipline:

- use opaque handles;
- use explicit result codes;
- include `size`, `version`, and reserved fields in public structs;
- define project-owned primitive types;
- avoid exposing platform headers in core public APIs;
- avoid public bitfields;
- avoid compiler-dependent struct layout;
- avoid STL/C++ ABI across plugin/runtime boundaries;
- avoid exceptions/RTTI crossing engine boundaries;
- clarify allocator ownership;
- avoid global singleton state;
- label APIs as experimental, stable, deprecated, reserved, internal, or removed.

This matters because portability across compilers, OSes, language bindings, plugin boundaries, and future rewrites requires stricter discipline than ordinary application code.

---

## 9. Data, protocol, save, pack, and replay rules preserved

The conversation treated persistent formats as first-class public contracts. Every persistent format should include:

- magic identifier;
- format ID;
- major/minor version;
- writer version;
- minimum reader version;
- endianness;
- schema/profile ID;
- chunk table or TLV registry;
- checksum or hash;
- optional signature;
- migration path;
- unknown-field policy;
- reserved tag registry.

It explicitly warned against raw `fwrite`/`fread` of in-memory structs as a save format because that bakes in padding, endian, alignment, compiler layout, and evolution assumptions.

The proposed long-term policy is that released IDs are never reused and old data gets fixtures and migration tests.

---

## 10. Testing, validation, and conformance preserved

The conversation said that every stable boundary should have:

- public spec;
- valid fixtures;
- invalid fixtures;
- malformed fixtures;
- golden outputs;
- migration cases;
- fuzz cases;
- roundtrip tests;
- deterministic replay tests where relevant;
- conformance tests that a replacement implementation must pass.

High-trust paths such as save/load, pack/mod loading, replay, network protocol, installer/updater, authority/capability systems, and content promotion were identified as needing stronger validation.

This is one of the biggest future-proofing points: without conformance tests, “modular” APIs are only promises.

---

## 11. Setup, launcher, tools, UI, and command boundaries preserved

The conversation separated operational roles:

- **Setup** modifies installed system state and should be transactional: plan, stage, verify, commit, receipt, rollback.
- **Launcher** is orchestration: discover products, select profiles, validate installs, resolve packs/mods, start the game, export diagnostics.
- **Tools** should use the same public contracts as runtime code.
- **UI** should not mutate authoritative state directly; it should send commands and receive results, refusals, diagnostics, progress, and view models.

This supports multiple frontends: CLI, TUI, rendered GUI, native wrapper, headless JSON, server admin, launcher, setup.

---

## 12. What was put off for later

The conversation deferred implementation. The major deferred work includes:

1. **Repo boundary audit** — inspect actual directories, headers, dependencies, naming, and data formats.
2. **Canonical architecture decision** — decide what parts of the proposed doctrine become binding.
3. **Public API policy** — draft and adopt rules for public headers, ABI compatibility, ownership, versioning, and lifecycle labels.
4. **Data evolution policy** — draft and adopt rules for saves, packs, replays, protocols, schemas, registries, and migrations.
5. **DDAP/DIL acceptance** — decide whether the assurance profile and integrity levels become project canon.
6. **Conformance test pilot** — choose one subsystem and prove the replacement-contract model.
7. **Layer checker** — implement dependency direction enforcement.
8. **Schema/ID registry checker** — enforce non-reuse and reservation of released IDs.
9. **Standards verification** — verify official sources before including external standards in the formal spec book.
10. **Cross-chat aggregation** — combine this report with other old-chat reports into a master Project Spec Book.

---

## 13. What the generated preservation package already contains

Before this companion report, the package already contained:

| File | Role |
|---|---|
| `00_manifest.md` | Package inventory and caveats. |
| `01_human_readable_report.md` | Main preservation report for the chat. |
| `02_context_transfer_packet.md` | Handoff packet for a future chat. |
| `03_spec_sheet.yaml` | YAML-style aggregation/spec sheet. |
| `04_registers.md` | Workstream, decision, task, constraint, preference, artifact, risk, verification, timeline, and spec contribution registers. |
| `05_aggregator_packet.md` | Compact cross-chat aggregation packet. |
| `06_reader_brief.md` | Short human reference. |
| `07_verification_and_audit.md` | Self-audit and verification queue. |
| `08_future_chat_bootstrap_prompt.md` | Prompt for continuing in a new chat. |
| `09_in_chat_reader.md` | Navigation guide and question menu. |
| `handoff_package.zip` | The prior ZIP bundle containing files 00–09. |

This new report adds a more direct narrative accompaniment that explicitly answers: what did we talk about, what did we decide, what did we do, what did we put off, and what should not be lost.

---

## 14. Most important carry-forward items

### 14.1 Most important idea

The project should be treated as a contract-governed engine platform, not just a collection of game files.

### 14.2 Most important architecture law

Domino must not depend on Dominium. Dominium should consume Domino through stable public contracts.

### 14.3 Most important compatibility law

Released IDs, tags, opcodes, capability IDs, save chunks, and error codes must not be reused.

### 14.4 Most important testing law

A boundary is not stable until it has conformance tests and fixtures.

### 14.5 Most important process law

Heavy assurance should apply only where risk justifies it. Do not burden ordinary creative iteration with certification-style process.

### 14.6 Most important unresolved issue

The actual repository must be inspected before declaring the proposed structure “best” or canonical.

---

## 15. Recommended next action sequence

1. **Read the main human-readable report and this companion report.**  
   Purpose: ensure the doctrine is understood before formalizing anything.

2. **Inspect the actual repo.**  
   Purpose: identify where existing structure, naming, headers, data formats, tools, and tests match or contradict the proposed architecture.

3. **Produce a boundary audit.**  
   Output: list of current public contracts, accidental public contracts, private internals, coupling violations, data formats, and migration risks.

4. **Accept/revise/reject DDAP and DIL.**  
   Output: clear decision on assurance profile and integrity levels.

5. **Draft `public-api-policy.md`.**  
   Output: rules for public headers, ABI, lifecycle labels, ownership, allocator rules, and versioning.

6. **Draft `data-evolution-policy.md`.**  
   Output: rules for save/pack/replay/protocol/schema IDs, migrations, unknown fields, and reserved values.

7. **Pick one conformance-test pilot.**  
   Recommended candidates: pack validator, save reader, replay verifier, or render command buffer.

8. **Create enforcement scripts.**  
   Output: layer checker, public header checker, schema evolution checker, reserved ID checker, and traceability checker.

9. **Aggregate with other old-chat reports.**  
   Output: master Project Spec Book draft with conflicts and duplicates identified.

---

## 16. Risks and failure modes

### Risk: treating recommendations as ratified decisions

Many architecture items are strong recommendations but not yet explicit user decisions. A future assistant should not say “the project decided X” unless the user ratifies it.

### Risk: freezing internals too early

The project needs stable public contracts, not frozen implementation details. Over-freezing private APIs would make the system harder to improve.

### Risk: delaying data compatibility too long

Save, pack, replay, protocol, and schema formats become hard to fix after release. A compatibility policy should be drafted early.

### Risk: over-applying assurance

DDAP/DIL should not turn creative iteration into bureaucracy. Heavy controls belong on high-trust paths.

### Risk: under-testing contracts

Without conformance fixtures and golden/malformed/migration tests, the claim of replaceability is weak.

### Risk: stale standards claims

External standards and official references should be verified before being merged into a formal spec book.

### Risk: repository mismatch

The proposed tree may not match the current repo. It should be used as a target model, not as proof of current state.

---

## 17. Decisions and statuses

| Item | Status | Notes |
|---|---|---|
| User wants portability/modularity/extensibility/reuse | FACT / user-stated | Strongly established. |
| User wants replaceability of files/directories/code/data | FACT / user-stated | Strongly established. |
| User wants OS-grade/proper-game-grade discipline | FACT / user-stated | Strongly established. |
| Use standards as design inputs, not compliance targets | Assistant recommendation; likely aligned | Needs user ratification for canon. |
| Create DDAP/DIL | Assistant recommendation | Open decision. |
| Stable public contracts, replaceable internals | Assistant recommendation; central doctrine | Should be confirmed by user. |
| Domino reusable, Dominium product-specific | Assistant recommendation; highly aligned | Should be confirmed by user. |
| Proposed directory structure | Candidate design | Needs repo inspection. |
| API/ABI rules | Candidate policy | Needs policy draft and acceptance. |
| Data-evolution rules | Candidate policy | High priority to formalize. |
| Preservation package generation | Completed | Files and ZIP generated. |
| Companion report and consolidated bundle | Completed by this task | See new ZIP and manifest. |

---

## 18. Open questions

1. Which assistant recommendations should become formal Domino/Dominium canon?
2. Should DDAP and DIL levels be adopted, renamed, simplified, or rejected?
3. What is the actual current repo structure?
4. Which APIs already exist and which are accidental/public/private?
5. Which data formats already exist and need migration policy?
6. What platforms are genuinely target platforms versus aspirational future targets?
7. Which language constraints are mandatory in each layer?
8. What is the first subsystem to receive conformance tests?
9. What is the minimum backward-compatibility promise before first public release?
10. How should this chat’s package merge with other project preservation packages?

---

## 19. Best follow-up questions

The best next questions to ask in this chat are:

1. Which recommendations from this package should become formal Domino/Dominium canon?
2. Can you turn the stable-contracts doctrine into a concise architecture constitution?
3. Can you draft `docs/architecture/public-api-policy.md`?
4. Can you draft `docs/architecture/data-evolution-policy.md`?
5. Can you make a repo audit checklist for checking whether our current structure violates these rules?
6. Can you convert the 20 architecture laws into CI-enforceable checks?
7. Can you design the first conformance-test pilot for the pack validator?
8. Can you design the first conformance-test pilot for the save format?
9. Can you make a decision matrix for DDAP/DIL adoption?
10. Can you prepare this package for merger into a master Project Spec Book?

---

## 20. Final summary

This conversation established the high-level architecture doctrine for Domino/Dominium as a serious, reusable, long-lived engine/game ecosystem. It started with a question about whether high-assurance standards should influence the project and expanded into a much broader set of engineering practices for portability, modularity, extensibility, replaceability, future-proofing, and compatibility.

The most important concept is stable public contracts with replaceable internals. The project should make deliberate promises at durable boundaries—public APIs, schemas, data formats, protocols, IDs, packs, saves, replays, and tool outputs—while keeping internal code and directory implementation free to evolve.

The conversation produced a candidate architecture with Domino as reusable engine/platform and Dominium as one product built on top. It proposed internal assurance levels, strict public API rules, data-evolution policies, conformance tests, deterministic simulation boundaries, transactional setup, launcher separation, toolchain discipline, and structured preservation artifacts.

What has been completed is a preservation and handoff package. What remains is formal adoption, repo inspection, policy drafting, test implementation, standards verification, and cross-chat aggregation.

The safest immediate next action is to inspect the real repository and produce a boundary audit. After that, the user should decide which recommendations become canon and begin drafting the public API and data evolution policies.
