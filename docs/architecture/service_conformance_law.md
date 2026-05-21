Status: CANONICAL
Last Reviewed: 2026-05-21
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: Σ, Φ, Υ, Ζ
Replacement Target: later service instance registries, lifecycle contracts, provider mappings, and product/app/workbench service bindings must instantiate this law rather than replace it
Binding Sources: `docs/canon/constitution_v1.md`, `docs/canon/glossary_v1.md`, `AGENTS.md`, `docs/runtime/RUNTIME_SERVICES.md`, `docs/architecture/SERVICES_AND_PRODUCTS.md`, `docs/planning/SEMANTIC_OWNERSHIP_REVIEW.md`

# Service Conformance Law

## 1. Purpose And Scope

This document defines the narrow service conformance substrate for future
product, app, Workbench, runtime, and tool-facing service declarations.

It exists to answer one question:

- what must a service declaration prove before it can claim conformance to
  Dominium service law?

It does not implement or authorize:

- runtime service dispatch
- service lifecycle, restart, hotswap, snapshot, replay, or state
  externalization behavior
- provider calls, network calls, filesystem expansion, or Gateway use
- product UX, Workbench UI, app behavior, or feature delivery
- semantic doctrine changes or domain ownership changes

## 2. Governing Model

A conforming service declaration describes a bounded service boundary. It is
evidence for future coordination work, not an implementation.

The declaration must stay subordinate to:

- canon and glossary
- `AGENTS.md`
- runtime service doctrine in `docs/runtime/RUNTIME_SERVICES.md`
- access-only service/product doctrine in
  `docs/architecture/SERVICES_AND_PRODUCTS.md`
- ownership and projection cautions from
  `docs/planning/SEMANTIC_OWNERSHIP_REVIEW.md`

## 3. Required Conformance Constraints

Every conforming service declaration must declare these constraints:

- `service_not_semantic_owner`
- `no_runtime_implementation_authorized`
- `no_provider_calls_authorized`
- `no_product_feature_authorized`
- `process_only_truth_mutation`
- `truth_perceived_render_separated`
- `capability_gated_access`
- `deterministic_refusal_or_degradation`
- `ownership_projection_respected`
- `contract_schema_discipline`
- `diagnostics_evidence_declared`

These constraints are machine-checked by
`tools/validators/contracts/check_service_conformance.py` against
`contracts/service/service_conformance.contract.toml`,
`contracts/service/service_conformance.schema.json`, and
`contracts/service/service_class.registry.json`.

## 4. Boundary Law

A conforming service may declare a boundary for future coordination,
inspection, product support, or integration work.

A conforming service must not:

- own Truth, semantic doctrine, product-shell meaning, or domain ownership
- mutate Truth directly
- bypass lawful Process execution
- collapse Truth, Perceived, and Rendered layers
- silently reinterpret capability surfaces
- silently degrade or fallback without typed refusal or deterministic
  degradation
- treat validator projections, generated outputs, or compatibility wrappers as
  semantic owners
- claim runtime implementation, provider execution, or product features from
  conformance alone

## 5. Contract And Validation Surfaces

The service conformance substrate is:

- `contracts/service/service_conformance.contract.toml`
- `contracts/service/service_conformance.schema.json`
- `contracts/service/service_class.registry.json`
- `tools/validators/contracts/check_service_conformance.py`
- `tests/contract/service_conformance/**`

The validator is deterministic for a fixed checkout:

- fixture paths are sorted
- service classes are sorted in output
- valid and invalid fixtures have explicit expected outcomes
- unknown references to registered capabilities, commands, modules, refusals,
  or diagnostics are reported as contract failures when the corresponding
  registry is available

## 6. Service Classes

The initial class vocabulary mirrors `docs/runtime/RUNTIME_SERVICES.md`:

- `execution_coordination`
- `observation_inspection`
- `presentation_support`
- `control_integration`
- `persistence_replay_support`
- `compatibility_policy_support`
- `domain_support`
- `product_support`

These are conformance classes, not service instances. Later work may define
instance registries or lifecycle behavior only through explicit scoped prompts.

## 7. Contract And Schema Impact

This task adds a new provisional service conformance contract and schema under
`contracts/service/**`.

It does not change existing command, module, diagnostic, capability, provider,
runtime, app, Workbench, canon, planning, release, or schema-law artifacts.

No migration is authorized. No compatibility reinterpretation is authorized.
Future changes to stable service declarations must update this contract or
provide explicit refusal/migration policy.

## 8. Non-Implementation Rule

Passing service conformance validation means only that a declaration obeys this
contract surface.

It is not proof that a service exists at runtime, that a provider can be called,
that a product exposes a feature, or that lifecycle/live-ops behavior is safe.
Those claims require later runtime, provider, product, and release-control work
with their own review gates and evidence.
