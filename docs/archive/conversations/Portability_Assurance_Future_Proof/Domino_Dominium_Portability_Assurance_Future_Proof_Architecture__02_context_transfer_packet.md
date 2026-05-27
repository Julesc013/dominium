# 29. Context Transfer Packet for a Future Chat — Domino/Dominium Portability, Assurance, and Future-Proof Architecture

## 29.1 Ultra-Condensed Bootstrap Brief

This chat is a major architecture checkpoint for Domino/Dominium. It first asked whether standards such as DO-178B/C and related security/supply-chain frameworks should influence the project. The proposed answer was yes, but only as design input. Domino/Dominium should not claim aviation, automotive, medical, or industrial compliance. It should borrow useful patterns: traceability, requirements-based tests, tool-impact classification, review independence, secure-development practices, release provenance, SBOM/license metadata, and risk-based assurance.

The internal version proposed was DDAP v0, using DIL levels from low-risk experiments to external-impacting systems. Most ordinary game/content/UI work should stay light. Stronger controls should apply to trust-bearing paths such as saves, packs, mod loading, replay, authority/capability logic, installers/updaters, signed releases, multiplayer authority, native/offline clients, and automated execution. This is a recommendation, not yet a user-ratified decision.

The user then clarified the deeper issue: all code should be portable, modular, extensible, reusable, replaceable, and future-proof. The user wants Domino reused for other games and possibly other engine/game projects. They want files and directories replaceable during major rewrites. The desired standard is a proper long-lived platform, closer to OS-grade discipline than a one-off indie project.

The assistant’s strongest doctrine was stable outside, replaceable inside. Public contracts and persistent formats should be stable, versioned, documented, and tested. Internal implementation code should remain free to change. Public contracts include headers, save formats, pack formats, replay formats, protocols, schemas, command/result APIs, capability IDs, error codes, and migration rules. Private internals include helper files, algorithms, backend details, and non-public structs.

The conversation emphasized that directory structure is not enough. A real module needs an owner, purpose, public contract, private implementation, declared dependencies, forbidden dependencies, fixtures, conformance tests, versioning policy, diagnostics/error policy, and replacement criteria. The replacement test is whether a directory can be deleted and reimplemented against only public contracts while still passing the same tests and loading the same data.

Several concrete repo ideas were proposed: include/domino, include/dominium, contracts, source/domino, source/dominium, tests/conformance, tests/migration, tests/fuzz, tools/validators, docs/architecture, and docs/assurance. These are proposals; the actual repo was not inspected.

API/ABI discipline was a major theme: opaque handles, desc structs with size/version/reserved fields, explicit allocator ownership, project-owned integer types, no platform handles in core APIs, no exposed private structs, no public bitfields, no C++ ABI across plugin boundaries, no global singleton state, and lifecycle labels such as experimental, stable, deprecated, internal, and removed.

Persistent data compatibility was treated as central. The assistant rejected raw struct dumps for long-lived saves. Instead it recommended v

## 29.2 Source Hierarchy

1. Direct user statements in this chat.
2. Explicit decisions accepted by the user.
3. Current task register.
4. Constraint register.
5. Artifact ledger.
6. Inferences.
7. Assistant suggestions not accepted by the user.
8. General model knowledge.

## 29.3 Operating Rules for Future Assistants

Preserve FACT / INFERENCE / UNCERTAIN / PROJECT-CONTEXT labels. Do not re-ask answered questions. Ask clarifying questions only when materially necessary. Verify stale facts. Do not invent repo details. Do not treat tentative assistant recommendations as final decisions. Preserve artifacts and IDs.

## 29.4 Active Workstreams

- **WORKSTREAM-01 — Standards-informed assurance profile**: Define a Domino/Dominium Assurance Profile that borrows useful assurance ideas without compliance claims. Status: Proposed.
- **WORKSTREAM-02 — Portable engine platform boundary**: Keep Domino reusable across games/projects through stable contracts and replaceable internals. Status: Active concern.
- **WORKSTREAM-03 — Directory/module structure and ownership**: Organise repo around ownership, public contracts, private implementation, tests, and replacement criteria. Status: Proposed.
- **WORKSTREAM-04 — Persistent data and compatibility**: Make saves/packs/replays/protocols/schemas versioned, migratable, and safe. Status: Proposed.
- **WORKSTREAM-05 — Determinism and replay**: Make deterministic state transition and replay validation architectural features. Status: Proposed.
- **WORKSTREAM-06 — Conformance, validation, and tooling**: Make modularity mechanically testable. Status: Proposed.
- **WORKSTREAM-07 — Setup, launcher, tools, and UI boundaries**: Keep setup/launcher/tools/UI as contract consumers, not privileged engine internals. Status: Proposed.
- **WORKSTREAM-08 — Chat preservation and spec-book aggregation**: Preserve this chat into human-readable and structured artifacts. Status: Completed by this response.

## 29.5 Current Priorities

1. Confirm recommendations that become project canon.
2. Inspect actual repo.
3. Draft public API and data evolution policies.
4. Create registries.
5. Pick one conformance-test pilot.
6. Verify external standards.
7. Feed into master spec with caveats.

## 29.6 Current Open Questions

- **QUESTION-01**: Is DDAP v0 accepted as project direction or only a recommendation pending user review?
- **QUESTION-02**: What is the current actual repo structure?
- **QUESTION-03**: Which public boundaries must be stable first?
- **QUESTION-04**: How strict should C89/C++98 portability be across all code?
- **QUESTION-05**: What should be the first pilot module for conformance/replacement testing?
- **QUESTION-06**: What exact compatibility promises should be made for saves, packs, mods, and protocols?
- **QUESTION-07**: Which external standards claims need verification before formal spec use?

## 29.7 Recommended First Action

Inspect the actual repository and produce a boundary audit: public headers, private implementation areas, persistent formats, schemas/protocols, tests, and dependency leaks. Then decide which proposed policies become enforceable first.
