Status: PROVISIONAL
Phase: CONVERGE-04
Machine-Readable Authority: `contracts/distribution/layout.contract.toml`

# Portable Install Layout

A compressed archive extraction must produce a valid portable install. No second install step, host registry entry, or absolute host path is required for portable mode.

Portable identity is self-describing and manifest-driven. The install root and store root may be the same physical tree, with mutable roots adjacent to immutable payloads.

## Example Tree

```text
DominiumPortable/
  install.manifest.json
  semantic_contract_registry.json
  release.manifest.json
  bin/
  descriptors/
  store/
    packs/
    profiles/
    locks/
  instances/
  saves/
  exports/
  logs/
  runtime/
    ipc/
    locks/
    temp/
  cache/
  ops/
    transactions/
  docs/
  LICENSES/
```

## Logical Root Mapping

| Logical root | Portable path |
| --- | --- |
| `INSTALL_ROOT` | `./` |
| `BIN_ROOT` | `bin/` |
| `DESCRIPTOR_ROOT` | `descriptors/` |
| `STORE_ROOT` | `store/` |
| `PACK_ROOT` | `store/packs/` |
| `PROFILE_ROOT` | `store/profiles/` |
| `INSTANCE_ROOT` | `instances/` |
| `SAVE_ROOT` | `saves/` |
| `EXPORT_ROOT` | `exports/` |
| `LOG_ROOT` | `logs/` |
| `RUNTIME_ROOT` | `runtime/` |
| `CACHE_ROOT` | `cache/` |
| `OPS_ROOT` | `ops/` |
| `DOC_ROOT` | `docs/` |
| `REDIST_ROOT` | `redist/` when shipped |
| `STORE_LOCK_ROOT` | `store/locks/` |
| `RUNTIME_LOCK_ROOT` | `runtime/locks/` |
| `OPS_TRANSACTION_ROOT` | `ops/transactions/` |

## Lock Split

`store/locks/` holds deterministic pack, content, capability, compatibility, and store-resolution locks. `runtime/locks/` holds process and IPC locks. `ops/transactions/` holds setup/update/rollback state.

Do not collapse these into one generic portable `locks/` doctrine.

## Identity Rules

- `install.manifest.json`, `semantic_contract_registry.json`, and `release.manifest.json` pin install and release identity.
- Hash identity is computed from content and manifests, not host path.
- Portable copies remain valid after directory copy when manifests and payloads are intact.
- Portable mode does not imply a gameplay/runtime mode flag.
