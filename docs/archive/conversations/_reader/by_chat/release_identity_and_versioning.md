Status: DERIVED
Last Reviewed: 2026-05-28
Supersedes: none
Superseded By: none
Stability: provisional
Result: reader_page_generated
Binding Sources: `docs/canon/constitution_v1.md`, `docs/canon/glossary_v1.md`, `AGENTS.md`, `docs/planning/AUTHORITY_ORDER.md`, `docs/planning/SNAPSHOT_INTAKE_PROTOCOL.md`
Authority Class: advisory_only
Source Class: conversation_handoff_export
Source Folder: `docs/archive/conversations/Release_Identity_and_Versioning/`
Promotion Status: not_reviewed

# Dominium XStack Release Identity and Versioning - Conversation Reader

This reader page is derived from archived conversation material. It cannot override canon, contracts, schema law, current queue state, live repo structure, or validated repo artifacts.

## What This Conversation Was About

This chat was about designing a durable release identity, versioning, compatibility, build, and packaging system for Dominium/XStack. The user began from dissatisfaction with products that change versioning policies midstream, citing examples such as Windows NT, Minecraft, macOS, .NET, Linux, and TeX. The underlying concern was not aesthetic only. The user wanted a versioning system that could survive long-term without arbitrary "vibe" bumps, without getting trapped in permanent `1.x`, and without overloading one number with too many incompatible meanings.

The discussion first compared Semantic Versioning with other versioning strategies, then moved into a project-specific model. Early suggestions included alternatives such as generation/epoch/feature/patch, but the conversation gradually converged on a stronger principle: one version number should not carry all truth. A large platform needs separate identities for public release naming, component compatibility, suite composition, build provenance, lifecycle/support channel, target platform, package type, and internal compatibility. This became the main conceptual outcome of the chat.

The user then clarified that Dominium/XStack has standalone products such as Stack, Tools, SDK, Engine, Game, Client, Server, Launcher, and Setup, plus suites or distributions such as All, Full, Lite, and Net. This led to a product-vs-suite distinction: products/components can have their own versions, while suites are curated bundles with human-facing release identities. The chat also established that setup should remain a standalone product capable of running portably and then managing installation, repair, uninstall, rollback, upgrade, and migration using bundled or network sources.

## Why It Mattered

This conversation matters as historical context for the topics tagged here: architecture, content, contracts_schema, determinism, governance, platform, release, setup_launcher, simulation, timekeeping, tooling, ui, worldgen, xstack_aide. Its value is explanatory and evidentiary, not authoritative. Any claim must be checked against current repo artifacts before promotion.

## What Was Discussed

The package appears to be a `conversation_handoff_package` with `14` source files. The primary extracted source is `docs/archive/conversations/Release_Identity_and_Versioning/Dominium_XStack_Release_Identity_and_Versioning__01_human_readable_report.md`.

## What Was Decided

- The user then objected to versioning policy drift in real products and expressed concern about SemVer's "1.x forever" failure mode. The first proposed answer was a four-part public version scheme, `GEN.EPOCH.FEATURE.PATCH`, meant to avoid fake major bumps. That idea was useful as an intermediate step but later became less central because XStack already has GBN for dense build history and separate build identity.
- The conversation then moved into how this might fit XStack. The model shifted from "better public version number" to "layered identity model." The assistant recommended preserving per-product versions, a global build number, build IDs, compatibility versions, and suite versions as separate layers. This became the foundation for later decisions.
- The user suggested that suites might use a separate consumer-facing or marketing version, while each component could use stricter SemVer. The chat accepted this as a mature pattern: suites are curated bundles, while components may have technical versions. The model was refined to avoid synchronized fake versioning and to avoid treating a suite major version as universal breakage.
- The user then asked if the suite version should still encode enough meaning to infer internal and external compatibility. The conversation clarified that the suite version can communicate a compatibility envelope or release family, but exact compatibility must live in explicit metadata. This led to the idea of compatibility profiles and later capabilities.
- The chat was then summarized into a knowledge base. After that, the user proposed an even deeper internal rule: use capabilities instead of versions for compatibility. The response accepted this as a stronger model: versions identify releases; capabilities decide interoperability; GBN/BII/hash identify exact artifacts. That is the current final design direction.
- The main design conclusion was that release identity should be layered: product/suite version, component version, build identity, compatibility/capability contracts, lifecycle channel, target/platform, package kind, and manifest metadata should remain separate. This is the central principle to carry forward.
- The chat rebuilt SemVer from first principles and decided that strict SemVer should apply only to components with declared public contracts. Candidate true-SemVer entities include SDKs, engine libraries, tool APIs/CLIs, protocol libraries, plugin hosts, schema libraries, and reusable runtime libraries. It remains unresolved which exact repo modules qualify.
- The user liked the visual shape of SemVer even for consumer-facing items. The chat accepted `X.Y.Z[-pre][+build]` as a useful shape, but required that non-SemVer products/suites be documented as release identifiers rather than API-compatibility promises.
- GBN should identify CI/public/internal builds and appear as provenance, e.g. `+gbn.7137`, but it must not be used as SemVer precedence. BII should primarily be structured manifest metadata, because it may encode lane, target, kind, configuration, and other build identity fields. The exact BII schema remains unresolved.
- The final conceptual refinement was that internal compatibility should use capabilities/contracts rather than version ranges alone. A version says what release something is; a capability says what it can do. This is especially useful for saves, packs, plugins, network handshakes, installers, renderers, and platform/runtime constraints.
- The conversation began as a comparison of versioning schemes. It evolved into a release identity architecture. It then became a SemVer adaptation exercise. Finally, it became a capability-based compatibility architecture layered under versioning.
- The major blockers are repo verification and formal user decisions on suite semantics, BII schema, target taxonomy, and capability registry design.

## What Was Not Decided

- The chat rebuilt SemVer from first principles and decided that strict SemVer should apply only to components with declared public contracts. Candidate true-SemVer entities include SDKs, engine libraries, tool APIs/CLIs, protocol libraries, plugin hosts, schema libraries, and reusable runtime libraries. It remains unresolved which exact repo modules qualify.
- GBN should identify CI/public/internal builds and appear as provenance, e.g. `+gbn.7137`, but it must not be used as SemVer precedence. BII should primarily be structured manifest metadata, because it may encode lane, target, kind, configuration, and other build identity fields. The exact BII schema remains unresolved.
- The main unresolved goals are to produce formal specs: Release Constitution, SemVer Component Inventory, Suite Release Policy, Build Identity Spec, Channel/Lifecycle Spec, Artifact Naming Spec, Manifest Schema, Target Taxonomy, and Capability Registry.
- It is still uncertain how strict the user wants suite `X.Y.Z` field meanings to be, whether capabilities should fully replace compatibility profiles or coexist with them, and how much old-platform support should be real versus aspirational.
- The most important unresolved issue is formal classification. Without knowing which entities are strict SemVer components, suite versions, product release IDs, build fields, or capabilities, the rest of the policy cannot be enforced safely.
- Platform targeting remains unresolved. The chat concluded that coarse families like WinNT5, WinNT10, MacOSX4, Linux5, or DOS5 are useful support labels, but exact binary compatibility needs target baselines and runtime/toolchain profiles. Linux kernel major alone is not enough. Windows 9x/NT/NT5/NT6/NT10 likely need separate build lanes or at least explicit tested baselines.

## Ideas Rejected, Superseded, Or Deprioritised

- The early four-part version proposal was superseded by a layered identity architecture.
- GBN should identify CI/public/internal builds and appear as provenance, e.g. `+gbn.7137`, but it must not be used as SemVer precedence. BII should primarily be structured manifest metadata, because it may encode lane, target, kind, configuration, and other build identity fields. The exact BII schema remains unresolved.
- These rejected or superseded options matter because future assistants may otherwise reintroduce them. The biggest trap is suggesting "just use SemVer everywhere." That was explicitly narrowed. Another trap is treating `stable` or `hotfix` as prerelease suffixes even after SemVer ordering was explained.

## What Future Work Came From It

- The chat rebuilt SemVer from first principles and decided that strict SemVer should apply only to components with declared public contracts. Candidate true-SemVer entities include SDKs, engine libraries, tool APIs/CLIs, protocol libraries, plugin hosts, schema libraries, and reusable runtime libraries. It remains unresolved which exact repo modules qualify.
- The user explicitly wanted a versioning/release identity policy that would not need to change halfway through. They wanted to avoid SemVer stagnation, arbitrary major bumps, and product-history confusion. Later, the user wanted the conversation reconstructed into a knowledge base and preservation package for future aggregation.
- These rejected or superseded options matter because future assistants may otherwise reintroduce them. The biggest trap is suggesting "just use SemVer everywhere." That was explicitly narrowed. Another trap is treating `stable` or `hotfix` as prerelease suffixes even after SemVer ordering was explained.
- The immediate future work is to convert this design into formal repo/spec artifacts. Recommended order:
- The user values long-term maintainability over short-term prettiness. They prefer explicit metadata over hidden inference. They want future assistants to preserve tentative status and not silently turn brainstorms into decisions.
- This preservation task creates the first actual downloadable package in this chat. Prior artifacts were primarily in-chat examples, summaries, and proposed spec fragments.
- The highest-risk misunderstanding is collapsing the layered model back into one universal version scheme. Future assistants should classify the entity first, then apply the correct policy.

## Important Artifacts

- `handoff`: `1`
- `manifest`: `2`
- `markdown`: `2`
- `primary_report`: `1`
- `prompt`: `2`
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
