Status: DERIVED
Last Reviewed: 2026-03-10
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: canon-aligned documentation set for convergence and release preparation

# Extension Migration Notes

## Legacy Bare Keys
- Existing bare extension keys remain loadable in `extensions.default`.
- Default-mode compatibility treats bare keys as aliases of `mod.unknown.<key>`.
- This aliasing is metadata discipline only; it does not authorize new behavior.

## Strictness
- `extensions.default`: ignore unknown keys deterministically.
- `extensions.warn`: emit deterministic warnings for unknown and legacy bare keys.
- `extensions.strict`: refuse unknown namespaced keys; legacy bare keys still surface compatibility warnings so old data remains usable.

## Authoring Guidance
- New content must use namespaced keys only.
- New interpreted keys must be declared in `data/registries/extension_interpretation_registry.json`.
- New behavior semantics must also name the required semantic contract version.

## Compatibility Note
- Existing saves and packs are not silently rewritten by this task.
- Existing legacy bare-key usage remains replay-stable because canonical normalization preserves source payload shape while enforcing deterministic ordering.
