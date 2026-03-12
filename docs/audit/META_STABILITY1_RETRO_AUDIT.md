Status: DERIVED
Last Reviewed: unknown
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: canon-aligned documentation set for convergence and release preparation

# META-STABILITY-1 Retro Audit

## Scope

Validated every file under `data/registries` with the META-STABILITY validator, including:

- common `record.<collection>[]` registries
- root `records[]` registries
- multi-collection registries
- singleton-entry registries
- legacy line registries:
  - `data/registries/control_capabilities.registry`
  - `data/registries/law_targets.registry`

## Global Baseline

- registry files scanned: `387`
- detected registry entries: `3329`
- already tagged entries: `426`
- missing stability markers: `2903`
- current tagged class counts:
  - `stable`: `31`
  - `provisional`: `395`
  - `experimental`: `0`

## Existing Status-Like Fields

Existing registry payloads already use fields such as:

- `status`
- `deprecated`
- `stub`
- `legacy_status`

These fields are not substitutes for `stability`. They describe local behavior or lifecycle notes, not the release-governed change discipline required by META-STABILITY.

## Safe Insertion Points

The safest non-breaking insertion points are:

- sibling `stability` on each existing dict entry
- sibling `stability` on singleton entry dicts such as `record.default_session_spec_template` and `record.run_mode`
- companion tagged dict collections for scalar-list registries that must preserve current loader inputs
- comment-prefixed stability blocks for legacy `.registry` files consumed as line registries

The wrapper form:

```json
{
  "id": "...",
  "stability": { "...": "..." },
  "data": { "...existing payload..." }
}
```

was not selected because it would move required existing fields and risks breaking current loaders.

## Registry Shape Findings

The repository currently uses these entry shapes:

- `record.<collection>[]`
- root `records[]`
- multiple dict collections in the same file
- singleton entry dicts under `record`
- scalar-list registries that need tagged companion entry collections
- legacy text registries with one semantic item per non-comment line

Special handling is required for:

- `data/registries/fluid_model_registry.json`
- `data/registries/intent_dispatch_whitelist.json`
- `data/registries/controlx_policy.json`
- `data/registries/session_defaults.json`
- `data/registries/survival_vertical_slice.json`
- `data/registries/control_capabilities.registry`
- `data/registries/law_targets.registry`

## Highest-Volume Untagged Registries

Largest current untagged surfaces by entry count:

- `data/registries/extension_interpretation_registry.json`: `275`
- `data/registries/action_template_registry.json`: `221`
- `data/registries/inspection_section_registry.json`: `105`
- `data/registries/explain_contract_registry.json`: `95`
- `data/registries/provenance_classification_registry.json`: `75`
- `data/registries/capability_registry.json`: `57`
- `data/registries/interaction_action_registry.json`: `56`
- `data/registries/instrument_type_registry.json`: `52`
- `data/registries/law_targets.registry`: `49`
- `data/registries/info_artifact_family_registry.json`: `46`

## Rare Immediate Stable Candidates

Stable should remain small in MVP. The rare immediate stable surfaces are:

- semantic contract registry entries
- CAP-NEG negotiation modes and degrade ladder semantics already pinned to `contract.cap_neg.negotiation.v1`
- pack degrade semantics already pinned to `contract.pack.compat.v1`
- time anchor policy as a special review candidate for this sweep

Everything else should default to `provisional` unless there is a clear contract-pinned reason not to.
