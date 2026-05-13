# Build Contract

Status: PROVISIONAL

Phase: POST-CONVERGE-10

## Purpose

Dominium build proof now follows this architecture:

```text
contracts/build -> machine probe -> generated local presets -> CMake -> CTest -> evidence
```

CMake remains the build executor. CTest remains the native test runner. AIDE, XStack, RepoX, and TestX orchestrate and prove build state; they do not replace CMake.

## Contract Layer

The build contract is split by concern:

| File | Role |
| --- | --- |
| `contracts/build/floors.toml` | OS/runtime floor registry |
| `contracts/build/toolchains.toml` | compiler, SDK, and generator families |
| `contracts/build/tuples.toml` | concrete configure/build/test lanes |
| `contracts/build/artifacts.toml` | generated artifact identity and evidence rules |
| `contracts/build/build_contract.schema.json` | broad contract shape for validators |

## Tuple Definition

A tuple combines:

- intent
- floor
- architecture
- toolchain
- runtime linkage
- configuration
- product set
- platform surface
- renderer surface

The provisional tuple pattern is:

```text
<intent>.<floor>.<arch>.<toolchain>.<runtime>.<config>
```

Example:

```text
verify.winnt10.x64.msvc143.mt.debug
```

## Preset Authority

`CMakePresets.json` is the stable shared entry surface. It must stay small enough to review and must not contain machine-local absolute paths.

`CMakeUserPresets.json` and `.dominium.local/` are generated local surfaces. They may contain host-specific details, but they are ignored and are not source authority.

## Support Claims

A tuple can only support a release or product claim after evidence exists for the required proof level:

- probe
- configure
- build
- test
- package

Matrix rows under `docs/release/` and `contracts/release/` must not be promoted by declarations alone.

## Distribution Relationship

Build tuples produce native binaries and build evidence. Package and portable projection contracts consume those outputs later; POST-CONVERGE-10 does not create public release artifacts or package bytes.
