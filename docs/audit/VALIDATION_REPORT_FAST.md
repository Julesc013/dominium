Status: DERIVED
Last Reviewed: 2026-03-13
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-ARCHIVE
Replacement Target: regenerated validation run artifact

# Validation Report FAST

- Result: `refused`
- Fingerprint: `1829fbcd993ad24956805c1bfbec1caf3098df95db00150b54521390b1207b56`
- Suite count: `10`

| Suite | Result | Adapter | Errors | Warnings |
| --- | --- | --- | --- | --- |
| `validate.schemas` | `complete` | `compatx_schema_suite` | `0` | `0` |
| `validate.registries` | `refused` | `stability_registry_suite` | `4` | `0` |
| `validate.identity` | `complete` | `identity_suite` | `0` | `0` |
| `validate.contracts` | `complete` | `semantic_contract_suite` | `0` | `0` |
| `validate.packs` | `complete` | `pack_verification_suite` | `0` | `0` |
| `validate.negotiation` | `complete` | `negotiation_suite` | `0` | `0` |
| `validate.library` | `complete` | `library_manifest_suite` | `0` | `0` |
| `validate.time_anchor` | `complete` | `time_anchor_suite` | `0` | `0` |
| `validate.arch_audit` | `refused` | `arch_audit_suite` | `4` | `9` |
| `validate.determinism` | `complete` | `determinism_scan_suite` | `0` | `0` |

## Blocking Findings

- `validate.registries`: registry entries must declare stability [data/registries/toolchain_test_profile_registry.json]
- `validate.registries`: registry entries must declare stability [data/registries/toolchain_test_profile_registry.json]
- `validate.registries`: registry entries must declare stability [data/registries/toolchain_test_profile_registry.json]
- `validate.registries`: registry entries must declare stability [data/registries/toolchain_test_profile_registry.json]
- `validate.arch_audit`: registry entries must declare stability [data/registries/toolchain_test_profile_registry.json]
- `validate.arch_audit`: registry entries must declare stability [data/registries/toolchain_test_profile_registry.json]
- `validate.arch_audit`: registry entries must declare stability [data/registries/toolchain_test_profile_registry.json]
- `validate.arch_audit`: registry entries must declare stability [data/registries/toolchain_test_profile_registry.json]
