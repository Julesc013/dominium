Status: CANONICAL
Last Reviewed: 2026-05-21
Supersedes: none
Superseded By: none
Stability: provisional

# Platform Support Policy

Release platform support is governed by the portability matrix. A release artifact is supported only when its platform floor, architecture, toolchain, product mode, package mode, runtime/provider capabilities, and release evidence are all declared.

`release_candidate` requires current release gate evidence. `supported` requires build, smoke, product, package, and release evidence. Planned, research, experimental, and provisional rows must not be presented as supported.

When a target is retired or removed later, version/deprecation law and replacement protocol must define migration, compatibility, or refusal behavior. Existing packs, saves, profiles, and release artifacts must not silently reinterpret platform support.

If a user requests an unsupported platform, architecture, toolchain, provider, product mode, or release artifact, the product must return typed portability diagnostics and refusal codes with recovery guidance.
