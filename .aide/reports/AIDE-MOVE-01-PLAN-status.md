# AIDE-MOVE-01-PLAN Status

## Status

- Task result: PASS
- Candidate selected: yes
- Root: `ide`
- Planned move count: 1
- Required apply-phase reference rewrites: 6
- Apply allowed: false
- Approval status: not_approved

## Candidate

Plan exactly one move:

| Source | Target | Risk | Notes |
| --- | --- | --- | --- |
| `ide/README.md` | `docs/architecture/IDE_PROJECTIONS.md` | low | Binding IDE projection README moves to architecture docs if later approved. |

`ide/manifests/**` is explicitly deferred because it is machine-readable authoritative projection metadata with active script, CMake, release, and architecture references.

## No-Apply Confirmation

No files were moved, deleted, renamed, or rewritten. No salvage map, move map, path alias, shim, or exception update was applied.

## Next Task

`AIDE-GATE-02 - Move Plan Apply Readiness Gate` should inspect this draft plan. Move application remains unauthorized.
