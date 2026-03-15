Status: DERIVED
Last Reviewed: 2026-03-14
Stability: provisional
Future Series: GOVERNANCE/RELEASE
Replacement Target: release-pinned governance profile and signed publication bundles

# Governance Model

## Project Parts

- Domino Engine: deterministic simulation core.
- Dominium Game layer: rule meaning and pack-driven behavior.
- Applications: client, server, setup, launcher, and tools.
- Pack formats and schemas: open specification surface.
- Protocols: CAP-NEG, IPC, pack-compat, and related interop contracts.
- Documentation and specs: canonical and derived docs.
- Release indices and manifests: offline-first release metadata.
- Trust root list: signer publication and policy surface.

## Governance Modes

### Fully Open

- Engine, game, and apps may all ship as open source.
- Schemas, protocols, and pack formats remain open.
- Packs may be fully open or mixed, subject to trust and redistribution policy.

### Core Closed, Ecosystem Open

- Engine and game may be closed source.
- Applications may remain open or partially open.
- Schemas, protocols, and pack formats remain open.
- Third-party packs and alternate release indices remain allowed.

### Mixed / Split Licensing

- Engine or game may be closed independently.
- Apps may remain open.
- Schemas, protocols, and pack formats remain open.
- Commercial packs may exist alongside open packs.

## Official vs Third-Party

- Official means both:
  - signed by an official trust root, when signatures are required by policy
  - present in an official release index
- Third-party ecosystems may publish their own:
  - trust roots
  - release indices
  - pack naming conventions
  - redistribution rules

## Namespacing And Fork Policy

- Pack identifiers remain namespaced and must not impersonate official namespaces.
- Forked release indices must not reuse an official signer id.
- Official suite tags use `v<semver>-<channel>`.
- Forks using the same suite version line must use `fork.<org>.v<semver>-<channel>`.

## Commercial Feature Gating

- Commercial gating must be capability-based and trust-based.
- Paid features may ship through signed packs and/or license artifacts.
- Enforcement must route through TRUST policy, mod policy, and CAP-NEG.
- Security by obscurity is not an accepted governance mechanism.

## Archive And Extinction Prevention

- Release indices and release manifests must be archived immutably.
- Artifact hashes remain canonical and content-addressed.
- Open-source source archives, when applicable, should be stored alongside the release manifest.
- Mirror policy:
  - primary archive
  - at least one secondary mirror
  - offline cold storage recommended

## Governance Changes

- Governance mode changes must bump `governance_version`.
- Governance mode changes must update trust root publication state.
- Governance mode changes must publish migration notes for release consumers and ecosystem forks.
