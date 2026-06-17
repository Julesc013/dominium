Status: DERIVED
Last Reviewed: 2026-06-17
Supersedes: legacy top-level `MODDING.md` FUTURE0 summary
Superseded By: none
Stability: provisional
Future Series: PUBLIC-DOCS
Replacement Target: long-lived public modding overview derived from canon, contracts, content docs, current trust model, and legal policy

# Dominium Modding And Packs

This document is the public entrypoint for Dominium modding and pack policy.

Dominium's current modding model is **data-first, contract-governed, and
explicitly bounded**. Packs can declare authored content, compatibility targets,
capabilities, laws, profiles, datasets, assets, and other data-defined surfaces.
They do not currently provide arbitrary executable runtime code.

This file is derived. If it conflicts with `docs/canon/constitution_v1.md`,
`docs/canon/glossary_v1.md`, `AGENTS.md`, active contracts, pack registries,
`.aide/queue/current.toml`, or reviewed audits, the higher-authority artifact
wins for project, technical, canon, architecture, validation, and governance
meaning.

Legal files control legal permissions and restrictions. This file does not grant
permission to publish, distribute, monetise, host, or maintain independent forks,
modified builds, servers, packs, tools, engines, games, products, or derivative
works.

## Current Public Boundary

| Area | Current public status |
|---|---|
| Data-first packs | Supported as the current trust-model direction. |
| Pack manifests and compatibility declarations | Governed by contracts and registries. |
| Capability/law-gated optional content | Required design direction. |
| Deterministic refusal or degradation for missing/incompatible content | Required design direction. |
| Arbitrary executable pack code | Not part of the current trust model. |
| Mods changing engine/runtime authority semantics | Not allowed. |
| Mods bypassing law, audit, or capability gates | Not allowed. |
| Broad package runtime | Blocked until a reviewed phase opens it. |
| Public mod distribution or monetisation | Not authorised without written permission from the Project Owner. |

## Legal Boundary

`LICENSE.md`, `CONTRIBUTOR_LICENSE_AGREEMENT.md`, `TRADEMARKS.md`,
`FAN_CONTENT_POLICY.md`, and `THIRD_PARTY_NOTICES.md` govern legal permissions,
identity use, contribution rights, fan/community content, and third-party
material.

This modding policy describes the intended technical and trust model for packs.
It does not, by itself, allow anyone to:

- publish or distribute mods, packs, patched builds, forks, launchers, tools, or
  servers;
- monetise Dominium-related content, services, hosting, marketplaces, videos,
  streams, guides, or derivative works;
- use Dominium or Domino names, marks, logos, or project identity as if a mod,
  pack, server, or tool is official;
- modify engine code or authoritative runtime code outside the official
  contribution process;
- bypass repository license restrictions.

Any public pack, mod, server, tool, marketplace, or derivative work requires
prior express written permission unless a future authoritative legal policy
expressly opens that use.

## Core Rule

Mods extend authored data and declared surfaces. They do not replace the engine,
rewrite authoritative execution semantics, bypass law, or create hidden fallback
behavior.

```text
pack data
  -> manifest and compatibility target
  -> capability/law checks
  -> explicit activation or refusal
  -> deterministic use by product/runtime surfaces
  -> diagnostics/evidence where applicable
```

## What Packs May Add

Subject to active contracts, registries, and legal permission, packs may add or
declare:

- authored content records
- profiles, parameter bundles, and law/profile data
- process, production, refinement, travel, institution, or policy data
- domain, worldgen, dataset, fixture, asset, or template payloads
- capability declarations and compatibility targets
- documentation and provenance metadata
- ToolIntent-facing data where law-gated and contract-supported

The exact accepted shapes are determined by the relevant `content/` and
`contracts/` surfaces, not by this summary alone.

## What Packs May Not Do

Packs and mods may not:

- modify engine code or authoritative runtime code
- bypass deterministic Process execution
- alter constitutional invariants
- introduce nondeterministic authoritative behavior
- silently coerce incompatible schema or version data
- bypass law, capability, audit, diagnostic, or refusal surfaces
- fabricate authority, entities, goods, provenance, or state outside lawful
contracts
- declare themselves public surfaces merely because files exist
- include arbitrary executable runtime code under the current trust model
- publish, distribute, monetise, or host Dominium-derived material without legal
  permission

## Compatibility Contract

Pack compatibility must be explicit:

1. Schemas and manifests declare identity, version, and stability where required.
2. Packs declare compatibility targets.
3. Missing optional packs produce deterministic degradation or deterministic
refusal.
4. Version mismatch produces explicit refusal or an explicit migration path, not
silent fallback.
5. Conflicts must be explicit and deterministically resolved.
6. Generated outputs are evidence unless a stronger source promotes them.

## Modding Status Honesty

Public docs should use this language:

| Claim | Use this wording | Avoid this wording |
|---|---|---|
| Pack model | "Dominium uses a data-first, contract-governed pack direction." | "Dominium supports arbitrary mod code." |
| Compatibility | "Packs must declare compatibility targets and refuse/degrade explicitly." | "The system will guess or silently adapt incompatible packs." |
| Runtime authority | "Mods do not alter authoritative runtime semantics." | "Mods can patch the engine or replace law." |
| Current maturity | "Pack and modding policy exists as a governed surface under active development." | "The complete public mod platform is released." |
| Package runtime | "Package runtime remains blocked until later reviewed phases." | "Runtime packages are broadly available now." |
| Legal permission | "Public distribution or monetisation requires written permission." | "Anyone can publish or sell Dominium mods." |

## Where To Start

Read these in order:

1. `README.md`
2. `LICENSE.md`
3. `CONTRIBUTOR_LICENSE_AGREEMENT.md`
4. `TRADEMARKS.md`
5. `FAN_CONTENT_POLICY.md`
6. `docs/STATUS.md`
7. this file
8. `content/README.md`
9. `content/packs/README.md`
10. `contracts/package/packs/README.md`
11. `contracts/capability/README.md`
12. relevant schema, registry, and contract files for the specific pack type

Architecture and policy references:

- `docs/architecture/EXTENSION_RULES.md`
- `docs/architecture/MOD_ECOSYSTEM_RULES.md`
- `docs/architecture/mod_pack_trust_model.md`
- `docs/architecture/PACK_FORMAT.md`
- `docs/architecture/MODPACK_FORMAT.md`
- `docs/architecture/CANON_INDEX.md`

## Contributor Rule

When adding or changing pack/content behavior:

1. Identify the relevant content root, contract, registry, and schema.
2. Keep pack behavior data-first.
3. Add or update validation and refusal behavior when shape or compatibility
meaning changes.
4. Update docs and examples in the same change when public modding meaning
changes.
5. Do not claim released mod-platform capability unless current status and
release/trust proof support that claim.
6. Follow `CONTRIBUTOR_LICENSE_AGREEMENT.md` for every pack, content, asset,
   schema, fixture, or documentation contribution.

## Maintenance Rule

When modding policy changes:

1. Update the governing canon, contract, registry, or reviewed audit first.
2. Update this file as a derived public summary.
3. Update `docs/STATUS.md` and `docs/ROADMAP.md` if current capability,
authorization, or sequencing changed.
4. Keep arbitrary executable pack code out of public claims unless a future
reviewed trust model explicitly opens it.
5. Keep legal permissions aligned with `LICENSE.md`, `TRADEMARKS.md`,
   `FAN_CONTENT_POLICY.md`, `THIRD_PARTY_NOTICES.md`, and any written permission
   from the Project Owner.
