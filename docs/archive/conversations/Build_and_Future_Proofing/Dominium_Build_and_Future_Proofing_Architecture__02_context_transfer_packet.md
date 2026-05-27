# Context Transfer Packet for a Future Chat — Dominium Build and Future-Proofing Architecture

## 29.1 Ultra-Condensed Bootstrap Brief

This chat concerned Dominium's long-term engineering governance. The user began from strict canon: C89 engine, C++98 game layer, deterministic/fixed-point behavior, RepoX/TestX governance, separate artifacts per OS floor, no CRT mixing, and no silent API creep. The first active question asked how to manage many machines and toolchains: VS2017 on one Win10 laptop, VS2022/VS2026 and XP toolchains on a desktop, and legacy VMs/hardware for VS2010, VS2005, VC6, VC1.5, Xcode 9, CodeWarrior Pro 9, etc.

The recommended answer was tuple-driven build governance: do not hand-maintain a giant `CMakePresets.json`. Instead, declare build tuples in contracts, probe each machine, generate local `CMakeUserPresets.json`, run CMake/CTest, collect TestX/RepoX proof, and preserve package/dist manifests. CMake remains build authority. AIDE probes, explains, generates local presets, verifies tuples, and records evidence. XStack orchestrates. RepoX/TestX enforce/prove.

The user then widened the question to modularity and portability. They want Dominium code reusable for other games on the Domino engine and potentially for other engine/game projects. They want future rewrites of whole files/directories to be possible without breaking compatibility. The response recommended treating Dominium as a portable deterministic engine platform with one game mounted on top: stable contracts first, replaceable implementations second, products third, presentation last. The current top-level structure appears close to correct, but deeper work remains: public surface registry, dependency-edge contract, ABI/header conformance, schema/protocol compatibility harness, replacement protocol, game/domain cleanup, content pack authority cleanup, and build tuple contracts.

Important: many recommendations are not explicitly accepted user decisions yet. Preserve FACT/INFERENCE/UNCERTAIN/PROJECT-CONTEXT labels. Verify current repo state before acting.

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

Preserve uncertainty labels. Do not re-ask answered questions. Ask only materially necessary clarifying questions. Verify stale repo/toolchain facts. Do not invent missing details. Do not treat tentative recommendations as final. Do not repeat rejected options. Preserve artifacts and IDs. Use structured outputs when continuing.

## 29.4 Active Workstreams

- WORKSTREAM-01: Build/toolchain governance.
- WORKSTREAM-02: Repo/source structure.
- WORKSTREAM-03: Public surface governance.
- WORKSTREAM-04: Replacement protocol.
- WORKSTREAM-05: Schema/protocol compatibility.
- WORKSTREAM-06: Preservation/aggregation.

## 29.5 Current Priorities

1. Decide which recommendations become canon.
2. Verify live repo state.
3. Add public surface registry.
4. Add build tuple contracts and machine probe.
5. Add dependency and compatibility enforcement.

## 29.6 Current Open Questions

- Which recommendations are accepted?
- What is current live repo HEAD and CI/build status?
- Which public surfaces are frozen/stable/internal?
- Which floors are MVP versus archival?

## 29.7 Recommended First Action

Ask the user to choose whether the next implementation focus is `STRUCTURE-01: Public Surface Registry` or `BUILD-CONTRACT-01: Tuple Build Contracts and Machine Probe`, then verify current repo state before editing.
