Status: DERIVED
Last Reviewed: 2026-04-02
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: Ρ, Λ
Replacement Target: intake doctrine revised only after post-Π reconciliation is complete
Binding Sources: `docs/canon/constitution_v1.md`, `docs/canon/glossary_v1.md`, `AGENTS.md`

# Snapshot Intake Protocol

## 1. Purpose

This document is the authoritative intake gate for the post-Ω/Ξ/Π repository state.
It defines how later Ρ-series planning prompts must intake the live repository, normalize mixed evidence, classify ambiguity, and refuse silent semantic drift.

It exists to make post-Π planning:

- deterministic
- repo-reality-first
- constitutionally conservative
- audit-friendly
- explicit about authority and quarantine

This protocol is planning-only.
It does not authorize refactors, runtime moves, schema rewrites, or semantic reinterpretation.

## 2. Scope

This protocol applies to:

- `Ρ-1 Reality Extraction`
- `Ρ-2 Blueprint Reconciliation`
- `Ρ-3 Foundation Readiness`
- `Ρ-4 Final Prompt Synthesis`
- later `Λ-series` semantic-framework planning that depends on a resolved post-Π snapshot

This protocol does not replace constitutional authority.
If it conflicts with canon, glossary, or `AGENTS.md`, those stronger sources win.

## 3. Snapshot Definition

A valid snapshot intake source is a repository-local artifact that satisfies all of the following:

1. It exists under the current repository root at intake time.
2. It can be assigned to a declared artifact family.
3. It has a clear planning role: normative, structural, compatibility, release, planning, or evidentiary.
4. Its scope can be stated without guessing hidden intent.

A valid source may be one of:

- a normative text artifact, such as canon, schema law, contract docs, or release constitutions
- a live structural artifact, such as code, build files, manifests, registries, or policy files
- a derived evidentiary artifact, such as a generated report, baseline, lockfile, or proof bundle with inspectable provenance

The following are not valid standalone sources of truth:

- chat history not materialized into the repo
- remembered assumptions from earlier planning sessions
- shell observations without a path-backed artifact
- path names alone without file-level evidence
- generated output whose source scope or provenance cannot be stated

## 4. Required Artifact Families

Later Ρ prompts must inventory artifact families in the fixed order below.
The family list is based on the live mixed repository state observed after Ω/Ξ/Π, not on a hypothetical clean-room layout.

| Order | Family ID | Typical Roots In This Repo | Primary Use In Intake | Default Handling |
| --- | --- | --- | --- | --- |
| 1 | `canon_and_root_governance` | `docs/canon/**`, `AGENTS.md` | semantic and vocabulary floor; repository execution contract | authoritative |
| 2 | `contract_and_schema_law` | `schema/**`, `docs/contracts/**`, binding governance docs under `docs/architecture/**` and `docs/release/**` | semantic, compatibility, and release doctrine | authoritative |
| 3 | `machine_schema_projections` | `schemas/**` and machine-readable schema exports | validator-facing contract projection | derived unless explicitly promoted for validator scope |
| 4 | `registries_manifests_and_pack_metadata` | `data/registries/**`, `data/packs/**`, `packs/**/pack*.json`, `repo/**`, `data/architecture/**`, `updates/**` | machine-readable runtime, compat, and release declarations | authoritative within declared scope |
| 5 | `live_code_and_build_surface` | `engine/**`, `game/**`, `client/**`, `server/**`, `runtime/**`, `app/**`, `appshell/**`, `launcher/**`, `setup/**`, `lib/**`, `libs/**`, domain roots, build files | implementation and structure reality | structurally authoritative |
| 6 | `release_distribution_and_update_surface` | `release/**`, `docs/release/**`, `repo/release_policy.toml`, `data/release/**`, `updates/**` | install, distribution, channel, archive, and update truth | release-authoritative |
| 7 | `planning_surfaces` | `docs/planning/**`, `data/planning/**`, `docs/blueprint/**`, `data/blueprint/**`, `docs/omega/**`, `docs/restructure/**`, `data/restructure/**` | planning constraints, sequencing, stop conditions, and reconciliation inputs | advisory by default; P-0 artifacts are planning-authoritative within intake scope |
| 8 | `generated_evidence_and_baselines` | `data/audit/**`, `data/baselines/**`, `artifacts/**`, `build/**`, `out/**`, `run_meta/**` | evidence of observed or generated state | derived unless explicitly promoted |
| 9 | `transitional_legacy_and_quarantine` | `legacy/**`, `attic/src_quarantine/**`, `quarantine/**`, roots such as `_orphaned` | migration evidence, residue, or quarantined material | transitional or quarantined |

Notes:

- `lib/**` and `libs/**` are not classified by name alone. They remain in family 5 until stronger evidence marks them otherwise.
- `schema/**` and `schemas/**` are intentionally separate families because this repo contains both.
- A family assignment never overrides the authority rules in [AUTHORITY_ORDER.md](/d:/Projects/Dominium/dominium/docs/planning/AUTHORITY_ORDER.md).

## 5. Deterministic Intake and Ordering Rules

Later Ρ prompts must normalize and report intake data using the following deterministic rules:

1. Enumerate families in the fixed family order from Section 4.
2. Normalize every path to a repo-relative POSIX-style path.
3. Sort artifacts within a family by case-folded normalized path ascending.
4. Break exact case-fold ties by original normalized path ascending.
5. Report claim conflicts in this fixed field order:
   `authority_domain`, `canonical_subject`, `family_id`, `normalized_path`, `status_class`, `disposition`.
6. Report duplicate candidates in the same fixed order, never in discovery order.
7. Never collapse two distinct paths into one subject without citing the shared identifier or explicit cross-reference that justifies the grouping.

Every Ρ-series inventory row must include, at minimum:

- `normalized_path`
- `family_id`
- `authority_domain`
- `status_class`
- `provenance_class`
- `claim_subject`
- `conflict_state`
- `quarantine_state`
- `evidence_note`

## 6. Artifact Status Classes

An artifact must be placed into exactly one primary status class for intake reporting:

| Status Class | Meaning |
| --- | --- |
| `authoritative` | May directly govern later planning within its declared scope. |
| `derived` | Produced from stronger sources or previous inventories; useful only with intact provenance. |
| `advisory` | Informative but not conflict-resolving on its own. |
| `stale` | Contradicted by stronger current evidence, explicitly superseded, or out of date for the current post-Ω/Ξ/Π snapshot. |
| `transitional` | Retained for migration, convergence, or comparison; not silently canonical. |
| `quarantined` | Explicitly excluded from canonical planning resolution until review completes. |

## 7. Authority and Ambiguity Classes

The intake layer must also assign an authority or ambiguity class where relevant:

| Class | Meaning | Default Disposition |
| --- | --- | --- |
| `semantically_authoritative` | Governs ontology, law, vocabulary, contract meaning, or refusal semantics. | use within semantic scope |
| `structurally_authoritative` | Governs what currently exists, where it lives, and how the repo is wired. | use within structural scope |
| `compatibility_authoritative` | Governs versioning, migration, compat classes, and explicit refusal paths. | use within compatibility scope |
| `release_authoritative` | Governs install, distribution, update, archive, and channel behavior. | use within release scope |
| `planning_authoritative` | Governs post-Π planning mechanics and sequencing only. | use within planning scope |
| `generated_authoritative` | Derived output that a stronger contract explicitly names as the consumer-facing operational artifact. | use only for that emitted scope |
| `advisory_only` | Helpful context with no decisive authority. | cite only as support |
| `stale_doc` | Prose or notes no longer aligned to the current stronger sources. | mark stale |
| `transitional` | Mixed-state residue that may still matter for convergence or archaeology. | keep visible but non-canonical |
| `duplicate_shadow` | Parallel artifacts appear to claim the same concept, interface, or ownership. | quarantine |
| `insufficient_evidence` | The repo does not provide enough evidence to classify safely. | quarantine |
| `quarantine_required` | Conflict or uncertainty is too strong for autonomous planning resolution. | stop and escalate |

## 8. Evidence Standards

When code, docs, manifests, generated artifacts, and prior plans disagree, later Ρ prompts must apply the following evidence standards:

### 8.1 Semantic claims

Use canon, glossary, explicit schema law, and contract docs first.
Live code may show implementation drift, but it must not silently redefine frozen doctrine.

### 8.2 Structural claims

Use the live repository tree, build scripts, imports/includes, active manifests, and active registries first.
Planning docs cannot override what is actually present in the post-Ω/Ξ/Π worktree.

### 8.3 Compatibility claims

Use schema version declarations, migration/refusal docs, compat manifests, compat registries, and explicit release-resolution metadata first.
Reports and tests confirm compliance; they do not invent new compatibility semantics.

### 8.4 Release and distribution claims

Use release policy, release/update schemas and manifests, component graph doctrine, and current update channel artifacts first.
Tool code is evidence of mechanism, not permission to bypass explicit release doctrine.

### 8.5 Planning claims

Use this P-0 protocol and the post-Π in-repo planning artifacts.
Historical series notes or earlier chat assumptions are supportive at most.

## 9. What Later Ρ Prompts May Assume

Later Ρ prompts may assume all of the following:

- The repository is in a mixed post-Ω/Ξ/Π state and must be treated as such.
- Canon, glossary, and `AGENTS.md` remain binding.
- The family order and normalization rules in this document are fixed.
- Live repo structure is authoritative for existence and location claims.
- Planning artifacts may constrain planning behavior, but not rewrite stronger semantic or structural truth.
- Explicitly legacy or quarantined areas remain non-canonical until resolved.

## 10. What Later Ρ Prompts Must Not Assume

Later Ρ prompts must not assume any of the following without path-backed evidence:

- that a plan from an earlier series still matches the live repo
- that `schemas/**` replaces `schema/**`, or the reverse
- that `lib/**` or `libs/**` are legacy because of naming alone
- that a generated report reflects the current source state unless its provenance is explicit
- that two similarly named artifacts are semantically equivalent
- that a missing doc proves a missing subsystem
- that a present subsystem is canonical just because it exists outside quarantine
- that migration, coercion, or semantic defaulting may occur silently

## 11. Quarantine Rules

Quarantine is mandatory when any of the following occurs:

1. Two same-tier authoritative sources make materially incompatible claims in the same authority domain.
2. A legacy, transitional, or quarantined area appears to implement a canonical concept in parallel with a live area.
3. Ownership of a concept, interface, or registry cannot be determined safely from current evidence.
4. A lower-level doc conflicts with stronger machine-readable or constitutional reality.
5. `schema/**` and `schemas/**` disagree in a way that changes meaning or validator shape without an explicit migration or projection rule.
6. A generated artifact is being used as authority without clear provenance or emission contract.
7. A later Ρ or Λ planning step would need to invent semantics, migrations, or structural ownership to continue.

Quarantine means:

- do not delete
- do not silently canonize
- do not synthesize implementation prompts from the disputed area
- record the conflict and route it to human review

## 12. Human Review Escalation

Human review is required when quarantine is triggered and also when the intake touches areas already identified by the current manual review doctrine, including:

- architecture graph changes
- semantic contract changes
- module ABI boundaries
- runtime privilege escalation policies
- distributed authority model changes
- lifecycle manager semantics
- restartless core replacement mechanisms
- trust root governance changes

When review is triggered, later Ρ prompts must output:

- the conflicting subject
- the candidate source paths
- the authority domain
- the reason autonomous resolution was refused
- the minimal review packet needed to continue

## 13. Silent Inference Prohibitions

The following must never be inferred silently:

- semantic intent from directory names alone
- current authority from historical status labels alone
- deprecation from age or path depth alone
- compatibility from parser success alone
- release legitimacy from generated output alone
- canonical ownership from duplicated identifiers alone
- equivalence between planning vocabulary and runtime vocabulary without glossary support

## 14. Downstream Obligations

Later post-Π planning must use this protocol as follows:

- `Ρ-1` inventories the snapshot and classifies artifacts, but does not resolve same-tier disputes silently.
- `Ρ-2` reconciles blueprint expectations against the `Ρ-1` inventory using the authority model.
- `Ρ-3` evaluates foundation readiness only from non-quarantined evidence and explicitly scoped exceptions.
- `Ρ-4` synthesizes later prompts only from resolved evidence sets and must carry forward quarantine boundaries.
- `Λ-series` semantic planning may extend doctrine only from canon plus resolved post-Π evidence, never from stale planning assumptions.

## 15. Operational Rule

If a later prompt cannot classify a source, resolve authority, or explain a conflict under this protocol, it must stop and emit a quarantine decision rather than improvise.
