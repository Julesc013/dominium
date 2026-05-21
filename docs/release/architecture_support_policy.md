Status: CANONICAL
Last Reviewed: 2026-05-21
Supersedes: none
Superseded By: none
Stability: provisional

# Architecture Support Policy

Release support is not inferred from source layout, folders, build presets, or installed toolchains. Architecture support is a validated claim with evidence.

## Full Native Release Claim

A `source_native_64` full native release claim requires:

```text
architecture
word size
endianness
ABI
toolchain
language baseline
provider capability status
build evidence
smoke evidence
product evidence
package evidence
release evidence
limitations
diagnostics
refusals
```

The mainline native architectures are `x86_64` and `arm64`.

## Non-Mainline Lanes

32-bit native targets are constrained or research lanes. Legacy and vintage systems use constrained-native, projection, replay/snapshot client, or archive-runner paths. They must not be described as full native product support unless a future reviewed policy changes the architecture tier and evidence requirements.

## Refusal

Unsupported architecture requests use typed diagnostics and refusals. A missing architecture, missing endian declaration, missing word-size declaration, missing evidence, pointer-width persisted format, or legacy target requiring projection must refuse or degrade explicitly.

No release is produced by the architecture policy itself.
