# Root Recycling Plan

Status: dry_run_no_apply

## Root Plan

| Root | Status | Risk | Files | Plan |
|---|---|---|---:|---|
| `ide/` | review_required | high | 4 | Preserve tracked README, schema, and examples. Improve classifier semantics for projection fixtures before any future map. |

## Future Required Salvage Maps

Future phases should prepare a file-level salvage map only if there is a concrete reason to change `ide/`. Current Q52 evidence recommends preserving all tracked files in place.

Required future salvage-map fields:

- current path
- semantic role
- owner
- target hint
- reference inventory
- validators
- rollback condition
- review gate

## Future Move Maps

No move map is proposed or approved by Q52. If a later task proposes one, it must include:

- all references to `ide/README.md`, `ide/manifests/**`, and projection output paths;
- schema/example validation;
- `.gitignore` preservation;
- compatibility and rollback plan.

## Future Path Aliases And Shims

No path aliases or shims are created in Q52. Future aliases would only be relevant if a reviewed move map is approved.

## Future Reference Rewrite Needs

No reference rewrite is proposed in Q52. Future rewrites must be gated by a reference inventory and validation evidence.

## Future Validation Needs

- JSON parse for manifest schema and examples.
- Projection manifest schema validation against examples.
- `roots validate`.
- `repo validate`.
- `refactor validate` before any future move/reference map.
- Build/projection smoke only in a future explicitly authorized task.

## Exception Retirement Conditions

- Generated IDE project outputs remain ignored under `/ide/**` except tracked README and manifests.
- Projection manifest schema and examples stay tracked unless a future reviewed map proves an equivalent canonical location.
- All references to IDE projection generation commands are inventoried before any path rewrite is proposed.

## Blockers

- Q52 is no-apply.
- The root contains schema identity and binding root policy.
- Example fixtures need schema validation before any fate beyond `keep`.

## Next Recommended Work

Q53 should declare the operating baseline: AIDE control plane installed, tool absorption plan complete, first root pilot complete, and future root recycling remains map-first/no-apply until explicitly authorized.
