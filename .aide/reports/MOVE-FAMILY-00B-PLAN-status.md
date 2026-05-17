# MOVE-FAMILY-00B-PLAN Status

Status: DRAFT
Last Reviewed: 2026-05-17
Approval Status: not_approved
Apply Allowed: false

## Result

Result: PASS_WITH_WARNINGS.

MOVE-FAMILY-00B-PLAN produced a gate-ready draft plan for tracked IDE projection manifest source metadata. It did not move, delete, rename, rewrite references, create shims, approve maps, apply maps, or retire exceptions.

## Baseline

- Structural baseline: BASELINE-00.
- Expected starting HEAD: `18ca419fc22e623166f02fede283d2594951b29e`.
- Release baseline: RELEASE-00 internal pilot proof.
- Prior blocker: MOVE-FAMILY-00-REFINE found `ide/manifests/**` was the clearest remaining ownership group.

## Scope

Inspected subtree:

```text
ide/manifests/**
```

Tracked manifests:

- `ide/manifests/projection_manifest.schema.json`
- `ide/manifests/projection_manifest_examples/example_linux_clang_modern_client_gui.projection.json`
- `ide/manifests/projection_manifest_examples/example_win_vc6_win9x_client_gui.projection.json`

## Plan Summary

- Planned moves: 3.
- Deferred tracked files: 0.
- Blocked files: 0.
- Target owner: `contracts/projections/ide/**`.
- Ready for `MOVE-FAMILY-00B-GATE`: true.
- Apply authorized now: false.

## Warnings

- `contracts/projections/ide/**` does not exist yet.
- `ownership_slots.toml` does not yet define an explicit projection contract slot.
- Generated projection manifests may continue to be emitted under `ide/manifests/*.projection.json`; that is generated output, not tracked source authority.

## Next Task

```text
MOVE-FAMILY-00B-GATE - IDE Manifest Projection Apply Readiness Gate
```
