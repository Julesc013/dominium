Status: DERIVED
Last Reviewed: 2026-05-20
Supersedes: none
Superseded By: none
Stability: provisional
Task: SCHEMA-CANON-01

# SCHEMA-CANON-01 Audit

## Scope

Canonicalize active tracked `contracts/schema/` buckets that still encoded old root names, abbreviation-era names, or duplicate singular/plural forms. This pass is limited to schema taxonomy and directly stale path references.

Starting commit: `b9626967084417db5a969b5a4cd0dd883746b5d1`

Branch: `main`

## Buckets Inspected

- `contracts/schema/compat/`
- `contracts/schema/core/`
- `contracts/schema/diag/`
- `contracts/schema/lib/`
- `contracts/schema/models/`
- `contracts/schema/mods/`
- `contracts/schema/render/`
- `contracts/schema/specs/`
- `contracts/schema/material/`
- `contracts/schema/materials/`

Empty or untracked old buckets such as `chem`, `civ`, `civilisation`, `fluid`, `geo`, `net`, `packs`, `tools`, and `validator` were also checked through `git ls-files`; no active tracked files remained there during this pass.

## Routing Decisions

- Compatibility schemas moved to `contracts/schema/compatibility/`.
- Diagnostic replay/repro schemas moved to `contracts/schema/runtime/diagnostics/`.
- Render schemas moved to `contracts/schema/runtime/render/`.
- Modding schema specs moved to `contracts/schema/package/modding/`.
- Compliance/spec-sheet schemas moved to `contracts/schema/validation/specs/`.
- Modeling schemas moved to `contracts/schema/domain/modeling/`.
- Singular/plural material schemas moved to `contracts/schema/domain/materials/`.
- Install/store/product-build schemas moved to `contracts/schema/install/`.
- Artifact, bundle, and provides schemas moved under `contracts/schema/package/`.
- GC schemas moved to `contracts/schema/runtime/storage/`.
- Instance profile schemas moved to `contracts/schema/profile/`.
- Save schema moved to `contracts/schema/save/`.
- Migration event schema moved to `contracts/schema/repo/migration/`.
- Generic core graph, flow, hazard, network, spatial, component, constraint, schedule, partition, and state schemas were split into `contracts/schema/domain/*` or `contracts/schema/engine/*` owners based on their stated purpose.

## Schema Identity

Schema bodies and `schema_id` fields were preserved. The moved files keep their semantic schema identity unless a future schema-versioned migration explicitly updates those IDs.

## References Updated

Active path references in current contracts, RepoX rules, docs, audit maps, and tool analyzers were updated from old schema paths to their new canonical locations where they directly referenced moved files or moved buckets.

Generated and historical archive snapshots were not hand-edited.

## Validator Update

`tools/validators/repo/check_path_terms.py` now treats the old active schema buckets as forbidden active path prefixes and points each one at the canonical owner.

## Validation Results

- `git ls-files` check for retired active schema buckets: PASS; no active tracked files remain under the old buckets moved by this pass.
- `python tools/validators/repo/check_path_terms.py --strict --json --max-findings 20`: PASS_WITH_WARNINGS with blocker count 0.
- `python scripts/verify_docs_sanity.py`: PASS.
- `git diff --check`: initially found pre-existing trailing whitespace in two touched audit docs after path reference rewrite; whitespace was cleaned and must be rerun in the combined validation pass.

Full CMake/CTest proof is deferred to the combined cleanup validation pass.

## Follow-Up Work

- Regenerate any generated-current topology or audit maps through their owning generators if their hashes are expected to match generated metadata.
- If schema IDs must eventually align with physical path taxonomy, perform that as an explicit schema identity migration with versioned compatibility review.
