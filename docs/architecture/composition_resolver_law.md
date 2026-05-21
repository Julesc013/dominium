Status: DERIVED
Last Reviewed: 2026-05-22
Supersedes: none
Superseded By: none
Stability: provisional

# Composition Resolver Law

COMPOSITION-RESOLVER-LAW-01 defines Dominium's first machine-readable
composition law for apps, profiles, packs, modules, providers, capabilities,
trust policy, compatibility policy, lockfiles, reports, diagnostics, and
evidence.

Composition is the product. A product is not just an executable, a launch
option, a source directory, or a Workbench view. A product is the resolved and
evidenced composition of descriptors, services, providers, modules, packs,
profiles, capabilities, platform/runtime constraints, policies, diagnostics,
refusals, and proof.

## Governing Inputs

This law extends, and does not replace, the constitutional execution floor:

- `docs/canon/constitution_v1.md`: A1 deterministic simulation and replay, A2
  process-only mutation, A3 law-gated authority, A7 truth/perceived/render
  separation, A9 pack-driven integration, A10 recorder/event integrity, and C1
  contract compatibility.
- `docs/canon/glossary_v1.md`: descriptor, capability, refusal, profile, pack,
  service, truth, render, law, and authority terms keep their canonical meaning.
- `AGENTS.md`: extend over replace, no silent drift, no path-as-identity, no
  planning prompt runtime work, and honest validation.
- Existing app, module, Workbench, provider, capability, refusal, diagnostic,
  artifact, schema, package, trust, service, and project graph contracts remain
  authoritative for their own surfaces.

Composition outputs are derived from contracts, manifests, registries, and
descriptors. Lockfiles and reports are evidence of a resolution; they are not
source truth by themselves.

## Vocabulary

- App descriptor: declared product composition input.
- Profile: user, product, workspace, or session configuration input.
- Pack: distributable authored payload.
- Module: descriptor-based functional extension unit.
- Provider: replaceable implementation of a service, backend, or integration
  kind.
- Capability: requested, provided, selected, refused, or degraded feature.
- Composition plan: unresolved requested composition.
- Composition decision: selected, refused, degraded, partial, planned, or
  fixture-only result of resolution.
- Lockfile: deterministic persisted evidence of a resolved composition.
- Mount plan: ordered pack, profile, module, or provider activation plan.
- Overlay: ordered data/content contribution with explicit conflict policy.
- Conflict: declared or detected overlap requiring refusal, override,
  degradation, or evidence.
- Report: capability, refusal, trust, compatibility, conflict, or evidence
  result.

## Boundary Rules

The composition resolver law preserves these boundaries:

- Paths are not identity.
- Product executable is not product identity.
- App descriptors name composition inputs; they do not own runtime services.
- Packs do not execute arbitrary code unless future reviewed trust/provider law
  allows that execution class.
- Modules are descriptor-based and cannot be enabled by folder presence alone.
- Providers are selected by declared service kind, capability, policy, and
  evidence, not by hidden runtime convenience.
- Workbench may present composition decisions, but it does not override them.
- AIDE may consume composition reports for routing and compact context, but
  tasks remain bounded by explicit allowed paths.

This task does not promote any fixture into support status. Fixture-only rows
prove contracts and validation behavior only.

## Machine Surfaces

Composition plan and decision schemas live under `contracts/composition/`:

- `composition_plan.schema.json`
- `composition_decision.schema.json`
- `composition_plan_kind.registry.json`
- `composition_status.registry.json`
- `deterministic_order_policy.registry.json`
- `overlay_conflict_policy.registry.json`
- `composition_report_kind.registry.json`
- `composition_resolver.contract.toml`

Derived lock/report schemas live under `contracts/lock/`:

- `app_composition_lock.schema.json`
- `pack_mount_lock.schema.json`
- `module_plan_lock.schema.json`
- `provider_selection_lock.schema.json`
- `capability_report.schema.json`
- `refusal_report.schema.json`
- `compatibility_report.schema.json`
- `trust_report.schema.json`

Profile composition is exposed through `contracts/profile/profile_composition.schema.json`
and `contracts/profile/profile.registry.json`.

The validator is:

```text
python tools/validators/contracts/check_composition_plan.py --repo-root . --strict
```

## Plan Model

A composition plan records the unresolved request. It includes:

- plan identity and kind
- app, profile, pack, module, provider, and capability references
- platform and renderer requests
- trust, compatibility, overlay, deterministic ordering, and evidence policies
- artifact inputs and requested outputs
- source references and status

Plan kinds are registered, not inferred from filenames. The initial set is:
`product_launch`, `workbench_workspace`, `package_mount`, `profile_load`,
`provider_selection`, `module_enablement`, `release_projection`, and
`test_fixture`.

## Decision Model

A composition decision records the result of resolving a plan. It can select,
refuse, degrade, partially resolve, remain planned, or stay fixture-only. It
records selected app/profile/pack/module/provider references, capability
decisions, refusals, diagnostics, conflict reports, lockfile references,
evidence, fallback trace, limitations, provenance, generator identity, and a
deterministic order key.

No decision may claim support without evidence. Degraded and partial decisions
must carry diagnostics and fallback trace.

## Deterministic Ordering

Resolver outputs must use deterministic ordering:

- packs sort by declared mount order, then `pack_id`, then version only when
  the selected policy names version as a tie-breaker
- profiles and workspace overrides sort by declared order, then descriptor ID
- module enablement order is descriptor-declared and stable
- provider selection order is governed by provider kind, required capability,
  policy, and deterministic candidate order
- capability decisions and refusal reports are ordered by request identity and
  stable code
- generated lockfiles use canonical object ordering and stable hashes where a
  hash is produced

Filesystem discovery order, hash-map order, thread completion order, platform
directory order, and wall-clock timing are not resolution inputs.

## Overlay And Conflict Law

Overlays are ordered contributions. Every overlapping contribution must declare
conflict behavior. Silent overwrite, implicit last-wins, ignored conflict, and
best-effort conflict behavior are forbidden.

Conflict reports are required when payloads overlap. User profile overrides and
workspace overrides are valid only when explicit and evidenced. If existing
pack verification or mod trust law defines stronger ordering or conflict
requirements for a pack class, those laws govern that pack class and this law
records the composition-level result.

## Provider And Capability Law

Provider selection plans and locks record the requested provider kind, required
capabilities, optional capabilities, candidates, selected provider, rejected
providers, degradation, refusal reasons, diagnostics, evidence, and conformance
references where available.

Capability reports record requested, available, selected, missing, degraded,
refused, recovery, and evidence fields. Missing required capabilities refuse or
degrade the decision. Provider fallback is never silent; it must be recorded in
`fallback_trace`.

## Module Enablement Law

Module plans and locks record requested modules, available modules, enabled
modules, refused modules, required and optional capabilities, document/view/
command contributions, required services/providers, diagnostics, and evidence.

Module identity is descriptor-based, not path-based. Workbench modules are one
consumer of the module system. Module enablement does not imply that a runtime
module loader exists.

## Trust And Evidence

Trust and compatibility inputs are explicit plan references. Trust reports,
compatibility reports, refusal reports, diagnostics, and lockfiles are produced
as evidence packets. They may support later launcher, package, Workbench,
client, server, setup, or release tasks, but they do not mutate source truth.

## Non-Goals

This law does not implement runtime composition resolution, package mounting,
provider selection runtime, module loading, Workbench shell/UI, renderer,
platform backend, gameplay, native GUI, or release publication.
