Status: CANONICAL
Last Reviewed: 2026-01-29
Supersedes: none
Superseded By: none
STATUS: CANONICAL
OWNER: architecture
LAST_VERIFIED: 2026-01-29

# Application Automation Model (APP-AUTO-0)

This document is the canonical representation of PROMPT APP-AUTO-0.

Normative rules:
- Application contracts are pure data POD and must not depend on engine/game headers.
- A shared UI-free appcore is mandatory; UI binds to the canonical command graph only.
- Win32 GUI shells are allowed, but must be IR-driven and behavior-free.
- CMake presets must allow VS 2026 to open/build application targets without manual edits.
- RepoX metadata must be surfaced by launcher/setup/tools.
