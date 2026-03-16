Status: DERIVED
Last Reviewed: 2026-03-13
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: RELEASE
Replacement Target: release-pinned artifact manifest generator and packaging baseline after RELEASE-1

# Release Identity Baseline

Fingerprint: `53e99968d06bba3a394ba1b39358dcd9c11711b6336c56c8e9fe48b33e461cc1`

## Build ID Inputs

- semantic contract registry hash
- compilation options hash
- source revision identifier if available, otherwise explicit build number
- product_id
- platform ABI tag only when unavoidable

## Governed Product Surfaces

| Product | SemVer Default | Descriptor Build Identity | Release Tag Example |
| --- | --- | --- | --- |
| `client` | `0.0.0` | `extensions.official.build_id` and `product_version + build_id suffix` | `v0.0.0-mock` |
| `engine` | `0.0.0` | `extensions.official.build_id` and `product_version + build_id suffix` | `v0.0.0-mock` |
| `game` | `0.0.0` | `extensions.official.build_id` and `product_version + build_id suffix` | `v0.0.0-mock` |
| `launcher` | `0.0.0` | `extensions.official.build_id` and `product_version + build_id suffix` | `v0.0.0-mock` |
| `server` | `0.0.0` | `extensions.official.build_id` and `product_version + build_id suffix` | `v0.0.0-mock` |
| `setup` | `0.0.0` | `extensions.official.build_id` and `product_version + build_id suffix` | `v0.0.0-mock` |
| `tool.attach_console_stub` | `0.0.0` | `extensions.official.build_id` and `product_version + build_id suffix` | `v0.0.0-mock` |

## Naming Templates

- binary: `<product_id>-<semver>+<build_id>-<platform_tag>`
- pack: `<pack_id>-<pack_version>-<pack_hash_prefix>`
- lock: `pack_lock-<hash_prefix>`
- bundle: `<bundle_kind>-<bundle_id>-<bundle_hash_prefix>`
- manifest: `manifest-<kind>-<hash_prefix>`

## Guarantees

- identical canonical inputs produce identical `build_id` values
- endpoint descriptors continue to carry deterministic build identity
- artifact names derive from content hashes and deterministic build IDs only

## Non-Guarantees

- bitwise-identical binaries across distinct toolchains are desirable but not guaranteed
- packaging/archive layout is not frozen by `RELEASE-0`

## Readiness

- Ready for `RELEASE-1` artifact manifest generation once release identity enforcement and tests stay green.
