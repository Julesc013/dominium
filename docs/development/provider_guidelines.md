Status: DERIVED
Last Reviewed: 2026-05-21
Supersedes: none
Superseded By: none
Stability: provisional

# Provider Guidelines

Use these guidelines when adding or reviewing renderers, platform backends,
storage/network/audio/input providers, package/profile loaders, Workbench
modules, external process adapters, or future native providers.

## Add A Provider

Create or update a provider descriptor with:

- `provider_id`
- `provider_kind`
- `owner`
- `version`
- `stability`
- `capabilities_provided`
- `entry_surface`
- `language`
- `abi`
- `determinism_impact`
- `security_impact`
- `threading_model`
- `lifetime_model`
- `trust_level`

Keep `implementation_path` non-authoritative. A path can help locate code, but
it is never provider identity.

## Choose IDs

Use semantic IDs such as:

- `domino.provider.render.software`
- `domino.provider.platform.win32`
- `domino.provider.storage.local`
- `dominium.provider.workbench.validation`

Do not use `runtime/render/software`, filenames, branch names, temporary status,
or local paths as IDs.

## Declare Capabilities

Providers must declare capabilities from `contracts/capability`. A provider
that cannot satisfy a required capability must refuse or degrade explicitly.
Silent fallback is forbidden.

## Conformance

Stable providers need conformance tests. Provisional and experimental providers
may have empty proof, but their status must remain visible. Do not mark native
or public provider ABI stable without ABI canon, conformance, replacement, and
trust proof.

## Selection And Refusal

Provider selection should produce a typed decision:

- `selected`: provider and capabilities are named.
- `degraded`: from/to providers, diagnostics, recovery, and evidence are named.
- `refused` or `unavailable`: refusal code and recovery are present.

Use provider diagnostics such as `DOM-PROVIDER-CAPABILITY-MISSING`,
`DOM-PROVIDER-CONFORMANCE-MISSING`, and
`DOM-PROVIDER-SELECTION-DEGRADED` instead of free text alone.

## Public Surface

Provider contracts, schemas, registries, validator, and fixtures are registered
as provisional public surfaces. Product code should not depend on validator
paths directly; command/provider surfaces should mediate behavior.

## Scope Guard

Do not turn provider folders into junk drawers. If a provider needs common law,
move the law into contracts. If it needs runtime service selection, wait for the
runtime/provider resolver task. If it needs replacement or deprecation behavior,
use the later replacement and version/deprecation laws.
