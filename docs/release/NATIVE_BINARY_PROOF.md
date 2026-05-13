# Native Binary Proof

## Status

- Phase: POST-CONVERGE-10
- Status: blocked

## Build Tuple

| Field | Value |
| --- | --- |
| tuple ID | `verify.host.host.host_default.host.debug` attempted as dry-run |
| toolchain | `host_default` |
| generator | none generated |
| config | `debug` |
| platform | `host` |
| renderer | `host` |
| proof level | probe only; configure/build/test blocked |

## Product Binaries

| Product | Target | Executable Name | Path | Present? | Notes |
| --- | --- | --- | --- | --- | --- |
| setup | `setup_cli` | `setup` | verify/local generated binary dir | no | no tuple configured |
| launcher | `launcher_cli` | `launcher` | verify/local generated binary dir | no | no tuple configured |
| client | `dominium_client` | `client` | verify/local generated binary dir | no | no tuple configured |
| server | `dominium_server` | `server` | verify/local generated binary dir | no | no tuple configured |
| tools | `dominium-tools` | `tools` | verify/local generated binary dir | no | no tuple configured |

## What This Proves

- The build contract, probe, local preset generator, and tuple runner exist.
- The local machine currently has no supported compiler/build-tool tuple.
- Native binaries remain missing.

## What This Does Not Prove

- product boot
- runtime/session proof
- portable projection proof
- public release support
- renderer or native GUI support
