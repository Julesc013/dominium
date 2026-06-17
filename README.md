# Dominium / Domino

**A deterministic, contract-governed simulation engine and game platform.**

Dominium is a governed simulation-game project built on Domino, a deterministic
substrate for lawful execution, replay, evidence, and public surfaces. It is for
people interested in simulation systems where commands, contracts, refusals,
content packs, diagnostics, and projections are explicit parts of the design
rather than hidden UI or renderer behavior.

The project is about invention, production, logistics, economics, settlement,
trust, communication, and institutional power emerging from lawful simulation
instead of scripted outcomes.

## Current Status

Dominium is **not release-ready** and should not be read as a playable public
game today. The repository has passed its Foundation Lock with warnings and is
currently advancing through narrow governed product-spine slices.

For the maintained status page, see `docs/STATUS.md`. For planned sequencing,
see `docs/ROADMAP.md`.

## Authority Model

This README is the public front door. It orients readers, but it is not the
highest authority.

Authority starts here:

1. `docs/canon/constitution_v1.md`
2. `docs/canon/glossary_v1.md`
3. `AGENTS.md`
4. Active contracts, registries, current queue state, and reviewed audits
5. Architecture and development docs
6. This README and other derived public summaries
7. Archive and old planning material, for provenance only

Repo artifacts outrank chat memory, generated echoes, convenience summaries,
and old planning notes.

## What This Is

Dominium has four related layers:

| Name | Role |
|---|---|
| **Domino** | The reusable deterministic substrate: execution, ordering, storage, replay, ABI-facing boundaries, and engine mechanisms. |
| **Dominium** | The official game, product, and domain layer on top of Domino. It defines rule meaning, process meaning, content use, and product composition. |
| **Workbench** | The governed operator environment for validation, evidence, inspection, and later authoring workflows. It is not an authority layer. |
| **AIDE / XStack** | Repo and control-plane harnesses for bounded patch execution. They help operate the repository; they do not replace canon, contracts, validation, or evidence. |

Dominium is therefore both a game project and an engine/platform project. The
long-lived rule is that product behavior should be expressed through commands,
contracts, diagnostics, refusals, evidence, and projection surfaces rather than
through ad hoc runtime shortcuts.

## What This Is Not

Dominium is not currently:

- a finished game release
- a monolithic game executable
- a renderer-owned simulation
- a traditional mode-flag game
- a silent fallback system
- a place where generated output becomes source truth by convenience
- a mod platform that accepts arbitrary executable pack code
- a public promise that all planned systems are implemented today

Full CTest and broader release/trust proof remain visible debt outside the
normal fast strict development gate.

## Core Idea

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

Every public interface should project the same command/result/refusal/diagnostic
truth. CLI, text/TUI, rendered GUI, native GUI, Workbench panels, CI, and AIDE
should not invent separate product behavior.

## Architecture At A Glance

```text
                 public readers / users / contributors
                                │
                                ▼
                      README and public docs
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                         Product layer                           │
│ apps/client  apps/server  apps/launcher  apps/setup  workbench  │
└───────────────────────────────┬─────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                  Command / result / refusal spine               │
│ commands  capabilities  diagnostics  evidence  projections      │
└───────────────────────────────┬─────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Domino deterministic substrate               │
│ execution  ordering  storage  replay  ABI boundaries            │
└───────────────────────────────┬─────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Contracts, content, tests, tools             │
│ registries  packs  schemas  validators  audits  AIDE queue      │
└─────────────────────────────────────────────────────────────────┘
```

The deeper map is in `docs/ARCHITECTURE.md` and
`docs/architecture/CANONICAL_SYSTEM_MAP.md`.

## Core Invariants

- **Determinism first:** identical canonical inputs produce identical
authoritative outputs.
- **Process-only mutation:** authoritative truth changes only through lawful,
deterministic Process execution.
- **Truth / perceived / render separation:** truth is authoritative; perception
is law-filtered; rendering is presentation only.
- **Profiles over mode flags:** behavior composition comes from profiles,
bundles, law surfaces, and constraints, not hardcoded runtime mode forks.
- **Explicit refusal:** unsupported or invalid transitions return deterministic,
auditable refusal.
- **Pack-driven integration:** optional content and capabilities are declared by
packs, contracts, registries, and compatibility law.
- **Public identity is contractual:** paths and implementations are not public
surfaces unless registered as such.

## What Exists Today

The repository currently contains:

- a CMake-based C17/C++17 source tree
- Domino engine substrate roots under `engine/`
- Dominium game/domain roots under `game/`
- runtime shell, platform, view, diagnostics, storage, input, audio, network,
and host-integration roots under `runtime/`
- product entrypoints under `apps/`
- machine-readable contracts under `contracts/`
- content and pack surfaces under `content/`
- validation, migration, codegen, packaging, audit, and developer tools under
`tools/`
- contract, invariant, smoke, integration, fixture, and proof suites under
`tests/`
- repo governance and queue material under `.aide/`, `AGENTS.md`, and `docs/`

Narrow product-spine slices recorded as completed include Workbench validation,
command/result/view, package mount, replay proof, barebones client shell, AIDE
workflow law, AIDE workunit schema, AIDE dev/main policy, AIDE checkpoint loop,
AIDE capability reality ledger, and presentation contract work. They do not open
broad product or release work by themselves.

## Quick Start For Developers

The primary public verification path is the CMake `verify` preset plus the fast
strict proof gate.

```powershell
cmake --preset verify
cmake --build --preset verify --target ALL_BUILD
py -3 tools/test/run_fast_strict.py --repo-root .
```

AIDE local health checks:

```powershell
py -3 .aide/scripts/aide_lite.py doctor
py -3 .aide/scripts/aide_lite.py validate
```

Targeted contract validators are useful when touching specific surfaces:

```powershell
py -3 tools/validators/repo/check_dependency_directions.py --repo-root . --strict
py -3 tools/validators/contracts/check_command_surface.py --repo-root . --strict
py -3 tools/validators/contracts/check_module_descriptors.py --repo-root . --strict
py -3 tools/validators/contracts/check_diagnostics_registry.py --repo-root . --strict
```

The `verify` preset is the normal development preset. Host-specific and
platform-specific details live in `docs/development/guides/BUILDING.md`.

## Project Layout

```text
apps/       thin product entrypoints and product composition
engine/     Domino deterministic substrate and public engine-facing surfaces
game/       Dominium domain rules, process emission, and game interpretation
runtime/    shell, platform, view, diagnostics, storage, input, audio, network
contracts/  machine-readable, version-pinned, compatibility-sensitive law
content/    authored packs, profiles, datasets, fixtures, assets, templates
docs/       canon, architecture, development, reference, planning, release, repo docs
tests/      contract, invariant, smoke, integration, fixture, and proof suites
tools/      validation, packaging, migration, release, audit, and developer tooling
archive/    historical, superseded, quarantined, or provenance-retained material
```

Ownership-sensitive split reminders:

- Do not infer ownership from similarly named roots.
- Follow `AGENTS.md` and scope-specific contract/planning artifacts before
binding new work to transitional, projected, or quarantined roots.
- Generated outputs are evidence unless a stronger source promotes them.

## Public Docs Map

| Reader goal | Start here |
|---|---|
| Understand the project quickly | `README.md`, `DOMINIUM.md` |
| Check what is real now | `docs/STATUS.md`, `.aide/queue/current.toml`, `docs/repo/FOUNDATION_LOCK.md` |
| Understand the architecture | `docs/ARCHITECTURE.md`, `docs/architecture/CANONICAL_SYSTEM_MAP.md`, `docs/architecture/CANON_INDEX.md` |
| See planned sequencing | `docs/ROADMAP.md`, `.aide/queue/current.toml` |
| Build locally | `docs/development/guides/BUILDING.md` |
| Contribute | `CONTRIBUTING.md`, `AGENTS.md` |
| Understand packs and modding | `MODDING.md`, `content/README.md`, `content/packs/README.md`, `contracts/package/packs/README.md` |
| Operate as an agent | `AGENTS.md`, `.aide/context/latest-task-packet.md` |

## Contracts And Public Surfaces

Public identity must be registered and versioned. A file path, implementation,
or generated artifact is not public merely because it exists.

Core contract entrypoints:

- Public surfaces: `contracts/public_surface/public_surface.contract.toml`
- Commands: `contracts/command/command_surface.contract.toml`
- Views: `contracts/view/view_surface.contract.toml`
- Diagnostics: `contracts/diagnostic/diagnostic_code.registry.json`
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

Early pack tiers remain data-first. Arbitrary executable code in packs is not
part of the current trust model.

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
4. Run targeted validation plus whitespace/diff checks.
5. Run fast strict when scope warrants it or when claiming gate status.
6. Report what was run and what was not run.

See `CONTRIBUTING.md` for contributor workflow notes, but resolve conflicts
against canon, glossary, AGENTS, and active contracts.

## License And Security

- License: `LICENSE.md`
- Security policy: `SECURITY.md`
