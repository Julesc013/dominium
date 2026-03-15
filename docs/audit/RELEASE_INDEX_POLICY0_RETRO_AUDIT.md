Status: DERIVED
Last Reviewed: 2026-03-14
Stability: provisional
Future Series: RELEASE-INDEX
Replacement Target: release-index governed suite evolution with explicit yanking and rollback policy

# RELEASE-INDEX-POLICY-0 Retro Audit

## Current Release Index Surface

- `schema/release/release_index.schema` defines a single channel-scoped offline-first release index.
- `src/release/update_resolver.py` currently treats `release_index.components` as a single exact target set keyed by `component_id`.
- `tools/release/update_model_common.py` emits one release-index snapshot per distribution bundle with an embedded component graph.
- `release_index.json` already carries semantic-contract, governance, platform-matrix, and component-graph hashes.

## Current Resolver Behavior

- Update resolution is deterministic and component-graph driven.
- Compatibility is currently governed by:
  - semantic contract hash equality
  - protocol-range overlap
  - target platform row presence
  - trust-policy enforcement
- There is no explicit release-resolution policy layer yet.
- There is no explicit yanked-component field or selection behavior.

## Current Install / Profile Assumptions

- `install.profile.full` is the implicit default in release/update surfaces.
- Install planning resolves component ids through the component graph, not through a version-selection policy.
- Update planning assumes one effective descriptor per `component_id`.
- The current bundle/install surfaces do not declare whether they are using suite-pinned or latest-compatible selection.

## Current Semantic / Protocol Versioning

- Semantic contract hash is the hard compatibility gate for updates.
- Supported protocol ranges are checked globally at release-index level.
- Product SemVer exists on component descriptors, but the resolver does not currently rank candidates by SemVer/build id.
- Suite version remains human-facing and is not currently used as the runtime-compatibility gate.

## Current Git / Changelog State

- Current local tags are legacy or safety-oriented: `canon-clean-2`, `safety/mega-13cb8ca7`.
- There is no current suite-tag policy matching `suite/vX.Y.Z-<channel>`.
- Top-level `CHANGELOG.md` exists and is generated, but product-specific release-tag alignment is not yet formalized.
- Additional doc-local changelog files exist under `docs/architecture/` and `docs/engine/`.

## Gaps Identified

- No explicit deterministic latest-compatible policy.
- No explicit yanking or yank-warning/refusal surface.
- No release-resolution policy registry or CLI parameter.
- Install transaction log does not yet require `install_plan_hash` and `prior_component_set_hash`.
- Git tagging policy for suite/product/contract alignment is not frozen.
