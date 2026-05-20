Status: DERIVED
Last Reviewed: 2026-05-21
Supersedes: none
Superseded By: none
Stability: provisional

# Provider Model

PROVIDER-MODEL-01 defines how Dominium describes replaceable providers,
backends, adapters, Workbench modules, and future native providers. Provider
identity is a semantic ID, not an implementation path. Provider availability is
not assumed, selection is explicit, and fallback is typed degradation.

## Provider Concept

A provider is a replaceable implementation of a capability, service, backend, or
interface. Renderers, platform hosts, storage backends, network transports,
audio/input systems, package/profile loaders, command handlers, Workbench
modules, external adapters, and native providers all use the same descriptor
model.

Provider IDs are lowercase dotted names:

- `domino.provider.render.null`
- `domino.provider.render.software`
- `domino.provider.storage.local`
- `dominium.provider.workbench.validation`

IDs must not contain paths, filenames, temporary labels, or build locations.
`implementation_path` is allowed only as a non-authoritative hint.

## Descriptor

Provider descriptors declare kind, owner, version, stability, provided and
required capabilities, entry surface, implementation path hint, language, ABI,
platform constraints, determinism impact, security impact, threading model,
lifetime model, diagnostics, refusals, conformance tests, replacement policy,
trust level, proof, and notes.

Stable providers require conformance tests. Native/provider ABI promotion must
obey the API/ABI canon and later replacement protocol. Provider dependencies
must obey dependency-direction law.

## Selection

A provider selection request names the requested provider kind, required
capabilities, preferred provider if any, acceptable degradation, platform
context, artifact context, and evidence requirement.

A provider selection decision is one of:

- `selected`
- `degraded`
- `refused`
- `unavailable`

Selected decisions name the provider and selected capabilities. Degraded
decisions name `degraded_from`, `degraded_to`, diagnostics, recovery, and
evidence. Refused or unavailable decisions include a refusal code and recovery.

## Relationships

Providers declare capability IDs from the capability registry. Missing or
unsupported providers use refusal codes and diagnostic codes. Evidence packets
record selection, degradation, and refusal proof. Public provider surfaces are
registered in the public surface registry. Provider descriptors are artifacts in
the artifact-identity sense, but this task does not migrate existing runtime
files into descriptors.

## Trust And Conformance

Initial trust levels include built-in, repo-canonical, generated,
local-untrusted, external-reviewed, external-process, native-trusted,
signed-release, fixture, and historical. Detailed mod/native trust remains later
work.

Conformance policy records required capabilities, public surfaces, fixtures,
diagnostics, ABI rules, dependency boundaries, and compatibility-corpus
relationships. PROVIDER-MODEL-01 defines the proof law only; it does not
implement a conformance runner.

## Examples

- Render: software can explicitly degrade to null for a headless test profile.
- Platform: Win32 providers must declare platform constraints and ABI posture.
- Storage: local storage declares deterministic ordering expectations where
  artifact hashes are involved.
- Package: validators declare package capabilities without implementing package
  runtime loading here.
- Workbench: modules may be providers, but Workbench is not authority and must
  consume command/provider contracts.

## Non-Goals

This law does not implement provider runtime loading, dynamic libraries,
renderer fallback, platform bindings, package/profile loader behavior,
Workbench UI, gameplay, networking, native provider ABI, or release behavior.
