Status: DERIVED
Last Reviewed: 2026-03-14
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: RELEASE/GOVERNANCE
Replacement Target: signed suite and product tagging policy with archive-index binding

# Git Tagging And Release Policy

## Tag Families

### Suite Tags

- Format: `suite/vX.Y.Z-<channel>`
- Example: `suite/v0.0.0-mock`
- A suite tag identifies one curated release-index snapshot.

### Product Tags

- Optional per-product tags:
  - `engine/vX.Y.Z`
  - `client/vX.Y.Z`
  - `server/vX.Y.Z`
  - `setup/vX.Y.Z`
  - `launcher/vX.Y.Z`
- Product tags describe product-specific SemVer history and do not replace suite tags.

### Contract Tags

- Format: `contracts/vN`
- Used when the semantic-contract bundle meaning changes in a way that requires a new compatibility epoch.

## Tag Rules

- Tags are append-only.
- Tag rewriting is forbidden.
- A suite tag must correspond to one immutable release-index snapshot.
- The tagged release documentation must reference:
  - `release_manifest_hash`
  - `component_graph_hash`
  - `semantic_contract_registry_hash`
  - `governance_profile_hash`

## Suite / Product Alignment

- Suite tags are human-facing curated snapshots.
- Product tags are optional and may move at different cadences.
- Runtime compatibility remains governed by semantic-contract, protocol, and format rules rather than suite tag name alone.
- Release manifests remain the machine-readable source of truth for actual artifact versions and hashes.

## Fork Policy

- Forks must not reuse official signer ids.
- Forked suite versions must use an explicit fork prefix such as `fork.<org>.v0.0.0-mock`.
- Fork-specific release indices should bind their own governance profile and trust roots.

## Archive Binding

- Every suite tag should have a matching release-index history snapshot.
- Archive records should retain:
  - suite tag
  - release id
  - release manifest hash
  - release index hash
  - component graph hash
  - semantic contract registry hash
