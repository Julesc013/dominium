Status: DERIVED
Last Reviewed: 2026-04-02
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: Λ-6, Σ-B, Φ, Υ
Replacement Target: future physical convergence work may consume this review but must not silently rewrite its meaning

# Semantic Ownership Review

## A. Purpose And Scope

This review classifies semantic ownership for the major duplicated, overlapping, or shadow-prone roots that remain visible in the live post-Λ-5 repository.

Its purpose is to make later work safe by answering a narrower question than repository convergence:

- which surface currently carries semantic source-of-truth authority
- which surface is a projection, mirror, or generated derivative
- which surface remains transitional
- which family still requires quarantine or later human review

This review is not a refactor plan, delete plan, or directory-merging action. It extends the P-2 reconciliation layer, the P-4 execution plan, and the `RG-SEM-0` gate from `docs/planning/GATES_AND_PROOFS.md` into explicit ownership law that later `Λ-6`, `Σ-B`, and `Φ/Υ` planning can consume directly.

## B. Ownership Classes

The following ownership classes are used in this review.

- `canonical`: the semantic source of truth for meaning within the reviewed scope.
- `projection`: a machine-readable, packaged, validator-facing, or otherwise derived surface that must stay semantically subordinate to a stronger canonical surface.
- `generated_derivative`: an emitted, compiled, cached, or run-produced surface that may be evidentiary but is not semantically authoritative.
- `advisory_mirror`: a human-readable or machine-readable mirror that restates stronger authority without becoming the owning root.
- `transitional`: a still-live surface retained for compatibility, coexistence, or staged migration; it must not be mistaken for the long-term semantic owner.
- `legacy`: a historical surface retained for reference without current semantic binding authority.
- `merge_later`: a control flag meaning later physical convergence is likely or expected, but is not executed by this review.
- `quarantined`: a control flag meaning later prompts must treat the family as unresolved in at least one important respect.
- `human_decision_required`: a control flag meaning later work must not invent a single winner without explicit human review.

The primary class describes what a path is today. The control flags describe what later work must still treat carefully.

## C. Decision Principles

Ownership decisions in this review follow the existing authority order and review doctrine.

1. Canon and glossary remain the vocabulary and behavior floor.
2. P-0 authority ordering and intake law outrank local README claims inside weaker roots.
3. Semantic authority is distinct from validator, packaging, runtime-distribution, or cached projection convenience.
4. Generated or emitted artifacts do not become canonical merely because tooling reads them.
5. Where evidence shows scoped ownership rather than one global winner, this review records scoped ownership instead of forcing a false collapse.
6. Where evidence is insufficient for a safe winner, quarantine is the correct result.
7. This review preserves future refactor freedom by classifying meaning, not physical layout.

## D. Review Families

This review explicitly covers the mandatory ownership-sensitive families and the additional families that show strong evidence of semantic overlap in the live repo.

| Family | Outcome | Residual Gate |
| --- | --- | --- |
| `field/` vs `fields/` | `fields/` is canonical; `field/` is a transitional compatibility facade | future physical convergence only |
| `schema/` vs `schemas/` | `schema/` is canonical semantic contract law; `schemas/` is a validator-facing projection/mirror | quarantine only if material drift appears |
| `packs/` vs `data/packs/` | scoped split ownership; no single-root winner | yes, residual quarantine and human review |
| `specs/reality/` vs `data/reality/` | specs are canonical; registries are operational projections | no |
| `docs/planning/` vs `data/planning/` | docs are canonical human-readable planning law; JSON roots are operational mirrors | no |
| generated evidence echoes | generated roots are non-canonical evidence only | no, unless someone attempts promotion |

## E. Per-Family Analysis

### E1. `field/` vs `fields/`

**Observed roles**

- `fields/field_engine.py` is the substantive implementation root and declares itself the deterministic field layer engine.
- `field/field_engine.py` is a compatibility wrapper that re-exports from `fields.field_engine`.
- `field/__init__.py` explicitly labels itself as compatibility exports for singular package paths.
- Live repo imports overwhelmingly bind to `fields`, with `field` retained for compatibility-facing access to the boundary exchange helper and singular import paths.

**Authority signals**

- wrapper docstrings in `field/`
- implementation weight in `fields/`
- live import usage across tools and tests

**Final classification**

- `fields/`: `canonical`
- `field/`: `transitional`
- family flags: `merge_later = true`, `quarantined = false`, `human_decision_required = false`

**Risk if misbound**

Later `Λ-6`, `Σ-B`, or `Φ` work could incorrectly bind to a compatibility facade instead of the semantic field substrate.

**Future merge and human review**

Future physical convergence is still plausible, but no additional human review is required to know that later semantic binding should target `fields/`.

### E2. `schema/` vs `schemas/`

**Observed roles**

- P-0 intake law explicitly assigns `schema/**` to `contract_and_schema_law`.
- The same intake law explicitly assigns `schemas/**` to `machine_schema_projections`.
- P-1 extraction records `schema/` as the authoritative `schema_law_and_contract_root`.
- P-1 extraction records `schemas/` as the derived `machine_schema_projection_root`.
- Validator and tooling surfaces consume `schemas/**`, but validator convenience does not outrank semantic contract law.

**Authority signals**

- `docs/planning/SNAPSHOT_INTAKE_PROTOCOL.md`
- `docs/planning/REALITY_EXTRACTION_REPORT.md`
- `data/planning/reality/schema_registry_inventory.json`
- `data/planning/reality/module_map.json`

**Final classification**

- `schema/`: `canonical`
- `schemas/`: `projection` and `advisory_mirror`
- family flags: `merge_later = false`, `quarantined = false at root-role level`, `human_decision_required = false`

**Residual quarantine rule**

If a material disagreement appears between `schema/**` and `schemas/**` without an explicit migration or projection rule, that disagreement must be quarantined immediately.

**Future merge and human review**

No root-level human review is required for present semantic binding. Future per-artifact conflicts remain quarantine-trigger events rather than permission for silent normalization.

### E3. `packs/` vs `data/packs/`

**Observed roles**

- `packs/README.md` and `docs/architecture/pack_system.md` define a canonical on-disk runtime pack substrate under `packs/<category>/<pack_id>/pack.json`.
- `data/packs/` contains authored content and declaration families with `pack_manifest.json`, `pack.toml`, `pack.manifest`, content folders, and supporting data/docs.
- P-1 extraction marks `packs/` as canonical and authoritative for runtime pack manifests.
- P-1 extraction marks `data/packs/` as authoritative within scope but transitional in canonicality assessment.
- The two roots are not equal peers carrying identical ownership semantics, but the live repo also does not justify pretending one simply replaces the other.

**Authority signals**

- `docs/planning/SNAPSHOT_INTAKE_PROTOCOL.md`
- `data/planning/reality/schema_registry_inventory.json`
- `packs/README.md`
- `docs/architecture/pack_system.md`
- observed live file-shape differences between `packs/**/pack*.json` and `data/packs/**`

**Final classification**

- `packs/`: `canonical` within runtime-packaging, activation, compatibility, and distribution-descriptor scope
- `data/packs/`: `transitional` but authoritative within authored pack content and declaration scope
- family flags: `merge_later = true`, `quarantined = true`, `human_decision_required = true`

**Residual quarantine**

This family is only partially resolved. Later prompts may rely on scoped ownership, but they must not assume that `packs/` and `data/packs/` can be freely substituted or that a single-root future winner has already been chosen.

**Future merge and human review**

Later physical or semantic unification is likely enough to justify the `merge_later` flag, but a single-root winner remains a human-review decision rather than something later prompts may infer.

### E4. `specs/reality/` vs `data/reality/`

**Observed roles**

- `specs/reality/` contains the normative Λ-series constitutional specs.
- `data/reality/` contains the operational machine-readable registries that mirror those specs.
- The completed Λ outputs reinforce a spec-to-registry relationship rather than a dual-canon relationship.

**Authority signals**

- completed Λ artifact pairing pattern
- normative `SPEC_*` naming under `specs/reality/`
- machine-readable registry naming under `data/reality/`

**Final classification**

- `specs/reality/`: `canonical`
- `data/reality/`: `projection`
- family flags: `merge_later = false`, `quarantined = false`, `human_decision_required = false`

### E5. `docs/planning/` vs `data/planning/`

**Observed roles**

- `docs/planning/` contains the human-readable planning law, review conclusions, and execution constitutions.
- `data/planning/` contains machine-readable registries, graphs, readiness matrices, and control mirrors used to operationalize that planning layer.
- This is a deliberate doctrine-plus-registry pairing rather than an equal-canon duplication.

**Authority signals**

- completed P-series artifact pairing pattern
- narrative review outputs under `docs/planning/`
- machine-readable inventories, matrices, and graphs under `data/planning/`

**Final classification**

- `docs/planning/`: `canonical`
- `data/planning/`: `projection` and `advisory_mirror`
- family flags: `merge_later = false`, `quarantined = false`, `human_decision_required = false`

### E6. Generated Evidence Echoes

**Reviewed surfaces**

- `build/**`
- `artifacts/**`
- `.xstack_cache/**`
- `run_meta/**`

**Final classification**

- all reviewed roots: `generated_derivative`
- family flags: `merge_later = false`, `quarantined = false`, `human_decision_required = false`

Generated reflections may be evidentiary, but they do not become semantic source-of-truth unless a stronger artifact explicitly promotes a specific emission contract into law.

## F. Canonical Vs Projected Distinction

Later prompts must treat ownership classes differently.

- Canonical roots own meaning, contract interpretation, and semantic lineage inside their declared scope.
- Projection roots expose the same meaning in machine-readable, packaged, or validator-facing form, but cannot redefine the canonical surface.
- Advisory mirrors may assist navigation, validation, or explanation, but they do not outrank stronger ownership roots.
- Generated derivatives may prove that a process emitted or compiled something; they do not become the owner of the originating semantics.

Convenience, tooling visibility, or runtime adjacency never implies semantic ownership by itself.

## G. Ownership And Later-Series Implications

| Decision | `Λ-6` | `Σ-B` | later `Φ` | later `Υ` |
| --- | --- | --- | --- | --- |
| `fields/` canonical over `field/` | bind bridges to `fields/` domain semantics | do not expose singular wrapper as the authoritative task surface | extract services from implementation root, treat wrapper as adapter | preserve historical wrapper lineage if later retired |
| `schema/` canonical over `schemas/` | bridge semantics from contract law, not validator exports | governance and MCP surfaces must not treat projections as owning law | runtime assumptions must follow semantic schema law | compatibility and migration policy must preserve `schema -> schemas` projection lineage |
| scoped split between `packs/` and `data/packs/` | distinguish authored pack meaning from packaged runtime descriptors | expose the correct pack layer for the job | preserve authored-vs-packaged boundaries | provenance, naming, compatibility, and archive policy must not erase authored/package lineage |
| `specs/reality/` canonical over `data/reality/` | bridge from specs, consume registries operationally | use registries without letting them replace normative meaning | runtime assumptions rely on spec-defined semantics | preserve spec-to-registry lineage |
| `docs/planning/` canonical over `data/planning/` | bridge planning meaning from docs | task and governance automation must not let registry convenience override review law | service planning should use docs as the semantic owner | archival or release packaging must preserve document-to-registry lineage |

## H. Quarantine Doctrine

The following quarantine rules remain active after this review.

1. `packs/` vs `data/packs/` remains under residual quarantine for any attempted single-root convergence or silent substitution.
2. Any material semantic disagreement between `schema/**` and `schemas/**` must be quarantined immediately rather than normalized by convenience.
3. `field/` remains a transitional wrapper zone; later prompts must not rebuild semantic field law around it.
4. Generated evidence roots remain non-authoritative unless an explicit higher-order emission contract promotes a specific emitted form.

While quarantine remains, later prompts must not assume:

- that one pack root already owns both authored and packaged roles
- that validator projections may redefine schema law
- that compatibility wrappers own the semantics they re-export
- that emitted evidence trees are a lawful substitute for authored semantic roots

## I. Anti-Patterns / Forbidden Shapes

- treating generated artifacts as canonical because they are convenient to read
- treating packaged or validator-facing projections as semantic source-of-truth
- allowing duplicated roots to drift independently without recorded lineage
- binding governance, MCP, or task surfaces to ambiguous roots by guesswork
- resolving split ownership by naming preference alone
- treating a transitional wrapper as if it were the stable semantic owner
- using future physical convergence to retroactively justify current silent ownership drift

## J. Stability And Evolution

This review is `provisional` in stability but binding for later planning and architecture prompts until explicitly superseded.

Later work may:

- consume these ownership decisions directly
- add new reviewed families when repo evidence warrants them
- perform later physical convergence using this review as semantic guidance

Later work may not:

- silently promote projections into canon
- silently demote canonical roots into advisory status
- collapse residual quarantine without explicit evidence or human review where this review requires it

## Review Summary

The ownership law after `Λ-5.5` is intentionally conservative.

- `fields/`, `schema/`, `specs/reality/`, and `docs/planning/` are the semantic owners within their declared scopes.
- `field/`, `schemas/`, `data/reality/`, and `data/planning/` are subordinate compatibility, projection, or mirror surfaces.
- `packs/` and `data/packs/` are not equal peers and not mutual replacements; they now have scoped ownership with residual quarantine and later human-review requirements.
- generated evidence trees remain evidence only.

That is enough clarification for `Λ-6`, `Σ-B`, and later `Φ/Υ` planning to proceed without silently binding to the wrong roots.
