Status: DERIVED
Last Reviewed: 2026-03-13
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-ARCHIVE
Replacement Target: regenerated validation run artifact

# Validation Report STRICT

- Result: `refused`
- Fingerprint: `296275ba3e0ee6d5076a8cbc3145a49eaf9ca7417d0cf69314294c4c38a6e351`
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
