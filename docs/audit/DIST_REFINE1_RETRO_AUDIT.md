Status: DERIVED
Last Reviewed: 2026-03-14
Stability: provisional
Future Series: DIST
Replacement Target: install-profile refinement and release-index availability governance

# DIST-REFINE-1 Retro Audit

## Current Distribution Assumptions

- DIST-1 assembly currently derives its component set from the component graph, but it always uses the single implicit default install plan.
- The assembled full bundle always writes a default instance and bundled store artifacts, regardless of whether a narrower install surface is desired.
- Setup install status already computes a component install plan, but there is no named profile registry or profile-driven planning command surface.

## Default Runtime Assets

- The default linked instance is governed by `instances/default/instance.manifest.json`.
- The default pack lock is governed by `locks/pack_lock.mvp_default.json`.
- The default profile bundle is governed by `profiles/bundles/bundle.mvp_default.json`.
- The baseline component graph is governed by `data/registries/component_graph_registry.json`.

## Implicit Full-Bundle Assumptions To Remove

- `build_dist_tree(...)` implicitly means "full bundle".
- The resolver default profile token is legacy (`install_profile.mvp_default`) rather than a governed registry entry.
- Setup and launcher expose install-plan information, but not named install profiles.

## Safe Insertion Points

- Add a dedicated `install_profile_registry.json` and route selection through `src/release/component_graph_resolver.py`.
- Thread `install_profile_id` through setup planning/apply, launcher status, and dist assembly without changing graph semantics.
- Keep default behavior aligned with the previous full-bundle composition so existing default-instance flows remain unchanged.
