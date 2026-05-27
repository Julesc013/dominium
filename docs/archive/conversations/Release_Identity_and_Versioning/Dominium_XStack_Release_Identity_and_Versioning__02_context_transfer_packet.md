# 29. Context Transfer Packet for a Future Chat — Dominium XStack Release Identity and Versioning

## 29.1 Ultra-Condensed Bootstrap Brief

This retired/old chat developed Dominium/XStack's release identity and versioning doctrine. The user dislikes products that change versioning policies halfway through and wanted a durable system that avoids SemVer `1.x` stagnation, arbitrary major bumps, and overloaded version strings. The central conclusion is that Dominium/XStack should use a layered release identity architecture rather than one universal version number.

Strict SemVer 2.0.0 should apply only to entities with declared public APIs or compatibility contracts. Strong candidates include SDKs, engine libraries, protocol/schema/plugin surfaces, reusable runtime libraries, and stable CLI/API tools. End-user products and suites may use the same visual shape, `X.Y.Z[-pre][+build]`, but must be documented as product/suite release identifiers, not strict SemVer compatibility promises unless they truly have a public API contract.

Products and suites are separate. Products include Stack, Tools, SDK, Engine, Game, Client, Server, Launcher, and Setup. Suites/distributions include All, Full, Lite, Net, User, Dev, etc. Metadata should include `scope=product|suite` and `id=...`. Suite versions should be human-curated, consumer-facing release identities. They may imply broad release family/train/update meaning, but exact compatibility belongs in explicit metadata.

GBN is exact CI/public/internal build provenance and may appear in SemVer build metadata such as `+gbn.7137`, but it must not be used as SemVer precedence. Git SHA may identify local builds, e.g. `+sha.deadbeef`. BII should primarily live as structured manifest metadata, with optional compact filename/build metadata projection.

Channels are split. `dev`, `alpha`, `beta`, and `rc` can be prerelease ordering labels. `stable`, `lts`, `nightly`, `internal`, `archival`, `hotfix`, `security`, and `rollback` should usually be lifecycle/support/release-class metadata. Do not use `-stable` or `-hotfix` as ordinary release suffixes.

Filenames are projections, not truth. Preferred pattern: `Dominium-<scope>-<id>-<version>-<target>-<arch>-<pkg>.<ext>`. Manifests are canonical and should include versions, GBN, BII, target family, target baseline, arch, runtime/toolchain profile, package kind, lifecycle, release class, capabilities/contracts, and suite membership.

Platform taxonomy remains open. The chat distinguished support families from exact binary target baselines. Linux kernel major alone is not enough. Old Windows/macOS/DOS targets need careful tested baselines.

The final refinement was capability-based internal compatibility: versions identify releases, capabilities/contracts decide interoperability. Examples: `save.schema@5`, `plugin.host@2`, `net.protocol@3`. This is a strong tentative direction requiring a formal capability registry and resolver rules.

## 29.2 Source Hierarchy

1. Direct user statements in this chat.
2. Explicit decisions accepted or echoed by the user.
3. Current task register.
4. Constraint register.
5. Artifact ledger.
6. Inferences from repeated discussion.
7. Assistant suggestions not accepted by the user.
8. General model knowledge.

## 29.3 Operating Rules for Future Assistants

- Preserve FACT / INFERENCE / UNCERTAIN / PROJECT-CONTEXT labels.
- Do not assume access to the old chat beyond this packet.
- Do not re-ask questions answered here unless the answer is ambiguous or stale.
- Verify external/toolchain/repo facts before relying on them.
- Do not treat tentative capability/profile/platform ideas as final.
- Do not collapse the layered model into SemVer everywhere.
- Do not use GBN as SemVer precedence.
- Keep manifests canonical and filenames as projections.
- Use structured outputs when continuing spec work.

## 29.4 Active Workstreams

See Workstream Register. Active workstreams: versioning doctrine, SemVer component classification, suite identity, GBN/BII integration, channels/lifecycle, artifact naming/manifest schema, target taxonomy, capability compatibility, and Setup role.

## 29.5 Current Priorities

1. Draft Release Constitution.
2. Classify all entities by versioning class.
3. Define suite X.Y.Z semantics.
4. Formalize GBN/BII.
5. Define capability/contract model.

## 29.6 Current Open Questions

See Open Questions Register. Main unresolved issues: strict SemVer inventory, suite semantics, BII schema, artifact filename grammar, manifest schema, target taxonomy, and capability-profile relationship.

## 29.7 Recommended First Action

Create the Release Constitution plus SemVer Component Inventory. That will anchor all later naming, packaging, manifest, and capability work.
