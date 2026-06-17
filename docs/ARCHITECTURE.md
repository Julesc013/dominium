Status: DERIVED
Last Reviewed: 2026-06-17
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: PUBLIC-DOCS
Replacement Target: long-lived public architecture overview derived from canon, contracts, and architecture docs

# Dominium Architecture Overview

This document is the public architecture overview for Dominium. It gives new
readers a stable mental model without asking them to start inside the full canon
corpus.

This page is derived. It does not replace `docs/canon/constitution_v1.md`,
`docs/canon/glossary_v1.md`, `AGENTS.md`, active contracts, or canonical
architecture documents under `docs/architecture/`.

## One-Sentence Model

Dominium keeps simulation behavior explicit by routing product intent through
commands, contracts, capability checks, deterministic execution, refusals,
results, diagnostics, evidence, and projection surfaces.

## System Shape

```text
                         public and developer entrypoints
                                      │
                                      ▼
┌───────────────────────────────────────────────────────────────────────┐
│                          Product composition                          │
│  apps/client   apps/server   apps/launcher   apps/setup   workbench   │
└───────────────────────────────────┬───────────────────────────────────┘
                                    │
                                    ▼
┌───────────────────────────────────────────────────────────────────────┐
│                       Projection and shell layer                       │
│  view/action models   shells   diagnostics   documents   snapshots    │
└───────────────────────────────────┬───────────────────────────────────┘
                                    │
                                    ▼
┌───────────────────────────────────────────────────────────────────────┐
│                    Command / result / refusal spine                    │
│  commands   capabilities   refusals   services   evidence   replay    │
└───────────────────────────────────┬───────────────────────────────────┘
                                    │
                                    ▼
┌───────────────────────────────────────────────────────────────────────┐
│                    Domino deterministic substrate                      │
│  execution   ordering   storage   replay proof   ABI-facing surfaces   │
└───────────────────────────────────┬───────────────────────────────────┘
                                    │
                                    ▼
┌───────────────────────────────────────────────────────────────────────┐
│                      Contract and content layer                        │
│  contracts   registries   schemas   packs   authored content   tests   │
└───────────────────────────────────────────────────────────────────────┘
```

## Core Architecture Rule

The reusable truth is the contract-governed semantic spine:

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

No presentation surface should invent separate product behavior. CLI, text/TUI,
rendered GUI, native GUI, Workbench panels, CI, and AIDE should project the same
command/result/refusal/diagnostic/evidence truth.

## Layers

| Layer | Responsibility | Not responsible for |
|---|---|---|
| Canon | Non-negotiable architecture, glossary, and authority rules | Day-to-day convenience summaries |
| Contracts | Machine-readable law, registries, schema/version boundaries, public surfaces | Product marketing or aspirational roadmap language |
| Domino engine | Deterministic execution substrate, ordering, storage, replay, ABI-facing boundaries | Game meaning or product-specific interpretation |
| Dominium game/domain | Rule meaning, process meaning, law targets, authored content use, product composition | Renderer-owned authority or hidden fallback behavior |
| Runtime/platform | Shell, platform, view, diagnostics, storage, input, audio, network, host integration | Authoritative truth mutation outside lawful process paths |
| Apps | Thin product entrypoints and composition surfaces | Defining new law by UI convenience |
| Content/packs | Authored data, profiles, datasets, fixtures, assets, templates | Arbitrary executable runtime extension |
| Tools/tests | Validation, migration, codegen, packaging, audit, proof, developer machinery | Promoting generated outputs into source truth |

## Product Roots

| Root | Public meaning |
|---|---|
| `apps/client/` | Client product composition, input, perception, and presentation shell. |
| `apps/server/` | Authoritative server product composition and admin/headless surfaces. |
| `apps/launcher/` | Profiles, instances, compatibility, and launch orchestration. |
| `apps/setup/` | Install, repair, rollback, and local product configuration. |
| `apps/workbench/` | Governed validation, evidence, inspection, and later authoring workflows. |
| `tools/` | Validators, migration tools, packaging helpers, codegen, audit, and developer machinery. |

Apps compose. Runtime implements reusable behavior. Contracts define law. Content
supplies authored payload. Tools validate, generate, migrate, and audit.

## Invariants

Dominium architecture is constrained by these public invariants:

- identical canonical inputs must produce identical authoritative outputs
- authoritative truth mutation must occur only through lawful deterministic
Process execution
- perception and rendering must remain derived from truth, not owners of truth
- behavior composition must come from profiles, bundles, law surfaces, and
constraints rather than hardcoded runtime mode flags
- unsupported or invalid transitions must produce deterministic, auditable
refusals
- optional content and capabilities must be declared by packs, contracts,
registries, and compatibility law
- a file path or implementation is not public merely because it exists

## Public Surface Rule

Public identity is contractual. A path, type, function, command, file, generated
artifact, or implementation detail is not a stable public surface unless the
appropriate contract or registry says so.

Start with:

- `contracts/public_surface/public_surface.contract.toml`
- `contracts/command/command_surface.contract.toml`
- `contracts/view/view_surface.contract.toml`
- `contracts/diagnostic/diagnostic_code.registry.json`
- `contracts/refusal/refusal_code.registry.json`
- `contracts/capability/capability.registry.json`
- `contracts/module/module_surface.contract.toml`
- `contracts/provider/provider.contract.toml`
- `contracts/service/service.contract.toml`
- `contracts/project_graph/project_graph_model.contract.toml`
- `contracts/package/`
- `contracts/replay/`

## Current Architecture Status

The architecture spine exists as repository law, contracts, validators, and
narrow completed slices. Broad product surfaces remain intentionally blocked
until later reviewed phases open them.

For current status, use `docs/STATUS.md` and `.aide/queue/current.toml`.
For roadmap sequencing, use `docs/ROADMAP.md`.

## Reading Order

For most readers:

1. `README.md`
2. `docs/STATUS.md`
3. this file
4. `DOMINIUM.md`
5. `docs/ROADMAP.md`
6. `CONTRIBUTING.md`

For implementation or agent work:

1. `docs/canon/constitution_v1.md`
2. `docs/canon/glossary_v1.md`
3. `AGENTS.md`
4. relevant active contracts
5. relevant canonical architecture document under `docs/architecture/`
6. relevant tests, validators, and queue/audit artifacts

## What Not To Infer

Do not infer that:

- a planned architecture surface is already implemented
- a completed narrow slice opens broad feature work
- Workbench is a complete editor
- renderer work is authorized because projection contracts exist
- pack contracts authorize arbitrary executable mod code
- fast strict passing means full release/trust certification
- generated outputs become truth unless a higher-authority source promotes them
