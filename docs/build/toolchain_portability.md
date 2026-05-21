Status: CANONICAL
Last Reviewed: 2026-05-21
Supersedes: none
Superseded By: none
Stability: provisional

# Toolchain Portability

Toolchain rows do not define product architecture support by themselves. Architecture support is governed by `contracts/platform/architecture_policy.contract.toml`; build targets are summarized in `docs/build/architecture_targets.md`.

Toolchain portability is declared in `contracts/platform/toolchain.registry.json` and validated by `tools/validators/platform/check_portability_matrix.py`.

The active mainline language floor remains governed by `contracts/build/language_baseline.contract.toml`. Toolchain rows must state compiler family, version floor, language floor, ABI expectation, CRT/runtime expectation, support status, evidence, and known limitations.

MSVC v143 may be build-proven only when the current evidence path proves it. Legacy MSVC, VC6, CodeWarrior, GCC, Clang, and Xcode rows are registry entries with planned or research status until their own proof exists.

Generated local presets and local compiler discovery are not support claims. Do not commit machine-local paths, SDK install paths, or host-only assumptions as portability proof.

Full native product builds are `source_native_64` and target `x86_64` or `arm64`. Existing `x64` rows are a compatibility alias for `x86_64`.
