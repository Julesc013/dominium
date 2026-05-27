# Companion Human-Readable Detailed Summary and Report

**Chat label:** Domino/Dominium Engine Baseline, Architecture, and Feasibility  
**Date anchor:** 2026-05-27 Australia/Melbourne  
**Source scope:** This chat only, plus files generated or uploaded inside this chat.  
**Purpose:** This companion report sits beside the full handoff package. It is written as a readable “what happened and what matters” account rather than a register dump.

---

## 1. Executive Summary

This conversation was a long architecture, feasibility, implementation-readiness, and preservation discussion for the **Domino engine** and **Dominium game** project. The central question was how to build a deterministic, portable, modular, reusable simulation engine that can support a deeply ambitious game: full-scale solar systems and planets, sparse construction and destruction, civilization-building, terraforming, machine and megaproject design, modding, multiplayer persistence, fog of war, and eventually CAD-like authoring.

The most important outcome was a correction of project sequencing. The project has a **real deterministic substrate**: there are engine and game build targets, execution/scheduler pieces, pack/registry/capability infrastructure, AppShell/product surfaces, early construction/fabrication modules, and strong architecture/governance doctrine. However, it does **not** yet have a finished playable game engine. The client still advertises that gameplay/world/package/provider/module runtime surfaces are unavailable and that `support_claim_playable=false`. The local playtest path is a target recipe rather than one fully hardened command. Therefore the immediate project priority is not CAD, destruction, economy, agents, MMO sharding, or broad gameplay. The immediate priority is **Milestone 0: make the baseline path honest**.

Milestone 0 means one canonical repo-local playtest command should create/materialize a session, boot it, start local loopback authority, run deterministic client/server smoke or baseline behavior, emit proof/replay/hash/compat artifacts, and pass strict validation. The known blockers discussed were: Python server/runtime circular import, server CLI forwarding/import path problems, `session_create -> session_boot` not passing for the intended baseline bundle, the implementation-vs-guidance seam around `bundle.base.lab` versus the MVP baseline bundle, missing/invalid time-anchor policy registry, and strict local playtest validation reporting blocked proof status.

After Milestone 0, the first true game slice should be tiny: one deterministic accepted/refused build action, one deterministic removal/damage action, one replay/hash proof, one minimal projection/rendering path, and one pack-driven object/action. This sequence was chosen because trying to “finish the engine” first would become an infinite engine project, while trying to build the full game before baseline hardening would build on unstable ground.

The conversation also produced several long-term architecture principles. Domino should be the reusable deterministic simulation substrate; Dominium should be one game/product layer built on it. The engine should define mechanisms, not Dominium-specific meanings. Game content and rules should be data/pack/registry/capability driven where possible. Client and renderer should project state and issue intents, not mutate truth. Server/domain authority should own authoritative multiplayer truth. Silent fallback is forbidden; explicit degradation and refusal are required.

For building and destroying, the conversation concluded that the game should be **CAD-capable but not CAD-required**. Ordinary players should be able to build through templates, snapping, intent-based actions, accessible controls, or low-performance interfaces. Advanced players and developers can use a full CAD-like suite. All authoring surfaces should compile into the same canonical design artifact. The user explicitly does not want normal gameplay based on recipes, tech trees, or experience levels, though those systems should remain available for modders and alternate game modes through packs, law, profiles, and capabilities.

For geometry, the recommended direction was a hybrid rather than voxel-first: use CSG/feature graphs for editing and procedural authoring, B-Rep for canonical validated solids, NURBS/B-spline faces for advanced curved surfaces, meshes for derived rendering/collision, and sparse voxels/SDFs/fields only where they are the right tool, such as terrain, mining, fluids, debris, craters, and damage approximation.

For the full-scale universe dream, the key feasibility doctrine is: **full scale, yes; full fidelity everywhere, no**. Domino should use hierarchical domains, orbits on rails, planet tiles, sparse terrain/terraforming overlays, collapsed civilization capsules, fog-of-war epistemics, active-fidelity budgets, domain-sharded multiplayer authority, and proof-carrying client compute. Unreal can help with rendering/editor/client presentation if desired, but it should not be treated as the authoritative deterministic simulation substrate.

---

## 2. What We Actually Discussed

### 2.1 Project identity: Domino, Dominium, and XStack

The conversation began with the user asking for a total project description by reading the docs and the GitHub repo. The project was framed as a stack:

- **Domino engine:** deterministic mechanisms, execution, storage, domains, replay, capabilities, law gates, pack/runtime primitives, rendering/platform abstraction.
- **Dominium game:** rules and meanings built on top of the engine: construction, physical systems, life, agents, economy, governance, survival, war, knowledge, scale, and eventually CAD-like design and full-scale universe gameplay.
- **Client/server/product shells:** presentation, intent projection, multiplayer authority, launcher/setup/tools, AppShell surfaces.
- **XStack/governance:** RepoX/TestX/AuditX/CompatX-like validation, proof, and drift control.

This distinction became one of the most important pieces of the chat. The engine should be reusable for other games or even other engine projects. That means Dominium-specific concepts should not leak into the Domino substrate.

### 2.2 Historical engine lessons

The user supplied a detailed comparison of revolutionary engines and technologies: SCUMM, Wolfenstein/Doom/Quake/id Tech, Build Engine, Unreal, RenderWare, Source, Havok, CryEngine, RAGE/Euphoria, Frostbite, Unity, id Tech 5, UE4, UE5, Decima, and related lineages.

The resulting lesson was not “copy Unreal” or “copy Doom.” It was that historically successful engines made hard ideas shippable, toolable, reusable, and production-friendly. The enduring lessons were:

- represent the world so the engine can cheaply decide what matters;
- make game logic and content data-driven;
- use physics and systems only where they are controllable and meaningful;
- stream worlds and assets rather than loading everything;
- treat the toolchain as part of the engine;
- build workflows that designers, modders, and developers can actually use.

The answer mapped those lessons onto Domino: virtualize expensive systems, use active sets, event queues, sufficient statistics, and collapsed capsules; make tooling and validation first-class; and do not build a monolithic renderer-first game engine.

### 2.3 Live repo reality and convergence

The user then corrected that the live repo had much more work than previously discussed. More docs and source were read or referenced during the chat, including MVP scope lock, frozen invariants, AppShell, capability negotiation, semantic contracts, pack verification, registry compile, determinism envelope, and construction/fabrication source files.

This changed the answer. The project was no longer treated as a blank-slate architecture. It was treated as a real but unfinished system that needs convergence. The recommended direction became:

> Turn Dominium from many good systems into one coherent modular machine: contracts → registries → compiled locks → capabilities → Work IR → deterministic runtime → proof/replay → AppShell/product surfaces.

The advice shifted toward validation unification, provider descriptors, registry bundle grouping, generated docs, a platform matrix, pack/mod tooling, and AuditX/RepoX triage.

### 2.4 CAD, construction, and player freedom

The user asked whether the game would need to provide a full CAD suite so players can build all items, machines, and structures. The answer separated **canonical design substrate** from **authoring surface**.

The recommended model is layered:

1. Low-skill players use templates, snapping, part placement, assisted actions, and text/intent commands.
2. Intermediate players modify parametric templates.
3. Advanced players edit constraints and assemblies.
4. Developers and expert players use CAD-grade design tools.
5. Generative assistants or scripts can propose designs, but those designs must still compile and validate into canonical artifacts.

This allows freedom without making CAD knowledge mandatory.

### 2.5 No default recipes, tech trees, or levels

The user explicitly stated that usual gameplay should not depend on technology trees, recipes, or experience levels. The answer preserved this preference. The alternative design is an affordance-and-constraint system: what a player can build depends on available materials, tools, processes, authority, law, environment, time, energy, and knowledge, not an arbitrary recipe unlock.

However, the engine should still support recipes, tech trees, levels, certifications, and similar systems for mods and alternate modes through packs, law profiles, capabilities, and policies.

### 2.6 Geometry: voxels versus CSG/B-Rep/NURBS

The user argued that Dual Universe went wrong by using a voxel-based engine and suggested B-Rep, CSG, NURBS, or a hybrid. The answer agreed that a pure voxel-first foundation would be a poor fit for precise machines, CAD semantics, interfaces, mass properties, and network-efficient authoritative objects.

The recommended model:

- **CSG / feature graph:** editable authoring and procedural history.
- **B-Rep:** canonical validated solid representation.
- **NURBS / B-splines:** optional advanced curved faces inside B-Rep.
- **Meshes:** derived rendering and collision proxies only.
- **Sparse voxels/SDF/fields:** terrain, mining, craters, fluids, fire, debris, damage approximation, volumetric phenomena.

Destruction should be event-driven and tiered: cosmetic damage, component damage, interface breakage, local cut/puncture, fracture/separation, and salvage/wreck states. The answer explicitly warned against doing full B-Rep booleans for every impact in real time.

### 2.7 Portability, modularity, and future-proofing

The user emphasized that all code should be portable, modular, extensible, and reusable for other games and engine projects, with directories and files replaceable if refactored. The answer said future-proofing does not come mainly from folders. It comes from contracts.

Key guidance:

- stable public APIs, flexible internals;
- public/private include boundaries;
- opaque handles and C ABI-like surfaces where needed;
- semantic contracts for behavior meaning;
- schemas for structure;
- capabilities for declared power;
- lockfiles for exact composition;
- proof/replay artifacts for actual execution;
- provider interfaces for replaceable backends;
- canonical serialization for persistent artifacts;
- golden replay/save/pack compatibility corpora.

A long-term directory shape was discussed, but the immediate advice was not to restructure broadly before baseline hardening.

### 2.8 Engine readiness and feasibility anxiety

The user then expressed worry that the project might be impossible and that they did not know how to write engines. The first answer framed the repo as a working deterministic foundation but not a full playable engine. The user then pasted a much more precise local assessment showing a stronger but still blocked current reality.

The corrected conclusion:

- Yes, there is a working compiled deterministic substrate.
- No, there is not yet a finished playable game engine.
- Yes, it is ready for baseline hardening and narrow vertical slices.
- No, it is not ready for broad game feature expansion.

The biggest correction was inserting **Milestone 0** before any builder/destruction lab.

### 2.9 Full-scale universe, planets, civilizations, MMO, and Unreal

The user described the full dream: full-scale solar systems, recreated and customizable planets, procedural/data-authored universe, civilization building, terraforming, cut/fill, megaprojects, machines, factories, fog of war, collapsed simulation for unsensed areas, client-shared compute, MMO persistent universe, single-player multiverse, and sparse construction/destruction.

The answer stated clearly that no conventional engine, including Unreal, can straightforwardly do the full version without major custom architecture. The only viable model is a deterministic multi-resolution universe:

- solar systems using orbits on rails initially;
- hierarchical planet domains and tiles;
- base procedural/data terrain plus sparse overlays;
- collapsed civilization capsules;
- fog of war as epistemic filtering, not just rendering;
- active simulation driven by sensing, interaction, due events, hazards, law obligations, and consistency;
- domain-sharded authority for MMO scale;
- clients allowed to contribute only derived/speculative/proof-carrying compute;
- proof/replay/hash validation for authoritative outcomes.

Unreal may be useful as a rendering/editor shell, but not as the authoritative deterministic simulation kernel.

---

## 3. What Was Decided

### 3.1 Strong decisions or accepted conclusions

1. **Domino should remain the reusable deterministic engine substrate.**  
   Dominium should be one game/product built on top, not the reason the engine exists.

2. **The current repo has a real deterministic substrate but not a finished playable game engine.**  
   This was sharpened after the user pasted the local readiness assessment.

3. **Milestone 0 comes before builder/destruction work.**  
   The first deliverable is one canonical repo-local playable baseline command passing strict validation.

4. **Do not start with full CAD, destruction, agents, economy, MMO, or broad renderer work.**  
   Those are downstream of baseline hardening.

5. **Normal gameplay should not rely on recipes, tech trees, or experience levels.**  
   Those can exist through packs/law/capabilities for mods and alternate modes.

6. **Full scale does not mean full fidelity everywhere.**  
   Full-scale solar systems and planets require collapsed sparse multi-resolution simulation.

### 3.2 Strong recommendations, not final decisions

1. Use a hybrid CSG/B-Rep/NURBS/mesh/SDF representation model for construction/destruction.
2. Treat CAD as an advanced tool surface, not required casual gameplay UI.
3. Use Unreal only as a possible client/editor/rendering shell, not the authoritative core.
4. Avoid broad repo restructuring until baseline proof exists.
5. Use a contract-compiled simulation platform model as the architecture north star.

These should be preserved as recommendations unless the user later explicitly confirms them as decisions.

---

## 4. What Was Put Off for Later

The chat explicitly or implicitly deferred:

- full CAD/B-Rep/CSG/NURBS implementation;
- arbitrary destruction;
- real chemistry/material simulation;
- economy/governance/war/agent loops;
- full vehicle/transport simulation;
- MMO-scale sharding and external multiplayer;
- full planet/civilization simulation;
- Unreal integration decision;
- broad directory restructure;
- full mod ecosystem;
- production renderer;
- client-shared authoritative compute;
- geometry provider selection;
- master Project Spec Book aggregation.

The reason these were deferred is not that they are unimportant. They were deferred because the local playable baseline path is not yet reliable. Feature work before baseline proof would increase uncertainty and project risk.

---

## 5. What We Actually Did in the Chat

The chat did not modify the repo. It did perform conceptual analysis and generated preservation artifacts.

Concrete things done:

- read and discussed repo docs and source files;
- identified the real project split between engine/game/product/governance;
- compared Domino against historical engine lessons;
- produced a modularity/future-proofing doctrine;
- proposed a CAD-capable layered authoring model;
- proposed a hybrid geometry/destruction strategy;
- corrected engine readiness after the user pasted local evidence;
- defined Milestone 0 as the immediate next milestone;
- described sparse full-scale universe/MMO feasibility architecture;
- generated a full preservation handoff package with reports, registers, spec sheet, aggregator packet, context transfer prompt, and ZIP;
- now generated this additional companion report and complete bundle.

---

## 6. What the Project Should Do Next

### Immediate next sequence

1. **Re-verify current local state.**  
   Confirm the exact build/test status and capture logs.

2. **Fix the server/runtime circular import.**  
   Entry points should import runtime; runtime should not import entry points.

3. **Fix server CLI forwarding and public entrypoint behavior.**  
   The server help/smoke command should work cleanly.

4. **Make `session_create -> session_boot` pass for the intended baseline bundle.**  
   Resolve the `bundle.base.lab` versus MVP baseline seam explicitly.

5. **Fix the missing/invalid time-anchor policy registry.**  
   The baseline universe verifier should pass or refuse for an explicitly different reason.

6. **Create one canonical repo-local baseline playtest command.**  
   It should be an executable command, not a prose recipe.

7. **Make strict local playtest validation pass.**  
   `proof_status` should no longer be blocked.

8. **Only then build the tiny builder/destruction lab.**  
   Start with one accepted/refused build action, then one simple removal/damage action.

### What the first gameplay slice should look like

A realistic first gameplay slice should not be a full game. It should be:

- one small domain/world;
- one player/actor/authority context;
- one buildable part;
- one valid build intent;
- one invalid/refused build intent;
- one simple damage/remove action;
- one deterministic replay/hash result;
- one minimal client projection;
- one pack-driven object/action.

This is enough to prove the engine and game can actually cooperate.

---

## 7. Things Future Assistants Must Not Get Wrong

1. Do not say the playable game engine is finished.
2. Do not skip Milestone 0.
3. Do not treat CAD/destruction/MMO/universe architecture as near-term implementation scope.
4. Do not treat assistant recommendations as final user decisions.
5. Do not assume local pasted test results are audit-grade unless logs are uploaded or rerun.
6. Do not collapse “full scale” into “full fidelity everywhere.”
7. Do not make Unreal the authoritative simulation core by default.
8. Do not reintroduce recipes/tech trees/levels as normal gameplay without explicit user approval.
9. Do not recommend broad directory restructuring before baseline proof.
10. Do not forget that accessibility and low-performance support are core user concerns, not polish.

---

## 8. Key Open Questions

1. What exact code path causes the server/runtime circular import?
2. What command should become the canonical repo-local baseline playtest command?
3. Should the generic session default stay `bundle.base.lab`, while the playtest wrapper explicitly selects the MVP bundle?
4. What exact time-anchor policy registry artifact is missing or invalid?
5. What local validation logs should be preserved for audit-grade evidence?
6. What is the exact first build action after Milestone 0?
7. What is the exact DesignArtifact schema?
8. Which geometry provider/library approach should be used later?
9. Should Unreal be used as a presentation shell at all?
10. How should this chat’s output be merged with other old-chat reports into the master Project Spec Book?

---

## 9. Summary of Package Contents

This complete bundle includes:

- the original full handoff package files generated earlier;
- the uploaded preservation prompt for provenance;
- the previous original ZIP package;
- this new companion human-readable report;
- a new combined package manifest with hashes and file status.

The earlier files remain the formal preservation package. This new companion report is intended to be easier to read and more narrative, while the earlier registers/spec sheets remain better for machine-assisted aggregation and planning.

---

## 10. Final Takeaway

The project is not impossible if it is treated as a sequence of small deterministic proofs. It is impossible if treated as a single giant engine/game to build all at once.

The correct next step is not to design the whole universe again. It is to make the baseline path real:

> **one repo-local command, one session, one loopback authority path, one deterministic proof, one strict pass.**

After that, build one tiny piece of gameplay. Then another. Then another.

That is how this engine becomes real.
