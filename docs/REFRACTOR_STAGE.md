# Refactor Stage Notes

Purpose
- Refactor the build and target graph to enforce product boundaries.
- Keep the repo buildable at all times with minimal, mechanical changes.
- Prepare for Visual Studio 2026 CMake workflows and Codex usage.

Invariants
- No intended runtime behavior changes unless required for build or boundary enforcement.
- No deletion of code; any removal from build is quarantined under legacy/ or docs/.
- No new third-party dependencies unless needed for Windows builds and vendored.
- Preserve C89/C90 + C++98 compatibility where the codebase targets it.

Rollback Strategy
- Each phase lands as a separate commit.
- To roll back, revert the last commit(s) for the phase.
- Quarantined legacy material stays in legacy/ with a README explaining why.
