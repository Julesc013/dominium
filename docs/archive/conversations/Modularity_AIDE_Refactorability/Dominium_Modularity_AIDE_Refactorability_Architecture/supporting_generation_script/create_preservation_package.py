from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
from textwrap import dedent
import yaml, json, datetime, os, re

out = Path('/mnt/data')
label = 'Dominium Modularity, AIDE Refactorability, and Future-Proof Architecture'
safe = 'Dominium_Modularity_AIDE_Refactorability_Architecture'
date_anchor = '2026-05-27 Australia/Melbourne'
created = '2026-05-27 20:30:25 AEST'

coverage_table = """| Field | Assessment |
|---|---|
| Chat label | Dominium Modularity, AIDE Refactorability, and Future-Proof Architecture |
| Date anchor | 2026-05-27 Australia/Melbourne |
| Source scope | This chat only, except explicitly labelled PROJECT-CONTEXT |
| Apparent access | Partial-to-good: visible current chat plus uploaded preservation prompt; not the full live repo or all prior generated files |
| Previously generated files available? | Unclear / mostly no: prior files are referenced, but not available as downloadable artifacts in this chat |
| Uploaded files or artifacts present? | Yes: `Pasted text.txt`, containing the preservation-package output contract |
| Contains future plans? | Yes |
| Contains decisions? | Yes, but many are assistant recommendations unless clearly adopted by user language |
| Contains pending tasks? | Yes |
| Contains unresolved questions? | Yes |
| Staleness risk | Medium: repo status, commit IDs, live tooling status, and external practice references need verification before implementation |
| Extraction confidence | 4/5 for visible-chat substance; 2/5 for live repo facts and older unavailable artifacts |
| Safe for later aggregation? | With caveats |
| Main limitations | No live repo inspection in this turn; no full old-chat transcript beyond visible current conversation; prior generated files and older uploads may be unavailable/expired; several repo-status claims were pasted from earlier assistant outputs and are not independently verified here. |
"""

one_page = """
This chat was about making Dominium structurally durable: portable, modular, extensible, reusable across future games, and refactorable without the user having to repeat a painful top-level cleanup. The discussion began from an already-developed architectural thread about Dominium’s source layout, distribution layout, package layout, install roots, runtime roots, bundle formats, and component matrices. The user brought in several previous assistant outputs that had converged on a broad direction: Dominium should not be treated like a one-off indie project, but like a long-lived platform with a stable architecture, stable contracts, deterministic build/release/install semantics, and a repo structure that can survive multiple products, renderers, platforms, shells, and content systems.

The key early idea was that Dominium needs more than a source repo directory layout. It needs a unified logical-root model that can be projected into CI output, `.dompkg` packages, portable installs, installed desktop/server layouts, read-only media, caches, staging roots, rollback state, symbols, provenance, save bundles, instance bundles, replay bundles, and diagnostics bundles. This led to the principle that `.zip` archives, installers, portable folders, package files, media images, save bundles, and runtime installs should not invent separate semantics. They should all bind to the same logical roots, with physical paths depending on mode and mutability.

The next topic was the source repo itself. The user and assistant treated the existing root clutter as a serious architectural problem, not cosmetic untidiness. The target root set was repeatedly narrowed toward stable ownership categories: `apps/`, `engine/`, `game/`, `runtime/`, `contracts/`, `content/`, `docs/`, `tests/`, `tools/`, `scripts/`, `cmake/`, `external/`, `release/`, `archive/`, and generated `dist/` under strict policy. The important conclusion was that future top-level roots should be refused by default. New work should fit into existing ownership surfaces unless it truly has a separate lifecycle and long-term purpose.

A major correction happened when the user rejected the old XStack/AuditX/RepoX/TestX framing. The user wanted to transition to AIDE as soon as possible and recycle existing code/docs/tests rather than ignore them. The answer shifted from “make old checks green first, then clean” to “install AIDE as the restructuring control plane now, wrap and salvage old tools, and then drive cleanup through AIDE work units.” This became one of the central outcomes of the chat: AIDE should own inventory, classification, move maps, salvage maps, reference rewriting, validators, evidence ledgers, path aliases, shims, and refactor history.

The user then broadened the goal. The concern was not only Dominium’s current folder tree, but whether the codebase could become a proper reusable game/engine platform. The final answer introduced a product-line architecture view. Code should be split by reuse level: reusable across Dominium products, reusable across future games on the same domino/Dominium engine, and reusable across unrelated engine or game projects. That means contracts, runtime infrastructure, tooling, deterministic base engine pieces, content-addressed storage, diagnostics, packaging, schemas, tests, and AIDE machinery should be reusable beyond Dominium where possible, while `game/` should hold Dominium-specific truth.

The most important stable principles were: paths are not identity; contracts and manifests define identity; apps are thin; runtime owns host adaptation; engine owns deterministic substrate; game owns Dominium-specific rules; durable APIs need stability levels; C89-compatible ABI seams should be used for stable boundaries without forcing every internal implementation to be C89; schemas and protocols must be versioned; capability negotiation should replace platform-era assumptions; generated outputs must be quarantined; and every future refactor should be mechanical, evidence-backed, and reversible.

This chat contributes a high-level architecture constitution and refactorability doctrine for Dominium. It should feed directly into a future Project Spec Book section on repository architecture, reusable engine architecture, runtime/platform modularity, packaging/install semantics, AIDE governance, API/ABI stability, schemas/protocols, deterministic data, testing, and compatibility policy. Its main limitation is that several concrete repo-status claims came from pasted earlier outputs and were not verified against the live repository in this turn.
"""

story = """
The conversation opened with the user pasting a prior analysis about Dominium’s distribution and install layouts. That analysis argued that the source repository is only one layer. Dominium also needs canonical layouts for release build output, compressed packages, portable installs, installed layouts, instances and saves, bundles, diagnostics, caches, staging, rollback, symbols, provenance, and media. The core idea was that all these physical layouts should be projections of one logical virtual-root contract. The user then pasted another prior analysis about root convergence. That analysis treated the live repository as cluttered, with many roots mixing ownership levels, and proposed a staged convergence program around a stable source layout, distribution layout, runtime/install layout, and mechanical enforcement.

The next pasted section focused on component naming. It argued that Dominium should support many platforms, renderers, shells, package types, and presentation qualities, but should avoid names like `compat`, `universal`, `legacy`, `modern`, `gl2`, `vk1`, `dx11`, `winui3`, and `portable_zip` as primary component IDs. The better pattern was to name the component by what it is, then put version, support status, host age, package format, and constraints into matrix fields. This led to a clean modular architecture model: fixed contracts, runtime components, product entrypoints, and domain/content components.

The user asked whether this was the best possible direction. The response accepted the broad direction but strengthened it: the goal should be a contract-driven projection system, not just a directory plan. The answer added machine-readable contracts, a projection model, split host/platform axes, evidence levels in matrix rows, refusal codes, generated artifact policy, thin-app enforcement, a truth pipeline, capability negotiation, a minimum viable proof path, and migration safety rules.

The user then pasted another prior analysis about remaining root clutter and CTest/AuditX/RepoX blockers. That analysis recommended not doing visual folder cleanup and instead stabilizing failing checks before root exception cleanup. The user objected to the XStack/AuditX/RepoX/TestX framing and said they wanted to transition to AIDE as soon as possible while recycling existing code and docs. This changed the direction of the plan. The response agreed that the old names were temporary scaffolding and should not become durable architecture. It proposed AIDE as the control plane, with old tools inventoried, wrapped, adapted, renamed, archived, or retired through evidence-backed work units.

The user then asked whether this was truly the best plan and emphasized not wanting to go through the restructuring headache again. The answer refined the objective: the aim is not a perfect structure that never changes, but a stable top-level constitution plus a refactor operating system. Future internal movement should be cheap because it is scripted, validated, reversible, and driven by AIDE move maps and salvage maps. This produced the idea of `AIDE-STRUCTURE-00`, a repo constitution and refactorability framework.

Finally, the user made the broadest request: Dominium code must be portable, modular, extensible, reusable for another game on the same engine, and potentially reusable for different engine or game projects. The user wanted to know what was missing, what practices apply generally and specifically, whether the directory structure and names were the best they could be, what major engineering organizations do, and how to maximize future-proofing and backwards compatibility. The response reframed Dominium as a product-line architecture rather than a single game. It proposed explicit reuse levels, stricter internal structure for `contracts/`, `engine/`, `game/`, `runtime/`, `apps/`, `content/`, and `release/`, and detailed practices for ABI design, API stability, schemas, protocols, naming, target-based builds, dependency visibility, component manifests, data design, tests, compatibility, AIDE-driven refactors, portability threats, determinism, memory, errors, logging, concurrency, serialization, and host abstraction.

The final user action was uploading a preservation-package prompt. That prompt requested a maximum-fidelity preservation report, structured registers, context transfer packet, spec sheet, aggregator packet, self-audit, downloadable files, and a final in-chat reader. This package is the result.
"""

topics = [
("Topic 1 — Unified layout projection system", "The chat repeatedly distinguished source layout from distribution/build output, packages, portable installs, installed layouts, media, caches, rollback roots, symbols, bundles, saves, and diagnostics. The conclusion was that these should not be separate semantic inventions. They should be physical projections of a shared virtual-root contract. This matters because `.zip`, `.dompkg`, installer, media image, and runtime folder semantics can otherwise drift apart. The uncertainty is that the exact contract file names and root names still need implementation against the live repo."),
("Topic 2 — Stable source repo constitution", "The target top-level layout stabilized around `.aide/`, `.github/`, `apps/`, `engine/`, `game/`, `runtime/`, `contracts/`, `content/`, `docs/`, `tests/`, `tools/`, `scripts/`, `cmake/`, `external/`, `release/`, `archive/`, and generated `dist/`. The purpose is to make root ownership long-lived and prevent future root sprawl. The most important rule is that new top-level roots are refused by default unless they pass a strict lifecycle and ownership test."),
("Topic 3 — AIDE as restructuring control plane", "The user objected to the XStack/AuditX/RepoX/TestX framing and wanted AIDE adopted quickly. The resulting plan made AIDE the repo-native control plane for inventory, task queues, policies, move maps, salvage maps, evidence ledgers, validation, and refactor history. Existing tools should be recycled, not discarded. This is central to future refactorability."),
("Topic 4 — Product-line architecture and reuse levels", "The final discussion broadened Dominium from a single game to a reusable platform. Code should be separated by whether it is reusable across Dominium products, reusable across games on the same domino/Dominium engine, or reusable across unrelated engine/game projects. This changes where code belongs: reusable infrastructure should live in `contracts/`, `engine/base/`, `runtime/`, or `tools/`, while Dominium-specific rules belong in `game/`."),
("Topic 5 — Contracts, API, ABI, schemas, and protocols", "The chat emphasized that durable identity and compatibility should live in contracts and manifests, not paths. Public seams need stability levels. C89-compatible ABI headers are valuable for stable boundaries, using opaque handles, explicit allocators, versioned structs, and stable error codes. Schemas and protocols need versioning, negotiation, compatibility ranges, refusal codes, and migration policy."),
("Topic 6 — Naming and component matrices", "The chat rejected names based on era, temporary project status, support status, or implementation-version encoding. Components should have boring literal names such as `opengl`, `direct3d`, `vulkan`, `software`, `win32`, `posix`, `cocoa`, `portable`, `installed`, with version/status/format fields carried separately. This reduces long-term naming debt."),
("Topic 7 — Build, dependency, and visibility discipline", "The discussion proposed target-based CMake and module boundaries rather than path mythology. Public headers, private headers, allowed dependencies, and forbidden dependencies should be explicit. Apps must remain thin. Engine must not depend on game/apps/runtime UI. Runtime adapts host/platform/rendering without owning simulation truth."),
("Topic 8 — Determinism, data, compatibility, and testing", "The chat stressed deterministic serialization, named RNGs, no wall-clock dependency in simulation, no filesystem ordering dependence, schema round-trip tests, replay tests, package verification tests, migration tests, renderer parity tests, and hermetic tests. Compatibility should be promised only for selected public seams, not every internal implementation."),
("Topic 9 — Preservation and aggregation", "The uploaded prompt converted the conversation into a preservation task. It requires a human-readable report first, then registers, spec sheet, aggregator packet, self-audit, and downloadable files. This final package is intended to be merged later with old-chat reports into a master Project Spec Book.")
]

# Registers data
workstreams = [
("WORKSTREAM-01","Stable repo constitution","Define stable top-level ownership roots and refuse future root sprawl.","Conceptually defined in chat; needs implementation.","Contracts, docs, validators, and root admission policy exist and are enforced.","active","P0","high","FACT/INFERENCE"),
("WORKSTREAM-02","Distribution and install projection","Unify package, portable, installed, media, cache, rollback, bundle, save, and diagnostics layouts through logical roots.","Strongly described in pasted prior analysis; not verified against live repo.","One logical-root projection contract drives all physical layouts.","active","P0","medium","FACT/UNCERTAIN"),
("WORKSTREAM-03","AIDE control plane","Use AIDE for migration, validation, evidence, queues, move maps, salvage maps, and refactor history.","User explicitly preferred AIDE over XStack-style framing.","AIDE owns restructuring workflow; old tools are wrapped and recycled.","active","P0","high","FACT"),
("WORKSTREAM-04","Old tool/code/doc recycling","Inventory and classify XStack/AuditX/RepoX/TestX-style material instead of discarding it.","Conceptual plan only.","Useful assets kept/adapted/extracted/converted; bad names retired.","active","P1","high","FACT/INFERENCE"),
("WORKSTREAM-05","Reusable engine/product-line architecture","Separate code by reuse level across Dominium products, future games, and unrelated engine projects.","Outlined in final architecture response.","Reusable layers isolated from Dominium-specific game rules.","active","P0","high","FACT/INFERENCE"),
("WORKSTREAM-06","Contracts/API/ABI/schema/protocol discipline","Make public seams versioned, stable where promised, and negotiable.","Outlined as doctrine; implementation pending.","Contracts define identity and compatibility; public ABI seams are durable.","active","P0","high","INFERENCE"),
("WORKSTREAM-07","Naming and matrix cleanup","Use clean component names with version/status/format fields separated.","Discussed in pasted component-naming analysis.","No durable names like legacy/modern/compat/XStack/gl2/vk1/dx11-as-primary.","active","P1","medium","FACT/INFERENCE"),
("WORKSTREAM-08","Determinism, testing, and proof matrix","Create deterministic, hermetic, replayable proof systems for engine, packages, saves, protocols, and renderers.","Discussed as best practice.","Refactors and releases have reproducible proof outputs.","active","P1","medium","INFERENCE"),
("WORKSTREAM-09","Spec-book aggregation","Preserve this chat for later merging into a master Project Spec Book.","Activated by uploaded prompt.","Human report, registers, YAML spec, aggregator packet, and ZIP exist.","active","P0","high","FACT")
]

decisions = [
("DECISION-01","Use a stable top-level root constitution rather than ad hoc root growth.","accepted direction","Repeated user concern about avoiding future restructure; assistant proposals align.","Prevents root sprawl and preserves ownership clarity.","Future roots require admission tests and validators.","WORKSTREAM-01","high","FACT/INFERENCE"),
("DECISION-02","Treat AIDE as the restructuring control plane.","accepted by user framing","User explicitly said to transition to AIDE ASAP and recycle existing material.","AIDE provides queue, evidence, move-map, and salvage discipline.","Old XStack-style tools become transitional assets.","WORKSTREAM-03","high","FACT"),
("DECISION-03","Recycle old tools/docs/tests rather than ignore or discard them.","accepted direction","User explicitly said there is code and docs to recycle.","Prevents loss of useful validators and policies.","Requires classification: keep/adapt/extract/convert/archive/drop.","WORKSTREAM-04","high","FACT"),
("DECISION-04","Paths are not identity; contracts and manifests define identity.","strong recommendation","Repeated in final architecture answer.","Makes directories replaceable and data portable.","Packs, saves, schemas, modules, and packages need IDs, versions, hashes, capabilities.","WORKSTREAM-05","high","INFERENCE"),
("DECISION-05","Design Dominium as a product-line architecture, not a one-off game.","accepted objective","User explicitly requested proper game/OS-like architecture and reusable code.","Supports reuse across products, games, and projects.","Requires stricter separation of engine/game/runtime/contracts/tools/content.","WORKSTREAM-05","high","FACT"),
("DECISION-06","Use C89-compatible stable ABI seams, without forcing all internals to be C89.","recommendation","Assistant proposed this refinement.","Stable external seams with flexible implementation.","Public headers need opaque handles, allocators, versioned structs, error codes.","WORKSTREAM-06","medium","INFERENCE"),
("DECISION-07","Avoid durable architecture names based on temporary tooling or status labels.","accepted direction","User disliked XStack framing; prior component naming analysis rejected legacy/modern/compat labels.","Prevents temporary migration scaffolding becoming permanent ontology.","Use boring literal names and matrix fields.","WORKSTREAM-07","high","FACT/INFERENCE"),
("DECISION-08","Future refactors should be AIDE work units with move maps and salvage maps.","recommendation aligned with user goal","User wanted future refactors easy and quick.","Turns restructuring into a mechanical process.","Requires AIDE refactor schemas, ledgers, validators, and temporary aliases.","WORKSTREAM-03","high","INFERENCE"),
("DECISION-09","Apps should be thin; runtime adapts host; engine/game own truth.","strong recommendation","Repeated in architecture doctrine.","Preserves portability and prevents UI/rendering/platform code owning simulation truth.","Boundary validators needed.","WORKSTREAM-05","medium-high","INFERENCE"),
("DECISION-10","Do not promise compatibility for every internal interface.","recommendation","Final response emphasized stabilizing correct public seams only.","Avoids maintenance paralysis.","Need stability levels and deprecation policy.","WORKSTREAM-06","medium","INFERENCE")
]

tasks = [
("TASK-01","Implement AIDE-STRUCTURE-00 / repo constitution and refactorability framework.","P0","U0","User/Codex/AIDE","None beyond repo access.","Current repo tree, existing validators, project doctrine.","Root constitution, ownership slots, AIDE refactor framework, non-blocking inventory tooling.","Create committed contracts/docs/tools without moving code.","WORKSTREAM-01","FACT/INFERENCE"),
("TASK-02","Implement AIDE-ARCH-00 / modularity and reuse constitution.","P0","U1","User/Codex/AIDE","AIDE-STRUCTURE-00 helpful first.","Architecture doctrine from this chat.","Dependency layers, API stability levels, C89 ABI rules, modularity docs, boundary checker.","Convert chat doctrine into repo contracts/docs.","WORKSTREAM-05","FACT/INFERENCE"),
("TASK-03","Inventory existing XStack/AuditX/RepoX/TestX-style tooling and classify it.","P0","U1","AIDE/Codex","AIDE inventory scaffolding.","Live repo files, old tool directories.","Tool recycling inventory and transition plan.","Run non-invasive inventory and mark keep/adapt/extract/convert/archive/drop.","WORKSTREAM-04","FACT"),
("TASK-04","Wrap old checks behind AIDE before renaming them.","P1","U1","AIDE/Codex","TASK-03.","Existing validators/tests/build checks.","AIDE task runner adapters.","Expose old checks as AIDE tasks while preserving behavior.","WORKSTREAM-03","INFERENCE"),
("TASK-05","Define logical-root projection contracts for distribution/install/media/bundles.","P0","U1","AIDE/Codex","Repo access and current distribution docs.","Existing docs/contracts if present.","Machine-readable distribution layout contract and docs.","Write contract first; validators non-blocking.","WORKSTREAM-02","INFERENCE"),
("TASK-06","Add boundary validators for apps/engine/game/runtime/contracts/content/tools.","P1","U2","AIDE/Codex","Dependency layer contract.","Build graph, include paths, manifests.","Report-only checker, later strict gate.","Start with detection only.","WORKSTREAM-06","INFERENCE"),
("TASK-07","Create component/module manifest pattern.","P1","U2","AIDE/Codex","Stable naming and dependency rules.","Candidate modules and targets.","Module manifests with owner, provides, requires, stability, forbidden dependencies, tests.","Pilot on one renderer and one engine module.","WORKSTREAM-07","INFERENCE"),
("TASK-08","Define portability threat checks.","P1","U2","AIDE/Codex","Architecture doctrine.","Compiler/platform/test matrix.","Checklist or validator for endian, width, locale, filesystem order, RNG, wall clock, FP determinism.","Add to docs and proof matrix.","WORKSTREAM-08","INFERENCE"),
("TASK-09","Verify live repo status before executing any concrete cleanup.","P0","U0","User/Codex","Repo access.","Current branch, commits, CTest output, validators.","Verified baseline report.","Do not rely on pasted commit/status claims without verification.","WORKSTREAM-01","UNCERTAIN"),
("TASK-10","Merge this package into future master Project Spec Book.","P1","U2","Aggregator chat/user","Other old-chat reports.","This report and ZIP.","Spec-book chapters and formal requirements candidates.","Use aggregator packet.","WORKSTREAM-09","FACT")
]

constraints = [
("CONSTRAINT-01","Source scope is this chat only unless Project-context is explicitly labelled.","reporting","hard","Uploaded preservation prompt.","Do not merge external memories silently.","High if a future assistant overgeneralizes.","high","FACT"),
("CONSTRAINT-02","Do not treat assistant suggestions as user decisions unless accepted.","epistemic","hard","Uploaded preservation prompt.","Decision register must distinguish recommendations from accepted decisions.","High.","high","FACT"),
("CONSTRAINT-03","Future architecture should avoid root sprawl.","architecture","hard-ish","User wants to avoid repeat restructuring.","New roots refused by default.","High if no validator exists.","high","FACT/INFERENCE"),
("CONSTRAINT-04","Existing code/docs/tests should be recycled rather than ignored.","migration","hard","User explicitly stated this.","Use classification before delete/archive.","High if cleanup becomes destructive.","high","FACT"),
("CONSTRAINT-05","AIDE names must not contaminate product/runtime/game architecture.","architecture","soft-to-hard","Assistant recommendation based on user rejection of XStack framing.","AIDE remains control plane; Dominium architecture remains separate.","Medium.","medium-high","INFERENCE"),
("CONSTRAINT-06","Portability and modularity are primary design goals.","technical","hard","User explicitly stated this is very important.","Avoid hidden OS calls, hardcoded paths, unstable ABI leakage.","High.","high","FACT"),
("CONSTRAINT-07","Durable data and protocols need versioning and migration/refusal policy.","compatibility","hard-ish","Architecture doctrine.","No silent save/package/schema migration.","High.","medium-high","INFERENCE"),
("CONSTRAINT-08","Generated outputs must be quarantined.","repo hygiene","hard-ish","Repeated assistant recommendation.","Generated files go to dist/build/.aide.local or canonical fixture/archive only.","Medium.","medium","INFERENCE")
]

prefs = [
("PREF-01","Direct, human-readable explanations first; machine-readable registers second.","output style","explicit","strong","Do not answer with only YAML or manifests.","High.","FACT"),
("PREF-02","Broad and deep architectural reasoning, not shallow folder advice.","analysis depth","explicit","strong","Explain principles, tradeoffs, big-project practices, and missing issues.","High.","FACT"),
("PREF-03","Preserve uncertainty and distinguish facts from inferences.","epistemic","explicit","strong","Use labels and do not overstate repo facts.","High.","FACT"),
("PREF-04","Avoid repeating previously rejected XStack-style ontology as durable architecture.","naming/architecture","explicit","strong","Use AIDE/control-plane vocabulary and boring project names.","Medium-high.","FACT"),
("PREF-05","Future work should be executable by Codex/AIDE with clear tasks.","workflow","inferred","strong","Provide prompts/tasks and validation outputs.","Medium.","INFERENCE"),
("PREF-06","Code should be reusable across games and projects, not one-off.","technical direction","explicit","strong","Design APIs, modules, data, tests, and directories as platform architecture.","High.","FACT")
]

questions = [
("QUESTION-01","What is the current live repo state and which of the pasted commit/status claims remain true?","Implementation depends on baseline accuracy.","Pasted text asserted specific repo status and failures.","Live branch, CTest, validators, current root inventory.","Inspect repo with GitHub/Codex and produce baseline report.","P0","WORKSTREAM-01","UNCERTAIN"),
("QUESTION-02","What exact parts of old XStack/AuditX/RepoX/TestX tooling are useful?","Recycling requires classification.","User wants recycling, not ignoring.","Actual file contents and usefulness.","AIDE inventory with keep/adapt/extract/convert/archive/drop.","P0","WORKSTREAM-04","FACT/UNCERTAIN"),
("QUESTION-03","Which APIs deserve stable/frozen compatibility promises?","Over-stabilizing internals is costly; under-stabilizing public seams breaks reuse.","Candidate seams include C ABI, schemas, commands, saves, packages, protocols.","Actual implementation maturity and external use cases.","Define stability levels and public API declarations.","P1","WORKSTREAM-06","INFERENCE"),
("QUESTION-04","Where should domino-engine reusable code stop and Dominium-specific game code begin?","Determines reuse for future games.","Final answer proposed reuse levels.","Actual current code ownership.","Inventory modules and classify reuse level.","P0","WORKSTREAM-05","INFERENCE"),
("QUESTION-05","What generated artifacts are intentionally tracked versus accidental?","Generated-output policy affects cleanup.","Pasted text references dist/artifacts and generated outputs.","Actual repository policy and files.","Generated artifact audit.","P1","WORKSTREAM-01","UNCERTAIN"),
("QUESTION-06","What should become formal Project Spec Book requirements versus background context?","Avoid prematurely hardening brainstorms.","This chat proposes many doctrines.","User confirmation and cross-chat consistency.","Aggregator review.","P1","WORKSTREAM-09","INFERENCE")
]

artifacts = [
("ARTIFACT-01","Pasted text.txt","uploaded prompt","Defines required preservation package structure and rules.","available in this chat","user upload","yes","Must be treated as active instruction for this turn.","FACT"),
("ARTIFACT-02","Prior distribution/install layout analysis pasted by user","pasted assistant output","Provided logical-root projection doctrine and layout examples.","visible in chat, not independently verified","user-pasted text","yes","Use as chat content; repo/doc claims need verification.","FACT/UNCERTAIN"),
("ARTIFACT-03","Prior convergence/root cleanup analysis pasted by user","pasted assistant output","Provided staged repo convergence and root allowlist plan.","visible in chat, not independently verified","user-pasted text","yes","Some specific live repo claims are unverified.","FACT/UNCERTAIN"),
("ARTIFACT-04","Prior component naming/matrix analysis pasted by user","pasted assistant output","Defined clean component naming doctrine.","visible in chat","user-pasted text","yes","Should inform spec-book naming/matrix chapter.","FACT"),
("ARTIFACT-05","AIDE transition prompt/task proposal","assistant-generated prompt","Suggested AIDE-00 bootstrap and recycling plan.","visible in chat","assistant response","yes, with user review","Prompt is recommendation, not executed.","INFERENCE"),
("ARTIFACT-06","AIDE-STRUCTURE-00 prompt","assistant-generated prompt","Defines repo constitution/refactorability framework task.","visible in chat","assistant response","yes","Candidate next Codex/AIDE task.","INFERENCE"),
("ARTIFACT-07","AIDE-ARCH-00 prompt","assistant-generated prompt","Defines modularity and reuse constitution task.","visible in chat","assistant response","yes","Candidate next Codex/AIDE task.","INFERENCE"),
("ARTIFACT-08","This preservation package","generated files + ZIP","Preserves this chat for reading, handoff, aggregation, and future spec-book work.","created in this turn","assistant generated","yes","Contains report, registers, context packet, spec sheet, aggregator packet, audit, reader brief.","FACT")
]

rejected = [
("REJECTED-01","Visual drag-and-drop cleanup of root folders","rejected","Would break paths, build, tests, package identity, and authority semantics.","final unless repo becomes trivial","Only reconsider for tiny isolated folders with move map and proof.","WORKSTREAM-01","FACT/INFERENCE"),
("REJECTED-02","XStack/AuditX/RepoX/TestX as durable architecture ontology","rejected/superseded","User disliked it; names are temporary scaffolding.","mostly final","May remain in history/ledgers during transition.","WORKSTREAM-03","FACT"),
("REJECTED-03","Discarding old tools/docs/tests during AIDE transition","rejected","User explicitly wants recycling.","final","Only drop after classification and evidence.","WORKSTREAM-04","FACT"),
("REJECTED-04","Perfect structure that never changes","superseded","Unrealistic; better target is stable top-level roots plus cheap internal refactors.","final as framing","N/A.","WORKSTREAM-01","INFERENCE"),
("REJECTED-05","Using paths as identity","rejected","Makes moves/refactors break artifacts.","final as doctrine","N/A.","WORKSTREAM-05","INFERENCE"),
("REJECTED-06","Stabilizing every internal interface forever","deprioritized","Too costly; stabilize public seams and let internals evolve.","tentative but strong","Revisit per API if external dependents emerge.","WORKSTREAM-06","INFERENCE"),
("REJECTED-07","Component IDs based on legacy/modern/compat/universal or version-coded names","rejected direction","Creates naming debt and mixes axes.","strong","Use only as status/version fields where needed.","WORKSTREAM-07","FACT/INFERENCE")
]

risks = [
("RISK-01","Future assistant treats assistant recommendations as user decisions.","Spec book hardens tentative ideas incorrectly.","medium","high","Keep labels and require user confirmation for major implementation commitments.","WORKSTREAM-09","FACT"),
("RISK-02","Live repo claims from pasted text are stale or wrong.","Codex tasks may target wrong blockers or paths.","medium","high","Verify repo state before implementation.","WORKSTREAM-01","UNCERTAIN"),
("RISK-03","AIDE becomes another mythology instead of a control plane.","Product architecture polluted by workflow names.","medium","medium-high","Keep AIDE under `.aide/`, `tools/aide/`, docs/aide; do not name runtime/game concepts after it.","WORKSTREAM-03","INFERENCE"),
("RISK-04","Old validators are renamed before being wrapped.","Regression detection lost.","medium","high","Wrap before rename; preserve behavior first.","WORKSTREAM-04","INFERENCE"),
("RISK-05","Root constitution becomes too rigid.","Useful evolution blocked.","low-medium","medium","Allow root admission test with high bar and validator update.","WORKSTREAM-01","INFERENCE"),
("RISK-06","Compatibility promises are too broad.","Maintenance burden and slow evolution.","medium","medium-high","Define stability levels; stabilize only public seams.","WORKSTREAM-06","INFERENCE"),
("RISK-07","Reusable code remains tangled with Dominium-specific game rules.","Future games/projects cannot reuse the engine cleanly.","medium-high","high","Classify modules by reuse level and enforce dependencies.","WORKSTREAM-05","FACT/INFERENCE"),
("RISK-08","Generated artifacts leak into source roots.","Repo becomes hard to reason about and refactor.","medium","medium","Generated-output policy and validator.","WORKSTREAM-01","INFERENCE")
]

verify = [
("VERIFY-01","Current live repo head, branch, validator status, and CTest status.","Pasted status may be stale/unverified.","GitHub/Codex live repo inspection.","P0","WORKSTREAM-01","UNCERTAIN"),
("VERIFY-02","Existence and contents of docs referenced in pasted analyses, such as VIRTUAL_PATHS, INSTALL_MODEL, DIST_TREE_CONTRACT, PKG_FORMAT.","They underpin distribution recommendations.","Live repo or uploaded docs snapshot.","P0","WORKSTREAM-02","UNCERTAIN"),
("VERIFY-03","Actual XStack/AuditX/RepoX/TestX paths and behavior.","Recycling plan depends on contents.","Repo inventory and test runs.","P0","WORKSTREAM-04","UNCERTAIN"),
("VERIFY-04","Current component matrix names and statuses.","Naming cleanup should target actual files.","Repo search.","P1","WORKSTREAM-07","UNCERTAIN"),
("VERIFY-05","External best-practice references used in prior answer.","Could be stale or context-dependent.","Official docs for CMake, Bazel, Chromium, Linux, SemVer, Google Testing.","P2","WORKSTREAM-05","UNCERTAIN"),
("VERIFY-06","Which prior generated files or old uploads are unavailable/expired.","Artifact ledger completeness depends on availability.","Conversation file list / user re-upload.","P1","WORKSTREAM-09","UNCERTAIN")
]

timeline = [
("1","User pasted prior distribution/install layout analysis.","Established need for multiple physical layouts unified by virtual roots.","Shifted beyond source folder cleanup.","Foundational for layout projection.","high"),
("2","User pasted prior repo convergence analysis.","Framed root clutter as ownership and enforcement problem.","Suggested stable source layout and validators.","Feeds root constitution.","high for chat content; medium for live repo claims"),
("3","User pasted prior component naming analysis.","Rejected version/status/era-coded component IDs.","Supports modular renderer/platform/package architecture.","Feeds matrix cleanup.","high"),
("4","Assistant strengthened plan with contracts, projection model, evidence levels, refusal codes, proof path.","Moved from folders to contract-driven architecture.","Became core doctrine.","high"),
("5","User rejected XStack-style framing and asked for AIDE transition and recycling.","Changed strategy from old-tool-first to AIDE-control-plane-first.","Central correction.","high"),
("6","Assistant proposed AIDE bootstrap, recycling inventory, wrap-before-rename, salvage maps.","Established AIDE as refactor OS.","Candidate next action.","high"),
("7","User asked how to avoid future headaches.","Goal became stable roots plus cheap future refactors, not perfect immutability.","Led to AIDE-STRUCTURE-00.","high"),
("8","User asked broad/deep portability/modularity/reuse question.","Expanded scope to proper game/OS-like architecture and product-line reuse.","Led to AIDE-ARCH-00 and detailed engineering practices.","high"),
("9","User uploaded preservation-package prompt.","Converted chat into report/export task.","This output fulfills that request.","high")
]

spec_contrib = [
("Repo Architecture","Stable root constitution, forbidden roots, ownership slots, root admission policy.","DECISION-01, WORKSTREAM-01","requirement","high","Must verify live repo before applying."),
("AIDE Governance","AIDE as control plane for refactors, evidence, queues, move/salvage maps.","DECISION-02, WORKSTREAM-03","requirement/context","high","Do not let AIDE names enter product architecture."),
("Modular Engine Architecture","Reuse levels across products/games/projects; engine/game/runtime/contracts separation.","DECISION-05, WORKSTREAM-05","requirement","high","Needs module inventory."),
("Distribution/Install Layout","Logical-root projection model for packages, installs, media, bundles, cache, rollback.","WORKSTREAM-02","requirement/open issue","medium","Repo docs need verification."),
("API/ABI/Schemas/Protocols","Versioned public seams, C ABI rules, stability levels, capability negotiation.","WORKSTREAM-06","requirement","medium-high","Requires design review per API."),
("Testing and Determinism","Hermetic, deterministic proof matrix; save/replay/package/schema tests.","WORKSTREAM-08","requirement","medium","Specific test implementation still open."),
("Naming Doctrine","Boring component names; versions/status in fields; retire XStack-style names.","WORKSTREAM-07","requirement/context","high","Needs current matrix audit.")
]

# Build report sections 0-16

def md_table(rows, headers):
    out = ['| ' + ' | '.join(headers) + ' |', '| ' + ' | '.join(['---']*len(headers)) + ' |']
    for r in rows:
        out.append('| ' + ' | '.join(str(x).replace('\n','<br>') for x in r) + ' |')
    return '\n'.join(out)

report = f"""# COMPLETE CHAT PRESERVATION REPORT — {label}

## 0. Coverage and Reliability Assessment

{coverage_table}

This package is based on the visible current chat and the uploaded `Pasted text.txt` prompt. It does not include live repository inspection, execution of validators, or complete access to older files generated in other chats. Some older uploaded files appear unavailable or expired in the broader chat environment. Where this report mentions repo state, CTest failures, specific commit IDs, or current file paths from pasted prior assistant outputs, those are treated as **UNCERTAIN / UNVERIFIED** unless independently verified later. The package is safe for aggregation if future readers preserve these labels and do not treat every assistant recommendation as an adopted user decision.

## 1. One-Page Orientation

{one_page}

## 2. The Story of the Conversation

{story}

## 3. Main Topics Discussed

"""
for title, body in topics:
    report += f"### {title}\n\n{body}\n\n"

report += """## 4. What We Were Trying to Achieve

### 4.1 Explicit Goals

The user explicitly wanted Dominium’s code and architecture to be portable, modular, extensible, reusable for other games on the same engine, and reusable where possible for different engine or game projects. The user also explicitly wanted to avoid repeating a painful restructuring process and wanted future full refactors to be as quick and easy as possible. The user wanted AIDE adopted quickly as the restructuring control plane and wanted existing code/docs/tests recycled rather than ignored.

### 4.2 Inferred Goals

The conversation implies a goal of turning Dominium into a long-lived product-line platform rather than a single-game repository. It also implies a desire for auditability: decisions should be grounded, visible, mechanically enforceable, and later aggregatable into a master spec. The user appears to value stable boundaries, explicit compatibility policy, and practical Codex/AIDE tasks.

### 4.3 Goals That Changed Over Time

The initial focus was directory and distribution structure. It then widened to component naming, repository convergence, AIDE governance, refactorability, and finally broad software engineering doctrine for reusable engine/platform development. The most important change was the rejection of the XStack-style framing and the shift toward AIDE as the near-term control plane.

### 4.4 Goals Still Unresolved

The live repo still needs verification. The exact AIDE files, contracts, validators, and migration tasks must be implemented. It remains unresolved which existing roots and tools map to which final homes, which APIs become stable, which code is reusable across products/games/projects, and which prior assistant recommendations should become formal requirements after user review.

## 5. Decisions Made and Why

"""
report += md_table([(d[0],d[1],d[2],d[3],d[6],d[7]) for d in decisions], ["ID","Decision","Status","Why it mattered / basis","Confidence","Label"])
report += "\n\n"
for d in decisions:
    report += f"### {d[0]} — {d[1]}\n\nStatus: {d[2]}. Basis: {d[3]} Rationale: {d[4]} Implications: {d[5]} Related workstream: {d[6]}. Confidence: {d[7]}. Label: {d[8]}. This should be revisited if live repo evidence contradicts the assumed structure, or if the user later chooses a different product-line strategy.\n\n"

report += """## 6. Ideas Considered but Rejected, Superseded, or Deprioritised

"""
for r in rejected:
    report += f"### {r[0]} — {r[1]}\n\nStatus: {r[2]}. It was rejected/superseded because {r[3]} Finality: {r[4]}. Reconsider conditions: {r[5]}. Related workstream: {r[6]}. Label: {r[7]}.\n\n"

report += """## 7. Important Reasoning, Rationale, and Tradeoffs

The visible rationale centered on avoiding architectural lock-in and path fragility. A neat folder tree alone does not make code reusable or portable. The durable solution requires contracts, manifests, APIs, build targets, validators, and AIDE-managed refactor machinery. The main tradeoff is between rigidity and flexibility: if every internal interface is frozen, the project becomes hard to evolve; if no seam is stable, future games, tools, saves, packs, and integrations cannot rely on anything. The proposed answer is to stabilize public seams and durable data formats, while allowing internals to change behind tests, migrations, and compatibility policies.

A second tradeoff is between immediate cleanup and preserving working checks. The user rejected throwing away old tools. The better path is wrap-before-rename: inventory existing tools, call them through AIDE, classify them, then migrate names and paths after their value is preserved. Another tradeoff is naming clarity versus historical continuity. Names like XStack or AuditX may be useful as migration history but should not become long-term product architecture.

The project’s portability goal creates specific constraints: deterministic engine code must avoid hidden OS calls, unnamed randomness, wall-clock dependence, filesystem-order dependence, unversioned binary formats, and public implementation structs. Runtime should adapt the host; engine/game truth should remain host-independent. The user’s deeper concern is not just this refactor, but preventing future architectural debt from accumulating unseen.

## 8. Plans, Future Work, and Next Steps

The recommended path is to implement AIDE-backed architecture contracts before moving large amounts of code. The highest-value next tasks are: verify live repo state; create the repo constitution/refactorability framework; create the modularity and reuse constitution; inventory and wrap old XStack-style tooling; define logical-root projection contracts; add non-blocking boundary validators; and only then perform ownership extraction waves.

Recommended next-action sequence:

1. **TASK-09** — Verify live repo baseline: current branch, root inventory, validators, CTest status, generated artifacts.
2. **TASK-01** — Implement AIDE-STRUCTURE-00: root constitution, ownership slots, AIDE refactor framework, move/salvage map schemas, inventory tooling.
3. **TASK-03** — Inventory old XStack/AuditX/RepoX/TestX-style tools and classify them.
4. **TASK-04** — Wrap old checks behind AIDE without changing behavior.
5. **TASK-02** — Implement AIDE-ARCH-00: modularity/reuse doctrine, dependency layers, C89 ABI rules, API stability levels, boundary checker.
6. **TASK-05** — Define distribution/install/media/bundle projection contracts.
7. **TASK-06/TASK-07/TASK-08** — Add boundary validators, component manifests, and portability/determinism proof checks.
8. Use AIDE work units for actual cleanup, with move maps, salvage maps, validators, evidence, and shim retirement.

## 9. Constraints, Preferences, and Non-Negotiables

### 9.1 Explicit Constraints and Preferences

The user wants human-readable explanation first, not only machine-readable artifacts. The user wants broad/deep reasoning and does not want to repeat restructuring pain. The user explicitly wants portable, modular, extensible, reusable code, and wants AIDE adoption plus recycling of existing code/docs/tests.

### 9.2 Inferred Constraints and Preferences

The user prefers source-grounded, audit-ready decisions; bounded uncertainty; explicit task prompts; and reusable engineering doctrine. Future assistants should avoid shallow affirmation and should distinguish accepted user decisions from assistant recommendations.

### 9.3 Uncertain or Unestablished Preferences

It is not yet established which specific compatibility promises the user wants to make for each API, save format, protocol, or package format. It is also not established how much generated output should be tracked in the repo. These need future decisions after repo verification.

## 10. Files, Artifacts, Outputs, and Prompts

"""
report += md_table(artifacts, ["ID","Artifact / file / prompt / output","Type","Purpose","Status","Origin","Carry forward?","Notes","Label"])
report += """

Important caveat: the only current uploaded file available for this task is `Pasted text.txt`, which contains the preservation-package prompt. Earlier generated handoff files, ZIP packages, or uploaded docs referenced in prior conversation are not available in this chat unless the user re-uploads them.

## 11. Open Questions and Unresolved Issues

"""
report += md_table(questions, ["ID","Question / issue","Why it matters","Known information","Unknown information","Resolution path","Priority","Related workstream","Label"])

report += """

## 12. Risks, Failure Modes, and What Future Chats Might Get Wrong

"""
report += md_table(risks, ["ID","Risk / failure mode","Consequence","Likelihood","Severity","Mitigation","Related workstream","Label"])

report += """

The most serious risk is that a future assistant treats this chat as if it verified the live repo. It did not. The second serious risk is that it hardens every assistant suggestion into a requirement. Several items are strong recommendations aligned with user goals, but still require implementation review. Future chats must preserve labels and verify stale facts.

## 13. What This Chat Contributes to the Larger Project or Future Spec Book

This chat contributes the architecture constitution layer: stable source layout, logical-root projection, AIDE governance, product-line reuse, modular engine/runtime/game separation, API/ABI/schema/protocol discipline, naming doctrine, generated-output policy, and refactorability workflow. It should feed future chapters on repo architecture, AIDE operations, engine modularity, distribution/install layout, API stability, portability, determinism, testing, and compatibility. It overlaps with other Dominium architecture chats and may conflict if earlier chats used different root names, older XStack terminology, or more specific platform/render priorities.

## 14. What I Should Remember

- The goal is not a perfect layout that never changes. The goal is stable top-level ownership plus mechanical, reversible internal refactors.
- AIDE should become the refactor/control plane now, not after all old XStack-style tooling is magically cleaned up.
- Existing tools/docs/tests should be inventoried and recycled, not discarded.
- Paths are not identity. Contracts, manifests, IDs, versions, hashes, and capabilities define identity.
- Dominium should be designed as a product-line architecture: reusable across products, future games on the same engine, and some unrelated engine projects where possible.
- `game/` should contain Dominium-specific truth. Reusable engine/runtime/tooling/contracts should not be trapped there.
- Stable C-style ABI seams are useful for durability, but internal implementation should remain flexible.
- Future assistants must verify live repo state before implementing cleanup.
- The best next action is AIDE-STRUCTURE-00 plus live repo baseline verification.

## 15. Best Questions I Can Ask Next in This Chat

### 15.1 Understanding the Chat

- Explain the difference between source layout, install layout, package layout, and AIDE refactor layout.
- Summarize the single most important architecture doctrine from this chat.

### 15.2 Decisions

- Which decisions in this chat were clearly accepted by me, and which are still assistant recommendations?
- Which compatibility promises should be made stable first?

### 15.3 Tasks and Next Actions

- Turn AIDE-STRUCTURE-00 into a Codex-ready implementation prompt.
- Turn AIDE-ARCH-00 into a shorter first-pass task that cannot break the build.

### 15.4 Artifacts and Files

- Extract the generated prompts from this report into a standalone implementation queue.
- Create a shorter checklist from the artifact ledger.

### 15.5 Risks and Verification

- What live repo facts must be verified before running Codex?
- Which pasted repo-status claims are most likely stale?

### 15.6 Future Spec Book / Aggregation

- Convert this chat into formal requirements for the master Project Spec Book.
- Compare this chat against another Dominium architecture report and identify conflicts.

### 15.7 Deep-Dive Questions Specific to This Chat

- Define a reusable engine/module boundary model for Dominium.
- Design the exact `contracts/repo/root_constitution.toml` schema.
- Design the exact AIDE move-map and salvage-map schema.

## 16. Compact Human Summary

This chat was about preventing Dominium from becoming a one-off, fragile game repository. The user wanted a structure and engineering doctrine strong enough for a proper long-lived game or OS-like project: portable, modular, extensible, reusable, backwards-compatible where appropriate, and easy to refactor in the future. The conversation began from earlier architecture outputs about repository layout, distribution/install layouts, package formats, runtime roots, component matrices, and root cleanup. The initial answer was that Dominium needs more than one folder tree: it needs a logical-root projection system. Source repo layout, build output, packages, portable installs, installed layouts, media, saves, instances, bundles, diagnostics, cache, staging, rollback, symbols, and provenance should all be governed by shared contracts rather than invented separately.

The source repo target stabilized around a small constitutional root set: `.aide/`, `.github/`, `apps/`, `engine/`, `game/`, `runtime/`, `contracts/`, `content/`, `docs/`, `tests/`, `tools/`, `scripts/`, `cmake/`, `external/`, `release/`, `archive/`, and generated `dist/` only under strict policy. The user’s concern was not simply aesthetic clutter; it was future portability and refactorability. The answer was that root sprawl should be refused by default and new top-level roots should pass a strict admission test.

A major correction came when the user objected to XStack/AuditX/RepoX/TestX-style framing. The user wanted AIDE adopted quickly and existing code/docs/tests recycled rather than ignored. This shifted the plan: AIDE should become the restructuring control plane now. Existing old tools should be inventoried, wrapped, classified, adapted, renamed, or archived through AIDE. They should not be deleted blindly, and their temporary names should not leak into durable Dominium architecture.

The deepest part of the chat reframed Dominium as product-line architecture. Code should be separated by reuse level: reusable across Dominium products, reusable across future games on the same domino/Dominium engine, and reusable across unrelated projects. This implies a strict split: `contracts/` for stable seams and identity; `engine/` for reusable deterministic substrate and domino engine; `game/` for Dominium-specific rules; `runtime/` for host/platform/render/audio/input/network/storage/UI adaptation; `apps/` for thin entrypoints; `content/` for authored data; `release/` for recipes; `tools/` and `.aide/` for validation and refactor machinery.

The most important doctrine is that paths are not identity. Durable things need IDs, versions, schemas, manifests, hashes, capabilities, compatibility ranges, and migration/refusal policy. Public APIs need stability levels. Stable C89-compatible ABI seams are useful, using opaque handles, explicit allocators, versioned structs, and stable error codes, but internals should remain flexible. Schemas and protocols need version negotiation and capability negotiation. Tests should be deterministic and hermetic. Generated outputs should be quarantined. Future refactors should run through AIDE inventory, move maps, salvage maps, reference rewriting, validators, build/test proof, evidence ledgers, and shim retirement.

The best next action is to verify live repo state, then implement AIDE-STRUCTURE-00 and AIDE-ARCH-00 as non-invasive control-plane and architecture-constitution tasks. Do not start broad moves until contracts and inventories exist. Do not trust pasted repo-status claims without verification. Do not treat every assistant recommendation here as an accepted decision. Preserve the uncertainty labels when merging this chat into the future Project Spec Book.
"""

# Registers markdown
registers = f"""# STRUCTURED REGISTERS — {label}

## 17. Workstream Register

{md_table(workstreams, ['ID','Name','Objective','Current state','Desired end state','Status','Priority','Confidence','Label'])}

## 18. Decision Register

{md_table(decisions, ['ID','Decision','Status','Evidence / basis','Rationale','Implications','Related workstream','Confidence','Label'])}

## 19. Task Register

{md_table(tasks, ['ID','Task','Priority','Urgency','Owner','Dependencies','Inputs needed','Expected output','Next step','Related workstream','Label'])}

## 20. Constraint Register

{md_table(constraints, ['ID','Constraint','Type','Hard/soft','Source / basis','Practical implication','Violation risk','Confidence','Label'])}

## 21. User Preference Register

{md_table(prefs, ['ID','Preference','Area','Explicit/inferred/uncertain','Strength','Practical implication','Risk if wrong','Label'])}

## 22. Open Questions Register

{md_table(questions, ['ID','Question / issue','Why it matters','Known information','Unknown information','Resolution path','Priority','Related workstream','Label'])}

## 23. Artifact Ledger

{md_table(artifacts, ['ID','Artifact / file / prompt / output','Type','Purpose','Status','Origin','Carry forward?','Notes','Label'])}

## 24. Rejected / Superseded Options Register

{md_table(rejected, ['ID','Option','Status','Reason','Final or tentative?','Reconsider conditions','Related workstream','Label'])}

## 25. Risk Register

{md_table(risks, ['ID','Risk / failure mode','Consequence','Likelihood','Severity','Mitigation','Related workstream','Label'])}

## 26. Verification Queue

{md_table(verify, ['ID','Item requiring verification','Why verification is needed','Suggested source/type','Priority','Related workstream','Label'])}

## 27. Chronological Timeline Register

{md_table(timeline, ['Sequence','Event / topic','What changed or was decided','Why it mattered','Current relevance','Confidence'])}

## 28. Spec Book Contribution Register

{md_table(spec_contrib, ['Spec-book area','Contribution from this chat','Source IDs','Should become requirement/context/open issue?','Confidence','Notes'])}
"""

context_packet = f"""# 29. Context Transfer Packet for a Future Chat — {label}

## 29.1 Ultra-Condensed Bootstrap Brief

This retired-chat handoff covers a Dominium architecture discussion about making the project portable, modular, extensible, reusable, and refactorable. The user wants Dominium built like a serious long-lived game/engine platform, not a one-off indie repository. The conversation moved from directory cleanup to a broader doctrine: stable root constitution, logical-root projection for distribution/install/package/media/bundles, AIDE as the refactor control plane, product-line reuse boundaries, versioned contracts and manifests, stable API/ABI seams, deterministic data, and mechanical future refactors.

The most important user correction was rejecting XStack/AuditX/RepoX/TestX-style architecture naming. The user wants AIDE adopted quickly and wants existing code/docs/tests recycled, not ignored. Therefore, old tooling should be inventoried, wrapped behind AIDE, classified as keep/adapt/extract/convert/archive/drop, then renamed or retired only after value is preserved.

The recommended stable source roots are `.aide/`, `.github/`, `apps/`, `engine/`, `game/`, `runtime/`, `contracts/`, `content/`, `docs/`, `tests/`, `tools/`, `scripts/`, `cmake/`, `external/`, `release/`, `archive/`, with `dist/` as generated/strictly governed output. New roots are refused by default. Paths are not identity; contracts and manifests define identity. Apps are thin. Runtime owns host adaptation. Engine owns deterministic substrate. Game owns Dominium-specific rules. Tools and AIDE own validation/refactor machinery.

The best next action is to verify live repo state, then implement AIDE-STRUCTURE-00 and AIDE-ARCH-00 as non-invasive scaffolding: root constitution, ownership slots, dependency layers, AIDE policies, move/salvage map schemas, inventory tooling, stability levels, C89 ABI rules, modularity docs, and report-only boundary validators. Do not treat pasted repo-status claims as verified. Do not treat all assistant recommendations as accepted user decisions.

## 29.2 Source Hierarchy

1. Direct user statements in this chat.
2. Explicit decisions accepted by the user, especially AIDE transition and recycling existing material.
3. Current task register.
4. Constraint register.
5. Artifact ledger.
6. Inferences from user goals and assistant responses.
7. Assistant suggestions not explicitly accepted.
8. General software engineering knowledge.

## 29.3 Operating Rules for Future Assistants

Preserve FACT / INFERENCE / UNCERTAIN / PROJECT-CONTEXT labels. Do not assume access to the old chat or live repo. Do not re-ask answered questions. Verify stale facts before relying on them. Do not invent missing details. Do not treat tentative items as final. Do not repeat rejected options, especially XStack-style durable naming or visual folder dragging. Preserve artifacts and registers. Use structured outputs when continuing.

## 29.4 Active Workstreams

Active workstreams are WORKSTREAM-01 through WORKSTREAM-09 from the register: repo constitution, distribution projection, AIDE control plane, old-tool recycling, reusable product-line architecture, contracts/API/ABI discipline, naming/matrix cleanup, determinism/testing/proof, and spec-book aggregation.

## 29.5 Current Priorities

Top priorities: verify repo state; implement AIDE-STRUCTURE-00; inventory/wrap old tooling; implement AIDE-ARCH-00; define logical-root projection contracts; add report-only boundary validators; create portability/determinism checks.

## 29.6 Current Open Questions

The main unresolved issues are: current live repo status; which old tools are useful; exact boundary between domino-engine reusable code and Dominium-specific game code; which APIs become stable; which generated artifacts are intentional; and which recommendations become formal spec requirements.

## 29.7 Recommended First Action

Run a live repo baseline verification, then execute AIDE-STRUCTURE-00 as a non-invasive commit that adds root constitution, AIDE refactor framework, move/salvage schema placeholders, and inventory tooling without moving runtime code.
"""

spec = {
  'spec_sheet': {
    'metadata': {
      'chat_label': label,
      'date_anchor': date_anchor,
      'source_scope': 'This chat only unless labelled PROJECT-CONTEXT',
      'apparent_coverage': 'Partial-to-good for visible chat; no live repo inspection',
      'confidence_1_to_5': 4,
      'staleness_risk': 'Medium',
      'safe_for_aggregation': 'With caveats',
      'main_limitations': ['No live repo verification', 'No full old-chat transcript beyond visible current conversation', 'Prior generated files not available', 'Pasted repo-status claims unverified']
    },
    'summary': {
      'one_sentence': 'This chat defines Dominium as a reusable, portable, contract-driven game/engine platform governed by AIDE-backed refactorability rather than ad hoc folder cleanup.',
      'short_brief': 'The conversation moved from distribution/source layout cleanup to a full modularity and future-proofing doctrine: stable root constitution, logical-root projections, AIDE control plane, product-line reuse boundaries, contracts/manifests as identity, versioned APIs/schemas/protocols, deterministic tests, and mechanical future refactors.',
      'main_topics': [t[0].split('—',1)[1].strip() for t in topics],
      'main_outputs': ['Architecture doctrine', 'AIDE transition plan', 'AIDE-STRUCTURE-00 task', 'AIDE-ARCH-00 task', 'Preservation package'],
      'highest_priority_carry_forward': ['Verify live repo state', 'Implement AIDE-STRUCTURE-00', 'Inventory and wrap old tooling', 'Implement AIDE-ARCH-00']
    },
    'source_rules': {
      'labels_used': ['FACT','INFERENCE','UNCERTAIN / UNVERIFIED','PROJECT-CONTEXT'],
      'conflict_rules': ['User statements outrank assistant suggestions', 'Live repo verification outranks pasted old status', 'Do not silently merge project context'],
      'staleness_rules': ['Repo status, commits, current docs, external tools, and API claims require verification before implementation']
    },
    'user_preferences': {
      'explicit': [p[1] for p in prefs if p[3]=='explicit'],
      'inferred': [p[1] for p in prefs if p[3]=='inferred'],
      'uncertain_or_not_established': ['Exact compatibility windows', 'Exact API stability levels per module', 'How much generated output should be tracked']
    },
    'workstreams': [dict(zip(['id','name','objective','current_state','desired_end_state','status','priority','confidence','label'], w)) for w in workstreams],
    'decisions': [dict(zip(['id','decision','status','evidence_or_basis','rationale','implications','related_workstreams','confidence','label'], d)) for d in decisions],
    'tasks': [dict(zip(['id','task','priority','urgency','owner','dependencies','inputs_needed','expected_output','next_step','related_workstreams','label'], t)) for t in tasks],
    'constraints': [dict(zip(['id','constraint','type','hard_or_soft','source_or_basis','implication','violation_risk','confidence','label'], c)) for c in constraints],
    'open_questions': [dict(zip(['id','question','why_it_matters','known','unknown','resolution_path','priority','related_workstreams','label'], q)) for q in questions],
    'rejected_or_superseded_options': [dict(zip(['id','option','status','reason','final_or_tentative','reconsider_conditions','related_workstreams','label'], r)) for r in rejected],
    'artifacts': [dict(zip(['id','name_or_description','type','purpose','status','origin','carry_forward','notes','label'], a)) for a in artifacts],
    'risks': [dict(zip(['id','risk','consequence','likelihood','severity','mitigation','related_workstreams','label'], r)) for r in risks],
    'verification_queue': [dict(zip(['id','item','why_verification_needed','suggested_source_type','priority','related_workstreams','label'], v)) for v in verify],
    'spec_book_notes': {
      'likely_sections': [s[0] for s in spec_contrib],
      'unique_contributions': ['AIDE-first refactorability doctrine', 'Product-line reuse framing', 'Stable root constitution plus cheap refactors', 'Paths are not identity'],
      'possible_duplicates_with_other_chats': ['Repo layout convergence', 'Distribution layout', 'Component matrices', 'AIDE governance'],
      'conflicts_to_watch_for': ['Old XStack terminology', 'Different root layouts from earlier chats', 'Over-specific renderer/platform priorities'],
      'formal_requirements_candidates': ['Root constitution', 'AIDE work unit process', 'Public API stability levels', 'Logical-root projection', 'Generated-output quarantine'],
      'background_context_candidates': ['Pasted repo status', 'Prior assistant explanations', 'External big-project examples'],
      'needs_user_confirmation': ['Which assistant recommendations become requirements', 'Exact compatibility windows', 'Exact module boundaries']
    },
    'final_recommendations': {
      'next_action_if_continuing_this_chat': 'Verify live repo state and draft AIDE-STRUCTURE-00 as a non-invasive task.',
      'next_action_for_aggregator': 'Merge this as architecture/refactorability doctrine with caveats about unverified repo state.',
      'user_checks_required': ['Confirm AIDE as committed control-plane direction', 'Confirm stable root set', 'Confirm whether AIDE-STRUCTURE-00 or AIDE-ARCH-00 should run first']
    }
  }
}

spec_yaml = yaml.safe_dump(spec, sort_keys=False, allow_unicode=True, width=120)

aggregator = f"""# Aggregator Packet — {label}

## Packet Metadata

* Chat label: {label}
* Date anchor: {date_anchor}
* Source scope: This chat only unless labelled PROJECT-CONTEXT
* Coverage: Partial-to-good for visible current chat; no live repo inspection
* Confidence: 4/5 visible substance; 2/5 live repo facts
* Staleness risk: Medium
* Merge priority: High for architecture doctrine
* Main limitations: Prior generated files unavailable; live repo status unverified; some claims are pasted from earlier assistant outputs.

## Ultra-Condensed Carry-Forward Capsule

This chat should be merged as a major Dominium architecture/refactorability doctrine source. It establishes that Dominium should not be treated as a one-off indie project. It should be developed like a long-lived game/engine platform with stable contracts, replaceable implementations, portable data, deterministic proof, and AIDE-governed refactorability. The core user concern is avoiding another painful restructuring and making code reusable across Dominium products, future games on the same domino/Dominium engine, and potentially unrelated engine or game projects.

The source layout target is a stable constitutional root set: `.aide/`, `.github/`, `apps/`, `engine/`, `game/`, `runtime/`, `contracts/`, `content/`, `docs/`, `tests/`, `tools/`, `scripts/`, `cmake/`, `external/`, `release/`, `archive/`, with `dist/` generated or strictly governed. New top-level roots should be refused by default. Future work should occur inside ownership slots. Root names like `core/`, `lib/`, `libs/`, `packs/`, `profiles/`, `models/`, `modding/`, `security/`, `safety/`, `governance/`, `validation/`, `meta/`, `compat/`, `updates/`, and `performance/` should generally be split into existing roots rather than kept as top-level owners.

A central correction is the user’s rejection of XStack/AuditX/RepoX/TestX-style framing. The merged spec should not preserve those as durable architecture names. Instead, AIDE should be the repo-native control plane for restructuring: inventory, policies, queues, work units, move maps, salvage maps, path aliases, validators, evidence ledgers, and refactor history. Existing old tools and docs should be recycled, not ignored. They should be classified as keep/adapt/extract/convert/archive/drop, wrapped before rename, and migrated only with evidence.

The most important engineering doctrine is: paths are not identity. Contracts and manifests define identity. Durable artifacts need stable IDs, versions, schemas, content hashes where applicable, capability declarations, compatibility ranges, and migration/refusal policy. Apps should be thin. Runtime adapts host/platform/render/audio/input/network/storage/UI. Engine owns deterministic reusable substrate. Game owns Dominium-specific rules. Content is authored data, not runtime cache. Release contains recipes, not generated build products. Tools may inspect everything but must not become runtime dependencies.

For portability and modularity, stable C89-compatible ABI seams should be used where durable external boundaries are needed, with opaque handles, explicit allocators, versioned structs, stable error codes, and no C++/implementation structs in public ABI. Internals should remain flexible. Public APIs need stability levels: experimental, provisional, stable, frozen, deprecated, removed. Schemas and protocols should be versioned, negotiation-capable, and migration-tested. Capability negotiation should replace platform-era assumptions. Generated artifacts must be quarantined. Tests should cover ABI/header compilation, schema round trips, migrations, determinism, replay, save/load, package verification, renderer parity, and command/TUI/GUI parity.

The best next action is to verify live repo state, then implement AIDE-STRUCTURE-00 and AIDE-ARCH-00 non-invasively. Do not move implementation code first. Do not delete old tools. Do not trust pasted repo-status claims without verification. Do not treat every assistant recommendation as user-adopted doctrine until reviewed.

## Top Carry-Forward Items

{md_table([
('P0','AIDE as restructuring control plane','Decision','DECISION-02','Central user correction and future refactor system','FACT','high'),
('P0','Stable root constitution','Decision','DECISION-01','Prevents root sprawl and repeat cleanup','FACT/INFERENCE','high'),
('P0','Paths are not identity','Doctrine','DECISION-04','Makes rewrites/refactors portable and cheap','INFERENCE','high'),
('P0','Product-line architecture','Doctrine','DECISION-05','Supports reuse across products/games/projects','FACT','high'),
('P0','Recycle old tooling/docs/tests','Constraint','DECISION-03','Avoids losing useful validators and policies','FACT','high')], ['Priority','Item','Type','Related ID','Why it matters','Label','Confidence'])}

## Workstream Summaries

"""
for w in workstreams:
    aggregator += f"* ID: {w[0]}\n  * Name: {w[1]}\n  * Objective: {w[2]}\n  * Current state: {w[3]}\n  * Desired end state: {w[4]}\n  * Priority: {w[6]}\n  * Next action: see task register.\n\n"
aggregator += f"""## Compact Registers for Merge

### Decisions

{md_table([(d[0],d[1],d[2],d[6],d[8]) for d in decisions], ['ID','Decision','Status','Workstream','Label'])}

### Tasks

{md_table([(t[0],t[1],t[2],t[3],t[9],t[10]) for t in tasks], ['ID','Task','Priority','Urgency','Workstream','Label'])}

### Constraints

{md_table([(c[0],c[1],c[2],c[3],c[8]) for c in constraints], ['ID','Constraint','Type','Hard/soft','Label'])}

### Open Questions

{md_table([(q[0],q[1],q[6],q[7],q[8]) for q in questions], ['ID','Question','Priority','Workstream','Label'])}

### Artifacts

{md_table([(a[0],a[1],a[2],a[4],a[6],a[8]) for a in artifacts], ['ID','Artifact','Type','Status','Carry forward?','Label'])}

### Risks

{md_table([(r[0],r[1],r[3],r[4],r[7]) for r in risks], ['ID','Risk','Likelihood','Severity','Label'])}

### Verification Queue

{md_table([(v[0],v[1],v[3],v[4],v[6]) for v in verify], ['ID','Item','Suggested source/type','Priority','Label'])}

## Possible Cross-Chat Duplicates

Repo layout convergence, distribution layout, component matrices, renderer/platform naming, AppShell virtual roots, `.dompkg` semantics, AIDE governance, Codex task prompts, previous old-chat handoff packages.

## Possible Cross-Chat Conflicts

Earlier chats may preserve XStack/AuditX/RepoX/TestX terms more strongly. Earlier directory layouts may have different root names. Earlier platform/render priorities may be more implementation-specific. Some previous repo-status claims may conflict with current live repo.

## Spec Book Integration Guidance

Feed this into chapters on repository architecture, AIDE governance, engine modularity, API/ABI/contracts, distribution/install layout, testing/determinism, compatibility, and refactorability. Formalize root constitution, AIDE refactor process, path-is-not-identity doctrine, public API stability levels, and generated-output policy. Keep pasted repo status as background until verified. Do not merge unverified commit IDs or CTest status as current facts.

## Aggregator Warnings

Do not treat this as live repo verification. Do not flatten assistant recommendations into decisions. Do not resurrect XStack as a desired architecture name. Do not ignore the user’s explicit requirement to recycle existing code/docs/tests. Do not compress away the product-line reuse framing.
"""

reader_brief = f"""# Reader Brief — {label}

## What this chat was about

This chat established a future-proofing doctrine for Dominium: stable repository ownership, AIDE-driven refactorability, portable modular code, reusable engine/runtime/contracts, and mechanically enforced compatibility boundaries.

## Top 20 things to know

1. The user wants Dominium built like a serious long-lived game/engine platform.
2. The goal is not just cleaner folders; it is long-term portability and refactorability.
3. A stable root constitution is needed.
4. New top-level roots should be refused by default.
5. AIDE should become the refactor control plane.
6. Old XStack/AuditX/RepoX/TestX-style tools should be recycled, not deleted.
7. Temporary workflow names should not become product architecture.
8. Paths are not identity.
9. Contracts and manifests define identity.
10. Apps should be thin.
11. Runtime owns host adaptation.
12. Engine owns deterministic reusable substrate.
13. Game owns Dominium-specific rules.
14. Content is authored data, not runtime cache.
15. Public APIs need stability levels.
16. Stable C ABI seams should use opaque handles, allocators, versioned structs, error codes.
17. Schemas/protocols need versioning and negotiation.
18. Generated artifacts need quarantine.
19. Future refactors should use AIDE move maps and salvage maps.
20. Live repo status must be verified before implementation.

## Decisions

See DECISION-01 through DECISION-10 in the registers. The clearest user-accepted decisions are AIDE adoption and recycling existing material.

## Pending tasks

Highest priority: verify repo state; implement AIDE-STRUCTURE-00; inventory old tooling; implement AIDE-ARCH-00.

## Open questions

Main questions: current live repo state; useful old tooling; stable API boundaries; reuse-level classification; generated artifact policy; which recommendations become formal requirements.

## Artifacts

The uploaded `Pasted text.txt` prompt requested this preservation package. This package generated Markdown, YAML, and ZIP outputs.

## Verification items

Verify live repo head, CTest/validator status, referenced docs, old tool paths, component matrix names, and prior generated file availability.

## Best next step

Run live repo baseline verification, then implement AIDE-STRUCTURE-00 as a non-invasive control-plane task.
"""

audit = f"""# Verification and Audit — {label}

## 32. Adversarial Self-Audit

{md_table([
('Full live repo not inspected','High','Mark repo facts as UNVERIFIED and add verification queue.','Yes','Implementation still requires repo access.'),
('Prior generated files unavailable','Medium','Do not claim access; list only visible/uploaded artifacts.','Yes','User may need to re-upload files.'),
('Assistant recommendations could be mistaken for decisions','High','Decision statuses distinguish accepted direction from recommendation.','Yes','Manual review still advised.'),
('Report may compress exact prompts too much','Medium','Preserve key AIDE task names and artifact references.','Yes','Original assistant responses should be consulted if exact wording needed.'),
('External best-practice claims from prior answer may be stale','Low-medium','Place in verification queue.','Yes','Verify official docs before citing in spec.'),
('Project context could leak into this-chat scope','Medium','Limit report to visible chat; label PROJECT-CONTEXT where relevant.','Yes','Some model memory shaped interpretation but not registers.'),
('User uploaded only a prompt with no explicit text message','Low','Treat file as active instruction because content explicitly requests action.','Yes','If unintended, user can discard package.')], ['Issue','Severity','Correction needed','Correction applied?','Residual risk'])}

## 33. Corrections Applied

The report marks live repo and older-file claims as unverified; distinguishes accepted user priorities from assistant recommendations; adds verification items for repo state and external references; treats AIDE adoption and recycling as user-backed; treats exact implementation details as pending; and avoids claiming that unavailable older files were accessed.

## 34. Final Reliability Assessment

* Completeness rating: 4/5 for visible chat; 2/5 for unavailable old files/live repo state.
* Reliability rating: 4/5 with uncertainty labels preserved.
* Human-readability rating: 4/5.
* Aggregation-readiness rating: 4/5 with caveats.
* Main remaining uncertainty sources: live repo state, prior generated files, actual old tooling contents, exact user acceptance of each assistant recommendation.
* Manual review before merge: yes, especially before converting recommendations into formal requirements.

## Verification Queue

{md_table(verify, ['ID','Item requiring verification','Why verification is needed','Suggested source/type','Priority','Related workstream','Label'])}
"""

bootstrap_prompt = f"""# Future Chat Bootstrap Prompt — {label}

I am continuing from a retired chat. The following handoff describes the old chat. Treat it as the starting context. Preserve FACT / INFERENCE / UNCERTAIN / PROJECT-CONTEXT labels. Do not assume access to the old chat. Do not re-ask answered questions. Verify stale facts before relying on them. Flag contradictions. Use the task register and open questions to determine next actions.

[PASTE CONTEXT TRANSFER PACKET HERE]

After loading the context, respond with:

1. context loaded;
2. top active priorities;
3. key constraints;
4. open questions;
5. contradictions or uncertainties;
6. recommended next action.

Do not treat assistant recommendations in the packet as user decisions unless labelled as accepted or directly backed by a user statement. Do not resurrect XStack/AuditX/RepoX/TestX as durable Dominium architecture names. Preserve the AIDE-first transition and recycling requirement.
"""

in_chat_reader = f"""# In-Chat Reader — {label}

## Package overview

This package preserves the current chat about Dominium modularity, future-proof structure, AIDE refactorability, and reusable engine architecture. It contains a human-readable report, structured registers, future-chat handoff, YAML spec sheet, aggregator packet, audit, reader brief, and bootstrap prompt.

## File index

1. `00_manifest.md` — file list and package status.
2. `01_human_readable_report.md` — sections 0–16.
3. `02_context_transfer_packet.md` — future-chat handoff.
4. `03_spec_sheet.yaml` — machine-readable aggregation sheet.
5. `04_registers.md` — workstreams, decisions, tasks, constraints, preferences, risks, verification.
6. `05_aggregator_packet.md` — compact merge packet for master spec aggregation.
7. `06_reader_brief.md` — short human reader guide.
8. `07_verification_and_audit.md` — self-audit and verification queue.
9. `08_future_chat_bootstrap_prompt.md` — prompt for a new chat.
10. `09_in_chat_reader.md` — this guide.

## Plain-English explanation

The chat’s core contribution is that Dominium needs stable ownership roots, AIDE-driven refactor mechanics, and strict separation of reusable engine/runtime/contracts from Dominium-specific game rules. The main next action is to verify live repo state and implement non-invasive AIDE structure and architecture contracts.

## Question menu

Ask: “Which decisions are accepted versus recommendations?”, “Draft the AIDE-STRUCTURE-00 Codex prompt”, “Design root_constitution.toml”, “What repo facts must be verified?”, “How should old XStack-style tools be recycled?”, or “Turn this into Project Spec Book requirements.”

## Top things to preserve

AIDE-first control plane; recycle existing tools/docs/tests; paths are not identity; stable root constitution; product-line architecture; public API stability levels; deterministic proof matrix.

## Safest next actions

Verify repo baseline, add AIDE scaffolding, inventory old tooling, then add modularity/reuse contracts. Avoid broad moves first.
"""

# Manifest after file list
file_names = [
 f'{safe}__00_manifest.md', f'{safe}__01_human_readable_report.md', f'{safe}__02_context_transfer_packet.md',
 f'{safe}__03_spec_sheet.yaml', f'{safe}__04_registers.md', f'{safe}__05_aggregator_packet.md',
 f'{safe}__06_reader_brief.md', f'{safe}__07_verification_and_audit.md', f'{safe}__08_future_chat_bootstrap_prompt.md',
 f'{safe}__09_in_chat_reader.md'
]
manifest = f"""# Manifest — {label}

Created: {created}
Date anchor: {date_anchor}
Source scope: This chat only unless labelled PROJECT-CONTEXT.

## Files created

{md_table([
(file_names[0],'Manifest','Index, purpose, counts, caveats, package status','Human + aggregator','High'),
(file_names[1],'Human-readable report','Sections 0–16: orientation, story, topics, decisions, plans, risks, summary','Human','Highest'),
(file_names[2],'Context transfer packet','Section 29 for future chat bootstrap','Future assistant','High'),
(file_names[3],'Spec sheet','Section 30 in YAML-style format','Aggregator/machine-assisted merge','High'),
(file_names[4],'Registers','Sections 17–28 with stable IDs','Human + aggregator','High'),
(file_names[5],'Aggregator packet','Section 31 compact merge packet','Central aggregator chat','High'),
(file_names[6],'Reader brief','Shorter human guide and top 20 things','Human','Medium-high'),
(file_names[7],'Verification and audit','Sections 32–34 plus verification queue','Reviewer','High'),
(file_names[8],'Future chat bootstrap prompt','Standalone prompt to continue from handoff','Future chat','Medium-high'),
(file_names[9],'In-chat reader','Package overview and question menu','Human','Medium')], ['File','Purpose','What it contains','Intended reader','Importance'])}

## Item counts

* Workstreams: {len(workstreams)}
* Decisions: {len(decisions)}
* Tasks: {len(tasks)}
* Constraints: {len(constraints)}
* Preferences: {len(prefs)}
* Open questions: {len(questions)}
* Artifacts: {len(artifacts)}
* Rejected/superseded options: {len(rejected)}
* Risks: {len(risks)}
* Verification items: {len(verify)}
* Timeline events: {len(timeline)}

## Main caveats

No live repo inspection was performed. Some prior generated files/old uploads are unavailable. Pasted repo-status claims are preserved as chat content but require verification before implementation. Assistant recommendations are not automatically user decisions.

## Final package status

Files created: yes. ZIP created: yes. Safe for later aggregation: with caveats.
"""

files = {
 file_names[0]: manifest,
 file_names[1]: report,
 file_names[2]: context_packet,
 file_names[3]: spec_yaml,
 file_names[4]: registers,
 file_names[5]: aggregator,
 file_names[6]: reader_brief,
 file_names[7]: audit,
 file_names[8]: bootstrap_prompt,
 file_names[9]: in_chat_reader,
}
for name, content in files.items():
    (out/name).write_text(content, encoding='utf-8')
zip_name = f'{safe}__handoff_package.zip'
with ZipFile(out/zip_name, 'w', ZIP_DEFLATED) as z:
    for name in file_names:
        z.write(out/name, arcname=name)
print('created', len(files), 'files and zip', zip_name)
print('\n'.join(file_names+[zip_name]))
