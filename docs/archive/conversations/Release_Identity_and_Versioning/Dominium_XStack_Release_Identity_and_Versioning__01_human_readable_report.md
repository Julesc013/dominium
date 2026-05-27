# COMPLETE CHAT PRESERVATION REPORT — Dominium XStack Release Identity and Versioning

## 0. Coverage and Reliability Assessment

| Field | Assessment |
| --- | --- |
| Chat label | Dominium XStack Release Identity and Versioning |
| Date anchor | 2026-05-27 Australia/Melbourne |
| Source scope | This chat only unless explicitly labelled PROJECT-CONTEXT. |
| Apparent access | Partial: current visible transcript/context and uploaded prompt are available; raw hidden/full transcript outside context is not independently accessible. |
| Previously generated files available? | No prior downloadable files visible in this task; this response creates new files. |
| Uploaded files or artifacts present? | Yes: Pasted text.txt, the preservation mega-prompt. |
| Contains future plans? | Yes. |
| Contains decisions? | Yes, with some tentative directions that need confirmation. |
| Contains pending tasks? | Yes. |
| Contains unresolved questions? | Yes. |
| Staleness risk | Low for design decisions; medium for SemVer primary-source wording and OS/toolchain feasibility. |
| Extraction confidence | 4/5 for visible chat substance; lower for actual repo/build-system state. |
| Safe for later aggregation? | With caveats. |
| Main limitations | No direct repo inspection in this task; no full raw transcript beyond the conversation context; some earlier assistant claims about existing XStack files remain unverified. |

The uploaded instruction file defines this as a maximum-fidelity preservation, explanation, handoff, audit, spec-prep, and export task for the current chat. The extraction below is grounded in the visible conversation context and the uploaded prompt. The report is intentionally conservative: assistant proposals are not treated as final user decisions unless the user clearly accepted, echoed, or built on them. Any claim about actual repository files, build scripts, toolchains, or OS support is marked as uncertain where the chat discussed it but this task did not independently verify it.

## 1. One-Page Orientation

This chat was about designing a durable release identity, versioning, compatibility, build, and packaging system for Dominium/XStack. The user began from dissatisfaction with products that change versioning policies midstream, citing examples such as Windows NT, Minecraft, macOS, .NET, Linux, and TeX. The underlying concern was not aesthetic only. The user wanted a versioning system that could survive long-term without arbitrary “vibe” bumps, without getting trapped in permanent `1.x`, and without overloading one number with too many incompatible meanings.

The discussion first compared Semantic Versioning with other versioning strategies, then moved into a project-specific model. Early suggestions included alternatives such as generation/epoch/feature/patch, but the conversation gradually converged on a stronger principle: one version number should not carry all truth. A large platform needs separate identities for public release naming, component compatibility, suite composition, build provenance, lifecycle/support channel, target platform, package type, and internal compatibility. This became the main conceptual outcome of the chat.

The user then clarified that Dominium/XStack has standalone products such as Stack, Tools, SDK, Engine, Game, Client, Server, Launcher, and Setup, plus suites or distributions such as All, Full, Lite, and Net. This led to a product-vs-suite distinction: products/components can have their own versions, while suites are curated bundles with human-facing release identities. The chat also established that setup should remain a standalone product capable of running portably and then managing installation, repair, uninstall, rollback, upgrade, and migration using bundled or network sources.

A central decision was to use strict SemVer 2.0.0 only where it genuinely applies: components with declared public APIs or compatibility contracts. Examples include SDKs, engine libraries, protocol/schema/plugin surfaces, reusable runtime libraries, and stable CLI/API tools. For user-facing products and suites, the user liked the shape of SemVer — `1.2.3`, `1.2.3-beta.1`, `1.2.3+gbn.7137` — but agreed that these should be explicitly labelled as release identifiers unless they truly satisfy strict SemVer semantics.

The chat also integrated XStack’s build concepts. Global Build Number (GBN) should be used for exact CI artifact identity and provenance, normally in build metadata such as `+gbn.7137`, but not as SemVer precedence. Build Identification / BII should primarily live in structured manifests, with optional compact projection into filenames or metadata. The conversation also split channel semantics: `dev`, `alpha`, `beta`, and `rc` can be prerelease ordering labels; `stable`, `lts`, `nightly`, `internal`, and `hotfix` are better treated as lifecycle or release-class metadata.

The final important shift was the user’s proposal that internal compatibility should use capabilities instead of relying only on versions. This was accepted as a strong tentative direction: versions identify releases, while capabilities/contracts decide interoperability. Examples include `save.schema@5`, `plugin.host@2`, `net.protocol@3`, and renderer/install/pack capabilities. This refines the earlier “compatibility axes” idea into an operational model.

The chat’s future value is high because it can become the basis for a Release Constitution, SemVer Component Inventory, Suite Release Policy, Build Identity Spec, Artifact Naming Spec, Target Taxonomy, Release Manifest Schema, and Capability Compatibility Spec. The main unresolved work is to formalize these into repo-ready documents and verify them against actual XStack/RepoX build files and real platform/toolchain constraints.

## 2. The Story of the Conversation

The conversation began with a broad comparison of Semantic Versioning against other versioning methods. The initial answer positioned SemVer as compatibility-focused, while CalVer, serial build numbers, marketing versions, build numbers, git hashes, protocol/schema versions, and release channels each solve different problems. This established the idea that version numbers are information encodings, not merely labels.

The user then objected to versioning policy drift in real products and expressed concern about SemVer’s “1.x forever” failure mode. The first proposed answer was a four-part public version scheme, `GEN.EPOCH.FEATURE.PATCH`, meant to avoid fake major bumps. That idea was useful as an intermediate step but later became less central because XStack already has GBN for dense build history and separate build identity.

The conversation then moved into how this might fit XStack. The model shifted from “better public version number” to “layered identity model.” The assistant recommended preserving per-product versions, a global build number, build IDs, compatibility versions, and suite versions as separate layers. This became the foundation for later decisions.

The user suggested that suites might use a separate consumer-facing or marketing version, while each component could use stricter SemVer. The chat accepted this as a mature pattern: suites are curated bundles, while components may have technical versions. The model was refined to avoid synchronized fake versioning and to avoid treating a suite major version as universal breakage.

The user then asked if the suite version should still encode enough meaning to infer internal and external compatibility. The conversation clarified that the suite version can communicate a compatibility envelope or release family, but exact compatibility must live in explicit metadata. This led to the idea of compatibility profiles and later capabilities.

A broader packaging discussion followed. The user listed standalone products and suites and proposed filename patterns including version, channel, build, platform, and architecture. The chat improved this by separating `scope` (`product` or `suite`), `id`, `version`, `target`, `arch`, and `pkg` kind. It also clarified that platform family and binary baseline are not the same thing: `WinNT5`, `Linux5`, or `MacOSX4` may be useful support-family labels, but exact compatibility requires a tested baseline/runtime/toolchain profile.

The user then reset the discussion from scratch around SemVer 2.0.0. The chat reconstructed SemVer’s core rules: public API requirement, major/minor/patch meanings, prerelease labels, build metadata, precedence, and common mistakes. The key consequences for XStack were that `stable` should not be encoded as `-stable`, `hotfix` should not normally be encoded as `-hotfix`, and GBN inside `+...` cannot determine SemVer precedence.

The user liked this distinction: strict SemVer for public APIs, explicitly non-SemVer but SemVer-shaped identifiers for end-user facing things. The chat then classified true SemVer components, product release identifiers, suite identifiers, GBN, BII, channels, and filenames. It concluded that file names are projections of metadata, while manifests are canonical.

The chat was then summarized into a knowledge base. After that, the user proposed an even deeper internal rule: use capabilities instead of versions for compatibility. The response accepted this as a stronger model: versions identify releases; capabilities decide interoperability; GBN/BII/hash identify exact artifacts. That is the current final design direction.

## 3. Main Topics Discussed

### Topic 1 — SemVer versus other versioning strategies

The chat compared SemVer, CalVer, serial numbering, marketing versions, build numbers, git hashes, protocol/schema versions, and channels. The conclusion was that each scheme answers a different question. SemVer is strong for public API compatibility, but weak as a universal product identity. CalVer is good for recency and support windows, but weak for compatibility. Build IDs and hashes are precise provenance tools, but poor human release labels.

The user should remember that the chat did not reject SemVer. It limited SemVer to the domain where it is truthful.

### Topic 2 — Versioning policy drift and “1.x hell”

The user’s concern was that many projects change versioning policy after the original scheme stops fitting. The chat identified the root cause as overloaded version strings. A scheme that tries to encode release age, compatibility, marketing generation, build identity, platform, and suite composition in one number will eventually break down.

The early four-part version proposal was superseded by a layered identity architecture.

### Topic 3 — Layered release identity architecture

The main design conclusion was that release identity should be layered: product/suite version, component version, build identity, compatibility/capability contracts, lifecycle channel, target/platform, package kind, and manifest metadata should remain separate. This is the central principle to carry forward.

### Topic 4 — Strict SemVer 2.0.0 for public APIs

The chat rebuilt SemVer from first principles and decided that strict SemVer should apply only to components with declared public contracts. Candidate true-SemVer entities include SDKs, engine libraries, tool APIs/CLIs, protocol libraries, plugin hosts, schema libraries, and reusable runtime libraries. It remains unresolved which exact repo modules qualify.

### Topic 5 — SemVer-shaped release IDs for non-SemVer products and suites

The user liked the visual shape of SemVer even for consumer-facing items. The chat accepted `X.Y.Z[-pre][+build]` as a useful shape, but required that non-SemVer products/suites be documented as release identifiers rather than API-compatibility promises.

### Topic 6 — Products versus suites

The chat separated standalone products from suites/distributions. Products include Stack, Tools, SDK, Engine, Game, Client, Server, Launcher, and Setup. Suites include All, Full, Lite, Net, User, Dev, and similar distributions. Metadata should include `scope=product|suite` to avoid ambiguity.

### Topic 7 — GBN and BII

GBN should identify CI/public/internal builds and appear as provenance, e.g. `+gbn.7137`, but it must not be used as SemVer precedence. BII should primarily be structured manifest metadata, because it may encode lane, target, kind, configuration, and other build identity fields. The exact BII schema remains unresolved.

### Topic 8 — Channels, lifecycle, and release class

The chat separated prerelease ordering labels from lifecycle/support metadata. `dev`, `alpha`, `beta`, and `rc` may belong in the version string. `stable`, `lts`, `nightly`, `internal`, `archival`, `hotfix`, `security`, and `rollback` should usually be lifecycle or release-class metadata.

### Topic 9 — Artifact naming and manifests

The proposed filename grammar became `Dominium-<scope>-<id>-<version>-<target>-<arch>-<pkg>.<ext>`. Examples included product SDKs, setup installers, and suite bundles. The chat stressed that filenames are not canonical truth; manifests are.

### Topic 10 — Platform and architecture taxonomy

The user proposed platform buckets for DOS, Windows, classic Mac, macOS, and Linux. The chat concluded that coarse platform labels are useful, but exact compatibility requires target baselines and runtime/toolchain profiles. Linux kernel major alone is not a reliable binary target. Windows 9x/NT families often need separate targets rather than one generic Windows binary.

### Topic 11 — Capabilities for internal compatibility

The final conceptual refinement was that internal compatibility should use capabilities/contracts rather than version ranges alone. A version says what release something is; a capability says what it can do. This is especially useful for saves, packs, plugins, network handshakes, installers, renderers, and platform/runtime constraints.

## 4. What We Were Trying to Achieve

### 4.1 Explicit Goals

The user explicitly wanted a versioning/release identity policy that would not need to change halfway through. They wanted to avoid SemVer stagnation, arbitrary major bumps, and product-history confusion. Later, the user wanted the conversation reconstructed into a knowledge base and preservation package for future aggregation.

### 4.2 Inferred Goals

The user likely wanted a repo-ready architecture for XStack/Dominium releases that can support many products, suites, channels, build identities, package types, targets, and internal compatibility checks. This is inferred from the repeated movement from theory into concrete product/suite/build/platform examples.

### 4.3 Goals That Changed Over Time

The conversation began as a comparison of versioning schemes. It evolved into a release identity architecture. It then became a SemVer adaptation exercise. Finally, it became a capability-based compatibility architecture layered under versioning.

### 4.4 Goals Still Unresolved

The main unresolved goals are to produce formal specs: Release Constitution, SemVer Component Inventory, Suite Release Policy, Build Identity Spec, Channel/Lifecycle Spec, Artifact Naming Spec, Manifest Schema, Target Taxonomy, and Capability Registry.

## 5. Decisions Made and Why

| ID | Decision | Status | Why it mattered | Confidence | Label |
| --- | --- | --- | --- | --- | --- |
| DECISION-01 | Use a layered release identity architecture rather than one universal version string. | Accepted direction | A single string cannot safely encode release identity, compatibility, provenance, support class, platform, package type, and suite composition. | 4 | FACT/INFERENCE |
| DECISION-02 | Strict SemVer 2.0.0 applies only where there is a declared public API/contract. | Accepted direction | SemVer is compatibility-centric and requires a public API; applying it everywhere would create fake semantics. | 5 | FACT |
| DECISION-03 | End-user products and suites may use SemVer-shaped identifiers without claiming strict SemVer semantics. | Accepted direction | Preserves readable familiar shape while avoiding false API compatibility claims. | 5 | FACT |
| DECISION-04 | Suites/distributions are separate from products/components. | Accepted direction | Full/Lite/Net/All are curated distributions, not equivalent to Engine/SDK/Client. | 4 | FACT |
| DECISION-05 | Suite versions should be human-curated and not strict SemVer. | Accepted direction | A suite is a tested bundle/release family, not one API. | 4 | FACT/INFERENCE |
| DECISION-06 | GBN belongs in build metadata/manifests as provenance, not SemVer precedence. | Accepted direction | SemVer build metadata after + does not affect precedence; GBN is exact build identity/order outside SemVer ordering. | 5 | FACT |
| DECISION-07 | BII should primarily be structured manifest metadata, with optional compact projection. | Tentative accepted direction | Full BII may become too structured/long for version strings. | 4 | INFERENCE |
| DECISION-08 | Do not encode stable as -stable and do not encode hotfix as a prerelease suffix. | Accepted direction | Under SemVer, -stable and -hotfix are prerelease identifiers below the plain release; hotfix should normally be a patch release plus release-class metadata. | 5 | FACT |
| DECISION-09 | Split prerelease ordering labels from lifecycle/support metadata. | Accepted direction | dev/alpha/beta/rc affect ordering; stable/lts/nightly/internal/hotfix describe policy/lifecycle. | 5 | FACT |
| DECISION-10 | Filenames are readable projections; manifests are canonical truth. | Accepted direction | Filenames cannot safely carry all metadata or evolve as the only authority. | 4 | FACT/INFERENCE |
| DECISION-11 | Separate support family from exact binary target baseline. | Accepted direction | A broad family like Linux5 or WinNT5 is not always an exact compatibility contract. | 4 | FACT/INFERENCE |
| DECISION-12 | Use capabilities/contracts internally for compatibility rather than relying on versions alone. | Tentative direction | Capabilities directly express what can interoperate, especially with backports, partial implementations, optional features, and multidimensional compatibility. | 3 | INFERENCE |

The decisions above are not all equally final. The strongest decisions are the separation of strict SemVer from SemVer-shaped release identifiers, the separation of product/suite/build/compatibility identities, and the rule that GBN/BII are provenance rather than SemVer precedence. The most tentative direction is the internal capability model, because the user proposed it and the assistant endorsed it, but the conversation has not yet produced a formal capability schema or user-ratified registry.

## 6. Ideas Considered but Rejected, Superseded, or Deprioritised

| ID | Option | Status | Reason | Final or tentative? | Reconsider conditions | Related workstream | Label |
| --- | --- | --- | --- | --- | --- | --- | --- |
| REJECTED-01 | Pure SemVer for everything. | Rejected/deprioritised | Does not fit suites, apps, packs, installers, and multidimensional compatibility. | Tentative but strong | Only reconsider for entities with declared public APIs. | WORKSTREAM-01 | FACT |
| REJECTED-02 | One universal version number for suite, products, builds, compatibility, and packages. | Rejected | Overloads one field and causes future policy drift. | Strong | Only tiny projects could accept this. | WORKSTREAM-01 | FACT/INFERENCE |
| REJECTED-03 | Four-part public version as the main answer. | Superseded | GBN already provides dense chronological/build identity, so public release need not add fourth field for density. | Tentative | May reappear for specific products if required by platform conventions. | WORKSTREAM-01 | FACT/INFERENCE |
| REJECTED-04 | Encoding stable as -stable. | Rejected | Under SemVer, any hyphen suffix is prerelease and sorts below stable. | Strong | Do not reconsider unless abandoning SemVer ordering semantics entirely. | WORKSTREAM-05 | FACT |
| REJECTED-05 | Encoding hotfix as -hotfix. | Rejected | Hotfix is usually a patch release plus release_class metadata, not a prerelease of the old version. | Strong | Only use for unreleased hotfix candidates if explicitly defined. | WORKSTREAM-05 | FACT |
| REJECTED-06 | Using Linux kernel major alone as exact binary target. | Rejected as exact target | Linux compatibility depends heavily on libc/runtime/toolchain/userland. | Strong | Can remain a coarse support family label. | WORKSTREAM-07 | FACT/INFERENCE |
| REJECTED-07 | Generic one-size Windows binary target. | Rejected as default | Windows 9x/NT families and old baselines differ materially. | Tentative | Could exist for very constrained CLI/tools after testing. | WORKSTREAM-07 | FACT/INFERENCE |
| REJECTED-08 | Filenames as canonical release truth. | Rejected | Filenames are too lossy and mutable. | Strong | Filename parsing may be used as convenience only. | WORKSTREAM-06 | FACT/INFERENCE |

These rejected or superseded options matter because future assistants may otherwise reintroduce them. The biggest trap is suggesting “just use SemVer everywhere.” That was explicitly narrowed. Another trap is treating `stable` or `hotfix` as prerelease suffixes even after SemVer ordering was explained.

## 7. Important Reasoning, Rationale, and Tradeoffs

The visible rationale was that version numbers are compact signals, but compactness becomes dangerous when one field carries too many meanings. SemVer is valuable because it ties version changes to public API compatibility, but that value disappears when applied to things without clear public APIs. Suite versions are valuable because humans need a simple release label, but they should not be mistaken for exact internal compatibility truth.

The main tradeoff was between readability and correctness. The user liked SemVer’s familiar shape, and the design preserves that shape. The correction is semantic: only true API/contract-bearing components claim strict SemVer. Products and suites may use SemVer-shaped identifiers but are explicitly not pure SemVer if their compatibility promises are not SemVer public-API promises.

GBN created another tradeoff. It gives dense build identity and repo-wide chronology, but SemVer build metadata does not affect precedence. The chosen model keeps GBN as provenance while requiring version/pre-release fields to handle release ordering.

Capabilities were introduced to reduce overreliance on versions for compatibility. This solves backports, partial implementations, optional features, multi-surface systems, and cross-product interoperability better than version ranges alone. The risk is capability chaos unless the registry is governed.

## 8. Plans, Future Work, and Next Steps

The immediate future work is to convert this design into formal repo/spec artifacts. Recommended order:

1. **Release Constitution**: define permanent field meanings and the rule that field meanings cannot be reinterpreted.
2. **Entity Classification / SemVer Component Inventory**: classify every product, suite, API, schema, protocol, plugin surface, and build field.
3. **Suite Release Policy**: define exactly what suite `X.Y.Z` means.
4. **Build Identity Spec**: define GBN, BII, git SHA, local build, CI build, and manifest usage.
5. **Channel/Lifecycle Spec**: define prerelease labels, lifecycle/support lanes, and release classes.
6. **Artifact Naming Spec**: freeze the filename grammar and package-kind vocabulary.
7. **Release Manifest Schema**: make manifests canonical.
8. **Target Taxonomy Spec**: define support families, exact baselines, architectures, runtime/toolchain profiles.
9. **Capability Compatibility Spec**: define capability namespaces, provided/required capabilities, versioned contracts, negotiation, migration, and validation.

The major blockers are repo verification and formal user decisions on suite semantics, BII schema, target taxonomy, and capability registry design.

## 9. Constraints, Preferences, and Non-Negotiables

### 9.1 Explicit Constraints and Preferences

The user prefers direct, audit-ready, source-grounded, high-fidelity reporting. They dislike overcompressed handoffs and machine-readable-only outputs. They want versioning policy stability and dislike arbitrary version policy shifts. They explicitly like strict SemVer for public APIs and SemVer-shaped identifiers for other release IDs.

### 9.2 Inferred Constraints and Preferences

The user values long-term maintainability over short-term prettiness. They prefer explicit metadata over hidden inference. They want future assistants to preserve tentative status and not silently turn brainstorms into decisions.

### 9.3 Uncertain or Unestablished Preferences

It is still uncertain how strict the user wants suite `X.Y.Z` field meanings to be, whether capabilities should fully replace compatibility profiles or coexist with them, and how much old-platform support should be real versus aspirational.

## 10. Files, Artifacts, Outputs, and Prompts

| ID | Artifact / file / prompt / output | Type | Purpose | Status | Origin | Carry forward? | Notes | Label |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| ARTIFACT-01 | Uploaded preservation mega-prompt: Pasted text.txt | Prompt/instruction file | Defines this preservation/export task. | Provided in current turn. | User upload | Yes | 1109-line prompt requiring human-readable report, registers, spec sheet, aggregator packet, self-audit, and file exports. | FACT |
| ARTIFACT-02 | In-chat versioning summary produced before upload | Chat output | Summarized decisions and unresolved issues up to that point. | Visible transcript | Assistant output | Yes | Served as prior knowledge-base baseline, but must not be treated as user-final decisions where not accepted. | FACT |
| ARTIFACT-03 | Canonical version examples | Examples/spec fragments | Illustrate strict SemVer and SemVer-shaped identifiers. | Visible discussion | Chat content | Yes | Examples include 1.2.3, 1.2.3-beta.1, +gbn.7137, +sha.deadbeef. | FACT |
| ARTIFACT-04 | Proposed artifact filename grammar | Spec fragment | Readable artifact naming model. | Visible discussion | Chat content | Yes | Pattern: Dominium-<scope>-<id>-<version>-<target>-<arch>-<pkg>.<ext>; not final. | FACT/INFERENCE |
| ARTIFACT-05 | Proposed capability model examples | Spec fragment | Internal compatibility strategy. | Visible discussion | Chat content | Yes | Examples: save.schema@5, plugin.host@2, net.protocol@3. Tentative. | INFERENCE |

This preservation task creates the first actual downloadable package in this chat. Prior artifacts were primarily in-chat examples, summaries, and proposed spec fragments.

## 11. Open Questions and Unresolved Issues

| ID | Question / issue | Why it matters | Known information | Unknown information | Resolution path | Priority | Related workstream | Label |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| QUESTION-01 | Which exact products/components are strict SemVer components? | Needed before Release Constitution can be enforced. | Candidates identified. | Final repo/component inventory and public API boundaries. | Audit repo and create SemVer Component Inventory. | P0 | WORKSTREAM-02 | FACT |
| QUESTION-02 | What exactly does suite version X.Y.Z mean? | Prevents future drift and marketing reinterpretation. | It is human-curated and non-SemVer. | Field semantics still not final. | Choose and document suite-major/train/update or equivalent. | P0 | WORKSTREAM-03 | FACT |
| QUESTION-03 | What is the exact BII schema? | BII must integrate with manifests, filenames, and support/debugging. | It should be structured metadata first. | Fields, tokenization, allowed values. | Inspect existing XStack/RepoX build identity and formalize. | P1 | WORKSTREAM-04 | FACT/INFERENCE |
| QUESTION-04 | What is the canonical artifact filename grammar? | Needed for releases/downloads. | Strong pattern proposed. | Final delimiters/case/fields/package kinds. | Draft naming spec and test examples. | P1 | WORKSTREAM-06 | FACT |
| QUESTION-05 | What should the manifest schema contain and validate? | Manifest is canonical truth. | Candidate fields listed. | Exact schema, required/optional fields, versioning. | Create YAML/JSON schema draft. | P1 | WORKSTREAM-06 | FACT |
| QUESTION-06 | What target family/baseline taxonomy should be used for DOS/Windows/Mac/Linux? | Avoids overclaiming binary compatibility. | Need to separate support family and exact baseline. | Exact labels and feasibility. | Research/test compiler/runtime support. | P1 | WORKSTREAM-07 | FACT/UNVERIFIED |
| QUESTION-07 | Should compatibility profiles remain distinct from capability contracts, or are capabilities the profile mechanism? | Affects internal resolver design. | Both ideas discussed. | Final relationship. | Design capability registry and map to suite manifests. | P1 | WORKSTREAM-08 | INFERENCE |

The most important unresolved issue is formal classification. Without knowing which entities are strict SemVer components, suite versions, product release IDs, build fields, or capabilities, the rest of the policy cannot be enforced safely.

## 12. Risks, Failure Modes, and What Future Chats Might Get Wrong

| ID | Risk / failure mode | Consequence | Likelihood | Severity | Mitigation | Related workstream | Label |
| --- | --- | --- | --- | --- | --- | --- | --- |
| RISK-01 | Future assistant treats SemVer-shaped product/suite IDs as strict SemVer. | False compatibility claims and wrong bump advice. | Medium | High | Always classify entity type first. | WORKSTREAM-01 | FACT/INFERENCE |
| RISK-02 | GBN used as SemVer ordering despite being in +build metadata. | Incorrect update ordering/resolver behavior. | Medium | High | Keep separate ordering fields and tests. | WORKSTREAM-04 | FACT |
| RISK-03 | BII becomes an overloaded version-string dump. | Fragile filenames and unreadable versions. | Medium | Medium | Keep full BII in manifest; expose compact token only. | WORKSTREAM-04 | INFERENCE |
| RISK-04 | OS/platform labels overclaim compatibility. | Artifacts fail on older claimed systems. | High | High | Separate support_family and target_baseline; test baselines. | WORKSTREAM-07 | FACT/UNVERIFIED |
| RISK-05 | Capabilities become undocumented string soup. | Compatibility resolver becomes arbitrary and hard to audit. | Medium | High | Create namespace, ownership, lifecycle, and validation rules. | WORKSTREAM-08 | INFERENCE |
| RISK-06 | Tentative ideas are merged as final requirements. | Spec book contains unstable or wrong commitments. | Medium | High | Preserve status labels and require user confirmation. | ALL | FACT/INFERENCE |
| RISK-07 | Human narrative is replaced by registers only. | User cannot understand old chat without rereading transcript. | Medium | Medium | Keep prose report as primary artifact. | Documentation | FACT |

The highest-risk misunderstanding is collapsing the layered model back into one universal version scheme. Future assistants should classify the entity first, then apply the correct policy.

## 13. What This Chat Contributes to the Larger Project or Future Spec Book

This chat contributes the release identity doctrine for Dominium/XStack. It should feed into chapters on release engineering, versioning, build identity, packaging, platform targeting, compatibility, capability negotiation, installer/setup workflow, and artifact manifests. The chat’s strongest formal-requirement candidates are: strict SemVer only for declared public APIs; SemVer-shaped identifiers for products/suites as separate release IDs; GBN/BII as provenance; manifests as canonical truth; channels split from lifecycle metadata; and capabilities/contracts as internal compatibility truth.

Items that should remain background until confirmed include exact suite field semantics, platform target families, and capability registry details.

## 14. What I Should Remember

- The core conclusion is layered identity: versions, suite labels, GBN, BII, capabilities, channels, targets, and package kinds each have separate jobs.
- Strict SemVer is for declared public APIs/contracts, not everything.
- User-facing products and suites may use SemVer-shaped IDs without claiming SemVer compatibility semantics.
- GBN identifies builds; it does not create SemVer precedence when placed after `+`.
- BII belongs primarily in structured metadata/manifests.
- `stable` and `hotfix` should not be encoded as prerelease suffixes.
- Filenames are projections. Manifests are truth.
- Platform support families are not exact binary baselines.
- Internal compatibility should likely be capability/contract-based.
- The next real work is formal spec writing and repo verification.

## 15. Best Questions I Can Ask Next in This Chat

### 15.1 Understanding the Chat
- Explain the difference between strict SemVer and SemVer-shaped release identifiers again using Dominium examples.
- What is the central design principle of this chat in one page?

### 15.2 Decisions
- Which decisions in this chat are firm, and which are only tentative?
- Which assistant suggestions have not yet been accepted as final user decisions?

### 15.3 Tasks and Next Actions
- Draft the Release Constitution from this chat.
- Create the SemVer Component Inventory table for Stack, Tools, SDK, Engine, Game, Client, Server, Launcher, and Setup.

### 15.4 Artifacts and Files
- Turn the artifact filename grammar into a normative spec.
- Convert the manifest field list into a JSON/YAML schema.

### 15.5 Risks and Verification
- What external facts need verification before this becomes a repo standard?
- Which OS/platform target assumptions are most likely to be wrong?

### 15.6 Future Spec Book / Aggregation
- Which sections of a master Dominium Project Spec Book should this chat feed into?
- What should an aggregator preserve versus leave tentative?

### 15.7 Deep-Dive Questions Specific to This Chat
- Design the internal capability registry for saves, packs, plugins, networking, renderers, installers, and runtimes.
- Decide whether compatibility profiles should be derived from capability sets or exist as separate named profiles.

## 16. Compact Human Summary

This chat developed a durable versioning and release identity strategy for Dominium/XStack. The user began with frustration about products that change versioning schemes over time and with SemVer’s tendency to create either permanent `1.x` stagnation or arbitrary major bumps. The conversation first compared versioning methods, then moved into a broader architecture: one version number cannot safely encode release identity, compatibility, build provenance, suite composition, support status, platform target, package type, and internal capability.

The strongest conclusion was to use a layered release identity system. Strict SemVer 2.0.0 should apply only to components with declared public APIs or compatibility contracts, such as SDKs, engine libraries, protocol/schema/plugin surfaces, reusable runtime libraries, and stable CLI/API tools. User-facing products and suites can still use a familiar SemVer-shaped syntax such as `1.2.3`, `1.2.3-beta.1`, and `1.2.3+gbn.7137`, but those identifiers must be documented as product or suite release IDs, not strict API SemVer unless a real public contract exists.

The chat separated products from suites. Products include Stack, Tools, SDK, Engine, Game, Client, Server, Launcher, and Setup. Suites/distributions include All, Full, Lite, Net, User, Dev, and similar bundles. The recommended metadata should include `scope=product|suite` and an `id`, so that `Engine` and `Full` are not flattened into the same namespace.

The chat integrated existing XStack ideas. GBN should identify exact CI/public/internal builds and may appear as build metadata, e.g. `+gbn.7137`, but it must not be used as SemVer precedence. BII should primarily be structured manifest metadata, with optional compact projection in filenames. Git SHA can identify local builds, e.g. `+sha.deadbeef`. The build/release system should distinguish exact provenance from release ordering.

Channels were split into two meanings. `dev`, `alpha`, `beta`, and `rc` can be prerelease ordering labels inside the version. `stable`, `lts`, `nightly`, `internal`, `archival`, and `hotfix` should generally be lifecycle or release-class metadata outside the version. A stable release is simply `1.2.3`, not `1.2.3-stable`. A hotfix should normally be a new patch version plus metadata, not `1.2.3-hotfix`.

Artifact names should be deterministic but not authoritative. The preferred filename pattern is `Dominium-<scope>-<id>-<version>-<target>-<arch>-<pkg>.<ext>`, but the manifest is the canonical truth. The manifest should contain product/suite identity, version, lifecycle, release class, target family, target baseline, architecture, package kind, GBN, BII, git hash, compatibility/capability information, and suite membership.

Platform targeting remains unresolved. The chat concluded that coarse families like WinNT5, WinNT10, MacOSX4, Linux5, or DOS5 are useful support labels, but exact binary compatibility needs target baselines and runtime/toolchain profiles. Linux kernel major alone is not enough. Windows 9x/NT/NT5/NT6/NT10 likely need separate build lanes or at least explicit tested baselines.

The final conceptual refinement was internal capability-based compatibility. Versions should identify releases; capabilities should decide whether things interoperate. Examples include `save.schema@5`, `plugin.host@2`, `net.protocol@3`, renderer capabilities, installer capabilities, pack schema capabilities, and runtime/platform capabilities. This is a tentative but strong direction and should become a formal capability registry if adopted.

The best next action is to draft a Release Constitution and SemVer Component Inventory, then formalize GBN/BII, channel/lifecycle, artifact naming, manifest schema, target taxonomy, and capability registry.
