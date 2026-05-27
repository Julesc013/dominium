Status: DERIVED
Last Reviewed: 2026-05-28
Supersedes: none
Superseded By: none
Stability: provisional
Result: reader_page_generated
Binding Sources: `docs/canon/constitution_v1.md`, `docs/canon/glossary_v1.md`, `AGENTS.md`, `docs/planning/AUTHORITY_ORDER.md`, `docs/planning/SNAPSHOT_INTAKE_PROTOCOL.md`
Authority Class: advisory_only
Source Class: conversation_handoff_export
Source Folder: `docs/archive/conversations/Modularity_AIDE_Refactorability/`
Promotion Status: not_reviewed

# Dominium Modularity, AIDE Refactorability, and Future-Proof Architecture - Conversation Reader

This reader page is derived from archived conversation material. It cannot override canon, contracts, schema law, current queue state, live repo structure, or validated repo artifacts.

## What This Conversation Was About

This chat was about making Dominium structurally durable: portable, modular, extensible, reusable across future games, and refactorable without the user having to repeat a painful top-level cleanup. The discussion began from an already-developed architectural thread about Dominium's source layout, distribution layout, package layout, install roots, runtime roots, bundle formats, and component matrices. The user brought in several previous assistant outputs that had converged on a broad direction: Dominium should not be treated like a one-off indie project, but like a long-lived platform with a stable architecture, stable contracts, deterministic build/release/install semantics, and a repo structure that can survive multiple products, renderers, platforms, shells, and content systems.

The key early idea was that Dominium needs more than a source repo directory layout. It needs a unified logical-root model that can be projected into CI output, `.dompkg` packages, portable installs, installed desktop/server layouts, read-only media, caches, staging roots, rollback state, symbols, provenance, save bundles, instance bundles, replay bundles, and diagnostics bundles. This led to the principle that `.zip` archives, installers, portable folders, package files, media images, save bundles, and runtime installs should not invent separate semantics. They should all bind to the same logical roots, with physical paths depending on mode and mutability.

The next topic was the source repo itself. The user and assistant treated the existing root clutter as a serious architectural problem, not cosmetic untidiness. The target root set was repeatedly narrowed toward stable ownership categories: `apps/`, `engine/`, `game/`, `runtime/`, `contracts/`, `content/`, `docs/`, `tests/`, `tools/`, `scripts/`, `cmake/`, `external/`, `release/`, `archive/`, and generated `dist/` under strict policy. The important conclusion was that future top-level roots should be refused by default. New work should fit into existing ownership surfaces unless it truly has a separate lifecycle and long-term purpose.

## Why It Mattered

This conversation matters as historical context for the topics tagged here: architecture, content, contracts_schema, determinism, governance, platform, release, simulation, timekeeping, tooling, ui, worldgen, xstack_aide. Its value is explanatory and evidentiary, not authoritative. Any claim must be checked against current repo artifacts before promotion.

## What Was Discussed

The package appears to be a `conversation_handoff_package` with `16` source files. The primary extracted source is `docs/archive/conversations/Modularity_AIDE_Refactorability/Dominium_Modularity_AIDE_Refactorability_Architecture__01_human_readable_report.md`.

## What Was Decided

- The final user action was uploading a preservation-package prompt. That prompt requested a maximum-fidelity preservation report, structured registers, context transfer packet, spec sheet, aggregator packet, self-audit, downloadable files, and a final in-chat reader. This package is the result.
- The user objected to the XStack/AuditX/RepoX/TestX framing and wanted AIDE adopted quickly. The resulting plan made AIDE the repo-native control plane for inventory, task queues, policies, move maps, salvage maps, evidence ledgers, validation, and refactor history. Existing tools should be recycled, not discarded. This is central to future refactorability.
- The discussion proposed target-based CMake and module boundaries rather than path mythology. Public headers, private headers, allowed dependencies, and forbidden dependencies should be explicit. Apps must remain thin. Engine must not depend on game/apps/runtime UI. Runtime adapts host/platform/rendering without owning simulation truth.
- The uploaded prompt converted the conversation into a preservation task. It requires a human-readable report first, then registers, spec sheet, aggregator packet, self-audit, and downloadable files. This final package is intended to be merged later with old-chat reports into a master Project Spec Book.
- The conversation implies a goal of turning Dominium into a long-lived product-line platform rather than a single-game repository. It also implies a desire for auditability: decisions should be grounded, visible, mechanically enforceable, and later aggregatable into a master spec. The user appears to value stable boundaries, explicit compatibility policy, and practical Codex/AIDE tasks.
- The initial focus was directory and distribution structure. It then widened to component naming, repository convergence, AIDE governance, refactorability, and finally broad software engineering doctrine for reusable engine/platform development. The most important change was the rejection of the XStack-style framing and the shift toward AIDE as the near-term control plane.
- The live repo still needs verification. The exact AIDE files, contracts, validators, and migration tasks must be implemented. It remains unresolved which existing roots and tools map to which final homes, which APIs become stable, which code is reusable across products/games/projects, and which prior assistant recommendations should become formal requirements after user review.
- Status: recommendation. Basis: Final response emphasized stabilizing correct public seams only. Rationale: Avoids maintenance paralysis. Implications: Need stability levels and deprecation policy. Related workstream: WORKSTREAM-06. Confidence: medium. Label: INFERENCE. This should be revisited if live repo evidence contradicts the assumed structure, or if the user later chooses a different product-line strategy.
- Status: rejected. It was rejected/superseded because Would break paths, build, tests, package identity, and authority semantics. Finality: final unless repo becomes trivial. Reconsider conditions: Only reconsider for tiny isolated folders with move map and proof.. Related workstream: WORKSTREAM-01. Label: FACT/INFERENCE.
- Status: rejected/superseded. It was rejected/superseded because User disliked it; names are temporary scaffolding. Finality: mostly final. Reconsider conditions: May remain in history/ledgers during transition.. Related workstream: WORKSTREAM-03. Label: FACT.
- Status: rejected. It was rejected/superseded because User explicitly wants recycling. Finality: final. Reconsider conditions: Only drop after classification and evidence.. Related workstream: WORKSTREAM-04. Label: FACT.
- Status: superseded. It was rejected/superseded because Unrealistic; better target is stable top-level roots plus cheap internal refactors. Finality: final as framing. Reconsider conditions: N/A.. Related workstream: WORKSTREAM-01. Label: INFERENCE.

## What Was Not Decided

- The live repo still needs verification. The exact AIDE files, contracts, validators, and migration tasks must be implemented. It remains unresolved which existing roots and tools map to which final homes, which APIs become stable, which code is reusable across products/games/projects, and which prior assistant recommendations should become formal requirements after user review.
- 1. **TASK-09** - Verify live repo baseline: current branch, root inventory, validators, CTest status, generated artifacts.
- The user prefers source-grounded, audit-ready decisions; bounded uncertainty; explicit task prompts; and reusable engineering doctrine. Future assistants should avoid shallow affirmation and should distinguish accepted user decisions from assistant recommendations.
- Important caveat: the only current uploaded file available for this task is `Pasted text.txt`, which contains the preservation-package prompt. Earlier generated handoff files, ZIP packages, or uploaded docs referenced in prior conversation are not available in this chat unless the user re-uploads them.
- The most serious risk is that a future assistant treats this chat as if it verified the live repo. It did not. The second serious risk is that it hardens every assistant suggestion into a requirement. Several items are strong recommendations aligned with user goals, but still require implementation review. Future chats must preserve labels and verify stale facts.
- Future assistants must verify live repo state before implementing cleanup.

## Ideas Rejected, Superseded, Or Deprioritised

- The chat rejected names based on era, temporary project status, support status, or implementation-version encoding. Components should have boring literal names such as `opengl`, `direct3d`, `vulkan`, `software`, `win32`, `posix`, `cocoa`, `portable`, `installed`, with version/status/format fields carried separately. This reduces long-term naming debt.
- The discussion proposed target-based CMake and module boundaries rather than path mythology. Public headers, private headers, allowed dependencies, and forbidden dependencies should be explicit. Apps must remain thin. Engine must not depend on game/apps/runtime UI. Runtime adapts host/platform/rendering without owning simulation truth.
- Status: rejected. It was rejected/superseded because Would break paths, build, tests, package identity, and authority semantics. Finality: final unless repo becomes trivial. Reconsider conditions: Only reconsider for tiny isolated folders with move map and proof.. Related workstream: WORKSTREAM-01. Label: FACT/INFERENCE.
- Status: rejected/superseded. It was rejected/superseded because User disliked it; names are temporary scaffolding. Finality: mostly final. Reconsider conditions: May remain in history/ledgers during transition.. Related workstream: WORKSTREAM-03. Label: FACT.
- Status: rejected. It was rejected/superseded because User explicitly wants recycling. Finality: final. Reconsider conditions: Only drop after classification and evidence.. Related workstream: WORKSTREAM-04. Label: FACT.
- Status: superseded. It was rejected/superseded because Unrealistic; better target is stable top-level roots plus cheap internal refactors. Finality: final as framing. Reconsider conditions: N/A.. Related workstream: WORKSTREAM-01. Label: INFERENCE.
- Status: rejected. It was rejected/superseded because Makes moves/refactors break artifacts. Finality: final as doctrine. Reconsider conditions: N/A.. Related workstream: WORKSTREAM-05. Label: INFERENCE.
- Status: deprioritized. It was rejected/superseded because Too costly; stabilize public seams and let internals evolve. Finality: tentative but strong. Reconsider conditions: Revisit per API if external dependents emerge.. Related workstream: WORKSTREAM-06. Label: INFERENCE.
- Status: rejected direction. It was rejected/superseded because Creates naming debt and mixes axes. Finality: strong. Reconsider conditions: Use only as status/version fields where needed.. Related workstream: WORKSTREAM-07. Label: FACT/INFERENCE.

## What Future Work Came From It

- The final user action was uploading a preservation-package prompt. That prompt requested a maximum-fidelity preservation report, structured registers, context transfer packet, spec sheet, aggregator packet, self-audit, downloadable files, and a final in-chat reader. This package is the result.
- The user objected to the XStack/AuditX/RepoX/TestX framing and wanted AIDE adopted quickly. The resulting plan made AIDE the repo-native control plane for inventory, task queues, policies, move maps, salvage maps, evidence ledgers, validation, and refactor history. Existing tools should be recycled, not discarded. This is central to future refactorability.
- The uploaded prompt converted the conversation into a preservation task. It requires a human-readable report first, then registers, spec sheet, aggregator packet, self-audit, and downloadable files. This final package is intended to be merged later with old-chat reports into a master Project Spec Book.
- The conversation implies a goal of turning Dominium into a long-lived product-line platform rather than a single-game repository. It also implies a desire for auditability: decisions should be grounded, visible, mechanically enforceable, and later aggregatable into a master spec. The user appears to value stable boundaries, explicit compatibility policy, and practical Codex/AIDE tasks.
- The live repo still needs verification. The exact AIDE files, contracts, validators, and migration tasks must be implemented. It remains unresolved which existing roots and tools map to which final homes, which APIs become stable, which code is reusable across products/games/projects, and which prior assistant recommendations should become formal requirements after user review.
- 1. **TASK-09** - Verify live repo baseline: current branch, root inventory, validators, CTest status, generated artifacts.
- 2. **TASK-01** - Implement AIDE-STRUCTURE-00: root constitution, ownership slots, AIDE refactor framework, move/salvage map schemas, inventory tooling.
- 3. **TASK-03** - Inventory old XStack/AuditX/RepoX/TestX-style tools and classify them.
- 4. **TASK-04** - Wrap old checks behind AIDE without changing behavior.
- 5. **TASK-02** - Implement AIDE-ARCH-00: modularity/reuse doctrine, dependency layers, C89 ABI rules, API stability levels, boundary checker.
- 6. **TASK-05** - Define distribution/install/media/bundle projection contracts.
- 7. **TASK-06/TASK-07/TASK-08** - Add boundary validators, component manifests, and portability/determinism proof checks.

## Important Artifacts

- `handoff`: `1`
- `json`: `1`
- `manifest`: `2`
- `markdown`: `2`
- `primary_report`: `1`
- `prompt`: `2`
- `py`: `1`
- `reader_brief`: `2`
- `registers`: `1`
- `spec_sheet`: `1`
- `verification`: `1`
- `zip`: `1`

## Verification Needed

- Verify every implementation, platform, tooling, release, and queue claim against current repo artifacts.
- Treat external platform or SDK claims as stale until independently checked.
- Treat old language-baseline claims as historical unless they match current `README.md` and current contracts.
- Do not infer current authority from the existence of this archive package.

## Candidate Promotions

Candidate promotions, if any, are recorded in `_promotion/PROMOTION_QUEUE.md`. This page does not promote claims.

## Do Not Assume

- Do not assume this conversation established current repo truth.
- Do not assume generated package reports are canonical.
- Do not assume old prompts were executed.
- Do not assume unresolved items are safe to implement.
- Do not use this package to open blocked work without stronger current authority.
