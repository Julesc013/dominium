Status: DERIVED
Last Reviewed: 2026-05-18
Supersedes: none
Superseded By: none

# MOVE-SCRIPT-00 Blockers

No router implementation blocker remains.

## Deferred Move Blockers

The dry-run deliberately skipped 172 tracked files. These are not tool failures; they require later reviewed MOVE-BULK gates.

| Blocker Class | Count |
| --- | ---: |
| `active_python_package_requires_import_rewrite_or_shim_plan` | 142 |
| `identity_sensitive_without_clear_identity_safe_route` | 59 |
| `target_uses_forbidden_segment_source` | 13 |
| `authority_sensitive_docs_only_route_requires_review` | 7 |
| `normative_specs_reality_docs_require_authority_review` | 7 |
| `target_uses_forbidden_segment_compat` | 3 |

Counts overlap where one file has multiple reasons.

## Non-Goals Preserved

- No moves.
- No deletes.
- No renames.
- No import rewrites.
- No reference rewrites.
- No shims.
- No move-map or salvage-map application.
- No layout exception retirement.

## Next Gate

`MOVE-BULK-BG-REFINEMENT-00` must decide which route candidates become authorized subsets and which skipped paths remain owner-deferred.
