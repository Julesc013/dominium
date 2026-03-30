Status: DERIVED
Stability: stable
Future Series: OMEGA
Replacement Target: Frozen ecosystem integrity baseline for v0.0.0-mock distribution gating.

# Ecosystem Verify Run

- result: `complete`
- platform_tag: `win64`
- deterministic_fingerprint: `3bd48e95a562475f877050a2223ffacc5c363726cf3bcdea2e088ac02947e426`
- baseline_present: `True`
- baseline_matches: `True`

## Resolved Profiles

- `install.profile.full` -> result=`complete`, components=`18`, plan=`efff3733556646fefc01e994cdd949d4b0c0ef2f07c2edbbcaf8c59a117ee091`
- `install.profile.server` -> result=`complete`, components=`11`, plan=`0c1fa27dd9a9ee7e0dc17f6444ed9f349552fd8153e26e1ec68ebcea7bcec141`
- `install.profile.tools` -> result=`complete`, components=`5`, plan=`942e1059269686f1987a7a1be9954e668bce88961c3d2146438cb8baeeb4da9b`

## Identity Coverage

- result: `complete`
- governed_identity_paths: `11`
- invalid_identity_paths: `0`
- binary_identity_result: `complete`

## Migration Coverage

- result: `complete`
- artifact_kinds: `12`
- policies: `12`

## Trust Coverage

- result: `complete`
- selected_trust_policy_id: `trust.default_mock`
- governance_hash_matches_release_index: `True`

## Update Coverage

- result: `complete`
- latest_compatible_plan_fingerprint: `3abfe57f79b0e2c4d29eb59d3185820ac7d1ab51bc4d67a7dc2634b2c53848e3`
- selected_yanked_component_ids: `none`
- skipped_yanked_count: `1`
