# Dominium / Domino

Dominium is a deterministic, contract-governed simulation game and operating
environment built on the Domino deterministic substrate.

The project is about invention, production, logistics, economics, settlement,
trust, communication, and institutional power emerging from lawful simulation
rather than scripted outcomes. Commands, processes, packs, capabilities,
diagnostics, evidence, and replay proof are first-class surfaces. Invalid action
must refuse explicitly; hidden fallback behavior is not part of the model.

## Home Point

Use this README as the project home point. It orients the product, repository,
and common proof commands. It is not the highest authority.

Authority starts here:

- Canon: `docs/canon/constitution_v1.md`
- Glossary: `docs/canon/glossary_v1.md`
- Agent governance: `AGENTS.md`
- Canon index: `docs/architecture/CANON_INDEX.md`
- Current queue: `.aide/queue/current.toml`
- Foundation status: `docs/repo/FOUNDATION_LOCK.md`
- Build guide: `docs/development/guides/BUILDING.md`
- Test tiers: `contracts/testing/test_tiers.contract.toml`
- Public surface registry: `contracts/public_surface/public_surface.contract.toml`

Repo artifacts outrank chat memory, generated echoes, convenience summaries, and
old planning notes.

## Current State

Current committed program position:

- Foundation Lock: `PASS_WITH_WARNINGS`.
- Post-wave queue state: `post_wave_1_pass_with_warnings`.
- Completed narrow Workbench validation slice:
  `WORKBENCH-VALIDATION-SLICE-01`.
- Current next task: `COMMAND-RESULT-VIEW-SLICE-01`.
- Alternate next task: `PACKAGE-MOUNT-SLICE-01`.
- Secondary follow-up: `POINTER-WIDTH-SERIALIZATION-AUDIT-01`.

The current queue does not authorize broad feature work. Broad Workbench UI,
runtime module loading, provider runtime, package runtime, gameplay, renderer
implementation, native GUI, and release publication remain blocked until later
reviewed phases explicitly open them.

## What This Is

Domino is the reusable deterministic substrate: execution, ordering, storage,
replay, ABI-facing boundaries, and other engine mechanisms.

Dominium is the official game, product, and domain layer on top of Domino. It
defines rules, process meaning, law targets, domain interpretation, authored
content use, and product composition.

Workbench is the richest operator environment for validation, evidence,
inspection, and later editing workflows. It consumes the same contracts and
services as other products; it is not an authority layer.

AIDE and Codex are repo/control-plane harnesses and bounded patch execution
surfaces. They help operate the repository; they do not replace canon,
contracts, validation, or evidence.

## What This Is Not

Dominium is not a monolithic game executable, a renderer-owned simulation, a
traditional mode-flag game, a silent fallback system, or a place where generated
output becomes source truth by convenience.

It is also not currently release-ready. Full CTest and broader release/trust
proof remain visible debt outside the normal fast strict development gate.

## Core Invariants

- Determinism first: identical canonical inputs produce identical authoritative
  outputs.
- Process-only mutation: authoritative truth changes only through lawful,
  deterministic Process execution.
- Truth / perceived / render separation: truth is authoritative; perception is
  law-filtered; rendering is presentation only.
- Profiles over mode flags: behavior composition comes from profiles, bundles,
  law surfaces, and constraints, not hardcoded runtime mode forks.
- Explicit refusal: unsupported or invalid transitions return deterministic,
  auditable refusal.
- Pack-driven integration: optional content and capabilities are declared by
  packs, contracts, registries, and compatibility law.
- Public identity is contractual: paths and implementations are not public
  surfaces unless registered as such.

## Semantic Spine

The reusable truth is not a button, screen, renderer, or tool. The reusable truth
is the contract-governed surface:

```text
intent
-> command
-> capability/refusal check
-> service or deterministic process
-> result | document | snapshot
-> diagnostics/evidence
-> view/action model
-> projection
-> shell
```

CLI, text/TUI, rendered GUI, native GUI, headless reports, Workbench panels, CI,
and AIDE should project the same command/result/refusal/diagnostic/evidence
truth rather than inventing separate product behavior.

## Product Shape

- `apps/client/`: client product composition, input, perception, and
  presentation shell.
- `apps/server/`: authoritative server product composition and admin/headless
  surfaces.
- `apps/launcher/`: profiles, instances, compatibility, and launch
  orchestration.
- `apps/setup/`: install, repair, rollback, and local product configuration.
- `apps/workbench/`: governed validation, evidence, inspection, and later
  authoring workflows.
- `tools/`: validators, migration tools, packaging helpers, codegen, audit, and
  developer machinery.

Apps compose. Runtime implements reusable behavior. Contracts define law.
Content supplies authored payload. Tools validate, generate, migrate, and audit.

## Repository Map

- `apps/`: thin product entrypoints and product composition.
- `engine/`: Domino deterministic substrate and public engine-facing surfaces.
- `game/`: Dominium domain rules, process emission, and game interpretation.
- `runtime/`: AppShell, platform, shell, UI/projection adapters, diagnostics,
  storage, input, audio, network, and host integration.
- `contracts/`: machine-readable, version-pinned, compatibility-sensitive law.
- `content/`: authored packs, profiles, datasets, fixtures-as-content, assets,
  templates, and source content payloads.
- `docs/`: canon, architecture, development, reference, planning, release, and
  repo documentation.
- `tests/`: contract, invariant, smoke, integration, fixture, and proof suites.
- `tools/`: repo-only validation, packaging, migration, release, audit, and
  developer tooling.
- `archive/`: historical, superseded, quarantined, or provenance-retained
  material.

Ownership-sensitive split reminders:

- Do not infer ownership from similarly named roots.
- Follow `AGENTS.md` and scope-specific contract/planning artifacts before
  binding new work to transitional, projected, or quarantined roots.
- Generated outputs are evidence unless a stronger source promotes them.

## Language And Platform Baseline

Mainline source uses:

- C17 for C code.
- C++17 for C++ code.
- C-compatible public ABI boundaries for stable binary-facing surfaces.

The active portability floor includes Windows 7 SP1, macOS 10.9.5, and Linux.
C++17 language mode is allowed, but public ABI surfaces do not expose C++
classes, STL types, exceptions, RTTI, allocator objects, or compiler object
layout.

See:

- `docs/development/LANGUAGE_BASELINE.md`
- `docs/development/C17_USAGE_POLICY.md`
- `docs/development/CPP17_USAGE_POLICY.md`
- `docs/development/MACOS_10_9_CPP17_LIBRARY_SUBSET.md`
- `contracts/abi/c_api.contract.toml`
- `contracts/abi/language_boundary.contract.toml`

## Build And Verify

Configure and build the normal verify preset:

```powershell
cmake --preset verify
cmake --build --preset verify --target ALL_BUILD
```

Run the normal development proof gate:

```powershell
py -3 tools/test/run_fast_strict.py --repo-root .
```

Run AIDE local health checks:

```powershell
py -3 .aide/scripts/aide_lite.py doctor
py -3 .aide/scripts/aide_lite.py validate
```

Run targeted contract validators as needed:

```powershell
py -3 tools/validators/repo/check_dependency_directions.py --repo-root . --strict
py -3 tools/validators/contracts/check_command_surface.py --repo-root . --strict
py -3 tools/validators/contracts/check_module_descriptors.py --repo-root . --strict
py -3 tools/validators/contracts/check_diagnostics_registry.py --repo-root . --strict
```

Fast strict is the normal development gate. Extended, release, and full proof
tiers are separate gates defined by `contracts/testing/test_tiers.contract.toml`.
A green fast strict result does not claim full certification.

## Contracts And Public Surfaces

Public identity must be registered and versioned. A file path, implementation,
or generated artifact is not public merely because it exists.

Core contract entrypoints:

- Public surfaces: `contracts/public_surface/public_surface.contract.toml`
- Commands: `contracts/command/command_surface.contract.toml`
- Views: `contracts/view/view_surface.contract.toml`
- Diagnostics: `contracts/diagnostics/diagnostic_code.registry.json`
- Refusals: `contracts/refusal/refusal_code.registry.json`
- Capabilities: `contracts/capability/capability.registry.json`
- Modules: `contracts/module/module_surface.contract.toml`
- Providers: `contracts/provider/provider.contract.toml`
- Services: `contracts/service/service.contract.toml`
- Project graph: `contracts/project_graph/project_graph_model.contract.toml`
- Packages and packs: `contracts/package/`
- Replay proof: `contracts/replay/`

When behavior or compatibility meaning changes, update the relevant contract
surface and proof in the same task.

## Content, Packs, And Modding

Content is authored data, not runtime law. Packs and registries describe optional
content, capabilities, compatibility, activation, and distribution surfaces.
Missing optional content must degrade or refuse explicitly.

Start with:

- `MODDING.md`
- `content/README.md`
- `content/packs/README.md`
- `contracts/package/packs/README.md`
- `contracts/capability/README.md`

Early pack tiers should remain data-first. Arbitrary executable code in packs is
not part of the current trust model.

## Documentation Map

Use canon and contracts first, then architecture and development docs for
implementation guidance.

- Product overview: `DOMINIUM.md`
- Documentation root: `docs/README.md`
- Canonical system map: `docs/architecture/CANONICAL_SYSTEM_MAP.md`
- Services and products: `docs/architecture/SERVICES_AND_PRODUCTS.md`
- Foundation status: `docs/repo/FOUNDATION_LOCK.md`
- Current queue: `.aide/queue/current.toml`
- Workbench validation slice: `docs/repo/audits/WORKBENCH_VALIDATION_SLICE_01.md`
- Document/patch transactions: `docs/architecture/document_patch_transaction.md`
- Project graph service: `docs/architecture/project_graph_service.md`
- Build matrix: `docs/development/BUILD_MATRIX.md`
- Build guide: `docs/development/guides/BUILDING.md`

Old docs are retained for provenance, but canon, glossary, AGENTS, active
contracts, current queue state, and reviewed audits outrank stale references.

## Contributing

Before substantive work, identify the governing class and authority documents.
Use the task invocation shape from `AGENTS.md`:

```text
Task:
Goal:
Touched Paths:
Relevant Invariants:
Contracts/Schemas:
Validation Level: FAST | STRICT | FULL
Expected Artifacts:
Non-Goals:
```

For ordinary bounded work:

1. Read the relevant canon, contract, and ownership documents.
2. Keep edits in the owning root.
3. Update contracts/schemas when behavior or compatibility meaning changes.
4. Run targeted validation plus `git diff --check`.
5. Run fast strict when scope warrants it or when claiming gate status.
6. Report what was run and what was not run.

See `CONTRIBUTING.md` for contributor workflow notes, but resolve conflicts
against canon, glossary, AGENTS, and active contracts.

## License And Security

- License: `LICENSE.md`
- Security policy: `SECURITY.md`
