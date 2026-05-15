# Dominium Root Preservation Plan

Status: needs_review

Root recycling policy for Dominium remains:

`inventory -> classify -> plan -> salvage map -> move map -> alias plan -> reference rewrite plan -> reviewed apply`

Q52 stops at plan.

## `ide/` Preservation

- Preserve `ide/README.md` because it declares binding IDE projection root behavior.
- Preserve `ide/manifests/projection_manifest.schema.json` because it is schema identity.
- Preserve projection example JSON files as tracked fixtures.
- Preserve `.gitignore` generated-output boundary for `/ide/**` with README/manifests exceptions.

## Future Apply Conditions

No apply is approved until a future task produces and reviews:

- salvage map;
- reference inventory;
- move map if any move is proposed;
- path alias plan if compatibility paths are needed;
- reference rewrite plan if references change;
- validation and rollback evidence.
