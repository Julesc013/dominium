Status: DERIVED
Last Reviewed: 2026-05-22
Supersedes: none
Superseded By: none
Stability: provisional

# Provider Selection Model

Provider selection is explicit, deterministic, and evidence-backed. A provider
is a replaceable implementation of a service, backend, or integration kind. It
is selected by descriptor, capability, policy, platform constraint, and proof,
not by hidden runtime convenience.

## Request

A provider request records:

- requested provider kind
- required capabilities
- optional capabilities
- platform, renderer, profile, pack, module, and artifact context where
  relevant
- preferred provider, if any
- acceptable degradation, if any
- trust and compatibility policy references

Provider kinds and provider IDs come from provider contracts and registries.
Unknown provider kinds or provider references are refusal conditions.

## Decision

A provider selection lock records:

- candidate providers
- selected provider
- selected capabilities
- rejected providers
- degradation
- refusal reasons
- diagnostics
- conformance references, when available
- evidence
- fallback trace for degraded selections

Selected providers must declare the required capabilities. Provider fallback is
not silent. A degraded decision without fallback trace, diagnostics, and
evidence is invalid.

## Capability Reports

Capability reports record requested, available, selected, missing, degraded,
refused, recovery, and evidence fields. Missing required capabilities must
either refuse the decision or produce an explicit degraded decision with
diagnostics, evidence, and recovery guidance.

Optional capabilities may be omitted only when the report names the omission and
the selected provider still satisfies required capabilities.

## Ordering

Candidate order is deterministic. The first composition law allows policy-based
ordering by provider kind, request ID, required capability ID, provider ID, and
declared preference. Hidden enumeration order, platform loader order, and
runtime availability probes are not sufficient evidence.

## Boundaries

This model does not implement provider runtime selection, native loading,
renderer/platform backends, storage/network/audio/input backends, network
access, package loading, or release publication. It defines the contract and
lock surfaces that future implementation slices must satisfy.
