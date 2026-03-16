Status: DERIVED
Last Reviewed: 2026-03-16
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: canon-aligned documentation set for convergence and release preparation

# META-STABILITY-1 Fix Plan

## Must-Fix For v0.0.0

### 1. Bulk missing-marker coverage

Apply a `stability` marker to every untagged dict entry across all registry files.

Default:

- `stability_class_id: provisional`
- `rationale: MVP stub or first implementation`
- `future_series`: family-specific
- `replacement_target`: short deterministic replacement plan

### 2. Scalar-list registries

Preserve existing loader-facing scalar arrays and add companion tagged entry collections for:

- `data/registries/fluid_model_registry.json`
- `data/registries/intent_dispatch_whitelist.json`
- `data/registries/controlx_policy.json`
- `data/registries/survival_vertical_slice.json`

### 3. Singleton entry dicts

Add sibling `stability` to singleton entries:

- `data/registries/session_defaults.json` -> `record.default_session_spec_template`
- `data/registries/controlx_policy.json` -> `record.run_mode`

### 4. Legacy text registries

Keep the line-registry format loadable and add comment-block stability metadata before each semantic line in:

- `data/registries/control_capabilities.registry`
- `data/registries/law_targets.registry`

### 5. Stable/provisional correction pass

Explicitly verify and correct the release-sensitive areas:

- SOL-1 illumination geometry registries
- SOL-2 orbit/ephemeris registries
- GAL-0 and GAL-1 registries
- EARTH-10 proxy registries
- CAP-NEG degrade ladders and negotiated modes
- pack compatibility registries
- library/provider registries
- negotiation mode registries
- time anchor policy registry

### 6. Enforcement upgrade

Move RepoX, AuditX, TestX, and ARCH-AUDIT stability scans from scoped META-STABILITY-0 coverage to full `data/registries` coverage.

## Acceptable Provisional Posture

The default release posture for MVP remains conservative:

- stable only for contract-pinned semantics
- provisional for first implementations, stubs, proxy layers, and replaceable default models
- experimental only when an explicit profile/entitlement gate already exists

## Exact Non-Breaking Conventions

- dict entry registries: add sibling `stability`
- singleton entry dicts: add sibling `stability`
- scalar-list registries: retain the scalar list and add companion tagged dict entries
- legacy `.registry` files: retain the line format and add preceding `# key: value` stability comments

## Validation After Sweep

Re-run:

- global stability validator
- RepoX META-STABILITY checks
- AuditX missing/provisional/stable-contract analyzers
- TestX tagging coverage
- ARCH-AUDIT tool
- TIME-ANCHOR tests
- MVP smoke/stress checks as far as current repo debt allows
