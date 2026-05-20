Status: CANONICAL
Last Reviewed: 2026-05-21
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: MOD-PACK-TRUST-MODEL-01, ASSURANCE-PROFILE-00
Replacement Target: none
Binding Sources: `AGENTS.md`, `docs/canon/constitution_v1.md`, `contracts/trust/mod_pack_trust.contract.toml`

# Mod Pack Trust Model

MOD-PACK-TRUST-MODEL-01 defines the default-deny trust ladder for mods, packs,
module packs, external process adapters, and native providers. It is policy,
validation, fixture, and documentation only. It does not implement a loader,
sandbox, dynamic library mechanism, Workbench UI, package mount runtime, or
release trust system.

## Core Rule

Mods and packs are not trusted because they exist. A pack is not code authority,
a module is not permission, a provider is not trusted by default, and native
providers are blocked unless a trusted or signed native provider policy applies.

Every trust decision must be representable as:

- subject ID and kind;
- trust level;
- requested permissions;
- declared capabilities;
- determinism and security impact;
- review and sandbox requirements;
- diagnostics and refusal codes;
- evidence reference.

## Trust Ladder

`data_only` is authored data only. It may read its own pack payload and has no
filesystem, network, process, external adapter, or native authority.

`schema_validated` is data validated by declared schemas or contracts. It may
contribute declared data, registries, content, themes, UI documents, and
validation evidence, but no executable code.

`scriptless_rule_data_pack` is declarative rule/data contribution. It cannot
run arbitrary scripts, and it must declare determinism impact before validation
or composition.

`workbench_authored_module` is a Workbench-authored descriptor/view/command
surface. It may invoke registered commands only. Private tool calls remain
forbidden when a command surface exists.

`external_process_adapter` talks to an external process. It must declare IPC or
protocol identity, filesystem/network/process permissions, security impact, and
determinism impact. It is not allowed in deterministic replay paths unless
explicitly isolated or refused.

`trusted_native_provider` is native implementation inside a trusted build or
release boundary. It must declare ABI, capabilities, provider descriptor,
platform constraints, and conformance evidence. Dynamic untrusted loading is
not enabled.

`signed_native_provider` is future policy only. It requires signing, release,
revocation, and assurance policy before it can become active.

## Permissions

Permissions are registry-backed authority requests. Capabilities are not
permissions, and permissions are not capabilities. A descriptor must declare
both when both are relevant.

Data-only packs receive no filesystem, network, process, or native permission.
External adapters must declare process, IPC, filesystem, network, and
determinism details. Native providers must use trusted/signed native provider
trust policy and conformance proof.

## Determinism

Determinism impact is mandatory. The replay path accepts deterministic,
presentation-only, and tooling-only declarations. Nondeterministic adapters or
providers must be isolated or refused. Unknown determinism impact refuses.

## Pack Overlays

Pack overlays are ordered, conflict-aware composition records. Silent overwrite
is forbidden. A future lockfile or mount plan will record overlay order,
conflicts, trust decisions, compatibility impact, and capability reports.

## Relationships

Artifact identity law provides artifact IDs and provenance. Schema/protocol law
governs descriptor and data evolution. Capability/refusal law supplies typed
decisions and recovery. Provider law governs replaceable providers. Module law
governs pack-provided modules. Version/deprecation and replacement law govern
future trust contract evolution.

Diagnostics and refusals are not prose-only. Trust validation uses registered
diagnostic codes and refusal codes so tools, Workbench, and future runtime
decisions can agree on the same machine-readable outcome.
