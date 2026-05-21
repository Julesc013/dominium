Status: CANONICAL
Last Reviewed: 2026-05-21
Supersedes: `contracts/service/service_conformance.contract.toml` as the primary service/provider conformance law narrative
Superseded By: none
Stability: provisional
Replacement Target: later runtime service dispatch, provider resolver, renderer/platform/package service work, and Workbench modules must instantiate this law rather than bypass it
Binding Sources: `docs/canon/constitution_v1.md`, `docs/canon/glossary_v1.md`, `AGENTS.md`, `docs/runtime/RUNTIME_SERVICES.md`, `docs/architecture/SERVICES_AND_PRODUCTS.md`, `docs/planning/SEMANTIC_OWNERSHIP_REVIEW.md`, `contracts/service/service.contract.toml`, `contracts/conformance/conformance.contract.toml`

# Service Conformance Law

## 1. Purpose

This law defines how Dominium service descriptors and conformance suites are declared before a service can be relied on by commands, apps, modules, Workbench, packages, runtime slices, renderers, platforms, or future game systems.

A service is a callable semantic runtime capability. A provider is a replaceable implementation of a service or backend. A descriptor proves only identity, references, limits, and evidence obligations. It is not a runtime dispatcher, provider loader, renderer backend, platform backend, package runtime, Workbench UI, or gameplay implementation.

## 2. Vocabulary

- `service`: callable semantic runtime capability governed by a service descriptor.
- `provider`: replaceable implementation of a service or backend, selected only after declared capability and conformance checks.
- `command`: user, test, app, or tool-facing invocation surface. A command may invoke a service, but service identity is not command identity.
- `module`: declared functional extension unit that may consume or provide commands, services, and views.
- `app`: product composition of commands, services, providers, modules, and packs.
- `conformance suite`: test, fixture, and evidence set proving a service or provider obeys a contract.

Workbench is a consumer and presenter of service-backed commands. It is not authority. Repo tools may inspect and validate service descriptors, but runtime must not depend on repo-only validators.

## 3. Identity

Service identity is a governed dotted ID such as `dominium.service.validation`. It is not a command ID, provider ID, file path, implementation path, or Workbench module path.

Provider identity is a governed provider ID. Implementation path may be useful metadata, but it is not authority and cannot substitute for provider identity.

The descriptor schema at `contracts/service/service_descriptor.schema.json` requires service identity, kind, owner, version, stability, public surface, command, result, refusal, diagnostic, capability, provider-kind, determinism, authority, artifact, replay, conformance, replacement, and deprecation fields.

## 4. Selection And Refusal

Capability selection must emit one of the governed decisions: `selected`, `degraded`, `refused`, or `evidence`.

Degraded behavior requires explicit evidence. Refusal requires a typed refusal code and diagnostic evidence. Missing services, missing providers, missing capabilities, service not implemented, provider refusal, and provider degradation are governed surfaces, not silent fallback.

## 5. Conformance

Conformance suites live under `contracts/conformance/**` and declare subject kind, subject ID, contract references, required capabilities, required fixtures, positive cases, negative cases, refusal cases, determinism cases, replay cases where relevant, artifact cases where relevant, evidence requirements, and status.

Allowed suite statuses are `planned`, `fixture_only`, `passing`, `failing`, and `retired`.

Only `passing` may carry `support_claim=true`. `planned` and `fixture_only` are valid planning and fixture states, but they do not imply runtime support, provider support, product support, or replacement compatibility.

## 6. Replacement Compatibility

Replacement compatibility is not proven by matching names. A replacement service or provider must preserve service/provider identity rules, command/result/refusal/diagnostic surfaces, capability declarations, provider-kind and limit declarations, artifact and replay implications, and replacement/deprecation policy references. Stable or support-claimed replacement requires passing conformance.

## 7. Non-Implementation Rule

This task adds law, descriptors, registries, fixtures, and validation only. It does not implement runtime service dispatch, provider resolver or provider runtime loading, renderer/platform/storage/network/audio/input/package/profile services, Workbench module runtime or UI, gameplay/domain behavior, or CMake targets.

Future renderer, platform, package, Workbench, and game work can consume this law by declaring service descriptors, provider descriptors, conformance suites, and evidence before support claims.
