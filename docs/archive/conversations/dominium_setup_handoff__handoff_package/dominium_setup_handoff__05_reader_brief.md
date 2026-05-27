# Reader Brief — Dominium Setup Handoff

## What This Chat Was About

This chat was primarily about the Dominium / Domino Setup system: a deterministic, auditable, reversible installer/updater/verifier/rollback authority. It began with cross-platform setup architecture and directory planning, then shifted to canonical repository alignment, build enforcement, engine purity, schema handoff, application-layer canon, and finally context transfer/report packaging.

The most important outcome is that setup is the only component allowed to install files, modify installation/system state, verify/repair installations, perform rollback, and enforce package layout. Launcher may invoke setup and read its outputs, but may not reimplement setup logic. Engine must not know setup exists.

Earlier proposed layouts using `setup/adapters`, adapter-local packaging, and `core/source` were superseded. The canonical setup layout is `setup/core/{fetch,verify,install,rollback}`, `setup/include/{dsk,dsu}`, `setup/packages`, `setup/platform`, `setup/tests`, and `setup/ui`.

The user stated that two large Codex prompts had already been applied: one for VS2026/CMake/build repair and one for engine purity/contract ownership. A further prompt was generated in this chat to finish setup code/docs/spec alignment. Actual repo state after those prompts was not verified in this chat.

## Most Important Things to Know

- Setup is sole installation mutation authority.
- Launcher invokes setup; launcher does not repair/install directly.
- Engine must remain pure and unaware of setup.
- Setup depends only on `libs/` and `schema/`.
- Public setup APIs live in `setup/include/dsk` and `setup/include/dsu`.
- Packaging belongs under `setup/packages/`.
- Cross-product contracts belong in `libs/contracts/include/dom_contracts`.
- CMake is authoritative; IDE projects are generated, not source of truth.
- Use C/C++ for setup execution, not .NET.
- CLI is canonical; GUI/TUI are views.
- UI is declarative data, not business logic.
- RepoX/TestX and BUILD-ID-0 govern release metadata and validation.
- Existing implementation is authoritative unless it violates locked rules.
- Do not delete code; quarantine under `legacy/`.
- Actual repo state must be verified before acting.

## Active Plans or Workstreams

- WORKSTREAM-01: Setup / Installer System
- WORKSTREAM-02: Canonical Repository and Build Enforcement
- WORKSTREAM-03: Engine Purity and Contract Ownership
- WORKSTREAM-04: Setup Schemas and Launcher Handoff
- WORKSTREAM-05: Application Layer Canon
- WORKSTREAM-06: Packaging/Reproducibility/Offline-Online Install
- WORKSTREAM-07: UI Frontend and Command Graph
- WORKSTREAM-08: RepoX/TestX/BUILD-ID Governance
- WORKSTREAM-09: Legacy Platform Support
- WORKSTREAM-10: Context Transfer/Report Packaging

## Decisions Already Made

- Setup sole authority.
- Canonical setup directory layout.
- Setup depends only on libs/schema.
- Launcher reads setup outputs and invokes setup only.
- Engine purity and neutral contracts are mandatory.
- CMake is authoritative.
- CLI canonical, UI as data.
- Repair/update/downgrade are explicit, not hidden.
- Rollback is first-class and journaled.
- Existing implementation must be audited, not redesigned.

## Pending Tasks

- Verify actual repo state.
- Run CMake configure/build/test.
- Run setup and launcher CLI smoke tests.
- Execute or audit the generated setup hardening prompt.
- Verify schema/setup files.
- Verify libs/contracts.
- Verify engine purity enforcement scripts.
- Audit setup platform/UI/packages/tests/docs.

## Open Questions

- Did the applied Codex prompts fully succeed?
- Has the setup hardening prompt been executed?
- What is the current setup/ tree?
- What setup schemas exist?
- Does libs/contracts compile?
- Are setup/launcher CLIs runnable?
- Is app command spine implemented?
- Where exactly does UI IR live?

## Files / Artifacts / Prompts to Preserve

- ARTIFACT-11 canonical repo/setup prompt.
- ARTIFACT-14 applied VS2026/CMake refactor prompt.
- ARTIFACT-15 applied engine purity/contract prompt.
- ARTIFACT-17 generated setup hardening prompt.
- ARTIFACT-19/20 application/project canon prompts.
- ARTIFACT-22 previous Context Transfer Packet.
- This report package.

## What to Verify Before Acting

- `tree /f setup`
- `tree /f schema`
- `tree /f libs\contracts`
- root `CMakeLists.txt`
- `setup/CMakeLists.txt`
- `CMakePresets.json`
- `cmake --preset vs2026-x64-debug`
- `cmake --build --preset vs2026-x64-debug`
- `ctest --preset vs2026-x64-debug`
- `setup --help`
- `launcher --help`

## Best Next Step

Verify actual repository state, then execute or audit the generated “Dominium Setup: Final Spec Alignment, Gap Closure, and Hardening Pass” prompt.
