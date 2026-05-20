Status: CANONICAL
Last Reviewed: 2026-05-21
Supersedes: none
Superseded By: none
Stability: provisional

# Portability Matrix

Portability is a matrix plus proof. A platform, compiler, renderer, package mode, product mode, or release artifact is not supported because code exists, because a preset exists, or because one local command succeeded.

The normative contract is `contracts/platform/portability_matrix.contract.toml`. Machine-readable rows live under `contracts/platform/*.registry.json` and `contracts/platform/*_portability.matrix.json`.

## Claim Shape

Every portability row declares target ID, target kind, platform floor, OS family/version floor, architecture, endianness, word size, toolchain, language floor, ABI, filesystem/path policy, dynamic loading, threading, networking, provider capabilities, product modes, support status, evidence, diagnostics, refusals, and limitations.

Target IDs are identity. Paths, folders, presets, installed compilers, and implementation names are evidence at most.

## Statuses

`unsupported`, `planned`, `research`, `experimental`, and `provisional` are not support claims.

`build_proven` requires build/configure evidence. `smoke_proven` requires smoke evidence. `product_proven` requires product boot/projection evidence. `release_candidate` requires release gate evidence. `supported` requires build, smoke, product, package, and release evidence.

## Platform Floors And Toolchains

Platform floors are registry entries, not product promises. Current rows include modern Windows host/headless proof lanes plus planned or research entries for legacy Windows, Linux, macOS, and portable package behavior.

Toolchains are registered with status and evidence. A local compiler installation is not support proof, and machine-local paths must not appear in support claims.

## Providers And Product Modes

Runtime, renderer, storage, package, audio, input, and network support must reference provider or capability IDs where available. Missing providers produce typed refusal or explicit degraded decisions; renderer fallback is never silent.

Product mode support must reference runtime/provider capabilities. CLI and headless proof lanes do not imply rendered, native, installer, or release support.

## Release And Packages

Package and release artifact rows must reference artifact/release evidence before support is claimed. Portable package mode is provisional until package and release proof exist.

## Diagnostics And Refusals

Unsupported platform, architecture, toolchain, provider, product mode, and unproven release requests use portability diagnostic and refusal codes from the central registries. Free-text refusal is not enough.
