Status: DERIVED
Last Reviewed: 2026-05-20
Task: PUBLIC-SURFACE-REGISTRY-01

# Initial Public Surface Inventory

This inventory is conservative. It registers important umbrella surfaces first
and avoids declaring stability unless proof already exists.

| Candidate ID | Kind | Path | Owner | Proposed Stability | Proof Present | Compatibility Proof Present | Register Now | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `domino.engine.public_headers.v1` | `c_header` | `engine/include` | `engine` | `provisional` | yes | no | yes | API/ABI canon remains next. |
| `domino.runtime.public_headers.v1` | `c_header` | `runtime/include` | `runtime` | `provisional` | yes | no | yes | Runtime headers are visible but not frozen. |
| `dominium.game.public_headers.v1` | `c_header` | `game/include` | `game` | `provisional` | yes | no | yes | Game headers expose domain concepts but are not stable external API. |
| `dominium.launcher.headers.v1` | `c_header` | `apps/launcher/include` | `apps.launcher` | `internal` | yes | n/a | yes | Registered to avoid accidental public claim. |
| `dominium.setup.headers.v1` | `c_header` | `apps/setup/include` | `apps.setup` | `internal` | yes | n/a | yes | Product-specific include tree remains internal. |
| `dominium.workbench.modules.v1` | `module_descriptor` | `apps/workbench/module` | `apps.workbench` | `internal` | yes | n/a | yes | Workbench modules are not stable descriptors yet. |
| `dominium.schema.catalog.v1` | `schema` | `contracts/schema` | `contracts.schema` | `provisional` | yes | no | yes | Individual schema stability waits for schema/protocol law. |
| `dominium.registry.catalog.v1` | `registry` | `contracts/registry` | `contracts.registry` | `provisional` | yes | no | yes | Large registry catalog is not globally stable. |
| `dominium.package.contracts.v1` | `package_format` | `contracts/package` | `contracts.package` | `provisional` | yes | no | yes | Package format stability waits for trust/artifact tasks. |
| `dominium.content.packs.v1` | `package_format` | `content/packs` | `content` | `provisional` | partial | no | yes | Pack content root is visible and important. |
| `dominium.repo.layout.v1` | `registry` | `contracts/repo/layout.contract.toml` | `contracts.repo` | `stable_data_contract` | yes | policy only | yes | Strict repo layout validator proves this governance contract. |
| `dominium.repo.root_allowlist.v1` | `registry` | `contracts/repo/root_allowlist.toml` | `contracts.repo` | `stable_data_contract` | yes | policy only | yes | Strict root allowlist validator proves this governance contract. |
| `dominium.repo.naming.v1` | `registry` | `contracts/repo/naming.contract.toml` | `contracts.repo` | `provisional` | yes | no | yes | Naming validators still classify known warning debt. |
| `dominium.testing.test_tiers.v1` | `registry` | `contracts/testing/test_tiers.contract.toml` | `tools.test` | `provisional` | yes | no | yes | Created by FAST-STRICT-TEST-TIER-01. |
| `dominium.release.update_channels.v1` | `registry` | `release/updates` | `release` | `provisional` | partial | no | yes | Release/trust proof is outside this task. |
| `dominium.release.control_plane.v1` | `release_artifact` | `release` | `release` | `provisional` | partial | no | yes | Source control-plane surface, not generated release output. |
| `dominium.archive.generated.aide.v1` | `archive_record` | `archive/generated/aide` | `archive` | `historical` | yes | n/a | yes | Historical/generated evidence, not active source truth. |
| `dominium.public_surface.fixture_suite.v1` | `test_fixture` | `tests/contract/public_surface` | `tests.contract` | `fixture` | yes | n/a | yes | Validator fixture suite. |
| `dominium.retired.root_schema.v1` | `archive_record` | `schema` | `contracts.repo` | `retired` | yes | n/a | yes | Root-level schema is retired. |
| `dominium.retired.root_schemas.v1` | `archive_record` | `schemas` | `contracts.repo` | `retired` | yes | n/a | yes | Root-level schemas is retired. |

## Deferred Candidates

| Candidate | Reason Deferred |
| --- | --- |
| individual engine/runtime/game headers | API-ABI-CANON-01 should split and prove stable subsets. |
| command surfaces | COMMAND-SURFACE-01 owns command contract stability. |
| diagnostic codes | DIAGNOSTIC-CODE-REGISTRY-01 owns diagnostic code registry hardening. |
| save/replay formats | future schema/protocol and replay migration proof required. |
| provider ABI | PROVIDER-MODEL-01 owns provider surface law. |
| Workbench workspace format | Workbench validation slice remains blocked until Foundation Lock. |
