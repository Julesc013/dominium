# Reader Brief — Dominium XStack Release Identity and Versioning

## What this chat was about

This chat designed a release identity/versioning architecture for Dominium/XStack. It moved from general versioning theory to a concrete layered model that separates strict SemVer components, SemVer-shaped product/suite release IDs, GBN/BII build provenance, channels/lifecycle, artifact names, platform targets, manifests, and capability-based compatibility.

## Top 20 things to know

1. Do not solve release identity with one number.
2. Strict SemVer is only for declared public APIs/contracts.
3. Products and suites may use SemVer-shaped IDs without strict SemVer semantics.
4. Products and suites are separate entity classes.
5. GBN is build provenance, not SemVer precedence.
6. BII should be structured manifest metadata.
7. Git SHA can identify local builds.
8. `stable` should not be encoded as `-stable`.
9. Hotfixes should normally be patch releases plus metadata.
10. dev/alpha/beta/rc are prerelease labels.
11. stable/lts/nightly/internal/hotfix are lifecycle/release-class metadata.
12. Filenames are projections, not canonical truth.
13. Manifests are canonical.
14. Package kind should be explicit.
15. Support family and binary target baseline are separate.
16. Linux kernel major alone is not an exact target.
17. Windows legacy families likely need separate baselines.
18. Setup is a standalone product with install/repair/rollback/migration duties.
19. Internal compatibility should likely use capabilities/contracts.
20. The next action is Release Constitution + SemVer Component Inventory.

## Decisions

See Decision Register in file 04.

## Pending tasks

See Task Register in file 04. Highest priority: Release Constitution, SemVer Component Inventory, suite version policy, GBN/BII spec, capability registry.

## Open questions

Exact suite semantics, exact SemVer component list, BII schema, filename grammar, manifest schema, target taxonomy, and capability registry.

## Artifacts

The uploaded prompt and this generated package are the main artifacts.

## Verification items

Verify SemVer primary spec, repo/build files, OS/toolchain feasibility, final product/suite inventory, and capability-profile relationship.

## Best next step

Draft the Release Constitution and SemVer Component Inventory.
