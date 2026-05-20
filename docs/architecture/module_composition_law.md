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

## Adding A Module

Add a descriptor using `contracts/module/module.schema.json`, choose a governed
module kind from `contracts/module/module_kind.registry.json`, bind dependencies
by stable IDs, add fixtures for validator behavior, and run:

```text
python tools/validators/contracts/check_module_descriptors.py --repo-root . --strict
```

Do not use a module descriptor to bless an unbounded folder, direct tool call,
or private app-specific shortcut.
