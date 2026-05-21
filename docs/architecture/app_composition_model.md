Status: DERIVED
Last Reviewed: 2026-05-22
Supersedes: none
Superseded By: none
Stability: provisional

# App Composition Model

An app is a product composition input. App identity is not the executable
filename, launcher option, implementation directory, or Workbench presentation.

## Role

An app descriptor declares the requested product shape. It may request default
profiles, packs, modules, providers, services, capabilities, renderer options,
platform targets, release references, evidence policy, and limitations.

The descriptor does not own the implementation of those services. Runtime
services remain governed by service/provider law. Pack activation remains
governed by package and trust law. Module enablement remains governed by module
law and the composition decision.

## Inputs

An app composition plan may include:

- `app_ref`
- `profile_refs[]`
- `pack_refs[]`
- `module_refs[]`
- `provider_requests[]`
- `capability_requests[]`
- optional `platform_target_ref`
- optional `renderer_request`
- trust, compatibility, overlay, deterministic ordering, and evidence policies
- artifact inputs and requested lock/report outputs

The app descriptor may name these references. It does not silently synthesize
them from paths or implementation directories.

## Outputs

The composition resolver law defines:

- `composition_plan.schema.json` for unresolved requests
- `composition_decision.schema.json` for selected, degraded, refused, partial,
  planned, or fixture-only decisions
- `app_composition_lock.schema.json` for derived app composition lock evidence
- capability, refusal, compatibility, and trust reports for supporting proof

The app composition lock records the selected app, profiles, packs, modules,
providers, capability decisions, diagnostics, evidence, limitations, and status.
It is not a new source descriptor.

## Support Claims

Fixture-only app composition proves schema and validator behavior. It is not a
product launch support claim. Planned rows and fixture rows must keep
`support_claim = false` when that field is present.

Support can be claimed only when the decision cites evidence for the requested
surface. A future launcher or runtime resolver may consume the lock, but the
lock alone does not prove executable product behavior.

## Boundaries

Apps may not bind private implementation paths as identity. Apps may not select
providers silently. Apps may not enable modules without declared capability.
Workbench may display app composition state, but Workbench is not composition
authority.

This model does not implement App Composer, product launch, package mounting,
provider runtime, module loading, renderer behavior, native GUI behavior, or
release publication.
