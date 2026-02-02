Status: CANONICAL
Last Reviewed: 2026-01-29
Supersedes: none
Superseded By: none
STATUS: CANONICAL
OWNER: architecture
LAST_VERIFIED: 2026-01-29

# Dev/Ops Model (DEV-OPS-0)

This document is the canonical representation of PROMPT DEV-OPS-0.

Normative rules:
- IDE/toolchain support must include VS 2026 and Xcode; legacy toolchains remain supported.
- C89/C++98 enforcement is mandatory regardless of IDE choice.
- CMake presets must include dev/verify/release/legacy profiles.
- UI must be accessible, localizable, and IR-driven; UI contains no business logic.
- RepoX must generate changelogs from commits; SemVer is manual.
- Launcher/setup/tools must surface RepoX/TestX metadata.
- Offline and air-gapped operation must be supported.
