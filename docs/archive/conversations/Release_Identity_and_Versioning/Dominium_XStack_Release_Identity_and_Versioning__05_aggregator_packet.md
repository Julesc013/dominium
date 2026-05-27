# 31. Aggregator Packet — Dominium XStack Release Identity and Versioning

## Packet Metadata

* Chat label: Dominium XStack Release Identity and Versioning
* Date anchor: 2026-05-27 Australia/Melbourne
* Source scope: This chat only unless labelled PROJECT-CONTEXT
* Coverage: Partial visible/current transcript plus uploaded prompt
* Confidence: 4/5
* Staleness risk: Low for design, medium for external/repo/toolchain claims
* Merge priority: High
* Main limitations: actual repo/build files and old-platform toolchain feasibility were not verified in this preservation task.

## Ultra-Condensed Carry-Forward Capsule

This chat is the main release identity/versioning doctrine chat for Dominium/XStack. It starts from the user's dislike of products that change versioning policies halfway through and develops a layered identity model that separates product/suite versions, strict SemVer components, build identity, GBN, BII, channels, lifecycle, artifact names, platform targets, manifests, and internal compatibility/capabilities.

The strongest outcome is that strict SemVer 2.0.0 should be used only for components with declared public APIs or compatibility contracts. Candidate true-SemVer components include SDKs, engine libraries, protocol/schema/plugin surfaces, reusable runtime libraries, and stable CLI/API tools. Other end-user products and suites may still use SemVer-shaped release identifiers such as `1.2.3`, `1.2.3-beta.1`, and `1.2.3+gbn.7137`, but those are not strict SemVer unless a declared public API exists.

Products and suites are distinct. Products include Stack, Tools, SDK, Engine, Game, Client, Server, Launcher, and Setup. Suites/distributions include All, Full, Lite, Net, User, Dev, etc. Metadata should include `scope=product|suite` and `id`. Suite versions should be human-curated consumer-facing release identities, not strict SemVer. Exact compatibility belongs in explicit metadata.

GBN is exact build provenance and can appear in build metadata like `+gbn.7137`; it must not be used as SemVer precedence. Local builds may use `+sha.deadbeef`. BII should be structured manifest metadata first, optionally compacted into filenames. Channels must be split: `dev/alpha/beta/rc` as prerelease ordering labels; `stable/lts/nightly/internal/archival/hotfix/security/rollback` as lifecycle or release-class metadata. Do not use `-stable` or normal `-hotfix` suffixes.

Filenames are projections, not truth. Preferred pattern: `Dominium-<scope>-<id>-<version>-<target>-<arch>-<pkg>.<ext>`. Manifests are canonical and should include product/suite identity, version, lifecycle, release class, GBN, BII, git hash, target family, exact baseline, arch, runtime/toolchain profile, package kind, compatibility/capability contracts, and suite membership.

Platform targeting remains open. The chat distinguished support families from exact binary target baselines. Coarse labels such as WinNT5, WinNT10, MacOSX4, Linux5, and DOS5 can be human-facing support families, but exact binary support requires tested baselines. Linux kernel major alone is not enough. Old Windows and Mac support requires toolchain/runtime verification.

The final refinement is capability-based internal compatibility. Versions identify releases; capabilities/contracts decide whether things interoperate. Examples: `save.schema@5`, `plugin.host@2`, `net.protocol@3`. This is a strong tentative direction requiring a formal capability registry and resolver rules.

## Top Carry-Forward Items

| Priority | Item | Type | Related ID | Why it matters | Label | Confidence |
| --- | --- | --- | --- | --- | --- | --- |
| P0 | Layered release identity model | Decision | DECISION-01 | Prevents overloaded version strings and future policy drift. | FACT/INFERENCE | 4 |
| P0 | Strict SemVer only for declared public APIs | Decision | DECISION-02 | Prevents false compatibility semantics. | FACT | 5 |
| P0 | SemVer-shaped release IDs for non-SemVer products/suites | Decision | DECISION-03 | Preserves readable syntax while staying honest. | FACT | 5 |
| P0 | Draft Release Constitution | Task | TASK-01 | Needed before formal repo adoption. | FACT/INFERENCE | 4 |
| P0 | Classify all entities | Task | TASK-02 | Determines which policy applies. | FACT | 4 |
| P1 | GBN/BII provenance model | Decision/task | DECISION-06/TASK-04 | Core build identity integration. | FACT | 4 |
| P1 | Capability compatibility model | Tentative decision/task | DECISION-12/TASK-09 | Best internal interop mechanism. | INFERENCE | 3 |

## Workstream Summaries

* ID: WORKSTREAM-01
* Name: Versioning doctrine
* Objective: Define which entities use strict SemVer, SemVer-shaped release IDs, suite versions, and compatibility metadata.
* Current state: Consensus direction formed; not yet formalized in repo.
* Desired end state: A permanent Release Constitution and entity classification table.
* Priority: P0
* Decisions: see Decision Register.
* Tasks: see Task Register.
* Constraints: see Constraint Register.
* Artifacts: see Artifact Ledger.
* Risks: see Risk Register.
* Open questions: see Open Questions Register.
* Next action: formalize in repo/spec document.

* ID: WORKSTREAM-02
* Name: SemVer component classification
* Objective: Identify which products/components expose public APIs and therefore may claim strict SemVer 2.0.0 compliance.
* Current state: Candidate list exists; final inventory not done.
* Desired end state: Complete component-by-component policy.
* Priority: P0
* Decisions: see Decision Register.
* Tasks: see Task Register.
* Constraints: see Constraint Register.
* Artifacts: see Artifact Ledger.
* Risks: see Risk Register.
* Open questions: see Open Questions Register.
* Next action: formalize in repo/spec document.

* ID: WORKSTREAM-03
* Name: Suite/distribution release identity
* Objective: Define suite versions for All/Full/Lite/Net/User/Dev distributions.
* Current state: Direction: SemVer-shaped but explicitly non-SemVer, human-curated.
* Desired end state: Stable suite version semantics and manifest binding.
* Priority: P0
* Decisions: see Decision Register.
* Tasks: see Task Register.
* Constraints: see Constraint Register.
* Artifacts: see Artifact Ledger.
* Risks: see Risk Register.
* Open questions: see Open Questions Register.
* Next action: formalize in repo/spec document.

* ID: WORKSTREAM-04
* Name: GBN and BII integration
* Objective: Integrate Global Build Number and Build Identification with version/build metadata without misusing precedence.
* Current state: GBN-as-provenance direction decided; BII schema still open.
* Desired end state: Canonical build identity spec and manifest fields.
* Priority: P1
* Decisions: see Decision Register.
* Tasks: see Task Register.
* Constraints: see Constraint Register.
* Artifacts: see Artifact Ledger.
* Risks: see Risk Register.
* Open questions: see Open Questions Register.
* Next action: formalize in repo/spec document.

* ID: WORKSTREAM-05
* Name: Channel/lifecycle model
* Objective: Separate prerelease ordering labels from lifecycle/support metadata.
* Current state: Direction clear; exact labels/order still to freeze.
* Desired end state: Channel/lifecycle spec.
* Priority: P1
* Decisions: see Decision Register.
* Tasks: see Task Register.
* Constraints: see Constraint Register.
* Artifacts: see Artifact Ledger.
* Risks: see Risk Register.
* Open questions: see Open Questions Register.
* Next action: formalize in repo/spec document.

* ID: WORKSTREAM-06
* Name: Artifact naming and manifest model
* Objective: Define deterministic artifact filenames while keeping manifests authoritative.
* Current state: Strong filename pattern proposed; final grammar/schema open.
* Desired end state: Artifact Naming Spec and Release Manifest Schema.
* Priority: P1
* Decisions: see Decision Register.
* Tasks: see Task Register.
* Constraints: see Constraint Register.
* Artifacts: see Artifact Ledger.
* Risks: see Risk Register.
* Open questions: see Open Questions Register.
* Next action: formalize in repo/spec document.

* ID: WORKSTREAM-07
* Name: Platform/architecture target taxonomy
* Objective: Separate coarse support families from exact binary target baselines.
* Current state: Need identified; taxonomy unresolved.
* Desired end state: Target triplet/profile registry for OS, arch, runtime/toolchain.
* Priority: P1
* Decisions: see Decision Register.
* Tasks: see Task Register.
* Constraints: see Constraint Register.
* Artifacts: see Artifact Ledger.
* Risks: see Risk Register.
* Open questions: see Open Questions Register.
* Next action: formalize in repo/spec document.

* ID: WORKSTREAM-08
* Name: Capability-based internal compatibility
* Objective: Use capabilities/contracts internally instead of relying on versions for interoperability.
* Current state: User proposed; assistant endorsed; not yet formalized.
* Desired end state: Capability registry, negotiation rules, and requirement/provision schema.
* Priority: P1
* Decisions: see Decision Register.
* Tasks: see Task Register.
* Constraints: see Constraint Register.
* Artifacts: see Artifact Ledger.
* Risks: see Risk Register.
* Open questions: see Open Questions Register.
* Next action: formalize in repo/spec document.

* ID: WORKSTREAM-09
* Name: Setup product role
* Objective: Represent Setup as standalone product capable of portable install/repair/uninstall/rollback/upgrade/migration using bundled or network sources.
* Current state: Discussed and accepted as architectural direction, but details not specified here.
* Desired end state: Setup release/manifest/install workflow spec.
* Priority: P2
* Decisions: see Decision Register.
* Tasks: see Task Register.
* Constraints: see Constraint Register.
* Artifacts: see Artifact Ledger.
* Risks: see Risk Register.
* Open questions: see Open Questions Register.
* Next action: formalize in repo/spec document.

## Compact Registers for Merge

### Decisions

| ID | Decision | Status | Confidence | Label |
| --- | --- | --- | --- | --- |
| DECISION-01 | Use a layered release identity architecture rather than one universal version string. | Accepted direction | 4 | FACT/INFERENCE |
| DECISION-02 | Strict SemVer 2.0.0 applies only where there is a declared public API/contract. | Accepted direction | 5 | FACT |
| DECISION-03 | End-user products and suites may use SemVer-shaped identifiers without claiming strict SemVer semantics. | Accepted direction | 5 | FACT |
| DECISION-04 | Suites/distributions are separate from products/components. | Accepted direction | 4 | FACT |
| DECISION-05 | Suite versions should be human-curated and not strict SemVer. | Accepted direction | 4 | FACT/INFERENCE |
| DECISION-06 | GBN belongs in build metadata/manifests as provenance, not SemVer precedence. | Accepted direction | 5 | FACT |
| DECISION-07 | BII should primarily be structured manifest metadata, with optional compact projection. | Tentative accepted direction | 4 | INFERENCE |
| DECISION-08 | Do not encode stable as -stable and do not encode hotfix as a prerelease suffix. | Accepted direction | 5 | FACT |
| DECISION-09 | Split prerelease ordering labels from lifecycle/support metadata. | Accepted direction | 5 | FACT |
| DECISION-10 | Filenames are readable projections; manifests are canonical truth. | Accepted direction | 4 | FACT/INFERENCE |
| DECISION-11 | Separate support family from exact binary target baseline. | Accepted direction | 4 | FACT/INFERENCE |
| DECISION-12 | Use capabilities/contracts internally for compatibility rather than relying on versions alone. | Tentative direction | 3 | INFERENCE |

### Tasks

| ID | Task | Priority | Urgency | Related workstream | Label |
| --- | --- | --- | --- | --- | --- |
| TASK-01 | Draft the Release Constitution defining permanent field meanings and the no-reinterpretation rule. | P0 | U1 | WORKSTREAM-01 | FACT/INFERENCE |
| TASK-02 | Inventory all Dominium/XStack entities and classify them as strict SemVer component, product release ID, suite release ID, compatibility/capability contract, or build/provenance field. | P0 | U1 | WORKSTREAM-02 | FACT |
| TASK-03 | Define suite version semantics for All, Full, Lite, Net, User, Dev, etc. | P0 | U1 | WORKSTREAM-03 | FACT |
| TASK-04 | Formalize GBN usage and BII schema. | P1 | U1 | WORKSTREAM-04 | FACT/INFERENCE |
| TASK-05 | Write Channel and Lifecycle Spec. | P1 | U1 | WORKSTREAM-05 | FACT |
| TASK-06 | Define artifact filename grammar and package-kind vocabulary. | P1 | U1 | WORKSTREAM-06 | FACT |
| TASK-07 | Define release manifest schema. | P1 | U1 | WORKSTREAM-06 | FACT/INFERENCE |
| TASK-08 | Define target family/baseline/arch/runtime taxonomy. | P1 | U2 | WORKSTREAM-07 | FACT/INFERENCE |
| TASK-09 | Design capability/contract registry and resolver rules. | P1 | U2 | WORKSTREAM-08 | INFERENCE |
| TASK-10 | Decide Setup product versioning and artifact policy. | P2 | U2 | WORKSTREAM-09 | INFERENCE |

### Constraints

| ID | Constraint | Hard/soft | Confidence | Label |
| --- | --- | --- | --- | --- |
| CONSTRAINT-01 | Do not change field meanings after adoption. | Hard | 5 | FACT/INFERENCE |
| CONSTRAINT-02 | Only claim strict SemVer for entities with declared public API/contract. | Hard | 5 | FACT |
| CONSTRAINT-03 | Build metadata after + must not be treated as SemVer precedence. | Hard | 5 | FACT |
| CONSTRAINT-04 | Stable and hotfix are not prerelease suffixes. | Hard | 5 | FACT |
| CONSTRAINT-05 | Manifest is canonical; filename is projection. | Hard | 4 | FACT/INFERENCE |
| CONSTRAINT-06 | Compatibility should not be inferred solely from product/suite version. | Hard | 4 | FACT/INFERENCE |
| CONSTRAINT-07 | Separate support family from exact binary target baseline. | Soft-to-hard | 4 | FACT/INFERENCE |
| CONSTRAINT-08 | Human-readable preservation reports must not be replaced by machine-only handoffs. | Hard | 5 | FACT |

### Open Questions

| ID | Question / issue | Priority | Related workstream | Label |
| --- | --- | --- | --- | --- |
| QUESTION-01 | Which exact products/components are strict SemVer components? | P0 | WORKSTREAM-02 | FACT |
| QUESTION-02 | What exactly does suite version X.Y.Z mean? | P0 | WORKSTREAM-03 | FACT |
| QUESTION-03 | What is the exact BII schema? | P1 | WORKSTREAM-04 | FACT/INFERENCE |
| QUESTION-04 | What is the canonical artifact filename grammar? | P1 | WORKSTREAM-06 | FACT |
| QUESTION-05 | What should the manifest schema contain and validate? | P1 | WORKSTREAM-06 | FACT |
| QUESTION-06 | What target family/baseline taxonomy should be used for DOS/Windows/Mac/Linux? | P1 | WORKSTREAM-07 | FACT/UNVERIFIED |
| QUESTION-07 | Should compatibility profiles remain distinct from capability contracts, or are capabilities the profile mechanism? | P1 | WORKSTREAM-08 | INFERENCE |

### Artifact Ledger

| ID | Artifact | Type | Carry forward? | Label |
| --- | --- | --- | --- | --- |
| ARTIFACT-01 | Uploaded preservation mega-prompt: Pasted text.txt | Prompt/instruction file | Yes | FACT |
| ARTIFACT-02 | In-chat versioning summary produced before upload | Chat output | Yes | FACT |
| ARTIFACT-03 | Canonical version examples | Examples/spec fragments | Yes | FACT |
| ARTIFACT-04 | Proposed artifact filename grammar | Spec fragment | Yes | FACT/INFERENCE |
| ARTIFACT-05 | Proposed capability model examples | Spec fragment | Yes | INFERENCE |

### Risk Register

| ID | Risk | Severity | Mitigation | Label |
| --- | --- | --- | --- | --- |
| RISK-01 | Future assistant treats SemVer-shaped product/suite IDs as strict SemVer. | High | Always classify entity type first. | FACT/INFERENCE |
| RISK-02 | GBN used as SemVer ordering despite being in +build metadata. | High | Keep separate ordering fields and tests. | FACT |
| RISK-03 | BII becomes an overloaded version-string dump. | Medium | Keep full BII in manifest; expose compact token only. | INFERENCE |
| RISK-04 | OS/platform labels overclaim compatibility. | High | Separate support_family and target_baseline; test baselines. | FACT/UNVERIFIED |
| RISK-05 | Capabilities become undocumented string soup. | High | Create namespace, ownership, lifecycle, and validation rules. | INFERENCE |
| RISK-06 | Tentative ideas are merged as final requirements. | High | Preserve status labels and require user confirmation. | FACT/INFERENCE |
| RISK-07 | Human narrative is replaced by registers only. | Medium | Keep prose report as primary artifact. | FACT |

### Verification Queue

| ID | Item | Priority | Related workstream | Label |
| --- | --- | --- | --- | --- |
| VERIFY-01 | Exact current SemVer 2.0.0 text before writing final normative repo spec. | P1 | WORKSTREAM-01 | UNVERIFIED |
| VERIFY-02 | Actual existing XStack/RepoX build files, GBN behavior, and BII fields. | P0 | WORKSTREAM-04 | UNCERTAIN |
| VERIFY-03 | Feasibility of proposed OS target families and one-binary-per-family claims. | P1 | WORKSTREAM-07 | UNVERIFIED |
| VERIFY-04 | Exact product/suite list in repository. | P0 | WORKSTREAM-02 | UNCERTAIN |
| VERIFY-05 | Whether capability profiles should be separate entities or derived from capability sets. | P1 | WORKSTREAM-08 | UNCERTAIN |

## Possible Cross-Chat Duplicates

Likely overlaps with Dominium architecture, build/distribution, installer/setup, platform/renderer, and XStack governance chats.

## Possible Cross-Chat Conflicts

Watch for older documents that require SemVer for all entities, encode stable/hotfix as prerelease suffixes, treat GBN as release precedence, use filenames as canonical truth, or use OS family labels as exact binary compatibility claims.

## Spec Book Integration Guidance

Feed this chat into release engineering, versioning, build identity, packaging, platform targets, installer/setup, and capability compatibility chapters. Make strict SemVer scoping, GBN/BII provenance, manifest authority, and capability-based compatibility formal requirements after user confirmation and repo verification. Keep exact suite semantics, BII schema, target taxonomy, and capability registry as open issues until resolved.

## Aggregator Warnings

Do not flatten products and suites. Do not convert tentative capability ideas into final requirements without confirmation. Do not erase uncertainty about actual repo state or OS/toolchain feasibility.
