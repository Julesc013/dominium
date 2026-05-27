# Context Transfer Packet for a Future Chat — Dominium Language, Platform, and Architecture Baseline

## 29.1 Ultra-Condensed Bootstrap Brief

This prior chat established Dominium’s current architecture baseline. The mainline is no longer C89/C++98 and should not pivot to pure C99 or pure C++11. The accepted direction is C17 + C++17, 64-bit source-native, little-endian, with a C-compatible public ABI and fixed-width explicit data formats. C17 is for deterministic law and stable contracts: ABI structs, fixed-point math, stable IDs, packets, save/replay/wire records, renderer command IR, capability/refusal structs, and provider facades. C++17 is for machinery: game orchestration, domain systems, runtime services, providers, renderer/platform backends, apps, Workbench, tools, jobs, and resource ownership.

The central design rule is semantic, not folder-based: C owns law; C++ owns machinery. Raylib and SDL2 are allowed as providers/backends, but their C APIs do not require a pure-C engine. Public/stable boundaries must not expose C++ classes, STL containers, templates, exceptions, RTTI, allocator ownership, native object layout, raw pointers, size_t, uintptr_t, or platform handles.

Full native products should be 64-bit: x86_64 and arm64. 32-bit and extreme legacy targets are constrained-native, contract-projection, or archive lanes. There is no universal primitive binary for Windows 98, Mac OS 9, modern consoles, and desktop OSes simultaneously. The common law is contracts, packets, replay/save formats, renderer IR, providers, and tests.

The larger architecture is: apps compose modules; modules require services; services are implemented by providers; providers declare capabilities; packs provide data/modules/content; profiles select packs/settings; contracts define compatibility; lockfiles make composition reproducible; commands invoke behavior; artifacts record results; tests prove behavior; Workbench operates it; AIDE governs it.

Current immediate blocker: Foundation Lock is not closed. Latest task/review packets say dependency-direction strict validation fails with 358 violations and 38 warnings. Workbench validation work is not authorized until FOUNDATION-REPAIR-DEPENDENCY-DIRECTION-01 repairs or classifies those violations and Foundation Closeout passes.

## 29.2 Source Hierarchy

1. Direct user statements in this chat.
2. Explicit decisions accepted by the user.
3. Current task register.
4. Constraint register.
5. Artifact ledger.
6. Inferences from repeated discussion.
7. Assistant suggestions not accepted by the user.
8. General model knowledge, only after verification if time-sensitive.

## 29.3 Operating Rules for Future Assistants

- Preserve FACT / INFERENCE / UNCERTAIN / PROJECT-CONTEXT labels.
- Do not re-ask answered questions.
- Do not treat assistant recommendations as accepted decisions unless the user accepted them.
- Verify stale platform/toolchain/library facts before relying on them.
- Do not repeat rejected options as fresh suggestions without noting their prior rejection.
- Do not build Workbench/product features before Foundation dependency-direction repair.
- Keep C++17 internal and C-compatible at public/stable boundaries.
- Use structured outputs when continuing tasks.

## 29.4 Active Workstreams

| ID | Name | Status | Priority | Next emphasis |
| --- | --- | --- | --- | --- |
| WORKSTREAM-01 | Language and architecture baseline | active | P0 | See task register |
| WORKSTREAM-02 | C/C++ responsibility split | active | P0 | See task register |
| WORKSTREAM-03 | ABI and public surface governance | active | P0 | See task register |
| WORKSTREAM-04 | Determinism and scheduler law | active | P0 | See task register |
| WORKSTREAM-05 | Repository boundaries and Foundation Lock | blocked | P0 | See task register |
| WORKSTREAM-06 | Provider/capability runtime model | active | P1 | See task register |
| WORKSTREAM-07 | Composition resolver and lockfiles | missing | P1 | See task register |
| WORKSTREAM-08 | Packs/modules/content/trust | active | P1 | See task register |
| WORKSTREAM-09 | Workbench and AIDE operating model | active | P1 | See task register |
| WORKSTREAM-10 | Legacy and platform support tiers | active | P1 | See task register |
| WORKSTREAM-11 | Performance and efficiency contracts | planned | P1 | See task register |

## 29.5 Current Priorities

1. TASK-01 dependency-direction repair.
2. TASK-02/TASK-03 stale wording updates.
3. TASK-04 architecture profile contract.
4. TASK-06/TASK-07 composition resolver and lockfiles.
5. TASK-10 Workbench validation slice after Foundation green.

## 29.6 Current Open Questions

See QUESTION-01 through QUESTION-07 in the open questions register.

## 29.7 Recommended First Action

Start `FOUNDATION-REPAIR-DEPENDENCY-DIRECTION-01`: run the dependency-direction strict validator, classify violations, repair real leaks, add only narrow justified exceptions, then rerun Foundation Closeout.
