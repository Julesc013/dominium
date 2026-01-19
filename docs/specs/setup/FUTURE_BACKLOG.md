# Setup Deferred / Non-Binding Backlog

This backlog is Deferred / Non-Binding. It documents ideas only and makes no
promises. Setup is complete without these items.

## Kernel-Level Ideas (Deferred)

### Job DAG parallelism (safe subsets only)
- Description: allow parallel execution for independent job subgraphs where safety
  and determinism are provable.
- Why not required now: correctness and resumability are satisfied with the
  current sequential job engine.
- Invariants: deterministic planning, resumable journals, no in-place mutation,
  stable audit emission, kernel remains OS-API-free.
- Blocking prerequisites: explicit dependency annotations and a deterministic
  parallel scheduler model.

### Stronger cryptographic digests (optional upgrade path)
- Description: add an optional stronger digest algorithm for artifacts and plans
  while keeping existing digest64 for compatibility.
- Why not required now: current digest64 is sufficient for SR-0..SR-11 scope and
  deterministic tests.
- Invariants: skip-unknown TLV fields, deterministic outputs, schema versioning.
- Blocking prerequisites: agreed algorithm choice and migration strategy.

### Signed manifest verification (offline trust roots)
- Description: verify manifest signatures using offline trust roots to prevent
  tampering.
- Why not required now: manifests are currently trusted inputs in offline
  workflows.
- Invariants: no network dependency, deterministic behavior, audit must record
  verification results.
- Blocking prerequisites: key distribution policy and trust root storage format.

### Content-addressed artifact cache
- Description: cache artifacts by digest to avoid re-downloading or re-staging.
- Why not required now: current staging model is sufficient and avoids cache
  invalidation complexity.
- Invariants: no in-place mutation, deterministic planning, sandbox enforcement.
- Blocking prerequisites: cache layout spec and eviction policy.

### Plan diffing and impact visualization
- Description: produce deterministic diffs between two plans for operator review.
- Why not required now: audits and digests already support verification of plan
  identity.
- Invariants: deterministic outputs, no side effects, audit completeness.
- Blocking prerequisites: stable plan diff format and tooling.

## Adapter-Level Ideas (Deferred)

### MSIX wrapper (launcher-only)
- Description: add an MSIX package wrapper that launches Setup for installation.
- Why not required now: Windows EXE + MSI wrappers cover current installer needs.
- Invariants: adapters remain thin, no install logic duplication, request TLV
  generated deterministically.
- Blocking prerequisites: MSIX packaging policy and signing requirements.

### Flatpak/AppImage wrappers
- Description: provide Linux distribution wrappers that call Setup for planning
  and state management.
- Why not required now: deb/rpm wrappers are sufficient for supported platforms.
- Invariants: ownership model separation, no external downloads, deterministic
  request emission.
- Blocking prerequisites: packaging policy and sandbox integration rules.

### Winget/Chocolatey metadata generation
- Description: generate catalog metadata for Windows package managers.
- Why not required now: distribution is managed by direct installers.
- Invariants: no network dependency at install time, stable metadata generation.
- Blocking prerequisites: registry metadata schema mapping and release pipeline
  integration.

### Advanced Steam verify/repair mapping
- Description: map Setup verify/repair to Steam depots and validation routines.
- Why not required now: Steam provider is stubbed and does not require deep
  integration yet.
- Invariants: deterministic audit, no external network calls during install.
- Blocking prerequisites: Steam API integration policy and offline behavior plan.

## Operator Tooling (Deferred)

### Interactive audit explorer
- Description: a local UI for browsing audit entries and refusal reasons.
- Why not required now: CLI dumps already provide deterministic audit output.
- Invariants: audit data remains the source of truth, no schema changes.
- Blocking prerequisites: stable audit query schema.

### Graphical plan visualizer
- Description: visualize plan steps, components, and intents for review.
- Why not required now: plan TLV and JSON dumps already provide full data.
- Invariants: deterministic data rendering, no plan mutation.
- Blocking prerequisites: visual format spec.

### Support bundle exporter (plan+state+journal+audit)
- Description: bundle forensic artifacts for support triage.
- Why not required now: scripts already collect artifacts deterministically.
- Invariants: no data loss, no mutation of source files.
- Blocking prerequisites: retention policy and bundle format.

## Policy/Process (Deferred)

### Formal compatibility promises per schema version
- Description: publish explicit compatibility guarantees per TLV schema version.
- Why not required now: schema freeze v1 already defines forward-compatibility.
- Invariants: skip-unknown safety and deterministic parsing.
- Blocking prerequisites: legal/policy review of compatibility guarantees.

### Long-term artifact notarization strategy
- Description: define notarization policy for archives and manifests.
- Why not required now: offline, deterministic install is the primary target.
- Invariants: no network dependency at install time, audit visibility.
- Blocking prerequisites: signing authority and retention requirements.

### Public documentation export formats
- Description: publish docs in additional formats (PDF, offline bundles).
- Why not required now: repository docs already cover the required content.
- Invariants: docs remain source of truth, no content drift.
- Blocking prerequisites: approved export pipeline and format standards.
