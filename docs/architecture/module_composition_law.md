Status: DERIVED
Last Reviewed: 2026-05-21
Supersedes: none
Superseded By: none
Stability: provisional

# Module Composition Law

MODULE-COMPOSITION-LAW-01 defines how Dominium declares modules, Workbench
workspaces, and app compositions. It does not implement module loading,
Workbench UI, app composition UI, pack mounting, provider runtime, or product
features.

## Vocabulary

- Component: source/build ownership unit.
- Service: callable runtime or command-facing capability.
- Provider: replaceable implementation of a service/backend/interface.
- Pack: distributable authored payload.
- Module: declared functional extension unit.
- Workspace: large user-facing Workbench composition.
- App: product composition.
- Artifact: persisted or exchanged versioned thing.

The terms are not interchangeable. A source folder may implement a module, but
it is not a module until it has a descriptor. Workbench is presentation and
workflow, not semantic authority.

## Ownership Placement

Module law separates identity, implementation, payload, presentation, and
composition.

| Layer | Canonical home | Rule |
| --- | --- | --- |
| Module declaration | `contracts/module/` or pack-provided module descriptors | Defines the extension unit by ID and contract, not by filesystem path. |
| Reusable behavior | `runtime/`, `game/`, `engine/`, `tools/`, or an owning `apps/*` product boundary | Lives under the root that owns the behavior being implemented. |
| Pack payload | `content/packs/<category>/<pack_id>/` | Distributes authored data, templates, presets, fixtures, assets, and declared module payloads. |
| Workbench module | `apps/workbench/module/` | Presents, edits, inspects, previews, or validates through governed commands and services. |
| Workbench workspace | `apps/workbench/workspace/` | Composes Workbench modules, panels, views, commands, and evidence surfaces. |
| App composition | `apps/<product>/` plus `contracts/app/` and `contracts/composition/` | Selects modules, packs, providers, profiles, and capabilities for a product. |

Do not create a top-level `modules/`, `plugins/`, `services/`, or
`workspaces/` root. Those names describe roles, not source ownership roots.

`runtime/module/` is reserved for a real module runtime service, such as module
discovery, dependency validation, activation planning, lock emission, or
capability resolution. It is not a dumping ground for reusable module
implementations.

`content/modules/` is not a distribution root. Pack-provided modules are
delivered through `content/packs/<category>/<pack_id>/`, optionally with a
pack-local `modules/` subdirectory or manifest section.

## Identity

Module identity is declared by `module_id`, not by path. IDs are lowercase
dotted names under `domino.*` or `dominium.*`; they must not contain path
separators, filenames, or temporary status words. Stable module behavior must
cite proof and a replacement policy.

## Dependencies

Modules bind to:

- service IDs
- command IDs
- view IDs
- document IDs
- capability IDs
- provider IDs
- artifact references

They do not bind to private implementation paths. When a command surface exists,
Workbench modules call commands or services rather than private validators or
tools.

## Pack Modules

Packs may provide modules only through declared module descriptors and pack
policy. Data-only packs cannot silently provide native providers. Activation is
explicit and evidence-bearing; MOD-PACK-TRUST-MODEL-01 deepens trust policy.

## Relationships

Module descriptors reference command, capability, provider, diagnostic, event,
view, document, and artifact surfaces. Replacement protocol governs stable
module replacement later. Schema/protocol and artifact identity law govern the
descriptor format and durable identity.

## World Creation Example

A reusable world-creation module identity such as
`dominium.module.world_creation.v1` is not owned by a Workbench folder.

- Its descriptor belongs in `contracts/module/` or in a pack-provided module
  descriptor.
- Its command, result, artifact, capability, refusal, and view law belongs under
  the corresponding `contracts/*` surfaces.
- Its Dominium-specific world generation behavior belongs under
  `game/domain/worldgen/`.
- Runtime dispatch, package/profile resolution, and provider selection belong
  under the relevant `runtime/*` owner when those services are real.
- Authored templates, presets, scenario seeds, tables, fixtures, and assets
  belong under `content/packs/worldgen/<pack_id>/`.
- Workbench editors, inspectors, preview panels, evidence drawers, and seed
  tools belong under `apps/workbench/module/` and may be composed into
  `apps/workbench/workspace/world_creation/`.
- Client, server, tools, AIDE, and other games consume the module through
  commands, services, artifacts, packs, and composition contracts. They do not
  import Workbench implementation folders as authority.

## Adding A Module

Add a descriptor using `contracts/module/module.schema.json`, choose a governed
module kind from `contracts/module/module_kind.registry.json`, bind dependencies
by stable IDs, add fixtures for validator behavior, and run:

```text
python tools/validators/contracts/check_module_descriptors.py --repo-root . --strict
```

Do not use a module descriptor to bless an unbounded folder, direct tool call,
or private app-specific shortcut.
