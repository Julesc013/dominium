# Accompanying Detailed Human Report — Dominium XStack Release Identity and Versioning

**Date anchor:** 2026-05-27 Australia/Melbourne  
**Chat label:** Dominium XStack Release Identity and Versioning  
**Source scope:** This chat only, unless explicitly marked otherwise.  
**Coverage note:** This report is based on the visible conversation context and the preservation files already generated in this chat. It is not an independent audit of the live repository, build scripts, or toolchain feasibility.

## 1. Executive Orientation

This conversation was about designing a durable versioning, release identity, compatibility, build provenance, artifact naming, packaging, and platform-targeting system for Dominium/XStack.

The user’s original concern was that many long-lived products change versioning policy halfway through their life. The user named examples such as Windows NT, Minecraft, macOS, .NET, Linux, and TeX. The complaint was not merely aesthetic. It was about information loss, unstable policy, arbitrary version bumps, and the tendency for version numbers to become cultural or marketing symbols rather than stable technical signals.

The earliest discussion compared Semantic Versioning against other versioning systems. SemVer was identified as good for communicating public API compatibility, but poor as a universal identity system for a large product or suite. Calendar Versioning is good for age and cadence. Serial or global build numbers are good for ordering and audit trails. Git hashes are good for exact source identity. Marketing versions are good for consumer recognition. Protocol/schema versions are good for interface contracts. Release channels are good for risk/support classification. The important conclusion was that each system answers a different question.

The conversation then moved from “pick the best versioning scheme” to “build a layered release identity architecture.” That became the central idea. Dominium/XStack should not compress product identity, suite identity, compatibility, build provenance, lifecycle channel, target OS, architecture, installer/package kind, and internal feature support into one overloaded version string. Instead, each concept should have its own field, each field should have one stable meaning, and future requirements should be handled by adding fields rather than reinterpreting old ones.

A major outcome was the separation between **strict SemVer** and **SemVer-shaped release identifiers**. The user liked the visual form of versions such as `1.2.3`, `1.2.3-beta.1`, `1.2.3+gbn.7137`, and `1.2.3-beta.1+sha.deadbeef`. The agreed direction was that this shape can be used broadly, but strict SemVer 2.0.0 semantics should only be claimed by entities with real declared public API or compatibility contracts. End-user products and suites can use the same shape as release identifiers without pretending that every component of SemVer’s public API compatibility model applies.

The conversation also integrated XStack-specific concepts such as Global Build Number (GBN), BII/build identification, suite downloads, Setup as a standalone product, release channels, platforms, architectures, packages, bundles, packs, and old-platform support. GBN should identify exact CI/global builds and can appear in build metadata such as `+gbn.7137`, but it must not be used as SemVer precedence because SemVer build metadata does not affect ordering. BII should primarily be structured manifest metadata, with possible compact projections into filenames or build metadata.

The final conceptual improvement was the user’s proposal that internal compatibility should use **capabilities** rather than versions. This was accepted as a strong direction. Versions identify releases; capabilities determine whether things can actually interoperate. Examples include `save.schema@5`, `plugin.host@2`, `net.protocol@3`, renderer capabilities, installer capabilities, runtime capabilities, and pack schema capabilities.

The chat therefore contributes a clear design philosophy for a future Dominium/XStack Release Constitution and Spec Book: use strict SemVer where it is true, SemVer-shaped identifiers where they are useful, explicit build provenance for exact artifact identity, manifests as canonical truth, and capability contracts for internal compatibility.

## 2. Chronological Narrative of the Conversation

### 2.1 Initial comparison of versioning systems

The chat began with a broad comparison of Semantic Versioning and other strategies. SemVer was described as `MAJOR.MINOR.PATCH`, with optional prerelease and build metadata. Its purpose is to communicate compatibility of a defined public API. Other schemes were compared against it:

- Calendar Versioning communicates release date or cadence.
- Monotonic/serial versioning communicates order only.
- Marketing versioning communicates customer-facing era or brand.
- Build/revision numbering identifies exact artifacts.
- Git hashes identify exact source states.
- Protocol/schema/API epoch versioning identifies interface contracts.
- Channel/track labels communicate risk, stability, and support class.

This established the central constraint: a versioning scheme should not be judged abstractly; it should be judged by the question it answers.

### 2.2 User concern: versioning drift and “1.x hell”

The user objected to products that change versioning policies halfway through and disliked arbitrary or symbolic versioning. The user also identified a real weakness in SemVer: if a product remains backward compatible for a long time, it can get stuck in `1.x` indefinitely. Conversely, if maintainers want a `2.0`, they may invent or exaggerate a breaking change.

An early answer proposed a four-part public version such as `GEN.EPOCH.FEATURE.PATCH` to avoid SemVer’s compatibility-only major field. This was useful as a conceptual step because it recognized that a product may need to express generation, milestone, ordinary progress, and fixes separately. However, the idea was later revised because XStack already has a separate Global Build Number and build identity system, so the public version does not need to carry every kind of density.

### 2.3 Shift to layered identity

The discussion then shifted toward a broader architecture. Instead of trying to invent one perfect public version number, the model became layered:

- product versions for individual products/components,
- suite versions for curated bundles/distributions,
- GBN for global build identity,
- BII/build ID for structured artifact provenance,
- compatibility axes for APIs, schemas, protocols, saves, plugins, and packs,
- channel/lifecycle metadata for risk and support class,
- target/platform/architecture metadata for artifact compatibility.

This is the point where the conversation stopped treating versioning as a single-number problem.

### 2.4 Product versions and suite versions

The user proposed using stricter SemVer-style component versions and a separate suite/marketing version, similar to historical office-suite models where individual components had separate product numbers. This was accepted as a mature pattern. Suites and components answer different questions:

- a component version says what version of that component/API/product is present;
- a suite version says what coordinated release/bundle/distribution a user downloaded or installed.

The conversation warned against synchronized fake versioning, where every component is forced to `1.2.0` just because the suite is `1.2.0`. That looks tidy but destroys information.

### 2.5 Suite version as meaningful but not strict SemVer

The user wanted the suite number to still encode meaning so that someone who only knows the suite number can infer a lot. The answer was that the suite version can communicate a broad compatibility envelope, release family, release train, or migration scale, but it must not replace the real compatibility metadata.

A possible suite version interpretation discussed was something like `MAJOR.TRAIN.UPDATE`, where:

- major means broad suite generation or era,
- train means coordinated release line or milestone,
- update means curated refresh within that train.

This was not fully finalized, but the direction was clear: the suite version should be human-curated and meaningful, but not strict SemVer.

### 2.6 Broader release identity and compatibility profiles

The conversation then broadened further. A stronger model was proposed: not only product versions and suite versions, but also compatibility profiles. A compatibility profile would summarize the suite-wide contract for save schema, network protocol, plugin/mod API, pack schema, renderer capability, and tooling interop.

This idea later evolved into the capability model. It remains a possible abstraction: either compatibility profiles can be explicit named objects, or they can be generated from declared capabilities.

### 2.7 Products, suites, Setup, packages, and platforms

The user then enumerated standalone products:

- Stack,
- Tools,
- SDK,
- Engine,
- Game,
- Client,
- Server,
- Launcher,
- Setup,
- etc.

The user also enumerated suites:

- All,
- Full,
- Lite,
- Net,
- etc.

The user explained that suite downloads can be full, user, dev, lite, net, etc., and that the Setup product can run standalone/portably and then manage install, repair, uninstall, rollback, upgrade, and migration from bundled files or network sources.

This established Setup as a real product with its own identity, not merely a side-effect of an installer package. It also clarified that a suite download is a curated distribution of products and content, not a single component.

### 2.8 Proposed filename grammar and refinement

The user proposed a filename form like:

```text
Dominium-<product>-<version>-<channel>+<build>-<platform>-<architecture>.extension
```

with examples such as:

```text
Dominium-Full-0.0.0-stable+7137-WinNT10-x86-64.zip
Dominium-Full-0.0.0-stable+7137-MacOSX4-PPC32.zip
Dominium-Full-0.0.1-hotfix+7138-Linux5-ARM64.zip
```

The conversation refined this. First, `stable` should not be encoded as a prerelease suffix, because under SemVer `1.0.0-stable` is actually a prerelease below `1.0.0`. Second, `hotfix` should usually not be encoded as a prerelease suffix. A hotfix should normally be a new patch version plus release-class metadata. Third, the filename should include a `scope`, because `Full` is a suite/distribution while `Engine` is a product.

A stronger filename pattern emerged:

```text
Dominium-<scope>-<id>-<version>-<target>-<arch>-<pkg>.<ext>
```

For example:

```text
Dominium-product-sdk-1.4.0-beta.2+gbn.7137-WinNT10-x86-64-portable.zip
Dominium-product-setup-1.0.1+gbn.7140-WinNT10-x86-64-installer.zip
Dominium-suite-full-0.9.0-rc.1+gbn.7200-WinNT10-x86-64-bundle.zip
```

This remained a proposal rather than a final locked spec.

### 2.9 Platforms and architectures

The user listed possible platform families including DOS5, Win3, Win4, WinNT3/4/5/6/10, classic Mac OS families, macOS families, and Linux kernel major families. The conversation concluded that platform family labels can be useful for humans, but they are not always precise enough to be binary compatibility targets.

The key distinction became:

- **support family**: broad human-facing label such as `WinNT5` or `Linux5`,
- **target baseline**: exact tested binary/runtime/toolchain baseline.

For Windows, the chat warned that Windows 9x, NT4, NT5, NT6, and NT10 are materially different target environments. For Linux, kernel major alone is weak because libc/runtime/toolchain/userland often matter more. For older macOS/classic Mac targets, CPU family, runtime format, and system APIs matter. This remains unresolved because real feasibility requires toolchain testing.

### 2.10 Reset around SemVer 2.0.0

The user asked to start from scratch by explaining SemVer 2.0.0 fully, then adapting it back to XStack. The chat reconstructed SemVer’s rules:

- SemVer requires a declared public API.
- `MAJOR.MINOR.PATCH` has compatibility semantics.
- prerelease identifiers after `-` sort below the corresponding normal version.
- build metadata after `+` does not affect precedence.
- version `0.y.z` is initial development and not stable.
- released artifacts must be immutable.

This became the basis for later choices.

### 2.11 Strict SemVer versus SemVer-shaped identifiers

The user liked strict SemVer for public APIs but also liked the visual look of SemVer for non-SemVer things. The conversation then defined a dual model:

- strict SemVer for true API/contract-bearing components;
- SemVer-shaped release identifiers for end-user products and suites.

This is a core final direction.

Examples preserved:

```text
1.2.3
1.2.3-beta.1
1.2.3-beta.1+gbn.7137
1.2.3-beta.1+sha.deadbeef
```

### 2.12 GBN, BII, channels, and manifests

The chat then answered specific design questions:

- Which entities are true SemVer components?
- Which are suites rather than components?
- How should GBN appear without misusing precedence?
- How should BII be encoded?
- Whether channels belong in prerelease labels, lifecycle metadata, or both.
- How filenames should project metadata without corrupting version semantics.

The answers were:

- true SemVer belongs to public API/contract components;
- suites are distributions, not SemVer components;
- GBN belongs in build metadata and manifests but not ordering semantics;
- BII should primarily be structured manifest metadata;
- `dev/alpha/beta/rc` can be prerelease ordering labels;
- `stable/lts/nightly/internal/hotfix/security/rollback` should be lifecycle/release-class metadata;
- filenames project metadata but do not define semantics.

### 2.13 Knowledge-base summary and preservation package

The user asked for a summary of what had been discussed, decided, and left unresolved. A substantial in-chat knowledge-base summary was produced. Later, the user uploaded a preservation mega-prompt asking for a maximum-fidelity chat preservation package. The response generated multiple files: manifest, human report, context transfer packet, YAML spec sheet, registers, aggregator packet, reader brief, audit file, future bootstrap prompt, in-chat reader, and a ZIP package.

The current turn asks for an accompanying human-readable detailed report and a new single ZIP bundle containing all relevant files. This file is that accompanying report.

### 2.14 Capabilities instead of internal version gating

The final design refinement before preservation was the user’s idea that internally, even though SemVer is used externally where appropriate, compatibility should use capabilities instead of versions. This was endorsed as a stronger model.

The rule became:

```text
versions identify releases;
capabilities decide interoperability;
GBN/BII/hash identify exact artifacts.
```

This is one of the most important conceptual outcomes of the chat.

## 3. Detailed Topic Summary

### Topic 1 — Why versioning policies drift

The chat began from the user’s frustration with versioning systems that change policy midway through a product’s life. The discussion identified the deeper cause: projects often start with one number, then later demand that it encode too many things. A single version string gets asked to represent compatibility, age, marketing era, suite composition, build identity, support status, and exact artifact provenance. That pressure eventually causes policy drift.

The chosen mitigation is not a cleverer single number. It is a layered identity system with stable field meanings.

### Topic 2 — SemVer’s proper role

SemVer was treated as valuable but limited. Its proper role is public API compatibility. It should be used when downstream users can reasonably ask whether an integration, plugin, SDK dependency, CLI script, schema consumer, or API user will still work.

The chat did not reject SemVer. It rejected pretending that SemVer applies to every kind of artifact.

### Topic 3 — Avoiding `1.x` hell and fake major bumps

The user worried that strict SemVer can trap a well-designed compatible product in `1.x` forever. This criticism was accepted as valid for products where users want the version to communicate maturity, era, or product progress. The solution is not fake major bumps. The solution is to avoid using strict SemVer semantics for suite/marketing/product release identifiers unless they actually describe a public API.

### Topic 4 — Product versus suite

A product is a shippable standalone thing such as Engine, Client, Server, Launcher, Setup, SDK, Tools, Game, or Stack. A suite is a curated distribution such as All, Full, Lite, Net, User, or Dev. Products and suites can both have versions, but the meanings differ.

Products may be strict SemVer if they expose real contracts. Suites should be human-facing release identities for bundles of products and content.

### Topic 5 — GBN and build identity

GBN is useful because it gives dense, global, monotonic identity for CI/build outputs. It is excellent for support, audit, artifact provenance, rollback, and logs. It should appear in build metadata or manifests, for example `+gbn.7137`.

However, GBN must not be used as SemVer precedence. In SemVer, build metadata after `+` is ignored for ordering. Therefore, if two artifacts have the same core version and differ only in `+gbn`, they are distinct artifacts but not different SemVer precedence levels.

### Topic 6 — BII/build identification

BII is better as structured metadata than as a long string crammed into a version. It may include build lane, target, architecture, configuration, package kind, CI/local status, and other provenance fields. A compact BII token can appear in filenames if needed, but the canonical BII should live in the manifest.

### Topic 7 — Channels and lifecycle labels

The chat split channel semantics into two concepts.

Prerelease ordering labels can live inside the version:

- `dev.N`,
- `alpha.N`,
- `beta.N`,
- `rc.N`.

Lifecycle/support/release-class labels should live outside the version:

- stable,
- LTS,
- nightly,
- internal,
- archival,
- hotfix,
- security,
- rollback.

This prevents SemVer ordering errors such as `1.0.0-stable` being treated as prerelease.

### Topic 8 — Filename grammar and package identity

Filenames should be deterministic and readable, but not the canonical source of truth. The proposed filename grammar is:

```text
Dominium-<scope>-<id>-<version>-<target>-<arch>-<pkg>.<ext>
```

This includes:

- `scope`: product or suite,
- `id`: engine, setup, full, net, etc.,
- `version`: already-formed release identifier,
- `target`: support family or target family,
- `arch`: architecture,
- `pkg`: portable, installer, bundle, pack, symbols, source, etc.

The manifest must include the exact baseline and detailed build identity.

### Topic 9 — Platforms, targets, and architectures

The user proposed many OS families and architecture families. The chat accepted the value of broad family labels but warned against overclaiming binary compatibility.

The durable model is:

- support family: broad human label,
- target baseline: exact tested system/runtime/toolchain contract,
- architecture: CPU architecture,
- runtime/toolchain profile: compiler/libc/CRT/API assumptions.

This is still unresolved and requires actual feasibility testing.

### Topic 10 — Capabilities and internal compatibility

The final technical refinement was to use capabilities internally. Capability compatibility is better than version-gating when systems have backports, optional features, partial implementations, old-platform variants, plugin surfaces, save schemas, pack schemas, network protocols, and multiple products.

A capability model might use declarations such as:

```yaml
provides:
  - save.schema@5
  - plugin.host@2
  - net.protocol@3
  - renderer.software.basic
requires:
  - runtime.winnt10.x86-64
  - pack.schema@4
```

This is not yet formalized, but it is a high-value direction.

## 4. Decisions and Their Status

### Firm or near-firm accepted directions

1. **Use layered identity, not one universal version string.**  
   This is the central design direction.

2. **Use strict SemVer only for declared public API/contract components.**  
   This is the strongest SemVer decision.

3. **Allow SemVer-shaped identifiers for non-SemVer products/suites.**  
   The shape is useful, but the semantics must be honest.

4. **Do not encode stable as `-stable`.**  
   Plain `1.2.3` is the stable release form.

5. **Do not encode normal hotfixes as `-hotfix`.**  
   A hotfix should normally be a patch release plus release-class metadata.

6. **GBN is provenance, not SemVer precedence.**  
   It can appear in `+gbn.7137`, but ordering requires version/pre-release changes.

7. **Filenames are projections; manifests are canonical.**  
   Filename fields help humans and scripts, but the manifest is truth.

8. **Separate prerelease labels from lifecycle/support metadata.**  
   This avoids semantic errors and future drift.

### Tentative or not fully formalized directions

1. **Suite version fields.**  
   The suite version should be human-curated and meaningful, but exact semantics of `X.Y.Z` remain unresolved.

2. **BII schema.**  
   BII should be structured metadata, but the exact fields are not final.

3. **Target taxonomy.**  
   Support family versus exact baseline is accepted, but the full taxonomy is not final.

4. **Capability registry.**  
   Capabilities are a strong direction, but the namespace, versioning, negotiation, and validation rules remain to be designed.

5. **Compatibility profiles.**  
   It is unclear whether named compatibility profiles should exist separately or be generated from capability sets.

## 5. Things Put Off for Later

The chat deliberately deferred several tasks because they require formal design, repo inspection, or user decisions.

### 5.1 Release Constitution

A short, permanent document should define:

- all identity fields,
- what each field means,
- which fields affect precedence,
- which fields are human-facing,
- which fields are machine-facing,
- the rule that field meanings must not be reinterpreted later.

### 5.2 SemVer Component Inventory

Every entity should be classified:

- strict SemVer component,
- SemVer-shaped product release identifier,
- suite/distribution release identifier,
- build/provenance field,
- compatibility/capability contract,
- artifact/package type.

### 5.3 Suite Version Policy

The suite version needs exact semantics. Possible model:

```text
MAJOR.TRAIN.UPDATE
```

but this was not finalized. The user must decide what changes require each field to bump.

### 5.4 Build Identity Spec

GBN and BII need a formal spec covering:

- local builds,
- CI builds,
- public builds,
- internal builds,
- git SHA,
- dirty working tree status,
- build lane,
- build kind,
- target,
- package kind,
- manifest fields,
- UI/log display.

### 5.5 Channel and Lifecycle Spec

The project needs a vocabulary and rules for:

- dev,
- alpha,
- beta,
- rc,
- stable,
- lts,
- nightly,
- internal,
- archival,
- hotfix,
- security,
- rollback.

### 5.6 Artifact Naming Spec

The filename grammar should be formalized with allowed values, case rules, separators, escaping rules, and examples.

### 5.7 Release Manifest Schema

The manifest should become canonical. It should include suite/product identity, version, GBN, BII, build hash, target baseline, architecture, package kind, lifecycle, release class, compatibility/capabilities, included component versions, and checksums.

### 5.8 Target Taxonomy

The project needs a table of supported platforms and exact baselines. This includes deciding whether labels such as DOS5, Win4, WinNT5, MacOSX4, and Linux5 are support families, binary targets, or both.

### 5.9 Capability Registry

The internal compatibility model should define capability namespaces, versions, required/provided semantics, optional capabilities, negotiation rules, migration rules, and conflict rules.

## 6. Risks and Failure Modes

### Risk 1 — Future assistant treats everything as strict SemVer

This would erase one of the main decisions. The correct model is strict SemVer only where there is a public contract. Suites and many products may use SemVer-shaped identifiers without strict SemVer semantics.

### Risk 2 — GBN is treated as version ordering

This is incorrect under SemVer if GBN appears in build metadata. GBN is excellent for provenance but not SemVer precedence.

### Risk 3 — Stable or hotfix are put back into prerelease labels

`1.2.3-stable` and `1.2.3-hotfix` were rejected for normal releases. Stable is plain `1.2.3`; hotfix is usually `1.2.4` plus metadata.

### Risk 4 — Filename becomes canonical truth

Filenames are projections. The manifest is the canonical artifact record.

### Risk 5 — Platform families overclaim compatibility

Broad labels such as WinNT5 or Linux5 can be helpful but may be misleading if used as exact binary claims.

### Risk 6 — Capability system becomes string soup

Capabilities need governance. They should have namespaces, owners, versioning rules, and validation, not arbitrary undocumented strings.

### Risk 7 — Tentative suggestions become formal requirements too early

Some ideas are strong but not final, especially suite version field semantics, BII schema, target taxonomy, and compatibility profile/capability design.

## 7. What Was Actually Done in This Chat

The chat produced:

1. a conceptual comparison of versioning systems;
2. a layered release identity model;
3. a distinction between strict SemVer and SemVer-shaped identifiers;
4. a product-versus-suite classification model;
5. preliminary classification of Dominium/XStack products and suites;
6. guidance on GBN, BII, channels, lifecycle, filenames, packages, targets, architectures, and manifests;
7. a capability-based internal compatibility direction;
8. an in-chat knowledge-base summary;
9. a maximum-fidelity preservation package with multiple markdown/YAML files and a ZIP;
10. this additional accompanying detailed human report;
11. a new bundle manifest and verification file;
12. a new complete ZIP containing the existing handoff files, prior ZIP, source prompt, and this report.

## 8. What the Next Assistant Should Understand Immediately

A future assistant should not restart the debate from “SemVer versus CalVer.” That was already explored. The current design direction is layered identity.

The future assistant should also not say “just use SemVer everywhere.” That was explicitly rejected. The correct distinction is:

```text
Strict SemVer: public API/contract components.
SemVer-shaped release IDs: products and suites where useful.
GBN/BII/hash: artifact provenance.
Manifests: canonical artifact truth.
Capabilities: internal compatibility truth.
```

The next useful action is to draft the Release Constitution and SemVer Component Inventory.

## 9. Best Next Work Product

The strongest next deliverable is probably a document titled:

```text
Dominium/XStack Release Identity Constitution v0.1
```

It should include:

1. entity classes,
2. version classes,
3. SemVer rules,
4. SemVer-shaped release identifier rules,
5. suite version semantics,
6. GBN rules,
7. BII rules,
8. channel/lifecycle rules,
9. artifact filename grammar,
10. manifest schema outline,
11. target taxonomy outline,
12. capability registry outline,
13. examples,
14. anti-patterns,
15. migration path from current build system.

## 10. Quick Memory Capsule

The chat decided that Dominium/XStack should use a layered release identity model. Strict SemVer 2.0.0 should apply only to components with declared public APIs/contracts. User-facing products and suites may use SemVer-shaped release identifiers like `1.2.3`, `1.2.3-beta.1`, and `1.2.3+gbn.7137`, but should not falsely claim strict SemVer if they are not API contracts. GBN is exact build provenance, not precedence. BII is structured build identity and should primarily live in manifests. `stable` should not be encoded as `-stable`; hotfixes should normally be patch releases with metadata, not `-hotfix`. Prerelease labels and lifecycle/support labels are separate. Products and suites are different entity classes. Filenames are metadata projections; manifests are canonical. Platform support needs support families and exact target baselines. Internally, compatibility should be handled by capability contracts rather than version ranges alone. The main unresolved work is to formalize this into a Release Constitution, component inventory, suite version policy, build identity spec, artifact naming spec, target taxonomy, manifest schema, and capability registry.

## 11. Verification Checklist

Before this becomes a formal project spec, verify:

- current XStack/RepoX build scripts and how GBN is actually generated;
- current BII/build_id fields and naming conventions;
- current product/suite inventory;
- current packaging outputs;
- existing platform target assumptions;
- actual compiler/runtime feasibility for legacy OS targets;
- whether existing docs already define compatibility fields;
- whether suite version semantics already exist somewhere;
- whether capability-like declarations already exist in code/config;
- whether artifact manifests already exist and what format they use.

## 12. Bundle Notes

This report is intended to accompany the existing preservation package. The fresh complete ZIP should include:

- the earlier manifest,
- the earlier full human-readable report,
- the context transfer packet,
- the YAML spec sheet,
- the registers,
- the aggregator packet,
- the reader brief,
- the verification/audit file,
- the future-chat bootstrap prompt,
- the in-chat reader,
- the earlier handoff ZIP,
- the uploaded source prompt copied under a clearer name,
- this accompanying detailed human report,
- the new bundle manifest and verification file.

The existing earlier files remain useful. This new report is not a replacement for the structured registers or spec sheet. It is a human-readable companion that retells the conversation and its conclusions in a more linear explanatory form.
