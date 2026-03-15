Status: DERIVED
Last Reviewed: 2026-03-14
Stability: provisional
Future Series: RELEASE-INDEX
Replacement Target: signed multi-source release indices with trust-ranked provider selection

# Release Index Resolution Policy

## Versioning Layers

### Suite Version

- Human-facing curated snapshot identifier.
- Used for release notes, archive records, and suite tags.
- Does not determine runtime compatibility on its own.

### Product Version

- SemVer for an individual product or component candidate.
- Used for deterministic latest-compatible ranking.

### Semantic Contract Version

- Governs simulation compatibility.
- Incompatible semantic-contract bundles must refuse update or install-plan resolution.

### Protocol Version

- Governs wire compatibility.
- Candidate selection must not bypass the negotiated protocol-range checks.

### Format Version

- Governs save/profile/pack/lock structure.
- Format compatibility remains loader/migration-policy governed and separate from suite version.

## Installation Policies

### `policy.exact_suite`

- Install exactly the component descriptors pinned by the suite snapshot.
- Uses the component graph as the authoritative component-selector set.
- Allows yanked descriptors when they are part of the pinned suite snapshot.
- Emits warnings or refusals according to the descriptor `yank_policy`.
- Frozen under `contract.release.resolution.exact_suite.v1`.

CLI alias: `exact_suite`

### `policy.latest_compatible`

- For each selected `component_id`, choose the highest compatible candidate satisfying:
  - semantic contract compatibility
  - protocol compatibility
  - trust policy
  - target matrix constraints
  - component graph dependency requirements
- Yanked candidates are excluded.
- Deterministic tie-break order:
  - higher `version` (SemVer)
  - then higher `build_id`
  - then lexicographically higher `artifact_id`
- `artifact_id` is currently carried in descriptor `extensions.artifact_id` for policy ranking.
- Frozen under `contract.release.resolution.latest_compatible.v1`.

CLI alias: `latest_compatible`

### `policy.lab`

- Uses the same candidate ranking rules as `policy.latest_compatible`.
- Allows experimental/provisional candidates when trust and contract constraints still pass.
- Allows yanked candidates only because the operator explicitly selected lab policy.
- Selecting `--policy lab` is the explicit confirmation for non-interactive flows.

CLI alias: `lab`

## Deterministic Resolution Rules

- Candidate grouping is by canonical `component_id`.
- Release-index component candidates are sorted deterministically by:
  - `component_id`
  - `version`
  - `build_id`
  - `artifact_id`
  - `content_hash`
- Component-graph traversal remains the source of dependency closure.
- Candidate selection happens only after deterministic component-graph resolution.
- Conflict resolution remains deterministic and explicit.

## Yanked Builds

Component descriptors may declare:

- `yanked`
- `yank_reason`
- `yank_policy`

Rules:

- `policy.latest_compatible` excludes yanked candidates and logs `explain.component_skipped_yanked`.
- `policy.exact_suite` may still select the pinned descriptor.
- `policy.lab` may still select yanked descriptors because the operator explicitly opted into lab behavior.
- If a selected descriptor has `yank_policy=warn`, the resolver emits a deterministic warning.
- If a selected descriptor has `yank_policy=refuse`, the resolver refuses deterministically.

## Rollback Discipline

Install transactions must record:

- `from_release_id`
- `to_release_id`
- `install_plan_hash`
- `prior_component_set_hash`
- `resolution_policy_id`

Rollback rules:

- rollback is deterministic reverse application from the transaction log
- no partial state is committed
- rollback must preserve the prior managed component set hash
- store GC must respect the rollback retention window and not delete reachable rollback artifacts

## Explainability

Resolvers must log:

- `explain.policy_applied`
- `explain.component_selected`
- `explain.component_skipped_yanked`

These explanations must be deterministic and included in machine-readable outputs.

## Changelog Layering

1. `CHANGELOG.md`
   - suite-level curated change summary
2. per-product changelog surfaces
   - product-specific change narrative
3. `release_manifest.json`
   - authoritative machine-readable version map for shipped artifacts
