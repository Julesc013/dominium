Status: CANONICAL
Last Reviewed: 2026-03-11
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: canon-aligned documentation set for convergence and release preparation

# INSTALL_MANIFEST_BASELINE

## Purpose

LIB-1 defines `InstallManifest` as the deterministic identity record for a Dominium install. An install is a product set, not just a folder of binaries. It pins:

- `install_id`
- `install_version`
- `product_builds`
- `semantic_contract_registry_hash`
- `supported_protocol_versions`
- `supported_contract_ranges`
- `default_mod_policy_id`
- `store_root_ref`
- `mode`
- `deterministic_fingerprint`

## Portable And Linked Layout

Portable reference layout:

```text
<install_root>/
  install.manifest.json
  semantic_contract_registry.json
  bin/
  store/
  instances/
  saves/
```

Linked reference layout:

```text
<install_root>/
  install.manifest.json
  semantic_contract_registry.json
  bin/
  (store_root_ref points to the shared store)
```

Descriptor sidecars may live adjacent to binaries under `bin/`.

## Product Build Identity

- Each present product publishes a `product_build_descriptor`.
- Descriptors pin `binary_hash` and `endpoint_descriptor_hash`.
- The install validator recomputes file hashes and verifies the bundled semantic contract registry hash.

Refusal surfaces:

- `refusal.install.missing_binary`
- `refusal.install.hash_mismatch`
- `refusal.install.contract_registry_mismatch`

## Multiple Install Coexistence

- Global host registration lives in `data/registries/install_registry.json`.
- Registry entries contain `install_id`, `path`, `version`, and `semantic_contract_registry_hash`.
- Registry ordering is deterministic by `install_id`.
- Fork coexistence is legal as long as `install_id` stays unique.

Suggested fork format:

- `fork.<origin>.<name>.<build_id>`

## Launcher Selection Rules

- Instances may pin `required_product_builds`.
- Instances may pin `required_contract_ranges`.
- Launcher preflight validates the selected install before pack checks.
- Inspect and replay flows may degrade to inspect-only on build mismatch; otherwise the launcher refuses with remediation.

## Readiness For LIB-2

LIB-1 is ready for `InstanceManifest` integration because instance manifests can now:

- reference installs deterministically by `install_id`
- pin required product builds
- pin required contract ranges
- remain portable or linked without path-derived identity

## Enforced Invariants

- `INV-INSTALL-MANIFEST-REQUIRED`
- `INV-INSTALL-NO-ABSOLUTE-PATH-DEPENDENCY`
- `INV-BINARY-HASH-MATCHES-MANIFEST`
