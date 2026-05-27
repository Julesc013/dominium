# Aggregator Packet — Dominium Advanced Simulation and Infrastructure Architecture

## 1. Packet Metadata

* Chat label: Dominium Advanced Simulation and Infrastructure Architecture
* Date anchor: 2026-05-27 Australia/Melbourne
* Source scope: THIS CHAT ONLY; project-context items labelled.
* Coverage: full based on visible chat and previous Context Transfer Packet.
* Confidence: 4/5.
* Staleness risk: low for internal architecture, medium for future external standards/software facts.
* Merge priority: high.
* Main limitations: no repo files inspected; no code implemented; other refactor plan unavailable; assistant proposals are not automatically user decisions.

## 2. Ultra-Condensed Carry-Forward Capsule

[FACT] This chat centered on the Dominium/Domino deterministic engine, specifically how to extend an already constrained simulation/game architecture into a robust, grid-agnostic, user-facing infrastructure construction system. The user began with a detailed advanced simulation starter prompt for Path D, requiring the assistant to act as a senior simulation systems architect. The hard constraints were explicit: Domino Engine is ISO C89, Dominium UI/tools are a portable C++98 subset, the engine must avoid OS APIs and platform-dependent behavior, deterministic paths must use fixed-point Q formats rather than floats, and all gameplay semantics must be data-driven rather than hardcoded.

[FACT] The first major output was a top-level advanced simulation architecture covering heat, power, fluids, hydrology, atmospheres, vehicles, structural loads/destruction, and a mod-extensible physics framework. The design proposed generic `dsim_*` domains, fixed-point units, deterministic tick ordering, replay/checksum hooks, and content-driven material/fluid/electrical/structural properties. No code was written and no repository files were inspected; all proposed file paths and module names remain unverified until checked against the actual repo.

[FACT] The user then shifted focus from physics to gameplay mechanics and end-user construction features. The design direction became: engine primitives remain generic; Dominium/content/rules provide semantics. UI actions should emit deterministic commands, not mutate state directly. Gameplay systems should operate through data-driven rules and stable command application, preserving replay and lockstep multiplayer.

[FACT] The largest design thread concerned building real-world-like infrastructure. The user asked how overlapping splines, lines, and runs can combine realistically: dual gauge rail, electric lines beside rail/roads, streetlights, overhead/third-rail electrification, undersea cables and pipelines, footpaths and roads. The proposed answer was to replace independent overlapping splines with canonical corridor bundles: one corridor alignment can host multiple content-defined cross-section slots and attachments over station ranges. This was then optimized into an authoring-versus-runtime model: editable corridors and junctions compile into deterministic microsegments, occupancy bitsets, connectivity graphs, and chunk-aligned spatial indices. A small deterministic packing VM was proposed for mod-extensible cross-section rules.

[FACT] The user broadened the requirement to “build basically anything seen in real life,” including complex highways, interchanges, overpasses, subway systems, rail yards, substations, and power plants. The resulting design uses corridors, parametric junctions, vertical layers, structure carriers, and modular facilities. Users should sketch an alignment, classify it with a profile, constrain it through rules such as slope/radius/clearance, refine it, and optionally detail it. Complex nodes are handled through junction archetypes; bridges, tunnels, viaducts, cuttings, and retaining walls are generated carriers rather than hand-placed beam-by-beam.

[FACT] Signage and markings were then treated as a generalized DECOR subsystem. Road markings are parametric decals; signs are props; automatic placement comes from rule packs; manual placement uses overrides, pinning, suppression, and semantic keys. The model was then generalized beyond splines to buildings, terrain, interiors, props, and rooms through Host Surfaces + Anchor Frames. The preferred placement mode is host-relative and parametric; freeform world placement is allowed but must be quantized and is second-class for edit stability.

[FACT] A key late decision was the explicit answer to whether users are stuck to grids: no. The engine should be grid-agnostic. Users should be able to build at arbitrary position, rotation, inclination, and along full 3D curves. Grids exist only as optional Dominium UI snapping aids. Determinism comes from fixed-point math, quantized command inputs, stable IDs, ordered iteration, fixed iteration counts, and parametric anchoring—not from grid restriction.

[FACT] The chat produced two major implementation-planning artifacts: a nine-step Codex prompt plan to implement the required arbitrary-placement changes, and a pasteable prompt for an existing GPT-5.2 refactor/optimization chat instructing it to merge these requirements into its existing plan without restarting. [UNCERTAIN / UNVERIFIED] It is unknown whether either prompt has been executed elsewhere.

[FACT] The prior maximum-fidelity Context Transfer Packet was already detailed. This final package repairs and normalizes it into stable IDs, registers, a YAML spec sheet, aggregator packet, reader brief, audit file, manifest, and ZIP archive. The highest-priority carry-forward facts are: preserve C89/C++98/fixed-point/determinism; never reintroduce global grid lock; keep BUILD/TRANS/STRUCT/DECOR/SIM boundaries clear; treat assistant designs as unimplemented until verified; and merge these requirements into any existing refactor plan rather than forking the architecture.

## 3. Top Carry-Forward Items

| Priority | Item | Type | Related ID | Why it matters | Label | Confidence |
|---|---|---|---|---|---|---|
| 1 | Engine must be grid-agnostic; grids are optional UI snapping aids. | Requirement | DECISION-15 / WORKSTREAM-10 | Core arbitrary placement goal. | INFERENCE | High |
| 2 | C89 engine, C++98 UI/tools, fixed-point deterministic math. | Constraint | DECISION-01..04 | Hard code rules. | FACT | High |
| 3 | No hardcoded gameplay semantics; content defines meaning. | Constraint | DECISION-05 | Mod/data-driven engine. | FACT | High |
| 4 | Corridor bundles + slots replace independent overlapping splines. | Architecture | DECISION-08 / WORKSTREAM-03 | Realistic co-location. | INFERENCE | Medium-High |
| 5 | Host Surfaces + Anchor Frames generalize placement. | Architecture | DECISION-13 / WORKSTREAM-07 | Buildings/interiors/terrain/props support. | INFERENCE | Medium-High |
| 6 | DECOR visual-only unless promoted. | Boundary | DECISION-14 | Performance and layering. | INFERENCE | Medium-High |
| 7 | Authoring state separate from compiled runtime caches. | Data model | DECISION-10 / DECISION-16 | Performance and replay. | INFERENCE | Medium-High |
| 8 | Use nine Codex prompts only after repo verification. | Implementation plan | ARTIFACT-11 / TASK-01 | Avoids invalid paths/assumptions. | FACT | High |

## 4. Workstream Summaries

### WORKSTREAM-01 — Advanced deterministic simulation architecture

* Objective: Architect heat, power, fluids, hydrology, atmosphere, vehicles, structural loads, and mod-extensible physics for Domino.
* Current state: High-level architecture produced as text; no code verified or written.
* Desired end state: Formal subsystem specs, C89 fixed-point data models, deterministic solvers, TLV schemas, serialization, replay, checksum hooks.
* Priority: High
* Decisions: DECISION-01, DECISION-03, DECISION-04, DECISION-05, DECISION-20
* Tasks: none specific
* Constraints: C89/C++98/fixed-point/data-driven/deterministic constraints apply.
* Artifacts: see artifact ledger.
* Risks: see risk register.
* Open questions: QUESTION-03
* Next action: verify dependencies and convert to formal spec or implementation prompt.

### WORKSTREAM-02 — Gameplay mechanics and end-user feature layering

* Objective: Define how gameplay mechanics live above generic engine primitives.
* Current state: Engine/game boundary and command/rules model proposed.
* Desired end state: Deterministic gameplay rules runtime with command schemas, validation, replay, and mod/content integration.
* Priority: High
* Decisions: DECISION-01, DECISION-02, DECISION-03, DECISION-05, DECISION-06
* Tasks: TASK-11
* Constraints: C89/C++98/fixed-point/data-driven/deterministic constraints apply.
* Artifacts: see artifact ledger.
* Risks: see risk register.
* Open questions: none specific
* Next action: verify dependencies and convert to formal spec or implementation prompt.

### WORKSTREAM-03 — Corridor overlap and co-location model

* Objective: Allow overlapping splines/lines/runs to combine realistically via shared corridor bundles.
* Current state: Corridor + slots + attachments design proposed.
* Desired end state: TRANS supports dual gauge rails, road/rail/utilities, electrification, footpaths, pipelines, and undersea routes without independent spline conflicts.
* Priority: High
* Decisions: DECISION-01, DECISION-03, DECISION-05, DECISION-08, DECISION-20
* Tasks: TASK-06, TASK-07
* Constraints: C89/C++98/fixed-point/data-driven/deterministic constraints apply.
* Artifacts: see artifact ledger.
* Risks: see risk register.
* Open questions: none specific
* Next action: verify dependencies and convert to formal spec or implementation prompt.

### WORKSTREAM-04 — Extensible performant corridor runtime

* Objective: Make corridor overlap/packing scalable, mod-extensible, deterministic, and cache-friendly.
* Current state: Packing VM, compiled microsegments, spatial indices, dirty flags, capabilities, and hot/cold split proposed.
* Desired end state: Incrementally compiled TRANS runtime with bounded deterministic rebuilds and mod-defined packing behavior.
* Priority: High
* Decisions: DECISION-01, DECISION-03, DECISION-05, DECISION-09, DECISION-10
* Tasks: TASK-06, TASK-07, TASK-08, TASK-13
* Constraints: C89/C++98/fixed-point/data-driven/deterministic constraints apply.
* Artifacts: see artifact ledger.
* Risks: see risk register.
* Open questions: QUESTION-06, QUESTION-07
* Next action: verify dependencies and convert to formal spec or implementation prompt.

### WORKSTREAM-05 — Build-anything real-world infrastructure authoring

* Objective: Let users build highways, interchanges, overpasses, subways, rail yards, substations, power plants, and dense facilities intuitively.
* Current state: Corridors + junctions + layers + modules + structure carriers design proposed.
* Desired end state: Tools for sketch/classify/constrain/refine/detail with parametric junctions, modular facilities, and deterministic compilation.
* Priority: High
* Decisions: DECISION-01, DECISION-03, DECISION-05, DECISION-11, DECISION-20
* Tasks: TASK-15, TASK-16
* Constraints: C89/C++98/fixed-point/data-driven/deterministic constraints apply.
* Artifacts: see artifact ledger.
* Risks: see risk register.
* Open questions: QUESTION-09, QUESTION-10, QUESTION-11, QUESTION-12
* Next action: verify dependencies and convert to formal spec or implementation prompt.

### WORKSTREAM-06 — Signage and road markings

* Objective: Support automatic and manual placement of signs, markings, decals, and related props.
* Current state: DECOR system with generated baseline, manual overrides, semantic keys, lane stations, approach contexts, and tiles proposed.
* Desired end state: Rule-generated and manually editable signage/marking system with regional standards as content packs.
* Priority: Medium-High
* Decisions: DECISION-01, DECISION-03, DECISION-05, DECISION-12, DECISION-14
* Tasks: TASK-10, TASK-17, TASK-18
* Constraints: C89/C++98/fixed-point/data-driven/deterministic constraints apply.
* Artifacts: see artifact ledger.
* Risks: see risk register.
* Open questions: QUESTION-13, QUESTION-14, QUESTION-15
* Next action: verify dependencies and convert to formal spec or implementation prompt.

### WORKSTREAM-07 — General host/anchor placement for buildings, terrain, interiors, and props

* Objective: Generalize placement beyond splines to arbitrary hosts.
* Current state: Host Surfaces + Anchor Frames architecture proposed.
* Desired end state: Terrain, structures, corridors, props, and rooms expose deterministic anchors; placements use host-relative parametric refs with freeform fallback.
* Priority: High
* Decisions: DECISION-01, DECISION-03, DECISION-05, DECISION-13, DECISION-14
* Tasks: TASK-09, TASK-10
* Constraints: C89/C++98/fixed-point/data-driven/deterministic constraints apply.
* Artifacts: see artifact ledger.
* Risks: see risk register.
* Open questions: QUESTION-08
* Next action: verify dependencies and convert to formal spec or implementation prompt.

### WORKSTREAM-08 — System linkage map

* Objective: Identify systems the placement/decor/building stack must link into.
* Current state: Linkage map produced across RES, ENV, BUILD, TRANS, STRUCT, SIM, JOB, AGENT, UI/tools, rendering, save/load, replay/MP, ownership, permissions, localization.
* Desired end state: Formal event/dependency/dirty-propagation graph and read/write boundaries.
* Priority: Medium-High
* Decisions: DECISION-01, DECISION-03, DECISION-05, DECISION-14, DECISION-20
* Tasks: TASK-18, TASK-19
* Constraints: C89/C++98/fixed-point/data-driven/deterministic constraints apply.
* Artifacts: see artifact ledger.
* Risks: see risk register.
* Open questions: QUESTION-14, QUESTION-16
* Next action: verify dependencies and convert to formal spec or implementation prompt.

### WORKSTREAM-09 — Unified BUILD / TRANS / STRUCT / DECOR / SIM architecture

* Objective: Summarize and stabilize the full planned building/structure/spline/etc system.
* Current state: Unified architecture summary produced.
* Desired end state: Formal spec defining ownership, APIs, mutation permissions, and compiled/source-of-truth lifecycle.
* Priority: High
* Decisions: DECISION-01, DECISION-03, DECISION-05, DECISION-10, DECISION-20
* Tasks: none specific
* Constraints: C89/C++98/fixed-point/data-driven/deterministic constraints apply.
* Artifacts: see artifact ledger.
* Risks: see risk register.
* Open questions: QUESTION-09
* Next action: verify dependencies and convert to formal spec or implementation prompt.

### WORKSTREAM-10 — Arbitrary placement / no grid lock

* Objective: Ensure construction works at arbitrary position, rotation, inclination, and full 3D curvature.
* Current state: Explicit design commitment made: engine grid-agnostic; grids are optional UI snapping only.
* Desired end state: Fixed-point pose/frame math, quantized placement commands, local parametric placement, and UI snap stack that does not impose grids.
* Priority: Highest
* Decisions: DECISION-01, DECISION-03, DECISION-04, DECISION-05, DECISION-15
* Tasks: TASK-03, TASK-04, TASK-05, TASK-06, TASK-09
* Constraints: C89/C++98/fixed-point/data-driven/deterministic constraints apply.
* Artifacts: see artifact ledger.
* Risks: see risk register.
* Open questions: QUESTION-03, QUESTION-04, QUESTION-05, QUESTION-16
* Next action: verify dependencies and convert to formal spec or implementation prompt.

### WORKSTREAM-11 — Codex implementation prompt plan

* Objective: Turn architecture into staged implementation prompts.
* Current state: Nine-prompt plan produced.
* Desired end state: Repo-specific Codex work orders adjusted after verifying actual files and existing code.
* Priority: High
* Decisions: DECISION-01, DECISION-02, DECISION-03, DECISION-04, DECISION-05
* Tasks: TASK-01, TASK-03, TASK-04, TASK-11, TASK-13
* Constraints: C89/C++98/fixed-point/data-driven/deterministic constraints apply.
* Artifacts: see artifact ledger.
* Risks: see risk register.
* Open questions: QUESTION-01, QUESTION-04
* Next action: verify dependencies and convert to formal spec or implementation prompt.

### WORKSTREAM-12 — Existing GPT-5.2 refactor plan integration

* Objective: Produce prompt to merge this chat's requirements into an existing refactor/optimization plan.
* Current state: Pasteable merge prompt produced.
* Desired end state: Other chat produces delta plan, updated subsystem table, implementation sequence, and regression checklist.
* Priority: High
* Decisions: DECISION-01, DECISION-03, DECISION-05, DECISION-19, DECISION-20
* Tasks: TASK-02
* Constraints: C89/C++98/fixed-point/data-driven/deterministic constraints apply.
* Artifacts: see artifact ledger.
* Risks: see risk register.
* Open questions: QUESTION-02
* Next action: verify dependencies and convert to formal spec or implementation prompt.

### WORKSTREAM-13 — Context transfer and report packaging

* Objective: Preserve this chat as a downloadable, shareable, reusable report package.
* Current state: Maximum-fidelity context transfer packet existed; this final package normalizes and exports it.
* Desired end state: Markdown/YAML/ZIP package safe for later aggregation and project spec construction.
* Priority: High
* Decisions: DECISION-01, DECISION-03, DECISION-05, DECISION-20
* Tasks: TASK-20
* Constraints: C89/C++98/fixed-point/data-driven/deterministic constraints apply.
* Artifacts: see artifact ledger.
* Risks: see risk register.
* Open questions: none specific
* Next action: verify dependencies and convert to formal spec or implementation prompt.

## 5. Registers for Merge

### Decision Register
| ID | Decision | Status | Label |
|---|---|---|---|
| DECISION-01 | Domino Engine core must remain ISO C89. | user-stated hard requirement | FACT |
| DECISION-02 | Dominium UI/tools must remain portable C++98 subset. | user-stated hard requirement | FACT |
| DECISION-03 | No OS APIs are allowed inside engine code. | user-stated hard requirement | FACT |
| DECISION-04 | Deterministic paths must avoid floats and use fixed-point Q formats. | user-stated hard requirement | FACT |
| DECISION-05 | Engine must not hardcode gameplay semantics; all real meanings are content-driven. | user-stated hard requirement | FACT |
| DECISION-06 | Gameplay mechanics should be implemented as deterministic commands plus data/rules above generic engine primitives. | assistant-proposed, not contradicted | INFERENCE |
| DECISION-07 | Engine owns generic primitives; Dominium owns gameplay semantics, UI, tools, and official content/rules. | assistant-proposed, not contradicted | INFERENCE |
| DECISION-08 | Overlapping infrastructure should merge into corridor bundles with slots rather than exist as competing independent splines. | assistant-proposed, not contradicted | INFERENCE |
| DECISION-09 | Cross-section and packing rules should be content-defined and compiled to a deterministic small VM. | assistant-proposed, not contradicted | INFERENCE |
| DECISION-10 | Corridors should have authoring representation separate from compiled microsegment runtime representation. | assistant-proposed, not contradicted | INFERENCE |
| DECISION-11 | Complex infrastructure should be authored through corridors, junctions, layers, modules, and facilities rather than hand-placed micro-objects. | assistant-proposed, not contradicted | INFERENCE |
| DECISION-12 | Signage and markings should be DECOR outputs: parametric decals/props generated by rules with manual override layers. | assistant-proposed, not contradicted | INFERENCE |
| DECISION-13 | Placement should generalize to all hosts via Host Surfaces + Anchor Frames. | assistant-proposed, not contradicted | INFERENCE |
| DECISION-14 | DECOR is visual-only unless explicitly promoted into a STRUCT/TRANS device. | assistant-proposed, not contradicted | INFERENCE |
| DECISION-15 | Engine should be grid-agnostic; grids are optional UI snapping aids only. | assistant-proposed explicit answer, not contradicted | INFERENCE |
| DECISION-16 | Determinism should come from fixed-point math, quantized commands, stable IDs, ordered iteration, fixed iterations, and parametric anchoring—not grids. | assistant-proposed, not contradicted | INFERENCE |
| DECISION-17 | Performance strategy should use hot/cold split, dirty flags, deterministic budgets, and chunk-aligned spatial indices. | assistant-proposed, not contradicted | INFERENCE |
| DECISION-18 | Implementation should be staged through nine Codex prompts covering specs, math, TRANS, STRUCT, DECOR, commands, UI, performance, and docs. | assistant-proposed plan | FACT |
| DECISION-19 | Existing GPT-5.2 refactor plan should be amended via delta, not restarted or forked. | user-requested direction embedded in generated prompt | FACT |
| DECISION-20 | No repository code or files were implemented in this chat before final package generation. | observed fact | FACT |

### Task Register
| ID | Task | Priority | Related workstream | Label |
|---|---|---|---|---|
| TASK-01 | Verify actual repository structure and existing module names before applying proposed paths. | High | WORKSTREAM-11 | UNCERTAIN / UNVERIFIED |
| TASK-02 | Compare this chat's requirements against the existing GPT-5.2 refactor/optimization plan. | High | WORKSTREAM-12 | FACT |
| TASK-03 | Create formal arbitrary placement and quantization spec. | High | WORKSTREAM-10, WORKSTREAM-11 | INFERENCE |
| TASK-04 | Choose and implement deterministic pose/frame math representation. | High | WORKSTREAM-10, WORKSTREAM-11 | UNCERTAIN / UNVERIFIED |
| TASK-05 | Audit existing engine for global grid assumptions. | High | WORKSTREAM-10 | UNCERTAIN / UNVERIFIED |
| TASK-06 | Implement or specify TRANS full 3D corridors with z-profile, optional roll/cant, and microsegment frames. | High | WORKSTREAM-03, WORKSTREAM-04, WORKSTREAM-10 | INFERENCE |
| TASK-07 | Define cross-section slots and attachment TLV schemas. | High | WORKSTREAM-03, WORKSTREAM-04 | INFERENCE |
| TASK-08 | Design deterministic cross-section packing VM. | Medium-High | WORKSTREAM-04 | INFERENCE |
| TASK-09 | Implement or specify STRUCT arbitrary orientation, local frames, surface graphs, and anchors. | High | WORKSTREAM-07, WORKSTREAM-10 | INFERENCE |
| TASK-10 | Implement or specify DECOR host/anchor placement and tile compilation. | High | WORKSTREAM-06, WORKSTREAM-07 | INFERENCE |
| TASK-11 | Define deterministic TLV command schemas for placement/editing. | High | WORKSTREAM-02, WORKSTREAM-10, WORKSTREAM-11 | INFERENCE |
| TASK-12 | Refactor Dominium UI tools so grids are optional snapping sources only. | Medium-High | WORKSTREAM-10 | INFERENCE |
| TASK-13 | Implement performance hardening: hot/cold split, dirty queues, compile budgets, spatial indices. | Medium-High | WORKSTREAM-04, WORKSTREAM-11 | INFERENCE |
| TASK-14 | Update docs, invariants checklist, and migration notes. | High | WORKSTREAM-11 | INFERENCE |
| TASK-15 | Define parametric junction archetype system. | Medium | WORKSTREAM-05 | INFERENCE |
| TASK-16 | Define modular facility system for substations, plants, and industrial complexes. | Medium | WORKSTREAM-05 | INFERENCE |
| TASK-17 | Define signage/marking rulesets and semantic override keys. | Medium | WORKSTREAM-06 | INFERENCE |
| TASK-18 | Define promotion boundary from decor to devices. | Medium | WORKSTREAM-06, WORKSTREAM-08 | INFERENCE |
| TASK-19 | Define replay/checksum contracts for source state versus caches. | High | WORKSTREAM-08, WORKSTREAM-10 | INFERENCE |
| TASK-20 | Store and use this final package during future aggregation. | High | WORKSTREAM-13 | FACT |

### Constraint Register
| ID | Constraint | Type | Hard/soft | Label |
|---|---|---|---|---|
| CONSTRAINT-01 | Domino Engine core must use ISO C89. | Language | Hard | FACT |
| CONSTRAINT-02 | Dominium UI/tools must use portable C++98 subset. | Language | Hard | FACT |
| CONSTRAINT-03 | No OS APIs inside engine code. | Layering/portability | Hard | FACT |
| CONSTRAINT-04 | No floats where determinism matters; use fixed-point Q formats. | Determinism/math | Hard | FACT |
| CONSTRAINT-05 | No platform-dependent behavior. | Determinism/portability | Hard | FACT |
| CONSTRAINT-06 | No hardcoded game semantics; all semantics data-driven. | Architecture/content | Hard | FACT |
| CONSTRAINT-07 | TLV-versioned content/data/commands. | Persistence/schema | Hard | FACT |
| CONSTRAINT-08 | Deterministic scheduler, replay, checksum, and lockstep multiplayer must remain intact. | Runtime/networking | Hard | FACT |
| CONSTRAINT-09 | Engine must be grid-agnostic; grids are optional UI snapping only. | Placement | Hard design requirement | INFERENCE |
| CONSTRAINT-10 | Parametric host-relative placement is preferred over world-space baking. | Placement/data model | Strong design constraint | INFERENCE |
| CONSTRAINT-11 | Freeform placement is allowed but must be quantized. | Placement/determinism | Hard for deterministic paths | INFERENCE |
| CONSTRAINT-12 | Authoring state must be separate from compiled runtime caches. | Performance/data ownership | Strong design constraint | INFERENCE |
| CONSTRAINT-13 | No tolerance-based solvers or unbounded convergence in deterministic paths; use fixed iteration/bounded work. | Determinism/performance | Hard design requirement | INFERENCE |
| CONSTRAINT-14 | Stable IDs and ordered iteration are required everywhere relevant. | Determinism | Hard | INFERENCE |
| CONSTRAINT-15 | DECOR is visual-only unless promoted to a device. | Layering/performance | Strong design constraint | INFERENCE |
| CONSTRAINT-16 | Content-defined cross-sections, rules, standards, and prototypes drive semantics. | Modding/data-driven | Hard design constraint | FACT |
| CONSTRAINT-17 | Compiled geometry/connectivity/decor tiles are caches, not source of truth. | Persistence/data model | Strong design constraint | INFERENCE |
| CONSTRAINT-18 | External/current facts, APIs, products, prices, laws, schedules, and software versions require future verification. | Evidence/staleness | Hard for future factual claims | FACT |
| CONSTRAINT-19 | This report covers this chat only; project-level context must be labelled. | Source scope | Hard | FACT |
| CONSTRAINT-20 | Future package output must preserve artifacts, prompts, rejected options, rationale, and open questions. | Documentation/output | Hard | FACT |

### Open Questions Register
| ID | Question / issue | Priority | Related workstream | Label |
|---|---|---|---|---|
| QUESTION-01 | What is the actual repository structure and current module naming? | High | WORKSTREAM-11 | UNCERTAIN / UNVERIFIED |
| QUESTION-02 | What does the existing GPT-5.2 refactor/optimization plan contain? | High | WORKSTREAM-12 | UNCERTAIN / UNVERIFIED |
| QUESTION-03 | Which exact Q formats should be used for each quantity? | High | WORKSTREAM-01, WORKSTREAM-10 | UNCERTAIN / UNVERIFIED |
| QUESTION-04 | Which deterministic orientation representation should be used? | High | WORKSTREAM-10, WORKSTREAM-11 | UNCERTAIN / UNVERIFIED |
| QUESTION-05 | Does existing code assume a global grid? | High | WORKSTREAM-10 | UNCERTAIN / UNVERIFIED |
| QUESTION-06 | What microsegment length or segmentation policy should TRANS use? | Medium-High | WORKSTREAM-04 | UNCERTAIN / UNVERIFIED |
| QUESTION-07 | What should the packing VM instruction set include? | Medium-High | WORKSTREAM-04 | UNCERTAIN / UNVERIFIED |
| QUESTION-08 | How are arbitrary imported meshes handled? | Medium | WORKSTREAM-07 | UNCERTAIN / UNVERIFIED |
| QUESTION-09 | How are bridge/tunnel/viaduct/cut/fill carriers owned between TRANS and STRUCT? | Medium-High | WORKSTREAM-05, WORKSTREAM-09 | UNCERTAIN / UNVERIFIED |
| QUESTION-10 | How does auto-grade choose bridge/tunnel/cut/fill? | Medium | WORKSTREAM-05 | UNCERTAIN / UNVERIFIED |
| QUESTION-11 | How expressive should junction archetypes be? | Medium | WORKSTREAM-05 | UNCERTAIN / UNVERIFIED |
| QUESTION-12 | What is the facility/module system for substations and power plants? | Medium | WORKSTREAM-05 | UNCERTAIN / UNVERIFIED |
| QUESTION-13 | How exactly do decor semantic keys and overrides work? | Medium | WORKSTREAM-06 | UNCERTAIN / UNVERIFIED |
| QUESTION-14 | Which signage/marking/decor items affect AI or simulation? | Medium | WORKSTREAM-06, WORKSTREAM-08 | UNCERTAIN / UNVERIFIED |
| QUESTION-15 | How should localization and glyph coverage for signs be handled? | Low-Medium | WORKSTREAM-06 | UNCERTAIN / UNVERIFIED |
| QUESTION-16 | What checksum and serialization state should include caches versus source state? | High | WORKSTREAM-08, WORKSTREAM-10 | UNCERTAIN / UNVERIFIED |

### Artifact Ledger
| ID | Artifact / file / prompt / output | Type | Status | Carry forward? | Label |
|---|---|---|---|---|---|
| ARTIFACT-01 | Advanced Simulation Architecture response | Text plan | Created in chat | Yes | FACT |
| ARTIFACT-02 | Gameplay Mechanics Architecture response | Text plan | Created in chat | Yes | FACT |
| ARTIFACT-03 | Corridor Bundle / Slots response | Text plan | Created in chat | Yes | FACT |
| ARTIFACT-04 | Extensible Performant Corridor response | Text plan | Created in chat | Yes | FACT |
| ARTIFACT-05 | Build Anything Infrastructure response | Text plan | Created in chat | Yes | FACT |
| ARTIFACT-06 | Signage and Road Markings response | Text plan | Created in chat | Yes | FACT |
| ARTIFACT-07 | Universal Host/Anchor Placement response | Text plan | Created in chat | Yes | FACT |
| ARTIFACT-08 | System Linkage response | Text plan | Created in chat | Yes | FACT |
| ARTIFACT-09 | Full BUILD/STRUCT/TRANS/DECOR System Summary | Text plan | Created in chat | Yes | FACT |
| ARTIFACT-10 | Arbitrary Placement / No Grid Lock response | Text plan | Created in chat | Yes | FACT |
| ARTIFACT-11 | Codex Prompt Plan | Prompt plan | Created in chat; not executed here | Yes | FACT |
| ARTIFACT-12 | Existing GPT-5.2 Refactor Merge Prompt | Copy-paste prompt | Created in chat; downstream use unknown | Yes | FACT |
| ARTIFACT-13 | Maximum-fidelity Context Transfer Packet | Context transfer document in chat text | Created before this packaging request | Yes | FACT |
| ARTIFACT-14 | Final downloadable report package | Markdown/YAML/ZIP files | Created by this response | Yes | FACT |

### Risk Register
| ID | Risk / failure mode | Severity | Mitigation | Related workstream | Label |
|---|---|---|---|---|---|
| RISK-01 | Future assistant treats proposed architecture as implemented code. | High | Verify repo and mark all proposals as unimplemented unless confirmed. | All | INFERENCE |
| RISK-02 | Subsystem boundaries collapse between BUILD, TRANS, STRUCT, DECOR, and SIM. | High | Use responsibility table and mutation permissions in specs. | WORKSTREAM-09 | INFERENCE |
| RISK-03 | Global grid dependency reintroduced for convenience. | High | Audit grid assumptions and keep grids UI-only. | WORKSTREAM-10 | INFERENCE |
| RISK-04 | Gameplay semantics hardcoded into engine. | High | Require RES/content prototypes and rule packs for semantics. | All | INFERENCE |
| RISK-05 | Codex emits C99/C++11+ or uses floats in deterministic code. | High | Put language/math constraints in every prompt and run code review. | WORKSTREAM-11 | INFERENCE |
| RISK-06 | Unordered containers or iteration order enter authoritative state updates. | High | Stable ID ordering and deterministic traversal requirements. | All | INFERENCE |
| RISK-07 | Signed integer overflow or implementation-defined behavior. | High | Fixed-point math spec, checked ranges, deterministic overflow policy. | WORKSTREAM-01, WORKSTREAM-10 | INFERENCE |
| RISK-08 | Tolerance-based geometry comparisons or solver convergence. | High | Use quantized thresholds and fixed iteration counts. | WORKSTREAM-04, WORKSTREAM-10 | INFERENCE |
| RISK-09 | Compiled caches serialized as authoritative state. | Medium-High | Serialize source-of-truth only; rebuild caches deterministically. | WORKSTREAM-09 | INFERENCE |
| RISK-10 | Rule VM becomes too expressive or nondeterministic. | Medium-High | Keep VM integer-only, bounded, versioned, and minimal. | WORKSTREAM-04, WORKSTREAM-06 | INFERENCE |
| RISK-11 | Anchor graph becomes too dense or unstable. | Medium | Generate anchors parametrically and preserve stable IDs. | WORKSTREAM-07 | INFERENCE |
| RISK-12 | DECOR accidentally becomes simulation-authoritative. | Medium-High | Promotion boundary: visual-only unless promoted to STRUCT/TRANS device. | WORKSTREAM-06, WORKSTREAM-08 | INFERENCE |
| RISK-13 | User manual signage/marking edits are lost during auto-regeneration. | Medium | Semantic keys, pin/suppress, manual override layer. | WORKSTREAM-06 | INFERENCE |
| RISK-14 | Complex infrastructure UX becomes full CAD rather than game-intuitive. | Medium-High | Use sketch/classify/constrain/refine/detail plus parametric archetypes. | WORKSTREAM-05 | INFERENCE |
| RISK-15 | Other refactor chat duplicates or conflicts with this plan. | High | Use generated merge prompt and perform delta review. | WORKSTREAM-12 | INFERENCE |
| RISK-16 | Future aggregation loses tentative status and converts brainstorms into decisions. | High | Preserve labels and confidence fields in aggregator packet and YAML. | WORKSTREAM-13 | INFERENCE |
| RISK-17 | External/current facts become stale. | Medium | Verify external facts before future use; this chat mainly contains internal architecture. | WORKSTREAM-13 | FACT |
| RISK-18 | Repo-specific paths in prompt plan are copied blindly. | Medium-High | Treat paths as proposed and verify repo before applying. | WORKSTREAM-11 | UNCERTAIN / UNVERIFIED |

### Verification Queue
| ID | Item requiring verification | Priority | Related workstream | Label |
|---|---|---|---|---|
| VERIFY-01 | Actual repository structure and file paths. | High | WORKSTREAM-11 | UNCERTAIN / UNVERIFIED |
| VERIFY-02 | Existing GPT-5.2 refactor/optimization plan contents. | High | WORKSTREAM-12 | UNCERTAIN / UNVERIFIED |
| VERIFY-03 | Current code's grid dependencies. | High | WORKSTREAM-10 | UNCERTAIN / UNVERIFIED |
| VERIFY-04 | Existing fixed-point math and unit conventions. | High | WORKSTREAM-01, WORKSTREAM-10 | UNCERTAIN / UNVERIFIED |
| VERIFY-05 | Existing command/replay/TLV systems. | High | WORKSTREAM-02, WORKSTREAM-11 | UNCERTAIN / UNVERIFIED |
| VERIFY-06 | Current TRANS/STRUCT/BUILD boundaries. | High | WORKSTREAM-09 | UNCERTAIN / UNVERIFIED |
| VERIFY-07 | Feasibility and cost of microsegment representation. | Medium-High | WORKSTREAM-04 | UNCERTAIN / UNVERIFIED |
| VERIFY-08 | Deterministic orientation representation choice. | High | WORKSTREAM-10 | UNCERTAIN / UNVERIFIED |
| VERIFY-09 | Checksum rules for source state versus caches. | High | WORKSTREAM-08, WORKSTREAM-10 | UNCERTAIN / UNVERIFIED |
| VERIFY-10 | Junction/facility archetype requirements from actual gameplay design. | Medium | WORKSTREAM-05 | UNCERTAIN / UNVERIFIED |
| VERIFY-11 | Regional signage/marking standards content scope. | Medium | WORKSTREAM-06 | UNCERTAIN / UNVERIFIED |
| VERIFY-12 | Whether Codex prompts have been executed elsewhere. | Medium-High | WORKSTREAM-11 | UNCERTAIN / UNVERIFIED |
| VERIFY-13 | Whether the existing refactor merge prompt was pasted and answered. | Medium-High | WORKSTREAM-12 | UNCERTAIN / UNVERIFIED |
| VERIFY-14 | This package's completeness after download. | Immediate | WORKSTREAM-13 | FACT |

## 6. Possible Cross-Chat Duplicates

- Advanced simulation architecture may duplicate earlier/later simulation planning chats.
- BUILD/TRANS/STRUCT/JOB/AGENT taxonomy may duplicate project foundation chats.
- Refactor/optimization plan may overlap with the existing GPT-5.2 refactor chat.
- Fixed-point/Q-format decisions may overlap with engine math chats.
- Signage/marking/decor may overlap with rendering/UI/content pipeline chats.
- Arbitrary placement/no-grid requirement may overlap with editor/tooling chats.

## 7. Possible Cross-Chat Conflicts

- Other chats may assume grid-based placement; this chat rejects global grid lock.
- Other chats may assign bridge/tunnel ownership differently between TRANS and STRUCT.
- Other chats may have different fixed-point units or orientation math.
- Other chats may use different names for BUILD/TRANS/STRUCT/DECOR responsibilities.
- Other chats may treat signage as traffic-authoritative by default; this chat says visual-only unless promoted.

## 8. Spec Book Integration Guidance

Feed this chat into chapters on deterministic engine constraints, simulation architecture, gameplay command model, TRANS corridors/junctions, STRUCT buildings/anchors, DECOR signage/markings, arbitrary placement, performance/incremental compilation, and implementation roadmap. Make hard user constraints formal requirements. Treat assistant-proposed implementation details as candidates requiring confirmation or repo verification.

## 9. Aggregator Warnings

Do not merge this with another plan by discarding uncertainty labels. Do not treat proposed file paths as real. Do not collapse grid-free placement into ordinary grid snapping. Do not treat the generated Codex prompts as executed. Do not summarize the whole project from this one chat.
