# STRUCTURED REGISTERS — Dominium XStack Release Identity and Versioning

## 17. Workstream Register

| ID | Name | Objective | Current state | Desired end state | Status | Priority | Confidence | Label |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| WORKSTREAM-01 | Versioning doctrine | Define which entities use strict SemVer, SemVer-shaped release IDs, suite versions, and compatibility metadata. | Consensus direction formed; not yet formalized in repo. | A permanent Release Constitution and entity classification table. | Active | P0 | 4 | FACT/INFERENCE |
| WORKSTREAM-02 | SemVer component classification | Identify which products/components expose public APIs and therefore may claim strict SemVer 2.0.0 compliance. | Candidate list exists; final inventory not done. | Complete component-by-component policy. | Open | P0 | 4 | FACT |
| WORKSTREAM-03 | Suite/distribution release identity | Define suite versions for All/Full/Lite/Net/User/Dev distributions. | Direction: SemVer-shaped but explicitly non-SemVer, human-curated. | Stable suite version semantics and manifest binding. | Active | P0 | 4 | FACT/INFERENCE |
| WORKSTREAM-04 | GBN and BII integration | Integrate Global Build Number and Build Identification with version/build metadata without misusing precedence. | GBN-as-provenance direction decided; BII schema still open. | Canonical build identity spec and manifest fields. | Active | P1 | 4 | FACT |
| WORKSTREAM-05 | Channel/lifecycle model | Separate prerelease ordering labels from lifecycle/support metadata. | Direction clear; exact labels/order still to freeze. | Channel/lifecycle spec. | Active | P1 | 4 | FACT |
| WORKSTREAM-06 | Artifact naming and manifest model | Define deterministic artifact filenames while keeping manifests authoritative. | Strong filename pattern proposed; final grammar/schema open. | Artifact Naming Spec and Release Manifest Schema. | Open | P1 | 4 | FACT/INFERENCE |
| WORKSTREAM-07 | Platform/architecture target taxonomy | Separate coarse support families from exact binary target baselines. | Need identified; taxonomy unresolved. | Target triplet/profile registry for OS, arch, runtime/toolchain. | Open | P1 | 3 | FACT/INFERENCE |
| WORKSTREAM-08 | Capability-based internal compatibility | Use capabilities/contracts internally instead of relying on versions for interoperability. | User proposed; assistant endorsed; not yet formalized. | Capability registry, negotiation rules, and requirement/provision schema. | Tentative | P1 | 3 | INFERENCE |
| WORKSTREAM-09 | Setup product role | Represent Setup as standalone product capable of portable install/repair/uninstall/rollback/upgrade/migration using bundled or network sources. | Discussed and accepted as architectural direction, but details not specified here. | Setup release/manifest/install workflow spec. | Active | P2 | 3 | FACT/INFERENCE |

## 18. Decision Register

| ID | Decision | Status | Evidence / basis | Rationale | Implications | Related workstream | Confidence | Label |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| DECISION-01 | Use a layered release identity architecture rather than one universal version string. | Accepted direction | Repeated user agreement with separating versions, suite identity, build identity, and compatibility. | A single string cannot safely encode release identity, compatibility, provenance, support class, platform, package type, and suite composition. | All release/spec work must keep separate fields for separate meanings. | WORKSTREAM-01 | 4 | FACT/INFERENCE |
| DECISION-02 | Strict SemVer 2.0.0 applies only where there is a declared public API/contract. | Accepted direction | User explicitly liked strict SemVer 2 compliance for public APIs. | SemVer is compatibility-centric and requires a public API; applying it everywhere would create fake semantics. | SDK, engine libraries, protocol/schema/plugin surfaces are candidates; apps/suites need separate policy. | WORKSTREAM-02 | 5 | FACT |
| DECISION-03 | End-user products and suites may use SemVer-shaped identifiers without claiming strict SemVer semantics. | Accepted direction | User liked the look of SemVer for non-SemVer things. | Preserves readable familiar shape while avoiding false API compatibility claims. | Docs must distinguish true SemVer from SemVer-shaped release IDs. | WORKSTREAM-01 | 5 | FACT |
| DECISION-04 | Suites/distributions are separate from products/components. | Accepted direction | User listed standalone products separately from suites; assistant recommended scope=id metadata. | Full/Lite/Net/All are curated distributions, not equivalent to Engine/SDK/Client. | Metadata and filenames should include scope=product\|suite. | WORKSTREAM-03 | 4 | FACT |
| DECISION-05 | Suite versions should be human-curated and not strict SemVer. | Accepted direction | User proposed suite number as marketing/consumer-facing while components use stricter SemVer. | A suite is a tested bundle/release family, not one API. | Suite version should bind to manifest and compatibility/capability metadata. | WORKSTREAM-03 | 4 | FACT/INFERENCE |
| DECISION-06 | GBN belongs in build metadata/manifests as provenance, not SemVer precedence. | Accepted direction | Discussed repeatedly; user examples used +gbn/build. | SemVer build metadata after + does not affect precedence; GBN is exact build identity/order outside SemVer ordering. | Use e.g. +gbn.7137 and store canonical GBN field in manifest. | WORKSTREAM-04 | 5 | FACT |
| DECISION-07 | BII should primarily be structured manifest metadata, with optional compact projection. | Tentative accepted direction | Assistant recommendation not contradicted; user asked how BII should be encoded. | Full BII may become too structured/long for version strings. | Define BII schema separately; optionally include short token in filename/build metadata. | WORKSTREAM-04 | 4 | INFERENCE |
| DECISION-08 | Do not encode stable as -stable and do not encode hotfix as a prerelease suffix. | Accepted direction | Discussed after SemVer reconstruction. | Under SemVer, -stable and -hotfix are prerelease identifiers below the plain release; hotfix should normally be a patch release plus release-class metadata. | Use 1.2.3 for stable; 1.2.4 plus release_class=hotfix for hotfix. | WORKSTREAM-05 | 5 | FACT |
| DECISION-09 | Split prerelease ordering labels from lifecycle/support metadata. | Accepted direction | Repeated in summary and subsequent user request. | dev/alpha/beta/rc affect ordering; stable/lts/nightly/internal/hotfix describe policy/lifecycle. | Channel spec must have separate fields. | WORKSTREAM-05 | 5 | FACT |
| DECISION-10 | Filenames are readable projections; manifests are canonical truth. | Accepted direction | Discussed in artifact naming sections. | Filenames cannot safely carry all metadata or evolve as the only authority. | Every artifact should carry or reference a manifest with full identity and compatibility/capability fields. | WORKSTREAM-06 | 4 | FACT/INFERENCE |
| DECISION-11 | Separate support family from exact binary target baseline. | Accepted direction | Discussed around DOS/Windows/Mac/Linux platform buckets. | A broad family like Linux5 or WinNT5 is not always an exact compatibility contract. | Target taxonomy should include family, baseline, arch, runtime/toolchain profile. | WORKSTREAM-07 | 4 | FACT/INFERENCE |
| DECISION-12 | Use capabilities/contracts internally for compatibility rather than relying on versions alone. | Tentative direction | User proposed this; assistant endorsed. | Capabilities directly express what can interoperate, especially with backports, partial implementations, optional features, and multidimensional compatibility. | Need formal capability registry and negotiation schema. | WORKSTREAM-08 | 3 | INFERENCE |

## 19. Task Register

| ID | Task | Priority | Urgency | Owner | Dependencies | Inputs needed | Expected output | Next step | Related workstream | Label |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| TASK-01 | Draft the Release Constitution defining permanent field meanings and the no-reinterpretation rule. | P0 | U1 | User/future assistant | Decisions 01-10 | This report and current chat | Repo-ready policy document. | Write concise normative spec. | WORKSTREAM-01 | FACT/INFERENCE |
| TASK-02 | Inventory all Dominium/XStack entities and classify them as strict SemVer component, product release ID, suite release ID, compatibility/capability contract, or build/provenance field. | P0 | U1 | User/future assistant | Product/suite list and repo inventory | Actual repo module/product list | Classification table. | Create entity register. | WORKSTREAM-02 | FACT |
| TASK-03 | Define suite version semantics for All, Full, Lite, Net, User, Dev, etc. | P0 | U1 | User/future assistant | Decision 05 | Suite list and desired release trains | Suite version policy. | Choose field semantics for X.Y.Z. | WORKSTREAM-03 | FACT |
| TASK-04 | Formalize GBN usage and BII schema. | P1 | U1 | User/future assistant | Decision 06-07 | Current XStack build files/specs | Build Identity Spec. | Inspect repo/current build scripts. | WORKSTREAM-04 | FACT/INFERENCE |
| TASK-05 | Write Channel and Lifecycle Spec. | P1 | U1 | User/future assistant | Decision 08-09 | Desired channel list | Policy for prerelease labels, lifecycle, release_class. | Freeze accepted labels and ordering. | WORKSTREAM-05 | FACT |
| TASK-06 | Define artifact filename grammar and package-kind vocabulary. | P1 | U1 | User/future assistant | Decision 10 | Packaging needs and target taxonomy | Artifact Naming Spec. | Choose canonical grammar and examples. | WORKSTREAM-06 | FACT |
| TASK-07 | Define release manifest schema. | P1 | U1 | User/future assistant | Tasks 02-06 | Fields for product/suite/build/target/capabilities | Machine-readable schema. | Create YAML/JSON schema draft. | WORKSTREAM-06 | FACT/INFERENCE |
| TASK-08 | Define target family/baseline/arch/runtime taxonomy. | P1 | U2 | User/future assistant | Decision 11 | Supported OS/toolchain feasibility data | Target Taxonomy Spec. | Validate proposed OS families against real toolchains. | WORKSTREAM-07 | FACT/INFERENCE |
| TASK-09 | Design capability/contract registry and resolver rules. | P1 | U2 | User/future assistant | Decision 12 | Compatibility surfaces to model | Capability Compatibility Spec. | List contract families and sample provides/requires. | WORKSTREAM-08 | INFERENCE |
| TASK-10 | Decide Setup product versioning and artifact policy. | P2 | U2 | User/future assistant | Setup role discussion | Installer architecture details | Setup-specific release/install workflow spec. | Define standalone/portable setup capabilities. | WORKSTREAM-09 | INFERENCE |

## 20. Constraint Register

| ID | Constraint | Type | Hard/soft | Source / basis | Practical implication | Violation risk | Confidence | Label |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| CONSTRAINT-01 | Do not change field meanings after adoption. | Governance | Hard | Repeated design principle in chat. | Add fields for new meaning instead of reinterpreting old ones. | High if not documented. | 5 | FACT/INFERENCE |
| CONSTRAINT-02 | Only claim strict SemVer for entities with declared public API/contract. | Versioning | Hard | SemVer discussion and user acceptance. | Need API/contract documentation before compliance claims. | High if applied decoratively. | 5 | FACT |
| CONSTRAINT-03 | Build metadata after + must not be treated as SemVer precedence. | Versioning | Hard | SemVer rule discussed. | GBN may identify artifact but not order SemVer releases. | High if update logic sorts build metadata as release order. | 5 | FACT |
| CONSTRAINT-04 | Stable and hotfix are not prerelease suffixes. | Versioning | Hard | SemVer ordering discussion. | Use plain stable versions and patch bump + metadata for hotfixes. | Medium. | 5 | FACT |
| CONSTRAINT-05 | Manifest is canonical; filename is projection. | Release engineering | Hard | Artifact discussion. | Do not derive full truth only from filename parsing. | High if files move/rename. | 4 | FACT/INFERENCE |
| CONSTRAINT-06 | Compatibility should not be inferred solely from product/suite version. | Compatibility | Hard | Compatibility-axis and capability discussion. | Use explicit capabilities/contracts/schemas/protocol fields. | High in plugin/network/save/pack cases. | 4 | FACT/INFERENCE |
| CONSTRAINT-07 | Separate support family from exact binary target baseline. | Platform | Soft-to-hard | Platform discussion. | Need target_baseline/runtime/toolchain fields. | High for Linux/old OS overclaims. | 4 | FACT/INFERENCE |
| CONSTRAINT-08 | Human-readable preservation reports must not be replaced by machine-only handoffs. | Documentation | Hard | Uploaded preservation prompt. | Reports must explain substance and rationale. | Medium. | 5 | FACT |

## 21. User Preference Register

| ID | Preference | Area | Explicit/inferred/uncertain | Strength | Practical implication | Risk if wrong | Label |
| --- | --- | --- | --- | --- | --- | --- | --- |
| PREF-01 | Direct, source-grounded, audit-ready answers. | Communication | Explicit/project/user profile | High | Use labels, evidence, caveats, and structured outputs. | Loss of trust or unusable handoffs. | PROJECT-CONTEXT/FACT |
| PREF-02 | Avoid versioning policy changes halfway through. | Design | Explicit | High | Design durable fields and governance now. | Recreates Windows/Mac/.NET-style frustration. | FACT |
| PREF-03 | Likes SemVer visual shape even for non-SemVer release IDs. | Versioning | Explicit | High | Use X.Y.Z[-pre][+build] shape while documenting semantic class. | May falsely imply SemVer if not labelled. | FACT |
| PREF-04 | Wants meaningful consumer/suite number without overloading compatibility truth. | Versioning | Explicit/inferred | High | Suite version should convey family/train/update but defer exact compatibility to manifest/capabilities. | Too much hidden complexity or misleading number. | FACT/INFERENCE |
| PREF-05 | Prefers detailed knowledge-base summaries for later aggregation. | Documentation | Explicit | High | Use registers, IDs, and human narrative. | Information loss. | FACT |

## 22. Open Questions Register

| ID | Question / issue | Why it matters | Known information | Unknown information | Resolution path | Priority | Related workstream | Label |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| QUESTION-01 | Which exact products/components are strict SemVer components? | Needed before Release Constitution can be enforced. | Candidates identified. | Final repo/component inventory and public API boundaries. | Audit repo and create SemVer Component Inventory. | P0 | WORKSTREAM-02 | FACT |
| QUESTION-02 | What exactly does suite version X.Y.Z mean? | Prevents future drift and marketing reinterpretation. | It is human-curated and non-SemVer. | Field semantics still not final. | Choose and document suite-major/train/update or equivalent. | P0 | WORKSTREAM-03 | FACT |
| QUESTION-03 | What is the exact BII schema? | BII must integrate with manifests, filenames, and support/debugging. | It should be structured metadata first. | Fields, tokenization, allowed values. | Inspect existing XStack/RepoX build identity and formalize. | P1 | WORKSTREAM-04 | FACT/INFERENCE |
| QUESTION-04 | What is the canonical artifact filename grammar? | Needed for releases/downloads. | Strong pattern proposed. | Final delimiters/case/fields/package kinds. | Draft naming spec and test examples. | P1 | WORKSTREAM-06 | FACT |
| QUESTION-05 | What should the manifest schema contain and validate? | Manifest is canonical truth. | Candidate fields listed. | Exact schema, required/optional fields, versioning. | Create YAML/JSON schema draft. | P1 | WORKSTREAM-06 | FACT |
| QUESTION-06 | What target family/baseline taxonomy should be used for DOS/Windows/Mac/Linux? | Avoids overclaiming binary compatibility. | Need to separate support family and exact baseline. | Exact labels and feasibility. | Research/test compiler/runtime support. | P1 | WORKSTREAM-07 | FACT/UNVERIFIED |
| QUESTION-07 | Should compatibility profiles remain distinct from capability contracts, or are capabilities the profile mechanism? | Affects internal resolver design. | Both ideas discussed. | Final relationship. | Design capability registry and map to suite manifests. | P1 | WORKSTREAM-08 | INFERENCE |

## 23. Artifact Ledger

| ID | Artifact / file / prompt / output | Type | Purpose | Status | Origin | Carry forward? | Notes | Label |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| ARTIFACT-01 | Uploaded preservation mega-prompt: Pasted text.txt | Prompt/instruction file | Defines this preservation/export task. | Provided in current turn. | User upload | Yes | 1109-line prompt requiring human-readable report, registers, spec sheet, aggregator packet, self-audit, and file exports. | FACT |
| ARTIFACT-02 | In-chat versioning summary produced before upload | Chat output | Summarized decisions and unresolved issues up to that point. | Visible transcript | Assistant output | Yes | Served as prior knowledge-base baseline, but must not be treated as user-final decisions where not accepted. | FACT |
| ARTIFACT-03 | Canonical version examples | Examples/spec fragments | Illustrate strict SemVer and SemVer-shaped identifiers. | Visible discussion | Chat content | Yes | Examples include 1.2.3, 1.2.3-beta.1, +gbn.7137, +sha.deadbeef. | FACT |
| ARTIFACT-04 | Proposed artifact filename grammar | Spec fragment | Readable artifact naming model. | Visible discussion | Chat content | Yes | Pattern: Dominium-<scope>-<id>-<version>-<target>-<arch>-<pkg>.<ext>; not final. | FACT/INFERENCE |
| ARTIFACT-05 | Proposed capability model examples | Spec fragment | Internal compatibility strategy. | Visible discussion | Chat content | Yes | Examples: save.schema@5, plugin.host@2, net.protocol@3. Tentative. | INFERENCE |

## 24. Rejected / Superseded Options Register

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

## 25. Risk Register

| ID | Risk / failure mode | Consequence | Likelihood | Severity | Mitigation | Related workstream | Label |
| --- | --- | --- | --- | --- | --- | --- | --- |
| RISK-01 | Future assistant treats SemVer-shaped product/suite IDs as strict SemVer. | False compatibility claims and wrong bump advice. | Medium | High | Always classify entity type first. | WORKSTREAM-01 | FACT/INFERENCE |
| RISK-02 | GBN used as SemVer ordering despite being in +build metadata. | Incorrect update ordering/resolver behavior. | Medium | High | Keep separate ordering fields and tests. | WORKSTREAM-04 | FACT |
| RISK-03 | BII becomes an overloaded version-string dump. | Fragile filenames and unreadable versions. | Medium | Medium | Keep full BII in manifest; expose compact token only. | WORKSTREAM-04 | INFERENCE |
| RISK-04 | OS/platform labels overclaim compatibility. | Artifacts fail on older claimed systems. | High | High | Separate support_family and target_baseline; test baselines. | WORKSTREAM-07 | FACT/UNVERIFIED |
| RISK-05 | Capabilities become undocumented string soup. | Compatibility resolver becomes arbitrary and hard to audit. | Medium | High | Create namespace, ownership, lifecycle, and validation rules. | WORKSTREAM-08 | INFERENCE |
| RISK-06 | Tentative ideas are merged as final requirements. | Spec book contains unstable or wrong commitments. | Medium | High | Preserve status labels and require user confirmation. | ALL | FACT/INFERENCE |
| RISK-07 | Human narrative is replaced by registers only. | User cannot understand old chat without rereading transcript. | Medium | Medium | Keep prose report as primary artifact. | Documentation | FACT |

## 26. Verification Queue

| ID | Item requiring verification | Why verification is needed | Suggested source/type | Priority | Related workstream | Label |
| --- | --- | --- | --- | --- | --- | --- |
| VERIFY-01 | Exact current SemVer 2.0.0 text before writing final normative repo spec. | Formal docs should cite the primary spec. | semver.org primary spec | P1 | WORKSTREAM-01 | UNVERIFIED |
| VERIFY-02 | Actual existing XStack/RepoX build files, GBN behavior, and BII fields. | Earlier discussion referenced repo/build system, but this preservation task did not inspect repo files. | Repo inspection | P0 | WORKSTREAM-04 | UNCERTAIN |
| VERIFY-03 | Feasibility of proposed OS target families and one-binary-per-family claims. | Compiler/runtime support is external and time/toolchain dependent. | Toolchain docs and build tests | P1 | WORKSTREAM-07 | UNVERIFIED |
| VERIFY-04 | Exact product/suite list in repository. | User listed examples with “etc.”, not final inventory. | Repo inventory and user confirmation | P0 | WORKSTREAM-02 | UNCERTAIN |
| VERIFY-05 | Whether capability profiles should be separate entities or derived from capability sets. | Design still tentative. | Architecture decision record/user decision | P1 | WORKSTREAM-08 | UNCERTAIN |

## 27. Chronological Timeline Register

| Sequence | Event / topic | What changed or was decided | Why it mattered | Current relevance | Confidence |
| --- | --- | --- | --- | --- | --- |
| 01 | Comparison of SemVer and other versioning methods | Established each scheme answers different questions. | Opened the design space beyond SemVer. | Background rationale. | 4 |
| 02 | User objected to policy drift and 1.x hell | Problem reframed as information design and field semantics. | Drove durable-field principle. | Central motivation. | 5 |
| 03 | Four-part public version considered | GEN/EPOCH/FEATURE/PATCH proposed. | Helped separate progress from compatibility. | Mostly superseded by layered identity + GBN. | 4 |
| 04 | XStack/GBN/build identity considered | Layered model recommended. | Connected theory to project build system. | Needs repo verification. | 3 |
| 05 | Components vs suite versions | User proposed stricter component SemVer plus meaningful suite version. | Created product/suite separation. | Core decision. | 5 |
| 06 | Suite version semantics refined | Suite version becomes human-curated release family/envelope, not strict SemVer. | Avoids overloading consumer label. | Needs formal semantics. | 4 |
| 07 | Products/suites/platforms/packaging listed | Filename and metadata grammar explored. | Mapped release identity to actual artifact names. | Spec work needed. | 4 |
| 08 | SemVer 2.0 reconstructed from scratch | Defined public API, prerelease, build metadata, precedence, stable/hotfix consequences. | Anchored future adaptations. | Core normative base. | 5 |
| 09 | SemVer-shaped non-SemVer IDs accepted | User liked visual syntax for non-API things. | Preserves readability without false semantics. | Core decision. | 5 |
| 10 | Knowledge-base summary produced | Prior summary captured decisions/open issues. | Served as pre-export baseline. | Useful but now superseded by this package. | 5 |
| 11 | Capabilities proposed for internal compatibility | Versions identify releases; capabilities decide interop. | Major refinement of compatibility model. | Tentative high-value direction. | 4 |
| 12 | Preservation mega-prompt uploaded | User requested full report, registers, spec sheet, aggregator packet, audit, and files. | Current task. | This package implements it. | 5 |

## 28. Spec Book Contribution Register


| Spec-book area | Contribution from this chat | Source IDs | Should become requirement/context/open issue? | Confidence | Notes |
|---|---|---|---|---|---|
| Release Engineering | Layered release identity model; separate product/suite/build/channel/target/package/capability fields. | DECISION-01, CONSTRAINT-01 | Requirement | 4 | Central contribution. |
| Versioning | Strict SemVer only for declared public APIs; SemVer-shaped release IDs elsewhere. | DECISION-02, DECISION-03 | Requirement | 5 | Needs entity inventory. |
| Suite/Distribution Model | Suites are curated distributions with human-facing versions, not strict SemVer components. | DECISION-04, DECISION-05 | Requirement/open issue | 4 | Exact suite X.Y.Z semantics still open. |
| Build Identity | GBN/BII/hash as provenance separate from precedence. | DECISION-06, DECISION-07 | Requirement/open issue | 4 | BII schema requires repo verification. |
| Channels/Lifecycle | Prerelease labels split from lifecycle/release class. | DECISION-08, DECISION-09 | Requirement | 5 | Straightforward to formalize. |
| Artifact Packaging | Filename grammar and package-kind vocabulary; manifest as truth. | DECISION-10 | Requirement/open issue | 4 | Final grammar/schema still open. |
| Platform Targeting | Support family vs exact binary baseline distinction. | DECISION-11 | Requirement/open issue | 4 | Needs toolchain verification. |
| Compatibility Architecture | Capability/contract-based compatibility model. | DECISION-12 | Open issue/likely requirement | 3 | Strong direction, not fully ratified. |
