Status: DERIVED
Last Reviewed: 2026-04-02
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: Ρ, Λ
Replacement Target: authority matrix revised only after post-Π reconciliation closes open quarantine sets
Binding Sources: `docs/canon/constitution_v1.md`, `docs/canon/glossary_v1.md`, `AGENTS.md`

# Authority Order

## 1. Purpose

This document defines the deterministic precedence order for resolving disagreements inside the post-Ω/Ξ/Π repository snapshot.
It does not change constitutional doctrine.
It only makes later Ρ-series and Λ-series planning explicit about which source wins for which kind of claim.

## 2. Global Baseline

The following order applies before any domain-specific refinement:

1. `docs/canon/constitution_v1.md`
2. `docs/canon/glossary_v1.md`
3. `AGENTS.md`
4. explicit schema law and contract docs under `schema/**` and `docs/contracts/**`
5. scope-specific constitutions and policy docs under `docs/architecture/**`, `docs/release/**`, and repo policy files such as `repo/release_policy.toml`
6. versioned machine-readable source artifacts such as registries, manifests, pack descriptors, and declared architecture data
7. live repo code and build configuration for structural and implementation reality
8. current in-repo planning artifacts, including this P-0 layer and current blueprint artifacts
9. generated reports, baselines, inventories, and proof bundles with intact provenance
10. stale docs, legacy notes, attic material, and explicitly quarantined areas
11. historical planning assumptions from earlier chats or unmaterialized discussions

This baseline is not enough by itself.
Every disagreement must be classified into an authority domain first.

## 3. Domain-Specific Authority

### 3.1 Semantic Authority

| Tier | Source Family | Authority Level | Rule |
| --- | --- | --- | --- |
| `SEM-1` | `docs/canon/constitution_v1.md`, `docs/canon/glossary_v1.md` | absolute | Frozen semantic doctrine, vocabulary, and refusal semantics. |
| `SEM-2` | `AGENTS.md`, `schema/**`, `docs/contracts/**` | absolute within repo-execution and contract scope | Governs repository obligations, schema law, migration/refusal duties, and task discipline. |
| `SEM-3` | binding architecture or release constitutions under `docs/architecture/**` and `docs/release/**` | conditional | Applies when the claim is inside the document's declared scope and does not conflict with higher tiers. |
| `SEM-4` | declared semantic registries and manifests under `data/registries/**`, `packs/**`, `data/packs/**`, `data/architecture/**` | conditional | May define data-driven meaning only when they are explicit, current, and not contradicted by higher tiers. |
| `SEM-5` | live repo code | conditional | Evidence of implementation state only; code cannot silently rewrite canon. |
| `SEM-6` | planning docs and old series outputs | contextual | May describe intent, never override stronger semantic sources. |
| `SEM-7` | generated reports, stale docs, attic, legacy notes, chat history | insufficient on their own | Never sufficient to define semantics. |

### 3.2 Structural Authority

| Tier | Source Family | Authority Level | Rule |
| --- | --- | --- | --- |
| `STR-1` | live repo tree, code, build files, import/include relationships, active manifests | absolute | Governs what exists now, where it lives, and how it is wired. |
| `STR-2` | machine-readable registries and manifests consumed by the live repo | conditional | Strong evidence for declared ownership, activation, and structural relationships. |
| `STR-3` | architecture and release docs | conditional | Strong only when still aligned to the observed tree. |
| `STR-4` | current planning docs | contextual | May propose structure, but may not overrule the live snapshot. |
| `STR-5` | generated reports and inventories | conditional | Evidence only if provenance is intact and inputs are known. |
| `STR-6` | stale docs, legacy notes, attic, chat history | insufficient on their own | May explain history, not present structure. |

### 3.3 Compatibility Authority

| Tier | Source Family | Authority Level | Rule |
| --- | --- | --- | --- |
| `COM-1` | schema version declarations, `schema/SCHEMA_VERSIONING.md`, migration/refusal contracts, compatibility docs under `docs/contracts/**` | absolute | Governs versioning semantics and whether migration or refusal is mandatory. |
| `COM-2` | compat manifests, compat registries, pack compat descriptors, release resolution metadata | absolute within artifact scope | Governs compatibility class, upgrade/downgrade behavior, and explicit refusal surfaces. |
| `COM-3` | compat and validation code | conditional | Implementation evidence for enforcement, not a license to bypass explicit contracts. |
| `COM-4` | planning docs and old reports | contextual | May propose compat work, not declare compat truth. |
| `COM-5` | stale docs, attic, legacy notes, chat history | insufficient on their own | Never enough to settle compatibility disputes. |

### 3.4 Release and Distribution Authority

| Tier | Source Family | Authority Level | Rule |
| --- | --- | --- | --- |
| `REL-1` | `repo/release_policy.toml`, release/update schemas, release manifests and indexes, component graph doctrine, `docs/release/**` constitutions | absolute within release scope | Governs channel, archive, install, update, distribution, and component-resolution meaning. |
| `REL-2` | release/update manifests, component graph data, release policy registries | conditional | Strong when current and not contradicted by `REL-1`. |
| `REL-3` | release tooling code | conditional | Shows mechanism and integration points, not policy supremacy. |
| `REL-4` | planning docs | contextual | Can sequence release work, not rewrite release law. |
| `REL-5` | generated reports, stale docs, legacy notes, chat history | insufficient on their own | Evidence only. |

### 3.5 Planning Authority

| Tier | Source Family | Authority Level | Rule |
| --- | --- | --- | --- |
| `PLN-1` | `docs/planning/SNAPSHOT_INTAKE_PROTOCOL.md`, `docs/planning/AUTHORITY_ORDER.md`, `data/planning/snapshot_intake_policy.json` | absolute within post-Π intake planning | Governs how later Ρ and Λ planning must classify and rank sources. |
| `PLN-2` | current blueprint and freeze-era planning artifacts under `docs/blueprint/**`, `data/blueprint/**`, `docs/omega/**`, `docs/restructure/**`, `data/restructure/**` | conditional | Governs current planning intent only where it does not conflict with stronger semantic, structural, compatibility, or release truth. |
| `PLN-3` | old series outputs, inventories, reports, and archaeology notes | contextual | Useful for history and traceability only when still aligned to the live snapshot. |
| `PLN-4` | stale planning notes, attic notes, chat history | insufficient on their own | Never authoritative for new planning decisions. |

## 4. Minimum Ranking For Common Source Categories

The table below gives the deterministic minimum ranking for the source categories later prompts will encounter most often.

| Source Category | Semantic | Structural | Compatibility | Release / Distribution | Planning | Notes |
| --- | --- | --- | --- | --- | --- | --- |
| live repo code | `SEM-5` conditional | `STR-1` absolute | `COM-3` conditional | `REL-3` conditional | insufficient on its own | strongest evidence for implementation and layout, not for constitutional reinterpretation |
| generated machine-readable artifacts | `SEM-7` insufficient unless promoted | `STR-5` conditional | `COM-4` contextual unless contract-promoted | `REL-5` insufficient unless contract-promoted | `PLN-3` contextual | may become `generated_authoritative` only when explicitly named as the emitted operational surface |
| schemas and registries | `SEM-2` to `SEM-4` depending on artifact | `STR-2` conditional | `COM-1` to `COM-2` strongest | `REL-2` conditional | `PLN-2` contextual if planning data | strongest machine-readable contract surface in the repo |
| manifests and compatibility metadata | `SEM-4` conditional | `STR-2` conditional | `COM-2` absolute within artifact scope | `REL-1` to `REL-2` strong | `PLN-2` contextual when used in planning datasets | pack, install, release, and update descriptors live here |
| architecture specs | `SEM-3` conditional | `STR-3` conditional | `COM-4` contextual | `REL-1` when release doctrine is explicit | `PLN-2` contextual | strong when scoped and current |
| planning docs | `SEM-6` contextual | `STR-4` contextual | `COM-4` contextual | `REL-4` contextual | `PLN-1` or `PLN-2` depending on document | planning authority is real but scope-limited |
| old series outputs and reports | `SEM-6` or `SEM-7` | `STR-5` or `STR-6` | `COM-4` or `COM-5` | `REL-5` | `PLN-3` | only useful when they still match the live repo |
| stale docs / legacy notes / attic material | insufficient | insufficient | insufficient | insufficient | `PLN-4` insufficient | may explain history, never settle present truth |
| historical planning assumptions from earlier chats | insufficient | insufficient | insufficient | insufficient | insufficient | must be materialized into the repo before they can matter |

## 5. Special Handling Rules

### 5.1 `schema/**` versus `schemas/**`

- `schema/**` carries schema law, migration obligations, and semantic contract prose.
- `schemas/**` carries machine-readable schema projections and validator-facing exports.
- If they align, use both in their respective scopes.
- If they disagree materially, semantic authority stays with `schema/**` and the disagreement is quarantined until projection ownership is resolved.

### 5.2 Generated Artifact Promotion

A generated artifact may be treated as `generated_authoritative` only when all of the following are true:

1. A stronger source explicitly requires that emitted artifact as the operational surface.
2. The emitting scope is deterministic and inspectable.
3. The input snapshot can be stated.
4. No higher-tier source contradicts the emitted meaning.

Otherwise, generated artifacts remain derived evidence.

### 5.3 Transitional and Quarantined Areas

- `legacy/**`, `attic/src_quarantine/**`, and `quarantine/**` are never authoritative on their own.
- They may supply historical or comparative evidence.
- If they shadow a live canonical concept, the subject is quarantined rather than silently merged.

### 5.4 Historical Planning Assumptions

Assumptions from earlier chats or prompt drafts have no authority until they are written into the repository and survive the authority rules above.

## 6. Conflict Resolution Procedure

Later Ρ prompts must resolve disagreements in this exact order:

1. Classify the claim domain: semantic, structural, compatibility, release, or planning.
2. Gather candidate sources in normalized path order.
3. Assign each candidate to the relevant authority tier.
4. Discard lower-tier candidates unless they remain useful as evidence of drift or history.
5. If a single highest-tier candidate remains, use it and mark lower conflicting candidates as stale, derived mismatch, or transitional as appropriate.
6. If multiple highest-tier candidates conflict materially, quarantine the subject and stop autonomous resolution.
7. Record the winning source, losing sources, authority domain, and disposition explicitly.

No later planning step may replace this procedure with "best judgment."

## 7. Operational Consequences

These rules imply the following:

- Code beats docs only for implementation and structure, not for constitutional semantics.
- Planning docs beat older planning notes only inside planning scope, never inside semantic or compatibility scope.
- Reports can confirm or contradict expectations, but they do not create doctrine.
- Legacy and attic material remain visible for archaeology, not canonical resolution.
- Any unresolved same-tier conflict becomes a review item, not a hidden assumption.
