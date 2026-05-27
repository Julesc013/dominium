# COMPLETE CHAT PRESERVATION REPORT — Dominium Canonical Architecture, Repository Foundation, and Provider Model

## 0. Coverage and Reliability Assessment

| Field | Assessment |
|---|---|
| Chat label | Dominium Canonical Architecture, Repository Foundation, and Provider Model |
| Date anchor | 2026-05-27 Australia/Melbourne |
| Source scope | This chat only, except where explicitly marked PROJECT-CONTEXT |
| Apparent access | Partial |
| Previously generated files available? | Yes: prior generated Markdown/plain-text handoff files are present in `/mnt/data`; older uploaded-file context has partly expired. |
| Uploaded files or artifacts present? | Yes: the preservation prompt, multiple directory-tree/report bundles, and prior handoff files are available in the sandbox. Some older uploaded files are expired or unavailable through file search. |
| Contains future plans? | Yes |
| Contains decisions? | Yes, with caveats: some were explicit user acceptances; many were assistant recommendations that the user explored, refined, or sent to other chats. |
| Contains pending tasks? | Yes |
| Contains unresolved questions? | Yes |
| Staleness risk | Medium to High for current repo state, library version facts, and live validation results; Low for conversation-internal doctrine and user preferences. |
| Extraction confidence | 4/5 for visible conversation substance; 3/5 for exact sequence because portions of the transcript are skipped/expired. |
| Safe for later aggregation? | Yes, with caveats |
| Main limitations | The visible conversation includes skipped message markers; some uploaded files expired; live repo state reports changed repeatedly; several “current” statuses came from user-provided summaries and should be verified before acting. |

Plain-language limitation note: this report reconstructs this chat from the visible transcript, the user’s embedded status summaries, and available sandbox files. It cannot guarantee perfect coverage of turns hidden behind “Skipped messages” markers or expired uploaded files. Where the chat reported repo commits, tests, and live validation statuses, those are preserved as FACTs **as reported in the chat**, not independently verified current repository truth unless explicitly noted.


## 1. One-Page Orientation

This chat was an extended architecture, repository-structure, and project-governance conversation for the Dominium game/project. The user’s core concern was that months of planning and refactoring had stalled actual development and that the repository had repeatedly grown new root directories, duplicate taxonomies, generic `src/`/`source/` wrappers, and unclear ownership boundaries. The user wanted to force the project toward a durable, future-proof structure before building Workbench, the client, the engine, the game systems, modules, packs, renderers, and provider integrations.

The conversation evolved from immediate directory cleanup into a much larger design model. The early problem was physical: too many roots, duplicate structures, vague names, product-specific code in reusable places, pack payloads mixed with package contracts, schemas organized around old roots, tests and docs mirroring obsolete paths, and tools acting like a second source tree. The user repeatedly challenged weak or over-broad directory proposals, especially ones that reintroduced `src/`, new top-level roots, long product names, status words like `legacy`/`modern`, and vendor-shaped structure.

The durable architectural answer that emerged was that the top-level root model should remain small and closed: `apps/`, `engine/`, `game/`, `runtime/`, `contracts/`, `content/`, `docs/`, `tests/`, `tools/`, `scripts/`, `cmake/`, `external/`, `release/`, and `archive/`, plus project/tooling roots like `.aide/`, `.github/`, and `.vscode/`. Generated/local roots such as `.dominium.local/`, `build/`, `out/`, `dist/`, `artifacts/`, and `reports/` must not become active source authority. The most important naming and ownership rule became: no new top-level roots unless a root contract intentionally allows them; no first-party `src/` or `source/`; no generic junk drawers like `core`, `shared`, `common`, `misc`, `lib`, or `data` in active source.

As the chat deepened, the model became less about folders and more about stable public surfaces. The user wanted modularity strong enough that code, directories, renderers, providers, and even large implementations could be replaced later without breaking saves, packs, mods, replays, or downstream games. The key doctrine became: **stable semantic IDs, stable public contracts, replaceable private implementations, and proof before promotion.** The assistant and user converged on “Domino” as the reusable deterministic substrate/framework layer, “Dominium” as one game/product family built on Domino, “Workbench” as the production/editing/validation/evidence environment, and “AIDE” as the repo/control-plane harness. Contracts define law; runtime implements services/projections/providers; apps compose products; content supplies authored payloads; tools validate/generate/migrate/audit; tests/replay/evidence prove behavior; archive preserves history without active authority.

The conversation produced many Codex/AIDE mega-prompts for concrete cleanup: runtime names, game rules, engine include boundaries, pack authority, schema canonicalization, content pack layout, apps-thin enforcement, Workbench naming, AIDE scan boundaries, tools/docs/test taxonomy cleanup, RepoX/TestX proof repair, full remediation, dependency-direction repair, provider structure, framework boundary, and full-gate legacy path routing. Several user status reports said these tasks landed with commits and passing validations, though many still ended `PASS_WITH_WARNINGS` rather than full green.

The current end-state of the chat is not “everything is perfect.” It is that the old root/directory crisis is largely resolved, while full release proof, full CTest, stale generated evidence, provider implementation, presentation/projection conformance, pack internal layout, and remaining warning buckets remain future work. The best next direction identified in the chat is not more giant structure thrashing, but targeted proof hygiene and governed product-spine work: clean stale full-gate/generated evidence, continue presentation/projection contracts, build provider conformance, and use raylib/SDL2/Lua as fenced providers rather than architecture.


## 2. The Story of the Conversation

### 2.1 From directory frustration to canonical root doctrine

The user began from intense frustration: months of planning had not produced enough actual development, and the repository still looked structurally unstable. The recurring symptom was root sprawl: new top-level folders, repeated `src/`/`source/` wrappers, redundant `appcore`/`appshell`/`shell` variants, product-specific roots, and duplicate plural/singular taxonomies. The user emphasized that the original warning sign was the assistant repeatedly adding new root directories and source folders despite the repo doctrine forbidding that pattern.

The first major conclusion was that the repo needed a closed set of ownership roots, not a new clever hierarchy. The top-level roots were settled as the standard canonical model: `apps`, `engine`, `game`, `runtime`, `contracts`, `content`, `docs`, `tests`, `tools`, `scripts`, `cmake`, `external`, `release`, and `archive`, with AIDE/GitHub/editor roots allowed. This did not mean every internal directory was perfect; it meant root churn should stop.

### 2.2 From structure to enforcement

The discussion then shifted from “what should the folders be?” to “how do we stop the repo from drifting again?” The user and assistant emphasized validators, allowlists, no-src/source rules, forbidden path terms, generated/local roots, bad-root absence, docs/tools/test taxonomy checks, dependency direction, and structure report integrity. The user asked repeatedly whether the repo was fixed after each status report, and the assistant kept distinguishing top-level success from internal residual debt.

This produced a pattern: generate a large Codex/AIDE task, the user ran it or reported a result, then the assistant evaluated what was truly fixed versus what was only validator/document churn. The user eventually demanded a one-shot “actual final cleanup” prompt because previous passes had sometimes added validators without moving directories. That prompt explicitly required real `git mv` routing, not just reports.

### 2.3 Converging on Domino, Dominium, Workbench, AIDE

Over time, the project model became clearer. Domino was defined as the reusable deterministic/runtime substrate; Dominium as the specific game/product family; Workbench as a production environment for editing, validation, inspection, packaging, UI authoring, evidence, and agent workflows; and AIDE as the repo/control-plane harness. This distinction mattered because the user wanted code and data reusable not only for Dominium but for other games or engine projects.

The assistant proposed that the framework should not be a new top-level `framework/` root. Instead, “Domino Framework” should be the public surface package formed by contracts, public headers, service/provider law, ABI law, conformance tests, and release profiles. The actual engine implementation remains in `engine/` and `runtime/`; the Dominium game implementation remains in `game/`, `content/`, and `apps/`.

### 2.4 From folders to public surfaces, APIs, ABIs, and compatibility

A major part of the chat concerned how to make code portable, modular, extensible, and replaceable. The user wanted stable C APIs where possible but also needed modern implementation power. The plan evolved from older C89/C++98 ambitions to a C17/C++17 mainline, while keeping the public ABI C-compatible, POD-only, versioned, and free of C++ ABI leakage. The user also considered C99/pure C/C++11 alternatives, but the settled doctrine was: C17 for boring law, ABI-facing types, packets, saves/replays, deterministic math, and low-level facades; C++17 for game orchestration, runtime services, providers, Workbench, tools, resource ownership, and large modular machinery.

The chat repeatedly emphasized that the stable boundary is not a folder; it is a registered public surface: C headers, ABI tables, schemas, protocols, command/view/event/refusal contracts, package/save/replay/profile formats, provider ABIs, capability IDs, diagnostic codes, and release artifacts. This motivated future tasks such as Public Surface Registry, API/ABI Canon, Dependency Direction, Compatibility Corpus, Replacement Protocol, Capability/Refusal Law, Provider Model, Presentation Contract, and Projection Conformance.

### 2.5 Workbench and the semantic spine

The Workbench brainstorming originally proposed large user-facing workspaces such as Project Editor, Interface Studio, Module/Pack Foundry, and App Composer. The discussion refined this: those are workspaces, not primitive modules. The system should distinguish components, services, providers, packs, modules, workspaces, apps, and artifacts. A module is a declared functional extension unit, not just a folder. A Workbench module is one consumer of the general module system, not the module system itself.

The presentation architecture also matured. CLI, TUI/text, rendered GUI, native GUI, and headless reports should not become separate systems. They should be projections over the same semantic spine: intent → command → capability/refusal check → service → result/document/snapshot → diagnostics/evidence → view → action model → projection → shell. This led to the recommendation for `PRESENTATION-CONTRACT-01` and `PROJECTION-CONFORMANCE-01`.

### 2.6 Provider model and third-party acceleration

Later the chat considered raylib, SDL2, Lua, raygui, rlgl, rlsw, raudio, and Dear ImGui. The user was dissatisfied with vendor-shaped structures, and the assistant refined the model: use raylib aggressively, but only as replaceable providers behind Dominium/Domino service contracts. SDL2 is a platform/input/audio provider family; Lua is a pinned script provider; raygui and ImGui are UI providers; rlgl and rlsw are raylib ecosystem render providers. Third-party types must not leak into engine, game, contracts, content, saves, replays, public SDK headers, or deterministic game law.

The final provider directory doctrine became service-first: `runtime/<service>/providers/<provider>/`, not `runtime/<vendor>/<service>/`. Provider choices belong in `release/profiles/` or `content/profiles/`, not app path names. External code belongs under `external/upstream/` or `external/vendor/`, but the repo should choose one convention.

### 2.7 Current reported state

By the end, user reports indicated that several actual cleanup commits landed. Important reported commits included provider-structure work, actual final structure cleanup, full-gate legacy path routing, and Domino framework boundary definition. The assistant judged the repo as structurally credible, with canonical structure and old active paths mostly clean, but not perfect. Full CTest/full-gate release proof remained ungreen, with stale AuditX/identity evidence, launcher marker debt, and other full-gate warnings still needing targeted maintenance. The final conclusion was that broad structure cleanup should largely stop; future work should be targeted proof hygiene and governed product-spine tasks.


## 3. Main Topics Discussed

### Topic 1 — Canonical repository root structure

The chat repeatedly returned to the question of which top-level roots should exist. The conclusion was that the root set should be closed and stable: `apps/`, `engine/`, `game/`, `runtime/`, `contracts/`, `content/`, `docs/`, `tests/`, `tools/`, `scripts/`, `cmake/`, `external/`, `release/`, and `archive/`, plus `.aide/`, `.aide.local.example/`, `.github/`, and `.vscode/`. The user strongly rejected proposals that reintroduced `src/`, `source/`, new top-level `modules/`, `plugins/`, `profiles/`, `labs/`, `framework/`, or `sdk/` roots. The goal was to keep roots as durable ownership planes, not topic buckets.

### Topic 2 — Source layout versus runtime/install/package layout

A recurring distinction was that source repo layout is not runtime/install/media/package layout. `store/`, `instances/`, `saves/`, `exports/`, `cache/`, `ops/`, portable install roots, media layouts, and `.dompkg` package projections are runtime/distribution concepts, not source roots. The conversation repeatedly separated build output, portable installs, installed layout, package cache, save bundles, instance bundles, diagnostics bundles, and source repo structure.

### Topic 3 — Apps, runtime, engine, game, contracts, content ownership

The chat developed strong ownership rules. `apps/` are thin product shells. `engine/` is deterministic substrate. `game/` is Dominium law, rule, world, and domain meaning. `runtime/` adapts host/platform/render/input/audio/network/storage/package/UI/services and implements projections/providers. `contracts/` is machine-readable law. `content/` is authored payload. `tools/` is repo-only machinery. `archive/` is inactive history/evidence.

### Topic 4 — Public surface, API, ABI, and language baseline

The user wanted reusable code not only for Dominium but for other games and engine projects. The conclusion was that stable public surfaces matter more than frozen folders. The repo should use C17 + C++17 as the active mainline baseline, with a C-compatible public ABI: opaque handles, versioned structs, fixed-width types, explicit allocation/lifetime rules, no STL/C++ ABI across public boundaries, no exceptions crossing ABI, and no raw object-layout serialization.

### Topic 5 — Dependency direction and replacement

A key design target was replaceability: whole implementations or directories should be rewritable behind stable contracts. Dependency direction became a crucial enforcement layer: apps may depend on runtime/game/contracts; game may depend on engine/contracts; runtime may depend on engine/contracts; engine must not depend on runtime/game/apps; contracts must not import implementation; runtime must not depend on tools; archive must not be active dependency. Replacement should be governed by replacement packets, conformance tests, compatibility corpora, and proof artifacts.

### Topic 6 — Workbench, modules, workspaces, and composition

The Workbench discussion distinguished workspaces from modules. Workspaces are large human-facing compositions like Project Graph, Interface Studio, Module Foundry, App Composer, and Release Forge. Workbench modules are smaller UI/functional units like validation dashboard, pack browser, evidence viewer, replay trace, renderer lab, and agent board. The general module system belongs in `contracts/module/` and manifests; Workbench modules are only one consumer.

### Topic 7 — Presentation and UI architecture

The user and assistant converged on a shared presentation spine: CLI, text/TUI, rendered GUI, native GUI, and headless should project the same command/result/refusal/document/view/action/evidence contracts. Contracts define semantic surfaces; runtime implements projection machinery; apps compose products; Workbench hosts workflows. Presentation modes should not become separate semantic authorities.

### Topic 8 — Packs, profiles, saves, replays, and artifacts

Packs are distributable authored payloads. The preferred pack layout became category-based, such as `content/packs/<category>/<pack_id>/`. Pack IDs must not depend on paths. Saves and replays must use stable IDs, schema versions, canonical serialization, deterministic hashes, and explicit migration/refusal policies. Backward compatibility must be a compatibility corpus plus tests, not intention.

### Topic 9 — Provider model, raylib, SDL2, Lua, and third-party boundaries

The later chat focused on raylib/SDL/Lua and other third-party accelerators. The doctrine became service-first and provider-backed: `runtime/<service>/providers/<provider>/`; external code under `external/upstream/` or `external/vendor/`; provider selection in profiles; third-party types fenced out of engine/game/contracts/content/saves/replays. Raylib is a seed provider suite, SDL2 a platform/input/audio provider, Lua a pinned script provider, raygui/ImGui UI providers, and rlgl/rlsw render providers.

### Topic 10 — Validators, proof gates, and full-gate debt

The chat produced a strong proof model. Fast strict is the normal development gate, while full CTest/full proof is T4/full-gate debt. Many validators were discussed: root allowlist, bad-root, no-src/source, forbidden names, canonical structure, dependency direction, public surface, provider structure, third-party include, report integrity, schema taxonomy, content layout, Workbench taxonomy, docs/tools/test taxonomy, and full-gate legacy paths. Full release readiness remains blocked until full-gate failures are resolved.


## 4. What We Were Trying to Achieve

### 4.1 Explicit Goals

The user explicitly wanted to stop the repository from blocking development. They wanted the directory structure fixed, not endlessly discussed. They wanted no more root sprawl, no `src/`/`source/` wrappers, no generic buckets, no long meaningless paths, and no vendor/product-shaped architecture. They wanted a repo structure suitable for a serious reusable game/engine platform rather than a one-off indie project. They also wanted future chats to have enough context to continue without re-explaining everything.

### 4.2 Inferred Goals

INFERENCE: The user wanted a durable method for deciding future structure changes, not just a one-time layout. They also wanted the assistant to become more rigorous: distinguish decisions from brainstorms, stop over-planning without execution, and preserve uncertainty. The user also wanted a structure that supports other Domino-based games and possibly different engine implementations.

### 4.3 Goals That Changed Over Time

The goal shifted from “fix folders” to “define stable public surfaces and make private implementations replaceable.” It also shifted from old C89/C++98 portability ambition to C17/C++17 mainline with C-compatible public ABI. Workbench shifted from a monolithic editor idea to a projection/command/workspace system over shared contracts. Raylib shifted from a possible app framework to a fenced provider suite.

### 4.4 Goals Still Unresolved

Full release proof is not green. Some warning buckets remain: generated evidence, full CTest/T4 failures, provider runtime implementation, presentation/projection conformance, pack internal layout, public ABI promotion, and possibly AIDE state classification. The user still needs to decide when “good enough” for product work is reached versus continuing maintenance cleanup.


## 5. Decisions Made and Why

### Decision overview

| ID | Decision | Status | Why it mattered | Confidence | Label |
|---|---|---|---|---|---|
| DECISION-01 | Keep a closed top-level root model | Accepted/current | Prevents root sprawl and repeated refactor churn | High | FACT |
| DECISION-02 | No first-party `src/`/`source/` wrappers | Accepted/current | Avoids meaningless nesting and ownership ambiguity | High | FACT |
| DECISION-03 | Domino is reusable substrate; Dominium is game/product family | Accepted/current | Enables reuse by other games/projects | High | FACT/INFERENCE |
| DECISION-04 | Workbench is not authority; contracts/commands/services are authority | Accepted/current | Prevents GUI-specific product logic | High | FACT |
| DECISION-05 | C17 + C++17 mainline, C-compatible public ABI | Accepted/current | Balances implementation power with portability and stable ABI | Medium-High | FACT as discussed; external details require verification |
| DECISION-06 | Service-first provider structure | Accepted/current | Keeps raylib/SDL/Lua replaceable | High | FACT |
| DECISION-07 | Do not add top-level `framework/` root | Accepted/current | Avoids competing public API roots | High | FACT |
| DECISION-08 | Profiles select providers; apps remain generic | Accepted/current | Prevents product variants from becoming directory architecture | High | FACT |
| DECISION-09 | Full CTest is full-gate debt, not normal daily gate | Accepted/current | Keeps development usable while preserving release proof | Medium-High | FACT from reports |
| DECISION-10 | Continue with targeted tasks, not giant structure passes, after cleanup credibility | Current recommendation | Prevents churn after structure is credible | Medium | INFERENCE |

### Explanatory decision notes

The closed root model was the most emotionally and technically important decision. The user repeatedly objected to root proliferation; the final root set became the anchor for all later advice. This decision affects every future proposal: if a concept can fit under an existing root, it should not become a new top-level root.

The no-`src` rule was also critical. The user considered repeated `src/` and `source/` folders as a central symptom of bad architecture. The final doctrine is that ownership directories are already source roots; implementation should live under meaningful module/subsystem folders, not generic `src` wrappers.

The Domino/Dominium split emerged as the long-term reuse strategy. Domino is the framework/substrate identity; Dominium is one game/product family. This lets the current repo host Dominium while still exposing reusable runtime/engine/contract/provider surfaces.

The framework-boundary decision rejected a top-level `framework/` root. The accepted model is that Domino Framework exists as public surfaces, ABI headers, contracts, and provider/service law. This prevents root sprawl while still supporting SDK/export concepts later.

The provider model decision was a major response to raylib/SDL/Lua discussions. Third-party libraries should be providers behind first-party service contracts. They can accelerate visible progress but must not own saved data, game law, public ABI, or content schemas.


## 6. Ideas Considered but Rejected, Superseded, or Deprioritised

| Option | Status | Reason |
|---|---|---|
| Top-level `src/` or repeated module `src/` folders | Rejected | Violates explicit repo doctrine and user preference. |
| New top-level `framework/` | Rejected | Framework identity should be public surfaces/contracts/headers, not another root. |
| Top-level `modules/`, `plugins/`, `services/`, `profiles/`, `labs/` | Rejected for now | Concepts fit under contracts/runtime/content/release/apps/tools. |
| Vendor-shaped structure such as `runtime/raylib/render` | Rejected | Repo should be service-first, provider-backed. |
| Product variants like `apps/client/rendered/raylib` as architecture | Rejected except temporary proof bootstraps | Apps should be generic; profiles select providers. |
| Pure C99 or pure C++11 baseline | Rejected | C17+C++17 better matches project scale and target floor. |
| C89/C++98 as active mainline | Superseded | Preserved as historical/research lane, not mainline. |
| Workbench as authority | Rejected | Workbench must consume command/view/document/evidence contracts. |
| `content/modules/` and `content/builtin/` as broad roots | Rejected | Packs are distributable payload units; modules are manifest-defined. |
| Separate contract roots for every UI mode (`contracts/tui`, `contracts/native`) | Rejected | UI modes are projections; contracts should remain semantic. |


## 7. Important Reasoning, Rationale, and Tradeoffs

The central tradeoff was between speed and long-term architectural integrity. The user wanted immediate progress after months of structure work, but also wanted to avoid repeating the same cleanup cycle. The resulting strategy became: enforce enough structure to prevent collapse, then proceed with narrow governed product slices instead of waiting for every possible governance layer to be perfect.

Another major tradeoff was between stable APIs and replaceable internals. The chat rejected the idea that every folder or private helper must be stable. Instead, stable identity lives in contracts, manifests, registries, public headers, artifact IDs, and compatibility tests. Private directories and implementations can move or be rewritten if public surfaces and compatibility proofs remain intact.

The raylib/SDL/Lua discussion raised a speed-versus-lock-in tradeoff. Raylib can accelerate rendering, audio, input, and Workbench prototypes. SDL2 can provide robust platform/input/audio provider roles. Lua can enable scripting and automation. But none should become architecture law. The solution was provider manifests, forbidden include validators, conformance tests, and profile-selected provider combinations.

The Workbench discussion involved a similar tradeoff. The user wanted powerful authoring workspaces, but the architecture must not make Workbench a privileged bypass. Therefore, Workbench modules and workspaces should operate through the same commands, views, actions, documents, diagnostics, and evidence packets that CLI, CI, headless, server, and future apps use.

A persistent uncertainty is the exact current repo state. The user supplied many status reports and directory exports, but several exports were internally inconsistent or stale at various points. The chat therefore repeatedly emphasized structure report integrity and verification before trusting tree analyses.


## 8. Plans, Future Work, and Next Steps

The visible next work falls into three tracks.

### 8.1 Maintenance / proof hygiene

The strongest immediate maintenance tasks are: refresh stale generated evidence, repair launcher pack-verification marker debt if still blocking fast strict, run or audit full CTest/T4 failures, and classify remaining full-gate failures by cause. The task names discussed include `FULL-GATE-GENERATED-EVIDENCE-REFRESH-01`, `FAST-STRICT-EVIDENCE-MARKER-REPAIR-01`, and `FULL-CTEST-AUDIT-NONPATH-01`.

### 8.2 Architecture/product-spine mainline

Mainline tasks discussed include `PRESENTATION-CONTRACT-01`, `PROJECTION-CONFORMANCE-01`, `COMMAND-RESULT-VIEW-SLICE-01`, `PACKAGE-MOUNT-SLICE-01`, and `WORKBENCH-VALIDATION-SLICE-01`. The rule is to prove narrow slices before broad UI, gameplay, renderer, provider runtime, or package runtime expansion.

### 8.3 Provider/third-party implementation

The provider path includes `PROVIDER-WEDGE-01`, `RAYLIB-SEED-PROVIDER-01`, `SDL2-PROVIDER-01`, `LUA-PROVIDER-PIN-01`, and follow-ups for render/draw/software/OpenGL/Direct3D/native platform providers. The structure rule is service-first: `runtime/<service>/providers/<provider>/`, with provider choices in profiles.

### Recommended sequence as of the chat’s end

1. Verify fast-strict/RepoX/structure report status from a clean current export.
2. If fast-strict is blocked, repair stale generated evidence/markers first.
3. If fast-strict is green, proceed to `PROJECTION-CONFORMANCE-01` or `PRESENTATION-CONTRACT-01` depending the live queue.
4. Do not run broad structure cleanup unless a validator reports hard active-path blockers.
5. Keep full CTest/T4 debt as release-gate work, not normal development gating.


## 9. Constraints, Preferences, and Non-Negotiables

### 9.1 Explicit Constraints and Preferences

- The user wants direct, audit-ready, source-grounded answers.
- The user dislikes vague reassurance and wants uncertainty labelled.
- The user wants no root sprawl, no arbitrary new top-level roots, and no repeated `src/`/`source/` wrappers.
- The user wants structure to support modularity, portability, extensibility, reuse, modding, backwards compatibility, and future replacement.
- The user strongly prefers actual execution/move prompts over endless micro-planning when structure is blocking work.
- The user wants future assistants not to treat assistant brainstorms as accepted decisions unless accepted by the user.

### 9.2 Inferred Constraints and Preferences

- INFERENCE: The user prefers aggressive cleanup when structural debt is blocking product work, but increasingly accepts targeted tasks once structure is credible.
- INFERENCE: The user values consistent vocabulary: component, service, provider, pack, module, workspace, app, artifact.
- INFERENCE: The user wants the repo to behave more like a long-lived engine/platform or OS-grade project than a one-off game.

### 9.3 Uncertain or Unestablished Preferences

- UNCERTAIN: The final exact convention for `external/upstream` versus `external/vendor` should be checked against current repo policy.
- UNCERTAIN: Whether Lua should be pinned to 5.4 or 5.5 is not settled in this chat.
- UNCERTAIN: Whether pack-internal `content/` directories are legitimate pack law or legacy remains to be verified.


## 10. Files, Artifacts, Outputs, and Prompts

Important artifacts in or associated with this chat include:

- `dominium_canonical_handoff.md` and `dominium_canonical_handoff.txt`: earlier generated handoff files summarizing a major phase of the repository/architecture discussion. Preserve and compare with this preservation package.
- Multiple directory-tree/report bundles: `dir_tree.json`, `dir_tree.txt`, `dirfiles_manifest.json`, `dirfiles_run.log`, `dirfiles.zip`. These were used to assess repo structure repeatedly. Several bundles were stale or internally inconsistent, which became a major risk and motivated report-integrity validators.
- `Pasted text.txt`: the uploaded preservation-package instruction that triggered this report.
- Numerous Codex/AIDE mega-prompts generated in-chat, including but not limited to: `RUNTIME-NAME-01`, `PACK-AUTHORITY-01`, `SCHEMA-CANON-01`, `CONTENT-PACK-CANON-01`, `APPS-THIN-01`, `WORKBENCH-NAME-01`, `AIDE-SCAN-BOUNDARY-01`, `TOOLS-FOLD-01`, `DOCS-CANON-01`, `REPOX-TESTX-CANON-PATHS-01`, `CANON-REMEDIATION-FULL-PROOF-01`, `REPOX-STRICT-DEBT-01`, `CANON-TASK-STATUS-RECONCILE-01`, `API-ABI-CANON-01`, `PUBLIC-SURFACE-REGISTRY-01`, `PROVIDER-STRUCTURE-CANON-01`, `CANON-STRUCTURE-ACTUAL-FINAL-CLEANUP-01`, and more.
- User-reported commits and status summaries: these include commits like `6e0dd93`, `1406490`, `3243fab`, `ce9ca`, and others. Treat them as FACTs reported in the chat, but verify live repo state before acting.
- Generated reports/audits mentioned by the user: `CANON_STRUCTURE_ACTUAL_FINAL_CLEANUP_01.md`, `FULL_GATE_LEGACY_TEST_ROUTE_01.md`, `PROVIDER_STRUCTURE_CANON_01.md`, `domino_framework_boundary.md`, and many AIDE/RepoX/TestX reports.


## 11. Open Questions and Unresolved Issues

- Is full CTest currently green? The chat repeatedly says no or not run; verify before any release/trust claim.
- Are stale AuditX/identity evidence and launcher marker debt still blocking fast strict? User reports changed over time; verify live.
- Are provider split warnings for storage/package still present? If yes, finish `STORAGE-PACKAGE-PROVIDER-SPLIT-01`.
- Are pack-internal `content/` directories canonical or legacy? This needs a pack-law decision.
- Are `.aide/cache`, `.aide/queue`, `.aide/reports`, and `.aide/ledgers` canonical control-plane state or mutable local state?
- Is the final live queue pointing to `PROJECTION-CONFORMANCE-01`, `PRESENTATION-CONTRACT-01`, or a maintenance task? Verify current `.aide/queue/current.toml`.
- Which Lua version should be pinned if/when Lua provider work begins?
- Should `external/upstream` or `external/vendor` be canonical? Verify current repo convention.


## 12. Risks, Failure Modes, and What Future Chats Might Get Wrong

Future assistants may think the directory structure is either completely broken or completely done. The correct state is more nuanced: broad structure appears credible, but release/full proof and warning debt remain.

A future assistant might also reintroduce top-level roots like `framework`, `profiles`, `labs`, `modules`, or `plugins`. This should be avoided unless the repo’s root contract explicitly changes.

Another risk is treating raylib, SDL2, Lua, ImGui, raygui, rlgl, rlsw, or raudio as architecture instead of providers. These libraries should be fenced behind service contracts and provider manifests.

A future assistant might over-trust stale directory exports. Structure-report integrity was a recurring issue. Always check commit, branch, dirty state, source mode, and hashes before using uploaded structure reports as truth.

A future assistant might also confuse Workbench modules with the general module system. Workbench modules are product UI modules; general module law belongs in contracts and manifests.


## 13. What This Chat Contributes to the Larger Project or Future Spec Book

This chat should feed major sections of a future Dominium/Domino Project Spec Book:

- Repository layout and ownership model.
- Domino Framework boundary and public surface registry.
- C17/C++17 language baseline and C-compatible ABI rules.
- Dependency-direction law.
- Service/provider/profile architecture.
- Workbench/module/workspace model.
- Presentation/projection semantic spine.
- Pack/content/profile/artifact identity law.
- Third-party provider fencing for raylib, SDL2, Lua, raygui, ImGui, rlgl, rlsw, and raudio.
- Proof gates, fast strict, full CTest/T4, and full-gate legacy routing.
- AIDE/Codex workflow and structure-report integrity.

Formal requirements candidates include: no top-level root sprawl; no first-party `src/source`; path is not identity; public surfaces must be registered; apps compose, runtime implements, contracts define; provider implementations must not leak third-party types across stable boundaries; full release proof requires full-gate green.


## 14. What I Should Remember

- The repo’s top-level root model is settled; do not redesign it casually.
- The user was angry because repeated structure planning had delayed real work; future work should be execution-oriented and honest about results.
- The strongest doctrine is: stable semantic IDs and contracts, replaceable implementations.
- Domino is the reusable substrate/framework; Dominium is one game/product family.
- Workbench is a production surface, not the authority.
- Third-party libraries are providers, not architecture.
- C17+C++17 is the mainline baseline, with C-compatible public ABI.
- Feature readiness is limited until proof gates are clean.
- Full CTest/T4 is release/full-proof debt, not the normal fast development gate.
- Do not trust stale structure exports; validate report bundle integrity.


## 15. Best Questions I Can Ask Next in This Chat

### 15.1 Understanding the Chat
- “Explain the Domino/Dominium/Workbench/AIDE distinction again in one page.”
- “What changed between the early folder-cleanup phase and the final provider-framework model?”

### 15.2 Decisions
- “Which decisions were explicitly accepted by me versus merely suggested by the assistant?”
- “Which root names and directory patterns are now forbidden?”

### 15.3 Tasks and Next Actions
- “Generate the next prompt for `PROJECTION-CONFORMANCE-01`.”
- “Generate a maintenance prompt for stale generated evidence and fast-strict blockers.”
- “Generate a targeted `PACK-INTERNAL-LAYOUT-CANON-01` prompt.”

### 15.4 Artifacts and Files
- “List all handoff/report files generated in this chat and what each should be used for.”
- “Compare this preservation report with the earlier `dominium_canonical_handoff.md`.”

### 15.5 Risks and Verification
- “What facts need live repo verification before I continue?”
- “What are the current risks if I start broad Workbench or renderer work now?”

### 15.6 Future Spec Book / Aggregation
- “Which parts of this chat should become formal spec-book requirements?”
- “What might conflict with other chats?”

### 15.7 Deep-Dive Questions Specific to This Chat
- “Should `external/upstream` or `external/vendor` be canonical?”
- “How should raylib/SDL2/Lua provider manifests be named?”
- “What exactly belongs in `apps/workbench/module/` versus `contracts/module/`?”


## 16. Compact Human Summary

This chat was about turning Dominium from a structurally unstable game repository into a credible, reusable, contract-governed Domino/Dominium platform. The user’s core frustration was that months of structure planning and refactoring had prevented actual development. The repo had repeatedly accumulated new roots, generic wrappers, duplicate directories, old path names, and unclear ownership. The user wanted the structure fixed decisively so Workbench, client, engine, game, provider, module, and pack work could begin without another refactor cycle.

The first major outcome was a closed top-level root model: `apps`, `engine`, `game`, `runtime`, `contracts`, `content`, `docs`, `tests`, `tools`, `scripts`, `cmake`, `external`, `release`, and `archive`, plus project roots like `.aide`, `.github`, and `.vscode`. The user strongly rejected top-level `src`, `source`, `modules`, `plugins`, `profiles`, `labs`, `framework`, and `sdk`. The conversation established that apps compose products; runtime implements reusable services, projections, providers, and host/platform integrations; engine owns deterministic substrate; game owns Dominium law, rule, world, and domain meaning; contracts define law; content supplies authored payload; tools validate/generate/migrate/audit; archive preserves history and evidence.

The chat then moved beyond folders into public-surface governance. The user wanted code to be reusable by other games and engine projects. The answer became stable contracts and IDs, not stable private folders. Domino is the reusable deterministic substrate/framework; Dominium is one game/product family; Workbench is the production/editing/validation/evidence environment; AIDE is the repo/control-plane harness. The framework should not be a new `framework/` root. It should be the set of public surfaces, ABI headers, contracts, service/provider law, and conformance tests.

Language policy was also settled. The old C89/C++98 ambition was superseded by C17+C++17 as the mainline baseline, while preserving a C-compatible public ABI: opaque handles, versioned structs, fixed-width types, explicit ownership/lifetime, no STL/C++ ABI leakage, no exceptions crossing the boundary, and no raw object-layout serialization. C17 owns boring law, ABI-facing data, packets, saves, replays, deterministic math, and low-level facades. C++17 owns runtime services, game orchestration, providers, apps, Workbench, tools, and resource ownership.

The Workbench model was refined heavily. Workbench should not be the authority. CLI, text/TUI, rendered GUI, native GUI, headless, Workbench, CI, and AIDE should project the same command/result/refusal/document/view/action/evidence contracts. A module is a declared functional extension unit, not just a folder. Workbench modules are only one consumer of general module law. Workspaces are larger user-facing compositions.

Third-party libraries were treated as providers. Raylib can be used aggressively, along with rlgl, rlsw, raygui, raudio, SDL2, Lua, and possibly ImGui, but they must be fenced. The final structure should be service-first: `runtime/<service>/providers/<provider>/`. Apps stay generic; profiles select providers; external third-party code lives under `external/upstream/` or `external/vendor/`; third-party types must not leak into engine, game, contracts, content, saves, replays, or public ABI.

Many concrete Codex/AIDE prompts were generated and many user status reports described commits landing. The repo reportedly reached a credible canonical state: old active paths routed, provider/profile structure added, full-gate legacy stale paths fixed, Domino framework boundary defined, fast strict and smoke tests passing in several reports. However, full CTest/T4 release proof remains ungreen or unverified, stale generated evidence and marker debt appear in some reports, and feature readiness remains limited. The best future work is targeted: repair proof hygiene, run/triage full CTest, continue projection conformance and presentation contracts, and then proceed with provider and Workbench product-spine slices.
