Status: CANONICAL
Last Reviewed: 2026-05-21
Supersedes: none
Superseded By: none
OWNER: architecture
LAST_VERIFIED: 2026-05-21
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: canon-aligned documentation set for convergence and release preparation

# Dev/Ops Model (DEV-OPS-0)

This document is the canonical representation of PROMPT DEV-OPS-0.

Normative rules:
- IDE/toolchain support must include VS 2026 and Xcode; legacy toolchains remain supported.
- C17/C++17 enforcement is mandatory for active mainline builds regardless of IDE choice.
- CMake presets must include dev/verify/release/legacy profiles.
- UI must be accessible, localizable, and IR-driven; UI contains no business logic.
- RepoX must generate changelogs from commits; SemVer is manual.
- Launcher/setup/tools must surface RepoX/TestX metadata.
- Offline and air-gapped operation must be supported.
