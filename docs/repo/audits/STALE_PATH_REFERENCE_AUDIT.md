Status: DERIVED
Last Reviewed: 2026-05-16
Supersedes: none
Superseded By: none

# Stale Path Reference Audit

Status: PROVISIONAL

Phase: CONVERGE-12

Date: 2026-05-12

## Scope

Search scope covered tracked repository text surfaces with generated output roots excluded from the scan where practical:

- docs and README surfaces
- repo contracts and validator docs
- migration inventory and move-map surfaces
- selected root-level current-facing files

Historical/archive/audit records were not rewritten merely because they document old paths.

## Terms Searched

Searched terms:

`client/`, `server/`, `setup/`, `launcher/`, `schema/`, `schemas/`, `lib/`, `libs/`, `app/`, `appshell/`, `runtime/`, `contracts/`, `content/`, `archive/`, `attic/`, `legacy/`, `quarantine/`, `geo/`, `chem/`, `fluid/`, `materials/`, `physics/`, `thermal/`, `electric/`, `worldgen/`, `field/`, `fields/`, `process/`, `archive/generated/dist/`, `build/`, `out/`, `archive/generated/artifacts/`, `repo/`.

Raw term matches remain high because the repository intentionally retains historical docs, source paths, audit records, and current canonical paths. The audit therefore classifies reference groups rather than mechanically replacing every occurrence.

## Summary Counts

| Classification | Count | Notes |
| --- | ---: | --- |
| current_authority_claim | 5 | High-risk docs patched with final CONVERGE-12 authority notes. |
| current_path_instruction | 1 | README governance root wording updated. |
| build_or_script_path | 0 | No build/script path patch was required by this task. |
| generated_or_ephemeral_reference | 4 | `build/`, `out/`, `archive/generated/dist/`, and `archive/generated/artifacts/` remain documented as generated or exception-backed. |
| historical_reference | 33 | Search terms remain in historical/current docs where not misleading authority. |
| archived_reference | 1 | Audit/archive records intentionally retain old path state. |
| superseded_reference | 5 | Layout authority docs retained but clearly superseded. |
| unresolved_review | 12 | Grouped unresolved review root/path classes remain exception-backed. |

## Reference Table

| File | Reference | Classification | Action | Notes |
| --- | --- | --- | --- | --- |
| `README.md` | `repo/` governance root | current_path_instruction | updated | Clarified `contracts/repo/` and `docs/repo/` as current governance layout surfaces; root `repo/` remains transitional/review. |
| `docs/architecture/ARCH_REPO_LAYOUT.md` | `client/`, `server/`, `launcher/`, `setup/`, `schema/`, old canonical layout heading | current_authority_claim | updated | Added final CONVERGE-12 note and demoted the old canonical layout heading for physical paths. |
| `docs/architecture/DIRECTORY_CONTEXT.md` | old authoritative directory contract and old product/schema roots | current_authority_claim | updated | Added final CONVERGE-12 note and converted current-authority wording to historical context. |
| `docs/restructure/FUTURE_LAYOUT_PROPOSAL.md` | `/src` proposal, `schema/`, `schemas/`, `appshell/`, product roots | superseded_reference | cross_reference_added | Retained as planning input; added final note that current contracts supersede the proposal. |
| `docs/architecture/CANON_INDEX.md` | canonical doc index listing older path docs | current_authority_claim | cross_reference_added | Added final note that this index is not current physical layout authority. |
| `docs/repo/STALE_LAYOUT_AUTHORITY.md` | stale authority inventory | current_authority_claim | updated | Marked CONVERGE-12 review status and listed patched docs. |
| `docs/release/*_mock.md` | target/interop matrix mock paths | superseded_reference | cross_reference_added | Release/component matrix contract now owns current support posture. |
| `docs/runtime/shell/UI_MODE_RESOLUTION.md` | mode claims | current_path_instruction | cross_reference_added | Product mode support posture linked to component matrix without changing semantics. |
| `docs/architecture/PLATFORM_RESPONSIBILITY.md` | platform backend support language | current_path_instruction | cross_reference_added | Platform matrix now records status rows. |
| `docs/architecture/RENDERER_RESPONSIBILITY.md` | renderer backend support language | current_path_instruction | cross_reference_added | Render matrix now records status rows. |
| repo-wide historical docs | old product/domain/schema/runtime paths | historical_reference | left_historical | Historical references remain when not presented as current layout authority. |
| repo-wide generated references | `build/`, `out/`, `archive/generated/dist/`, `archive/generated/artifacts/` | generated_or_ephemeral_reference | not_current_authority | Covered by root policy, exception ledger, and distribution projection docs. |
| `contracts/repo/layout_exceptions.toml` | 37 active exception paths | unresolved_review | unresolved_followup | Retargeted active exception retirement from `CONVERGE-12` to `POST-CONVERGE`. |

## High-Risk Stale Authority

The highest-risk stale authority surfaces were:

- `README.md`
- `docs/architecture/ARCH_REPO_LAYOUT.md`
- `docs/architecture/DIRECTORY_CONTEXT.md`
- `docs/restructure/FUTURE_LAYOUT_PROPOSAL.md`
- `docs/architecture/CANON_INDEX.md`

Each now points readers to current source layout authority:

- `contracts/repo/layout.contract.toml`
- `contracts/repo/root_allowlist.toml`
- `contracts/repo/layout_exceptions.toml`
- `docs/repo/REPO_LAYOUT_TARGET.md`

## Unresolved References

Unresolved stale-reference follow-up remains grouped, not hidden:

- active exception-backed roots and files in `contracts/repo/layout_exceptions.toml`
- historical docs that still mention old roots as old state
- older release/target matrix mocks that remain reference inputs
- current-facing docs that may still deserve narrower CONVERGE-12-plus cleanup, but no longer outrank current contracts

Unresolved grouped stale-reference count: 12.
