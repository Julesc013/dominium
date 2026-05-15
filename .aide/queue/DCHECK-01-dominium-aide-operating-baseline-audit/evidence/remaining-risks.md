# Remaining Risks

Status: needs_review

- Durable baseline is blocked until Q52/Q53/Q53R and generated AIDE outputs are committed intentionally. DCHECK-01 itself is committed as a checkpoint.
- Current validation PASS results depend on uncommitted `.aide/scripts/aide_lite.py` Q53R repair.
- Full `eval run` is timeout-prone.
- Refactor move/salvage/path-alias/reference-rewrite maps are not created and not approved.
- Release command family is installed but target-local release bundle is absent; release publishing remains forbidden.
- Repo/tool/root inventories still contain unknown/high-risk classifications.
- Sibling Eureka already has Q54-related evidence and dirty state; coordinate globally after Dominium commit finalization.
