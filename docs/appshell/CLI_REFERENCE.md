Status: DERIVED
Last Reviewed: 2026-03-11
Supersedes: none
Superseded By: none

# CLI Reference

This reference is generated from `data/registries/command_registry.json` and
`data/registries/refusal_to_exit_registry.json`.

## Shared Commands

| Command | Description | Refusals |
| --- | --- | --- |
| `compat-status` | Run deterministic endpoint compatibility status and show negotiated mode plus disabled features. | `refusal.compat.contract_mismatch`, `refusal.compat.no_common_protocol`, `refusal.io.invalid_args` |
| `console` | Alias of `console enter` for deterministic REPL console access. | - |
| `descriptor` | Emit the CAP-NEG endpoint descriptor for the active product. | `refusal.io.invalid_args` |
| `diag` | Emit deterministic shell diagnostic metadata. | - |
| `help` | Show deterministic AppShell help generated from the command registry. | - |
| `packs` | Alias of `packs list` for deterministic pack enumeration. | `refusal.io.invalid_args` |
| `profiles` | Alias of `profiles list` for deterministic bundle enumeration. | - |
| `verify` | Alias of `packs verify` for offline pack/profile verification. | `refusal.io.invalid_args`, `refusal.pack.contract_range_mismatch`, `refusal.pack.registry_missing`, `refusal.pack.schema_invalid`, `refusal.pack.trust_denied` |
| `version` | Emit deterministic product version metadata and build identity. | - |
| `console enter` | Open the deterministic REPL console session stub for the current product. | - |
| `packs build-lock` | Verify packs offline and emit a deterministic pack lock plus compatibility report. | `refusal.io.invalid_args`, `refusal.pack.contract_range_mismatch`, `refusal.pack.registry_missing`, `refusal.pack.schema_invalid`, `refusal.pack.trust_denied` |
| `packs list` | List available pack manifests in deterministic order. | `refusal.io.invalid_args` |
| `packs verify` | Run the offline pack compatibility verification pipeline. | `refusal.io.invalid_args`, `refusal.pack.contract_range_mismatch`, `refusal.pack.registry_missing`, `refusal.pack.schema_invalid`, `refusal.pack.trust_denied` |
| `profiles list` | List available profile bundles in deterministic order. | - |
| `profiles show` | Show a single profile bundle by bundle id. | `refusal.io.invalid_args`, `refusal.io.profile_not_found` |

## Namespaces

| Namespace | Products | Description |
| --- | --- | --- |
| `client.*` | `client` | Reserved stable namespace for client-specific runtime commands. |
| `engine.*` | `engine` | Reserved stable namespace for engine product commands. |
| `game.*` | `game` | Reserved stable namespace for game product commands. |
| `geo.*` | `client`, `tool.attach_console_stub` | Reserved stable namespace for GEO explain and inspection commands. |
| `launcher.*` | `launcher` | Reserved stable namespace for launcher product commands. |
| `logic.*` | `client`, `tool.attach_console_stub` | Reserved stable namespace for logic compile, probe, and trace commands. |
| `server.*` | `server` | Reserved stable namespace for server command surfaces. |
| `session.*` | `client`, `launcher`, `server`, `setup` | Reserved stable namespace for session lifecycle commands. |
| `setup.*` | `setup` | Reserved stable namespace for setup product commands. |
| `tool.*` | `tool.attach_console_stub` | Reserved stable namespace for tool product commands. |

## Refusal To Exit Mapping

| Refusal Match | Exit Code | Description |
| --- | --- | --- |
| `refusal.compat.*` | `30` | Compatibility and negotiation failures map to the contract/compatibility range. |
| `refusal.compat.feature_disabled` | `50` | Negotiated feature-disable refusals map to the refusal range. |
| `refusal.contract.*` | `30` | Contract mismatches map to the contract/compatibility range. |
| `refusal.debug.*` | `50` | Debug/gating refusals map to the refusal range except where explicitly overridden. |
| `refusal.debug.command_unknown` | `10` | Unknown registered-command tokens map to usage-range exits. |
| `refusal.io.*` | `40` | IO/host-shell failures map to the transport and IO-shell range. |
| `refusal.io.invalid_args` | `10` | Invalid command arguments map to usage-range exits. |
| `refusal.io.profile_not_found` | `20` | Missing profile bundles are treated as pack/profile surface failures. |
| `refusal.law.*` | `50` | Law refusals map to the refusal range. |
| `refusal.pack.*` | `20` | Pack validation and verification failures map to the pack/profile range. |
| `refusal.server.command_unknown` | `50` | Unknown live server console commands remain explicit refusal-range failures. |

## Product Views

### `client`

- `compat-status`: Run deterministic endpoint compatibility status and show negotiated mode plus disabled features.
- `console`: Alias of `console enter` for deterministic REPL console access.
- `descriptor`: Emit the CAP-NEG endpoint descriptor for the active product.
- `diag`: Emit deterministic shell diagnostic metadata.
- `help`: Show deterministic AppShell help generated from the command registry.
- `packs`: Alias of `packs list` for deterministic pack enumeration.
- `profiles`: Alias of `profiles list` for deterministic bundle enumeration.
- `verify`: Alias of `packs verify` for offline pack/profile verification.
- `version`: Emit deterministic product version metadata and build identity.
- `console enter`: Open the deterministic REPL console session stub for the current product.
- `packs build-lock`: Verify packs offline and emit a deterministic pack lock plus compatibility report.
- `packs list`: List available pack manifests in deterministic order.
- `packs verify`: Run the offline pack compatibility verification pipeline.
- `profiles list`: List available profile bundles in deterministic order.
- `profiles show`: Show a single profile bundle by bundle id.
- `client.*`: Reserved stable namespace for client-specific runtime commands.
- `geo.*`: Reserved stable namespace for GEO explain and inspection commands.
- `logic.*`: Reserved stable namespace for logic compile, probe, and trace commands.
- `session.*`: Reserved stable namespace for session lifecycle commands.

### `engine`

- `compat-status`: Run deterministic endpoint compatibility status and show negotiated mode plus disabled features.
- `console`: Alias of `console enter` for deterministic REPL console access.
- `descriptor`: Emit the CAP-NEG endpoint descriptor for the active product.
- `diag`: Emit deterministic shell diagnostic metadata.
- `help`: Show deterministic AppShell help generated from the command registry.
- `packs`: Alias of `packs list` for deterministic pack enumeration.
- `profiles`: Alias of `profiles list` for deterministic bundle enumeration.
- `verify`: Alias of `packs verify` for offline pack/profile verification.
- `version`: Emit deterministic product version metadata and build identity.
- `console enter`: Open the deterministic REPL console session stub for the current product.
- `packs build-lock`: Verify packs offline and emit a deterministic pack lock plus compatibility report.
- `packs list`: List available pack manifests in deterministic order.
- `packs verify`: Run the offline pack compatibility verification pipeline.
- `profiles list`: List available profile bundles in deterministic order.
- `profiles show`: Show a single profile bundle by bundle id.
- `engine.*`: Reserved stable namespace for engine product commands.

### `game`

- `compat-status`: Run deterministic endpoint compatibility status and show negotiated mode plus disabled features.
- `console`: Alias of `console enter` for deterministic REPL console access.
- `descriptor`: Emit the CAP-NEG endpoint descriptor for the active product.
- `diag`: Emit deterministic shell diagnostic metadata.
- `help`: Show deterministic AppShell help generated from the command registry.
- `packs`: Alias of `packs list` for deterministic pack enumeration.
- `profiles`: Alias of `profiles list` for deterministic bundle enumeration.
- `verify`: Alias of `packs verify` for offline pack/profile verification.
- `version`: Emit deterministic product version metadata and build identity.
- `console enter`: Open the deterministic REPL console session stub for the current product.
- `packs build-lock`: Verify packs offline and emit a deterministic pack lock plus compatibility report.
- `packs list`: List available pack manifests in deterministic order.
- `packs verify`: Run the offline pack compatibility verification pipeline.
- `profiles list`: List available profile bundles in deterministic order.
- `profiles show`: Show a single profile bundle by bundle id.
- `game.*`: Reserved stable namespace for game product commands.

### `launcher`

- `compat-status`: Run deterministic endpoint compatibility status and show negotiated mode plus disabled features.
- `console`: Alias of `console enter` for deterministic REPL console access.
- `descriptor`: Emit the CAP-NEG endpoint descriptor for the active product.
- `diag`: Emit deterministic shell diagnostic metadata.
- `help`: Show deterministic AppShell help generated from the command registry.
- `packs`: Alias of `packs list` for deterministic pack enumeration.
- `profiles`: Alias of `profiles list` for deterministic bundle enumeration.
- `verify`: Alias of `packs verify` for offline pack/profile verification.
- `version`: Emit deterministic product version metadata and build identity.
- `console enter`: Open the deterministic REPL console session stub for the current product.
- `packs build-lock`: Verify packs offline and emit a deterministic pack lock plus compatibility report.
- `packs list`: List available pack manifests in deterministic order.
- `packs verify`: Run the offline pack compatibility verification pipeline.
- `profiles list`: List available profile bundles in deterministic order.
- `profiles show`: Show a single profile bundle by bundle id.
- `launcher.*`: Reserved stable namespace for launcher product commands.
- `session.*`: Reserved stable namespace for session lifecycle commands.

### `server`

- `compat-status`: Run deterministic endpoint compatibility status and show negotiated mode plus disabled features.
- `console`: Alias of `console enter` for deterministic REPL console access.
- `descriptor`: Emit the CAP-NEG endpoint descriptor for the active product.
- `diag`: Emit deterministic shell diagnostic metadata.
- `help`: Show deterministic AppShell help generated from the command registry.
- `packs`: Alias of `packs list` for deterministic pack enumeration.
- `profiles`: Alias of `profiles list` for deterministic bundle enumeration.
- `verify`: Alias of `packs verify` for offline pack/profile verification.
- `version`: Emit deterministic product version metadata and build identity.
- `console enter`: Open the deterministic REPL console session stub for the current product.
- `packs build-lock`: Verify packs offline and emit a deterministic pack lock plus compatibility report.
- `packs list`: List available pack manifests in deterministic order.
- `packs verify`: Run the offline pack compatibility verification pipeline.
- `profiles list`: List available profile bundles in deterministic order.
- `profiles show`: Show a single profile bundle by bundle id.
- `server.*`: Reserved stable namespace for server command surfaces.
- `session.*`: Reserved stable namespace for session lifecycle commands.

### `setup`

- `compat-status`: Run deterministic endpoint compatibility status and show negotiated mode plus disabled features.
- `console`: Alias of `console enter` for deterministic REPL console access.
- `descriptor`: Emit the CAP-NEG endpoint descriptor for the active product.
- `diag`: Emit deterministic shell diagnostic metadata.
- `help`: Show deterministic AppShell help generated from the command registry.
- `packs`: Alias of `packs list` for deterministic pack enumeration.
- `profiles`: Alias of `profiles list` for deterministic bundle enumeration.
- `verify`: Alias of `packs verify` for offline pack/profile verification.
- `version`: Emit deterministic product version metadata and build identity.
- `console enter`: Open the deterministic REPL console session stub for the current product.
- `packs build-lock`: Verify packs offline and emit a deterministic pack lock plus compatibility report.
- `packs list`: List available pack manifests in deterministic order.
- `packs verify`: Run the offline pack compatibility verification pipeline.
- `profiles list`: List available profile bundles in deterministic order.
- `profiles show`: Show a single profile bundle by bundle id.
- `session.*`: Reserved stable namespace for session lifecycle commands.
- `setup.*`: Reserved stable namespace for setup product commands.

### `tool.attach_console_stub`

- `compat-status`: Run deterministic endpoint compatibility status and show negotiated mode plus disabled features.
- `console`: Alias of `console enter` for deterministic REPL console access.
- `descriptor`: Emit the CAP-NEG endpoint descriptor for the active product.
- `diag`: Emit deterministic shell diagnostic metadata.
- `help`: Show deterministic AppShell help generated from the command registry.
- `packs`: Alias of `packs list` for deterministic pack enumeration.
- `profiles`: Alias of `profiles list` for deterministic bundle enumeration.
- `verify`: Alias of `packs verify` for offline pack/profile verification.
- `version`: Emit deterministic product version metadata and build identity.
- `console enter`: Open the deterministic REPL console session stub for the current product.
- `packs build-lock`: Verify packs offline and emit a deterministic pack lock plus compatibility report.
- `packs list`: List available pack manifests in deterministic order.
- `packs verify`: Run the offline pack compatibility verification pipeline.
- `profiles list`: List available profile bundles in deterministic order.
- `profiles show`: Show a single profile bundle by bundle id.
- `geo.*`: Reserved stable namespace for GEO explain and inspection commands.
- `logic.*`: Reserved stable namespace for logic compile, probe, and trace commands.
- `tool.*`: Reserved stable namespace for tool product commands.
