Status: CANONICAL
Last Reviewed: 2026-05-21
Supersedes: none
Superseded By: none
Stability: provisional
Replacement Target: later provider resolver and backend implementations must instantiate this law rather than bypass it
Binding Sources: `docs/architecture/service_conformance_law.md`, `contracts/provider/provider.contract.toml`, `contracts/provider/provider_conformance.contract.toml`, `contracts/conformance/conformance.contract.toml`

# Provider Conformance Law

## 1. Purpose

A provider is a replaceable implementation of a service or backend. It is not trusted because it exists in the repo or because it has an implementation path. It is selectable only when it declares capabilities, limits, refusal behavior, fallback behavior, evidence policy, replacement policy, and applicable conformance suites.

## 2. Provider Descriptor Obligations

Provider descriptors may declare `implemented_service_ids`, `conformance_suite_refs`, `capabilities_provided`, `capabilities_required`, `fallback_behavior`, `refusal_behavior`, `evidence_policy`, and `replacement_policy`.

If a provider claims an implemented service, it must reference a conformance suite targeting that provider. Planned and fixture-only suites are allowed as non-support evidence, but they do not make the provider usable as a runtime implementation.

## 3. Selection Boundaries

Provider selection must be explicit. Silent fallback is forbidden. If a provider cannot satisfy the requested service, capability, trust level, platform limit, artifact behavior, replay constraint, or conformance status, the result must be degraded with evidence or refused with typed refusal.

Provider identity is never an implementation path. Implementation path is only metadata and cannot satisfy conformance or replacement compatibility.

## 4. Replacement

A replacement provider must preserve the service contract it implements, declared capabilities, refusal/diagnostic behavior, artifact and replay limits, and replacement policy. Stable or support-claimed replacement requires passing provider conformance, not fixture-only evidence.

## 5. Non-Implementation Rule

This law does not implement provider loading, renderer/platform backends, storage/network/audio/input providers, package runtime, Workbench module runtime, or gameplay behavior. It only defines the proof surface future provider implementations must satisfy before being relied on.
