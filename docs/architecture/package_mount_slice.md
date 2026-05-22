Status: DERIVED
Last Reviewed: 2026-05-22
Supersedes: none
Superseded By: none
Stability: provisional

# Package Mount Slice

PACKAGE-MOUNT-SLICE-01 proves one narrow package/profile mount planning path.
It does not implement runtime package mounting, a mod loader, provider runtime,
module loading, product launch behavior, renderer work, native GUI, gameplay, or
release publication.

## Proof Chain

The slice uses this contract-only chain:

```text
package/profile fixture
-> dominium.package.mount.plan.v1
-> package_mount_result
-> composition plan and decision refs
-> pack_mount.lock derived evidence
-> capability/trust/compatibility/refusal reports
-> evidence ref
-> CLI/headless validator output
```

The proof fixture lives under `tests/contract/package/fixtures`. The validator is
`tools/validators/package/check_package_mount_slice.py`.

## Identity Rules

Package identity comes from declared package IDs, not folders or fixture paths.
Source paths are evidence references only. A package source reference may point
to a fixture manifest, but `source_ref_is_authority` must remain `false`.

The positive fixture uses `pack.base.procedural`, which is already present in
the package lock surface. Negative fixtures reject path-like package identities
and unknown package refs.

## Lockfile Rule

`pack_mount.lock.json` is derived evidence. It records the selected package,
mount order, overlays, diagnostics, limitations, and evidence. It is not source
truth and cannot promote fixture-only behavior into runtime support.

## Refusals And Diagnostics

The slice reuses existing refusal and diagnostic law:

- unknown package refs map to composition reference refusal
- missing required capabilities map to capability refusal
- unsupported trust levels map to mod/pack trust refusal
- silent overlay overwrite maps to pack/composition overlay refusal
- source-truth lockfiles are rejected as evidence boundary violations
- degraded fallback without trace is rejected

## Remaining Gaps

The next runtime-spine tasks may build on this proof, but they remain separate:

- actual package runtime mounting
- content payload execution
- mod loading
- provider resolution runtime
- Workbench pack browser
- launcher/setup/client package consumption
- release package publication
