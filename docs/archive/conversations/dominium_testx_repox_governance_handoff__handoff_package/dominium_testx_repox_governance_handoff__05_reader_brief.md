# Reader Brief — Dominium TestX RepoX Governance Handoff

## What This Chat Was About

This chat was about preserving and formalising the governance layer around Dominium / Domino: TestX, RepoX, build identity, application/UI rules, IDE/toolchain projections, authority-based demo/free distribution, control-layer containment, language/ABI policy, old OS support, and eventual cross-chat handoff. It was not primarily about adding gameplay content. The latest upstream canon pasted by the user is now controlling: architecture is closed, canon is locked, and future chats should implement, audit, optimise, and maintain rather than redesign.

The biggest change to preserve is versioning: earlier global-build-number ideas were superseded by BUILD-ID-0. Product SemVer remains manual. Release-grade GBN is centrally allocated only for beta/rc/release/hotfix and shared by all products in a release. BII is always present for dev/ci. No distributed artifact may lack GBN. Protocol/schema/API/ABI versions are orthogonal and mismatches refuse loudly.

The second major contribution is RepoX: IDEs are projections, not source of truth. CMake + TestX/RepoX own the build graph. IDE files should be generated/disposable under /ide except documented packaging inputs. The user supplied a strict legacy/modern toolchain matrix and later installed Windows 10 + VS2022 for MVP testing.

The third major contribution is authority-based distribution: demo/free/tourist/full/service experiences should use the same binaries/content and differ by authority/entitlement. Piracy is contained by denying durable value extraction, not by corrupting the core with DRM.

## Most Important Things to Know

- Latest upstream canon supersedes earlier assistant drafts.
- Architecture is closed; do not redesign.
- Core ontology: Assemblies, Fields, Processes, Agents, Law.
- Engine C89; game C++98; public headers parseable forever.
- BUILD-ID-0 replaces earlier build-number ideas.
- CLI is canonical; GUI/TUI bind to the same command graph.
- UI is data, never logic.
- Setup is only install mutation authority.
- Tools are read-only by default.
- IDEs are projections; CMake/TestX/RepoX own graph.
- Demo/free/full/tourist are authority profiles, not code forks.
- Control systems are optional external layers and non-interfering.
- Old OS support can be dropped by stopping new binaries, not by breaking old compatible binaries.
- VS2022/v141_xp is an MVP path, not archival replacement for VC7.1/VC6.

## Active Plans or Workstreams

WORKSTREAM-01 Dominium / Domino core engine and game, WORKSTREAM-02 Content system, packs, and zero-asset boot, WORKSTREAM-03 Application layer canon, WORKSTREAM-04 Renderers, platforms, and headless operation, WORKSTREAM-05 TESTX / VALIDATE verification system, WORKSTREAM-06 TESTX2 control layers and non-interference, WORKSTREAM-07 TESTX3 authority, demo, tourist, services, and piracy containment, WORKSTREAM-08 REPOX repository ownership and IDE projections, WORKSTREAM-09 Toolchain and legacy OS matrix, WORKSTREAM-10 TESTX4 language profiles and ABI discipline, WORKSTREAM-11 Policy-as-data and rules-to-checks automation, WORKSTREAM-12 Windows MVP build/test plan with VS2022

## Decisions Already Made

See DECISION-01 through DECISION-27 in the registers. Highest priority: DECISION-01, DECISION-06, DECISION-10, DECISION-21, DECISION-23.

## Pending Tasks

Start with TASK-01 through TASK-06: repo audit, canon index/status, build/version reconciliation, and IDE inventory.

## Open Questions

Highest priority: QUESTION-01 through QUESTION-08.

## Files / Artifacts / Prompts to Preserve

Preserve the Context Transfer Packet, latest upstream SYSTEM ROLE block, TESTX original prompt, TESTX2/TESTX3/REPOX prompts, TESTX4 proposal, Windows VS2022 MVP recommendation, repo tree snapshot, and this report package.

## What to Verify Before Acting

Verify CANON_INDEX, BUILD-ID-0 files/scripts, docs status headers, CMakePresets, CI, IDE artifacts, public header parseability, language compliance, zero-asset boot tests, and VS2022 toolsets/SDKs.

## Best Next Step

Run a Phase 0 audit of the actual repo before changing code: canon docs, build/version files, CMake/CI, IDE artifacts, APP/UI binding, and language/profile compliance.
