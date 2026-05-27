# COMPLETE CHAT PRESERVATION REPORT — Dominium Canonical Structure and Domino Framework Architecture

## 0. Coverage and Reliability Assessment

| Field | Assessment |
|---|---|
| Chat label | Dominium Canonical Structure and Domino Framework Architecture |
| Date anchor | 2026-05-27 Australia/Melbourne |
| Source scope | This chat only unless labelled PROJECT-CONTEXT |
| Apparent access | Partial |
| Previously generated files available? | Yes: earlier Markdown/plain-text handoff files are mounted in `/mnt/data`; some previously uploaded files expired. |
| Uploaded files or artifacts present? | Yes: repeated directory-tree exports, dirfiles manifests, run logs, ZIP bundles, and the current preservation prompt text. |
| Contains future plans? | Yes |
| Contains decisions? | Yes, with some decisions tentative or dependent on repo proof status. |
| Contains pending tasks? | Yes |
| Contains unresolved questions? | Yes |
| Staleness risk | Medium to High for live repo state and third-party library/version facts; Low for architectural decisions explicitly discussed. |
| Extraction confidence | 4/5 for the visible chat and mounted summaries; 3/5 for exact historical file states because some uploads expired and several structure bundles were mixed/stale. |
| Safe for later aggregation? | Yes, with caveats |
| Main limitations | The full original transcript is not available as a separate complete export. This report reconstructs from the visible chat context, uploaded preservation prompt, earlier generated handoff files, and user-provided status reports. Some file uploads expired and live-repo facts may have changed after the last status report. |

Plain-language limitation note: this report is a high-fidelity reconstruction of the accessible conversation, not a forensic transcript. It preserves the substance, decisions, prompts, tasks, tradeoffs, and current state as established in the chat. It does not claim to know every file in the user’s local repository beyond the uploaded snapshots and user-reported task results.

## 1. One-Page Orientation

This chat was a long-running architecture and repository-convergence session for the Dominium project. The central problem was that Dominium’s repository structure had become too sprawling, redundant, and unstable for serious development. The user was blocked from building real features because the repo kept accumulating new roots, duplicated concepts, `src/` and `source/` folders, old domain roots, tool roots, app roots, and generated-state confusion. The user repeatedly emphasized that the project needed to become future-proof, portable, modular, extensible, moddable, reusable, backward-compatible, and not another one-off indie project.

The conversation gradually moved from directory cleanup into a broader architectural doctrine. Early discussion focused on distinguishing source repo layout from distribution, installed, portable, package, save, media, cache, rollback, and diagnostics layouts. A major conclusion was that Dominium needed one logical virtual-root model projected into multiple physical layouts, not a different ad hoc tree for every artifact type. This then became a source-layout convergence effort: keep a small closed set of top-level roots—`apps/`, `engine/`, `game/`, `runtime/`, `contracts/`, `content/`, `docs/`, `tests/`, `tools/`, `scripts/`, `cmake/`, `external/`, `release/`, and `archive/`—and prevent new root sprawl.

As the work progressed, the user pushed back hard against structure proposals that reintroduced the very mistakes the refactor was meant to eliminate, especially root-level `src/`, nested `src/`, `source/`, vague `core`, `lib`, `common`, `shared`, top-level `modules`, `plugins`, `profiles`, `labs`, and product/vendor-shaped roots. This produced a stronger naming and ownership doctrine: paths encode ownership, public symbols encode namespace, stable IDs encode semantic identity, and private names stay concise. The user and assistant converged on the rule that **path is not identity, implementation is not contract, UI is not authority, and generated output is not source truth**.

A major architectural shift was the emergence of the “Domino Framework / Dominium Game” distinction. Domino is the reusable deterministic substrate and service/provider framework; Dominium is one game/product family built on it; Workbench is the production, editing, validation, evidence, and inspection environment; AIDE is the repo/control-plane harness. The project should not create a top-level `framework/` root; instead, the framework exists through `contracts/`, public headers under `engine/include/domino` and `runtime/include/domino`, provider/service law, public-surface registries, conformance tests, and release/profile descriptors.

Another large theme was provider architecture. The chat settled on a service-first provider model: Dominium/DOMINO owns service contracts; third-party libraries like raylib, rlgl, rlsw, raygui, raudio, SDL2, Lua, and possibly Dear ImGui are replaceable providers. Provider implementations live under `runtime/<service>/providers/<provider>/`; third-party source lives under `external/upstream/` or equivalent; provider choices live in `release/profiles/` or `content/profiles/`, not app directory names. The user asked whether names should be `sdl2` or `sdl`, `raylib` or `rlgl`, `win32` or `windows`, `d3d11` or `directx`; the answer was to use generic service roots, exact implementation provider folder names, and fully qualified provider IDs.

The chat also defined the Workbench/presentation architecture. Workbench should not be the center of the system. It is one consumer of semantic contracts, commands, services, providers, packs, modules, and artifacts. The correct presentation spine is: intent → command → capability/refusal check → service → result/document/snapshot → diagnostics/evidence → view/action model → projection → shell. CLI, text/TUI, rendered GUI, native GUI, headless reports, Workbench panels, CI, and AIDE should be projections over the same command/view/action/evidence contracts, not separate UI systems.

Many large Codex/AIDE prompts were generated or outlined to force structure cleanup and proof hardening. The user reported several commits and validation states, including canonical structure cleanup, provider structure enforcement, framework boundary definition, and full-gate legacy path routing. The most recent established status is that the structure is credible and much improved, but not perfect: fast strict, canonical structure, CMake verify/build, smoke tests, and targeted capability tests pass or pass with warnings; full CTest/T4 release proof remains debt; broad feature work is still blocked; narrow governed tasks such as projection conformance, presentation contracts, provider wedges, and full-gate evidence repair remain next.

A future assistant must understand that this chat was not merely about folders. It was about turning a messy game repository into a deterministic, contract-governed, provider-backed, pack-composed simulation platform. The most important carry-forward is the doctrine: freeze public surfaces, replace private implementations, preserve artifacts, verify behavior.

## 2. The Story of the Conversation

The chat began from the user’s frustration that Dominium had been stuck in planning/refactoring for months. The user wanted an “ultimate” directory structure that would not require another large restructure. Early answers proposed broad final layouts and routing maps, but the user strongly rejected anything that reintroduced root sprawl, `src/`/`source/`, long paths, proper-name-heavy directories, or vague wrapper folders. This produced one of the central constraints: **no root `src/`, no root `source/`, no nested module `src/`, no generic wrappers, no new top-level roots without contract approval**.

The first major phase was source-root convergence. The conversation established the canonical top-level root set and clarified that source layout must be separate from release output, install layout, portable layout, media layout, package layout, save/bundle layout, diagnostics bundles, and setup/cache/rollback state. The repo should not contain runtime install roots like `store/`, `instances/`, `saves/`, `cache/`, or `ops/` as source roots. Distribution and install layouts should be projections of virtual roots, not drivers of source-tree ownership.

The second phase was bad-root routing. The chat generated large Codex prompts for residual cleanup: runtime name cleanup, pack authority cleanup, schema taxonomy cleanup, content pack layout cleanup, app thinness, Workbench naming, AIDE scan boundary, tools fold, docs canon, RepoX/TestX canonical path repair, remediation proof, RepoX strict debt repair, and task-status reconciliation. The user repeatedly reported commits and validation results from Codex/AIDE runs. Over time, the repo moved from obvious root chaos toward a canonical root model with progressively fewer stale active paths.

The third phase was frustration-driven tightening. The user objected that earlier suggestions still permitted architectural sloppiness. The assistant then articulated stricter naming and structure laws: singular/plural distinctions, short local paths, project prefixes only at public/global boundaries, stable IDs in contracts/manifests rather than paths, and no status words like `legacy`, `modern`, `experimental`, `compat`, `universal`, `old`, `new`, `future`, `v2`, `v3` in active source paths except where semantically justified.

The fourth phase shifted from folders to API/ABI and public surface governance. The user wanted code to be reusable not only for Dominium but for other games and even other engine projects. This led to the Domino/Dominium split: Domino is the reusable deterministic substrate; Dominium is the game/product family. The project needs stable C-compatible public APIs/ABIs, versioned structs, opaque handles, explicit ownership, allocator rules, error/refusal codes, provider descriptors, capability negotiation, compatibility corpora, replacement protocols, dependency-direction validation, and public-header consumer tests. Initially the doctrine referenced C89/C++98, but later the user introduced and accepted a C17/C++17 mainline baseline for Windows 7 SP1+, macOS 10.9.5+, and Linux, while preserving C-compatible ABI boundaries.

The fifth phase defined Workbench and modules. The user brought in brainstorming from another chat about Project Editor, Interface Studio, Module/Pack Foundry, App Composer, Release Forge, etc. The chat refined this into a vocabulary: component = source/build unit; service = callable runtime capability; provider = replaceable implementation; pack = distributable authored payload; module = declared functional extension unit; workspace = large Workbench composition; app = product composition; artifact = persisted/versioned object. This prevented `module/` from becoming the next junk drawer. Reusable modules should not live under `apps/workbench/`; only Workbench UI modules belong there. Module law belongs under `contracts/module/`, module payloads can be delivered through packs, reusable behavior lives under `runtime/` or `game/`, and Workbench presents/edits modules through commands and views.

The sixth phase defined presentation architecture. The user asked about unifying CLI, TUI, rendered GUI, native GUI, Workbench, launcher, setup, server, and client. The chat concluded that all should project the same semantic truth: commands, results, refusals, documents, snapshots, diagnostics, evidence, views, and actions. It rejected separate contract worlds for `tui`, `rendered`, and `native`; those are projection modes under `runtime/projection/`, not semantic authorities under `contracts/`. This produced a refined runtime target: `runtime/command`, `runtime/action`, `runtime/document`, `runtime/patch`, `runtime/view`, `runtime/projection/{cli,text,rendered,native,headless}`, `runtime/ui`, `runtime/render`, `runtime/platform`, etc.

The seventh phase was raylib/SDL/Lua provider architecture. The user pasted or summarized advice about using raylib heavily. The chat accepted the accelerator strategy but rejected vendor-shaped structure. Raylib, rlgl, rlsw, raygui, raudio, SDL2, and Lua should be providers behind first-party service contracts, not engine law. Provider implementations should live under `runtime/<service>/providers/<provider>/`; provider choices should be in profiles, not app paths; third-party types must not leak into `engine/`, `game/`, `contracts/`, `content/`, saves, replays, packs, or public SDK headers. Lua should be pinned as a script provider with Dominium script API versioning, not raw Lua ABI as mod law.

The eighth phase handled the framework question. The user considered adding a `framework/` root and splitting `engine/domino_reference` and `game/dominium`. The chat rejected a new top-level `framework/` root. Domino Framework is not a source root; it is the collection of public surfaces, ABI headers, contracts, service/provider law, and conformance tests. The reference implementation remains in `engine/` and `runtime/`; Dominium remains in `game/`, `content/`, and `apps/`. A later external SDK can be generated from registered public surfaces, but the repo should not add a new active `framework/` root.

The final visible phase was proof and maintenance status. The user reported commits such as `refactor(repo): finish canonical structure cleanup`, `tests: route full-gate legacy path expectations`, and `repo: define Domino framework boundary`. The assistant evaluated each status. The conclusion: the directory structure is now credible and mostly fixed, with canonical structure gates passing, old active paths cleaned, provider/profile structure in place, and stale full-gate path expectations reduced. But the repo is not perfect and not full-release-ready. Remaining work includes stale AuditX/identity evidence, launcher pack marker debt, full CTest/T4 nonpath failures, provider split warnings, public header ABI promotion warnings, storage/package provider split, projection conformance, presentation contracts, and targeted residual taxonomy cleanups.

## 3. Main Topics Discussed

### Topic 1 — Canonical source-root structure

FACT: The user wanted to end repeated repo-structure churn and stop new roots from appearing. The conversation converged on a closed top-level root model: `apps`, `engine`, `game`, `runtime`, `contracts`, `content`, `docs`, `tests`, `tools`, `scripts`, `cmake`, `external`, `release`, `archive`, plus `.aide`, `.aide.local.example`, `.github`, and `.vscode` as project/tooling roots. Generated/local roots such as `.aide.local`, `.dominium.local`, `build`, `out`, `dist`, `artifacts`, `reports`, `tmp`, and `__pycache__` must not become active tracked source.

This mattered because the repo had repeatedly accumulated roots that mixed product, runtime, domain, tooling, generated, archive, and documentation concerns. The canonical model was intended to make future growth predictable and enforceable.

### Topic 2 — No `src/` / `source/` and no generic wrappers

FACT: The user explicitly objected that earlier proposals violated the rule against adding `src/` and `source/` folders. The chat locked the doctrine that first-party source modules should not contain root or nested `src/`, `source`, `sources`, `code`, `impl`, `common`, `shared`, `misc`, or `lib` wrappers. Implementation files should live under ownership paths directly.

The exception is third-party/external source, archive/history, or fixtures preserving upstream/provenance layout.

### Topic 3 — Source layout versus distribution/install layouts

FACT: The conversation emphasized that source layout is not runtime/install layout. Distribution artifacts, `.dompkg` packages, compressed archives, portable installs, installed roots, media layouts, caches, staging, rollback, save bundles, instance bundles, replay/diagnostic bundles, and symbols/provenance layouts are separate projection models. The source repo should not contain active install roots like `store/`, `instances/`, `saves/`, `exports`, `cache`, or `ops`.

This matters because Dominium needs multiple physical layouts but one semantic virtual-root contract.

### Topic 4 — Domino versus Dominium

FACT: The chat established a strong distinction between Domino and Dominium. Domino is the reusable deterministic substrate/framework. Dominium is one game/product family built on Domino. Workbench is a production/editing/validation/evidence environment. AIDE is the repo/control-plane harness.

This distinction matters for reuse. Future games or engine projects should be able to reuse Domino surfaces, providers, tools, and contracts without inheriting Dominium-specific game law, content packs, app descriptors, or domains.

### Topic 5 — Public surface, API, and ABI governance

FACT: The chat concluded that directory cleanliness is not enough. Public/private/stable/internal surfaces need explicit registry and validation. Public/stable surfaces include C headers, ABI tables, schemas, registries, protocols, commands, views, events, refusals, package/save/replay formats, provider ABIs, capability IDs, diagnostic codes, and release artifacts.

The visible rationale was that stable boundaries must be frozen, versioned, owned, and tested, while private implementation remains replaceable. This is one of the main future-proofing mechanisms.

### Topic 6 — C17/C++17 baseline with C-compatible ABI

FACT: The chat moved from older C89/C++98 discipline to a C17/C++17 mainline baseline. The target floor discussed was Windows 7 SP1+, macOS 10.9.5+, and Linux, with 64-bit little-endian x86_64 and arm64 first. Public ABI should remain C-compatible, POD-only, versioned, explicit about ownership/lifetime, and free of C++ ABI leakage.

UNCERTAIN / UNVERIFIED: Exact compiler/toolchain support details and third-party library versions were discussed with references in prior turns; current real-world facts should be verified before release policy is finalized.

### Topic 7 — Commands, views, actions, projections, and UI unification

FACT: The chat established that CLI, text/TUI, rendered GUI, native GUI, headless reports, Workbench, server/admin surfaces, CI, and AIDE should be projections of the same command/result/refusal/document/view/action system. The system should not grow four separate UI systems.

The refined spine was: intent → command → capability/refusal check → service → result/document/snapshot → diagnostics/evidence → view/action model → projection → shell.

### Topic 8 — Workbench and module composition

FACT: The chat clarified that Workbench modules are not the general module system. Workbench modules are user-facing UI/presentation modules under `apps/workbench/module/`; large user-facing compositions are Workbench workspaces under `apps/workbench/workspace/`; module law belongs under `contracts/module/`; pack-delivered module payloads live under `content/packs/.../modules`; reusable behavior lives under `runtime/`, `game/`, or `engine` depending ownership.

This matters because a world creation workspace, pack foundry, app composer, or interface studio must be reusable through commands, services, providers, packs, and artifacts—not hardwired into Workbench folders.

### Topic 9 — Service-first provider architecture and third-party libraries

FACT: The chat concluded that raylib, rlgl, rlsw, raygui, raudio, SDL2, Lua, and possibly ImGui should be providers, not architecture. Dominium owns service contracts; providers satisfy them. Provider implementations live under `runtime/<service>/providers/<provider>/`; provider choices live in profiles; third-party source lives under `external/upstream/` or equivalent; third-party headers/types must be fenced.

The user specifically asked naming questions such as `sdl2` versus `sdl`, `raylib` versus `rlgl`, `win32` versus `windows`, and `d3d11` versus `directx`. The answer: use generic service roots, exact provider implementation folder names, fully qualified provider IDs, family metadata in profiles, and readable user labels.

### Topic 10 — Domino Framework boundary

FACT: The user considered whether a framework approach required a `framework/` root. The chat decided no: Domino Framework is a public surface package made from contracts and public headers; the reference implementation remains in `engine/` and `runtime/`. `framework/` and `sdk/` top-level roots should be guarded against unless explicitly contracted later.

The user later reported a commit defining this boundary and adding validators.

### Topic 11 — Proof gates and validation state

FACT: The chat tracked a shift from broad structure cleanup to proof hygiene. Fast strict, AIDE doctor/validate, RepoX strict, CMake verify/build, smoke CTest, canonical structure, provider structure, and targeted capability tests were reported as passing or passing with warnings at various stages. Full CTest/T4 release proof remained debt.

This matters because the repo can support narrow governed development but is not broad-release ready.

## 4. What We Were Trying to Achieve

### 4.1 Explicit Goals

The user explicitly wanted to stop months of refactor churn, make the directory structure future-proof, avoid new root directories, eliminate redundant `src/`/`source` patterns, make the code portable and modular, allow reuse across other games and engine projects, support Workbench and product development, and preserve the chat for future aggregation.

These goals were addressed by defining a closed root model, ownership rules, service/provider architecture, public surface governance, ABI policy, command/view/projection spine, provider profiles, and maintenance prompts.

### 4.2 Inferred Goals

INFERENCE: The user also wanted psychological closure: a clear point where structure work stops being the main activity. The assistant repeatedly distinguished “structure credible with warnings” from “perfect” and recommended targeted maintenance instead of more giant move passes once the major structure gates passed.

### 4.3 Goals That Changed Over Time

The conversation began as directory cleanup. It became architecture governance. It then became proof, provider, Workbench, framework, and preservation planning. The language baseline shifted from C89/C++98 ideas to C17/C++17 with a C-compatible ABI. The provider approach shifted from “use raylib” to “raylib is a seed provider suite behind first-party service contracts.” The framework idea shifted from adding `framework/` to defining framework boundaries through contracts and public headers.

### 4.4 Goals Still Unresolved

Full CTest/T4 remains unresolved. Some warnings remain: stale AuditX/identity evidence, launcher pack-verification marker debt, provider split warnings, public header ABI promotion warnings, pack internal `content/` layout warnings, residual schema buckets, AIDE state-like roots, and full-gate nonpath failures. Broader Workbench UI, runtime module loading, provider runtime, package runtime, gameplay, renderer implementation, native GUI, and release publication remain blocked or limited until proof gates advance.

## 5. Decisions Made and Why

| ID | Decision | Status | Why it mattered | Confidence | Label |
|---|---|---|---|---|---|
| DECISION-01 | Keep a closed canonical top-level root set. | Accepted | Prevents root sprawl. | High | FACT |
| DECISION-02 | No first-party root/nested `src` or `source`. | Accepted | Prevents generic wrappers and repeated confusion. | High | FACT |
| DECISION-03 | Treat Domino as reusable substrate and Dominium as game/product family. | Accepted | Enables reuse beyond one game. | High | FACT |
| DECISION-04 | Define framework through contracts/public headers, not a top-level `framework/` root. | Accepted and later reportedly committed. | Avoids new root ambiguity. | High | FACT |
| DECISION-05 | Use C17/C++17 mainline with C-compatible ABI boundaries. | Accepted as doctrine in chat. | Balances modern implementation with portable ABI. | Medium-High | FACT/UNVERIFIED for external toolchains |
| DECISION-06 | Use service-first provider structure for raylib/SDL/Lua. | Accepted and reportedly committed. | Enables third-party acceleration without lock-in. | High | FACT |
| DECISION-07 | Workbench is a consumer/projection surface, not authority. | Accepted | Prevents product/UI bypassing contracts. | High | FACT |
| DECISION-08 | Use module/pack/app/workspace terminology precisely. | Accepted | Prevents `module/` becoming a junk drawer. | High | FACT |
| DECISION-09 | Continue narrow governed slices; broad feature work remains blocked until gates improve. | Accepted through reported queue/status. | Prevents architecture regression. | High | FACT |
| DECISION-10 | Stop giant structure refactors after canonical structure gates are clean; use targeted maintenance. | Recommended and broadly accepted after cleanup passes. | Avoids endless churn. | Medium | INFERENCE |

Each decision depended on the assumption that the repository is being actively validated by AIDE, RepoX, structure validators, CMake, and smoke/full tests. Some exact statuses depend on user-reported task results and should be rechecked in the live repo before new work.

## 6. Ideas Considered but Rejected, Superseded, or Deprioritised

`framework/` as a top-level root was rejected. It seemed attractive as a way to separate framework and implementation, but it competed with `contracts/`, `engine/include`, `runtime/include`, and `public_surface` law. It may be reconsidered only if a future root contract explicitly defines an external SDK/source package root.

Top-level `modules/`, `plugins/`, `services/`, `profiles/`, and `labs/` were rejected. These concepts belong under existing roots: `contracts/module`, `runtime/<service>`, `content/packs`, `release/profiles`, `apps/*/proof`, `tools/experiments` if allowed, or `archive/generated/experiments`.

`apps/client/rendered/raylib` and `apps/workbench/raylib` as product architecture were rejected. Apps should be generic product shells; provider choices belong in profiles.

Raylib-shaped architecture was rejected. Raylib can be heavily used, but only behind provider/service contracts. Raylib types must not leak into engine/game/contracts/content/saves/replays/public ABI.

Pure C99 or pure C++11 were rejected as mainline baselines. C17/C++17 with C-compatible ABI was preferred.

C89/C++98 as mainline was superseded by C17/C++17, while the discipline of stable C-shaped ABI and deterministic serialization was retained.

Putting reusable modules under `apps/workbench/module/` was rejected. Workbench modules are UI/presentation modules only; the general module system lives in contracts/manifests/packs/runtime/game as appropriate.

Separate UI systems for CLI/TUI/rendered/native were rejected. Projection over shared semantic contracts was preferred.

## 7. Important Reasoning, Rationale, and Tradeoffs

The core tradeoff was between early speed and long-term replaceability. Raylib, SDL2, Lua, and raygui could accelerate visible progress, but if their types leaked into public contracts, saves, game law, or engine state, the project would become vendor-bound. The service-first provider model preserves speed while fencing contamination.

Another tradeoff was between structure purity and endless churn. The user wanted perfection, but the chat repeatedly distinguished between hard blockers, warning-level debt, and speculative cleanup. Once major old paths were removed and canonical validators passed, the correct move became targeted maintenance and proof repair rather than another broad restructure.

A third tradeoff was between generic framework ambitions and repo root simplicity. Adding `framework/`, `sdk/`, `modules/`, or `profiles/` would appear clean in isolation but would undermine the hard-won closed root model. The better solution is generated/exported packages under `release/`, public surface registries under `contracts/`, and implementation under existing roots.

The user cared most about avoiding another cleanup cycle, making code/data/modules/packs reusable, preserving determinism and backward compatibility, supporting Workbench/client/server/apps, and keeping the architecture audit-ready.

## 8. Plans, Future Work, and Next Steps

The most recently discussed next workstreams were:

1. Proof hygiene: fix stale AuditX/identity evidence and launcher marker debt so fast-strict/RepoX gates are clean.
2. Full-gate maintenance: run or shard full CTest and classify nonpath failures.
3. Projection conformance: prove CLI/text/rendered/native/headless projections over existing command/result/view/evidence contracts.
4. Presentation contract: formalize view/action/projection/document/snapshot contracts.
5. Provider implementation wedges: raylib/SDL2/Lua providers, null providers, conformance tests, forbidden include checks.
6. Pack internal layout cleanup: decide whether pack-internal `content/` is canonical or legacy.
7. Runtime/engine residual taxonomy: classify session/serialization/foundation/compatibility residuals.
8. AIDE state classification: ensure `.aide/cache`, `.aide/queue`, `.aide/reports`, `.aide/ledgers` are canonical control-plane/evidence or moved to local/generated roots.

Recommended immediate sequence based on the latest reported state:

```text
1. FAST-STRICT-EVIDENCE-MARKER-REPAIR-01 or FULL-GATE-GENERATED-EVIDENCE-REFRESH-01
2. PROJECTION-CONFORMANCE-01
3. PRESENTATION-CONTRACT-01, if not already completed or if projection work exposes gaps
4. PROVIDER-WEDGE-01 / RAYLIB-SEED-PROVIDER-01, once provider law and gates are clean
5. FULL-CTEST-AUDIT-NONPATH-01
```

## 9. Constraints, Preferences, and Non-Negotiables

### 9.1 Explicit Constraints and Preferences

The user prefers direct, rigorous, source-grounded, audit-ready answers with explicit uncertainty. The user repeatedly asked for “best possible,” “future-proof,” “modular,” and “no excuses” structure. The user dislikes vague or redundant directory names and strongly rejects root/nested `src` and `source` structures. The user wants no new top-level roots unless truly justified and contracted. The user wants downloadable handoff/report packages where possible.

### 9.2 Inferred Constraints and Preferences

INFERENCE: The user values high control over architectural naming and does not want assistant suggestions to silently become decisions. The user wants prompts that Codex/AIDE can execute without repeatedly asking for clarification. The user prefers explicit blockers and status classifications such as PASS, PASS_WITH_WARNINGS, BLOCKED, LIMITED, and NO.

### 9.3 Uncertain or Unestablished Preferences

UNCERTAIN: Exact accepted spelling of some roots (`diagnostic` versus `diagnostics`, `external/upstream` versus `external/vendor`, `lua54` versus `lua55`) may depend on current repo canon after the last commit. Future assistants should check the latest contracts and validators before renaming.

## 10. Files, Artifacts, Outputs, and Prompts

Key artifacts include:

- Earlier generated handoff files: `dominium_canonical_handoff.md` and `.txt` in `/mnt/data`. These summarize the state as of 2026-05-20 and should be preserved as historical handoff context.
- Multiple uploaded `dir_tree.json`, `dir_tree.txt`, `dirfiles_manifest.json`, `dirfiles_run.log`, and `dirfiles.zip` bundles. Their usefulness varied because several were mixed/stale. They established the need for structure-report integrity validation.
- Large Codex/AIDE prompts generated in chat, including runtime naming, pack authority, schema canon, content pack canon, app thinness, Workbench naming, AIDE scan boundary, tools fold, docs canon, RepoX/TestX canonical paths, remediation/full proof, strict debt repair, structure finalization, residual loops, provider structure, framework boundary, and full-gate legacy path routing.
- User-reported audits and commits: `CANON_STRUCTURE_FINALIZE_NOW_01`, `CANON_STRUCTURE_ACTUAL_FINAL_CLEANUP_01`, `FULL_GATE_LEGACY_TEST_ROUTE_01`, `PROVIDER_STRUCTURE_CANON_01`, and `domino_framework_boundary.md`.
- The current uploaded preservation prompt: `Pasted text.txt`, which requested this complete preservation package.

## 11. Open Questions and Unresolved Issues

1. Is full CTest/T4 now green? Known answer from chat: no, not yet. It needs auditing and repair.
2. Are stale AuditX/identity evidence and launcher marker debt fixed? Last visible status said no or still pending.
3. Are raylib/SDL2/Lua providers implemented or only planned? Last status said no third-party implementation was introduced; provider work remains separate.
4. Is `external/upstream` or `external/vendor` canonical in the latest repo? Needs live repo verification.
5. Is Lua provider `lua54` or `lua55` chosen? The chat discussed pinning one but did not establish a final user decision.
6. Is `contracts/diagnostic` or `contracts/diagnostics` canonical? The chat suggested consistency but did not confirm final repo state.
7. Are pack-internal `content/` folders law or legacy? Still an open cleanup item.
8. Are `.aide/cache` and `.aide/queue` canonical control-plane data or mutable state? Needs classification assurance.

## 12. Risks, Failure Modes, and What Future Chats Might Get Wrong

A future assistant might restart broad structure refactoring despite the repo being past the structure crisis. Avoid this by checking the latest validators and focusing on targeted warnings.

A future assistant might add `framework/`, `modules/`, `profiles/`, or `labs/` roots because they seem conceptually clean. This would violate the hard-won closed-root doctrine unless explicitly approved by contracts.

A future assistant might treat raylib, SDL2, Lua, or ImGui as architecture rather than providers. Avoid by enforcing provider manifests, forbidden include validators, and service-first structure.

A future assistant might assume Workbench modules are general modules. They are not. Workbench modules are UI/product modules; general module law lives under contracts/manifests/packs.

A future assistant might confuse generated reports with source truth. The chat repeatedly identified structure-report integrity as a problem.

A future assistant might treat PASS_WITH_WARNINGS as full green. It is not. Feature readiness remains limited until full-gate proof improves.

## 13. What This Chat Contributes to the Larger Project or Future Spec Book

This chat should feed into spec-book chapters on repository structure, root policy, naming law, distribution/install layout, public surface registry, API/ABI policy, provider architecture, module/pack/app/workspace composition, Workbench architecture, presentation/projection design, testing/proof gates, AIDE workflow, and third-party provider policy.

Formal requirements candidates include: closed top-level root set; no `src/source`; service-first provider structure; provider profile model; third-party leakage fences; C17/C++17 with C-compatible ABI; public surface registry; command/result/refusal/view/action projection spine; Workbench non-authority rule; and package/save/replay compatibility law.

Potential overlaps with other chats: worldgen, Workbench modules, raylib integration, provider wedges, language baseline, and AIDE workflow law. Potential conflicts: exact Lua version, exact external third-party path convention, exact contract singular/plural root names, and how soon to implement raylib providers versus projection contracts.

## 14. What I Should Remember

- The top-level structure is mostly settled; do not redesign it casually.
- Domino Framework is not a `framework/` root; it is contracts, public surfaces, service/provider law, public headers, and conformance tests.
- Dominium is the game/product family; Domino is the reusable substrate.
- Raylib/SDL2/Lua are providers, not architecture.
- Apps should not hardwire providers in their paths; profiles select providers.
- Workbench is a projection/operator over commands, views, evidence, modules, packs, and artifacts; it is not authority.
- Module identity, pack identity, provider identity, app identity, and workspace identity are not paths.
- Fast strict and smoke can be green while full CTest remains red. Do not overclaim.
- Remaining work is proof hygiene and targeted hardening, not another broad root cleanup.

## 15. Best Questions I Can Ask Next in This Chat

### 15.1 Understanding the Chat
- “Summarize the Domino/Dominium split in one page.”
- “Explain why we rejected a top-level `framework/` root.”
- “Explain the difference between component, service, provider, pack, module, workspace, app, and artifact.”

### 15.2 Decisions
- “Which decisions are definitely accepted versus only suggested?”
- “Which naming choices still need live repo verification?”

### 15.3 Tasks and Next Actions
- “Generate the next prompt for FAST-STRICT-EVIDENCE-MARKER-REPAIR-01.”
- “Generate PROJECTION-CONFORMANCE-01.”
- “Generate PROVIDER-WEDGE-01 for raylib/SDL2/Lua.”

### 15.4 Artifacts and Files
- “List every generated handoff and audit artifact from this chat.”
- “Which dirfiles exports were inconsistent and why?”

### 15.5 Risks and Verification
- “What are the highest-risk ways a future assistant could corrupt the architecture?”
- “What live repo facts should be verified before continuing?”

### 15.6 Future Spec Book / Aggregation
- “Turn this chat into a spec-book chapter outline.”
- “Extract formal requirements from the chat.”

### 15.7 Deep-Dive Questions Specific to This Chat
- “Should provider profiles live under release/profiles or content/profiles?”
- “How should pack-internal `content/` versus `data/` be resolved?”
- “What should the first raylib provider wedge implement?”

## 16. Compact Human Summary

This chat was a long, high-stakes architecture and repository convergence session for Dominium. The user wanted to end months of refactor churn and finally establish a structure capable of supporting real development. The conversation began with directory layout and grew into a broader architecture for a reusable Domino substrate, a Dominium game/product family, a Workbench production environment, and an AIDE control-plane harness.

The most important structural conclusion was to keep a small closed set of active roots: `apps`, `engine`, `game`, `runtime`, `contracts`, `content`, `docs`, `tests`, `tools`, `scripts`, `cmake`, `external`, `release`, and `archive`, plus a few project/tooling roots. The repo should not add `framework`, `modules`, `plugins`, `services`, `profiles`, `labs`, `src`, `source`, or vague junk roots. Paths encode ownership, not identity. Public identity belongs in contracts, manifests, registries, stable IDs, public headers, and compatibility tests.

The chat then established the Domino versus Dominium distinction. Domino is the reusable deterministic/runtime framework. Dominium is one game/product family built on it. Workbench is a production and validation environment over the same contracts. AIDE is the control-plane harness. The “Domino Framework” should not be a new top-level `framework/` root; it is the collection of public surfaces, contracts, ABI law, service/provider law, public headers under `engine/include/domino` and `runtime/include/domino`, and conformance tests.

The main technical doctrine became: freeze contracts, replace implementations, preserve artifacts, verify behavior. C17/C++17 is the mainline language baseline, but public ABI remains C-compatible: POD structs, explicit versioning, opaque handles, explicit ownership, no C++ ABI leakage, and no third-party types in stable surfaces. Deterministic law remains first-party.

The Workbench/module discussion produced a precise vocabulary. A component is a source/build unit; a service is a callable runtime capability; a provider is a replaceable implementation; a pack is distributable authored payload; a module is a declared functional extension unit; a workspace is a large user-facing Workbench composition; an app is a shipped product composition; an artifact is a persisted versioned object. Reusable modules should not live under `apps/workbench`; Workbench modules are UI modules only. General module law belongs under `contracts/module`, module payloads can be delivered through packs, and reusable behavior lives under `runtime`, `game`, or `engine` depending ownership.

The presentation/UI model was also unified. CLI, text/TUI, rendered GUI, native GUI, headless reports, Workbench panels, CI, and AIDE should all project the same semantic contracts. The spine is intent → command → capability/refusal check → service → result/document/snapshot → diagnostics/evidence → view/action model → projection → shell. This avoids building separate UI systems and prevents Workbench from becoming authority.

Third-party libraries were then placed into the provider model. Raylib, rlgl, rlsw, raygui, raudio, SDL2, Lua, and possibly ImGui are valuable accelerators, but only as providers. Runtime services own the stable identity; providers implement them. Correct paths look like `runtime/render/providers/raylib`, `runtime/platform/providers/sdl2`, `runtime/script/providers/lua54`, and provider choices live in profiles, not app folder names. Third-party types must not leak into `engine`, `game`, `contracts`, `content`, saves, replays, packs, or public ABI.

Many executable Codex/AIDE prompts were generated or summarized, and the user reported commits that progressively cleaned the repo. The most recent state is credible but not perfect: canonical structure and old-path cleanup are mostly green; fast strict, CMake verify/build, smoke CTest, and targeted capability tests pass; full CTest/T4 remains debt; feature readiness is limited; broad feature work remains blocked. The next meaningful work is proof hygiene and targeted hardening, not another wide directory refactor.


# STRUCTURED REGISTERS — Dominium Canonical Structure and Domino Framework Architecture

## 17. Workstream Register

| ID | Name | Objective | Current state | Desired end state | Status | Priority | Confidence | Label |
|---|---|---|---|---|---|---|---|---|
| WORKSTREAM-01 | Canonical Repository Structure | End root/path chaos and enforce ownership roots. | Mostly clean; residual warnings remain. | Closed root set with validators and no stale active paths. | PASS_WITH_WARNINGS | P0 | High | FACT |
| WORKSTREAM-02 | Domino Framework Boundary | Define framework without new top-level root. | Reported committed and validated. | Framework identity lives in contracts/public headers/service law. | PASS_WITH_WARNINGS | P0 | High | FACT |
| WORKSTREAM-03 | Public Surface / ABI Governance | Register stable/public surfaces and enforce C-compatible ABI. | Scaffolds exist; warnings remain. | Every stable surface registered, versioned, tested. | Active | P0 | Medium | FACT |
| WORKSTREAM-04 | Service-first Provider Architecture | Make raylib/SDL/Lua providers, not architecture. | Provider structure partly committed; implementation still pending. | Runtime service providers with conformance tests and profiles. | Active | P0 | High | FACT |
| WORKSTREAM-05 | Presentation / Projection Spine | Unify CLI/TUI/rendered/native/headless over semantic views/actions. | Concept accepted; task remains active. | Projection conformance over shared commands/views/evidence. | Active | P1 | High | FACT |
| WORKSTREAM-06 | Workbench Product Spine | Build Workbench modules/workspaces through contracts. | Validation slice reported done; broad UI blocked. | Workbench shell/module/workspace over command/view/projection system. | Limited | P1 | High | FACT |
| WORKSTREAM-07 | Full-gate Proof / CTest | Remove stale tests and achieve full release proof. | Legacy path subset fixed; full CTest not green. | Full CTest/T4 classified or green. | Active debt | P0 | High | FACT |
| WORKSTREAM-08 | AIDE Control Plane | Govern AIDE queue/tasks/evidence and avoid stale generated state. | Some warnings remain. | AIDE workflow law and clean evidence/queue state. | Active debt | P1 | Medium | FACT |
| WORKSTREAM-09 | Pack/Content Authority | Keep authored packs under content and package law under contracts. | Mostly fixed; pack internal layout warnings remain. | Clear pack authority and consistent internal layout. | Active debt | P1 | High | FACT |

## 18. Decision Register

| ID | Decision | Status | Evidence / basis | Rationale | Implications | Related workstream | Confidence | Label |
|---|---|---|---|---|---|---|---|---|
| DECISION-01 | Keep closed canonical root set. | Accepted | Repeated prompts/reports. | Prevent root sprawl. | No casual new roots. | WORKSTREAM-01 | High | FACT |
| DECISION-02 | No first-party `src`/`source`. | Accepted | User explicit objection. | Avoid generic wrappers. | Validators should enforce. | WORKSTREAM-01 | High | FACT |
| DECISION-03 | Domino ≠ Dominium. | Accepted | Multiple later summaries. | Enables reuse. | Separate reusable substrate from game/product. | WORKSTREAM-02 | High | FACT |
| DECISION-04 | No top-level `framework/`. | Accepted | User-reported commit `repo: define Domino framework boundary`. | Avoid root ambiguity. | Framework is contracts/public headers. | WORKSTREAM-02 | High | FACT |
| DECISION-05 | C17/C++17 mainline with C-compatible ABI. | Accepted doctrine. | User pasted language-baseline synthesis. | Modern implementation plus portable boundary. | ABI validators and public header rules. | WORKSTREAM-03 | Medium | FACT/VERIFY |
| DECISION-06 | Third-party libraries are providers. | Accepted | Raylib/SDL/Lua discussions. | Avoid vendor lock-in. | Runtime provider paths and manifests. | WORKSTREAM-04 | High | FACT |
| DECISION-07 | Workbench is not authority. | Accepted | Workbench/presentation discussions. | Prevent UI bypass. | Workbench calls commands/services. | WORKSTREAM-06 | High | FACT |
| DECISION-08 | CLI/TUI/rendered/native are projections. | Accepted | Presentation spine discussions. | Avoid four UI systems. | `runtime/projection/*`, semantic contracts. | WORKSTREAM-05 | High | FACT |
| DECISION-09 | Provider choices live in profiles, not app paths. | Accepted | Provider structure reports. | Avoid product variants. | Use `release/profiles`/`content/profiles`. | WORKSTREAM-04 | High | FACT |

## 19. Task Register

| ID | Task | Priority | Urgency | Owner | Dependencies | Inputs needed | Expected output | Next step | Related workstream | Label |
|---|---|---|---|---|---|---|---|---|---|---|
| TASK-01 | Repair stale AuditX/identity/launcher marker fast-strict debt. | P0 | U0 | AIDE/Codex | Current repo state | Latest fast-strict failure output | Clean normal gate | Generate/execute repair prompt | WORKSTREAM-07 | FACT |
| TASK-02 | Projection conformance. | P1 | U1 | AIDE/Codex | Presentation contract basics | Existing command/result/view artifacts | Conformance tests for projection modes | Run `PROJECTION-CONFORMANCE-01` | WORKSTREAM-05 | FACT |
| TASK-03 | Presentation contract finalization. | P1 | U1 | AIDE/Codex | Command/diagnostic contracts | Current contracts tree | View/action/projection schemas and validators | Run `PRESENTATION-CONTRACT-01` | WORKSTREAM-05 | FACT |
| TASK-04 | Raylib/SDL/Lua provider wedge. | P1 | U2 | AIDE/Codex | Provider structure and third-party fences | Provider manifests, vendored sources | First provider implementation scaffold | Run `PROVIDER-WEDGE-01` | WORKSTREAM-04 | INFERENCE |
| TASK-05 | Full CTest audit nonpath failures. | P0 | U1 | AIDE/Codex | Legacy path route done | Full CTest output | Failure ledger | Run `FULL-CTEST-AUDIT-NONPATH-01` | WORKSTREAM-07 | FACT |
| TASK-06 | Pack internal layout canon. | P1 | U2 | AIDE/Codex | Pack authority mostly fixed | Current pack leaves | Documented or normalized pack internals | Run pack layout task | WORKSTREAM-09 | FACT |
| TASK-07 | AIDE state classification. | P1 | U2 | AIDE/Codex | AIDE control-plane model | `.aide` tree | Clear source/local/generated classification | Run AIDE state task | WORKSTREAM-08 | FACT |
| TASK-08 | Runtime/engine residual taxonomy. | P2 | U2 | AIDE/Codex | Canonical structure cleanup | Current roots | Classified session/serialization/foundation etc. | Targeted cleanup | WORKSTREAM-01 | FACT |

## 20. Constraint Register

| ID | Constraint | Type | Hard/soft | Source / basis | Practical implication | Violation risk | Confidence | Label |
|---|---|---|---|---|---|---|---|---|
| CONSTRAINT-01 | No new top-level roots without contract approval. | Structure | Hard | User and repeated doctrine. | Reject `framework/`, `modules/`, `profiles/`, `labs`. | Root sprawl. | High | FACT |
| CONSTRAINT-02 | No first-party `src`/`source` wrappers. | Structure | Hard | User explicit objection. | Implementation lives under ownership paths. | Refactor recurrence. | High | FACT |
| CONSTRAINT-03 | No third-party type leakage into stable law. | Architecture | Hard | Provider doctrine. | Raylib/SDL/Lua only in providers/proofs. | Vendor lock-in. | High | FACT |
| CONSTRAINT-04 | Public ABI is C-compatible, not C++ ABI. | ABI | Hard | Language baseline doctrine. | POD/opaque/versioned structs. | Binary instability. | Medium-High | FACT |
| CONSTRAINT-05 | Workbench must use command/service/evidence spine. | Product | Hard | Workbench doctrine. | No private validator/tool bypass. | UI becomes authority. | High | FACT |
| CONSTRAINT-06 | Full release readiness requires full-gate proof. | Testing | Hard for release | Reported status. | Do not claim release green. | False readiness. | High | FACT |

## 21. User Preference Register

| ID | Preference | Area | Explicit/inferred/uncertain | Strength | Practical implication | Risk if wrong | Label |
|---|---|---|---|---|---|---|---|
| PREF-01 | Direct, rigorous, audit-ready answers. | Communication | Explicit profile + behavior | Strong | Use clear status, caveats, evidence. | User distrust. | FACT |
| PREF-02 | Avoid vague/soft language when structure is bad. | Communication | Inferred | Strong | Say not done when not done. | Misleading reassurance. | INFERENCE |
| PREF-03 | Prefer executable prompts for Codex/AIDE. | Workflow | Explicit through repeated requests | Strong | Generate concrete tasks with acceptance criteria. | Work stalls. | FACT |
| PREF-04 | Do not ask unnecessary clarifying questions. | Workflow | Explicit system/user preference | Strong | Proceed with assumptions and labels. | User frustration. | FACT |
| PREF-05 | Keep architecture future-proof and reusable. | Technical | Explicit | Strong | Favor contracts/providers/profiles over vendor/product paths. | Future refactor. | FACT |

## 22. Open Questions Register

| ID | Question / issue | Why it matters | Known information | Unknown information | Resolution path | Priority | Related workstream | Label |
|---|---|---|---|---|---|---|---|---|
| QUESTION-01 | Is full CTest green after latest fixes? | Determines release/full proof readiness. | Last visible status: not green/not fully run. | Current live status. | Run full CTest or audited shard. | P0 | WORKSTREAM-07 | FACT |
| QUESTION-02 | Lua 5.4 or 5.5? | Script ABI/provider pinning. | Chat says pin one. | Final choice. | Decide after compatibility/security review. | P1 | WORKSTREAM-04 | UNCERTAIN |
| QUESTION-03 | `external/upstream` or `external/vendor`? | Consistency and provenance. | Both discussed; final should choose one. | Latest repo canon. | Check contracts/docs. | P1 | WORKSTREAM-04 | UNCERTAIN |
| QUESTION-04 | Is pack internal `content/` canonical? | Pack layout and tooling. | Warning remains. | Pack law. | Run pack internal layout task. | P1 | WORKSTREAM-09 | FACT |
| QUESTION-05 | Are `.aide/cache` and `.aide/queue` source or local state? | Prevent generated/live state confusion. | Need classification. | Exact contents. | AIDE state classification task. | P1 | WORKSTREAM-08 | FACT |

## 23. Artifact Ledger

| ID | Artifact / file / prompt / output | Type | Purpose | Status | Origin | Carry forward? | Notes | Label |
|---|---|---|---|---|---|---|---|---|
| ARTIFACT-01 | `dominium_canonical_handoff.md/.txt` | Handoff files | Earlier self-contained summary. | Created earlier | This chat | Yes | Historical snapshot as of 2026-05-20. | FACT |
| ARTIFACT-02 | `dir_tree.json`, `dirfiles_manifest.json`, ZIP exports | Structure evidence | Inspect repo tree. | Mixed quality | User uploads | Yes with caveats | Many bundles were inconsistent/stale. | FACT |
| ARTIFACT-03 | `CANON_STRUCTURE_ACTUAL_FINAL_CLEANUP_01.md` | Audit | Actual structure cleanup. | User-reported committed | Repo | Yes | Key proof of structure cleanup. | FACT |
| ARTIFACT-04 | `FULL_GATE_LEGACY_TEST_ROUTE_01.md` | Audit | Routed stale full-gate tests. | User-reported committed | Repo | Yes | Important proof-gate improvement. | FACT |
| ARTIFACT-05 | `domino_framework_boundary.md` | Architecture doc | Defines framework without root. | User-reported committed | Repo | Yes | Core decision artifact. | FACT |
| ARTIFACT-06 | Large Codex/AIDE prompts | Prompts | Execute cleanup and governance tasks. | Many generated in chat | This chat | Yes | Useful prompt templates. | FACT |
| ARTIFACT-07 | Current preservation package | Report package | Preserve this chat. | Created now | This response | Yes | See file links. | FACT |

## 24. Rejected / Superseded Options Register

| ID | Option | Status | Reason | Final or tentative? | Reconsider conditions | Related workstream | Label |
|---|---|---|---|---|---|---|---|
| REJECTED-01 | Top-level `framework/` | Rejected | Competes with contracts/public headers. | Mostly final | External SDK/root contract requires it. | WORKSTREAM-02 | FACT |
| REJECTED-02 | Top-level `modules/` | Rejected | Would become junk drawer. | Final unless separate module repo. | True module repository. | WORKSTREAM-06 | FACT |
| REJECTED-03 | Product paths like `apps/client/rendered/raylib` | Rejected | Provider choice belongs in profiles. | Final | Temporary proof boot only. | WORKSTREAM-04 | FACT |
| REJECTED-04 | Raylib as engine architecture | Rejected | Vendor lock-in. | Final | None; raylib remains provider. | WORKSTREAM-04 | FACT |
| REJECTED-05 | C89/C++98 as mainline | Superseded | Too restrictive for current target. | Tentative on platform verification | Retro/research lane. | WORKSTREAM-03 | FACT |
| REJECTED-06 | Separate UI systems for CLI/TUI/rendered/native | Rejected | Duplicates behavior. | Final | None; projections only. | WORKSTREAM-05 | FACT |

## 25. Risk Register

| ID | Risk / failure mode | Consequence | Likelihood | Severity | Mitigation | Related workstream | Label |
|---|---|---|---|---|---|---|---|
| RISK-01 | Future assistant restarts broad structure churn. | Lost time/regression. | Medium | High | Use targeted tasks only; check validators. | WORKSTREAM-01 | INFERENCE |
| RISK-02 | PASS_WITH_WARNINGS treated as full green. | Premature feature/release work. | Medium | High | Preserve readiness labels. | WORKSTREAM-07 | FACT |
| RISK-03 | Third-party types leak into contracts/game/saves. | Vendor lock-in. | Medium | High | Forbidden include/type validators. | WORKSTREAM-04 | FACT |
| RISK-04 | Workbench calls private tools directly. | UI becomes authority. | Medium | High | Command/view/action contracts. | WORKSTREAM-06 | FACT |
| RISK-05 | Mixed structure reports mislead agents. | Chasing stale paths. | High historically | Medium | Structure report integrity validator. | WORKSTREAM-01 | FACT |
| RISK-06 | Full CTest remains unclassified. | Hidden release blockers. | Medium | High | Full-gate audit ledger. | WORKSTREAM-07 | FACT |

## 26. Verification Queue

| ID | Item requiring verification | Why verification is needed | Suggested source/type | Priority | Related workstream | Label |
|---|---|---|---|---|---|---|
| VERIFY-01 | Latest live repo status after last commit. | User reports may be stale. | Git status / latest audit. | P0 | All | FACT |
| VERIFY-02 | Full CTest result. | Full release readiness. | CTest output ledger. | P0 | WORKSTREAM-07 | FACT |
| VERIFY-03 | Third-party versions/support floors. | External facts change. | Official raylib/SDL/Lua docs. | P1 | WORKSTREAM-04 | VERIFY |
| VERIFY-04 | Provider profile path convention. | Avoid path churn. | Current contracts/docs. | P1 | WORKSTREAM-04 | UNCERTAIN |
| VERIFY-05 | AIDE state classification. | Prevent local/generated contamination. | Inspect `.aide` dirs. | P1 | WORKSTREAM-08 | FACT |

## 27. Chronological Timeline Register

| Sequence | Event / topic | What changed or was decided | Why it mattered | Current relevance | Confidence |
|---|---|---|---|---|---|
| 1 | Initial directory-layout debate | Need multiple layouts but one virtual-root/projection model. | Prevent install/package/source confusion. | Background doctrine. | High |
| 2 | User backlash against `src`/root sprawl | No `src/source`, no new roots. | Core constraint. | Still active. | High |
| 3 | Canonical root model established | Closed source root set. | End root chaos. | Current basis. | High |
| 4 | Cleanup prompts generated/executed | Runtime/game/schema/content/tools/docs/tests moved. | Practical convergence. | Historical/audit context. | High |
| 5 | Public surface/API/ABI phase | Need stable contract governance. | Reuse/future-proofing. | Active. | High |
| 6 | C17/C++17 baseline | Mainline implementation modernized. | Language policy. | Active, verify toolchains. | Medium |
| 7 | Module/workbench vocabulary split | Component/service/provider/pack/module/workspace/app terms. | Prevent junk drawers. | Active. | High |
| 8 | Presentation spine | UI modes become projections. | Reusable Workbench/client/UI. | Active. | High |
| 9 | Provider/raylib/SDL/Lua model | Third-party as providers. | Fast progress + replaceability. | Active. | High |
| 10 | Framework boundary | No `framework/` root. | Prevent root sprawl. | Active. | High |
| 11 | Full-gate legacy routing | Retired path tests updated. | Cleaner proof signal. | Recent status. | High |

## 28. Spec Book Contribution Register

| Spec-book area | Contribution from this chat | Source IDs | Should become requirement/context/open issue? | Confidence | Notes |
|---|---|---|---|---|---|
| Repo structure | Closed root model, no src/source. | DECISION-01, DECISION-02 | Requirement | High | Core canon. |
| Framework architecture | Domino framework via contracts/public headers. | DECISION-03, DECISION-04 | Requirement | High | Avoid top-level framework. |
| Provider architecture | Service-first providers and profiles. | DECISION-06 | Requirement | High | Raylib/SDL/Lua policy. |
| Workbench architecture | Workbench as projection/operator. | DECISION-07, DECISION-08 | Requirement/context | High | Guides first UI work. |
| ABI/language policy | C17/C++17 + C-compatible ABI. | DECISION-05 | Requirement after verification | Medium | External facts need verification. |
| Testing/proof gates | Fast strict vs full gate. | TASK-01, TASK-05 | Requirement/open issue | High | Full CTest debt remains. |


# Context Transfer Packet for a Future Chat

## Ultra-Condensed Bootstrap Brief

This old chat concerned Dominium’s transition from a messy, root-sprawling game repository into a deterministic, contract-governed, provider-backed, pack-composed simulation platform built on a reusable Domino substrate. The user’s core need was to stop months of structure churn and establish an architecture that supports real development of engine, game, Workbench, apps, modules, packs, providers, and future games without another large refactor.

The major accepted root model is: `apps/`, `engine/`, `game/`, `runtime/`, `contracts/`, `content/`, `docs/`, `tests/`, `tools/`, `scripts/`, `cmake/`, `external/`, `release/`, `archive/`, plus `.aide/`, `.aide.local.example/`, `.github/`, `.vscode/`. Do not add top-level `framework/`, `modules/`, `plugins/`, `services/`, `profiles/`, `labs/`, `sdk/`, `src/`, or `source/` unless explicitly contracted.

The key doctrine is: path is not identity; implementation is not contract; UI is not authority; generated output is not source truth. Domino Framework is not a source root; it is the public-surface package made of contracts, ABI law, service/provider law, public headers under `engine/include/domino` and `runtime/include/domino`, and conformance tests. Dominium is the game/product family. Workbench is the production/editor/evidence environment. AIDE is the control-plane harness.

The system vocabulary is: component = source/build unit; service = callable runtime capability; provider = replaceable implementation; pack = authored distributable payload; module = declared functional extension unit; workspace = Workbench composition; app = product composition; artifact = persisted versioned object. Raylib, rlgl, rlsw, raygui, raudio, SDL2, Lua, and similar libraries are providers, not architecture. Provider implementations live under `runtime/<service>/providers/<provider>/`; provider selections live in `release/profiles/` or `content/profiles/`; apps stay generic.

The presentation model is: intent → command → capability/refusal check → service → result/document/snapshot → diagnostics/evidence → view/action model → projection → shell. CLI, text/TUI, rendered GUI, native GUI, headless, Workbench, CI, and AIDE should be projections of the same semantic surfaces.

Current repo status per user reports: broad structure chaos is mostly resolved; canonical structure and fast strict pass or pass with warnings; full CTest/T4 release proof remains debt; broad feature work remains blocked; narrow governed tasks continue. Recent reported work included final canonical structure cleanup, full-gate legacy path routing, provider-structure enforcement, and Domino framework boundary definition.

Recommended next action depends on latest repo status: if fast-strict/RepoX still fail on stale AuditX/identity or launcher marker debt, repair that first. Otherwise proceed with `PROJECTION-CONFORMANCE-01` and/or `PRESENTATION-CONTRACT-01`, then provider wedge tasks for raylib/SDL/Lua.

## Source Hierarchy

1. Direct user statements in this chat.
2. Explicit user-accepted decisions and user-reported commits/statuses.
3. Task and constraint registers in this preservation package.
4. Uploaded directory tree/status artifacts, with caveats for stale/mixed runs.
5. Earlier generated handoff files in `/mnt/data`.
6. Inferences clearly marked.
7. Assistant suggestions not accepted by the user.
8. General model knowledge.

## Operating Rules for Future Assistants

Preserve FACT / INFERENCE / UNCERTAIN / PROJECT-CONTEXT labels. Do not assume access to the old chat. Do not re-ask questions already answered. Verify stale facts before relying on them. Do not treat tentative brainstorms as decisions. Do not repeat rejected options such as adding top-level `framework/`, `modules/`, or `profiles/`. Preserve artifacts and use structured outputs when continuing. Do not restart broad structure cleanup unless a validator finds a hard blocker.

## Active Workstreams

- Canonical structure and root policy.
- Domino Framework boundary and public surface governance.
- C17/C++17 and C-compatible ABI policy.
- Service-first provider architecture and third-party fencing.
- Presentation/projection spine.
- Workbench module/workspace development.
- Full-gate proof repair.
- AIDE workflow/evidence classification.

## Current Priorities

1. Repair stale proof/evidence/marker debt if fast-strict is blocked.
2. Proceed to `PROJECTION-CONFORMANCE-01` / `PRESENTATION-CONTRACT-01` when gates allow.
3. Implement provider wedge for raylib/SDL/Lua only through service/provider contracts.
4. Continue full CTest/T4 audit.

## Current Open Questions

- Is full CTest green in the live repo?
- Which Lua version is pinned?
- Is `external/upstream` or `external/vendor` canonical?
- Are AIDE cache/queue/reports canonical control-plane data or local/generated state?
- Is pack-internal `content/` canonical or legacy?

## Recommended First Action

Check the latest live repo gate status. If fast-strict or RepoX still fails due stale evidence/marker debt, run a focused proof-hygiene repair. If normal gates are clean, run `PROJECTION-CONFORMANCE-01` next.


spec_sheet:
  metadata:
    chat_label: "Dominium Canonical Structure and Domino Framework Architecture"
    date_anchor: "2026-05-27 Australia/Melbourne"
    source_scope: "This chat only unless labelled PROJECT-CONTEXT"
    apparent_coverage: "Partial but substantial"
    confidence_1_to_5: 4
    staleness_risk: "medium-high for live repo state; medium for external library facts; low for explicit architecture decisions"
    safe_for_aggregation: "yes_with_caveats"
    main_limitations:
      - "Full transcript export unavailable."
      - "Some uploaded files expired."
      - "Several repo structure bundles in the chat were mixed/stale."
      - "Latest live repo state should be verified before action."

  summary:
    one_sentence: "This chat converged Dominium from directory-structure chaos toward a Domino framework model based on contracts, public surfaces, services, providers, packs, modules, profiles, proofs, and narrow governed product slices."
    short_brief: "The chat established a closed top-level root model, rejected src/source/root sprawl, distinguished Domino from Dominium, defined service-first provider architecture for raylib/SDL/Lua, unified Workbench and UI around command/view/action/projection contracts, and tracked multiple cleanup/proof commits while preserving full-gate debt as unresolved."
    main_topics:
      - "Canonical repository structure"
      - "Domino/Dominium framework boundary"
      - "Public surface and ABI governance"
      - "Service-first providers"
      - "Workbench modules/workspaces"
      - "Presentation/projection architecture"
      - "Full-gate proof debt"
    main_outputs:
      - "Earlier handoff files"
      - "Large Codex/AIDE cleanup prompts"
      - "Structured doctrine for roots, providers, modules, packs, apps, workspaces"
    highest_priority_carry_forward:
      - "Do not add top-level framework/modules/profiles/labs/sdk roots."
      - "Keep third-party libraries behind runtime providers."
      - "Repair proof-gate debt before broad feature work."

  source_rules:
    labels_used: ["FACT", "INFERENCE", "UNCERTAIN / UNVERIFIED", "PROJECT-CONTEXT"]
    conflict_rules:
      - "User-reported current repo state supersedes older uploaded directory trees if clearly later."
      - "Fresh tracked-only exports supersede mixed or stale dirfiles bundles."
      - "Explicit user acceptance supersedes assistant brainstorm."
    staleness_rules:
      - "External library versions and platform support require verification."
      - "Live repo state requires fresh git/validator checks."

  user_preferences:
    explicit:
      - "Direct, audit-ready, source-grounded answers."
      - "No src/source folder sprawl."
      - "No casual new top-level roots."
      - "Generate executable prompts when requested."
    inferred:
      - "The user wants decisive status labels and no false reassurance."
      - "The user values architecture that can survive future rewrites."
    uncertain_or_not_established:
      - "Exact singular/plural spelling for some contract roots."
      - "Exact external/upstream versus external/vendor convention."

  workstreams:
    - id: WORKSTREAM-01
      name: "Canonical Repository Structure"
      label: FACT
      objective: "Stop root/path chaos."
      current_state: "Mostly clean with warnings."
      desired_end_state: "Closed root set and no active stale paths."
      status: "PASS_WITH_WARNINGS"
      priority: P0
      background: "Repo had many bad roots and redundant structures."
      decisions_made: [DECISION-01, DECISION-02]
      decisions_pending: []
      tasks: [TASK-05, TASK-08]
      constraints: [CONSTRAINT-01, CONSTRAINT-02]
      dependencies: []
      timeline: "Major cleanup occurred across many reported commits."
      blockers: []
      risks: [RISK-01, RISK-05]
      artifacts: [ARTIFACT-02, ARTIFACT-03]
      success_criteria: ["no unexpected top-level roots", "canonical structure validator passes"]
      next_action: "Targeted residuals only."
      verification_needed: [VERIFY-01]
      confidence: high
    - id: WORKSTREAM-04
      name: "Service-first Provider Architecture"
      label: FACT
      objective: "Use third-party libraries as replaceable providers."
      current_state: "Provider structure reportedly committed; provider implementations pending."
      desired_end_state: "Providers selected by profiles and tested by conformance suites."
      status: "active"
      priority: P0
      background: "Raylib/SDL/Lua considered as accelerators."
      decisions_made: [DECISION-06]
      decisions_pending: ["Lua version", "external source path convention"]
      tasks: [TASK-04]
      constraints: [CONSTRAINT-03]
      dependencies: [WORKSTREAM-03]
      timeline: "Provider model refined after rejecting raylib-shaped architecture."
      blockers: []
      risks: [RISK-03]
      artifacts: []
      success_criteria: ["forbidden include validator passes", "provider conformance tests exist"]
      next_action: "Provider wedge after proof gates."
      verification_needed: [VERIFY-03, VERIFY-04]
      confidence: high

  decisions:
    - id: DECISION-04
      decision: "Do not add top-level framework/."
      status: "accepted"
      label: FACT
      evidence_or_basis: "User-reported Domino framework boundary commit."
      rationale: "Framework should be contracts/public headers/service law, not a new source root."
      implications: "Public APIs live under contracts and include roots."
      related_workstreams: [WORKSTREAM-02]
      uncertainty: "Need latest repo verification for exact files."
    - id: DECISION-06
      decision: "Third-party libraries are providers."
      status: "accepted"
      label: FACT
      evidence_or_basis: "Multiple raylib/SDL/Lua turns and provider-structure commit report."
      rationale: "Allows acceleration without vendor lock-in."
      implications: "runtime/<service>/providers/<provider>; apps select profiles."
      related_workstreams: [WORKSTREAM-04]
      uncertainty: "Provider implementations not yet complete."

  tasks:
    - id: TASK-01
      task: "Repair fast-strict stale evidence/launcher marker debt."
      priority: P0
      urgency: U0
      owner: "AIDE/Codex"
      dependencies: []
      inputs_needed: ["latest fast-strict/RepoX output"]
      expected_output: "clean normal gate or exact failure ledger"
      next_step: "generate focused repair prompt"
      related_workstreams: [WORKSTREAM-07]
      label: FACT
      confidence: high

  constraints:
    - id: CONSTRAINT-01
      constraint: "No new top-level roots without explicit contract approval."
      type: "repository structure"
      hard_or_soft: hard
      source_or_basis: "repeated user requirement and cleanup doctrine"
      implication: "Reject framework/modules/profiles/labs as roots."
      violation_risk: "root sprawl and renewed restructure cycle"
      label: FACT
      confidence: high

  open_questions:
    - id: QUESTION-02
      question: "Which Lua version should be pinned?"
      why_it_matters: "Lua ABI/version affects script provider and mod compatibility."
      known: "Scripts should target dominium/domino script API, not raw Lua ABI."
      unknown: "Final Lua 5.4 vs 5.5 choice."
      resolution_path: "Verify platform/library constraints and choose one."
      priority: P1
      related_workstreams: [WORKSTREAM-04]
      label: UNCERTAIN

  rejected_or_superseded_options:
    - id: REJECTED-01
      option: "Top-level framework/ root"
      status: "rejected"
      reason: "Duplicates contracts/public headers and reopens root sprawl."
      final_or_tentative: "mostly final"
      reconsider_conditions: "only if root contract is explicitly changed for external SDK/source package"
      related_workstreams: [WORKSTREAM-02]
      label: FACT

  artifacts:
    - id: ARTIFACT-01
      name_or_description: "dominium_canonical_handoff.md and .txt"
      type: "handoff"
      purpose: "Earlier continuation summary"
      status: "created earlier and mounted"
      origin: "this chat"
      carry_forward: true
      notes: "Historical snapshot, not latest state"
      label: FACT

  risks:
    - id: RISK-03
      risk: "Third-party type leakage into stable surfaces"
      consequence: "vendor lock-in and replay/save incompatibility"
      likelihood: medium
      severity: high
      mitigation: "forbidden include/type validators and provider boundary docs"
      related_workstreams: [WORKSTREAM-04]
      label: FACT

  verification_queue:
    - id: VERIFY-01
      item: "latest live repo state"
      why_verification_needed: "user-reported commits may not reflect current branch"
      suggested_source_type: "git status, latest audits, validator run"
      priority: P0
      related_workstreams: [WORKSTREAM-01, WORKSTREAM-07]
      label: FACT

  spec_book_notes:
    likely_sections:
      - "Repository structure"
      - "Domino Framework boundary"
      - "Service/provider architecture"
      - "Workbench/presentation architecture"
      - "Testing and proof gates"
    unique_contributions:
      - "Detailed root-policy refinement"
      - "Raylib/SDL/Lua provider doctrine"
      - "No-framework-root decision"
    possible_duplicates_with_other_chats:
      - "Workbench brainstorming"
      - "Language baseline discussions"
      - "Raylib provider discussions"
    conflicts_to_watch_for:
      - "Exact external path convention"
      - "Lua version"
      - "Diagnostic root singular/plural"
    formal_requirements_candidates:
      - "No top-level framework/modules/profiles/labs roots"
      - "runtime/<service>/providers/<provider> provider structure"
      - "C-compatible public ABI"
    background_context_candidates:
      - "Historical frustration and repeated refactor churn"
    needs_user_confirmation:
      - "Final Lua version"
      - "Provider implementation sequencing"

  final_recommendations:
    next_action_if_continuing_this_chat: "Verify latest repo gate status, then repair fast-strict/evidence debt or proceed to projection conformance."
    next_action_for_aggregator: "Merge this as the canonical repository/framework/provider architecture thread."
    user_checks_required:
      - "Confirm latest commit and full CTest state."
      - "Confirm provider convention names if repo changed after this chat."


# Aggregator Packet — Dominium Canonical Structure and Domino Framework Architecture

## Packet Metadata

* Chat label: Dominium Canonical Structure and Domino Framework Architecture
* Date anchor: 2026-05-27 Australia/Melbourne
* Source scope: This chat only unless labelled PROJECT-CONTEXT
* Coverage: Partial but substantial
* Confidence: 4/5 for accessible substance; lower for exact latest repo state
* Staleness risk: Medium to High for live repo status and third-party versions
* Merge priority: High
* Main limitations: Full transcript not separately exported; some uploads expired; several structure bundles were stale/mixed.

## Ultra-Condensed Carry-Forward Capsule

This chat is the main architecture/convergence thread for Dominium’s repository structure and Domino framework model. The user wanted to stop months of structure churn and finally make the repo suitable for real development. The conversation converged on a closed top-level root model: apps, engine, game, runtime, contracts, content, docs, tests, tools, scripts, cmake, external, release, archive, plus limited project/tooling roots. New top-level framework/modules/plugins/services/profiles/labs/sdk/src/source roots were rejected.

The central doctrine is: path is not identity; implementation is not contract; UI is not authority; generated output is not source truth. Domino is the reusable deterministic/runtime framework; Dominium is the game/product family; Workbench is the production/evidence/editor environment; AIDE is the control-plane harness. Domino Framework should not become a `framework/` root. It is represented by contracts, public surfaces, ABI law, service/provider law, public headers, and conformance tests.

The chat defined precise vocabulary: component = source/build unit; service = callable runtime capability; provider = replaceable implementation; pack = authored distributable payload; module = declared extension unit; workspace = Workbench composition; app = product composition; artifact = persisted versioned object. Workbench modules are not the general module system.

Presentation architecture became a major result. CLI, text/TUI, rendered GUI, native GUI, headless reports, Workbench panels, AIDE, and CI should all project the same semantic spine: intent → command → capability/refusal check → service → result/document/snapshot → diagnostics/evidence → view/action model → projection → shell.

The chat also set the raylib/SDL/Lua doctrine. Raylib, rlgl, rlsw, raygui, raudio, SDL2, Lua, and possibly ImGui are providers. Their code belongs under external and runtime provider paths. Third-party types must not leak into engine, game, contracts, content, saves, replays, packs, or public ABI. Provider choices live in profiles, not app path names.

Multiple cleanup tasks/prompts were generated and user-reported commits landed: actual canonical structure cleanup, full-gate legacy path routing, provider structure enforcement, and Domino framework boundary definition. The current state is credible but not full release green. Structure is mostly fixed; fast strict/smoke generally pass or pass with warnings; full CTest/T4 remains debt; broad feature work remains blocked; narrow governed work can continue after gate-specific blockers are repaired.

## Top Carry-Forward Items

| Priority | Item | Type | Related ID | Why it matters | Label | Confidence |
|---|---|---|---|---|---|---|
| P0 | Closed top-level root set | Requirement | DECISION-01 | Prevents root sprawl | FACT | High |
| P0 | No top-level framework/ | Requirement | DECISION-04 | Preserves contract/public-header model | FACT | High |
| P0 | Service-first provider structure | Requirement | DECISION-06 | Enables raylib/SDL/Lua without lock-in | FACT | High |
| P0 | C-compatible ABI | Requirement | DECISION-05 | Enables portability/replacement | FACT | Medium-High |
| P1 | Projection spine | Requirement | DECISION-08 | Prevents four UI systems | FACT | High |
| P1 | Full CTest/T4 debt remains | Open issue | QUESTION-01 | Blocks release/full proof | FACT | High |

## Workstream Summaries

* ID: WORKSTREAM-01
* Name: Canonical Repository Structure
* Objective: Keep source roots closed and active paths canonical.
* Current state: Mostly clean with warnings.
* Desired end state: No stale active paths; validators enforce structure.
* Priority: P0
* Decisions: DECISION-01, DECISION-02
* Tasks: targeted residuals only.
* Constraints: no new roots, no src/source.
* Artifacts: structure cleanup audits, dirfiles exports.
* Risks: restarting broad churn.
* Open questions: latest live status.
* Next action: verify latest tree if needed.

* ID: WORKSTREAM-04
* Name: Service-first Provider Architecture
* Objective: Use raylib/SDL/Lua as replaceable providers.
* Current state: Provider law/structure reported in place; implementation pending.
* Desired end state: runtime/<service>/providers/<provider> with profiles and conformance.
* Priority: P0
* Decisions: DECISION-06
* Tasks: Provider wedge after proof hygiene.
* Constraints: no third-party leakage.
* Risks: vendor-shaped architecture.
* Open questions: Lua version, external path convention.

## Compact Registers for Merge

Use sections 17–28 of the full register file as authoritative compact registers.

## Possible Cross-Chat Duplicates

Workbench brainstorming, language baseline, raylib/SDL/Lua provider discussions, AIDE workflow law, and worldgen/module composition may overlap with other old chats.

## Possible Cross-Chat Conflicts

Exact naming of `external/upstream` versus `external/vendor`, Lua version, diagnostic/diagnostics root, and the timing of provider wedge versus presentation contract may conflict with later chats.

## Spec Book Integration Guidance

This chat should feed into chapters on repo structure, framework boundary, provider architecture, public surfaces, ABI, Workbench/presentation, modules/packs/apps, testing/proof gates, and AIDE governance. Treat most architecture doctrine as candidate requirements; treat exact current repo status as verification-dependent.

## Aggregator Warnings

Do not merge assistant brainstorming as final user decisions unless user accepted it. Do not overclaim full green. Do not add new roots. Verify live repo state before executing tasks.


# Verification and Audit — Dominium Canonical Structure and Domino Framework Architecture

## Adversarial Self-Audit

| Issue | Severity | Correction needed | Correction applied? | Residual risk |
|---|---|---|---|---|
| Full transcript not accessible as separate export. | Medium | Mark coverage partial. | Yes | Some turn-level detail may be omitted. |
| Some uploaded files expired. | Medium | Note file-access limitation. | Yes | Missing historical artifacts. |
| User-reported repo commits may be stale. | High | Add verification queue. | Yes | Must check live repo before action. |
| Assistant suggestions may be mistaken for decisions. | High | Label accepted vs suggested. | Yes | Some implicit acceptance still inferred. |
| External library facts may be stale. | Medium | Mark for verification. | Yes | Need web/current docs before release policy. |
| Report may over-compress details. | Medium | Include files plus in-chat reader. | Partial | Full exhaustive transcript still absent. |

## Corrections Applied

- Coverage was labelled partial rather than full.
- Tentative decisions were separated from accepted decisions where possible.
- External facts and live repo state were placed in the verification queue.
- Rejected options were preserved.
- The report warns against treating PASS_WITH_WARNINGS as full green.

## Final Reliability Assessment

* Completeness rating: 4/5 for accessible substance.
* Reliability rating: 4/5 for architectural decisions; 3/5 for exact latest repo state.
* Human-readability rating: 4/5.
* Aggregation-readiness rating: 4/5 with caveats.
* Main remaining uncertainty sources: live repo state, full CTest status, exact provider version choices, expired uploads, and whether later chats superseded some details.
* Manual review before merge: recommended.

## Verification Queue

See register section 26.


# In-Chat Reader — Dominium Canonical Structure and Domino Framework Architecture

## Package overview

This preservation package captures the substance of the Dominium canonical repository structure and Domino framework architecture chat. It is intended for human reading, future chat continuation, and later aggregation into a project spec book.

## File index

Read first: `01_human_readable_report.md`.
Use for continuing in another chat: `02_context_transfer_packet.md`.
Use for aggregation: `03_spec_sheet.yaml` and `05_aggregator_packet.md`.
Use for precise tables: `04_registers.md`.
Use for caveats: `07_verification_and_audit.md`.

## Top things to preserve

- Closed root model.
- No `framework/` root.
- Service-first provider model.
- Workbench is not authority.
- Third-party libraries are providers.
- C17/C++17 with C-compatible ABI.
- Full CTest remains debt.

## Safest next actions

1. Verify latest live repo status.
2. Repair fast-strict evidence/marker debt if present.
3. Run projection conformance and presentation contract work.
4. Do provider wedge work only behind contracts and validators.
