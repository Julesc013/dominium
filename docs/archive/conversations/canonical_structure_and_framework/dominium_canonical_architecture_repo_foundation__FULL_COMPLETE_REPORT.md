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


# STRUCTURED REGISTERS

## 17. Workstream Register

| ID | Name | Objective | Current state | Desired end state | Status | Priority | Confidence | Label |
|---|---|---|---|---|---|---|---|---|
| WORKSTREAM-01 | Canonical repo structure | Stabilize roots and internal ownership taxonomy | Broad structure credible with warnings | No active old paths, validators green, targeted residuals only | Active / mostly complete | P0 | High | FACT |
| WORKSTREAM-02 | Domino framework boundary | Define framework as public surfaces/contracts/headers, not root | Reported commit added boundary docs/validator | Stable exported public surface model | Active | P0 | High | FACT |
| WORKSTREAM-03 | API/ABI governance | C-compatible public ABI over C17/C++17 internals | Doctrine established; validators partly reported | Public surfaces registered and tested | Active | P0 | Medium | FACT/INFERENCE |
| WORKSTREAM-04 | Provider architecture | Service-first provider model for raylib/SDL/Lua/etc. | Provider structure reported landed with warnings | Providers selected by profiles and conformance-tested | Active | P0 | High | FACT |
| WORKSTREAM-05 | Workbench/product spine | Build Workbench and product slices through command/view/evidence contracts | Validation slice reported landed; projection work pending | Workbench consumes shared command/view/document spine | Active | P1 | Medium | FACT |
| WORKSTREAM-06 | Full-gate proof | Remove stale full-gate failures and prove full suite | Targeted stale path subset fixed; full CTest not green | Full CTest/T4 green or all failures classified | Active | P0/P1 | High | FACT |
| WORKSTREAM-07 | Third-party provider fencing | Use raylib/SDL/Lua fast without contaminating contracts/game/engine | Doctrine established; implementation pending | Forbidden include + provider manifests + conformance tests | Active | P1 | High | FACT/INFERENCE |
| WORKSTREAM-08 | Chat preservation | Preserve this chat for future handoff/spec aggregation | This package generated | Aggregator-ready report and files | Active | P0 | High | FACT |

## 18. Decision Register

| ID | Decision | Status | Evidence / basis | Rationale | Implications | Related workstream | Confidence | Label |
|---|---|---|---|---|---|---|---|---|
| DECISION-01 | Keep closed top-level root set | Current | Repeated accepted doctrine | Prevent root sprawl | Future roots require contract update | WORKSTREAM-01 | High | FACT |
| DECISION-02 | No first-party `src/source` wrappers | Current | User explicitly objected | Avoid meaningless nesting | Ownership dirs are source roots | WORKSTREAM-01 | High | FACT |
| DECISION-03 | Domino/Dominium split | Current | Repeated synthesis accepted in discussion | Enables reuse | Public surfaces become Domino framework | WORKSTREAM-02 | High | FACT |
| DECISION-04 | No top-level `framework/` root | Current | User reported commit defining boundary | Avoid root competition | Framework lives in contracts/headers | WORKSTREAM-02 | High | FACT |
| DECISION-05 | C17+C++17 mainline with C-compatible ABI | Current | Discussion and user status text | Balance portability and implementation power | C++ internals, C ABI boundaries | WORKSTREAM-03 | Medium-High | FACT/VERIFY |
| DECISION-06 | Service-first provider directories | Current | Provider structure discussions and status report | Keeps third-party replaceable | `runtime/<service>/providers/<provider>` | WORKSTREAM-04 | High | FACT |
| DECISION-07 | Apps do not hardwire providers | Current | Repeated doctrine | Avoid product variant explosion | Profiles choose providers | WORKSTREAM-04 | High | FACT |
| DECISION-08 | Workbench not authority | Current | Repeated doctrine | Prevent GUI-specific truth | Workbench uses commands/views/evidence | WORKSTREAM-05 | High | FACT |
| DECISION-09 | Fast strict normal gate; full CTest full-gate debt | Current | Reported test-tier doctrine | Keeps dev loop usable | Full release proof remains separate | WORKSTREAM-06 | High | FACT |

## 19. Task Register

| ID | Task | Priority | Urgency | Owner | Dependencies | Inputs needed | Expected output | Next step | Related workstream | Label |
|---|---|---|---|---|---|---|---|---|---|---|
| TASK-01 | Verify current repo state from fresh export | P0 | U0 | User/Codex | None | Fresh tracked export | Truthful status | Run report-integrity checks | WORKSTREAM-01 | FACT |
| TASK-02 | Repair stale generated evidence/markers if fast strict fails | P0 | U0/U1 | Codex/AIDE | Current validation logs | AuditX/identity/launcher failure logs | Fast strict green | Run targeted repair | WORKSTREAM-06 | FACT/UNCERTAIN |
| TASK-03 | Run full CTest audit | P1 | U1 | Codex/AIDE | Fast strict green | Full CTest output | Failure ledger | Classify/fix/defer failures | WORKSTREAM-06 | FACT |
| TASK-04 | Implement/validate projection conformance | P1 | U1 | Codex/AIDE | Presentation contracts | Command/result/view fixtures | Projection tests | Generate PROJECTION-CONFORMANCE prompt | WORKSTREAM-05 | FACT |
| TASK-05 | Define/finish presentation contracts | P1 | U1 | Codex/AIDE | Command/result/refusal contracts | View/action/projection schemas | Semantic presentation law | Run PRESENTATION-CONTRACT | WORKSTREAM-05 | FACT |
| TASK-06 | Provider wedge for raylib/SDL/Lua | P2 | U2 | Codex/AIDE | Provider structure green | Third-party source policy, manifests | Seed providers | Run provider wedge tasks | WORKSTREAM-04 | INFERENCE |
| TASK-07 | Pack internal layout canon | P2 | U2 | Codex/AIDE | Pack authority check | Pack tree + manifests | Canonical pack internals | Decide content/ vs data/ law | WORKSTREAM-01 | FACT |
| TASK-08 | Generate master spec book from old-chat reports | P2 | U2 | User/future assistant | This and other chat reports | Aggregator packets | Master spec | Use spec sheet/aggregator packet | WORKSTREAM-08 | FACT |

## 20. Constraint Register

| ID | Constraint | Type | Hard/soft | Source / basis | Practical implication | Violation risk | Confidence | Label |
|---|---|---|---|---|---|---|---|---|
| CONSTRAINT-01 | No new top-level roots without contract | Repo structure | Hard | User and doctrine | Route concepts into existing roots | Root sprawl | High | FACT |
| CONSTRAINT-02 | No first-party src/source wrappers | Repo structure | Hard | User explicitly objected | Use ownership dirs directly | Redundant nesting | High | FACT |
| CONSTRAINT-03 | Third-party types must not cross stable boundaries | Architecture | Hard | Provider doctrine | Fence raylib/SDL/Lua/ImGui | Vendor lock-in | High | FACT |
| CONSTRAINT-04 | Public ABI is C-compatible | API/ABI | Hard | Doctrine | No C++ ABI/STL/exceptions across ABI | ABI breakage | High | FACT |
| CONSTRAINT-05 | Workbench must use commands/views/evidence | Product architecture | Hard | Doctrine | No private validator/tool bypass | Divergent behavior | High | FACT |
| CONSTRAINT-06 | Do not treat assistant suggestions as user decisions | Reporting | Hard | User prompt | Preserve tentative status | False history | High | FACT |
| CONSTRAINT-07 | Verify current facts that may have changed | Factuality | Hard | User/system preference | Search/live verify current repo/library claims | Stale answers | High | FACT |

## 21. User Preference Register

| ID | Preference | Area | Explicit/inferred/uncertain | Strength | Practical implication | Risk if wrong | Label |
|---|---|---|---|---|---|---|---|
| PREF-01 | Direct, audit-ready answers | Communication | Explicit | High | State verdict and evidence | Loss of trust | FACT |
| PREF-02 | Mark uncertainty | Factuality | Explicit | High | Use FACT/INFERENCE/UNCERTAIN | Overclaiming | FACT |
| PREF-03 | Avoid endless planning without execution | Workflow | Explicit/inferred | High | Give actionable prompts/tasks | Frustration/stall | FACT |
| PREF-04 | Preserve rejected/superseded options | Handoff | Explicit | High | Include rejection register | Repeated mistakes | FACT |
| PREF-05 | Future-proof modular architecture | Technical | Explicit | High | Favor contracts/providers/profiles | Structural lock-in | FACT |

## 22. Open Questions Register

| ID | Question / issue | Why it matters | Known information | Unknown information | Resolution path | Priority | Related workstream | Label |
|---|---|---|---|---|---|---|---|---|
| QUESTION-01 | Is full CTest green now? | Release/full proof | Reports say not green/not run | Current live result | Run full CTest or audit shard | P0/P1 | WORKSTREAM-06 | UNCERTAIN |
| QUESTION-02 | Which provider implementation comes first? | Product progress | raylib/SDL/Lua doctrine established | Exact current queue | Check queue/current, priorities | P1 | WORKSTREAM-04 | UNCERTAIN |
| QUESTION-03 | Lua 5.4 or 5.5? | Script ABI stability | Pin one version; script API separate | Chosen version | Decide based on compatibility/toolchain | P2 | WORKSTREAM-04 | UNCERTAIN |
| QUESTION-04 | Is pack-internal content/ canonical? | Pack compatibility | Mixed layouts discussed | Actual pack law | Inspect contracts/package | P1/P2 | WORKSTREAM-01 | UNCERTAIN |
| QUESTION-05 | Are AIDE cache/queue/reports canonical? | Source/generated boundary | State-like dirs discussed | Exact current classification | AIDE state classification task | P1 | WORKSTREAM-01 | UNCERTAIN |

## 23. Artifact Ledger

| ID | Artifact / file / prompt / output | Type | Purpose | Status | Origin | Carry forward? | Notes | Label |
|---|---|---|---|---|---|---|---|---|
| ARTIFACT-01 | dominium_canonical_handoff.md/txt | Generated handoff | Earlier project handoff | Available in sandbox | This chat | Yes | Compare with this report | FACT |
| ARTIFACT-02 | dir_tree / dirfiles bundles | Uploaded reports | Structure assessment | Mixed reliability | User uploads | Yes with caveats | Verify integrity before use | FACT |
| ARTIFACT-03 | CANON_STRUCTURE_ACTUAL_FINAL_CLEANUP_01 prompt/report | Task/audit | Actual structure cleanup | Reported committed | Chat/user status | Yes | Key structural milestone | FACT |
| ARTIFACT-04 | FULL_GATE_LEGACY_TEST_ROUTE_01 | Task/audit | Route stale full-gate test paths | Reported committed | Chat/user status | Yes | Improves full-gate signal | FACT |
| ARTIFACT-05 | Domino framework boundary docs/validator | Docs/validator | Prevent framework root sprawl | Reported committed | Chat/user status | Yes | Important architecture decision | FACT |
| ARTIFACT-06 | This preservation package | Report package | Preserve chat for aggregation | Created now | Current response | Yes | Use as cross-chat input | FACT |

## 24. Rejected / Superseded Options Register

| ID | Option | Status | Reason | Final or tentative? | Reconsider conditions | Related workstream | Label |
|---|---|---|---|---|---|---|---|
| REJECTED-01 | Top-level framework/ | Rejected | Competes with contracts/public headers | Mostly final | If multiple external framework packages require root and root contract changes | WORKSTREAM-02 | FACT |
| REJECTED-02 | Top-level modules/plugins/services/profiles/labs | Rejected | Reopens root sprawl | Mostly final | Explicit root contract change | WORKSTREAM-01 | FACT |
| REJECTED-03 | Vendor-shaped runtime/raylib tree | Rejected | Violates service-first provider model | Final for architecture | None except experiments | WORKSTREAM-04 | FACT |
| REJECTED-04 | Workbench as authority | Rejected | Would diverge from CLI/headless/CI | Final | None | WORKSTREAM-05 | FACT |
| REJECTED-05 | Pure C99 mainline | Rejected | Insufficient for large modular architecture | Current | If project scope radically shrinks | WORKSTREAM-03 | FACT |

## 25. Risk Register

| ID | Risk / failure mode | Consequence | Likelihood | Severity | Mitigation | Related workstream | Label |
|---|---|---|---|---|---|---|---|
| RISK-01 | Stale/mixed structure reports | Wrong cleanup decisions | Medium | High | Structure report integrity validator | WORKSTREAM-01 | FACT |
| RISK-02 | More broad cleanup churn | Delays product work | Medium | High | Targeted tasks only after structure credible | WORKSTREAM-01 | INFERENCE |
| RISK-03 | Third-party leakage | Vendor lock-in, broken saves/replays | Medium | High | Forbidden include/type validators | WORKSTREAM-04 | FACT |
| RISK-04 | Full CTest ignored too long | Release proof unreliable | Medium | High | Full-gate audit ledger | WORKSTREAM-06 | FACT |
| RISK-05 | Assistant treats suggestions as decisions | Bad handoff/spec | Medium | Medium | Preserve labels and evidence basis | WORKSTREAM-08 | FACT |

## 26. Verification Queue

| ID | Item requiring verification | Why verification is needed | Suggested source/type | Priority | Related workstream | Label |
|---|---|---|---|---|---|---|
| VERIFY-01 | Current live repo HEAD/status | User reports changed over time | Fresh git status/export | P0 | WORKSTREAM-01 | FACT |
| VERIFY-02 | Full CTest current result | Release readiness unknown | Run full CTest/T4 audit | P0/P1 | WORKSTREAM-06 | FACT |
| VERIFY-03 | Current fast strict blockers | Reports mention stale evidence/marker debt | Run fast strict/RepoX | P0 | WORKSTREAM-06 | FACT |
| VERIFY-04 | Raylib/SDL/Lua current versions/support | External facts can change | Official upstream docs/releases | P1/P2 | WORKSTREAM-04 | VERIFY |
| VERIFY-05 | Pack internal layout law | Avoid breaking packs | contracts/package + manifests | P1/P2 | WORKSTREAM-01 | FACT |

## 27. Chronological Timeline Register

| Sequence | Event / topic | What changed or was decided | Why it mattered | Current relevance | Confidence |
|---|---|---|---|---|---|
| 1 | Early layout critique | User rejected root sprawl and src/source wrappers | Set hard structural doctrine | Foundational | High |
| 2 | Canonical root model | Closed root set established | Stopped top-level churn | Still current | High |
| 3 | Distribution/install discussion | Source layout separated from runtime/package layouts | Prevented source/runtime confusion | Current | High |
| 4 | Move scripts/prompts | Generated many cleanup prompts | Drove actual repo changes | Historical and artifact value | High |
| 5 | Public API/ABI shift | Stable surfaces > stable folders | Future-proofing | Current | High |
| 6 | C17/C++17 baseline | Superseded C89/C++98 mainline | Implementation policy | Current but verify repo | Medium |
| 7 | Workbench/module model | Modules/workspaces/services/providers distinguished | Prevented module junk drawer | Current | High |
| 8 | Provider model | raylib/SDL/Lua as providers | Enabled acceleration without lock-in | Current | High |
| 9 | Framework boundary | Rejected top-level framework root | Prevented new root sprawl | Current | High |
| 10 | Preservation prompt | User requested maximum-fidelity package | Enables future handoff/spec book | Current | High |

## 28. Spec Book Contribution Register

| Spec-book area | Contribution from this chat | Source IDs | Should become requirement/context/open issue? | Confidence | Notes |
|---|---|---|---|---|---|
| Repo layout | Closed root model, no src/source, no root sprawl | DECISION-01, CONSTRAINT-01 | Requirement | High | Central contribution |
| Framework/API | Domino framework boundary, public surface model | DECISION-03, DECISION-04 | Requirement | High | Avoid framework root |
| Provider architecture | Service-first provider folders, profiles | DECISION-06, WORKSTREAM-04 | Requirement | High | Important for raylib/SDL/Lua |
| Presentation | Command/result/view/action/projection spine | WORKSTREAM-05 | Requirement/context | Medium-High | Needs implementation proof |
| Proof gates | Fast strict vs full CTest/T4 distinction | DECISION-09 | Requirement/context | High | Prevents dev-loop paralysis |
| Third-party policy | Fence provider types from stable surfaces | CONSTRAINT-03 | Requirement | High | Essential to modularity |


## 29. Context Transfer Packet for a Future Chat

### 29.1 Ultra-Condensed Bootstrap Brief

We are continuing from a long Dominium architecture/repository chat. The main project is Dominium, a game/product family built on a reusable Domino substrate/framework. The central problem was months of directory-structure churn blocking development. The user strongly rejected new top-level roots, `src/`/`source/` wrappers, generic junk drawers, and vague structure. The settled top-level roots are `apps`, `engine`, `game`, `runtime`, `contracts`, `content`, `docs`, `tests`, `tools`, `scripts`, `cmake`, `external`, `release`, and `archive`, plus `.aide`, `.github`, `.vscode`, and `.aide.local.example`. Do not add `framework`, `modules`, `plugins`, `profiles`, `labs`, or `sdk` roots.

The current doctrine is: path is not identity; implementation is not contract; UI is not authority; generated output is not source truth. Stable identity lives in contracts, manifests, registries, stable IDs, public headers, artifacts, compatibility corpus, and release metadata. Implementations live in folders and may be replaced behind tests.

Domino Framework is not a new root. It is the collection of public surfaces, ABI headers, contracts, service/provider law, and conformance tests. Engine/runtime are the reference implementation. Dominium game lives in `game`, `content`, and `apps`. Workbench is a production/editing/validation/evidence environment over shared commands/views/documents/evidence, not an authority.

The repo has reportedly undergone actual cleanup commits and now has credible canonical structure with warnings. Full release proof remains not green. Future assistants must verify live status before acting. The next likely tasks are targeted proof hygiene, presentation/projection conformance, provider wedges, and full-gate audits—not broad root redesign.

### 29.2 Source Hierarchy

1. Direct user statements in this chat.
2. Explicit decisions accepted by the user.
3. Current task/register/audit summaries provided by the user.
4. Constraints/preferences register in this report.
5. Artifact ledger and generated files.
6. Inferences clearly labelled.
7. Assistant suggestions not explicitly accepted.
8. General model knowledge, verified if current-world facts matter.

### 29.3 Operating Rules for Future Assistants

Preserve FACT / INFERENCE / UNCERTAIN / PROJECT-CONTEXT labels. Do not assume access to the old chat. Do not re-ask answered questions. Verify stale repo/library/tool facts before relying on them. Do not treat tentative brainstorms as final decisions. Do not repeat rejected roots or vendor-shaped structures. Preserve artifacts and uncertainty. Use structured outputs for continuation.

### 29.4 Active Workstreams

Active workstreams include canonical structure residuals, framework/public surface governance, provider architecture, Workbench/product spine, full-gate proof hygiene, third-party provider fencing, and chat/spec preservation.

### 29.5 Current Priorities

1. Verify current live repo status from fresh export.
2. If fast strict/RepoX is blocked, repair stale evidence/marker debt.
3. If proof gates are clean, continue `PROJECTION-CONFORMANCE-01` or `PRESENTATION-CONTRACT-01`.
4. Avoid broad root cleanup unless a hard validator fails.

### 29.6 Current Open Questions

See Open Questions Register, especially full CTest status, pack internal layout, Lua version, AIDE state classification, and current queue.

### 29.7 Recommended First Action

Ask the user for or generate a fresh tracked-only repo status/export, then verify whether fast strict and RepoX are green. If they are green, proceed with `PROJECTION-CONFORMANCE-01`. If not, repair stale generated evidence/marker debt first.


## 30. Spec Sheet

```yaml
spec_sheet:
  metadata:
    chat_label: "Dominium Canonical Architecture, Repository Foundation, and Provider Model"
    date_anchor: "2026-05-27 Australia/Melbourne"
    source_scope: "This chat only unless labelled PROJECT-CONTEXT"
    apparent_coverage: "Partial visible transcript; skipped/expired content exists"
    confidence_1_to_5: 4
    staleness_risk: "Medium to High for current repo state; Low for internal doctrine"
    safe_for_aggregation: "Yes, with caveats"
    main_limitations:
      - "Some transcript portions are hidden behind skipped-message markers."
      - "Some uploaded files expired or were mixed across runs."
      - "Repo commit/test status must be verified live before action."
  summary:
    one_sentence: "This chat converted Dominium repo cleanup into a broader Domino framework, provider, public-surface, and proof-gated architecture doctrine."
    short_brief: "The chat settled root structure, rejected root sprawl, defined Domino vs Dominium, formalized provider/service/profile thinking, and generated many cleanup/proof prompts."
    main_topics:
      - "Canonical repo structure"
      - "Domino framework boundary"
      - "C17/C++17 and C-compatible ABI"
      - "Provider architecture for raylib/SDL/Lua"
      - "Workbench semantic spine"
      - "Proof gates and full-gate debt"
    main_outputs:
      - "Handoff files"
      - "Preservation package"
      - "Codex/AIDE prompts"
      - "Decision/task/risk registers"
    highest_priority_carry_forward:
      - "Verify current live repo status."
      - "Do not add new top-level roots."
      - "Continue targeted proof hygiene or projection conformance, not broad cleanup."
  source_rules:
    labels_used: ["FACT", "INFERENCE", "UNCERTAIN / UNVERIFIED", "PROJECT-CONTEXT"]
    conflict_rules:
      - "Prefer direct user statements and committed/status reports over assistant suggestions."
      - "Verify live repo state when reports disagree."
    staleness_rules:
      - "External library/toolchain/version claims require verification before implementation decisions."
  user_preferences:
    explicit:
      - "Direct, audit-ready, uncertainty-labelled answers."
      - "No root sprawl or repeated src/source wrappers."
      - "Future-proof modular reusable design."
    inferred:
      - "Execution-oriented prompts over endless planning."
      - "Strong preference for validators and mechanical enforcement."
    uncertain_or_not_established:
      - "Exact Lua version."
      - "external/upstream vs external/vendor."
  workstreams:
    - id: WORKSTREAM-01
      name: "Canonical repo structure"
      label: FACT
      objective: "Stabilize roots and internal ownership"
      current_state: "Credible with warnings by reported status"
      desired_end_state: "No active old paths and targeted residual warnings only"
      status: "Mostly complete"
      priority: P0
      background: "Core topic of chat"
      decisions_made: [DECISION-01, DECISION-02]
      tasks: [TASK-01, TASK-07]
      constraints: [CONSTRAINT-01, CONSTRAINT-02]
      dependencies: []
      blockers: []
      risks: [RISK-01, RISK-02]
      artifacts: [ARTIFACT-02, ARTIFACT-03]
      success_criteria: ["canonical validators pass", "fresh report integrity passes"]
      next_action: "Verify current fresh export"
      verification_needed: [VERIFY-01]
      confidence: 4
    - id: WORKSTREAM-04
      name: "Provider architecture"
      label: FACT
      objective: "Use service-first replaceable providers"
      current_state: "Doctrine and some structures reported landed"
      desired_end_state: "Provider manifests, conformance tests, fenced third-party code"
      status: "Active"
      priority: P1
      background: "raylib/SDL/Lua discussions"
      decisions_made: [DECISION-06, DECISION-08]
      tasks: [TASK-06]
      constraints: [CONSTRAINT-03]
      dependencies: ["public surface", "profiles", "capability law"]
      blockers: []
      risks: [RISK-03]
      artifacts: []
      success_criteria: ["no third-party leakage", "provider conformance tests"]
      next_action: "Provider wedge after proof hygiene"
      verification_needed: [VERIFY-04]
      confidence: 4
  decisions:
    - id: DECISION-01
      decision: "Keep a closed top-level root set."
      status: "current"
      label: FACT
      evidence_or_basis: "Repeated user acceptance and cleanup reports"
      rationale: "Prevents root sprawl"
      implications: "New concepts must route into canonical roots"
      related_workstreams: [WORKSTREAM-01]
      uncertainty: "Low"
  tasks:
    - id: TASK-01
      task: "Verify current repo status from fresh export"
      priority: P0
      urgency: U0
      owner: "User/Codex"
      dependencies: []
      inputs_needed: ["fresh tracked export", "git status"]
      expected_output: "Current truthful status"
      next_step: "Run report integrity"
      related_workstreams: [WORKSTREAM-01]
      label: FACT
      confidence: 4
  constraints:
    - id: CONSTRAINT-01
      constraint: "No new top-level roots without root-contract update"
      type: "repo structure"
      hard_or_soft: "hard"
      source_or_basis: "user preference and doctrine"
      implication: "Use existing roots"
      violation_risk: "root sprawl"
      label: FACT
      confidence: 5
  open_questions:
    - id: QUESTION-01
      question: "Is full CTest green now?"
      why_it_matters: "Release/full proof readiness"
      known: "Reports say not green or not run"
      unknown: "Current result"
      resolution_path: "Run full CTest audit"
      priority: P0
      related_workstreams: [WORKSTREAM-06]
      label: UNCERTAIN
  rejected_or_superseded_options:
    - id: REJECTED-01
      option: "Top-level framework/"
      status: "rejected"
      reason: "Framework is public surfaces/contracts, not a source root"
      final_or_tentative: "mostly final"
      reconsider_conditions: "explicit root contract change"
      related_workstreams: [WORKSTREAM-02]
      label: FACT
  artifacts:
    - id: ARTIFACT-01
      name_or_description: "dominium_canonical_handoff.md"
      type: "handoff"
      purpose: "Earlier project handoff"
      status: "available in sandbox"
      origin: "this chat"
      carry_forward: true
      notes: "Compare with this preservation package"
      label: FACT
  risks:
    - id: RISK-01
      risk: "Stale/mixed structure reports"
      consequence: "Wrong cleanup decisions"
      likelihood: "medium"
      severity: "high"
      mitigation: "structure report integrity validator"
      related_workstreams: [WORKSTREAM-01]
      label: FACT
  verification_queue:
    - id: VERIFY-01
      item: "Current live repo HEAD/status"
      why_verification_needed: "User reports changed repeatedly"
      suggested_source_type: "fresh git status/export"
      priority: P0
      related_workstreams: [WORKSTREAM-01]
      label: FACT
  spec_book_notes:
    likely_sections:
      - "Repository architecture"
      - "Domino framework boundary"
      - "Provider model"
      - "Workbench architecture"
      - "Proof gates"
    unique_contributions:
      - "Path is not identity doctrine"
      - "Service-first provider model"
    possible_duplicates_with_other_chats:
      - "Workbench brainstorming"
      - "Raylib/SDL/Lua provider discussion"
    conflicts_to_watch_for:
      - "C89/C++98 older plans vs C17/C++17 mainline"
      - "framework root proposals vs no-framework-root decision"
    formal_requirements_candidates:
      - "No src/source wrappers"
      - "Provider implementations cannot leak third-party types"
    background_context_candidates:
      - "History of repo frustration"
    needs_user_confirmation:
      - "Lua version"
      - "external/upstream vs external/vendor"
  final_recommendations:
    next_action_if_continuing_this_chat: "Verify current repo state and proceed with projection conformance or proof hygiene depending gate status."
    next_action_for_aggregator: "Merge registers, preserving uncertainty and rejected options."
    user_checks_required:
      - "Confirm live repo status"
      - "Confirm next task priority"

```

## 31. Aggregator Packet

# Aggregator Packet — Dominium Canonical Architecture, Repository Foundation, and Provider Model

## Packet Metadata

* Chat label: Dominium Canonical Architecture, Repository Foundation, and Provider Model
* Date anchor: 2026-05-27 Australia/Melbourne
* Source scope: This chat only unless labelled PROJECT-CONTEXT
* Coverage: Partial visible transcript with skipped/expired portions
* Confidence: 4/5 for main doctrine, 3/5 for exact chronology/live status
* Staleness risk: Medium to High for repo/library current facts
* Merge priority: High
* Main limitations: Some turns hidden; repo status changed repeatedly; live verification required.

## Ultra-Condensed Carry-Forward Capsule

This chat records the evolution of Dominium from a chaotic directory/refactor problem into a broader Domino/Dominium architecture doctrine. The user’s primary concern was that months of planning and cleanup had blocked actual development. The user wanted structure to be fixed enough to build Workbench, client, engine, game, providers, modules, and packs without repeating the refactor cycle.

The settled top-level source roots are `apps`, `engine`, `game`, `runtime`, `contracts`, `content`, `docs`, `tests`, `tools`, `scripts`, `cmake`, `external`, `release`, and `archive`, with `.aide`, `.github`, `.vscode`, and `.aide.local.example` as project/tooling roots. New top-level roots such as `framework`, `modules`, `plugins`, `profiles`, `labs`, `sdk`, `src`, and `source` are rejected unless a future root contract explicitly authorizes them.

The core doctrine is: path is not identity, implementation is not contract, UI is not authority, and generated output is not source truth. Stable identity lives in contracts, manifests, registries, stable IDs, public headers, compatibility corpus, release metadata, and tests. Private implementations live in folders and can be replaced behind conformance and compatibility proof.

Domino is the reusable deterministic substrate/framework. Dominium is one game/product family using Domino. Workbench is the production/editing/validation/evidence environment over shared commands/views/documents/evidence. AIDE is the repo/control-plane harness. Contracts define law; runtime implements services/projections/providers; apps compose products; content supplies authored payload; tools validate/generate/migrate/audit; tests/replay/evidence prove behavior; archive preserves history.

The chat also settled that Domino Framework should not be a new top-level `framework/` root. It should be a public-surface package formed from contracts, public headers, service/provider law, ABI rules, and conformance tests. Mainline language baseline is C17 + C++17, with a C-compatible public ABI and no C++ ABI leakage.

Provider architecture became service-first: `runtime/<service>/providers/<provider>/`. Raylib, rlgl, rlsw, raygui, raudio, SDL2, Lua, and ImGui may be used aggressively as providers, but cannot become engine/game/contracts/content law. Apps remain generic; profiles select providers. Third-party types must not cross stable boundaries.

Many Codex/AIDE prompts and user-reported commits addressed actual cleanup. The final known status is structurally credible but not fully release-green. Full CTest/T4 and stale generated evidence/proof debt remain. Future work should be targeted: proof hygiene, projection conformance, provider conformance, presentation contracts, pack internal layout, and full-gate audits—not broad root redesign.

## Top Carry-Forward Items

| Priority | Item | Type | Related ID | Why it matters | Label | Confidence |
|---|---|---|---|---|---|---|
| P0 | Closed top-level root model | Decision | DECISION-01 | Prevents root sprawl | FACT | High |
| P0 | No `src/source` wrappers | Constraint | CONSTRAINT-02 | Prevents ownership ambiguity | FACT | High |
| P0 | Domino framework as public surfaces, not root | Decision | DECISION-04 | Prevents `framework/` sprawl | FACT | High |
| P0 | Service-first providers | Decision | DECISION-06 | Enables raylib/SDL/Lua replacement | FACT | High |
| P0 | Verify live repo state | Task | TASK-01 | Reports changed repeatedly | FACT | High |
| P1 | Projection conformance | Task | TASK-04 | Needed before broad UI/Workbench | FACT | Medium |

## Workstream Summaries

See Workstream Register in File 04. Main active workstreams: canonical structure, framework boundary, API/ABI governance, provider architecture, Workbench/product spine, full-gate proof, third-party fencing, preservation.

## Compact Registers for Merge

Use File 04 for complete registers. Merge DECISION-01 through DECISION-09, TASK-01 through TASK-08, CONSTRAINT-01 through CONSTRAINT-07, QUESTION-01 through QUESTION-05, ARTIFACT-01 through ARTIFACT-06, RISK-01 through RISK-05, and VERIFY-01 through VERIFY-05.

## Possible Cross-Chat Duplicates

Workbench module/workspace architecture; raylib/SDL/Lua provider plan; repo structure cleanup; C17/C++17 language baseline; AIDE/Codex workflow law; full-gate proof debt.

## Possible Cross-Chat Conflicts

Older chats may still recommend C89/C++98, top-level `src`, `framework/`, vendor-shaped raylib structure, or Workbench-as-authority. Treat those as superseded unless reaffirmed later.

## Spec Book Integration Guidance

This chat should inform formal requirements for repo layout, public surfaces, ABI law, provider structure, Workbench semantics, proof gates, and third-party boundaries. It should remain background context for emotional/project history but formal requirements should be extracted into concise normative sections.

## Aggregator Warnings

Do not merge assistant brainstorms as user decisions. Preserve uncertainty. Verify current repo state. Do not restart root-structure debate unless fresh evidence shows hard blockers.


## 32. Adversarial Self-Audit

| Issue | Severity | Correction needed | Correction applied? | Residual risk |
|---|---|---|---|---|
| Hidden skipped transcript portions | High | Mark coverage partial | Yes | Some omitted details may remain |
| User-reported commits not independently verified | High | Label as reported in chat | Yes | Live repo may differ |
| External library/version facts stale | Medium | Put in verification queue | Yes | Must verify before implementation |
| Long list of prompts may omit some | Medium | Use representative list, not exhaustive claim | Yes | Some prompts may be missing |
| Assistant suggestions could be mistaken for decisions | High | Distinguish accepted/current vs suggested | Yes | Some acceptance inferred from user flow |
| Report may still over-compress some file details | Medium | Include artifact ledger and preservation package | Yes | Future deep dive may need original transcript |
| Current repo status changed many times | High | Recommend fresh export/status | Yes | Current state remains uncertain |

## 33. Corrections Applied

- Marked transcript access as partial rather than full.
- Labelled repo statuses as user-reported unless independently verified.
- Preserved rejected/superseded options separately.
- Included verification queue for live repo and external facts.
- Avoided claiming every suggested task was completed or accepted.

## 34. Final Reliability Assessment

* Completeness rating: 4/5 for visible conversation, 3/5 for hidden/skipped details.
* Reliability rating: 4/5 for doctrine and user preferences, 3/5 for exact live repo state.
* Human-readability rating: 4/5.
* Aggregation-readiness rating: 4/5 with caveats.
* Main uncertainty sources: skipped transcript messages, expired uploads, repeated repo status changes, unverified live HEAD/tests, external library/toolchain facts.
* Manual review before merge: recommended.
